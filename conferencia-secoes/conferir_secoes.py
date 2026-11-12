"""Compara por seção/categoria duas publicações oficiais; não detecta toda fraude."""
from collections import Counter
from pathlib import Path
import csv
import hashlib
import io
import json
import zipfile

ROOT = Path(__file__).resolve().parent
BU_ROOT = ROOT.parent / 'nacional'
URL = 'https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_2026_BR.zip'
FIELDS = ['SG_UF', 'CD_MUNICIPIO', 'NR_ZONA', 'NR_SECAO', 'NR_VOTAVEL']

def key(row):
    return (row['SG_UF'], *(int(row[k]) for k in FIELDS[1:]))

def read(path, cargo):
    values = {}
    sections = set()
    zero_sections = set()
    snapshots = set()
    duplicates = []
    codes = Counter()
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if n.lower().endswith('.csv')]
        assert len(names) == 1, names
        with z.open(names[0]) as f:
            sample = f.read(65536)
        try:
            sample.decode('utf-8-sig')
            encoding = 'utf-8-sig'
        except UnicodeDecodeError:
            encoding = 'latin1'
        with z.open(names[0]) as f:
            rows = csv.DictReader(io.TextIOWrapper(f, encoding=encoding), delimiter=';')
            assert set(FIELDS + [cargo, 'QT_VOTOS', 'NR_TURNO', 'CD_ELEICAO']) <= set(rows.fieldnames)
            for row in rows:
                if row['NR_TURNO'] != '2' or row['CD_ELEICAO'] != '6258':
                    continue
                assert row['ANO_ELEICAO'] == '2026'
                if row[cargo] == '-1' and cargo == 'CD_CARGO_PERGUNTA':
                    assert int(row['QT_VOTOS']) == int(row['QT_COMPARECIMENTO']) == 0
                    zero_sections.add(key(row)[:4])
                    continue
                if row[cargo] != '1':
                    continue
                k = key(row)
                votes = int(row['QT_VOTOS'])
                assert votes >= 0
                if k in values:
                    duplicates.append(list(k))
                values[k] = votes
                sections.add(k[:4])
                snapshots.add((row['DT_GERACAO'], row['HH_GERACAO']))
                codes[k[-1]] += votes
    return values, sections, zero_sections, snapshots, duplicates, codes

# A identidade inclui a seção, impedindo que diferenças compensatórias desapareçam na soma.
assert key(dict(SG_UF='AC',CD_MUNICIPIO='01007',NR_ZONA='009',NR_SECAO='0001',NR_VOTAVEL='13')) == ('AC',1007,9,1,13)
a, sa, za, ga, da, ca = {}, set(), set(), set(), [], Counter()
for source in json.loads((BU_ROOT / 'fontes-bu.json').read_text()):
    path = BU_ROOT / 'originais' / source['url'].rsplit('/',1)[1]
    values, sections, zeros, generations, duplicates, codes = read(path, 'CD_CARGO_PERGUNTA')
    assert not (set(a) & set(values)), source['uf']
    a.update(values); sa.update(sections); za.update(zeros); ga.update(generations); da.extend(duplicates); ca.update(codes)
    print('BU:',source['uf'],len(sections),flush=True)
p = ROOT / 'votacao_secao_2026_BR.zip'
b, sb, zb, gb, db, cb = read(p, 'CD_CARGO')
assert not da and not db, 'Duplicatas encontradas; conferir antes da comparação.'
common = sa & sb
missing_a = sorted(sb - sa)
missing_b = sorted(sa - sb)
differences = []
omitted_zero_a = omitted_zero_b = 0
for k in sorted(set(a) | set(b)):
    if k[:4] not in common:
        continue
    av, bv = a.get(k,0), b.get(k,0)
    if av != bv:
        differences.append(dict(zip(FIELDS,k), votos_bu=av, votos_totalizacao=bv, diferenca=av-bv))
    elif k not in a: omitted_zero_a += 1
    elif k not in b: omitted_zero_b += 1
with (ROOT/'divergencias-secoes.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=FIELDS+['votos_bu','votos_totalizacao','diferenca']); w.writeheader();w.writerows(differences)
with p.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
out=dict(eleicao=6258,turno=2,cargo='presidente',url=URL,bytes=p.stat().st_size,sha256=digest,
    registros_bu=len(a),registros_totalizacao=len(b),secoes_bu=len(sa),secoes_totalizacao=len(sb),secoes_comuns=len(common),
    secoes_bu_zero_comparecimento=sorted(za),secoes_so_bu=missing_b,secoes_so_totalizacao=missing_a,
    categorias_bu=dict(ca),categorias_totalizacao=dict(cb),geracao_bu=sorted(ga),geracao_totalizacao=sorted(gb),
    duplicatas_bu=len(da),duplicatas_totalizacao=len(db),divergencias=len(differences),
    categorias_zero_omitidas_bu=omitted_zero_a,categorias_zero_omitidas_totalizacao=omitted_zero_b,
    criterio='Chave UF/município/zona/seção/categoria; categoria ausente equivale a zero somente em seção presente em ambas as fontes. Seções ausentes são registradas separadamente.',
    limite='Consistência entre duas publicações oficiais; não compara boletins físicos nem votos digitados, não valida assinatura digital e não certifica ausência de fraude.')
(ROOT/'resultado-conferencia-secoes.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out,ensure_ascii=False,indent=2))
