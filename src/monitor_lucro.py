import os
import requests
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

# Taxas
IMPOSTO_TOTAL = float(os.getenv('IMPOSTO_SIMPLES', 0.04)) + float(os.getenv('IMPOSTO_ICMS', 0.20))
MARGEM_MIN = float(os.getenv('MARGEM_MINIMA', 0.30))

def get_dolar():
    try:
        r = requests.get("https://economia.awesomeapi.com.br/last/USD-BRL")
        return float(r.json()['USDBRL']['ask'])
    except:
        return 6.00 # Fallback

def setup():
    if not ACCESS_TOKEN:
        print(Fore.RED + "❌ TOKEN NÃO ENCONTRADO NO .ENV")
        return False
    session = shopify.Session(SHOP_URL, API_VERSION, ACCESS_TOKEN)
    shopify.ShopifyResource.activate_session(session)
    return True

def auditar():
    if not setup(): return

    dolar = get_dolar()
    print(Fore.CYAN + f"\n=== 🕵️  AKIRA AUDITOR (VOSTOK SERVER) - Dólar: R$ {dolar:.2f} ===\n")
    
    products = shopify.Product.find()
    print(f"{'PRODUTO':<35} | {'PREÇO':<10} | {'CUSTO':<10} | {'LUCRO':<10} | {'MARGEM'}")
    print("-" * 90)

    for p in products:
        for v in p.variants:
            price = float(v.price)
            # Tenta pegar custo, assume 0 se falhar (necessário inventory scope)
            cost = 0.0
            try:
                inv = shopify.InventoryItem.find(v.inventory_item_id)
                if inv.cost: cost = float(inv.cost)
            except: pass

            taxas = price * IMPOSTO_TOTAL
            lucro = price - taxas - cost
            margem = (lucro / price) if price > 0 else 0
            
            cor = Fore.GREEN if margem >= MARGEM_MIN else Fore.RED
            if cost == 0: cor = Fore.YELLOW
            
            print(f"{p.title[:35]:<35} | {price:>10.2f} | {cost:>10.2f} | {lucro:>10.2f} | {cor}{margem*100:>5.1f}%")

if __name__ == "__main__":
    auditar()
