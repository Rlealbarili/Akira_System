import os
import sys
import unittest
from unittest.mock import patch

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import suporte_akira


class SuporteSmokeTests(unittest.TestCase):
    def test_handle_updates_processes_message(self):
        fake_updates = {
            "ok": True,
            "result": [
                {
                    "update_id": 5,
                    "message": {
                        "chat": {"id": 99},
                        "text": "oi",
                        "from": {"first_name": "Tester"},
                    },
                }
            ],
        }

        with patch("suporte_akira._telegram_get_json", return_value=fake_updates), \
             patch("suporte_akira.get_product_context", return_value=[]), \
             patch("suporte_akira.brain.responder_faq", return_value="resposta"), \
             patch("suporte_akira.send_msg") as send_msg_mock:
            last_id = suporte_akira.handle_updates(0)

        self.assertEqual(last_id, 5)
        send_msg_mock.assert_called_once_with(99, "resposta")

    def test_handle_updates_returns_last_id_on_error(self):
        with patch("suporte_akira._telegram_get_json", side_effect=RuntimeError("timeout")), \
             patch("suporte_akira.time.sleep"):
            last_id = suporte_akira.handle_updates(7)
        self.assertEqual(last_id, 7)


if __name__ == "__main__":
    unittest.main()
