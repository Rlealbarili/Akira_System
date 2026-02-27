import os
import sys
import unittest
from unittest.mock import patch

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from healthcheck import AkiraHealthcheck


class HealthcheckSmokeTests(unittest.TestCase):
    def test_run_fails_when_critical_check_fails(self):
        checker = AkiraHealthcheck(strict=False)
        with patch.object(AkiraHealthcheck, "_check_env", return_value=("PASS", "ok")), \
             patch.object(AkiraHealthcheck, "_check_shopify", return_value=("FAIL", "down")), \
             patch.object(AkiraHealthcheck, "_check_telegram", return_value=("PASS", "ok")), \
             patch.object(AkiraHealthcheck, "_check_ollama", return_value=("PASS", "ok")), \
             patch.object(AkiraHealthcheck, "_check_playwright", return_value=("PASS", "ok")):
            summary = checker.run()
        self.assertFalse(summary["ok"])

    def test_run_passes_when_only_non_critical_fails(self):
        checker = AkiraHealthcheck(strict=False)
        with patch.object(AkiraHealthcheck, "_check_env", return_value=("PASS", "ok")), \
             patch.object(AkiraHealthcheck, "_check_shopify", return_value=("PASS", "ok")), \
             patch.object(AkiraHealthcheck, "_check_telegram", return_value=("PASS", "ok")), \
             patch.object(AkiraHealthcheck, "_check_ollama", return_value=("FAIL", "ollama down")), \
             patch.object(AkiraHealthcheck, "_check_playwright", return_value=("PASS", "ok")):
            summary = checker.run()
        self.assertTrue(summary["ok"])


if __name__ == "__main__":
    unittest.main()
