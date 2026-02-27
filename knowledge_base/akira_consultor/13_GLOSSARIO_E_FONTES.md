# Glossario e Fontes

## Glossario rapido
- SKU: unidade de catalogo vendavel.
- Hero SKU: item principal de aquisicao.
- Profit SKU: item de maior margem.
- Trust SKU: item de entrada para reduzir risco de compra.
- Kill switch: desativacao automatica de produto de risco.
- RMA: processo de devolucao/troca por problema de qualidade.

## Fontes internas usadas (repositorio)
- Backend precificacao: `src/precificacao_dinamica.py`
- Monitor de margem: `src/monitor_lucro.py`
- Sentinela de fornecedor: `src/sentinela.py`
- Bot de suporte: `src/suporte_akira.py`
- IA local: `src/akira_brain.py`
- Notificacao Telegram: `src/notificacao.py`
- Conteudos institucionais: `data/content/*.html`
- Frontend headless: `frontend/app/page.tsx`, `frontend/lib/shopify.ts`
- Utilitarios de token/escopo: `scripts/*.py`

## Campos para atualizar com dados reais da operacao
- Receita mensal.
- Ticket medio.
- Conversao por canal.
- CAC por canal.
- LTV por coorte.
- Top 10 SKUs por margem.
