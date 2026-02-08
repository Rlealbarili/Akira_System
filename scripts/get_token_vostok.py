import os
import requests
from dotenv import load_dotenv

# Carregar variáveis
load_dotenv('config/.env')

SHOP_URL = os.getenv('SHOPIFY_SHOP_URL')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
SCOPES = "read_products,write_products,read_orders,write_orders,read_draft_orders,write_draft_orders,read_inventory,write_inventory,read_content,write_content,read_themes,write_themes,read_script_tags,write_script_tags,read_price_rules,write_price_rules,read_discounts,write_discounts,read_marketing_events,write_marketing_events,read_resource_feedbacks,read_shopify_payments_payouts,read_locations,read_translations,write_translations"
REDIRECT_URI = "http://localhost" # Padrão para Partners

def gerar_token():
    print(f"\n{'='*60}")
    print(f"🔐 PROTOCOLO DE AUTENTICAÇÃO VOSTOK - AKIRA SYSTEM")
    print(f"{'='*60}")
    
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ ERRO: CLIENT_ID e CLIENT_SECRET estão vazios no arquivo config/.env")
        return

    # 1. Gerar URL
    auth_url = (
        f"https://{SHOP_URL}/admin/oauth/authorize?"
        f"client_id={CLIENT_ID}&"
        f"scope={SCOPES}&"
        f"redirect_uri={REDIRECT_URI}"
    )
    
    print("\n👉 1. COPIE ESTA URL E ABRA NO SEU NAVEGADOR LOCAL (FORA DO SSH):")
    print("-" * 80)
    print(auth_url)
    print("-" * 80)
    
    print("\n👉 2. Após autorizar, você será redirecionado para uma página de erro (Localhost).")
    print("👉 3. Copie o código que aparece na URL (ex: .../?code=SEU_CODIGO_AQUI...)")
    
    code = input("\n⌨️  COLE O CÓDIGO AQUI E APERTE ENTER: ").strip()
    
    # 2. Trocar Code por Token
    url = f"https://{SHOP_URL}/admin/oauth/access_token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code
    }
    
    print("\n🔄 Trocando código por Token Permanente...")
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        token = response.json().get('access_token')
        print("\n" + "✅"*10 + " SUCESSO! " + "✅"*10)
        print(f"\nSEU TOKEN DE ACESSO (shpat_): \n{token}\n")
        print("⚠️  AGORA ADICIONE ESTE TOKEN NO ARQUIVO config/.env")
    else:
        print(f"\n❌ FALHA: {response.text}")

if __name__ == "__main__":
    gerar_token()
