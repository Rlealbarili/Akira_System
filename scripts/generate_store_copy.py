
import os
from colorama import Fore, Style, init

# Init Colorama
init(autoreset=True)

# Config
OUTPUT_DIR = "data/content"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Conteúdo Definido
CONTENT_MAP = {
    "about_mission.html": """
    <h3>SYSTEM ORIGIN // AKIRA</h3>
    <p>Nós não vendemos brinquedos. Forjamos ferramentas de interface.
    A Akira Gear nasceu da necessidade de precisão absoluta. Em um mundo de plástico e ruído, oferecemos densidade, PBT e silêncio tático.
    Nossa curadoria de hardware é feita para quem entende que o milissegundo define o vencedor.
    Design industrial. Engenharia acústica. Estética nevrálgica.
    Bem-vindo ao sistema.</p>
    """,
    
    "logistics_protocol.html": """
    <h3>LOGISTICS PROTOCOL // GLOBAL</h3>
    <p>Operamos com nodes de distribuição internacional descentralizados.
    Ao iniciar uma aquisição, seu hardware é despachado diretamente da linha de montagem asiática para sua base.
    <br><br>
    // PRAZO ESTIMADO: 10 a 25 dias úteis.
    <br>
    // RASTREAMENTO: Obrigatório. O ID de monitoramento será injetado no seu e-mail em até 72h.
    <br><br>
    A transparência é absoluta. Acompanhe a trajetória do pacote em tempo real.</p>
    """,
    
    "satisfaction_guarantee.html": """
    <h3>RMA & WARRANTY // PROTOCOL</h3>
    <p>Se o hardware não atender aos parâmetros de qualidade esperados, você tem 7 dias corridos após o recebimento para iniciar o protocolo de devolução.
    Sem burocracia. Sem perguntas irrelevantes.
    Garantia de integridade ativa contra defeitos de fabricação.
    Nossa reputação é baseada na solidez do nosso equipamento.</p>
    """,
    
    "footer_tagline.html": """
    <p>AKIRA GEAR // SYSTEMS ONLINE. FORGED FOR ENTHUSIASTS. EST. 2026.</p>
    """
}

def generate_content():
    print(Fore.CYAN + "=== 🖋️  AKIRA PRIME CONTENT GENERATOR ===\n")
    
    for filename, content in CONTENT_MAP.items():
        filepath = os.path.join(OUTPUT_DIR, filename)
        # Limpar indentação extra para o arquivo final
        clean_content = "\n".join([line.strip() for line in content.strip().splitlines()])
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(clean_content)
        
        print(f"✅ Gerado: {Fore.YELLOW}{filepath}")
    
    print(Fore.GREEN + "\n✅ Ativos de texto gerados em data/content/. Copie e cole na Shopify.")

if __name__ == "__main__":
    generate_content()
