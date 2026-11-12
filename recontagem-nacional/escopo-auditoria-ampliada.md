# Ampliação da auditoria dos dados públicos: Presidente, 2º turno de 2026

Pesquisa iniciada em 06/11/2026, horário de Brasília. Recorte: eleição federal 6258, pleito 3221, votação de 25/10/2026. Consolidação concluída em 06/11/2026, horário de Brasília. Esta nota distingue verificações executadas e extensões ainda não realizadas. O objetivo é verificar consistência e autenticidade dos registros consultáveis; esses testes não permitem concluir, isoladamente, ausência de fraude em todo o processo.

## Recontagem nacional incremental: viável sem armazenar 124 GB

O [catálogo oficial de arquivos transmitidos para totalização](https://dadosabertos.tse.jus.br/dataset/resultados-2026-arquivos-transmitidos-para-totalizacao) oferece 28 ZIPs do segundo turno, incluindo DF e exterior ZZ. A descrição limita o conjunto aos arquivos com situação **Totalizado**. Não é um histórico de todas as versões rejeitadas ou de todas as tentativas de transmissão.

Inventariamos os diretórios centrais dos **28 arquivos**, por HTTP Range. Os ZIPs somam **124.136.069.320 bytes**, mas os diretórios centrais têm somente **259.788.744 bytes**. Foram listadas **2.496.140 entradas**, sem nomes duplicados. Os manifestos `membros-UF.jsonl.gz` (regeneráveis, omitidos da entrega) contêm nome, offset, tamanho comprimido/descomprimido, método e CRC de cada entrada; os resumos incluem URL, Last-Modified e SHA-256 do diretório recebido.

| Família | Quantidade de arquivos | Bytes comprimidos |
|---|---:|---:|
| BU regular (`bu.dat`) | 499.178 | 396.119.185 |
| BU do Sistema de Apuração (`busa.dat`) | 29 | 18.270 |
| RDV (`rdv.dat`) | 499.207 | 139.985.863 |
| Assinaturas VOTA (`vota.vsc`) | 499.178 | 30.552.478.198 |
| Assinaturas SA (`sa.vsc`) | 29 | 1.041.175 |
| Logs de urna (`log.jez`) | 499.178 | 90.356.468.723 |
| Logs SA (`logsa.jez`) | 29 | 1.242.007 |
| Imagens de BU (`imgbu.dat`) | 499.178 | 2.202.260.210 |
| Imagens de BU SA (`imgbusa.dat`) | 29 | 122.258 |

Há ainda 28 leia-me e 77 arquivos auxiliares `.id`. A seleção quantitativa é exata: **499.207 BUs, contando BU e BUSA, e 499.207 RDVs**. A extensão bu.dat também pode representar resultados recuperados pelo RED; não classificamos nacionalmente os motivos de contingência. As 29 apurações SA estão no exterior. Sua origem declarada no RDV é `cedula`; não devem ser descritas como votos digitados originalmente pelo eleitor na urna eletrônica.

Os conteúdos comprimidos de BU/BUSA e RDV somam **536.123.318 bytes**. Com cabeçalhos ZIP e trechos adjacentes mínimos, o plano seletivo precisa de aproximadamente **622,5 MB**, acrescidos dos metadados e dos delimitadores HTTP. Não é necessário transferir os logs de 90 GB para comparar as contagens.

O servidor aceitou, em teste real, requisições `multipart/byteranges`: até 64 trechos não contíguos são solicitados numa mesma chamada. Cada resposta precisa ser HTTP 206; uma resposta integral é rejeitada antes da leitura do corpo. O cliente verifica Content-Range, tamanho, método deflate e CRC de cada entrada; conserva o SHA-256 de cada BU e RDV efetivamente processado. O cabeçalho `If-Unmodified-Since` usa o Last-Modified observado para evitar misturar versões durante a leitura.

**Benchmarks executados:** uma leitura contínua de 32 MiB levou 1,76 s; a decodificação e comparação de 153 pares levou 0,12 s. Quatro conexões lendo 128 MiB somadas alcançaram cerca de 29 MB/s. O teste seletivo multipart processou 255 seções em 0,77 s com quatro chamadas e 460.459 bytes transferidos. Esses valores são medições deste ambiente, não garantias de desempenho para outras redes. A execução nacional usa quatro processos e limita cada um a 20 chamadas/s, com checkpoint de resultados por UF.

**Resultado concluído:** foram recontadas e reconciliadas as **499.207 seções publicadas**, em 28 abrangências, incluindo DF e exterior. Não houve divergências entre RDV e BU, entre os binários e BWeb por seção, nem seções faltantes, extras ou chaves duplicadas no conjunto comparado. A soma reproduziu o EA20 oficial: código 13, **64.256.232**; código 22, **59.826.041**; brancos, **1.430.496**; nulos, **2.723.305**; total, **128.236.074 votos**. A recontagem recebeu **682.175.272 bytes em 8.455 chamadas**, além do inventário e dos testes prévios. Esses números não incluem uma análise dos logs nacionais nem validação das assinaturas de todas as urnas. O consolidado está em `resultados/conclusao-nacional.json`.

O EA20 usado foi gerado em 25/10/2026 às 23:27:02 (IDG 4241309), enquanto o BWeb consultado registra geração em 26/10/2026 às 07:42:38. Os horários de publicação diferem; a comparação efetiva confirmou as mesmas contagens. As 499.207 seções apuradas incluem duas sem votos; as 41 seções não instaladas não integram os pares publicados. Não se apresentou a cobertura dos pares como cobertura de eventos que não produziram BU.

## O que o processamento verifica

O script `recontar_nacional_seletivo.py` seleciona somente `bu.dat`, `busa.dat` e `rdv.dat` a partir dos nomes realmente inventariados. O decodificador segue os [schemas ASN.1 e exemplos oficiais de 2026](https://www.tse.jus.br/eleicoes/eleicoes-2026-content/arquivos/formato-arquivos-de-bu-rdv-e-assinatura-digital). Os originais do pacote de especificação e seus hashes estão preservados em `../fontes-tse/spec/` e seu manifesto de proveniência.

As verificações incluem fase oficial, pleito 3221, eleição 6258, cargo Presidente, município/zona/seção coincidentes no RDV e BU, contagem nominal para 13 e 22, brancos e categorias nulas. As variações de voto nulo, incluindo nulo por repetição, são agrupadas como nulos. A soma deve coincidir com o comparecimento **do cargo**, campo `qtdComparecimento`. Nos BUs de apuração manual observados, o campo geral `qtdEleitoresCompareceram` é zero, enquanto o comparecimento válido por cargo está preenchido; usar indiscriminadamente o campo geral produziria falsos alertas.

A etapa `conferir_recontagem_nacional.py` liga os resultados aos arquivos CSV de BUs já processados. Verifica SHA-256 dos CSVs derivados, unicidade da chave decodificada, nome do arquivo compatível com UF/pleito/município/zona/seção, igualdade de cobertura e comparação das quatro categorias em **cada seção**. Depois, soma e confere o resultado oficial EA20 nacional. Uma igualdade apenas dos totais nacionais não substituiria essa conferência por seção, porque diferenças locais poderiam se compensar.

As duas seções sem comparecimento — Trípoli e Ciudad Guayana — foram decodificadas separadamente: ambas possuem explicitamente eleição 6258 e cargo Presidente, com listas vazias de votos tanto no RDV quanto no BU. Não se inferiu zero apenas da ausência de um registro. A evidência está em `secoes-zero-decodificadas.json`.

## Assinaturas: avanços executados e limites

### Amostra de Bujari

Executamos a verificação criptográfica de hardware dos **três arquivos publicados da seção Bujari/AC, zona 9, seção 1: BU, RDV e log**. As três assinaturas foram válidas; seus hashes coincidiram com os hashes dos envelopes de software e hardware. A assinatura do certificado da urna foi verificada com a chave do emissor `AC UE2022` incorporada ao utilitário oficial. Para cada arquivo, um controle negativo com mensagem alterada foi rejeitado.

Código e evidência: `assinaturas/verificar_assinaturas_amostra.py`, `assinaturas/assinaturas-amostra-resultado.json` e `assinaturas/requirements-validadores.txt`. O utilitário oficial `assinatura_hash.py` e `lib/mr_util.py` foram usados sem modificar sua lógica criptográfica. A documentação oficial explica a verificação de hashes, das assinaturas dos arquivos e da assinatura do certificado; os modelos 2020/2022 usam EdDSA/Ed521, enquanto outros modelos usam ECDSA.

A execução integral do exemplo oficial reportou arquivos ausentes porque o envelope também menciona arquivos que não estavam na amostra e/ou não fazem parte desse conjunto público, como registros auxiliares e biométricos. Esse resultado foi preservado em `assinaturas/validacao-assinatura-bujari.log`; não foi ocultado nem interpretado como assinatura inválida. A verificação subsequente foi explicitamente limitada aos três arquivos disponíveis. A imagem do BU existe no ZIP, mas não foi baixada nessa amostra.

**Não executamos** validação completa da cadeia X.509, revogação, todos os critérios temporais dos certificados, assinaturas de software ou assinaturas de todas as urnas nacionais. Verificar a assinatura de um certificado com uma chave de emissor fixada é uma etapa, não toda a validação de confiança. As assinaturas nacionais exigiriam transferir cerca de 30,55 GB adicionais e um benchmark criptográfico próprio antes de estimar custo total.

### Resultado final nacional

O [JWS do resultado presidencial nacional](https://resultados.tse.jus.br/oficial/ele2026/6258/dados/br/br-c0001-e006258-u.jws) foi baixado e sua assinatura **Ed25519/EdDSA foi verificada** usando a chave pública fixada do Apêndice B do [manual oficial de verificação JWS](https://www.tse.jus.br/eleicoes/eleicoes-2026-content/arquivos/divulgacao-de-resultados/manual-verificacao-jws). O conteúdo assinado coincide com o JSON final usado na soma nacional. Um controle negativo foi rejeitado. Evidências: `assinaturas/resultado-final-br.jws`, `assinaturas/verificar_jws_final.py` e `assinaturas/jws-final-resultado.json`.

Essa verificação autentica a assinatura em relação à chave pública adotada. Não implica validação das assinaturas de todos os BUs que contribuíram para o resultado, nem uma certificação externa de todos os eventos eleitorais. Não foi executada validação de cadeia X.509/LCR para esse JWS.

## Outras evidências públicas úteis

| Evidência | Fonte e acesso observado | O que pode acrescentar | Limite |
|---|---|---|---|
| Correspondências esperadas e efetivadas | [Catálogo do segundo turno](https://dadosabertos.tse.jus.br/dataset/resultados-2026-correspondencias-esperadas-e-efetivadas-2-turno) | Vincular seção, equipamento e carga; explicar contingências e substituições | Uma substituição documentada não é indício automático de fraude |
| Logs da urna e SA | Nos ZIPs já inventariados | Cronologia de abertura, votação, encerramento e ocorrências técnicas | Exigem interpretação contextual; não revelam o conteúdo individual do voto |
| Logs de preparação Gedai | [Catálogo Gedai do segundo turno](https://dadosabertos.tse.jus.br/dataset/resultados-2026-logs-do-sistema-de-preparacao-das-urnas-eletronicas-gedai-2-turno) | Relacionar preparação e carga ao equipamento utilizado | A presença de um evento precisa ser confrontada com o procedimento esperado |
| Configuração e auxiliares de seção | [Documentação técnica e EA16/EA18](https://www.tse.jus.br/eleicoes/informacoes-tecnicas-sobre-a-divulgacao-de-resultados) | Seções principais/agregadas, arquivos disponíveis, geração e vínculo | Não confundir seção agregada com BU próprio ausente |
| BU impresso recolhido na seção | [Procedimentos de auditoria do TSE](https://www.tse.jus.br/eleicoes/urna-eletronica/seguranca-da-urna/como-realizar-auditoria) | Comparação com evidência coletada antes/independentemente do download da totalização | Imagem digital baixada da mesma fonte não substitui coleta independente |
| Relatórios de integridade/autenticidade | Portais dos TREs e TSE | Comparar entradas controladas e resultado; documentar ocorrências e amostragem | O teste cobre as urnas/amostras efetivamente auditadas |
| Atas de seção e relatórios de totalização | Justiça Eleitoral; parte por solicitação fundamentada | Contextualizar contingência, voto em cédula, anulação e ocorrências | Não foi demonstrada disponibilidade de um pacote nacional completo de todas as atas |

Exemplos de páginas oficiais com materiais de auditoria: [TRE-DF](https://www.tre-df.jus.br/eleicoes/auditoria-da-votacao-eletronica-2026), [TRE-MA](https://www.tre-ma.jus.br/eleicoes/eleicoes-2026/auditoria-da-votacao-eletronica), [TRE-MT](https://www.tre-mt.jus.br/eleicoes/2026/auditoria-da-votacao-eletronica), [TRE-SC](https://www.tre-sc.jus.br/eleicoes/eleicoes-2026/eleicoes-2026-auditoria-de-votacao-eletronica) e [TRE-RJ](https://www.tre-rj.jus.br/eleicoes/eleicoes-plebiscitos-e-referendos/eleicoes-2026/auditoria-da-votacao-eletronica). Localizamos páginas e relações de documentos; não revisamos todos os relatórios de todas as UFs.

Em [comunicado de 1º/11/2026](https://www.tse.jus.br/comunicacao/noticias/2026/Novembro/tres-devem-encaminhar-ao-tse-relatorios-de-auditoria-das-urnas-eletronicas-ate-4-de-novembro), o TSE informa o envio dos relatórios regionais até 4/11 e publicação em até 30 dias após o segundo turno. Portanto, em 6/11 não se deve presumir que toda a documentação consolidada já esteja publicada. O [TCU informou acompanhar os testes de integridade de 2026](https://pesquisa.apps.tcu.gov.br/documento/noticia/NOTICIA-10841.KEY/%2520/DTRELEVANCIA%2520desc/0), com previsão de relatório consolidado em até 30 dias após o segundo turno. A existência desse acompanhamento não equivale a termos analisado seu relatório final.

## Conclusões permitidas

A recontagem completa e a cobertura reconciliada confirmaram que os votos dos RDVs publicados reproduzem os BUs publicados, que estes coincidem com os CSVs por seção e que sua soma reproduz o resultado final. O alcance é maior do que uma amostra local, mas continua sendo uma verificação dos registros disponíveis. BU e RDV compartilham origem no sistema; coincidência entre eles não exclui uma falha comum anterior à geração dos dois.

Assinaturas válidas acrescentam evidência contra alteração posterior dos arquivos em relação às chaves verificadas; não provam sozinhas que o equipamento recebeu corretamente a vontade de cada eleitor. Logs, atas, auditorias com entradas conhecidas, fiscalização e evidências físicas acrescentam camadas distintas. Divergências técnicas devem ser reproduzidas e contextualizadas antes de qualificá-las; ausência de divergências nesses testes não autoriza uma declaração absoluta de “eleição sem fraude”.

## Próximos passos mínimos, em ordem

A recontagem nacional, a reconciliação e as verificações restritas de assinatura já foram concluídas. Extensões possíveis, ainda não executadas:

1. Ampliar assinaturas por amostra estratificada de modelos de urna e apuração SA, antes de propor validação nacional de 30,55 GB.
2. Vincular ocorrências específicas a correspondências, logs e atas; evitar varreduras sem pergunta ou critério definido.
3. Revisar relatórios públicos de testes de integridade e fiscalização, registrando amostra, data, entidade responsável e eventuais ressalvas; atualizar quando o material ainda pendente for publicado.
