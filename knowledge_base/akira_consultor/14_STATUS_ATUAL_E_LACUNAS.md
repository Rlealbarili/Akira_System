# Status Atual e Lacunas Criticas

## O que ja esta implementado
- Conexao Shopify via Admin API no backend.
- Repricing automatico por margem.
- Monitor de lucro por variante.
- Sentinela com kill switch por custo/estoque.
- Bot de notificacao via Telegram.
- Frontend headless em Next.js consumindo Storefront API.

## Lacunas tecnicas atuais
1. Testes automatizados inexistentes.
2. Observabilidade limitada (sem painel unico de saude).
3. Dependencia de scraping com risco de variacao de layout/captcha.
4. Inconsistencias de versao de API em scripts.

## Lacunas de negocio
1. Decisao final de posicionamento (perifericos vs apparel tatico).
2. ICP e canais pagos ainda sem meta numerica formal.
3. Falta de quadro de KPIs com baseline real (receita, conversao, CAC, LTV).

## Alertas observados em operacao
- Ocorrencias de timeout no Telegram em loop de suporte.
- Ocorrencias de indisponibilidade do endpoint local de IA (Ollama).
- Ocorrencias de jobs sem token lido corretamente.

## Acoes prioritarias (proximos 7 dias)
1. Definir posicionamento unico da marca e alinhar todo o copy.
2. Implantar healthcheck diario de integracoes.
3. Fechar baseline de KPIs (com dados reais da loja).
4. Criar rotina de testes minimos para modulos criticos (`sentinela`, `precificacao`).
