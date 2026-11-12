"""Confere cobertura e valores RDV/BU binários com BWeb por seção e EA20 nacional."""
from pathlib import Path
from collections import Counter
import csv,gzip,io,json,zipfile,hashlib
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'resultados';BWEB=ROOT.parent/'nacional'
expected=json.loads((BWEB/'resultado-nacional.json').read_text());sources=json.loads((BWEB/'fontes-bu.json').read_text())
results=[];total=Counter()
for source in sources:
 uf=source['uf'];r=json.loads((OUT/f'{uf}-resumo.json').read_text())
 assert not r['erros'] and not r['pares_incompletos'],uf
 binary={}
 assert hashlib.sha256((OUT/f'{uf}-secoes.csv.gz').read_bytes()).hexdigest()==r['sha256_csv']
 with gzip.open(OUT/f'{uf}-secoes.csv.gz','rt') as f:
  for row in csv.DictReader(f):
   key=tuple(int(row[k]) for k in ['municipio','zona','secao']);assert key not in binary
   assert row['stem']==f'o03221{uf.lower()}{key[0]:05d}{key[1]:04d}{key[2]:04d}',(uf,row['stem'],key)
   binary[key]={code:int(row[f'rdv_{code}']) for code in [13,22,95,96]}
   assert all(row[f'rdv_{code}']==row[f'bu_{code}'] for code in [13,22,95,96])
   assert sum(binary[key].values())==int(row['comparecimento'])
   if not sum(binary[key].values()):assert uf=='ZZ' and key in [(30686,1,443),(29564,1,91)]
 assert len(binary)==r['secoes_recontadas']
 web={};seen=set()
 with zipfile.ZipFile(BWEB/'originais'/source['url'].rsplit('/',1)[1]) as z:
  name=next(n for n in z.namelist() if n.endswith('.csv'))
  with z.open(name) as f:
   for row in csv.DictReader(io.TextIOWrapper(f,encoding='latin1'),delimiter=';'):
    if row['CD_ELEICAO']!='6258':continue
    if row['CD_CARGO_PERGUNTA'] not in ['1','-1']:continue
    key=tuple(int(row[k]) for k in ['CD_MUNICIPIO','NR_ZONA','NR_SECAO']);values=web.setdefault(key,{13:0,22:0,95:0,96:0})
    if row['CD_CARGO_PERGUNTA']=='-1':assert row['QT_VOTOS']=='0' and row['QT_COMPARECIMENTO']=='0';continue
    code=int(row['NR_VOTAVEL']);assert code in values;assert (key,code) not in seen;seen.add((key,code));values[code]=int(row['QT_VOTOS'])
 missing=sorted(set(web)-set(binary));extra=sorted(set(binary)-set(web));diff=[k for k in web.keys()&binary.keys() if web[k]!=binary[k]]
 assert not missing and not extra and not diff,(uf,missing[:2],extra[:2],diff[:2])
 totals={str(code):sum(v[code] for v in binary.values()) for code in [13,22,95,96]}
 assert totals=={str(code):r['votos'].get(str(code),0) for code in [13,22,95,96]}
 total.update(totals);results.append(dict(uf=uf,secoes=len(binary),faltantes=len(missing),extras=len(extra),divergencias=len(diff),votos=totals,origens=r['origens'],requests=r['requests'],bytes_recebidos=r['bytes_recebidos'],segundos=r['segundos']))
 print(uf,'cobertura e votos coincidem:',len(binary),flush=True)
keys={'13':'lula','22':'flavio','95':'brancos','96':'nulos'}
assert all(total[code]==expected['resultado_oficial'][k] for code,k in keys.items())
summary=dict(ano=2026,turno=2,eleicao=6258,pleito=3221,abrangencias=28,secoes=sum(r['secoes'] for r in results),votos=dict(total),total_votos=sum(total.values()),divergencias_rdv_bu=0,divergencias_binarios_csv=0,secoes_faltantes=0,secoes_extras=0,bytes_recebidos=sum(r['bytes_recebidos'] for r in results),requests=sum(r['requests'] for r in results),origens=dict(sum((Counter(r['origens']) for r in results),Counter())),por_uf=results,limite='Consistência dos RDVs publicados, BUs binários, CSVs e totalização. Há29 RDVs de apuração por cédulas; não são registros diretos da digitação do eleitor. Assinaturas nacionais, cadeia completa, revogação e logs nacionais não foram verificados. Não constitui prova de ausência de fraude em todo o processo.')
(OUT/'conclusao-nacional.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
with (OUT/'totais-nacionais.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['categoria','rdv','bu_binario','bu_csv','ea20_oficial','diferenca'])
 for code,k in keys.items():w.writerow([k,total[code],total[code],total[code],expected['resultado_oficial'][k],0])
print(json.dumps({k:v for k,v in summary.items() if k!='por_uf'},ensure_ascii=False,indent=2))
