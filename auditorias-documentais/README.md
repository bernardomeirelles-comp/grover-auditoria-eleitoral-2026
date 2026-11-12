# Testes e auditorias eleitorais de 2026: fontes e acesso

Pesquisa encerrada em 6 de novembro de 2026, horário de São Paulo. Relógio consultado: 7/11/2026, 01:38 UTC. Esta nota distingue conteúdo lido, documentos apenas localizados e resultados que ainda precisam ser reproduzidos. Não é um levantamento exaustivo dos 27 TREs.

## O que já pode sustentar o artigo

Há evidência pública de auditorias com entradas conhecidas: no Teste de Integridade, votos previamente escritos em cédulas são digitados na urna e comparados ao resultado eletrônico. Isso permite conferir a contabilização nas urnas selecionadas. É uma evidência diferente da comparação RDV–BU, que confere a consistência entre dois arquivos relacionados da mesma votação. Ambas têm alcance definido; nenhuma, isoladamente, demonstra ausência de toda forma de fraude em uma eleição.

O material consultado permite citar resultados de terceiros e localizar atas dos dois turnos. **Atualização após downloads pelo Chrome: três atas do TRE-DF foram lidas visualmente por inteiro, totalizando 14 páginas. Uma delas registra uma divergência real do teste, atribuída pela comissão a erro humano de digitação após revisão da filmagem.** Foram transcritos totais de 16 urnas, mas não há nesses anexos a dupla de contagens por candidato que permitiria refazer o batimento detalhado. Os resultados documentais não são achados de nossa execução de Grover.

## Atas baixadas e conferidas visualmente

Os três PDFs e as imagens de todas as páginas estão preservados em `fontes/auditorias2026/`, com URL, tamanho e SHA-256 em `manifesto.json`. O download via Chrome pelo coordenador resolveu o HTTP 403 encontrado na requisição direta.

### CLDF: divergência de digitação documentada, 16 urnas

[Ata da audiência do Teste de Integridade na CLDF, segundo turno, 25/10/2026, sete páginas](https://www.tre-df.jus.br/eleicoes/arquivos-eleicoes-2026/ata-auditoria-cldf-25-10/@@display-file/file/ata-teste-de-integridade-2510-cldf.pdf).

As páginas 4–5 informam os totais das 16 urnas e a soma de 3.585 cédulas. A transcrição está em `fontes/auditorias2026/cldf-totais-por-urna-transcritos.csv`; a soma foi recalculada e coincide. A página 4 registra, na 8ª Zona Eleitoral, seção 0626, ilha 6, às 9h46, que o operador digitou **11 para governador**, enquanto a cédula 046 indicava **voto em branco**. A página 5 informa que a diferença apareceu na comparação final, que as imagens foram revisadas publicamente e que a comissão atribuiu a divergência a erro humano de digitação, sem identificar indício de falha da urna. Nas demais urnas, a ata declara coincidência.

Esse é um caso concreto útil para o artigo: localizar uma divergência é uma etapa de auditoria; determinar sua causa exige evidência adicional. Também mostra por que comparar apenas o total de votos é insuficiente: a seção 0626 tem 219 registros tanto na urna quanto no SAVP, apesar da diferença na distribuição de uma categoria. Não apresentar essa ocorrência como fraude ou erro do equipamento. É do cargo de governador no teste do DF, não da votação presidencial real.

As páginas 3–4 também registram ocorrências de falso positivo na identificação biométrica durante a habilitação de eleitores no procedimento convencional. A ata lista ocorrências; não fornece uma investigação técnica para cada uma. Elas não são sinônimo da divergência de contabilização acima.

A página 6 informa que representantes da CGU e do TCU receberam cópias do espelho do SAVP, relatório de divergência e BU da seção 0626, além dos documentos de duas outras seções. Esses documentos não integram o PDF de sete páginas. Buscar anexos no processo TCU 020.282/2026-5 pode fornecer as contagens detalhadas, mas isso ainda não foi comprovado.

### TSE: duas urnas, 200 e 189 votos

[Ata da audiência no TSE, segundo turno, 25/10/2026, cinco páginas](https://www.tre-df.jus.br/eleicoes/arquivos-eleicoes-2026/ata-auditoria-tse-2510/@@display-file/file/ata-auditoria-tse-2510.pdf).

A página 2 identifica 1ª ZE/seção 0009 e 18ª ZE/seção 0190. A página 4 informa, respectivamente, **200 e 189 votos**, e ausência de diferenças entre a mídia de resultado e o aplicativo de apoio. A soma 389 coincide com a notícia institucional. A mesma página registra dois eventos denominados falso positivo na primeira urna, às 8h40 e 13h20, sem detalhar a causa. Portanto, escrever “sem divergências na comparação final”, não “sem qualquer ocorrência”.

A página 5 cita a Análise Comparativa dos Resultados e a coincidência dos BUs com os relatórios do apoio; esse relatório detalhado não está anexado. A ata fornece totais e conclusão da comissão, não contagens por candidato que nosso programa tenha comparado.

### Biometria: seção 229, 61 participantes, ocorrências operacionais

[Ata padronizada da Escola Canadense, seção 229, segundo turno, duas páginas](https://www.tre-df.jus.br/eleicoes/arquivos-eleicoes-2026/ata-tse-escola-canadense-2510-secao-229/@@display-file/file/ata-tse-escola-canadense-2510-secao-229_redacado.pdf).

A página 1 identifica Brasília, 11ª ZE, seção 229, modelo de urna 2020 e **61 voluntários**. A página 2 registra ausência de representantes partidários no início, falha na impressora de apoio sanada de imediato e sete ocorrências denominadas falsos negativos biométricos. Esses 61 são participantes da habilitação, não um total de votos por candidato extraído de BU. O formulário não traz tabela de resultados nem conclusão detalhada de comparação. Não inferir taxa de erro da eleição ou falha na contagem a partir dessas ocorrências.

## Resultados oficiais publicados e efetivamente lidos

| Fonte | Recorte e informação confirmada | Uso correto |
|---|---|---|
| [TSE, Teste de Integridade do 2º turno, 25/10/2026](https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/teste-de-integridade-do-2o-turno-no-tse-confirma-correspondencia-entre-cedulas-e-votos-nas-urnas) | Duas urnas no Museu do Voto, em parceria com o TRE-DF; 389 votos auditados; a notícia relata ausência de divergências. Menciona também duas urnas e ausência de divergências no 1º turno, sem informar nessa matéria o total de votos daquele turno. | Resultado relatado pelo TSE para esse recorte. Os 389 votos não são a amostra nacional. A notícia não fornece a dupla de contagens por candidato necessária para reproduzir a comparação. |
| [TRE-SP, conclusão do teste no 2º turno, 25/10/2026](https://www.tre-sp.jus.br/comunicacao/noticias/2026/Outubro/teste-de-integridade-das-urnas-no-2o-turno-e-concluido-sem-divergencias-em-sao-paulo) | 33 urnas: 30 no Centro Cultural São Paulo e três com biometria na Unip; a notícia relata ausência de divergências. | Evidência documental de resultado de uma amostra estadual. Aproximadamente 16 mil cédulas preparadas não devem ser tratadas automaticamente como 16 mil votos efetivamente executados. |
| [TSE, confirmação das melhorias do Teste Público da Urna, 15/5/2026](https://www.tse.jus.br/comunicacao/noticias/2026/Maio/eleicoes-2026-testes-confirmam-mais-uma-vez-a-seguranca-do-sistema-eleitoral-brasileiro) | Etapa de confirmação de 13 a 15/5, vinculada ao teste de dezembro de 2025; quatro testes selecionados. A matéria relata eficácia das melhorias verificadas pelos participantes. | Evidência sobre testes de segurança e correções, com autoria institucional identificada. Não é auditoria dos votos de outubro nem demonstração matemática de segurança absoluta. |

Observação de qualidade: a legenda da foto da notícia do TSE sobre o segundo turno menciona 2025; o corpo, a publicação de 25/10/2026 e a referência expressa às eleições de 2026 identificam o evento. Não usar a legenda como data do teste.

## Atas localizadas: prioridade para obter tabelas

As linhas desta tabela registram o que os portais listam. Não afirmam que os anexos já foram lidos ou que necessariamente contêm tabelas aproveitáveis.

| Portal oficial | Documentos localizados e cobertura | Estado do acesso nesta pesquisa |
|---|---|---|
| [TRE-DF, Auditoria 2026](https://www.tre-df.jus.br/eleicoes/auditoria-da-votacao-eletronica-2026) | Item 1.9: atas CLDF, TSE e biometria dos dois turnos. Atas padronizadas de biometria: seções 230/244 no 1º turno e 229/247 no 2º. | Atas CLDF, TSE e biometria 229 do segundo turno baixadas pelo Chrome e lidas integralmente; resultados acima. As demais não foram lidas. |
| [TRE-RJ, Auditoria 2026](https://www.tre-rj.jus.br/eleicoes/eleicoes-plebiscitos-e-referendos/eleicoes-2026/auditoria-da-votacao-eletronica) | Lista atas de integridade dos dois turnos, atas de definição das urnas e atas de biometria do 1º turno para seções 286/373. Plano de 33 urnas para integridade e dez para autenticidade. | Texto lido; anexos ainda não obtidos. Prioridade: “Ata do Teste de Integridade – 2º turno”. |
| [TRE-SC, Auditoria 2026](https://www.tre-sc.jus.br/eleicoes/eleicoes-2026/eleicoes-2026-auditoria-de-votacao-eletronica) | Lista atas do sorteio e da execução nos dois turnos. Por turno: 25 urnas para integridade convencional, duas com biometria e oito para autenticidade. | Texto lido; anexos ainda não obtidos. São 27 urnas de integridade, não 35. |
| [TRE-TO, COAVE 2026](https://www.tre-to.jus.br/eleicoes/eleicoes-2026/auditoria-coave-2026) | Atas de encerramento e biometria do 1º turno com links; documentos de autenticidade também listados. Plano de 20 urnas de integridade, incluindo duas com biometria, e três de autenticidade. | Portal aberto e links extraídos. As entradas de encerramento da integridade do 2º turno apareciam sem link no extrator. Anexos do 1º turno retornaram conteúdo vazio. |
| [TRE-BA, Auditoria 2026](https://www.tre-ba.jus.br/eleicoes/eleicoes-2026-1/auditoria-da-votacao-eletronica) | Seleção de urnas dos turnos em PDF/CSV e documentação de auditoria. | Página localizada. Não foi obtida tabela de comparação de resultados. |
| [TRE-PA, Auditoria 2026](https://www.tre-pa.jus.br/eleicoes/eleicoes-2026-1/auditoria-da-votacao-eletronica-eleicoes-2026) | Documentação de seleção de seções e procedimentos. | Página localizada. Não foi obtida tabela de comparação de resultados. |

Links exatos de anexos do Tocantins, recuperados do portal, ainda sem conteúdo conferido:

- [Ata 23/2026: encerramento da integridade, 1º turno](https://www.tre-to.jus.br/eleicoes/eleicoes-2026/auditoria-coave-2026/arquivos-atas/1-turno-2026/ata_23_sei_000012302790853).
- [Ata de integridade com biometria, seção 410](https://www.tre-to.jus.br/eleicoes/eleicoes-2026/auditoria-coave-2026/arquivos-atas/1-turno-2026/ata-do-teste-de-integridade-com-biometria-secao-410).
- [Ata de integridade com biometria, seção 614](https://www.tre-to.jus.br/eleicoes/eleicoes-2026/auditoria-coave-2026/arquivos-atas/1-turno-2026/ata-do-teste-de-integridade-com-biometria-secao-614).

## TCU: fiscalização de 2026 e uma pista para relatórios já encaminhados

O [Acórdão 2558/2026–Plenário, de 16/9/2026](https://pesquisa.apps.tcu.gov.br/doc/acordao-completo/2558/2026/Plen%C3%A1rio), processo 019.754/2026-4, autoriza a fiscalização dos testes nos 27 TREs. É autorização, não resultado final.

A [notícia do TCU de 2/10/2026](https://portal.tcu.gov.br/imprensa/noticias/eleicoes-2026-tcu-acompanha-testes-de-integridade-das-urnas-eletronicas) identifica o processo de execução **020.282/2026-5**. Seu objeto é acompanhar a conformidade dos procedimentos de integridade, com e sem biometria. Prevê relatório consolidado ao TSE em até 30 dias corridos após o segundo turno. Não confundir esse prazo de cooperação com o prazo de 90 dias do consolidado do TSE.

O [índice público de processos do TCU](https://pesquisa.apps.tcu.gov.br/resultado/processo/elei%25C3%25A7%25C3%25B5es/%2520%2520) mostra o processo 020.282/2026-5 aberto, com peças de transparência ativa 77, 44 e 5. O trecho indexado identifica a peça 44 como disponibilização de relatórios do primeiro turno e outro despacho como disponibilização após a segunda etapa. Os anexos e eventuais links internos não foram abertos. O coordenador tentou a interface Chrome duas vezes, com falha `ERR_CONNECTION_RESET`. **Nenhum relatório completo desse processo foi inspecionado; não inferimos seu conteúdo dos despachos indexados.** A [página de transparência TSE, exercício 2026](https://www.tse.jus.br/transparencia-e-prestacao-de-contas/auditorias/tribunal-de-contas-da-uniao-exercicio-2026), localizada pelo coordenador, também identifica esse processo.

Não foi localizado nesta pesquisa um relatório final consolidado do TCU de 2026 com conclusão e dados examinados. Ausência no levantamento não significa inexistência.

## BU impresso versus BU digital: precedente concreto, de 2022

Um [relatório disponível na pesquisa oficial do TCU](https://pesquisa.apps.tcu.gov.br/redireciona/acordao-completo/ACORDAO-COMPLETO-2613374) descreve comparação de 559 BUs no primeiro turno e 604 no segundo turno de **2022**, totalizando 1.163 boletins, sem divergências nesse procedimento. A coleta contemporânea do impresso e a comparação com o divulgado permitem verificar transmissão/publicação. O texto também descreve outra amostra de 4.577 boletins do primeiro turno. Esses conjuntos e métodos não devem ser misturados.

O documento contém um trecho isolado com total 1.223, incompatível com 559+604; vários outros trechos e a soma sustentam 1.163. Se esse antecedente for utilizado, citar os quantitativos por turno e registrar a inconsistência editorial. A consulta de pesquisa expôs o conteúdo; a abertura direta da aplicação exige JavaScript. Não usar esses resultados como achados de 2026 ou como resultado de nossa execução.

## Teste Público da Urna 2025 e confirmação em 2026

O [portal oficial TPU](https://www.tse.jus.br/eleicoes/tpu) lista relatórios finais das comissões Avaliadora e Reguladora e o compêndio do evento. URLs extraídas dos links:

- [Relatório final da Comissão Avaliadora](https://www.tse.jus.br/eleicoes/arquivos/tpu-relatorio-final-da-comissao-avaliadora/@@display-file/file/final-relatorio-comissao-avaliadora.pdf).
- [Relatório final da Comissão Reguladora](https://www.tse.jus.br/eleicoes/arquivos/tse-relatorio-final-da-comissao-reguladora-2026).
- [Compêndio do Teste Público de Segurança dos Sistemas Eleitorais de 2025](https://www.tse.jus.br/eleicoes/eleicoes-2026-content/arquivos/compendio-teste-publico-de-seguranca-dos-sistemas-eleitorais-de-2025-teste-publico-da-urna).

Os três downloads diretos retornaram HTTP 403. O extrator web não leu os PDFs. Assim, é correto dizer que o portal oferece os documentos; não é correto resumir como se o conteúdo final tivesse sido examinado. `fontes/auditorias2026/manifesto.json` registra essas tentativas, sem arquivos simulados ou hash inventado. O agente coordenador pode tentar a interface Chrome, em que houve sucesso prévio com outro arquivo TSE.

A [matéria institucional de 18/12/2025](https://www.tse.jus.br/comunicacao/noticias/2025/Dezembro/teste-da-urna-2025-confirma-seguranca-dos-sistemas-eleitorais) relata 29 planos executados, 19 integralmente e dez parcialmente, com achados de aperfeiçoamento. A etapa de confirmação de maio de 2026 é um evento posterior. Usar as datas correspondentes, sem chamar o teste de dezembro de experimento eleitoral de outubro.

## Disponibilidade, prazos e limites

A [notícia TSE de 1/11/2026](https://www.tse.jus.br/comunicacao/noticias/2026/Novembro/tres-devem-encaminhar-ao-tse-relatorios-de-auditoria-das-urnas-eletronicas-ate-4-de-novembro) informa o envio dos relatórios do segundo turno até 4/11. A remessa não comprova publicação imediata. O [calendário eleitoral consolidado](https://www.tse.jus.br/legislacao/compilada/res/2026/resolucao-no-23-760-de-2-de-marco-de-2026) fixa 24/11/2026 como data-limite para publicação dos relatórios individuais dos TREs. A [Resolução 23.673 consolidada, art. 66](https://www.tse.jus.br/legislacao/compilada/res/2021/resolucao-no-23-673-14-de-dezembro-de-2021) prevê o consolidado TSE em até 90 dias após o segundo turno. Em 6/11, portanto, os prazos finais de publicação ainda não haviam se esgotado.

O art. 66 exige registro da contagem manual independente em pelo menos uma urna do local e de ocorrências durante os procedimentos. Já o art. 66-J restringe o fornecimento de BU, RDV e logs das urnas submetidas ao teste de integridade. Essa regra é específica dos equipamentos do teste; não é uma proibição geral de acesso aos arquivos das seções reais. Para montar a dupla entrada/saída do teste, a fonte viável pode ser a ata/relatório com contagens, não o download dos arquivos brutos do equipamento.

## Aplicação ao experimento com Grover

1. Uma tabela real de integridade permitiria comparar, para cada candidato/categoria e urna testada, a contagem independente com a contagem eletrônica. Manter documento, página, turno e identificador da urna para cada linha transcrita. Verificar manualmente números e OCR.
2. Sem essa tabela, o caminho reproduzível continua sendo RDV versus BU de votação real, com a conclusão limitada à consistência dos arquivos examinados. As notícias de integridade entram como contexto bibliográfico separado.
3. Se as linhas reais forem todas iguais, há zero soluções para a busca. O experimento deve mostrar esse caso, sem introduzir uma divergência oculta e chamá-la de fraude encontrada. Um controle alterado só é válido quando identificado como alteração de teste.
4. Grover procura diferenças conforme a regra implementada; não determina intenção, autoria ou fraude. Uma divergência demanda conferência dos dados e investigação de sua causa.
5. Nem um resultado negativo numa amostra nem uma rodada de Grover certifica ausência de divergências nacionais. A teoria para dados completos, erro probabilístico e número desconhecido de soluções está em `abrangencia-nacional-grover.md`.

Não foram executados experimentos, nem acessado hardware, nem alterado o artigo nesta pesquisa. Pendências prioritárias: abrir as peças TCU 77/44 e procurar os relatórios quantitativos mencionados nas atas. As atas lidas já oferecem evidência documental para uma discussão concreta, mas os totais por urna não substituem as contagens por candidato necessárias para refazer a comparação.

## Parágrafo sugerido para o artigo — menos de 150 palavras

As atas do segundo turno de 2026 documentam verificações com votos previamente registrados em papel. No TSE, duas urnas receberam 389 votos, sem divergências na comparação final; a ata também registra dois eventos chamados de falso positivo, sem detalhar sua causa (ata TSE, p. 4–5). Na Câmara Legislativa do Distrito Federal, 16 urnas receberam votos de 3.585 cédulas. Houve uma diferença para governador: o operador digitou 11 quando o papel indicava branco. Segundo a comissão, a revisão das filmagens confirmou erro humano, sem indício de falha da urna (ata CLDF, p. 4–5). O episódio mostra que encontrar uma diferença não determina sua causa. Esses resultados são documentais, pertencem às urnas testadas e complementam a análise presidencial deste trabalho; não são resultados de nossa execução de Grover nem certificam a ausência de fraude na eleição nacional.

Na versão final, substituir as indicações entre parênteses pelas referências bibliográficas das duas atas. As imagens integrais ficam somente no material de proveniência; não é necessário reproduzir assinaturas e nomes dos participantes no artigo.
