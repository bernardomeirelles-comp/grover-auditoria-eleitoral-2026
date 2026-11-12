# Comparação nacional por seção e categoria

O programa compara os boletins BWeb com a publicação oficial de votação por seção, filtrando eleição 6258, segundo turno e presidente. A chave é UF, município, zona, seção e categoria. É uma comparação clássica entre publicações do mesmo órgão, não uma coleta independente de boletins físicos.

Resultado: 1.931.103 registros e 499.205 seções com votos em ambas as fontes; zero divergências, duplicatas ou seções com votos ausentes. As duas seções administrativas com comparecimento zero são identificadas separadamente no JSON. Os arquivos foram gerados em horários diferentes, preservados no resultado.

## Reproduzir

1. Execute primeiro `python nacional/totalizar_bu_nacional.py` na raiz do projeto para obter os 28 arquivos BWeb em `nacional/originais`.
2. Baixe o [ZIP oficial de votação por seção](https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_2026_BR.zip) e salve nesta pasta como `votacao_secao_2026_BR.zip`. São 241.891.087 bytes. O SHA-256 da cópia utilizada está no JSON; ele registra a identidade da nossa cópia, não uma validação de assinatura digital.
3. Execute `python conferencia-secoes/conferir_secoes.py` na raiz. Usa apenas a biblioteca padrão do Python 3.11 ou posterior.

A leitura do ZIP verifica os CRCs; a comparação rejeita duplicatas. Categorias ausentes só são interpretadas como zero quando a seção existe nas duas fontes. Seções presentes em apenas uma fonte são listadas separadamente. Nenhuma ausência foi encontrada neste processamento.

O ZIP grande fica fora do Overleaf. O script, a tabela de divergências e o resumo JSON permitem reproduzir e inspecionar a análise. Esta verificação não comprova como cada eleitor votou nem a ausência de toda forma de fraude.
