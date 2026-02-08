
import os
import requests
from dotenv import load_dotenv

load_dotenv('config/.env')

SHOP_URL = os.getenv('SHOPIFY_SHOP_URL')
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')

def revoke_token():
    if not ACCESS_TOKEN:
        print("❌ Nenhum token para revogar.")
        return

    print(f"Revogando token: {ACCESS_TOKEN[:10]}...")
    url = f"https://{SHOP_URL}/admin/api_permissions/current.json"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            print("✅ Token revogado com sucesso! O próximo login irá gerar um novo.")
        else:
            print(f"❌ Erro ao revogar token: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    revoke_token()
