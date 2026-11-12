"""Compara alterações adicionais sem acessar a IBM nem regravar a análise principal."""
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from qiskit import transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

import reavaliar as review

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'revisao'
DELTAS = (-10, -2, 1, 10, 100)
VARIANTS = ('original', 'gray_cancelado')
NOISE = .003


def run():
    left = [row['rdv'] for row in review.original.read_data()['records']]
    cases, skipped, circuits = [], [], []
    for target in range(4):
        for delta in DELTAS:
            right = left.copy()
            right[target] += delta
            if right[target] < 0:
                skipped.append({'target': target, 'delta': delta, 'reason': 'negative_count'})
                continue
            for variant in VARIANTS:
                circuit = transpile(review.search(left, right, variant),
                    basis_gates=['u', 'cx'], optimization_level=3, seed_transpiler=review.SEED)
                ideal = Statevector.from_instruction(circuit).probabilities([0, 1])
                assert np.isclose(ideal[target], 1), (target, delta, variant, ideal)
                cases.append({'target': target, 'delta': delta, 'before': left[target],
                    'after': right[target], 'variant': variant, 'cx': int(circuit.count_ops().get('cx', 0)),
                    'depth': circuit.depth(), 'ideal_p': float(ideal[target])})
                circuit.save_probabilities([0, 1])
                circuits.append(circuit)
    noise = NoiseModel()
    noise.add_all_qubit_quantum_error(depolarizing_error(NOISE, 2), ['cx'])
    noise.add_all_qubit_quantum_error(depolarizing_error(NOISE / 10, 1), ['u'])
    result = AerSimulator(method='density_matrix', noise_model=noise,
        max_parallel_threads=2).run(circuits).result()
    for index, case in enumerate(cases):
        probabilities = np.asarray(result.data(index)['probabilities'])
        assert np.isclose(probabilities.sum(), 1)
        case['noise'] = NOISE
        case['p'] = float(probabilities[case['target']])
    comparisons = []
    for index in range(0, len(cases), 2):
        original, changed = cases[index:index + 2]
        assert (original['target'], original['delta']) == (changed['target'], changed['delta'])
        difference = changed['p'] - original['p']
        comparisons.append({'target': original['target'], 'delta': original['delta'],
            'original_p': original['p'], 'gray_cancelado_p': changed['p'],
            'difference': difference,
            'outcome': 'equal' if abs(difference) <= 1e-10 else 'better' if difference > 0 else 'worse'})
    assert len(comparisons) + len(skipped) == len(left) * len(DELTAS)
    OUT.mkdir(exist_ok=True)
    with (OUT / 'variacoes.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(cases[0]))
        writer.writeheader()
        writer.writerows(cases)
    summary = {
        'executed_utc': datetime.now(timezone.utc).isoformat(),
        'analysis': 'additional_exploratory_cases_after_primary_local_analysis',
        'noise': NOISE, 'deltas': DELTAS, 'variants': VARIANTS,
        'basis_gates': ['u', 'cx'], 'optimization_level': 3, 'seed_transpiler': review.SEED,
        'simulation': 'density_matrix_probabilities_without_shot_sampling',
        'cases': len(comparisons), 'circuits': len(cases), 'skipped': skipped,
        'outcomes': {name: sum(c['outcome'] == name for c in comparisons) for name in ('better', 'equal', 'worse')},
        'comparisons': comparisons,
        'source_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                          for name in ('testar-variacoes.py', 'reavaliar.py', 'experimento.py', 'dados/entrada.json', 'revisao/protocolo.json')},
        'result_sha256': hashlib.sha256((OUT / 'variacoes.csv').read_bytes()).hexdigest(),
    }
    (OUT / 'variacoes.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    run()
