"""Confere tabelas e totais entregues sem baixar dados; não redecodifica RDVs."""
from pathlib import Path
from collections import Counter
import csv,gzip,hashlib,json
ROOT=Path(__file__).resolve().parent
national=json.loads((ROOT/'resultados/conclusao-nacional.json').read_text())
expected=json.loads((ROOT.parent/'nacional/resultado-nacional.json').read_text())
total=Counter();sections=0;origins=Counter()
for ufdata in national['por_uf']:
 uf=ufdata['uf'];summary=json.loads((ROOT/'resultados'/f'{uf}-resumo.json').read_text());path=ROOT/'resultados'/f'{uf}-secoes.csv.gz'
 assert hashlib.sha256(path.read_bytes()).hexdigest()==summary['sha256_csv']
 assert not summary['erros'] and not summary['pares_incompletos']
 keys=set();votes=Counter()
 with gzip.open(path,'rt') as f:
  for row in csv.DictReader(f):
   key=tuple(int(row[x]) for x in ['municipio','zona','secao']);assert key not in keys;keys.add(key)
   assert row['stem']==f'o03221{uf.lower()}{key[0]:05d}{key[1]:04d}{key[2]:04d}'
   for code in ['13','22','95','96']:
    assert row[f'rdv_{code}']==row[f'bu_{code}'];votes[code]+=int(row[f'rdv_{code}'])
   assert sum(int(row[f'rdv_{code}']) for code in ['13','22','95','96'])==int(row['comparecimento'])
   origins.update(row['origens'].split('|'))
 assert len(keys)==summary['secoes_recontadas']==ufdata['secoes']
 assert dict(votes)==summary['votos']==ufdata['votos']
 total.update(votes);sections+=len(keys)
assert sections==national['secoes']==int(expected['secoes_resultado']['sa'])
assert dict(total)==national['votos']
for code,label in {'13':'lula','22':'flavio','95':'brancos','96':'nulos'}.items():assert total[code]==expected['resultado_oficial'][label]
assert dict(origins)==national['origens']
print(f'28 abrangências; {sections} seções; {sum(total.values())} votos. Hashes e totais entregues conferidos.')
print('Esta checagem usa as tabelas entregues; a recontagem original exige leitura dos RDVs/BU oficiais.')
