"""Soma BUs CSV do segundo turno presidencial de 2026, com fontes congeladas."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import csv
import hashlib
import io
import json
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'originais'
RAW.mkdir(exist_ok=True)
SOURCES = json.loads((ROOT / 'fontes-bu.json').read_text())
CATEGORIES = {'13': 'lula', '22': 'flavio', '95': 'brancos', '96': 'nulos'}

def download(source):
    name = source['url'].rsplit('/', 1)[1]
    path = RAW / name
    checksum_path = RAW / (name + '.sha512')
    if not checksum_path.exists():
        with urllib.request.urlopen(source['checksum_url'], timeout=60) as response:
            checksum_path.write_bytes(response.read())
    expected = checksum_path.read_text().split()[0].lower()
    assert len(expected) == 128
    if not path.exists():
        temp = path.with_suffix('.partial')
        with urllib.request.urlopen(source['url'], timeout=60) as response, temp.open('wb') as file:
            assert response.status == 200
            received = 0
            while chunk := response.read(1024 * 1024):
                received += len(chunk)
                if received > source['size_bytes']:
                    raise ValueError('Arquivo excedeu tamanho observado; interrompido.')
                file.write(chunk)
        assert received == source['size_bytes']
        temp.replace(path)
    with path.open('rb') as file:
        actual = hashlib.file_digest(file, 'sha512').hexdigest()
    assert actual == expected, f'Hash inválido: {name}'
    print('Hash conferido:', source['uf'], path.stat().st_size, flush=True)
    return dict(source, sha512=actual, bytes=path.stat().st_size)

def parse(source):
    name = source['url'].rsplit('/', 1)[1]
    with zipfile.ZipFile(RAW / name) as archive:
        csv_names = [n for n in archive.namelist() if n.lower().endswith('.csv')]
        assert len(csv_names) == 1
        member = csv_names[0]
        with archive.open(member) as file:
            sample = file.read(65536)
        try:
            sample.decode('utf-8-sig')
            encoding = 'utf-8-sig'
        except UnicodeDecodeError:
            encoding = 'latin1'
        # O leiaute oficial especifica Latin 1; BOM UTF8 ou amostra UTF8 são reconhecidos.
        sections = {}
        zero_sections = {}
        seen = set()
        generations = set()
        types = Counter()
        names = set()
        total_rows = 0
        with archive.open(member) as file:
            reader = csv.DictReader(io.TextIOWrapper(file, encoding=encoding), delimiter=';')
            assert {'CD_CARGO_PERGUNTA', 'NR_TURNO', 'CD_ELEICAO', 'QT_VOTOS', 'SG_UF'} <= set(reader.fieldnames)
            for row in reader:
                total_rows += 1
                if row['CD_CARGO_PERGUNTA'] != '1':
                    if row['CD_CARGO_PERGUNTA'] == '-1' and row['CD_ELEICAO'] == '6258':
                        assert row['NR_TURNO'] == '2' and row['CD_PLEITO'] == '3221'
                        assert row['QT_VOTOS'] == '0' and row['QT_COMPARECIMENTO'] == '0'
                        assert row['DS_TIPO_URNA'] == 'Apurada' and row['NR_VOTAVEL'] == '-1'
                        zero_key = (row['SG_UF'], row['CD_MUNICIPIO'], row['NR_ZONA'], row['NR_SECAO'])
                        assert zero_key not in zero_sections
                        zero_sections[zero_key] = row
                    continue
                assert row['NR_TURNO'] == '2' and row['CD_ELEICAO'] == '6258' and row['CD_PLEITO'] == '3221'
                assert row['SG_UF'] == source['uf'] and row['ANO_ELEICAO'] == '2026'
                code = row['NR_VOTAVEL']
                if code not in CATEGORIES:
                    raise ValueError(f'Categoria presidencial inesperada: {code}')
                key = (row['SG_UF'], row['CD_MUNICIPIO'], row['NR_ZONA'], row['NR_SECAO'])
                row_key = key + (code,)
                assert row_key not in seen, f'Duplicata de seção/categoria: {row_key}'
                seen.add(row_key)
                identity = (row['NR_URNA_EFETIVADA'], row['QT_COMPARECIMENTO'], row['DS_TIPO_URNA'], row['DT_EMISSAO_BU'])
                section = sections.setdefault(key, dict(identity=identity, totals=Counter()))
                assert section['identity'] == identity, f'Metadados conflitantes na seção: {key}'
                votes = int(row['QT_VOTOS'])
                assert votes >= 0
                section['totals'][CATEGORIES[code]] += votes
                types[row['DS_TIPO_URNA']] += 1
                generations.add((row['DT_GERACAO'], row['HH_GERACAO']))
                names.add((code, row['NM_VOTAVEL']))
        assert not (set(zero_sections) & set(sections))
        totals = Counter()
        differences = []
        for key, section in sections.items():
            totals.update(section['totals'])
            count = sum(section['totals'].values())
            if count != int(section['identity'][1]):
                differences.append(dict(secao=key, soma=count, comparecimento=section['identity'][1]))
        assert not differences, differences[:10]
        if source['uf'] == 'AC':
            assert dict(sections[('AC', '1007', '9', '1')]['totals']) == dict(lula=68, flavio=149, brancos=2, nulos=13)
        return dict(uf=source['uf'], secoes=len(sections) + len(zero_sections), secoes_com_linhas_presidenciais=len(sections), secoes_sem_comparecimento=list(zero_sections.values()), registros_presidenciais=len(seen), linhas_csv=total_rows, encoding=encoding, geracoes=sorted(generations), tipos_urna=dict(types), nomes=sorted(names), **{k: totals[k] for k in CATEGORIES.values()}, total=sum(totals.values()), inconsistencias_comparecimento=len(differences))

assert len(SOURCES) == 28 and {'DF', 'ZZ'} <= {s['uf'] for s in SOURCES}
manifest = list(ThreadPoolExecutor(max_workers=4).map(download, SOURCES))
(ROOT / 'manifesto-downloads.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
results = []
for source in SOURCES:
    result = parse(source)
    results.append(result)
    print('Totalizado:', result['uf'], result['secoes'], result['total'], flush=True)

fields = ['uf', 'secoes', 'secoes_com_linhas_presidenciais', 'registros_presidenciais', 'lula', 'flavio', 'brancos', 'nulos', 'total']
with (ROOT / 'totais-por-uf.csv').open('w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(results)
national = {key: sum(r[key] for r in results) for key in fields if key != 'uf'}
official = json.loads((ROOT / 'resultado-oficial-br.json').read_text())
assert official['ele'] == '6258' and official['t'] == '2' and official['f'] == 'o' and official['tf'] == 's'
candidates = {c['n']: int(c['vap']) for office in official['carg'] for group in office['agr'] for party in group['par'] for c in party['cand']}
expected = dict(lula=candidates['13'], flavio=candidates['22'], brancos=int(official['v']['vb']), nulos=int(official['v']['tvn']), total=int(official['v']['tv']))
differences = {key: national[key] - expected[key] for key in expected}
assert all(value == 0 for value in differences.values()), differences
assert national['secoes'] == int(official['s']['sa'])
summary = dict(ano=2026, turno=2, eleicao=6258, cargo='Presidente', abrangencias=28, inclui_df=True, inclui_exterior_zz=True, nacional_bu=national, resultado_oficial=expected, diferencas= differences, snapshot_bu=sorted({tuple(g) for r in results for g in r['geracoes']}), snapshot_resultado=dict(data=official['dg'], hora=official['hg'], idg=official['idg'], final=official['tf']), secoes_resultado=official['s'], bytes_zip=sum(s['bytes'] for s in manifest), hashes_sha512_conferidos=len(manifest), duplicatas_secao_categoria=0, inconsistencias_comparecimento=sum(r['inconsistencias_comparecimento'] for r in results), por_uf=results, limite='Comparação aritmética de BUs CSV publicados com totalização publicada. RDVs nacionais e assinaturas criptográficas não foram verificados. Snapshots de extração diferentes são documentados; igualdade dos totais não certifica todo o processo eleitoral.')
(ROOT / 'resultado-nacional.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2))
print(json.dumps(dict(nacional=national, oficial=expected, diferencas=differences), ensure_ascii=False, indent=2))
