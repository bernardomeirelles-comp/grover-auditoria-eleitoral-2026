# Verificação de fontes e procedência eleitoral

Consulta em 11 de novembro de 2026, horário de Brasília. A requisição do resultado nacional recebeu cabeçalho HTTP Date de 12/11/2026 às 00:29:33 UTC, equivalente a 11/11 às 21:29:33 em Brasília. Foram consultados os endereços públicos, sem acesso autenticado e sem execução na IBM.

## Evidência de ambiente oficial

A [documentação técnica de 2026 do TSE](https://www.tse.jus.br/eleicoes/informacoes-tecnicas-sobre-a-divulgacao-de-resultados) associa o segundo turno de 25/10/2026 ao pleito 3221 e à eleição geral federal 6258 no ambiente `oficial`, sob `resultados.tse.jus.br`.

A mesma página distingue o ambiente de ensaios, `resultados-sim.tse.jus.br/simulado`, o identificador `simulado2026` e outros códigos de eleição, como 22410 para o ensaio federal do segundo turno. A identificação do conjunto utilizado não depende somente de nomes de candidatos: URL, código da eleição, pleito, turno, datas e campos do arquivo foram conferidos.

O [JSON nacional consultado](https://resultados.tse.jus.br/oficial/ele2026/6258/dados/br/br-c0001-e006258-u.json) respondeu HTTP 200, sem redirecionamento para ambiente de ensaios. Campos observados: `ele=6258`, `t=2`, `f=o`, `dg=25/10/2026`, `hg=23:27:02`, `idg=4241309`, `tf=s`, `and=f`. Seu SHA-256 foi `67fae708b0c7977fc9847d36100c63313621bff971178c48f2da99969707c263`, igual ao hash já preservado em `nacional/resumo-nacional.json`. O JSON interpretado também é idêntico a `nacional/resultado-oficial-br.json`.

| Campo do resultado nacional | Valor consultado |
|---|---:|
| Votos de Lula | 64.256.232 |
| Votos de Flávio Bolsonaro | 59.826.041 |
| Brancos | 1.430.496 |
| Nulos | 2.723.305 |
| Total | 128.236.074 |
| Seções previstas | 499.248 |
| Seções instaladas e apuradas | 499.207 |
| Seções não instaladas | 41 |

Foram consultados também os 28 endereços de abrangência usados em `nacional/resultados-oficiais-uf/`, incluindo DF e ZZ. O padrão é `https://resultados.tse.jus.br/oficial/ele2026/6258/dados/{uf}/{uf}-c0001-e006258-u.json`. Todos retornaram HTTP 200, eleição 6258, turno 2 e fase `o`; todos os objetos JSON coincidem com os arquivos locais correspondentes. Essa verificação confirma a procedência e a estabilidade desses snapshots; não refaz a recontagem nacional dos RDVs.

## Conferência adicional da amostra de Bujari

O [ZIP de BUs do Acre](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_AC_261020260742.zip) foi baixado novamente em memória e respondeu HTTP 200, com 1.254.611 bytes. SHA-512: `95f19aad9534d21ea703670030ea1d51b5a89c2b40f3ba5466d60de2765b9067f225fd863000c282fe47fb6457a9f43df5fd536dec7753f3813667c99b3efa3b`. O valor coincide com o manifesto local.

As quatro linhas presidenciais da seção 1, zona 9, município 1007, apresentam ano 2026, tipo `Eleição Ordinária`, pleito 3221, data do pleito 25/10/2026, turno 2, eleição 6258 e cargo 1. A geração do CSV é 26/10/2026 às 07:42:38. As contagens são 68 para Lula, 149 para Flávio Bolsonaro, 2 brancos e 13 nulos. Portanto, o valor 148 empregado no experimento é uma alteração artificial da cópia de trabalho, não um registro oficial localizado nesta consulta.

## Cobertura e limites da evidência

O [dataset de arquivos transmitidos](https://dadosabertos.tse.jus.br/dataset/resultados-2026-arquivos-transmitidos-para-totalizacao) declara abranger apenas arquivos em situação Totalizado. O [dataset dos BUs](https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna) separa os turnos e as UFs. É necessário manter a reconciliação das seções, incluindo as duas sem comparecimento e as 41 não instaladas, ao descrever a cobertura.

A evidência consultada sustenta que os snapshots usados pertencem à divulgação oficial da eleição 6258. Ela não fornece uma evidência independente da intenção do eleitor nem prova geral de ausência de fraude. RDV, BU e totalização são registros relacionados do mesmo processo; a [descrição do TSE](https://www.tse.jus.br/eleicoes/historia/processo-eleitoral-brasileiro/votacao/votacao-segura) informa que o BU é gerado a partir do RDV. Os hashes comprovam identidade de arquivos; não substituem a validação de assinaturas ou toda a cadeia de confiança.

A documentação de 2026 contém trechos antigos, como informações sobre candidatura ainda não definitiva e URLs de simulados ainda não disponíveis. Esses trechos convivem com endereços e cronogramas já divulgados. Por isso, a procedência foi baseada nos identificadores da seção Ambiente Oficial e nos arquivos efetivamente recebidos, não na suposição de que toda a página foi atualizada de forma simultânea.

## Referências científicas e alcance

- [Lindeman e Stark, 2012](https://www.stat.berkeley.edu/~stark/Preprints/gentle12.pdf), DOI `10.1109/MSP.2012.56`, IEEE Security & Privacy, 10(5), 42–49. Acrescentado como `lindeman2012`. Fundamenta a distinção entre a concordância de registros digitais relacionados e auditorias limitadoras de risco apoiadas em registros verificáveis pelo eleitor. O procedimento deste trabalho não é uma auditoria limitadora de risco.
- [Boyer et al., 1998](https://arxiv.org/abs/quant-ph/9605034). Fundamenta o efeito do número de soluções e a busca com quantidade desconhecida. As páginas 493–505 existentes na bibliografia coincidem com o registro Crossref do DOI; o arXiv exibe 493–506. Manteve-se o metadado do DOI.
- [Stoudenmire e Waintal, 2024](https://arxiv.org/abs/2303.11317), Physical Review X 14, 041029. Fundamenta examinar a estrutura e os custos do oráculo. Não autoriza concluir que toda aplicação de Grover é inútil.
- [Pokharel e Lidar, 2024](https://arxiv.org/abs/2211.04543), DOI `10.1038/s41534-023-00794-6`, npj Quantum Information 10, artigo 23. Metadados confirmados no Crossref. Fundamenta avaliar estratégias de supressão de erros e limitações da mitigação de leitura, sem presumir que os resultados se transferem ao circuito deste trabalho.
- [AbuGhanem, 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC11711768/), Scientific Reports 15, 1281. Testa diferentes oráculos em circuitos pequenos. Fundamenta variar a posição procurada em controles locais e físicos.
- [Bautra, Dimitrijevs e Yakaryilmaz, 2026](https://arxiv.org/abs/2603.14607). Acrescentado como `bautra2026`, explicitamente preprint, versão 1 de 15/03/2026. Compara modelos de ruído derivados de CSV, backend e snapshots e identifica dependência do dispositivo e da transpilação. Não demonstra que uma calibração atual reconstrói uma execução passada.
- [Documentação Qiskit Aer](https://qiskit.github.io/qiskit-aer/tutorials/2_device_noise_simulation.html). Versão consultada 0.18.2. Descreve uma aproximação de ruído baseada em dados do dispositivo. A simulação deve ser identificada como modelo, e não como reprodução exata de uma máquina.

Foi acrescentada `tseDivulgacao2026`, preservando `tseDivulgacao2024` para não quebrar referências antigas. A redação nova deve citar a chave de 2026 para os dados desta eleição. Todas as chaves anteriores foram mantidas.

## Acesso e verificações que não foram realizadas

As URLs científicas da bibliografia não apresentaram erro 404 na checagem. Parte do portal TSE retornou HTTP 403 ao cliente Python, mas foi legível pela ferramenta de navegação. Isso é limitação de acesso automatizado, não motivo para declarar a fonte inexistente. O endereço do formato BU/RDV entrega ZIP, que a ferramenta de leitura web não extrai. As duas atas TRE-DF e o conteúdo do manual JWS não puderam ser relidos online nesta rodada; suas afirmações específicas dependem dos PDFs locais já preservados. A página oficial de 2026 lista o manual JWS.

Uma tentativa de obter `https://resultados.tse.jus.br/oficial/ele2026/comum/config/ele-c.json` retornou 404. Esse endereço não foi utilizado como evidência e não houve tentativa de adivinhar outras variantes. A identificação do pleito vem da documentação oficial e dos campos do CSV novamente obtido.

Não foram baixados novamente os 28 ZIPs de RDV/BU nem reexecutadas as assinaturas ou a recontagem nacional. Esta nota registra uma verificação de fontes, metadados e correspondência dos resultados publicados. Não substitui os testes dos programas e a documentação das execuções nacionais.
