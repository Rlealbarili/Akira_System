# Modelo Operacional Dropshipping

## Modelo operacional atual
- Fonte de abastecimento: fornecedores internacionais (AliExpress e similares).
- Fulfillment: envio direto da Asia para cliente final.
- Prazo informado: 10 a 25 dias uteis.
- Rastreio: esperado em ate 72h apos compra.

## Fluxo operacional alvo
1. Produto aprovado por margem, risco e disponibilidade.
2. Produto publicado na Shopify.
3. Sentinela audita custo/estoque no fornecedor.
4. Precificacao dinamica protege margem.
5. Pedido confirmado e cliente recebe comunicacao.
6. Rastreio enviado e suporte acompanha excecoes.

## SLAs internos recomendados
- Confirmacao de pedido: ate 24h.
- Envio de rastreio: ate 72h.
- Primeira resposta de suporte: ate 12h.
- Resolucao de incidente de pedido: ate 72h.

## Pontos criticos de operacao
- Variacao de preco de fornecedor.
- Ruptura de estoque apos venda.
- Divergencia entre copy de prazo e prazo real.
- Falha de sincronizacao de custo na Shopify.

## Controles obrigatorios
- Kill switch para risco de margem/estoque.
- Log de alteracoes de preco.
- Check diario de conectividade (Shopify, Telegram, Ollama, scraping).
