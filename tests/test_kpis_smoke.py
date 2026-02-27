import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import atualizar_kpis
from atualizar_kpis import KPIUpdater


class FakeFulfillment:
    def __init__(self, tracking_number, created_at):
        self.tracking_number = tracking_number
        self.created_at = created_at


class FakeLineItem:
    def __init__(self, title, variant_title, quantity, price, variant_id):
        self.title = title
        self.variant_title = variant_title
        self.quantity = quantity
        self.price = price
        self.variant_id = variant_id
        self.inventory_item_id = None


class FakeOrder:
    def __init__(self):
        self.id = 1
        self.total_price = "100.00"
        self.total_shipping_price = "10.00"
        self.created_at = "2026-02-01T10:00:00-03:00"
        self.refunds = []
        self.transactions = []
        self.line_items = [FakeLineItem("Keycap Kit", "Red", 1, "100.00", 101)]
        self.fulfillments = [FakeFulfillment("TRACK123", "2026-02-02T08:00:00-03:00")]


class FakeProductVariant:
    def __init__(self, inventory_item_id, title):
        self.inventory_item_id = inventory_item_id
        self.title = title


class FakeProduct:
    def __init__(self):
        self.id = 10
        self.status = "active"
        self.variants = [
            FakeProductVariant(1001, "Keycap Red"),
            FakeProductVariant(1002, "Keycap Blue"),
        ]


class FakeVariant:
    def __init__(self, inventory_item_id):
        self.inventory_item_id = inventory_item_id


class FakeInventoryItem:
    def __init__(self, cost):
        self.cost = cost


class KpiSmokeTests(unittest.TestCase):
    def _env_getter(self, key, default=None):
        values = {
            "SHOPIFY_SHOP_URL": "fake-shop.myshopify.com",
            "SHOPIFY_ACCESS_TOKEN": "fake-token",
            "SHOPIFY_API_VERSION": "2025-01",
            "IMPOSTO_SIMPLES": "0.04",
            "IMPOSTO_ICMS": "0.20",
        }
        return values.get(key, default)

    def test_atualizar_kpis_read_write_with_mock_shopify_api(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            baseline_path = os.path.join(tmpdir, "baseline_kpis.json")
            baseline_seed = {
                "financeiro": {},
                "operacional": {},
                "loja": {
                    "sessoes_totais": 100
                },
                "meta": {
                    "ticket_medio_alvo": 450.0,
                    "margem_media_alvo": 0.35,
                    "taxa_conversao_alvo": 0.02,
                    "rastreio_72h_alvo": 0.90,
                },
                "metadados": {
                    "baseline_criado_em": "2026-02-27T00:00:00-03:00",
                    "ultima_atualizacao": None,
                    "fase_atual": "fase_1_fundacao",
                    "status": "aguardando_primeiros_pedidos",
                },
            }
            with open(baseline_path, "w", encoding="utf-8") as f:
                json.dump(baseline_seed, f)

            def inventory_item_find_side_effect(inventory_item_id):
                if inventory_item_id == 1001:
                    return FakeInventoryItem("40.00")
                if inventory_item_id == 1002:
                    return FakeInventoryItem(None)
                return FakeInventoryItem("0.00")

            with patch("atualizar_kpis.BASELINE_PATH", baseline_path), \
                 patch("atualizar_kpis.load_dotenv"), \
                 patch("atualizar_kpis.os.getenv", side_effect=self._env_getter), \
                 patch.object(KPIUpdater, "setup_shopify", return_value=True), \
                 patch("atualizar_kpis.shopify.Order.find", return_value=[FakeOrder()]), \
                 patch("atualizar_kpis.shopify.Product.find", return_value=[FakeProduct()]), \
                 patch("atualizar_kpis.shopify.Variant.find", return_value=FakeVariant(1001)), \
                 patch("atualizar_kpis.shopify.InventoryItem.find", side_effect=inventory_item_find_side_effect), \
                 patch("atualizar_kpis.enviar_telegram") as enviar_telegram_mock:
                updater = KPIUpdater()
                ok = updater.atualizar()

            self.assertTrue(ok)
            self.assertTrue(os.path.exists(baseline_path))

            with open(baseline_path, "r", encoding="utf-8") as f:
                updated = json.load(f)

            self.assertEqual(updated["operacional"]["total_pedidos"], 1)
            self.assertEqual(updated["financeiro"]["faturamento_bruto_total"], 100.0)
            self.assertEqual(updated["financeiro"]["ticket_medio"], 100.0)
            self.assertEqual(updated["loja"]["skus_ativos_total"], 2)
            self.assertEqual(updated["loja"]["skus_com_custo_cadastrado"], 1)
            self.assertEqual(updated["loja"]["skus_sem_custo_cadastrado"], 1)
            self.assertIsNotNone(updated["metadados"]["ultima_atualizacao"])
            self.assertAlmostEqual(updated["loja"]["taxa_conversao"], 0.01, places=4)

            # Margem calculada para o pedido: (100 - 24 - 10 - 40) / 100 = 0.26 => alerta
            enviar_telegram_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
