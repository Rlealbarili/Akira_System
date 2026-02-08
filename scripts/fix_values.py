
import os
import shopify
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Init Colorama
init(autoreset=True)

# Carregar Env
load_dotenv('config/.env')

SHOP_URL = os.getenv('SHOPIFY_SHOP_URL')
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')
API_VERSION = os.getenv('SHOPIFY_API_VERSION')

def setup():
    if not ACCESS_TOKEN:
        print(Fore.RED + "❌ TOKEN NÃO ENCONTRADO NO .ENV")
        return False
    try:
        session = shopify.Session(SHOP_URL, API_VERSION, ACCESS_TOKEN)
        shopify.ShopifyResource.activate_session(session)
        return True
    except Exception as e:
        print(Fore.RED + f"❌ ERRO DE CONEXÃO: {e}")
        return False

def fix_values():
    if not setup(): return
    
    # 1. Reverter Preço do Magan
    # 2. Corrigir Custo do Miku
    
    products = shopify.Product.find()
    
    for p in products:
        # Ação 1: Magan Keycap (Reverter Preço)
        if "Magan Keycap" in p.title:
            print(f"\n📦 ENCONTRADO: {p.title}")
            for v in p.variants:
                if "Magan-KR" in v.title or "Magan-EN" in v.title or "China Mainland" in v.title:
                    old_price = v.price
                    # Reverter para 297.90
                    target_price = "297.90"
                    
                    if old_price != target_price:
                        v.price = target_price
                        v.save()
                        print(f"   🔄 PREÇO REVERTIDO: R$ {old_price} -> R$ {target_price}")
                    else:
                        print(f"   ✅ PREÇO JÁ ESTÁ EM R$ {target_price}")

        # Ação 2: Miku Keycap (Setar Custo)
        if "Miku" in p.title:
            print(f"\n📦 ENCONTRADO: {p.title}")
            for v in p.variants:
                if "73 keys" in v.title:
                    try:
                        inv = shopify.InventoryItem.find(v.inventory_item_id)
                        old_cost = inv.cost
                        target_cost = "96.60"
                        
                        if str(old_cost) != target_cost:
                            inv.cost = target_cost
                            inv.save()
                            print(f"   💰 CUSTO ATUALIZADO (73 keys): R$ {old_cost} -> R$ {target_cost}")
                        else:
                            print(f"   ✅ CUSTO JÁ ESTÁ EM R$ {target_cost}")
                    except Exception as e:
                        print(f"   ❌ ERRO AO ATUALIZAR CUSTO: {e}")

if __name__ == "__main__":
    print(Fore.CYAN + "=== 🛠️  AKIRA VALUE FIXER ===\n")
    fix_values()
