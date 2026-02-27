import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import shopify
from colorama import Fore, Style, init
from dotenv import load_dotenv

try:
    from notificacao import enviar_telegram
except ImportError:
    import sys

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from notificacao import enviar_telegram


init(autoreset=True)

BASELINE_PATH = "data/kpis/baseline_kpis.json"


class KPIUpdater:
    def __init__(self):
        load_dotenv("config/.env")
        self.shop_url = os.getenv("SHOPIFY_SHOP_URL")
        self.access_token = os.getenv("SHOPIFY_ACCESS_TOKEN")
        self.api_version = os.getenv("SHOPIFY_API_VERSION")

        imposto_simples = float(os.getenv("IMPOSTO_SIMPLES", "0.04"))
        imposto_icms = float(os.getenv("IMPOSTO_ICMS", "0.20"))
        self.imposto_total = imposto_simples + imposto_icms

        self._inventory_cost_cache: Dict[int, Tuple[float, bool]] = {}
        self._variant_inventory_item_cache: Dict[int, Optional[int]] = {}

    def _log_info(self, msg: str) -> None:
        print(Fore.CYAN + msg + Style.RESET_ALL)

    def _log_ok(self, msg: str) -> None:
        print(Fore.GREEN + msg + Style.RESET_ALL)

    def _log_error(self, msg: str) -> None:
        print(Fore.RED + msg + Style.RESET_ALL)

    def _now_iso(self) -> str:
        return datetime.now().astimezone().isoformat(timespec="seconds")

    def setup_shopify(self) -> bool:
        if not self.shop_url or not self.access_token or not self.api_version:
            self._log_error("[KPI] ERRO: variaveis Shopify ausentes no config/.env")
            return False
        try:
            session = shopify.Session(self.shop_url, self.api_version, self.access_token)
            shopify.ShopifyResource.activate_session(session)
            return True
        except Exception as e:
            self._log_error(f"[KPI] ERRO de conexao Shopify: {e}")
            return False

    def _safe_float(self, value, default: float = 0.0) -> float:
        try:
            if value is None:
                return default
            return float(str(value).replace(",", "."))
        except Exception:
            return default

    def _parse_iso(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            return None

    def _load_or_init_baseline(self) -> Dict:
        if os.path.exists(BASELINE_PATH):
            try:
                with open(BASELINE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    return data
            except Exception as e:
                self._log_error(f"[KPI] ERRO lendo baseline existente: {e}")

        now_iso = self._now_iso()
        return {
            "financeiro": {
                "faturamento_bruto_total": 0.0,
                "ticket_medio": 0.0,
                "margem_media_real_por_pedido": 0.0,
                "margem_por_sku": {},
                "custo_medio_por_pedido": 0.0,
            },
            "operacional": {
                "total_pedidos": 0,
                "pedidos_com_rastreio_em_72h": 0.0,
                "taxa_reembolso": 0.0,
                "taxa_chargeback": 0.0,
                "tempo_medio_despacho_horas": 0.0,
            },
            "loja": {
                "taxa_conversao": 0.0,
                "skus_ativos_total": 0,
                "skus_com_custo_cadastrado": 0,
                "skus_sem_custo_cadastrado": 0,
                "sessoes_totais": 0,
            },
            "meta": {
                "ticket_medio_alvo": 450.0,
                "margem_media_alvo": 0.35,
                "taxa_conversao_alvo": 0.02,
                "rastreio_72h_alvo": 0.90,
            },
            "metadados": {
                "baseline_criado_em": now_iso,
                "ultima_atualizacao": None,
                "fase_atual": "fase_1_fundacao",
                "status": "aguardando_primeiros_pedidos",
            },
        }

    def _save_baseline(self, data: Dict) -> None:
        os.makedirs(os.path.dirname(BASELINE_PATH), exist_ok=True)
        with open(BASELINE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _fetch_orders(self) -> List:
        orders = []
        limit = 250
        since_id = None

        while True:
            params = {"status": "any", "limit": limit}
            if since_id:
                params["since_id"] = since_id

            batch = shopify.Order.find(**params)
            batch_list = list(batch) if batch else []
            if not batch_list:
                break

            orders.extend(batch_list)
            if len(batch_list) < limit:
                break

            max_id = max([getattr(o, "id", 0) for o in batch_list] or [0])
            if not max_id or max_id == since_id:
                break
            since_id = max_id

        return orders

    def _fetch_products(self) -> List:
        products = []
        limit = 250
        since_id = None

        while True:
            params = {"limit": limit}
            if since_id:
                params["since_id"] = since_id

            batch = shopify.Product.find(**params)
            batch_list = list(batch) if batch else []
            if not batch_list:
                break

            products.extend(batch_list)
            if len(batch_list) < limit:
                break

            max_id = max([getattr(p, "id", 0) for p in batch_list] or [0])
            if not max_id or max_id == since_id:
                break
            since_id = max_id

        return products

    def _get_inventory_item_id_from_variant(self, variant_id: Optional[int]) -> Optional[int]:
        if not variant_id:
            return None

        if variant_id in self._variant_inventory_item_cache:
            return self._variant_inventory_item_cache[variant_id]

        try:
            variant = shopify.Variant.find(variant_id)
            inventory_item_id = getattr(variant, "inventory_item_id", None)
            self._variant_inventory_item_cache[variant_id] = inventory_item_id
            return inventory_item_id
        except Exception:
            self._variant_inventory_item_cache[variant_id] = None
            return None

    def _get_inventory_cost(self, inventory_item_id: Optional[int]) -> Tuple[float, bool]:
        if not inventory_item_id:
            return 0.0, False

        if inventory_item_id in self._inventory_cost_cache:
            return self._inventory_cost_cache[inventory_item_id]

        try:
            inv = shopify.InventoryItem.find(inventory_item_id)
            cost_raw = getattr(inv, "cost", None)
            if cost_raw in (None, ""):
                result = (0.0, False)
            else:
                result = (self._safe_float(cost_raw, 0.0), True)
            self._inventory_cost_cache[inventory_item_id] = result
            return result
        except Exception as e:
            self._log_error(f"[KPI] ERRO ao ler custo do InventoryItem {inventory_item_id}: {e}")
            result = (0.0, False)
            self._inventory_cost_cache[inventory_item_id] = result
            return result

    def _order_shipping_total(self, order) -> float:
        direct = self._safe_float(getattr(order, "total_shipping_price", None), 0.0)
        if direct > 0:
            return direct

        try:
            shipping_set = getattr(order, "total_shipping_price_set", None)
            if shipping_set:
                shop_money = getattr(shipping_set, "shop_money", None)
                if shop_money:
                    return self._safe_float(getattr(shop_money, "amount", None), 0.0)
                if isinstance(shipping_set, dict):
                    return self._safe_float(
                        shipping_set.get("shop_money", {}).get("amount"),
                        0.0,
                    )
        except Exception:
            pass

        return 0.0

    def _order_has_tracking_in_72h(self, order) -> bool:
        created_at = self._parse_iso(getattr(order, "created_at", None))
        if not created_at:
            return False

        fulfillments = getattr(order, "fulfillments", []) or []
        for fulfillment in fulfillments:
            tracking_number = getattr(fulfillment, "tracking_number", None)
            tracking_numbers = getattr(fulfillment, "tracking_numbers", None)
            has_tracking = bool(tracking_number) or bool(tracking_numbers)
            if not has_tracking:
                continue

            fulfillment_created_at = self._parse_iso(getattr(fulfillment, "created_at", None))
            if not fulfillment_created_at:
                continue

            delta_h = (fulfillment_created_at - created_at).total_seconds() / 3600.0
            if delta_h <= 72:
                return True

        return False

    def _order_dispatch_hours(self, order) -> Optional[float]:
        created_at = self._parse_iso(getattr(order, "created_at", None))
        if not created_at:
            return None

        fulfillments = getattr(order, "fulfillments", []) or []
        dispatch_times = []
        for fulfillment in fulfillments:
            fulfillment_created_at = self._parse_iso(getattr(fulfillment, "created_at", None))
            if fulfillment_created_at:
                dispatch_times.append(fulfillment_created_at)

        if not dispatch_times:
            return None

        first_dispatch = min(dispatch_times)
        delta_h = (first_dispatch - created_at).total_seconds() / 3600.0
        return max(delta_h, 0.0)

    def _count_refunds(self, order) -> int:
        refunds = getattr(order, "refunds", []) or []
        return len(refunds)

    def _is_chargeback(self, order) -> bool:
        transactions = getattr(order, "transactions", []) or []
        for tx in transactions:
            kind = str(getattr(tx, "kind", "")).lower()
            status = str(getattr(tx, "status", "")).lower()
            if "chargeback" in kind or "chargeback" in status:
                return True
        return False

    def _compute_order_cogs(self, order) -> Tuple[float, Dict[str, Dict[str, float]]]:
        cogs_total = 0.0
        sku_stats: Dict[str, Dict[str, float]] = {}

        line_items = getattr(order, "line_items", []) or []
        for item in line_items:
            quantity = int(getattr(item, "quantity", 0) or 0)
            if quantity <= 0:
                continue

            title = str(getattr(item, "title", "SKU desconhecido"))
            variant_title = str(getattr(item, "variant_title", "")).strip()
            sku_title = title if not variant_title or variant_title == "Default Title" else f"{title} - {variant_title}"

            inventory_item_id = getattr(item, "inventory_item_id", None)
            if not inventory_item_id:
                variant_id = getattr(item, "variant_id", None)
                inventory_item_id = self._get_inventory_item_id_from_variant(variant_id)

            cost_unit, has_cost = self._get_inventory_cost(inventory_item_id)
            if not has_cost:
                self._log_info(f"[KPI] SKU sem custo cadastrado no pedido: {sku_title}")

            line_cost = cost_unit * quantity
            cogs_total += line_cost

            if sku_title not in sku_stats:
                sku_stats[sku_title] = {"revenue": 0.0, "cost": 0.0}
            sku_stats[sku_title]["revenue"] += self._safe_float(getattr(item, "price", None), 0.0) * quantity
            sku_stats[sku_title]["cost"] += line_cost

        return cogs_total, sku_stats

    def atualizar(self) -> bool:
        self._log_info("\n=== AKIRA KPI UPDATER // BASELINE ===\n")

        if not self.setup_shopify():
            return False

        data = self._load_or_init_baseline()

        orders = self._fetch_orders()
        products = self._fetch_products()

        total_pedidos = len(orders)
        faturamento_bruto_total = 0.0
        total_refunds = 0
        chargebacks = 0
        tracking_72h_count = 0
        dispatch_hours_values = []
        margin_values = []
        total_order_cost_with_shipping = 0.0
        margem_por_sku_acc: Dict[str, Dict[str, float]] = {}

        for order in orders:
            total_price = self._safe_float(getattr(order, "total_price", None), 0.0)
            shipping_total = self._order_shipping_total(order)
            tax_total = total_price * self.imposto_total

            cogs_total, sku_stats = self._compute_order_cogs(order)
            for sku_name, stats in sku_stats.items():
                if sku_name not in margem_por_sku_acc:
                    margem_por_sku_acc[sku_name] = {"revenue": 0.0, "cost": 0.0}
                margem_por_sku_acc[sku_name]["revenue"] += stats["revenue"]
                margem_por_sku_acc[sku_name]["cost"] += stats["cost"]

            order_cost = cogs_total + shipping_total
            total_order_cost_with_shipping += order_cost
            faturamento_bruto_total += total_price

            if total_price > 0:
                margem = (total_price - tax_total - shipping_total - cogs_total) / total_price
                margin_values.append(margem)

            total_refunds += self._count_refunds(order)
            if self._is_chargeback(order):
                chargebacks += 1

            if self._order_has_tracking_in_72h(order):
                tracking_72h_count += 1

            dispatch_hours = self._order_dispatch_hours(order)
            if dispatch_hours is not None:
                dispatch_hours_values.append(dispatch_hours)

        ticket_medio = (faturamento_bruto_total / total_pedidos) if total_pedidos > 0 else 0.0
        margem_media_real = (sum(margin_values) / len(margin_values)) if margin_values else 0.0
        custo_medio_por_pedido = (total_order_cost_with_shipping / total_pedidos) if total_pedidos > 0 else 0.0

        pedidos_com_rastreio_em_72h = (tracking_72h_count / total_pedidos) if total_pedidos > 0 else 0.0
        taxa_reembolso = (total_refunds / total_pedidos) if total_pedidos > 0 else 0.0
        taxa_chargeback = (chargebacks / total_pedidos) if total_pedidos > 0 else 0.0
        tempo_medio_despacho_horas = (
            sum(dispatch_hours_values) / len(dispatch_hours_values)
            if dispatch_hours_values
            else 0.0
        )

        margem_por_sku = {}
        for sku_name, stats in margem_por_sku_acc.items():
            revenue = stats["revenue"]
            cost = stats["cost"]
            if revenue > 0:
                margem_por_sku[sku_name] = (revenue - cost - (revenue * self.imposto_total)) / revenue

        skus_ativos_total = 0
        skus_com_custo_cadastrado = 0
        skus_sem_custo_cadastrado = 0

        for product in products:
            if str(getattr(product, "status", "")).lower() != "active":
                continue
            variants = getattr(product, "variants", []) or []
            for variant in variants:
                skus_ativos_total += 1
                inventory_item_id = getattr(variant, "inventory_item_id", None)
                if not inventory_item_id:
                    skus_sem_custo_cadastrado += 1
                    self._log_info(f"[KPI] SKU sem inventory_item_id: {getattr(variant, 'title', 'Unknown')}")
                    continue

                _, has_cost = self._get_inventory_cost(inventory_item_id)
                if has_cost:
                    skus_com_custo_cadastrado += 1
                else:
                    skus_sem_custo_cadastrado += 1
                    self._log_info(f"[KPI] SKU sem custo cadastrado: {getattr(variant, 'title', 'Unknown')}")

        sessoes_totais = int(data.get("loja", {}).get("sessoes_totais", 0) or 0)
        taxa_conversao = (total_pedidos / sessoes_totais) if sessoes_totais > 0 else 0.0

        data["financeiro"] = {
            "faturamento_bruto_total": round(faturamento_bruto_total, 2),
            "ticket_medio": round(ticket_medio, 2),
            "margem_media_real_por_pedido": round(margem_media_real, 4),
            "margem_por_sku": {k: round(v, 4) for k, v in margem_por_sku.items()},
            "custo_medio_por_pedido": round(custo_medio_por_pedido, 2),
        }

        data["operacional"] = {
            "total_pedidos": total_pedidos,
            "pedidos_com_rastreio_em_72h": round(pedidos_com_rastreio_em_72h, 4),
            "taxa_reembolso": round(taxa_reembolso, 4),
            "taxa_chargeback": round(taxa_chargeback, 4),
            "tempo_medio_despacho_horas": round(tempo_medio_despacho_horas, 2),
        }

        data["loja"] = {
            "taxa_conversao": round(taxa_conversao, 4),
            "skus_ativos_total": skus_ativos_total,
            "skus_com_custo_cadastrado": skus_com_custo_cadastrado,
            "skus_sem_custo_cadastrado": skus_sem_custo_cadastrado,
            "sessoes_totais": sessoes_totais,
        }

        data.setdefault("meta", {
            "ticket_medio_alvo": 450.0,
            "margem_media_alvo": 0.35,
            "taxa_conversao_alvo": 0.02,
            "rastreio_72h_alvo": 0.90,
        })

        data.setdefault("metadados", {})
        data["metadados"].setdefault("baseline_criado_em", self._now_iso())
        data["metadados"]["ultima_atualizacao"] = self._now_iso()
        data["metadados"].setdefault("fase_atual", "fase_1_fundacao")
        data["metadados"]["status"] = (
            "aguardando_primeiros_pedidos" if total_pedidos == 0 else "coletando_dados_reais"
        )

        self._save_baseline(data)

        self._log_ok(f"[KPI] baseline atualizado em: {BASELINE_PATH}")
        self._log_info(f"[KPI] total_pedidos: {total_pedidos}")
        self._log_info(f"[KPI] faturamento_bruto_total: R$ {faturamento_bruto_total:.2f}")
        self._log_info(f"[KPI] ticket_medio: R$ {ticket_medio:.2f}")
        self._log_info(f"[KPI] margem_media_real_por_pedido: {margem_media_real:.2%}")
        self._log_info(
            "[KPI] skus_ativos_total: "
            f"{skus_ativos_total} | com_custo: {skus_com_custo_cadastrado} | sem_custo: {skus_sem_custo_cadastrado}"
        )
        self._log_info(f"[KPI] taxa_reembolso: {taxa_reembolso:.2%}")

        if margem_media_real < 0.30:
            msg = (
                "⚠️ **AKIRA KPI ALERTA**\n"
                f"Margem media real abaixo de 30%.\n"
                f"Atual: {margem_media_real:.2%}\n"
                f"Pedidos: {total_pedidos} | Faturamento: R$ {faturamento_bruto_total:.2f}"
            )
            try:
                enviar_telegram(msg)
                self._log_ok("[KPI] alerta de margem enviado no Telegram")
            except Exception as e:
                self._log_error(f"[KPI] erro ao notificar Telegram: {e}")

        return True


def main() -> int:
    updater = KPIUpdater()
    ok = updater.atualizar()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
