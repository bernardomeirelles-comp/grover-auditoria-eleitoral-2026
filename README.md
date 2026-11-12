# Grover e conferência de registros eleitorais

Material do artigo sobre a conferência dos registros presidenciais de 2026, segundo turno, eleição 6258 e pleito 3221. A conferência nacional usa programas clássicos. Grover foi aplicado a diferenças artificiais entre quatro contagens de uma seção de Bujari/AC.

[Artigo em PDF](artigo.pdf) · [Roteiro de reprodução](roteiro-reproducao.md) · [Fontes verificadas](revisao/fontes-verificadas.md)

Repositório: https://github.com/bernardomeirelles-comp/grover-auditoria-eleitoral-2026

Versão final da Sprint 3: explicações e organização do artigo revisadas, com os mesmos dados e experimentos da Sprint 2. Referência desta entrega: `sprint3-final`.

## Resultados e limites

As tabelas entregues abrangem 499.207 seções apuradas e 128.236.074 votos. As contagens de RDV, BU e publicações comparadas coincidiram. Essa concordância verifica os registros publicados; não observa a intenção de cada eleitor nem prova ausência de toda forma de fraude.

Na revisão quântica, foram executados três blocos de 512 repetições no IBM `ibm_marrakesh`, com oito buscas e quatro controles por bloco. A interface registrou dois segundos de QPU por trabalho, seis segundos no total, valores exibidos pela plataforma. Os 36 segmentos e as três sequências completas passaram pela validação ideal. A versão simplificada apresentou maior acerto nos 12 pares de posição e bloco, mas nenhuma busca física alcançou o equilíbrio de consultas adotado.

A [tabela dos 12 casos agregados](revisao/analise-ibm/tabela-resultados.md) reúne as frequências e a variação entre blocos. As [contagens por bloco](revisao/analise-ibm/resultados-por-bloco.csv), [resultados agregados](revisao/analise-ibm/resultados-agregados.csv) e [limitações do modelo](revisao/analise-ibm/LEIA-ME.md) permitem conferir os cálculos. Os controles incluem preparação, reinicialização e leitura; não isolam apenas a leitura.

A referência clássica é 2,25 consultas sob a promessa de exatamente uma divergência. O protocolo quântico contabiliza uma consulta ao oráculo e uma verificação clássica por tentativa, resultando em `2/p`; o equilíbrio é `p = 8/9`, aproximadamente 88,89%. Essa convenção não mede tempo de execução nem inclui o custo de preparar os dados.

A execução histórica de 6/11/2026, com 331 acertos em 2.048 medições, permanece em `dados/ibm-result.json`. Os novos trabalhos ficam separados em `revisao/composer/brutos/`. As cópias públicas dos metadados omitem identificadores de conta; contagens, circuitos, datas e parâmetros científicos foram preservados.

## Conferir a entrega

Python 3.11.16 foi usado no ambiente registrado. A instalação requer internet; os comandos de conferência abaixo não acessam a IBM. Não execute com `python -O`, pois as verificações usam `assert`.

```sh
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
shasum -a 256 -c MANIFEST.sha256
python recontagem-nacional/conferir_entrega.py
python fontes-tse/conferir_hashes_2026.py
python testar-controles.py
```

A conferência offline relê as tabelas entregues; não baixa nem redecodifica todos os RDVs. O [roteiro](roteiro-reproducao.md) separa essa verificação da nova obtenção dos arquivos públicos, das simulações locais, da reanálise IBM e da compilação do artigo. Reexecutar programas pode regravar arquivos derivados: use uma cópia de trabalho. Nenhum comando do roteiro envia trabalhos à IBM.

## Arquivos principais

| Caminho | Conteúdo |
|---|---|
| `main.tex`, `parte-experimental.tex`, `referencias.bib`, `IEEEtran.cls` | Fontes do artigo |
| `experimento.py`, `reavaliar.py`, `testar-variacoes.py` | Circuitos e simulações |
| `testar-controles.py` | Testes do comparador clássico |
| `analisar-repeticoes.py`, `revisao/analise-ibm/` | Análise dos três trabalhos e modelo aproximado de ruído |
| `revisao/composer/`, `revisao/calibracao/` | Protocolo, circuitos, exportações e calibração datada |
| `gerar-figuras.py`, `figuras/` | Figuras e hashes dos dados usados |
| `fontes-tse/` | Binários originais da amostra e esquemas ASN.1 |
| `nacional/`, `recontagem-nacional/`, `conferencia-secoes/` | Resultados, procedência e programas nacionais |
| `MANIFEST.sha256`, `relatorio-preparacao.md` | Integridade do pacote e verificações realizadas |

Os ZIPs nacionais ficam fora do repositório, com fontes e hashes preservados. A leitura completa depende dos servidores oficiais. As assinaturas verificadas têm o alcance especificado em seus relatórios, sem validação de todas as urnas. A calibração posterior não reconstrói a execução histórica, e o modelo aproximado não identifica uma causa única para os erros físicos.
