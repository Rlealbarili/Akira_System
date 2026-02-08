import requests
import json
import os

# Configuration
SHOP_DOMAIN = "akira-13004.myshopify.com"
STOREFRONT_TOKEN = "d60b874559eed51c92bd873f6182eb80"
API_VERSION = "2024-01"

def test_storefront():
    url = f"https://{SHOP_DOMAIN}/api/{API_VERSION}/graphql.json"
    
    headers = {
        "X-Shopify-Storefront-Access-Token": STOREFRONT_TOKEN,
        "Content-Type": "application/json"
    }
    
    query = """
    {
      shop {
        name
        description
        primaryDomain {
          url
        }
      }
      products(first: 3) {
        edges {
          node {
            title
            handle
          }
        }
      }
    }
    """
    
    print(f"📡 Connecting to Storefront API: {url}")
    
    try:
        response = requests.post(url, json={"query": query}, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if "errors" in data:
                print(f"❌ GraphQL Errors: {json.dumps(data['errors'], indent=2)}")
            else:
                print("✅ Connection Successful!")
                shop = data['data']['shop']
                print(f"🏠 Shop Name: {shop['name']}")
                print(f"🔗 URL: {shop['primaryDomain']['url']}")
                
                products = data['data']['products']['edges']
                print(f"📦 Found {len(products)} products:")
                for p in products:
                    print(f"   - {p['node']['title']}")
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    test_storefront()
