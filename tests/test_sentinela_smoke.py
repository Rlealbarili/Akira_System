import os
import sys
import unittest
from unittest.mock import patch

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from sentinela import SentinelSystem


class FakeVariant:
    def __init__(self, inventory_item_id):
        self.inventory_item_id = inventory_item_id


class FakeProduct:
    def __init__(self):
        self.id = 123
        self.title = "Fake Product"
        self.tags = ""
        self.status = "active"
        self.variants = [FakeVariant(999)]

    def save(self):
        return True


class FakeInventoryItem:
    def __init__(self):
        self.cost = None
        self.saved = False

    def save(self):
        self.saved = True
        return True


class SentinelaSmokeTests(unittest.TestCase):
    def _env_getter(self, key, default=None):
        values = {
            "SHOPIFY_SHOP_URL": "fake-shop.myshopify.com",
            "SHOPIFY_ACCESS_TOKEN": "fake-token",
            "SHOPIFY_API_VERSION": "2025-01",
        }
        return values.get(key, default)

    @patch("sentinela.shopify.ShopifyResource.activate_session")
    @patch("sentinela.shopify.Session")
    @patch("sentinela.load_dotenv")
    @patch("sentinela.os.getenv")
    def test_auditar_produto_aciona_kill_switch_por_custo(self, getenv_mock, *_):
        getenv_mock.side_effect = self._env_getter
        sentinela = SentinelSystem()
        product = FakeProduct()

        with patch("sentinela.shopify.Product.find", return_value=product), \
             patch.object(sentinela, "_get_ali_data", return_value=(49.50, 1.00, True)), \
             patch.object(sentinela, "_kill_switch", return_value=True) as kill_switch_mock:
            ok = sentinela.auditar_produto(123, "https://example.com/product")

        self.assertTrue(ok)
        kill_switch_mock.assert_called_once()

    @patch("sentinela.shopify.ShopifyResource.activate_session")
    @patch("sentinela.shopify.Session")
    @patch("sentinela.load_dotenv")
    @patch("sentinela.os.getenv")
    def test_auditar_produto_atualiza_cost_quando_aprovado(self, getenv_mock, *_):
        getenv_mock.side_effect = self._env_getter
        sentinela = SentinelSystem()
        product = FakeProduct()
        inventory_item = FakeInventoryItem()

        with patch("sentinela.shopify.Product.find", return_value=product), \
             patch.object(sentinela, "_get_ali_data", return_value=(20.00, 5.00, True)), \
             patch("sentinela.shopify.InventoryItem.find", return_value=inventory_item):
            ok = sentinela.auditar_produto(123, "https://example.com/product")

        self.assertTrue(ok)
        self.assertEqual(inventory_item.cost, 25.00)
        self.assertTrue(inventory_item.saved)


if __name__ == "__main__":
    unittest.main()
