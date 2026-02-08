
import os
import requests
import time
from dotenv import load_dotenv

load_dotenv('config/.env')

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

def get_updates():
    if not TOKEN:
        print("❌ Token não encontrado.")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    
    print(f"📡 Buscando mensagens para @AkiraGear_bot...")
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if not data.get('ok'):
            print(f"❌ Erro na API: {data}")
            return

        result = data.get('result', [])
        
        if not result:
            print("📭 Nenhuma mensagem encontrada.")
            print("👉 Por favor, envie uma mensagem (ex: /start) para o bot e tente novamente.")
            return

        # Pegar a última mensagem
        last_msg = result[-1]
        chat_id = last_msg['message']['chat']['id']
        user = last_msg['message']['from']['first_name']
        
        print(f"\n✅ MENSAGEM RECEBIDA!")
        print(f"👤 Usuário: {user}")
        print(f"🆔 YOUR CHAT ID: {chat_id}")
        print("\n⚠️  Copiando ID para o arquivo .env automaticamente...")
        
        # Atualizar .env (Isso é um hack simples, idealmente usar regex ou parser)
        env_path = 'config/.env'
        with open(env_path, 'r') as f:
            lines = f.readlines()
            
        with open(env_path, 'w') as f:
            for line in lines:
                if line.startswith('TELEGRAM_CHAT_ID='):
                    f.write(f'TELEGRAM_CHAT_ID="{chat_id}"\n')
                else:
                    f.write(line)
        print("💾 .env atualizado com sucesso!")

    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

if __name__ == "__main__":
    get_updates()
