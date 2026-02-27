# Automacoes e Bots

## Modulos ativos
- `src/precificacao_dinamica.py`
  - Recalcula preco com base em custo, impostos e margem alvo.
  - Gera insight curto via `AkiraBrain`.
  - Envia alerta via Telegram.

- `src/monitor_lucro.py`
  - Auditoria de margem por variante.
  - Mostra preco, custo, lucro e margem.

- `src/sentinela.py`
  - Scraping no fornecedor com Playwright.
  - Regras criticas:
    - custo_total_usd > 50.00 => kill switch.
    - sem estoque => kill switch.
  - Kill switch: `status=draft` + tag `SENTINELA_BAN: motivo` + notificacao.

- `src/suporte_akira.py`
  - Listener Telegram para suporte.
  - Usa IA local para responder FAQ com contexto de produto.

- `src/setup_frontend.py`
  - Injecao de paginas institucionais na Shopify.

## Riscos operacionais observados em logs
- Falha de conectividade no Telegram (timeouts).
- Ollama local indisponivel/endpoint divergente.
- Tentativas com token ausente em cron.

## Padrao recomendado de resiliencia
- Sempre logar erro e continuar loop principal.
- Nunca interromper processamento por falha de notificacao.
- Definir retries com backoff para servicos externos.
