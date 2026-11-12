# Origem das chaves usadas na verificação

Consulta: 06/11/2026.

## Assinaturas dos arquivos da urna, amostra Bujari

O pacote oficial [Formato de arquivos de BU, RDV e assinatura digital — 2026](https://www.tse.jus.br/eleicoes/eleicoes-2026-content/arquivos/formato-arquivos-de-bu-rdv-e-assinatura-digital) fornece `assinatura_hash.py` e `lib/mr_util.py`. Estes foram preservados em `oficial/`, sem alterar sua lógica. O segundo contém certificados/chaves de emissores incorporados pelo TSE; para a amostra, o emissor identificado foi AC UE2022.

O certificado da urna vem no envelope original `o03221ac0100700090001-vota.vsc`. Primeiro se confere sua assinatura com a chave do emissor; depois as assinaturas de hardware do BU, RDV e log com a chave da urna. Os hashes dos arquivos coincidiram com os envelopes SW/HW. Uma mensagem alterada foi rejeitada em cada controle negativo.

Isso não implementa validação completa de cadeia, políticas de certificado, revogação, assinatura SW nem assinaturas de todas as urnas. Os arquivos ausentes mencionados pelo exemplo oficial não foram buscados indiscriminadamente; a verificação restrita identifica seu alcance. Fonte do ZIP e hashes da especificação: `../../fontes-tse/proveniencia-leiaute-2026.json`.

## Assinatura do resultado nacional

A chave Ed25519 foi fixada a partir do Apêndice B do [Manual oficial de verificação JWS](https://www.tse.jus.br/eleicoes/eleicoes-2026-content/arquivos/divulgacao-de-resultados/manual-verificacao-jws), e não aceita automaticamente a partir do token recebido:

```json
{"kty":"OKP","use":"sig","key_ops":["verify"],"alg":"EdDSA","kid":"sNbt9Q_fLS65zE1_ZLNV-XRRwPY","crv":"Ed25519","x":"kWlpNHjuws1csyQZwzn3Fhzbi3RD435RbpThtSr4hMc"}
```

JWS consultado: [Resultado presidencial nacional, eleição6258](https://resultados.tse.jus.br/oficial/ele2026/6258/dados/br/br-c0001-e006258-u.jws). A assinatura foi válida, o payload coincidiu com o JSON final congelado e a mensagem alterada foi rejeitada. Não foi executada validação de cadeia X.509/LCR. A conclusão se refere à assinatura verificada com a chave pública oficial adotada.
