# Riscos e Controles

## Risco 1: Secrets expostos
- Impacto: alto.
- Controle: remover segredos de codigo/log; usar `.env` local e rotacao periodica.

## Risco 2: Dependencia de scraping
- Impacto: medio/alto.
- Controle: tratar timeout, captcha, seletores variaveis e fallback seguro.

## Risco 3: Produto vendido sem margem
- Impacto: alto.
- Controle: precificacao automatica + sentinela + bloqueio de SKU de risco.

## Risco 4: Promessa comercial fora da realidade
- Impacto: alto (reputacao).
- Controle: alinhar copy com SLA real e acompanhamento proativo.

## Risco 5: Falha de stack local de IA
- Impacto: medio.
- Controle: fallback de resposta e monitor de disponibilidade do Ollama.

## Risco 6: Instabilidade de integracoes externas
- Impacto: medio.
- Controle: retries, timeout, logs estruturados e alertas.

## Auditoria minima semanal
- Verificar escopos de token Shopify.
- Verificar SKUs sem custo.
- Verificar taxa de falhas no suporte bot.
- Verificar produtos em `draft` por sentinela e motivo.
