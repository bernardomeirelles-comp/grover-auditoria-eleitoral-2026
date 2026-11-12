# Preparação do pacote público

Estado: versão de entrega `sprint2-revisada`, com PDF compilado no Overleaf e conferido visualmente em suas sete páginas. O repositório de destino é [bernardomeirelles-comp/grover-auditoria-eleitoral-2026](https://github.com/bernardomeirelles-comp/grover-auditoria-eleitoral-2026). O PDF do pacote é idêntico ao arquivo final entregue. Seu texto coincide com a compilação local após normalização de espaços e ligaturas.

## Conteúdo

O pacote reúne o artigo, suas fontes, os programas, as tabelas nacionais e a procedência dos dados. Estão presentes os 28 CSVs gzip por seção, os hashes individuais e as versões de código registradas na recontagem. As cópias em `codigo-executado` documentam a versão usada na coleta. Foram excluídos históricos de redação, rascunhos, pilotos, caches, grandes ZIPs e a pasta duplicada `arquivos-complementares`.

A revisão IBM inclui três trabalhos de 512 repetições por caso, com 12 segmentos em cada trabalho. A interface exibiu dois segundos de QPU por trabalho, seis segundos no total. A tabela dos 12 casos agregados fica em `revisao/analise-ibm/tabela-resultados.md`; os CSVs preservam também o detalhamento por bloco. O artigo é entregue uma única vez, em `artigo.pdf`.

## Metadados IBM saneados

As versões públicas omitem somente os campos de identificação da conta listados abaixo. Resultados, circuitos e parâmetros científicos foram preservados. Os arquivos privados originais não foram alterados. A análise foi reexecutada sobre a cópia pública para que os hashes de entrada identifiquem seus metadados saneados.

```json
[
  {
    "file": "revisao/composer/brutos/job-dbqhnlhabdes73fo9s1g-info.json",
    "removed_fields": [
      "user_id"
    ],
    "private_original_sha256": "d0a2494ea085b638e3697d02e221ebbe60c645985563b3e0a4171b200ecba652",
    "public_sha256": "b028f1ffe94ef10bba7808937464530e9018da728bd4b72a89f29fd3c5c238a0",
    "results_altered": false
  },
  {
    "file": "revisao/composer/brutos/job-dbqggnfv5hds73dg1q00-info.json",
    "removed_fields": [
      "user_id"
    ],
    "private_original_sha256": "79178ca4299e62ed437796edf32152c29e10dddece38de3155b612f104e9f8dc",
    "public_sha256": "9365ac5fd689c36ce85ad1c69afbbf6776fd24e17763ab15737e6cbb4a99f0c8",
    "results_altered": false
  },
  {
    "file": "revisao/composer/brutos/job-dbqgid7v5hds73dg1rp0-info.json",
    "removed_fields": [
      "user_id"
    ],
    "private_original_sha256": "6bef5e1777a6a7f1b5601faeea152457060d649a4c8723645aac5f17aaa37b19",
    "public_sha256": "699608d32c8d5305d3763d751cd33897b15501e6085e44bc04aaa4ac2dd83f2e",
    "results_altered": false
  }
]
```

## Verificações executadas

- Instalação das dependências principais em ambiente virtual novo com Python 3.11 em macOS ARM64; `pip check` sem conflitos, inclusive após a sincronização final.
- Reanálise pública dos três trabalhos: 36 segmentos validados, `complete_three_block_design=true`, circuitos físicos e três sequências completas aprovados na validação ideal.
- Todos os hashes de entrada dos relatórios IBM correspondem às cópias públicas. Os três arquivos `result.json` são byte a byte iguais às exportações originais.
- Conferência offline das tabelas: 28 abrangências, 499.207 seções e 128.236.074 votos.
- Hashes SHA-512 de BU, RDV e log da amostra: conferidos nos envelopes SW e HW.
- Quatro controles clássicos negativos rejeitados, inclusive troca de categoria preservando o total.
- JWS nacional: assinatura válida para a chave pública fixada, conteúdo coincidente e controle negativo rejeitado.
- Manifesto histórico `recontagem-nacional/SHA256SUMS`: todos os arquivos presentes e hashes coincidentes. Seis logs foram recuperados das cópias com extensão alternativa e validados pelos hashes históricos.
- No ambiente novo, passaram 708 verificações do oráculo em 59 pares de entrada, a reanálise do resultado IBM histórico e a geração de figuras. As probabilidades ideais com zero, uma, duas, três e quatro soluções foram, respectivamente, zero, um, 0,5, zero e um.
- Nenhum padrão de chave privada, token GitHub, Bearer, CRN, identificador IBM ou atribuição literal de senha/token foi encontrado na varredura auxiliar. Certificados públicos e o JWS eleitoral são dados de verificação.
- As figuras referenciadas pelo TEX estão presentes. Nenhum arquivo alcança o limite de 100 MB do GitHub.

## Limites

Os ZIPs nacionais de RDV/BU e BWeb e o ZIP de votação por seção não integram o pacote. Seus endereços e hashes foram preservados. A redecodificação completa depende da rede; a conferência das tabelas entregues funciona offline. Dados brutos que não foram preservados integralmente precisam ser obtidos novamente das fontes indicadas.

A instalação opcional dos validadores de assinatura de hardware e a repetição da coleta nacional não foram executadas neste ambiente novo. As dependências principais estão fixadas, mas não há imagem de sistema nem lock de todas as dependências transitivas. A varredura de credenciais é auxiliar e não equivale a auditoria formal de segurança.

Não houve nova submissão IBM durante esta preparação. Os resultados nacionais descrevem concordância entre registros públicos; não certificam a intenção do eleitor nem ausência absoluta de fraude. A comparação quântica mede a convenção de consultas descrita no artigo, sem demonstrar vantagem de tempo total. O modelo de ruído é aproximado e não identifica uma causa única para a perda observada.

O `MANIFEST.sha256` identifica os bytes entregues, excluindo o próprio manifesto, a pasta Git e caches. Reexecutar os programas pode atualizar arquivos derivados; confira primeiro o manifesto e trabalhe em uma cópia.
