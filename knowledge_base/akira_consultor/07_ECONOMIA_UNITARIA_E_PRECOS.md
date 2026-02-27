# Economia Unitaria e Precos

## Regras de margem observadas
- Impostos totais default: simples + ICMS = 0.24.
- Margem minima operacional: 0.20 (em precificacao dinamica).
- Margem alvo de repricing: 0.35.

## Formula observada
`preco_base = custo / (1 - (impostos + margem_alvo))`
`novo_preco = ceil(preco_base) - 0.10` (ajuste psicologico de final)

## Politica de seguranca de custo (Sentinela)
- Se `custo_fornecedor + frete > USD 50.00`, desativa produto.
- Se sem estoque no fornecedor, desativa produto.

## KPIs financeiros recomendados
- Margem de contribuicao media por pedido.
- Margem por SKU (top 20%).
- Percentual de SKUs sem custo cadastrado.
- Delta entre custo esperado e custo real no pedido.

## Guardrails de preco
- Nao manter SKU ativo sem custo valido.
- Nao rodar campanha paga em SKU sem monitoramento de custo.
- Alertar automaticamente quando margem < limite.

## Decisoes automaticas sugeridas
- Margem < minima: repricing imediato.
- Custo ou frete acima do teto: pausar SKU.
- Repeticao de ruptura de estoque: remover SKU do catalogo de campanha.
