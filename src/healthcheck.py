import argparse
import json
import os
import time

import requests
import shopify
from colorama import Fore, Style, init as colorama_init
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

colorama_init(autoreset=True)


class AkiraHealthcheck:
    def __init__(self, timeout=8, strict=False):
        load_dotenv("config/.env")
        self.timeout = int(timeout)
        self.strict = bool(strict)

    def _log(self, level, message):
        colors = {
            "PASS": Fore.GREEN,
            "WARN": Fore.YELLOW,
            "FAIL": Fore.RED,
            "INFO": Fore.CYAN,
        }
        color = colors.get(level, Fore.WHITE)
        print(f"{color}[HEALTH/{level}] {Style.RESET_ALL}{message}")

    def _run_check(self, name, check_fn):
        started = time.time()
        try:
            status, detail = check_fn()
        except Exception as exc:
            status = "FAIL"
            detail = f"unexpected error: {exc}"
        elapsed_ms = int((time.time() - started) * 1000)
        return {
            "name": name,
            "status": status,
            "detail": detail,
            "elapsed_ms": elapsed_ms,
        }

    def _check_env(self):
        required = [
            "SHOPIFY_SHOP_URL",
            "SHOPIFY_ACCESS_TOKEN",
            "SHOPIFY_API_VERSION",
            "TELEGRAM_BOT_TOKEN",
            "TELEGRAM_CHAT_ID",
            "OLLAMA_URL",
            "OLLAMA_MODEL",
        ]
        missing = [key for key in required if not os.getenv(key)]
        if missing:
            return "FAIL", f"missing env vars: {', '.join(missing)}"
        return "PASS", "all required env vars found"

    def _check_shopify(self):
        shop_url = os.getenv("SHOPIFY_SHOP_URL")
        token = os.getenv("SHOPIFY_ACCESS_TOKEN")
        api_version = os.getenv("SHOPIFY_API_VERSION")
        if not shop_url or not token or not api_version:
            return "FAIL", "missing Shopify env vars"

        try:
            session = shopify.Session(shop_url, api_version, token)
            shopify.ShopifyResource.activate_session(session)
            shop = shopify.Shop.current()
            shop_name = getattr(shop, "name", "unknown-shop")
            return "PASS", f"connected to Shopify shop '{shop_name}'"
        except Exception as exc:
            return "FAIL", f"Shopify API failed: {exc}"

    def _check_telegram(self):
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            return "FAIL", "missing TELEGRAM_BOT_TOKEN"

        url = f"https://api.telegram.org/bot{token}/getMe"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
            if not payload.get("ok"):
                return "FAIL", f"Telegram API returned ok=false: {payload}"
            username = payload.get("result", {}).get("username", "unknown")
            return "PASS", f"telegram bot reachable (@{username})"
        except Exception as exc:
            return "FAIL", f"Telegram API failed: {exc}"

    def _check_ollama(self):
        base_url = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
        try:
            response = requests.get(f"{base_url}/api/tags", timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
            models = payload.get("models", [])
            return "PASS", f"ollama reachable ({len(models)} models visible)"
        except Exception as exc:
            return "FAIL", f"Ollama API failed: {exc}"

    def _check_playwright(self):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto("about:blank")
                browser.close()
            return "PASS", "playwright chromium launch ok"
        except Exception as exc:
            return "FAIL", f"playwright check failed: {exc}"

    def run(self):
        checks = [
            ("ENV", self._check_env, True),
            ("SHOPIFY", self._check_shopify, True),
            ("TELEGRAM", self._check_telegram, True),
            ("OLLAMA", self._check_ollama, False),
            ("PLAYWRIGHT", self._check_playwright, True),
        ]

        self._log("INFO", "starting AKIRA healthcheck")
        results = []
        has_critical_fail = False
        has_warning = False

        for name, fn, critical in checks:
            result = self._run_check(name, fn)
            results.append(result)
            status = result["status"]
            detail = result["detail"]
            elapsed = result["elapsed_ms"]

            if status == "PASS":
                self._log("PASS", f"{name} ok ({elapsed} ms) - {detail}")
            elif status == "WARN":
                has_warning = True
                self._log("WARN", f"{name} warn ({elapsed} ms) - {detail}")
            else:
                if critical:
                    has_critical_fail = True
                self._log("FAIL", f"{name} fail ({elapsed} ms) - {detail}")

        ok = not has_critical_fail and not (self.strict and has_warning)
        summary = {
            "timestamp": int(time.time()),
            "ok": ok,
            "strict": self.strict,
            "results": results,
        }
        return summary


def main():
    parser = argparse.ArgumentParser(description="AKIRA central healthcheck")
    parser.add_argument("--strict", action="store_true", help="fail on warnings")
    parser.add_argument("--timeout", type=int, default=8, help="request timeout seconds")
    parser.add_argument("--json-out", default="", help="optional json report path")
    args = parser.parse_args()

    checker = AkiraHealthcheck(timeout=args.timeout, strict=args.strict)
    summary = checker.run()

    if args.json_out:
        out_path = args.json_out
        out_dir = os.path.dirname(out_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as file_obj:
            json.dump(summary, file_obj, indent=2)

    if summary["ok"]:
        print(Fore.GREEN + "[HEALTH/INFO] overall status: OK")
        raise SystemExit(0)
    print(Fore.RED + "[HEALTH/INFO] overall status: FAIL")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
