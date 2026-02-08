
import os
import requests
from dotenv import load_dotenv

# Carregar Env
load_dotenv('config/.env')

def enviar_telegram(mensagem):
    """
    Envia mensagem para o Telegram configurado no .env.
    Não lança exceção para não interromper fluxo principal.
    """
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        print("⚠️  TELEGRAM: Token ou Chat ID não configurados.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": mensagem,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        # Sucesso silencioso
    except Exception as e:
        print(f"⚠️  ERRO TELEGRAM: {e}")

if __name__ == "__main__":
    enviar_telegram("Teste de notificação Akira System 📡")
