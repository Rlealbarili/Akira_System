
import os
import shopify
from dotenv import load_dotenv

load_dotenv('config/.env')

SHOP_URL = os.getenv('SHOPIFY_SHOP_URL')
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')
API_VERSION = os.getenv('SHOPIFY_API_VERSION')

session = shopify.Session(SHOP_URL, API_VERSION, ACCESS_TOKEN)
shopify.ShopifyResource.activate_session(session)

print("Tentando acessar produtos...")
products = shopify.Product.find(limit=1)
if not products:
    print("Nenhum produto encontrado.")
else:
    p = products[0]
    v = p.variants[0]
    print(f"Produto: {p.title}")
    print(f"Variant ID: {v.id}, Inventory Item ID: {v.inventory_item_id}")
    
    try:
        print("Tentando acessar InventoryItem...")
        inv = shopify.InventoryItem.find(v.inventory_item_id)
        print(f"Sucesso! Cost: {inv.cost}")
    except Exception as e:
        print(f"ERRO ao acessar InventoryItem: {e}")
