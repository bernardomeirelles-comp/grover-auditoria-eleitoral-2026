# Recontagem nacional dos RDVs e comparação com BUs

Recorte: Presidente, segundo turno de 2026, pleito 3221, eleição 6258. Esta pasta reúne resultados por seção, código, proveniência e verificações de assinatura. O arquivo `resultados/conclusao-nacional.json` registra a conclusão consolidada; a tabela curta está em `resultados/totais-nacionais.csv`.

## Conteúdo entregue

- `resultados/UF-secoes.csv.gz`: 28 tabelas, uma por UF/ZZ, com chave da seção, contagens RDV e BU, comparecimento por cargo, origem declarada dos votos e SHA-256 de cada arquivo binário processado.
- `resultados/UF-resumo.json`: cobertura, totais, falhas, volume recebido, duração e SHA-256 da respectiva tabela derivada.
- `inventario-UF.json`, `diretorios-zip.json`, `fontes-zip.json`: URLs, tamanhos, datas e contagem de membros dos arquivos oficiais.
- `inventario-nacional-resumo.json`: 499.178 BUs regulares (`bu.dat`), 29 BUs de apuração (`busa.dat`) e 499.207 RDVs.
- `assinaturas/`: JWS nacional, resultados das verificações, scripts e utilitários oficiais necessários à reprodução.
- `codigo-executado/`: cópia da versão dos scripts usada na pesquisa. `proveniencia-codigo.json` registra hashes e as diferenças da versão portável.
- `secoes-zero-decodificadas.json`: evidência das duas seções do exterior com comparecimento zero, com eleição e cargo explicitamente presentes.

Resultado concluído: 499.207 seções reconciliadas, 128.236.074 votos e zero divergências entre RDV, BU binário, BWeb por seção e total nacional. A leitura seletiva recebeu 682.175.272 bytes em 8.455 chamadas, além do inventário. BUs regulares também podem conter resultados recuperados pelo RED; sua extensão não certifica ausência de contingência.

Os ZIPs nacionais de 124 GB não integram a entrega. Também foram omitidos os manifestos detalhados de 2,5 milhões de entradas: podem ser regenerados diretamente dos diretórios ZIP por HTTP Range. As tabelas entregues preservam os hashes dos BU/RDV lidos; os binários completos não são armazenados nesta pasta. CRC de ZIP e SHA-256 de rastreabilidade não equivalem à verificação criptográfica das assinaturas nacionais.

## Conferência offline da entrega

Usar Python 3.11 ou posterior. A pasta deve ficar ao lado de `nacional/` e `fontes-tse/`, como na entrega.

```sh
python conferir_entrega.py
```

Este comando usa somente a biblioteca padrão. Confere hashes dos 28 CSVs derivados, chaves, duplicatas, igualdade das contagens RDV/BU registradas, comparecimento e totais por UF/nacionais contra o resultado oficial congelado. É uma conferência das tabelas entregues; não redecodifica os binários originais.

Para repetir também a reconciliação por seção contra os BUs CSV publicados, são necessários os 28 ZIPs BWeb em `../nacional/originais/`. Esses ZIPs não acompanham o projeto para limitar seu tamanho. Se ausentes, o primeiro comando abaixo os obtém; o segundo executa a comparação por seção:

```sh
python ../nacional/totalizar_bu_nacional.py
python conferir_recontagem_nacional.py
```

O download BWeb pode transferir aproximadamente 144 MB, conferindo os checksums SHA-512 oficiais. Não executar Python com `-O`, pois as verificações usam `assert`.

## Repetir a leitura dos RDVs e BUs oficiais

```sh
python -m pip install -r requirements.txt
python inventariar_zip_remoto.py ALL
python recontar_nacional_seletivo.py
python conferir_recontagem_nacional.py
```

A leitura do inventário transfere cerca de 260 MB de metadados. A recontagem usa até 64 ranges não contíguos por chamada e quatro processos. A resposta precisa ser HTTP 206; downloads integrais são rejeitados. Os diretórios permitem selecionar somente BU/BUSA e RDV; payloads comprimidos somam 536 MB, com cabeçalhos e delimitação HTTP adicionais. Não se baixam os logs ou as assinaturas nacionais para essa comparação.

**Cache:** a recontagem reutiliza um resumo final de UF que já exista em `resultados/`. Para uma reprodução totalmente nova sem sobrescrever a execução entregue, copie esta pasta para um novo local mantendo a estrutura relativa dos diretórios e mova a pasta `resultados/` para outro nome antes de executar. Também é possível indicar UFs específicas, por exemplo `python recontar_nacional_seletivo.py AC ZZ`. Uma UF só recebe resumo final quando termina sua leitura; falhas são registradas e impedem a consolidação sem ressalvas.

`benchmark_rdv.py` contém o decodificador e comparador compartilhado; seu nome reflete a origem no teste de desempenho. `planejar_ranges.py` constrói os grupos de trechos. Os schemas oficiais usados ficam em `../fontes-tse/spec/`. O manifesto da especificação registra a URL de origem e seus hashes.

## Assinaturas reproduzíveis

Instalar as dependências em um ambiente virtual separado, se desejado:

```sh
python -m pip install -r assinaturas/requirements-validadores.txt
python assinaturas/verificar_assinaturas_amostra.py
python assinaturas/verificar_jws_final.py
```

A validação amostral abrange assinaturas de hardware de BU, RDV e log da seção Bujari, com dados em `../fontes-tse/`. A assinatura do certificado é conferida contra a chave do emissor incorporada no utilitário oficial. Não valida todos os requisitos de cadeia, revogação ou assinaturas de software. O relatório integral inicial do exemplo oficial foi preservado e inclui arquivos ausentes; o resultado restrito identifica exatamente os três arquivos conferidos.

O JWS nacional é verificado por Ed25519 com a chave pública fixada do Apêndice B do manual oficial. O conteúdo assinado é comparado ao JSON congelado em `../nacional/resultado-oficial-br.json`. Há controles negativos de mensagem alterada. Origem das chaves e limites estão em `assinaturas/ORIGEM-DAS-CHAVES.md`.

## Interpretação

A reconciliação verifica consistência entre registros oficiais publicados e sua totalização. As 29 seções do Sistema de Apuração declaram origem em cédulas; seus RDVs são registros da apuração, não da digitação original do eleitor na urna. BU e RDV compartilham origem no sistema, e a igualdade não exclui falhas comuns anteriores à geração dos dois. As assinaturas verificadas têm alcance explicitamente limitado; não se conclui ausência absoluta de fraude no processo eleitoral.
