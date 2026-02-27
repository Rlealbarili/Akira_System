
import os
import requests
import time
import shopify
from dotenv import load_dotenv
from akira_brain import AkiraBrain

# Carregar Env
load_dotenv('config/.env')

# Config
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SHOP_URL = os.getenv('SHOPIFY_SHOP_URL')
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')
API_VERSION = os.getenv('SHOPIFY_API_VERSION')

TELEGRAM_GET_TIMEOUT = int(os.getenv('TELEGRAM_GET_TIMEOUT', '35'))
TELEGRAM_SEND_TIMEOUT = int(os.getenv('TELEGRAM_SEND_TIMEOUT', '10'))
TELEGRAM_RETRIES = int(os.getenv('TELEGRAM_RETRIES', '3'))
TELEGRAM_BACKOFF_BASE = float(os.getenv('TELEGRAM_BACKOFF_BASE', '1.5'))

# Setup Brain
brain = AkiraBrain()
CACHE_PRODUTOS = []


def setup_shopify():
    if not ACCESS_TOKEN:
        print("❌ TOKEN NÃO ENCONTRADO NO .ENV")
        return False
    try:
        session = shopify.Session(SHOP_URL, API_VERSION, ACCESS_TOKEN)
        shopify.ShopifyResource.activate_session(session)
        return True
    except Exception as e:
        print(f"❌ Erro ao ativar sessão Shopify: {e}")
        return False


def _sleep_backoff(attempt):
    time.sleep(TELEGRAM_BACKOFF_BASE ** max(0, attempt - 1))


def _telegram_get_json(url, timeout, retries):
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            last_error = e
            print(f"⚠️ Telegram GET falhou ({attempt}/{retries}): {e}")
            if attempt < retries:
                _sleep_backoff(attempt)
    raise RuntimeError(last_error)


def _telegram_post_json(url, payload, timeout, retries):
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            response = requests.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            last_error = e
            print(f"⚠️ Telegram POST falhou ({attempt}/{retries}): {e}")
            if attempt < retries:
                _sleep_backoff(attempt)
    raise RuntimeError(last_error)

def get_product_context(query):
    """
    Busca simples: retorna dados do primeiro produto que conter a palavra-chave no título.
    Idealmente, faria um cache, mas para MVP vamos buscar na API ou usar uma lista pré-carregada.
    Para ser rápido e não estourar API rate limit, vamos carregar tudo na memória ao iniciar (Cache Simples).
    """
    return [p for p in CACHE_PRODUTOS if query.lower() in p.title.lower()]

def carregar_produtos():
    print("📦 Carregando catálogo de produtos...")
    try:
        return shopify.Product.find()
    except Exception as e:
        print(f"❌ Erro ao carregar produtos: {e}")
        return []

def refresh_cache():
    global CACHE_PRODUTOS
    CACHE_PRODUTOS = carregar_produtos()

def handle_updates(last_id):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id+1}&timeout=30"
    try:
        data = _telegram_get_json(url, timeout=TELEGRAM_GET_TIMEOUT, retries=TELEGRAM_RETRIES)
        
        if not data.get('ok'): return last_id
        
        results = data.get('result', [])
        
        for msg in results:
            update_id = msg['update_id']
            if update_id > last_id:
                last_id = update_id
                
                if 'message' in msg and 'text' in msg['message']:
                    chat_id = msg['message']['chat']['id']
                    user_text = msg['message']['text']
                    user_name = msg['message']['from'].get('first_name', 'Usuário')
                    
                    print(f"📩 Mensagem de {user_name}: {user_text}")
                    
                    # Lógica de Atendimento
                    produtos_encontrados = get_product_context(user_text)
                    
                    if produtos_encontrados:
                        # Pega o primeiro
                        p = produtos_encontrados[0]
                        variants_info = ", ".join([f"{v.title}: R$ {v.price}" for v in p.variants])
                        product_data = f"Nome: {p.title}. Variantes/Preços: {variants_info}. Descrição: {p.body_html[:200]}..."
                        
                        resposta = brain.responder_faq(user_text, product_data)
                    else:
                        # Resposta genérica
                        resposta = brain.responder_faq(user_text, "Nenhum produto específico identificado. Responda como suporte geral da loja.")

                    # Enviar Resposta
                    send_msg(chat_id, resposta)
                    
        return last_id
        
    except Exception as e:
        print(f"⚠️ Erro no loop: {e}")
        time.sleep(5)
        return last_id

def send_msg(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        data = _telegram_post_json(
            url,
            {"chat_id": chat_id, "text": text},
            timeout=TELEGRAM_SEND_TIMEOUT,
            retries=TELEGRAM_RETRIES,
        )
        if not data.get('ok'):
            print(f"⚠️ Telegram retornou ok=false ao enviar mensagem: {data}")
    except Exception as e:
        print(f"⚠️ Falha ao enviar resposta no Telegram: {e}")

if __name__ == "__main__":
    if not TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN não configurado.")
        raise SystemExit(1)
    if not setup_shopify():
        raise SystemExit(1)

    refresh_cache()
    print("🎧 AKIRA LISTENER: Monitorando Telegram...")
    last_update_id = 0
    while True:
        last_update_id = handle_updates(last_update_id)
        time.sleep(1)
