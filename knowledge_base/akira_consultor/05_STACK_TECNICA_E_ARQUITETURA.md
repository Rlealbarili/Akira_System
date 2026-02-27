# Stack Tecnica e Arquitetura

## Visao geral
- Backend: Python.
- Ecommerce: Shopify Admin API + Storefront API.
- Frontend: Next.js (headless, `shopify-buy`).
- Automacoes: scripts Python e rotinas de monitoramento.
- Notificacao: Telegram bot.
- IA local: Ollama (modelo configuravel).

## Estrutura de pastas
- `src/`: modulos principais de negocio e automacao.
- `scripts/`: utilitarios de token, debug e setup.
- `frontend/`: loja headless Next.js.
- `data/content/`: textos institucionais.
- `logs/`: logs operacionais.

## Integracoes principais
- Shopify Admin API: produtos, variantes, inventory item cost, paginas.
- Shopify Storefront API: leitura de produtos no frontend.
- Telegram API: alertas e canal de suporte.
- Playwright: scraping robusto para fornecedor.

## Decisoes de engenharia observadas
- Sessao Shopify via variaveis em `config/.env`.
- Fallback de import para rodar scripts dentro e fora de `src/`.
- Erros de integracao tratados para nao quebrar loops longos.

## Dividas tecnicas detectadas
- Falta de suite de testes automatizados.
- Inconsistencia de versao da API Shopify em scripts.
- Dependencia de seletores fragil em scraping.
- Ausencia de monitoramento central de saude.
