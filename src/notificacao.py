
import os
import requests
import time
from dotenv import load_dotenv

# Carregar Env
load_dotenv('config/.env')

TELEGRAM_TIMEOUT = int(os.getenv('TELEGRAM_TIMEOUT', '10'))
TELEGRAM_RETRIES = int(os.getenv('TELEGRAM_RETRIES', '3'))
TELEGRAM_BACKOFF_BASE = float(os.getenv('TELEGRAM_BACKOFF_BASE', '1.5'))


def _sleep_backoff(attempt):
    time.sleep(TELEGRAM_BACKOFF_BASE ** max(0, attempt - 1))


def enviar_telegram(mensagem):
    """
    Envia mensagem para o Telegram configurado no .env.
    Nao lanca excecao para nao interromper fluxo principal.
    Retorna True em sucesso, False em falha.
    """
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        print("⚠️  TELEGRAM: Token ou Chat ID não configurados.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": mensagem,
        "parse_mode": "Markdown"
    }

    for attempt in range(1, TELEGRAM_RETRIES + 1):
        try:
            response = requests.post(url, json=payload, timeout=TELEGRAM_TIMEOUT)
            response.raise_for_status()

            data = response.json()
            if not data.get("ok", False):
                desc = data.get("description", "unknown error")
                raise RuntimeError(f"Telegram API returned ok=false: {desc}")

            return True
        except Exception as e:
            print(f"⚠️  ERRO TELEGRAM (tentativa {attempt}/{TELEGRAM_RETRIES}): {e}")
            if attempt < TELEGRAM_RETRIES:
                _sleep_backoff(attempt)

    return False

if __name__ == "__main__":
    enviar_telegram("Teste de notificação Akira System 📡")
