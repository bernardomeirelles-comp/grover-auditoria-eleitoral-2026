"""Confere os totais CSV com os JSONs finais de cada UF; preserva snapshots."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'resultados-oficiais-uf'
OUTPUT.mkdir(exist_ok=True)
SUMMARY = json.loads((ROOT / 'resultado-nacional.json').read_text())

def compare(row):
    uf = row['uf'].lower()
    url = f'https://resultados.tse.jus.br/oficial/ele2026/6258/dados/{uf}/{uf}-c0001-e006258-u.json'
    path = OUTPUT / f'{uf}.json'
    if not path.exists():
        with urllib.request.urlopen(url, timeout=30) as response:
            path.write_bytes(response.read())
    data = json.loads(path.read_text())
    assert data['ele'] == '6258' and data['t'] == '2' and data['f'] == 'o'
    candidates = {c['n']: int(c['vap']) for office in data['carg'] for group in office['agr'] for party in group['par'] for c in party['cand']}
    official = dict(lula=candidates['13'], flavio=candidates['22'], brancos=int(data['v']['vb']), nulos=int(data['v']['tvn']), total=int(data['v']['tv']))
    differences = {k: row[k] - v for k, v in official.items()}
    assert all(v == 0 for v in differences.values()), (uf, differences)
    return dict(uf=row['uf'], url=url, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), data=data['dg'], hora=data['hg'], idg=data['idg'], and_=data['and'], oficial=official, diferencas=differences, secoes_csv=row['secoes'], secoes_oficiais=data['s'], diferenca_secoes=row['secoes']-int(data['s']['sa']))

results = list(ThreadPoolExecutor(max_workers=4).map(compare, SUMMARY['por_uf']))
(ROOT / 'comparacao-resultados-uf.json').write_text(json.dumps(results, ensure_ascii=False, indent=2))
print('28 UFs: totais de candidatos, brancos e nulos coincidentes.')
print('Diferenças na contagem de seções:', [(r['uf'], r['diferenca_secoes']) for r in results if r['diferenca_secoes']])
