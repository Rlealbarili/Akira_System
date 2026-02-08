
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

# Dados das Páginas
PAGES_DATA = {
    "SYSTEM ORIGIN // AKIRA": """
    <h2>ORIGIN</h2>
    <p>Nós não vendemos brinquedos. Forjamos ferramentas de interface.</p>
    <p>A Akira Gear nasceu da necessidade de precisão absoluta. Em um mundo de plástico e ruído, oferecemos densidade, PBT e silêncio tático.</p>
    <p>Nossa curadoria de hardware é feita para quem entende que o milissegundo define o vencedor.</p>
    <hr>
    <p><strong>EST. 2026 // SYSTEMS ONLINE.</strong></p>
    """,

    "LOGISTICS PROTOCOL // GLOBAL": """
    <h2>GLOBAL DISTRIBUTION NODES</h2>
    <p>Operamos com distribuição descentralizada direta da Ásia.</p>
    <ul>
        <li><strong>PRAZO ESTIMADO:</strong> 10 a 25 dias úteis.</li>
        <li><strong>RASTREAMENTO:</strong> Obrigatório. O ID de monitoramento é injetado no seu sistema em até 72h.</li>
    </ul>
    <p>A transparência é absoluta. Acompanhe a trajetória do pacote em tempo real através do nosso sistema.</p>
    """,

    "RMA & WARRANTY // PROTOCOL": """
    <h2>7-DAY PROTOCOL</h2>
    <p>Se o hardware não atender aos parâmetros, você tem <strong>7 dias corridos</strong> após o recebimento para iniciar o protocolo de devolução.</p>
    <p>Sem burocracia. Sem perguntas irrelevantes.</p>
    <p>Garantia de integridade ativa contra defeitos de fabricação.</p>
    """
}

def create_pages():
    if not setup(): return

    print(Fore.CYAN + "=== 🏗️  AKIRA FRONTEND SETUP ===\n")

    for title, body in PAGES_DATA.items():
        # Verificar se já existe
        existing_pages = shopify.Page.find(title=title)
        
        if existing_pages:
            print(f"{Fore.YELLOW}⚠️  Página '{title}' já existe (Skipping).")
        else:
            # Criar página
            new_page = shopify.Page()
            new_page.title = title
            new_page.body_html = body.strip()
            new_page.published = True
            
            if new_page.save():
                print(f"{Fore.GREEN}✅ Página '{title}' injetada com sucesso.")
            else:
                print(f"{Fore.RED}❌ Erro ao criar '{title}': {new_page.errors.full_messages()}")

if __name__ == "__main__":
    create_pages()
