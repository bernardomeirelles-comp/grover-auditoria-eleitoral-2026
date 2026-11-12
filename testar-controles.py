"""Controles negativos no comparador real RDV/BU, sem alterar os originais."""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'recontagem-nacional'))
from benchmark_rdv import BC, RC, compare

source = ROOT / 'fontes-tse'
rdv = (source / 'o03221ac0100700090001-rdv.dat').read_bytes()
bu = (source / 'o03221ac0100700090001-bu.dat').read_bytes()
assert compare(rdv, bu)['comparecimento'] == 232
envelope = BC.decode('EntidadeEnvelopeGenerico', bu)
original = BC.decode('EntidadeBoletimUrna', envelope['conteudo'])


def encode_bu(value):
    changed = copy.deepcopy(envelope)
    changed['conteudo'] = BC.encode('EntidadeBoletimUrna', value)
    return BC.encode('EntidadeEnvelopeGenerico', changed)


def office(value):
    for election in value['resultadosVotacaoPorEleicao']:
        if election['idEleicao'] == 6258:
            for group in election['resultadosVotacao']:
                for cargo in group['totaisVotosCargo']:
                    if cargo['codigoCargo'][1] == 'presidente':
                        return cargo
    raise AssertionError('Cargo ausente no controle')


cases = []
value = copy.deepcopy(original)
office(value)['votosVotaveis'][0]['quantidadeVotos'] += 1
cases.append(('um_voto_a_mais', value))
value = copy.deepcopy(original)
votes = office(value)['votosVotaveis']
positive = [v for v in votes if v['quantidadeVotos'] > 0]
positive[0]['quantidadeVotos'] -= 1
positive[1]['quantidadeVotos'] += 1
cases.append(('troca_de_categoria_preservando_total', value))
value = copy.deepcopy(original)
value['identificacaoSecao']['secao'] += 1
cases.append(('identificacao_de_secao_incorreta', value))
value = copy.deepcopy(original)
office(value)['codigoCargo'] = ('cargoConstitucional', 'governador')
cases.append(('cargo_presidencial_ausente', value))

results = []
for name, value in cases:
    try:
        compare(rdv, encode_bu(value))
    except AssertionError:
        results.append({'control': name, 'rejected': True})
    else:
        raise AssertionError(f'Controle aceito incorretamente: {name}')
assert compare(rdv, bu)['comparecimento'] == 232
(ROOT / 'revisao').mkdir(exist_ok=True)
(ROOT / 'revisao/controles-classicos.json').write_text(json.dumps(results, indent=2))
print(json.dumps(results, indent=2))
