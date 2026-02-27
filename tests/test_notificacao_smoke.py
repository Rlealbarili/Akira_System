import os
import sys
import unittest
from unittest.mock import patch

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import notificacao


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class NotificacaoSmokeTests(unittest.TestCase):
    def _env_getter(self, key):
        values = {
            "TELEGRAM_BOT_TOKEN": "token",
            "TELEGRAM_CHAT_ID": "chat",
        }
        return values.get(key)

    def test_enviar_telegram_success(self):
        with patch("notificacao.os.getenv", side_effect=self._env_getter), \
             patch("notificacao.requests.post", return_value=FakeResponse({"ok": True})):
            ok = notificacao.enviar_telegram("teste")
        self.assertTrue(ok)

    def test_enviar_telegram_retries_then_success(self):
        side_effects = [RuntimeError("temp error"), FakeResponse({"ok": True})]
        with patch("notificacao.os.getenv", side_effect=self._env_getter), \
             patch("notificacao.time.sleep"), \
             patch("notificacao.requests.post", side_effect=side_effects):
            ok = notificacao.enviar_telegram("teste")
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
