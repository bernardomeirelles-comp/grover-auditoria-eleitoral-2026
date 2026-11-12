from pathlib import Path
import base64,hashlib,json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
ROOT=Path(__file__).resolve().parent
SOURCE='https://www.tse.jus.br/eleicoes/eleicoes-2026-content/arquivos/divulgacao-de-resultados/manual-verificacao-jws'
KEY={'kty':'OKP','use':'sig','key_ops':['verify'],'alg':'EdDSA','kid':'sNbt9Q_fLS65zE1_ZLNV-XRRwPY','crv':'Ed25519','x':'kWlpNHjuws1csyQZwzn3Fhzbi3RD435RbpThtSr4hMc'}
def dec(x):return base64.urlsafe_b64decode(x+'='*((-len(x))%4))
token=(ROOT/'resultado-final-br.jws').read_text().strip();head,payload,sig=token.split('.')
h=json.loads(dec(head));assert h['alg']==KEY['alg'] and h['kid']==KEY['kid']
key=Ed25519PublicKey.from_public_bytes(dec(KEY['x']));message=(head+'.'+payload).encode();key.verify(dec(sig),message)
body=dec(payload);official=ROOT.parent/'nacional-2026-2t/resultado-oficial-br.json'
assert json.loads(body)==json.loads(official.read_bytes())
try:key.verify(dec(sig),message+b'x')
except InvalidSignature:negative=True
else:raise RuntimeError('Controle negativo não rejeitado')
out=dict(url_jws='https://resultados.tse.jus.br/oficial/ele2026/6258/dados/br/br-c0001-e006258-u.jws',fonte_chave=SOURCE,chave_publica=KEY,assinatura_eddsa_valida=True,payload_igual_json_final=True,controle_negativo_rejeitado=negative,sha256_jws=hashlib.sha256(token.encode()).hexdigest(),sha256_json=hashlib.sha256(official.read_bytes()).hexdigest(),limite='Verificação Ed25519 com chave pública fixada do Apêndice B do manual oficial. Não executa validação de cadeia X.509/LCR; não verifica assinaturas dos arquivos de urna nacionais.')
(ROOT/'jws-final-resultado.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False,indent=2))
