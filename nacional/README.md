# Reprodução da totalização presidencial — 2º turno de 2026

Análise clássica executada em 06/11/2026. Foram somados todos os 28 arquivos de BU CSV publicados no recorte (27 UFs e exterior ZZ), com 144.283.710 bytes comprimidos. As 1.931.103 linhas presidenciais pertencem a 499.205 seções; outras duas seções apuradas têm comparecimento zero e registros administrativos sem cargo. Total: 499.207 seções apuradas, coincidente com a publicação oficial.

Os resultados nacionais e os de cada UF/ZZ coincidem exatamente com os respectivos arquivos oficiais EA20 para os dois candidatos, votos brancos e nulos. Zero duplicatas de seção/categoria; zero divergências entre soma de votos e comparecimento em cada seção.

## Executar

Requer **Python 3.11 ou posterior**, somente biblioteca padrão. A versão 3.9 do Python fornecida pelo macOS não contém `hashlib.file_digest`.

```sh
python3.11 totalizar_bu_nacional.py
python3.11 conferir_resultados_por_uf.py
```

No ambiente usado na pesquisa, o interpretador é `../../.venv/bin/python` a partir desta pasta.

O primeiro script confere os hashes dos ZIPs já presentes. Se um ZIP ou checksum estiver ausente, baixa-o da URL explícita de `fontes-bu.json`, com limite de tamanho. A leitura de CSV ocorre diretamente dentro do ZIP, sem extrair arquivos grandes. O segundo script compara cada UF com seu JSON congelado; só acessa a rede quando o snapshot dessa UF está ausente. O snapshot nacional `resultado-oficial-br.json` já acompanha o pacote e deve ser preservado para repetir esta comparação exata.

Os originais oficiais não são alterados. Os scripts regravam arquivos de resultados derivados. Não executar com a opção Python `-O`, pois as verificações utilizam `assert`.

## Arquivos principais

- `fontes-bu.json`: URLs observadas no catálogo oficial, tamanhos e Last-Modified.
- `originais/`: pasta criada na reprodução, com os 28 ZIPs e seus checksums SHA-512; os ZIPs não acompanham a cópia Overleaf.
- `manifesto-downloads.json`: hashes efetivamente conferidos e tamanhos reais.
- `resultado-oficial-br.json`: resultado nacional oficial congelado; URL e cabeçalhos em `fonte-resultado-oficial-br.json`.
- `resultados-oficiais-uf/`: 28 JSONs oficiais congelados.
- `resultado-nacional.json`: resultado detalhado, datas das extrações e estatísticas por UF.
- `totais-por-uf.csv`: totais calculados em cada UF/ZZ.
- `comparacao-resultados-uf.json`: comparação de todas as categorias e seções por UF, com hashes SHA-256 dos JSONs.
- `comparacao-nacional.csv`: tabela curta adequada ao artigo.
- `resumo-nacional.json`: resumo de proveniência e resultados.
- `secoes-sem-comparecimento.json`: as duas linhas administrativas do exterior que explicam a diferença entre seções apuradas e seções com linhas presidenciais.
- `secoes-zz.json`: configuração de seções do exterior, obtida de `https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3221/config/zz/zz-p003221-cs.json`.

`cobertura-por-uf-oficial.json` registra a investigação inicial antes de incluir as duas seções sem comparecimento. `comparacao-resultados-uf.json` é o resultado final corrigido; a investigação inicial não representa votos ausentes.

## Tratamento de dados

Filtro: cargo 1 (Presidente), turno 2, eleição 6258, pleito 3221, ano 2026. Categorias: candidato 13, candidato 22, brancos 95, nulos 96. Chave de unicidade: UF, município, zona, seção e categoria. O número físico da urna não é usado como chave, pois a apuração pode reutilizar equipamentos em contextos distintos.

As linhas com cargo/votável -1, eleição federal e comparecimento zero são verificadas e contadas separadamente como seções apuradas sem votos. Não são transformadas em linhas inventadas de candidatos. Somar as quatro categorias de votos em cada seção precisa reproduzir seu comparecimento. A soma do conjunto de seções precisa reproduzir os totais publicados por UF e nacionalmente.

Snapshot BU: 26/10/2026 07:42:38. Snapshot nacional EA20: 25/10/2026 23:27:02, IDG 4241309, totalização final. São horários diferentes; a comparação documenta a igualdade de seus resultados finais.

## Limite da conclusão

Reproduzimos aritmeticamente a totalização publicada a partir dos BUs CSV publicados. Não recontamos RDVs nacionais nem verificamos as assinaturas criptográficas/cadeias de certificados dos arquivos. Os checksums SHA-512 conferidos não equivalem a essa validação. Fontes e metodologia ampla em `../auditabilidade-nacional-2026.md`.
