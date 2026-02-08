import shopify
import os
import requests
import json
from dotenv import load_dotenv

# Load Admin Environment
load_dotenv('config/.env')

SHOP_URL = os.getenv('SHOPIFY_SHOP_URL')
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')
API_VERSION = "2024-04" # Using a recent version

def generate_token_graphql():
    if not ACCESS_TOKEN:
        print("❌ Admin Access Token not found.")
        return

    print(f"Connecting to {SHOP_URL} via GraphQL...")
    
    url = f"https://{SHOP_URL}/admin/api/{API_VERSION}/graphql.json"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    
    mutation = """
    mutation storefrontAccessTokenCreate($input: StorefrontAccessTokenInput!) {
      storefrontAccessTokenCreate(input: $input) {
        storefrontAccessToken {
          accessToken
          title
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    
    variables = {
        "input": {
            "title": "Akira Headless GraphQL"
        }
    }
    
    try:
        response = requests.post(url, json={"query": mutation, "variables": variables}, headers=headers)
        data = response.json()
        
        if 'errors' in data:
            print(f"❌ GraphQL Error: {data['errors']}")
            return

        result = data.get('data', {}).get('storefrontAccessTokenCreate', {})
        user_errors = result.get('userErrors', [])
        
        if user_errors:
            print(f"❌ User Errors: {user_errors}")
            return
            
        token = result.get('storefrontAccessToken', {}).get('accessToken')
        if token:
            print(f"✅ SUCCESS! Storefront Access Token: {token}")
            
            # Update .env.local
            env_path = "akira_system/frontend/.env.local"
            # Adjust path if running from root or akira_system
            if not os.path.exists(env_path):
                env_path = "frontend/.env.local"

            print(f"Updating {env_path}...")
            
            with open(env_path, 'r') as f:
                lines = f.readlines()
                
            with open(env_path, 'w') as f:
                for line in lines:
                    if line.startswith("NEXT_PUBLIC_SHOPIFY_STOREFRONT_ACCESS_TOKEN="):
                        f.write(f'NEXT_PUBLIC_SHOPIFY_STOREFRONT_ACCESS_TOKEN="{token}"\n')
                    else:
                        f.write(line)
        else:
            print("❌ No token returned in response.")
            print(json.dumps(data, indent=2))

    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    generate_token_graphql()
