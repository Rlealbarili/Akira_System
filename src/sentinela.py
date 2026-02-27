import os
import re
from typing import List, Optional, Set, Tuple

import shopify
from dotenv import load_dotenv
from colorama import Fore, Style, init as colorama_init
from playwright.sync_api import (
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)

# Importar modulo de notificacao com fallback para execucao fora da pasta src
try:
    from notificacao import enviar_telegram
except ImportError:
    import sys

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from notificacao import enviar_telegram


colorama_init(autoreset=True)


class AliScrapeError(RuntimeError):
    pass


class SentinelSystem:
    """
    Guardiao de seguranca: audita um produto (Shopify) contra dados do fornecedor (AliExpress)
    e aciona um "kill switch" quando custo/estoque violam regras.
    """

    def __init__(
        self,
        *,
        max_total_usd: float = 50.0,
        headless: bool = True,
        playwright_timeout_ms: int = 30_000,
    ):
        # Carregar Env
        load_dotenv("config/.env")

        self.max_total_usd = float(max_total_usd)
        self.headless = bool(headless)
        self.playwright_timeout_ms = int(playwright_timeout_ms)

        self.shop_url = os.getenv("SHOPIFY_SHOP_URL")
        self.access_token = os.getenv("SHOPIFY_ACCESS_TOKEN")
        self.api_version = os.getenv("SHOPIFY_API_VERSION")

        self._log("INFO", "SENTINELA ONLINE // initializing Shopify session")
        if not self.access_token or not self.shop_url or not self.api_version:
            raise RuntimeError(
                "Shopify env vars ausentes. Verifique SHOPIFY_SHOP_URL, SHOPIFY_ACCESS_TOKEN, SHOPIFY_API_VERSION em config/.env"
            )

        session = shopify.Session(self.shop_url, self.api_version, self.access_token)
        shopify.ShopifyResource.activate_session(session)

    def _log(self, level: str, msg: str) -> None:
        palette = {
            "INFO": Fore.CYAN,
            "OK": Fore.GREEN,
            "WARN": Fore.YELLOW,
            "ERROR": Fore.RED,
            "KILL": Fore.MAGENTA,
        }
        color = palette.get(level.upper(), Fore.WHITE)
        print(f"{color}[SENTINELA/{level.upper():5}] {Style.RESET_ALL}{msg}")

    def _parse_money(self, raw: str) -> float:
        """
        Converte strings como '$12.34', 'US $ 12,34', '12.34' -> float.
        """
        if raw is None:
            raise ValueError("money string is None")

        s = str(raw).strip()
        s = s.replace("\u00a0", " ")  # nbsp
        # Remove currency symbols/labels
        s = re.sub(r"(?i)\b(us\s*\$|usd|r\$|\$|brl)\b", "", s)
        # Keep only digits, dot, comma, minus
        s = re.sub(r"[^0-9,.\-]", "", s).strip()
        if not s:
            raise ValueError(f"unable to parse money from: {raw!r}")

        # If both comma and dot exist, assume comma is thousands separator
        if "," in s and "." in s:
            s = s.replace(",", "")
        else:
            # If only comma exists, treat as decimal separator
            if "," in s and "." not in s:
                s = s.replace(",", ".")

        return float(s)

    def _extract_first_price_like(self, text: str) -> Optional[float]:
        if not text:
            return None
        # Prefer explicit USD patterns first
        m = re.search(r"(?i)(?:us\\s*\\$|usd\\s*\\$|\\$)\\s*([0-9]+(?:[.,][0-9]{1,2})?)", text)
        if m:
            try:
                return self._parse_money(m.group(0))
            except Exception:
                return None

        # Fallback: any number with 2 decimals
        m = re.search(r"([0-9]+(?:[.][0-9]{2}))", text)
        if m:
            try:
                return float(m.group(1))
            except Exception:
                return None
        return None

    def _normalize_label(self, value: str) -> str:
        if value is None:
            return ""
        text = str(value).strip().lower()
        text = re.sub(r"[^a-z0-9]+", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _variant_tokens(self, variant) -> Set[str]:
        tokens = set()
        raw_values = [
            getattr(variant, "title", None),
            getattr(variant, "option1", None),
            getattr(variant, "option2", None),
            getattr(variant, "option3", None),
        ]
        for raw in raw_values:
            if not raw:
                continue
            normalized = self._normalize_label(str(raw))
            if normalized:
                tokens.add(normalized)
            # Tambem quebra variantes compostas (ex.: "Red / 75 keys")
            for part in re.split(r"[/|,-]", str(raw)):
                part_norm = self._normalize_label(part)
                if part_norm:
                    tokens.add(part_norm)
        return tokens

    def _variant_matches_oos(self, variant, oos_norms: List[str]) -> bool:
        if not oos_norms:
            return False
        tokens = self._variant_tokens(variant)
        if not tokens:
            return False
        for token in tokens:
            if len(token) < 2:
                continue
            for oos in oos_norms:
                if not oos:
                    continue
                if token == oos or token in oos or oos in token:
                    return True
        return False

    def _get_ali_data(self, url: str) -> Tuple[float, float, bool]:
        """
        Retorna (preco_usd, frete_usd, em_estoque).

        Observacao: scraping depende do layout do AliExpress, entao a extracao
        e feita em camadas e pode precisar de ajustes de seletores conforme o tempo.
        """
        if not url:
            raise AliScrapeError("URL do AliExpress vazia")

        self._log("INFO", f"SCANNING SUPPLIER TARGET // {url}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                locale="en-US",
                viewport={"width": 1365, "height": 900},
            )
            page = context.new_page()
            page.set_default_timeout(self.playwright_timeout_ms)

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=self.playwright_timeout_ms)
                # networkidle pode nunca estabilizar; melhor ser tolerante.
                try:
                    page.wait_for_load_state("networkidle", timeout=min(10_000, self.playwright_timeout_ms))
                except PlaywrightTimeoutError:
                    pass

                html = page.content()

                # Heuristica simples para paginas de verificacao/captcha. Nao tentamos burlar.
                lower_html = (html or "").lower()
                if any(x in lower_html for x in ("captcha", "verify you are", "security check")):
                    raise AliScrapeError("AliExpress retornou pagina de verificacao (captcha/security check).")

                # --- Preco ---
                meta_prices = []
                for sel in (
                    'meta[property="og:price:amount"]',
                    'meta[property="product:price:amount"]',
                    'meta[itemprop="price"]',
                ):
                    el = page.query_selector(sel)
                    if not el:
                        continue
                    content = el.get_attribute("content")
                    if content:
                        try:
                            meta_prices.append(self._parse_money(content))
                        except Exception:
                            pass

                # Alguns layouts exibem o preco como texto
                dom_prices = []
                for sel in (
                    "span.product-price-value",
                    "div.product-price-current",
                    "div.product-price span",
                    "span.uniform-banner-box-price",
                ):
                    el = page.query_selector(sel)
                    if not el:
                        continue
                    try:
                        txt = el.inner_text()
                    except Exception:
                        txt = None
                    pval = self._extract_first_price_like(txt or "")
                    if pval is not None:
                        dom_prices.append(pval)

                # Fallback: regex no HTML (menor confianca)
                html_price = self._extract_first_price_like(html)

                if not meta_prices and not dom_prices and html_price is None:
                    raise AliScrapeError("Falha ao extrair o preco do AliExpress (nenhum candidato encontrado).")

                # Se existir preco em meta tags, prioriza (tende a ser o "real" do produto).
                if meta_prices:
                    price = min([x for x in meta_prices if x > 0], default=None)
                elif dom_prices:
                    # Em geral queremos o menor preco valido (evita capturar valores de faixa/sem desconto)
                    price = min([x for x in dom_prices if x > 0], default=None)
                else:
                    price = html_price

                if price is None or price <= 0:
                    raise AliScrapeError("Falha ao extrair o preco do AliExpress (candidatos invalidos).")

                # --- Frete ---
                shipping = 0.0
                shipping_candidates = []

                # Tentativa: procurar texto de shipping/frete no HTML
                ship_match = re.search(
                    r"(?is)(shipping|frete)[^\\$]{0,120}(us\\s*\\$|usd\\s*\\$|\\$)\\s*([0-9]+(?:[.,][0-9]{1,2})?)",
                    html or "",
                )
                if ship_match:
                    try:
                        shipping_candidates.append(self._parse_money(ship_match.group(3)))
                    except Exception:
                        pass

                # Free shipping heuristica
                if re.search(r"(?i)free\\s+shipping", html or ""):
                    shipping_candidates.append(0.0)

                if shipping_candidates:
                    shipping = min([x for x in shipping_candidates if x >= 0], default=0.0)
                else:
                    self._log("WARN", "Frete nao identificado com clareza; assumindo 0.00 (pode exigir ajuste de seletor).")

                # --- Estoque ---
                in_stock = True
                if any(
                    phrase in lower_html
                    for phrase in (
                        "out of stock",
                        "sold out",
                        "no longer available",
                        "currently unavailable",
                        "this item is unavailable",
                    )
                ):
                    in_stock = False

                # Heuristica por botoes
                try:
                    add_btn = page.query_selector('button:has-text("Add to cart")')
                    if add_btn:
                        aria_disabled = (add_btn.get_attribute("aria-disabled") or "").lower()
                        disabled = add_btn.get_attribute("disabled")
                        if disabled is not None or aria_disabled == "true":
                            in_stock = False
                except Exception:
                    pass

                self._log(
                    "OK",
                    f"ALI DATA LOCKED // price={price:.2f} usd | shipping={shipping:.2f} usd | in_stock={in_stock}",
                )
                return float(price), float(shipping), bool(in_stock)

            except (PlaywrightTimeoutError, PlaywrightError) as e:
                raise AliScrapeError(f"Playwright error durante scraping: {e}") from e
            finally:
                try:
                    context.close()
                except Exception:
                    pass
                try:
                    browser.close()
                except Exception:
                    pass

    def _kill_switch(self, product, reason: str) -> bool:
        """
        Desativa o produto imediatamente (draft) e marca com tag de banimento.
        """
        product_id = getattr(product, "id", None)
        title = getattr(product, "title", "Unknown")
        reason = (reason or "UNSPECIFIED").strip()

        self._log("KILL", f"KILL SWITCH ARMED // product_id={product_id} // reason={reason}")

        try:
            product.status = "draft"

            existing_tags = [t.strip() for t in (product.tags or "").split(",") if t.strip()]
            ban_tag = f"SENTINELA_BAN: {reason}"
            if ban_tag not in existing_tags:
                existing_tags.append(ban_tag)
            product.tags = ", ".join(existing_tags)

            ok = bool(product.save())
            if not ok:
                errs = getattr(product, "errors", None)
                details = ""
                try:
                    details = f" {errs.full_messages()}" if errs else ""
                except Exception:
                    details = ""
                self._log("ERROR", f"Falha ao salvar produto em draft.{details}")
                return False

            self._log("OK", f"TARGET NEUTRALIZED // '{title}' set to draft + tag applied")

        except Exception as e:
            self._log("ERROR", f"Erro ao acionar kill switch: {e}")
            return False

        # Notificar (nao pode interromper fluxo)
        try:
            msg = (
                f"**SENTINELA: PRODUTO DESATIVADO**\n"
                f"Produto: {title}\n"
                f"ID: {product_id}\n"
                f"Motivo: {reason}\n"
                f"Status: draft"
            )
            enviar_telegram(msg)
        except Exception as e:
            self._log("WARN", f"Falha ao enviar Telegram (kill switch): {e}")

        return True

    def _detect_variant_ghosts(self, page, product) -> List[str]:
        """
        Detecta variantes esgotadas no fornecedor (disabled/greyed out),
        retornando lista de TITULOS de variantes da Shopify afetadas.
        """
        variant_candidates = []
        blocked_terms = (
            "add to cart",
            "buy now",
            "quantity",
            "shipping",
            "ship to",
            "store",
            "coupon",
            "login",
        )

        selectors = (
            "button[disabled]",
            "button[aria-disabled='true']",
            "li[aria-disabled='true']",
            "[class*='sku'][class*='disabled']",
            "[class*='SKU'][class*='disabled']",
            "[class*='sku-property-item'][class*='disabled']",
            "[class*='comet-v2-select-item'][aria-disabled='true']",
        )

        for selector in selectors:
            try:
                elements = page.query_selector_all(selector) or []
            except Exception:
                continue
            for element in elements:
                text = ""
                try:
                    text = (element.inner_text() or "").strip()
                except Exception:
                    text = ""
                if not text:
                    for attr in ("title", "aria-label", "data-sku-title", "data-title"):
                        try:
                            text = (element.get_attribute(attr) or "").strip()
                        except Exception:
                            text = ""
                        if text:
                            break
                if not text:
                    continue
                norm = self._normalize_label(text)
                if not norm:
                    continue
                if any(term in norm for term in blocked_terms):
                    continue
                variant_candidates.append(norm)

        if not variant_candidates:
            self._log("INFO", "SKU GHOST SCAN // no disabled supplier variant found")
            return []

        variant_candidates = sorted(set(variant_candidates))
        ghosts = set()

        for variant in getattr(product, "variants", []) or []:
            variant_name = (getattr(variant, "title", "") or "").strip()
            if not variant_name:
                continue
            tokens = self._variant_tokens(variant)
            match_found = False
            for token in tokens:
                if len(token) < 2:
                    continue
                if any(token == c or token in c or c in token for c in variant_candidates):
                    match_found = True
                    break
            if match_found:
                ghosts.add(variant_name)

        ghost_list = sorted(ghosts)
        if ghost_list:
            self._log("WARN", f"SKU GHOST SCAN // variants_oos={ghost_list}")
        else:
            self._log("WARN", "SKU GHOST SCAN // disabled options found, but no Shopify variant match")
        return ghost_list

    def _scan_variant_ghosts(self, ali_url: str, product) -> List[str]:
        """
        Abre a pagina do fornecedor e delega deteccao de variante fantasma.
        Falhas sempre retornam lista vazia para nao quebrar o fluxo principal.
        """
        if not ali_url:
            return []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                locale="en-US",
                viewport={"width": 1365, "height": 900},
            )
            page = context.new_page()
            page.set_default_timeout(self.playwright_timeout_ms)
            try:
                page.goto(ali_url, wait_until="domcontentloaded", timeout=self.playwright_timeout_ms)
                try:
                    page.wait_for_load_state("networkidle", timeout=min(10_000, self.playwright_timeout_ms))
                except PlaywrightTimeoutError:
                    pass
                return self._detect_variant_ghosts(page, product)
            except Exception as e:
                self._log("WARN", f"SKU GHOST SCAN FAILURE // {e}")
                return []
            finally:
                try:
                    context.close()
                except Exception:
                    pass
                try:
                    browser.close()
                except Exception:
                    pass

    def _zero_variant_inventory(self, product, variant_names_oos: List[str]) -> int:
        """
        Zera estoque apenas das variantes afetadas e aplica tag de rastreio.
        Retorna quantidade de variantes atualizadas.
        """
        if not variant_names_oos:
            return 0

        oos_norms = [self._normalize_label(name) for name in variant_names_oos if self._normalize_label(name)]
        if not oos_norms:
            return 0

        existing_tags = [t.strip() for t in (product.tags or "").split(",") if t.strip()]
        tags_changed = False
        updated = 0
        product_id = getattr(product, "id", None)
        product_title = getattr(product, "title", "Unknown")

        for variant in getattr(product, "variants", []) or []:
            if not self._variant_matches_oos(variant, oos_norms):
                continue

            variant_name = (getattr(variant, "title", "") or "Unknown Variant").strip()
            inventory_item_id = getattr(variant, "inventory_item_id", None)
            if not inventory_item_id:
                self._log("WARN", f"SKU DEATH // variant '{variant_name}' sem inventory_item_id")
                continue

            level_zeroed = False
            try:
                # Carrega InventoryItem para validar existencia da variante no inventario.
                shopify.InventoryItem.find(inventory_item_id)
            except Exception as e:
                self._log("WARN", f"SKU DEATH // falha ao buscar inventory item ({variant_name}): {e}")
                continue

            try:
                levels = shopify.InventoryLevel.find(inventory_item_ids=inventory_item_id)
            except Exception as e:
                self._log("WARN", f"SKU DEATH // falha ao buscar inventory levels ({variant_name}): {e}")
                continue

            if not levels:
                self._log("WARN", f"SKU DEATH // nenhum inventory level encontrado para '{variant_name}'")
                continue

            for level in levels:
                location_id = getattr(level, "location_id", None)
                if location_id is None:
                    continue
                try:
                    shopify.InventoryLevel.set(location_id, inventory_item_id, 0)
                    level_zeroed = True
                except Exception:
                    try:
                        shopify.InventoryLevel.set(
                            location_id=location_id,
                            inventory_item_id=inventory_item_id,
                            available=0,
                        )
                        level_zeroed = True
                    except Exception as e:
                        self._log(
                            "WARN",
                            f"SKU DEATH // falha ao zerar level (variant='{variant_name}', location={location_id}): {e}",
                        )

            if not level_zeroed:
                continue

            updated += 1
            track_tag = f"SENTINELA_VARIANT_OOS: {variant_name}"
            if track_tag not in existing_tags:
                existing_tags.append(track_tag)
                tags_changed = True

            self._log("WARN", f"SKU DEATH CONFIRMED // variant='{variant_name}' inventory set to 0")

            try:
                msg = (
                    f"**SENTINELA: VARIANTE ESGOTADA**\n"
                    f"Produto: {product_title}\n"
                    f"ID: {product_id}\n"
                    f"Variante: {variant_name}\n"
                    f"Motivo: VARIANTE_ESGOTADA_NO_FORNECEDOR"
                )
                enviar_telegram(msg)
            except Exception as e:
                self._log("WARN", f"Falha ao enviar Telegram (variant oos): {e}")

        if tags_changed:
            try:
                product.tags = ", ".join(existing_tags)
                if not product.save():
                    self._log("WARN", "SKU DEATH // falha ao salvar tags de variante OOS no produto")
                else:
                    self._log("OK", "SKU DEATH // product tracking tags updated")
            except Exception as e:
                self._log("WARN", f"SKU DEATH // falha ao persistir tags no produto: {e}")

        return updated

    def auditar_produto(self, shopify_product_id: int, ali_url: str) -> bool:
        """
        Orquestra a auditoria:
        - Scrape AliExpress (preco, frete, estoque)
        - Regras criticas: total > 50 USD ou sem estoque -> kill switch
        - Se aprovado: atualiza cost do InventoryItem das variantes

        Retorna True quando completou a auditoria (kill switch ou atualizacao de custo),
        e False quando falhou (ex: scraping/Shopify error).
        """
        self._log("INFO", f"AUDIT ORDER RECEIVED // shopify_product_id={shopify_product_id}")

        try:
            product = shopify.Product.find(shopify_product_id)
        except Exception as e:
            self._log("ERROR", f"Falha ao buscar produto na Shopify: {e}")
            return False

        if not product:
            self._log("ERROR", "Produto nao encontrado na Shopify.")
            return False

        try:
            price, shipping, in_stock = self._get_ali_data(ali_url)
        except AliScrapeError as e:
            # Robustez: falhou scraping, loga e segue sem quebrar fluxos externos.
            self._log("ERROR", f"SCRAPE FAILURE // {e}")
            return False
        except Exception as e:
            self._log("ERROR", f"Erro inesperado no scraping: {e}")
            return False

        total = round(float(price) + float(shipping), 2)

        # Regra Critica 1
        if total > self.max_total_usd:
            reason = f"CUSTO_TOTAL_USD {total:.2f} > {self.max_total_usd:.2f}"
            return bool(self._kill_switch(product, reason))

        # Regra Critica 2
        if not in_stock:
            reason = "ESTOQUE_ZERADO_NO_FORNECEDOR"
            return bool(self._kill_switch(product, reason))

        # Produto segue ativo: detectar variante fantasma (SKU Death)
        try:
            ghost_variants = self._scan_variant_ghosts(ali_url, product)
            if ghost_variants:
                self._zero_variant_inventory(product, ghost_variants)
        except Exception as e:
            # Nunca quebrar auditoria principal por falha de variante fantasma.
            self._log("WARN", f"SKU DEATH PIPELINE FAILURE // {e}")

        # Aprovado: atualizar custo das variantes
        updated_any = False
        for v in getattr(product, "variants", []) or []:
            inv_id = getattr(v, "inventory_item_id", None)
            if not inv_id:
                continue
            try:
                inv = shopify.InventoryItem.find(inv_id)
                inv.cost = total
                ok = bool(inv.save())
                if ok:
                    updated_any = True
                    self._log("OK", f"COST UPDATED // inventory_item_id={inv_id} cost={total:.2f}")
                else:
                    self._log("WARN", f"Falha ao salvar InventoryItem {inv_id} (sem detalhes).")
            except Exception as e:
                self._log("WARN", f"Falha ao atualizar cost do InventoryItem {inv_id}: {e}")

        if not updated_any:
            self._log("WARN", "Auditoria ok, mas nenhum InventoryItem foi atualizado (sem variantes ou falta de permissao).")
            return False

        return True


if __name__ == "__main__":
    # Execucao manual rapida para testes:
    # python src/sentinela.py <shopify_product_id> <ali_url>
    import sys

    if len(sys.argv) < 3:
        print("Usage: python src/sentinela.py <shopify_product_id> <ali_url>")
        raise SystemExit(2)

    sent = SentinelSystem()
    ok = sent.auditar_produto(int(sys.argv[1]), sys.argv[2])
    raise SystemExit(0 if ok else 1)
