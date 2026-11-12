"""Revisão local: validação dos oráculos e comparação de implementações.

Não acessa a IBM. Os resultados de novembro de 6 permanecem em dados/;
esta análise escreve somente em revisao/ e figuras/revisao-ruido.pdf.
"""
import csv
import itertools
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, qasm3, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

import experimento as original

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'revisao'
VARIANTS = ('original', 'cancelado', 'gray_cancelado')
LEVELS = (0, .001, .002, .003, .004, .005, .01, .03, .1)
SEED = 20261111
BASELINE = 2.25
THRESHOLD = 2 / BASELINE


def encode(left, right, gray=False):
    a, b, vocabulary = original.encode(left, right)
    if gray:
        vocabulary = {value: code ^ (code >> 1) for value, code in vocabulary.items()}
        a = [vocabulary[value] for value in left]
        b = [vocabulary[value] for value in right]
    return a, b, vocabulary


def reduced_loader(left, right):
    """Cancela portas idênticas de dois carregadores, sem receber o alvo."""
    occurrences = Counter()
    for loader in (original.table_loader(left), original.table_loader(right)):
        for item in loader.data:
            qubits = tuple(loader.find_bit(q).index for q in item.qubits)
            assert item.operation.name in ('x', 'cx', 'ccx')
            assert all(q < 2 for q in qubits[:-1]) and qubits[-1] >= 2
            occurrences[item.operation.name, qubits] += 1
    circuit = QuantumCircuit(5)
    # Os controles nunca são alvos: essas portas comutam e o par cancela.
    for (name, qubits), count in occurrences.items():
        if count % 2:
            getattr(circuit, name)(*qubits)
    return circuit


def oracle(left, right, variant):
    a, b, _ = encode(left, right, gray=variant == 'gray_cancelado')
    if variant == 'original':
        return original.oracle(a, b)
    assert variant in VARIANTS
    load = reduced_loader(a, b)
    circuit = QuantumCircuit(5)
    circuit.compose(load, inplace=True)
    circuit.x([2, 3, 4])
    circuit.h(4)
    circuit.ccx(2, 3, 4)
    circuit.h(4)
    circuit.x([2, 3, 4])
    circuit.global_phase = math.pi
    circuit.compose(load.inverse(), inplace=True)
    return circuit


def search(left, right, variant, measure=False):
    circuit = QuantumCircuit(5, name=variant)
    circuit.h([0, 1])
    circuit.compose(oracle(left, right, variant), inplace=True)
    circuit.h([0, 1])
    circuit.x([0, 1])
    circuit.cz(0, 1)
    circuit.x([0, 1])
    circuit.h([0, 1])
    if measure:
        circuit.add_register(ClassicalRegister(2, 'registro'))
        circuit.measure([0, 1], [0, 1])
    return circuit


def controlled_cases():
    records = original.read_data()['records']
    left = [row['rdv'] for row in records]
    for target in range(4):
        right = left.copy()
        right[target] -= 1
        yield target, left.copy(), right


def validate():
    rng = np.random.default_rng(SEED)
    cases = []
    for mask in range(16):
        left = [68, 149, 2, 13]
        right = [value - ((mask >> i) & 1) for i, value in enumerate(left)]
        cases.append((left, right))
    cases += [([7]*4, [7]*4), ([0]*4, [1]*4), ([0,1,2,3], [4,5,6,7])]
    cases += [(rng.integers(0, 8, 4).tolist(), rng.integers(0, 8, 4).tolist()) for _ in range(40)]
    checked = 0
    for left, right in cases:
        marked = [i for i in range(4) if left[i] != right[i]]
        expected_p = math.sin(3 * math.asin(math.sqrt(len(marked)/4)))**2
        for variant in VARIANTS:
            circuit = oracle(left, right, variant)
            for index in range(4):
                actual = Statevector.from_int(index, 32).evolve(circuit).data
                expected = np.zeros(32, complex)
                expected[index] = -1 if index in marked else 1
                assert np.allclose(actual, expected, atol=1e-9), (left, right, variant, index)
                checked += 1
            state = Statevector.from_instruction(search(left, right, variant))
            assert np.isclose(sum(state.probabilities()[i] for i in marked), expected_p)
            assert np.isclose(sum(state.probabilities()[:4]), 1)
    costs = [min(order.index(1)+1, 3) for order in itertools.permutations(range(4))]
    assert np.mean(costs) == BASELINE
    assert np.isclose(THRESHOLD, 8/9)
    return {'oracle_basis_checks': checked, 'input_pairs': len(cases),
            'variants': list(VARIANTS), 'patterns_checked': 16,
            'classical_mean_promised_one': BASELINE,
            'threshold_restart_protocol': THRESHOLD,
            'ideal_success_by_m': [round(math.sin(3*math.asin(math.sqrt(m/4)))**2, 12) for m in range(5)]}


def write_csv(path, rows):
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run():
    OUT.mkdir(exist_ok=True)
    protocol = OUT / 'protocolo.json'
    if not protocol.exists():
        protocol.write_text(json.dumps({
            'registered_utc': datetime.now(timezone.utc).isoformat(),
            'status': 'exploratory_revision_after_feedback',
            'hypothesis': 'gray_cancelado improves minimum success across the four targets at lambda=.003 relative to original, with identical compilation settings',
            'primary_metric': 'minimum conditional probability over four targets at lambda=.003',
            'secondary_metrics': ['CX count', 'depth', 'noise threshold for p=8/9'],
            'variants': VARIANTS, 'noise_levels': LEVELS,
            'basis_gates': ['u', 'cx'], 'optimization_level': 3, 'seed_transpiler': SEED,
            'noise_model': 'depolarization lambda after CX and lambda/10 after U; no readout noise',
            'simulation': 'density matrix probabilities, no Monte Carlo shots or confidence intervals',
            'hardware_plan': {'variants': ['original','gray_cancelado'], 'targets': [0,1,2,3],
                              'blocks': 3, 'shots': 512, 'readout_preparations_per_block': 4,
                              'submit_only_after_validation_and_usage_estimate': True},
            'old_hardware_result': 'preserved; new calibration cannot identify its historical cause'
        }, indent=2, ensure_ascii=False))
    saved_protocol = json.loads(protocol.read_text())
    current_settings = {
        'variants': list(VARIANTS), 'noise_levels': list(LEVELS),
        'basis_gates': ['u', 'cx'], 'optimization_level': 3, 'seed_transpiler': SEED,
    }
    if any(saved_protocol.get(key) != value for key, value in current_settings.items()):
        raise ValueError('Configuração diferente do protocolo preservado; registre outra análise antes de executar.')
    validation = validate()
    (OUT/'validacao.json').write_text(json.dumps(validation, indent=2))
    print('Validação:', json.dumps(validation), flush=True)
    circuits, resources = [], []
    for target, left, right in controlled_cases():
        for variant in VARIANTS:
            circuit = transpile(search(left, right, variant), basis_gates=['u', 'cx'],
                                optimization_level=3, seed_transpiler=SEED)
            assert np.isclose(Statevector.from_instruction(circuit).probabilities([0,1])[target], 1)
            circuits.append((target, variant, circuit))
            resources.append({'variant':variant, 'target':target, 'qubits':5,
                              'cx':int(circuit.count_ops().get('cx',0)),
                              'u':int(circuit.count_ops().get('u',0)), 'depth':circuit.depth()})
            measured = circuit.copy()
            measured.add_register(ClassicalRegister(2, 'registro'))
            measured.measure([0,1], [0,1])
            (OUT/f'{variant}-{target:02b}.qasm').write_text(qasm3.dumps(measured))
    write_csv(OUT/'recursos.csv', resources)
    rows = []
    for level in LEVELS:
        noise = NoiseModel()
        if level:
            noise.add_all_qubit_quantum_error(depolarizing_error(level,2), ['cx'])
            noise.add_all_qubit_quantum_error(depolarizing_error(level/10,1), ['u'])
        simulator = AerSimulator(method='density_matrix', noise_model=noise, max_parallel_threads=2)
        runnable=[]
        for _, _, circuit in circuits:
            q=circuit.copy();q.save_probabilities([0,1]);runnable.append(q)
        result=simulator.run(runnable).result()
        for i,(target,variant,_) in enumerate(circuits):
            probs=np.asarray(result.data(i)['probabilities'])
            assert np.isclose(sum(probs),1)
            p=float(probs[target])
            rows.append({'variant':variant,'target':target,'noise':level,'p':p,
                         'oracle_calls':1/p,'classical_checks':1/p,'unit_cost':2/p,
                         **{f'p_{j:02b}':float(probs[j]) for j in range(4)}})
        print('Ruído concluído:',level,flush=True)
    write_csv(OUT/'probabilidades.csv',rows)
    summary=[]
    for level in LEVELS:
        for variant in VARIANTS:
            values=[r['p'] for r in rows if r['noise']==level and r['variant']==variant]
            summary.append({'variant':variant,'noise':level,'p_min':min(values),'p_mean':float(np.mean(values)),
                            'p_max':max(values),'mean_unit_cost':float(np.mean([2/p for p in values]))})
    write_csv(OUT/'resumo.csv',summary)
    primary={v:min(r['p'] for r in rows if r['variant']==v and r['noise']==.003) for v in VARIANTS}
    (OUT/'conclusao-local.json').write_text(json.dumps({'primary_metric':primary,
        'hypothesis_supported_in_this_model':primary['gray_cancelado']>primary['original'],
        'not_hardware_calibrated':True,'not_end_to_end_advantage':True},indent=2))
    plot(summary)


def plot(summary):
    plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','STIXGeneral'],
                         'mathtext.fontset':'stix','font.size':10,'pdf.fonttype':42,
                         'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(6.7,3.15),layout='constrained')
    labels={'original':'Original','cancelado':'Cancelamento','gray_cancelado':'Gray + cancelamento'}
    for variant,color,marker in zip(VARIANTS,['#555555','#9b6c32','#174b70'],['o','s','^']):
        series=[r for r in summary if r['variant']==variant and r['noise']>0]
        ax.plot([r['noise'] for r in series],[100*r['p_min'] for r in series],marker=marker,
                markersize=4,color=color,label=labels[variant],linewidth=1.3)
    ax.axhline(100*THRESHOLD,color='#333333',linestyle='--',linewidth=.8,label='Equilíbrio: 88,89%')
    ax.set_xscale('log');ax.set_ylim(20,103)
    ax.set_xlabel('Parâmetro de despolarização por CX')
    ax.set_ylabel('Menor acerto entre quatro posições (%)')
    ax.legend(loc='upper center',bbox_to_anchor=(.5,1.20),ncol=2,frameon=False,fontsize=9)
    fig.savefig(ROOT/'figuras/revisao-ruido.pdf')
    plt.close(fig)


if __name__ == '__main__':
    run()
