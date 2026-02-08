import shopify
import os
from dotenv import load_dotenv

# Load Admin Environment
load_dotenv('config/.env')

SHOP_URL = os.getenv('SHOPIFY_SHOP_URL')
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')
API_VERSION = os.getenv('SHOPIFY_API_VERSION')

def generate_storefront_token():
    if not ACCESS_TOKEN:
        print("❌ Admin Access Token not found.")
        return

    print(f"Connecting to {SHOP_URL}...")
    session = shopify.Session(SHOP_URL, API_VERSION, ACCESS_TOKEN)
    shopify.ShopifyResource.activate_session(session)

    # Check for existing tokens
    print("Checking for existing Storefront Access Tokens...")
    tokens = shopify.StorefrontAccessToken.find()
    
    token_value = None
    
    for token in tokens:
        print(f"Found token: {token.title}")
        if token.title == "Akira Headless":
            token_value = token.access_token
            print("✅ Found existing 'Akira Headless' token.")
            break
            
    if not token_value:
        print("Creating new Storefront Access Token 'Akira Headless'...")
        new_token = shopify.StorefrontAccessToken.create({
            "title": "Akira Headless"
        })
        if new_token.errors:
            print(f"❌ Error creating token: {new_token.errors.full_messages()}")
        else:
            token_value = new_token.access_token
            print("✅ Token created successfully.")

    if token_value:
        print(f"Storefront Access Token: {token_value}")
        
        # Update .env.local
        env_path = "frontend/.env.local"
        
        # Read existing content
        with open(env_path, 'r') as f:
            lines = f.readlines()
            
        # Write new content
        with open(env_path, 'w') as f:
            for line in lines:
                if line.startswith("NEXT_PUBLIC_SHOPIFY_STOREFRONT_ACCESS_TOKEN="):
                    f.write(f'NEXT_PUBLIC_SHOPIFY_STOREFRONT_ACCESS_TOKEN="{token_value}"\n')
                else:
                    f.write(line)
                    
        print(f"✅ Updated {env_path} with the new token.")
    
    shopify.ShopifyResource.clear_session()

if __name__ == "__main__":
    generate_storefront_token()
