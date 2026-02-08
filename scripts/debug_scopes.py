
import os
import shopify
import requests
from dotenv import load_dotenv

load_dotenv('config/.env')

SHOP_URL = os.getenv('SHOPIFY_SHOP_URL')
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')

def check_scopes():
    print(f"Token: {ACCESS_TOKEN[:10]}...")
    url = f"https://{SHOP_URL}/admin/oauth/access_scopes.json"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            scopes = [s['handle'] for s in data.get('access_scopes', [])]
            print("\n✅ Active Scopes:")
            for s in scopes:
                print(f" - {s}")
                
            if 'read_content' in scopes:
                print("\n🎉 read_content ESTÁ ATIVO!")
            else:
                print("\n❌ read_content NÃO ESTÁ ATIVO.")
        else:
            print(f"❌ Erro ao consultar escopos: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    check_scopes()
