import os
import sys
import unittest
from unittest.mock import patch

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from akira_brain import AkiraBrain


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class AkiraBrainSmokeTests(unittest.TestCase):
    def test_gerar_insight_returns_content(self):
        brain = AkiraBrain()
        brain.retries = 1
        payload = {"message": {"content": "Insight gerado"}}

        with patch("akira_brain.requests.post", return_value=FakeResponse(payload)):
            result = brain.gerar_insight("Produto", "100.00", "120.00")

        self.assertEqual(result, "Insight gerado")

    def test_responder_faq_returns_error_message_on_failure(self):
        brain = AkiraBrain()
        brain.retries = 1

        with patch("akira_brain.requests.post", side_effect=RuntimeError("offline")):
            result = brain.responder_faq("Pergunta", "Contexto")

        self.assertIn("Erro de comunicação", result)


if __name__ == "__main__":
    unittest.main()
