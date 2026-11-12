# Presidência — segundo turno de 2026

Amostra da mesma seção de Bujari/AC utilizada na pesquisa anterior: município TSE 01007, zona 9, seção 1. Votação de 25/10/2026, pleito 3221 e eleição presidencial 6258. Originais do primeiro turno foram preservados em outro diretório; nada foi sobrescrito.

| Categoria | Recontagem RDV | Boletim de Urna |
|---|---:|---:|
| Lula (13) | 68 | 68 |
| Flávio Bolsonaro (22) | 149 | 149 |
| Brancos | 2 | 2 |
| Nulos | 13 | 13 |
| **Total** | **232** | **232** |

Essas quatro categorias representam toda a votação presidencial da seção, e a soma coincide com o comparecimento. A mesma urna tem registros de governador, eleição 6260, comparados separadamente pelo script: 49, 154, 5 e 24 votos. A tabela presidencial não mistura cargos.

## Fontes e arquivos

- Conjunto oficial: https://dadosabertos.tse.jus.br/dataset/resultados-2026-arquivos-transmitidos-para-totalizacao
- ZIP observado no catálogo: https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/arqurnatot/bu_imgbu_logjez_rdv_vscmr_2026_2t_AC.zip
- Leiaute oficial de 2026: https://www.tse.jus.br/eleicoes/eleicoes-2026-content/arquivos/formato-arquivos-de-bu-rdv-e-assinatura-digital
- Identidade dos candidatos: https://www.tse.jus.br/eleicoes/eleicoes-2026-content/propostas-de-governo-dos-candidatos-ao-cargo-de-presidente-da-republica-eleicoes-2026/planos-de-governo-dos-candidatos-ao-cargo-de-presidente-da-republica-eleicoes-2026

Consulta em 6/11/2026 (São Paulo). `proveniencia-download.json` registra URL, cabeçalhos HTTP, tamanhos e posições das entradas no ZIP. Os originais são `o03221ac0100700090001-bu.dat`, `-rdv.dat`, `-log.jez` e `-vota.vsc`. Os esquemas ASN.1 oficiais de 2026 estão em `spec/`; seus hashes e a origem do pacote constam em `proveniencia-leiaute-2026.json`.

O arquivo para o experimento é `amostra-presidencia-2026-2t.json`. A tabela de quatro linhas está em `comparacao-presidencia-2026-2t.csv`; a comparação dos dois cargos e oito categorias está em `comparacao-completa-2026.csv`.

## Reprodução

Python 3.11 e dependências em `requirements.txt`:

```sh
python -m pip install -r requirements.txt
python baixar_amostra_2026.py
python recontagem_2026.py
python conferir_hashes_2026.py
```

Os três comandos foram executados com sucesso. O primeiro usa HTTP Range para obter apenas o diretório ZIP e quatro arquivos, sem baixar todo o pacote estadual; verifica tamanho e CRC de cada entrada. Falha se Range não for atendido, ou se um arquivo existente diferir da origem, preservando o original.

A recontagem usa a especificação ASN.1 oficial e codec BER. Confere fase, pleito e identificação da seção, agrupa votos nominais por candidato e brancos/nulos por categoria. Assertivas conferem igualdade de todos os totais e a soma presidencial de 232 votos.

A conferência SHA512 de BU, RDV e log coincidiu com os hashes contidos nos dois envelopes SW/HW. A assinatura criptográfica e a cadeia de certificados não foram verificadas; hashes coincidentes não devem ser apresentados como essa verificação.

## Conclusão permitida

Nesta seção, os totais recontados do RDV coincidem com o BU para Presidência no segundo turno de 2026. Nenhuma divergência real foi encontrada nessa comparação. Os dois arquivos vêm da mesma urna; não são evidências plenamente independentes. O resultado não certifica a integridade de toda a eleição.

Para testar Grover, a divergência deve ser introduzida em uma cópia identificada como artificial, preservando estes originais. A conclusão experimental deverá tratar da capacidade de localizar essa diferença controlada, das repetições e dos efeitos do ruído. Nenhum circuito quântico ou execução IBM foi realizado por esta etapa de pesquisa.
