"""Verificação restrita de arquivos publicados; usa utilitário oficial inalterado."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parent
OFFICIAL=ROOT/'oficial'
sys.path.insert(0,str(OFFICIAL))
from lib.mr_util import extrai_entidade_decoded,extrai_chave_certificado_hw,valida_certificado,common_name
sample=ROOT.parent.parent/'fontes-tse';stem='o03221ac0100700090001'
schema=str(ROOT.parent.parent/'fontes-tse/spec/assinatura.asn1');vsc=str(sample/(stem+'-vota.vsc'))
e,codec=extrai_entidade_decoded(schema,vsc,'EntidadeAssinaturaEcourna')
x509,_,key,verifier=extrai_chave_certificado_hw(schema,vsc)
certok=valida_certificado(x509,verifier);assert certok
output=dict(certificado_assinatura_valida=certok,emissor=common_name(x509['tbsCertificate']['issuer'][1]),sujeito=common_name(x509['tbsCertificate']['subject'][1]),validade_declarada=str(x509['tbsCertificate']['validity']),arquivos=[],ausentes=[],auto_hashes={},limites='Assinatura do certificado verificada com chave do emissor incorporada no utilitário oficial. Não foi executada validação completa de cadeia, validade temporal, revogação ou assinatura de software. Assinaturas de hardware somente dos três arquivos publicados selecionados.')
for tag in ['assinaturaSW','assinaturaHW']:
 en=e[tag];output['auto_hashes'][tag]=hashlib.sha512(en['conteudoAutoAssinado']).digest()==en['autoAssinado']['assinatura']['hash'];assert output['auto_hashes'][tag]
hw=codec.decode('Assinatura',e['assinaturaHW']['conteudoAutoAssinado'])
sw=codec.decode('Assinatura',e['assinaturaSW']['conteudoAutoAssinado'])
swmap={x['nomeArquivo']:x for x in sw['arquivosAssinados']}
for row in hw['arquivosAssinados']:
 name=row['nomeArquivo'];path=sample/name
 if not path.exists():output['ausentes'].append(name);continue
 if not name.endswith(('-bu.dat','-rdv.dat','-log.jez')):continue
 digest=hashlib.sha512(path.read_bytes()).digest();assert digest==row['assinatura']['hash']==swmap[name]['assinatura']['hash']
 signature=row['assinatura']['assinatura'];message=hashlib.sha512(digest).digest()
 valid=verifier.verify(message,signature,key);assert valid
 altered=bytes([message[0]^1])+message[1:];negative=verifier.verify(altered,signature,key);assert not negative
 output['arquivos'].append(dict(nome=name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),hash_hw_sw_ok=True,assinatura_hw_valida=valid,controle_negativo_rejeitado=not negative))
output['sha256_codigo_oficial']={str(f.relative_to(OFFICIAL)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [OFFICIAL/'assinatura_hash.py',OFFICIAL/'lib/mr_util.py']}
(ROOT/'assinaturas-amostra-resultado.json').write_text(json.dumps(output,ensure_ascii=False,indent=2));print(json.dumps(output,ensure_ascii=False,indent=2))
