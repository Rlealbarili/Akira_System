
import os
import requests
import json
from dotenv import load_dotenv

# Carregar Env (caso seja importado isoladamente)
load_dotenv('config/.env')

class AkiraBrain:
    def __init__(self):
        self.url = f"{os.getenv('OLLAMA_URL', 'http://localhost:11434')}/api/chat"
        self.model = os.getenv('OLLAMA_MODEL', 'qwen2.5:7b-instruct')

    def gerar_insight(self, produto, old_price, new_price):
        """
        Gera uma justificativa curta para a mudança de preço.
        Retorna string ou None se falhar/timeout.
        """
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "Você é AKIRA, uma IA gestora de e-commerce Cyberpunk. Responda em PT-BR. Seja conciso (max 1 frase). Estilo: Técnico, Frio, Executivo."
                },
                {
                    "role": "user",
                    "content": f"O produto {produto} teve reajuste de R$ {old_price} para R$ {new_price}. Justifique a mudança (ex: flutuação cambial, escassez de silício, demanda)."
                }
            ],
            "stream": False
        }

        try:
            # Timeout de 5s para não travar o sistema principal
            response = requests.post(self.url, json=payload, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            if 'message' in data and 'content' in data['message']:
                return data['message']['content'].strip()
            return None
            
        except requests.exceptions.Timeout:
            print("⚠️  AKIRA BRAIN: Timeout (IA Ocupada).")
            return None
        except Exception as e:
            print(f"⚠️  AKIRA BRAIN ERROR: {e}")
            return None

    def responder_faq(self, pergunta_usuario, dados_produto):
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "Você é o Suporte Técnico da Akira Gear. Especialista em teclados mecânicos e periféricos. Responda de forma curta, prestativa e Cyberpunk. Use os dados do produto fornecidos para ser preciso."
                },
                {
                    "role": "user",
                    "content": f"Contexto do Produto: {dados_produto}. Pergunta do Cliente: {pergunta_usuario}"
                }
            ],
            "stream": False
        }
        try:
            response = requests.post(self.url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            if 'message' in data and 'content' in data['message']:
                return data['message']['content'].strip()
            return "⚠️ O sistema neural está reiniciando... Tente novamente em breve."
        except Exception as e:
            print(f"⚠️  AKIRA FAQ ERROR: {e}")
            return "⚠️ Erro de comunicação com o núcleo."

if __name__ == "__main__":
    # Teste rápido de sanidade
    brain = AkiraBrain()
    insight = brain.gerar_insight("Teste Produto", "100.00", "150.00")
    print(f"Insight: {insight}")
