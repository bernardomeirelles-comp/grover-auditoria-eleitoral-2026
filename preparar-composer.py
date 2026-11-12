"""Prepara três blocos para o Composer; nunca envia trabalhos à IBM."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, qasm3, transpile
from qiskit_aer import AerSimulator

from reavaliar import controlled_cases, search, SEED

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'revisao' / 'composer'
OUT.mkdir(exist_ok=True)
experiments = []
for target, left, right in controlled_cases():
    for variant in ('original', 'gray_cancelado'):
        circuit = transpile(search(left, right, variant), basis_gates=['u', 'cx'],
                            optimization_level=3, seed_transpiler=SEED)
        experiments.append((f'{variant}_{target:02b}', target, circuit))
for target in range(4):
    circuit = QuantumCircuit(5)
    for bit in range(2):
        if target & (1 << bit):
            circuit.x(bit)
    experiments.append((f'controle_{target:02b}', target, circuit))

manifest = {'created_utc': datetime.now(timezone.utc).isoformat(), 'shots_per_block': 512,
            'blocks': [], 'backend_requested': 'ibm_marrakesh',
            'design': '12 sequential segments per shot, reset before each, three randomized orders',
            'limitations': ['controls include preparation, reset and readout',
                            'barriers do not fix physical layout; inspect exported compilation',
                            'within-shot segments are not independent circuits'],
            'code_sha256': {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                            for name in ['reavaliar.py', 'experimento.py', 'preparar-composer.py']}}
rng = np.random.default_rng(SEED)
for block in range(3):
    order = rng.permutation(len(experiments)).tolist()
    circuit = QuantumCircuit(5)
    segments = []
    for position, index in enumerate(order):
        label, target, segment = experiments[index]
        register = ClassicalRegister(2, f'r{position:02d}')
        circuit.add_register(register)
        circuit.reset(range(5))
        circuit.barrier()
        circuit.compose(segment, inplace=True)
        circuit.measure([0, 1], register)
        circuit.barrier()
        segments.append({'register': register.name, 'experiment': label, 'target': target,
                         'cx': int(segment.count_ops().get('cx', 0)), 'depth': segment.depth()})
    source = qasm3.dumps(circuit)
    imported = qasm3.loads(source)
    # Validate the actual upload file, including mid-circuit reset and register order.
    counts = AerSimulator().run(imported, shots=32, seed_simulator=SEED).result().get_counts()
    expected = ' '.join(f'{s["target"]:02b}' for s in reversed(segments))
    assert counts == {expected: 32}, (counts, expected)
    path = OUT / f'bloco-{block+1}.qasm'
    path.write_text(source)
    manifest['blocks'].append({'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                              'segments': segments, 'ideal_expected': expected,
                              'ideal_validation_shots': 32, 'operations': dict(circuit.count_ops()),
                              'depth': circuit.depth()})
(OUT/'protocolo.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
print(json.dumps({b['file']: b['operations'] for b in manifest['blocks']}, indent=2))
