from pathlib import Path
import json,gzip,time,struct,zlib,hashlib
from collections import Counter
import asn1tools
from inventariar_zip_remoto import read
ROOT=Path(__file__).resolve().parent
spec=ROOT.parent/'formatos-2026/spec'
RC=asn1tools.compile_files(str(spec/'rdv.asn1'),'ber');BC=asn1tools.compile_files(str(spec/'bu.asn1'),'ber')
def extract(data,start,e):
 off=e['offset']-start;h=struct.unpack_from('<4s5H3I2H',data,off);assert h[0]==b'PK\x03\x04'
 begin=off+30+h[-2]+h[-1];b=data[begin:begin+e['compressed']]
 b=zlib.decompress(b,-15) if e['method']==8 else b
 assert len(b)==e['size'] and zlib.crc32(b)==e['crc']
 return b

def compare(rbytes,bbytes):
 r=RC.decode('EntidadeResultadoRDV',rbytes)['rdv'];env=BC.decode('EntidadeEnvelopeGenerico',bbytes);b=BC.decode('EntidadeBoletimUrna',env['conteudo'])
 assert r['fase']==b['fase']=='oficial';assert r['pleito']==b['cabecalho']['idEleitoral'][1]==3221
 for f in ['municipioZona','secao']:assert r['identificacao'][f]==b['identificacaoSecao'][f]
 rc=Counter();bc=Counter();origins=[];comparecimento_cargo=0
 for election in r['eleicoes'][1]:
  if election['idEleicao']!=6258:continue
  origins.append(election.get('origemVotosSA','urna'))
  for office in election['votosCargos']:
   if office['idCargo'][1]!='presidente':continue
   for v in office['votos']:
    typ=v['tipoVoto'];code=int(v['digitacao']) if typ=='nominal' else 95 if typ.startswith('branco') else 96 if typ.startswith('nulo') else None
    assert code in [13,22,95,96],(typ,code)
    rc[code]+=1
 for election in b['resultadosVotacaoPorEleicao']:
  if election['idEleicao']!=6258:continue
  for res in election['resultadosVotacao']:
   for office in res['totaisVotosCargo']:
    if office['codigoCargo'][1]!='presidente':continue
    comparecimento_cargo+=res['qtdComparecimento']
    for v in office['votosVotaveis']:
     typ=v['tipoVoto'];code=v.get('identificacaoVotavel',{}).get('codigo') if typ=='nominal' else 95 if typ.startswith('branco') else 96 if typ.startswith('nulo') else None
     assert code in [13,22,95,96],(typ,code);bc[code]+=v['quantidadeVotos']
 assert rc==bc,(rc,bc)
 assert sum(rc.values())==comparecimento_cargo,('comparecimento_cargo',sum(rc.values()),comparecimento_cargo)
 return dict(votos=dict(rc),comparecimento=comparecimento_cargo,origens=origins,tipo_rdv=r['eleicoes'][0],identificacao=r['identificacao'])
if __name__=='__main__':
 s=json.loads((ROOT/'inventario-AC.json').read_text());entries=[json.loads(l) for l in gzip.open(ROOT/'membros-AC.jsonl.gz','rt')]
 start=time.monotonic();data=read(s['url'],0,32*1024*1024-1);download=time.monotonic()-start
 chosen={e['name']:e for e in entries if e['offset']+e['compressed']+512<len(data)}
 begin=time.monotonic();results=[]
 for name,e in chosen.items():
  if name.endswith('-rdv.dat'):
   stem=name[:-8];bu=chosen.get(stem+'-bu.dat') or chosen.get(stem+'-busa.dat')
   if bu:results.append(compare(extract(data,0,e),extract(data,0,bu)))
 elapsed=time.monotonic()-begin
 out=dict(bytes_download=len(data),segundos_download=download,mb_por_segundo=len(data)/1e6/download,secoes=len(results),segundos_decodificacao=elapsed,secoes_por_segundo=len(results)/elapsed,divergencias=0)
 (ROOT/'benchmark.json').write_text(json.dumps(out,indent=2));print(out)
