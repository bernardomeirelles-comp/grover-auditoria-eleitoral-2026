"""Recontagem da amostra pública de 2026, segundo ASN.1/BER oficial do TSE."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import asn1tools

ROOT = Path(__file__).resolve().parent
STEM = 'o03221ac0100700090001'
rdv_codec = asn1tools.compile_files(str(ROOT / 'spec/rdv.asn1'), codec='ber')
bu_codec = asn1tools.compile_files(str(ROOT / 'spec/bu.asn1'), codec='ber')
rdv = rdv_codec.decode('EntidadeResultadoRDV', (ROOT / (STEM + '-rdv.dat')).read_bytes())['rdv']
envelope = bu_codec.decode('EntidadeEnvelopeGenerico', (ROOT / (STEM + '-bu.dat')).read_bytes())
bu = bu_codec.decode('EntidadeBoletimUrna', envelope['conteudo'])
assert rdv['fase'] == bu['fase'] == 'oficial'
assert rdv['pleito'] == bu['cabecalho']['idEleitoral'][1] == 3221
for field in ('municipioZona', 'secao'):
    assert rdv['identificacao'][field] == bu['identificacaoSecao'][field]

rdv_counts = {}
for election in rdv['eleicoes'][1]:
    for office in election['votosCargos']:
        counts = Counter()
        for vote in office['votos']:
            kind = vote['tipoVoto']
            if kind == 'nuloPorRepeticao':
                kind = 'nulo'
            assert kind in ('nominal', 'legenda', 'branco', 'nulo'), kind
            code = int(vote['digitacao'][:2] if kind == 'legenda' else vote['digitacao']) if kind in ('nominal', 'legenda') else ''
            counts[(kind, code)] += 1
        rdv_counts[(election['idEleicao'], office['idCargo'][1])] = counts

rows = []
for election in bu['resultadosVotacaoPorEleicao']:
    for result in election['resultadosVotacao']:
        for office in result['totaisVotosCargo']:
            key = (election['idEleicao'], office['codigoCargo'][1])
            counts = Counter()
            for vote in office['votosVotaveis']:
                code = vote.get('identificacaoVotavel', {}).get('codigo', '')
                counts[(vote['tipoVoto'], code)] += vote['quantidadeVotos']
            assert counts == rdv_counts[key], (key, counts - rdv_counts[key], rdv_counts[key] - counts)
            for (kind, code), total in sorted(counts.items(), key=lambda x: (x[0][0], str(x[0][1]))):
                rows.append(dict(eleicao=key[0], cargo=key[1], tipo=kind, codigo=code, votos_rdv=rdv_counts[key][(kind, code)], votos_bu=total))

with (ROOT / 'comparacao-completa-2026.csv').open('w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=rows[0])
    writer.writeheader()
    writer.writerows(rows)
selected = []
for kind, code, label in [('nominal', 13, 'Lula'), ('nominal', 22, 'Flávio Bolsonaro'), ('branco', '', 'Brancos'), ('nulo', '', 'Nulos')]:
    row = next(r for r in rows if r['eleicao'] == 6258 and r['cargo'] == 'presidente' and r['tipo'] == kind and r['codigo'] == code)
    selected.append(dict(indice=len(selected), categoria=label, **row))
assert len(selected) == 4
assert sum(r['votos_bu'] for r in selected) == bu['qtdEleitoresCompareceram'] == 232
with (ROOT / 'comparacao-presidencia-2026-2t.csv').open('w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=selected[0])
    writer.writeheader()
    writer.writerows(selected)
out = dict(data_consulta='2026-11-06 America/Sao_Paulo', uf='AC', municipio='Bujari', municipio_codigo_tse=1007, zona=9, secao=1, pleito=3221, turno=2, data_votacao='2026-10-25', eleicao=6258, cargo='presidente', comparecimento=bu['qtdEleitoresCompareceram'], selecao='Mesma seção de Bujari usada na pesquisa inicial; todas as quatro categorias presidenciais do segundo turno, sem seleção por contagens pequenas.', registros=selected, grupos_comparados=len(rdv_counts), categorias_comparadas=len(rows), divergencias=0, escopo='Consistência RDV-BU desta seção. Não é conclusão sobre integridade da eleição inteira.', fonte_arquivos='https://dadosabertos.tse.jus.br/dataset/resultados-2026-arquivos-transmitidos-para-totalizacao', fonte_identidade='https://www.tse.jus.br/eleicoes/eleicoes-2026-content/propostas-de-governo-dos-candidatos-ao-cargo-de-presidente-da-republica-eleicoes-2026/planos-de-governo-dos-candidatos-ao-cargo-de-presidente-da-republica-eleicoes-2026', arquivos={name: dict(bytes=(ROOT/name).stat().st_size, sha256=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()) for name in (STEM+'-bu.dat', STEM+'-rdv.dat', STEM+'-log.jez', STEM+'-vota.vsc')})
(ROOT / 'amostra-presidencia-2026-2t.json').write_text(json.dumps(out, ensure_ascii=False, indent=2))
print(json.dumps(out, ensure_ascii=False, indent=2))
