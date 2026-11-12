"""Busca de uma divergência entre quatro pares de contagens eleitorais.

O circuito codifica as contagens sem perda de igualdade e compara os códigos. Não recebe uma lista
de posições divergentes. Os arquivos oficiais permanecem separados da cópia
alterada exclusivamente para teste.
"""
import csv
import itertools
import json
import math
import platform
import time
from importlib.metadata import version
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, qasm3, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

ROOT = Path(__file__).resolve().parent
LEVELS = [0, 0.001, 0.003, 0.005, 0.01, 0.03, 0.1]
SEEDS = [20261107, 20261108, 20261109]
SHOTS = 4096


def read_data():
    data = json.loads((ROOT / "dados/entrada.json").read_text())
    records = data["records"]
    if len(records) != 4:
        raise ValueError("Este experimento exige quatro registros.")
    for row in records:
        for key in ("rdv", "bu", "bu_test"):
            if type(row[key]) is not int or row[key] < 0:
                raise ValueError("As contagens devem ser inteiros não negativos.")
        if row["rdv"] != row["bu"]:
            raise ValueError("A amostra original deve ter sido conferida.")
    if sum(r["rdv"] != r["bu_test"] for r in records) != 1:
        raise ValueError("A cópia de teste precisa ter uma divergência.")
    if sum(abs(r["bu_test"] - r["bu"]) for r in records) != 1:
        raise ValueError("A alteração deve ser de um voto.")
    left, right, codes = encode([r["rdv"] for r in records], [r["bu_test"] for r in records])
    if {str(k): v for k,v in codes.items()} != data["encoding"]:
        raise ValueError("Dicionário de códigos inconsistente.")
    return data


def encode(left, right):
    if len(left) != 4 or len(right) != 4:
        raise ValueError("São necessários quatro totais em cada tabela.")
    if any(type(v) is not int or v < 0 for v in [*left, *right]):
        raise ValueError("Os totais devem ser inteiros não negativos.")
    vocabulary = sorted(set(left) | set(right))
    if len(vocabulary) > 8:
        raise ValueError("O registrador de três qubits admite oito códigos.")
    codes = {value: code for code, value in enumerate(vocabulary)}
    return [codes[v] for v in left], [codes[v] for v in right], codes


def table_loader(values):
    if len(values) != 4 or any(type(v) is not int or not 0 <= v < 8 for v in values):
        raise ValueError("O carregador exige quatro códigos de três bits.")
    qc = QuantumCircuit(5, name="Carregar codigos por XOR")
    for bit in range(3):
        f = [(value >> bit) & 1 for value in values]
        if f[0]:
            qc.x(2 + bit)
        if f[0] ^ f[1]:
            qc.cx(0, 2 + bit)
        if f[0] ^ f[2]:
            qc.cx(1, 2 + bit)
        if f[0] ^ f[1] ^ f[2] ^ f[3]:
            qc.ccx(0, 1, 2 + bit)
    return qc


def oracle(left, right):
    qc = QuantumCircuit(5, name="Comparar codigos")
    load_left, load_right = table_loader(left), table_loader(right)
    qc.compose(load_left, inplace=True)
    qc.compose(load_right, inplace=True)
    # O XOR é zero exatamente quando os códigos coincidem.
    qc.x([2, 3, 4])
    qc.h(4)
    qc.ccx(2, 3, 4)
    qc.h(4)
    qc.x([2, 3, 4])
    qc.global_phase = math.pi  # Inverte a convenção para marcar os não zeros.
    qc.compose(load_right.inverse(), inplace=True)
    qc.compose(load_left.inverse(), inplace=True)
    return qc


def search_circuit(left, right, measure=True):
    qc = QuantumCircuit(5)
    qc.h([0, 1])
    qc.compose(oracle(left, right), inplace=True)
    qc.h([0, 1])
    qc.x([0, 1])
    qc.cz(0, 1)
    qc.x([0, 1])
    qc.h([0, 1])
    if measure:
        qc.add_register(ClassicalRegister(2, "registro"))
        qc.measure([0, 1], [0, 1])
    return qc


def check_oracle(left, right):
    mark = oracle(left, right)
    for index in range(4):
        state = Statevector.from_int(index, 32).evolve(mark)
        expected = np.zeros(32, complex)
        expected[index] = -1 if left[index] != right[index] else 1
        assert np.allclose(state.data, expected, atol=1e-10)


def self_check(left, right):
    for a, b in itertools.product(range(5), repeat=2):
        check_oracle([a] * 4, [b] * 4)
    for values in itertools.product(range(5), repeat=4):
        load = table_loader(values)
        for index in range(4):
            state = Statevector.from_int(index, 32).evolve(load)
            assert np.isclose(abs(state.data[index + (values[index] << 2)]), 1)
    check_oracle(left, right)
    check_oracle(left, left)
    marked = [i for i in range(4) if left[i] != right[i]]
    assert len(marked) == 1
    ideal = Statevector.from_instruction(search_circuit(left, right, measure=False))
    assert np.isclose(ideal.probabilities()[marked[0]], 1)
    control = Statevector.from_instruction(search_circuit(left, left, measure=False))
    assert np.allclose(control.probabilities()[:4], [0.25] * 4)
    orders = list(itertools.permutations(range(4)))
    costs = [min(order.index(marked[0]) + 1, 3) for order in orders]
    assert np.mean(costs) == 2.25
    return marked[0], costs


def wilson(success, total):
    z = 1.959963984540054
    p = success / total
    denominator = 1 + z*z/total
    center = (p + z*z/(2*total)) / denominator
    half = z * math.sqrt(p*(1-p)/total + z*z/(4*total*total)) / denominator
    return max(0, center-half), min(1, center+half)


def write_csv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def is_different(index, left, right):
    return left[index] != right[index]


def run():
    start = time.perf_counter()
    data = read_data()
    left, right, codes = encode([r["rdv"] for r in data["records"]],
                                [r["bu_test"] for r in data["records"]])
    original_bu = [codes[r["bu"]] for r in data["records"]]
    marked, classical_costs = self_check(left, right)
    circuit = transpile(search_circuit(left, right), basis_gates=["u", "cx"],
                        optimization_level=1, seed_transpiler=SEEDS[0])
    control = transpile(search_circuit(left, original_bu), basis_gates=["u", "cx"],
                        optimization_level=1, seed_transpiler=SEEDS[0])
    (ROOT / "circuito.qasm").write_text(qasm3.dumps(circuit))
    (ROOT / "circuito.txt").write_text(str(circuit.draw(output="text", fold=100)))
    rows, raw, checks = [], [], []
    for level in LEVELS:
        noise = NoiseModel()
        if level:
            noise.add_all_qubit_quantum_error(depolarizing_error(level / 10, 1), ["u"])
            noise.add_all_qubit_quantum_error(depolarizing_error(level, 2), ["cx"])
        sim = AerSimulator(method="density_matrix", noise_model=noise,
                           max_parallel_threads=2)
        counts_all = dict.fromkeys(range(4), 0)
        for seed in SEEDS:
            counts = sim.run(circuit, shots=SHOTS, seed_simulator=seed).result().get_counts()
            assert sum(counts.values()) == SHOTS
            for bits, count in counts.items():
                index = int(bits, 2)
                counts_all[index] += count
                raw.append(dict(noise=level, seed=seed, index=index, count=count))
        total = SHOTS * len(SEEDS)
        success = sum(count for index, count in counts_all.items()
                      if is_different(index, left, right))
        lo, hi = wilson(success, total)
        p = success / total
        rows.append(dict(noise=level, shots=total, success=success, p=p,
                         p_low=lo, p_high=hi, queries=2/p, q_low=2/hi, q_high=2/lo))
        # Sem divergência, toda saída precisa ser rejeitada pela verificação final.
        control_counts = sim.run(control, shots=SHOTS, seed_simulator=SEEDS[0]).result().get_counts()
        accepted = sum(n for bits, n in control_counts.items()
                       if is_different(int(bits, 2), left, original_bu))
        assert accepted == 0
        checks.append(dict(noise=level, shots=SHOTS, accepted=accepted,
                           counts=json.dumps(control_counts, sort_keys=True)))
        print(json.dumps(rows[-1]), flush=True)
    write_csv(ROOT / "dados/resultados.csv", rows)
    write_csv(ROOT / "dados/contagens.csv", raw)
    write_csv(ROOT / "dados/controle.csv", checks)
    write_csv(ROOT / "dados/classico.csv",
              [dict(order=" ".join(map(str, order)), queries=cost)
               for order, cost in zip(itertools.permutations(range(4)), classical_costs)])
    metadata = dict(execution="simulação local", python=platform.python_version(),
                    packages={p: version(p) for p in ["qiskit", "qiskit-aer", "numpy", "matplotlib"]},
                    seeds=SEEDS, shots_per_seed=SHOTS, noise_levels=LEVELS,
                    qubits=circuit.num_qubits, depth=circuit.depth(),
                    encoding=codes, encoded_rdv=left, encoded_bu_test=right,
                    operations=dict(circuit.count_ops()), target_index=marked,
                    classical_queries=2.25, success_threshold=8/9,
                    noise_model="lambda após CX; lambda/10 após U; leitura ideal",
                    elapsed_seconds=time.perf_counter()-start)
    (ROOT / "dados/metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False))
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "savefig.dpi": 200})
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5), layout="constrained")
    for ax, metric, lo, hi, ref, label in [
        (axes[0], "p", "p_low", "p_high", 8/9, "Chance de localizar a divergência"),
        (axes[1], "queries", "q_low", "q_high", 2.25, "Consultas esperadas até encontrá-la")]:
        y = np.array([r[metric] for r in rows])
        ax.errorbar(range(len(rows)), y,
                    yerr=[np.maximum(0, y-np.array([r[lo] for r in rows])),
                          np.maximum(0, np.array([r[hi] for r in rows])-y)],
                    marker="o", capsize=3, color="#184b75", label="Grover no simulador")
        ax.axhline(ref, color="#b14e32", linestyle="--",
                   label="Equilíbrio: 88,89%" if metric == "p" else "Busca clássica: 2,25")
        ax.set_xticks(range(len(rows)), [str(r["noise"]).replace(".", ",") for r in rows], rotation=40)
        ax.set(xlabel="Intensidade do ruído simulado", ylabel=label)
        ax.grid(alpha=.15)
        ax.legend(fontsize=8)
    axes[0].set_ylim(0, 1.08)
    fig.savefig(ROOT / "figuras/ruido.png")
    plt.close(fig)
    print(json.dumps(metadata, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
