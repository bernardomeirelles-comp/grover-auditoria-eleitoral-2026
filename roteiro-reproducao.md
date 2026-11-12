# Roteiro de reprodução

Todos os comandos partem da raiz do projeto. Use uma cópia para recalcular resultados: vários programas regravam tabelas, metadados e figuras. Os arquivos brutos eleitorais e as exportações IBM não devem ser editados. Não use `python -O`.

## 1. Ambiente

Python 3.11.16 foi usado no ambiente registrado. A instalação abaixo requer internet. As análises locais posteriores não precisam de conta IBM.

```sh
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
```

O arquivo fixa as dependências principais usadas pelo código; não é uma imagem completa de sistema operacional nem um lock de todas as dependências transitivas. Para as assinaturas de hardware da amostra, há requisitos adicionais no passo 4.

## 2. Verificar o conteúdo entregue, sem rede

Na cópia preparada para publicação, confirme o manifesto antes de reexecutar programas:

```sh
shasum -a 256 -c MANIFEST.sha256
python recontagem-nacional/conferir_entrega.py
python fontes-tse/conferir_hashes_2026.py
```

`conferir_entrega.py` relê as 28 tabelas `.csv.gz`, verifica seus hashes, a unicidade das seções e os totais. Não baixa nem redecodifica todos os RDVs. O resultado esperado é 499.207 seções e 128.236.074 votos, com as comparações previstas satisfeitas. O manifesto identifica os bytes entregues; depois de regenerar saídas, diferenças no manifesto podem decorrer dessa regeneração.

## 3. Recontar a amostra, executar controles e simular localmente

```sh
python fontes-tse/recontagem_2026.py
python fontes-tse/conferir_hashes_2026.py
python preparar-dados.py
python testar-controles.py
python reavaliar.py
python testar-variacoes.py
python analisar-ibm.py
python gerar-figuras.py
```

A amostra deve manter `[68, 149, 2, 13]` nos arquivos oficiais. O teste usa uma cópia com `[68, 148, 2, 13]`. O programa de controles introduz alterações em memória e exercita o comparador; não modifica os binários.

`reavaliar.py` compara as implementações e as quatro posições. Os valores calculados por matriz densidade em `revisao/probabilidades.csv` são probabilidades exatas do modelo numérico, não frequências de novas medições. A referência clássica é 2,25 consultas sob a promessa de uma única divergência; com a convenção `2/p`, o equilíbrio é 88,89%.

`testar-variacoes.py` amplia os valores alterados e registra casos não aplicáveis, como contagem negativa. `analisar-ibm.py` relê a execução histórica de 6/11 e não se conecta à IBM. A simulação histórica completa também pode ser refeita com `python experimento.py`; ela é separada da comparação revisada e regrava arquivos em `dados/`.

## 4. Verificar assinaturas preservadas, sem rede após instalar dependências

```sh
python recontagem-nacional/assinaturas/verificar_jws_final.py
python -m pip install -r recontagem-nacional/assinaturas/requirements-validadores.txt
python recontagem-nacional/assinaturas/verificar_assinaturas_amostra.py
```

A instalação adicional usa um commit fixado de ECPy no GitHub, portanto requer Git e internet. A primeira verificação usa a chave pública do manual para o JWS nacional. A segunda verifica somente as assinaturas de hardware dos arquivos BU, RDV e log da amostra. Nenhuma substitui validação integral de cadeia, revogação ou de todas as urnas.

## 5. Reanalisar os novos trabalhos IBM, sem nova submissão

Os arquivos de entrada estão em `revisao/composer/brutos/`, acompanhados de `revisao/composer/protocolo.json` e da calibração em `revisao/calibracao/`.

```sh
python analisar-repeticoes.py
```

O programa decodifica as exportações locais, valida os circuitos físicos e compara um modelo aproximado com as frequências observadas. O campo `complete_three_block_design` do resumo informa se os três blocos previstos estão presentes. Um resultado parcial não deve ser apresentado como desenho completo. Cópias públicas dos metadados de trabalhos omitem identificadores de conta; contagens e circuitos são preservados.

A calibração tem sua própria data. O modelo não representa todos os mecanismos físicos e não reconstrói a execução histórica. `preparar-composer.py` apenas gera circuitos localmente, mas não faz parte da sequência necessária para conferir os trabalhos já executados. O roteiro não contém autenticação, submissão ou consumo de QPU.

## 6. Repetir as comparações nacionais a partir dos arquivos públicos

Esta etapa usa rede e espaço em disco. Para BWeb, os 28 ZIPs somam aproximadamente 144 MB. Os programas conferem os checksums oficiais preservados ou obtidos das URLs indicadas.

```sh
python nacional/totalizar_bu_nacional.py
python nacional/conferir_resultados_por_uf.py
python recontagem-nacional/conferir_recontagem_nacional.py
```

A comparação adicional com votação por seção exige o ZIP de aproximadamente 242 MB. Para manter o snapshot entregue verificável, confira seu hash antes de usá-lo:

```sh
curl --fail --location 'https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_2026_BR.zip' --output conferencia-secoes/votacao_secao_2026_BR.zip
python - <<'CHECK'
import hashlib, json
from pathlib import Path
p = Path('conferencia-secoes')
expected = json.loads((p / 'resultado-conferencia-secoes.json').read_text())['sha256']
with (p / 'votacao_secao_2026_BR.zip').open('rb') as source:
    assert hashlib.file_digest(source, 'sha256').hexdigest() == expected
CHECK
python conferencia-secoes/conferir_secoes.py
```

O SHA-256 do arquivo utilizado na entrega está em `conferencia-secoes/resultado-conferencia-secoes.json`. Uma versão diferente deve ser tratada como nova coleta, e não como reprodução byte a byte da anterior.

Para redecodificar os RDVs nacionais, siga `recontagem-nacional/README.md`. Essa etapa obtém cerca de 260 MB de inventário e centenas de MB de trechos dos ZIPs, evitando os aproximadamente 124 GB dos pacotes completos. Execute em cópia separada e mova `recontagem-nacional/resultados/` para outro nome antes de iniciar, pois resultados existentes são reutilizados como cache.

```sh
python recontagem-nacional/inventariar_zip_remoto.py ALL
python recontagem-nacional/recontar_nacional_seletivo.py
python recontagem-nacional/conferir_recontagem_nacional.py
```

Os servidores precisam aceitar HTTP Range. Falhas de download e mudanças nas fontes não devem ser silenciadas. Nenhum desses comandos acessa a IBM.

## 7. Gerar figuras e compilar

```sh
python gerar-figuras.py
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

É necessária uma instalação LaTeX com os pacotes do preâmbulo. Os comandos Python não instalam LaTeX. No Overleaf, o arquivo principal é `main.tex`. Os arquivos `.gz` fazem parte do pacote público e devem manter essa extensão.

## Alcance

Reproduzir a conferência significa repetir os cálculos sobre os registros publicados e verificar os resultados experimentais preservados. Não permite observar a intenção individual do eleitor, excluir erros comuns às fontes nem certificar ausência absoluta de fraude. A redução de consultas de Grover é analisada separadamente do custo de preparar os dados e do tempo total de execução.
