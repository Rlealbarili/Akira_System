
import os
import requests
import time
from dotenv import load_dotenv

# Carregar Env (caso seja importado isoladamente)
load_dotenv('config/.env')

class AkiraBrain:
    def __init__(self):
        self.base_url = os.getenv('OLLAMA_URL', 'http://localhost:11434').rstrip('/')
        self.url = f"{self.base_url}/api/chat"
        self.model = os.getenv('OLLAMA_MODEL', 'qwen2.5:7b-instruct')
        self.retries = int(os.getenv('OLLAMA_RETRIES', '2'))
        self.backoff = float(os.getenv('OLLAMA_BACKOFF_BASE', '1.6'))

    def _chat(self, payload, timeout):
        last_error = None
        for attempt in range(1, self.retries + 1):
            try:
                response = requests.post(self.url, json=payload, timeout=timeout)
                response.raise_for_status()
                data = response.json()

                if 'message' in data and 'content' in data['message']:
                    return data['message']['content'].strip()
                return None
            except requests.exceptions.Timeout as e:
                last_error = e
                print(f"⚠️  AKIRA BRAIN: Timeout na tentativa {attempt}/{self.retries}.")
            except Exception as e:
                last_error = e
                print(f"⚠️  AKIRA BRAIN ERROR (tentativa {attempt}/{self.retries}): {e}")

            if attempt < self.retries:
                time.sleep(self.backoff ** (attempt - 1))

        return None, last_error

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

        # Timeout curto para nao travar repricing
        result = self._chat(payload, timeout=5)
        if isinstance(result, tuple):
            return None
        return result

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

        result = self._chat(payload, timeout=10)
        if isinstance(result, tuple):
            _, err = result
            if err:
                print(f"⚠️  AKIRA FAQ ERROR: {err}")
            return "⚠️ Erro de comunicação com o núcleo."
        if not result:
            return "⚠️ O sistema neural está reiniciando... Tente novamente em breve."
        return result

if __name__ == "__main__":
    # Teste rápido de sanidade
    brain = AkiraBrain()
    insight = brain.gerar_insight("Teste Produto", "100.00", "150.00")
    print(f"Insight: {insight}")
