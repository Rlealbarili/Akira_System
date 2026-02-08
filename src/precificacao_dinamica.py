
import os
import requests
import shopify
import math
import datetime
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Importar novos módulos
try:
    from akira_brain import AkiraBrain
    from notificacao import enviar_telegram
except ImportError:
    # Fallback para execução fora da pasta src
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from akira_brain import AkiraBrain
    from notificacao import enviar_telegram

# Init Colorama
init(autoreset=True)

# Carregar Env
load_dotenv('config/.env')

SHOP_URL = os.getenv('SHOPIFY_SHOP_URL')
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')
API_VERSION = os.getenv('SHOPIFY_API_VERSION')

# Taxas e Margens
IMPOSTO_TOTAL = float(os.getenv('IMPOSTO_SIMPLES', 0.04)) + float(os.getenv('IMPOSTO_ICMS', 0.20))
MARGEM_MIN = float(os.getenv('MARGEM_MINIMA', 0.20)) # Ajustado para 0.20
MARGEM_ALVO = 0.35

# Instanciar Brain
brain = AkiraBrain()

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

def calcular_novo_preco(custo, margem_alvo=MARGEM_ALVO):
    """
    Fórmula: Preço = Custo / (1 - (Impostos + Margem_Alvo))
    Arredondar para o final ".90" (ex: 154.90)
    """
    if custo <= 0: return 0.0
    
    divisor = 1 - (IMPOSTO_TOTAL + margem_alvo)
    if divisor <= 0: return 0.0
    
    preco_base = custo / divisor
    
    novo_preco = math.ceil(preco_base) - 0.10
    
    if novo_preco < preco_base:
        novo_preco += 1.0
        
    return round(novo_preco, 2)

def auditar_e_precificar():
    if not setup(): return

    print(Fore.CYAN + f"\n=== 🧠  AKIRA DYNAMIC PRICING + BRAIN (VOSTOK) ===\n")
    print(f"Margem Mínima: {MARGEM_MIN*100:.0f}% | Margem Alvo: {MARGEM_ALVO*100:.0f}% | Impostos: {IMPOSTO_TOTAL*100:.0f}%")
    
    products = shopify.Product.find()
    
    logfile_path = 'logs/pricing.log'
    os.makedirs('logs', exist_ok=True)
    
    print(f"\n{'PRODUTO':<35} | {'PREÇO ATUAL':<12} | {'NOVO PREÇO':<12} | {'AÇÃO'}")
    print("-" * 80)

    for p in products:
        for v in p.variants:
            price = float(v.price)
            cost = 0.0
            try:
                inv = shopify.InventoryItem.find(v.inventory_item_id)
                if inv.cost: cost = float(inv.cost)
            except: pass
            
            if cost == 0:
                print(f"{p.title[:35]:<35} | {price:>10.2f}   | {'-':>10}   | {Fore.YELLOW}Ignorado (Sem Custo)")
                continue

            taxas_valor = price * IMPOSTO_TOTAL
            lucro = price - taxas_valor - cost
            margem = (lucro / price) if price > 0 else 0
            
            if margem < MARGEM_MIN:
                novo_preco = calcular_novo_preco(cost, MARGEM_ALVO)
                
                # Executar Alteração
                v.price = novo_preco
                v.save()
                
                # 🧠 AKIRA BRAIN INSIGHT
                print(f"{Fore.MAGENTA}   🧠 Solicitando análise do Akira Brain...")
                motivo = brain.gerar_insight(p.title, price, novo_preco)
                if not motivo:
                    motivo = "Reajuste automático de margem de segurança."
                
                # Montar Notificação
                emoji = "📉" if novo_preco < price else "📈"
                msg_telegram = (
                    f"⚠️ **AKIRA SYSTEM: REPRIFICAÇÃO**\n"
                    f"🛒 **Produto:** {p.title}\n"
                    f"📉 **De:** R$ {price:.2f}\n"
                    f"{emoji} **Para:** R$ {novo_preco:.2f}\n"
                    f"🧠 **Análise:** {motivo}"
                )
                
                # Logar
                log_msg = f"ALERTA: {p.title} ajustado de R$ {price} para R$ {novo_preco}. Motivo: {motivo}"
                print(f"{p.title[:35]:<35} | {price:>10.2f}   | {novo_preco:>10.2f}   | {Fore.GREEN}ATUALIZADO 🔼")
                print(f"   📝 Insight: {motivo}")
                
                with open(logfile_path, "a") as f:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"[{timestamp}] {log_msg}\n")
                    
                # 📡 Enviar Telegram
                enviar_telegram(msg_telegram)
                
            else:
                print(f"{p.title[:35]:<35} | {price:>10.2f}   | {'-':>10}   | {Fore.BLUE}Mantido (OK)")

if __name__ == "__main__":
    auditar_e_precificar()
