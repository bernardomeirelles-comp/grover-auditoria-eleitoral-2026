"""Analisa somente exports IBM locais; não possui conexão ou submissão à IBM.

Decodifica sampler v2 compactado, valida cada circuito físico e compara um
modelo aproximado da calibração com segmentos reinicializados isoladamente.
"""
import base64
import csv
import hashlib
import importlib.util
import json
import math
import re
import zlib
from collections import Counter
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit, qasm3
from qiskit.quantum_info import average_gate_fidelity
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, thermal_relaxation_error

ROOT = Path(__file__).resolve().parent
COMPOSER = ROOT / "revisao/composer"
OUT = ROOT / "revisao/analise-ibm"
STATES = ["00", "01", "10", "11"]
SOURCE = "https://qiskit.github.io/qiskit-aer/tutorials/2_device_noise_simulation.html"


def wilson(k, n):
    z = 1.959963984540054
    p = k / n
    d = 1 + z*z/n
    c = (p + z*z/(2*n))/d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return c-h, c+h


def write_csv(name, rows):
    with (OUT / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def decode_result(path):
    result = json.loads(path.read_text())
    assert result["schema_version"] == "v2.0" and len(result["data"]) == 1
    arrays, counts = {}, {}
    for register, entry in result["data"][0]["results"].items():
        assert entry["dtype"] == "bool" and entry["shape"] == [1, 512, 2]
        payload = zlib.decompress(base64.b64decode(entry["data"], validate=True))
        assert len(payload) == 128
        bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8)).reshape(512, 2)
        # Exibição IBM: coluna esquerda é o bit mais significativo, c[1].
        values = 2*bits[:, 0] + bits[:, 1]
        arrays[register] = values
        counts[register] = {state: int(np.count_nonzero(values == i)) for i, state in enumerate(STATES)}
    assert set(arrays) == {f"r{i:02d}" for i in range(12)}
    return arrays, counts


def physical_circuits(info):
    texts = info["params"]["quantum_program"]["circuits"]["data"]
    assert len(texts) == 1
    text = texts[0]
    physical = sorted({int(q) for q in re.findall(r"\$(\d+)", text)})
    assert len(physical) == 5
    lookup = {q: i for i, q in enumerate(physical)}
    compact = re.sub(r"\$(\d+)", lambda m: f"q[{lookup[int(m.group(1))]}]", text)
    compact = compact.replace('include "stdgates.inc";', 'include "stdgates.inc";\nqubit[5] q;')
    full = qasm3.loads(compact)
    segments = []
    current = QuantumCircuit(5, 2)
    measurements = {}
    name = None
    for item in full.data:
        qubits = [full.find_bit(q).index for q in item.qubits]
        if item.operation.name == "measure":
            register, bit = full.find_bit(item.clbits[0]).registers[0]
            assert name is None or name == register.name
            name = register.name
            assert bit not in measurements
            measurements[bit] = qubits[0]
            current.measure(qubits[0], bit)
            if len(measurements) == 2:
                assert current.count_ops().get("reset", 0) == 5
                segments.append((name, current, dict(measurements)))
                current, measurements, name = QuantumCircuit(5, 2), {}, None
        else:
            assert not item.clbits
            current.append(item.operation, qubits)
    assert len(segments) == 12
    assert all(item.operation.name == "barrier" for item in current.data)
    return text, compact, full, physical, segments


def probabilities(circuit, mapping, noise=None):
    q = circuit.remove_final_measurements(inplace=False)
    q.save_probabilities([mapping[0], mapping[1]])
    simulator = AerSimulator(method="density_matrix", noise_model=noise, max_parallel_threads=2)
    result = simulator.run(q, shots=1).result()
    p = np.asarray(result.data(0)["probabilities"], dtype=float)
    assert np.isclose(p.sum(), 1) and np.min(p) > -1e-10
    return p


def pair_values(text):
    return {int(k): float(v) for k, v in (piece.split(":") for piece in text.split(";") if piece)}


def calibration_model(full, physical, calibration):
    """Ajusta despolarização residual à infidelidade total; não soma dois erros totais."""
    model = NoiseModel(basis_gates=["rx", "rz", "sx", "x", "cz", "id"])
    rows = []
    seen = set()
    for item in full.data:
        name = item.operation.name
        if name in ("barrier", "measure", "reset", "rz"):
            continue  # RZ virtual; resets e esperas são ideais neste modelo isolado.
        qubits = tuple(full.find_bit(q).index for q in item.qubits)
        key = name, qubits
        if key in seen:
            continue
        seen.add(key)
        phys = [physical[i] for i in qubits]
        if name == "cz":
            rates = pair_values(calibration[phys[0]]["CZ error"])
            times = pair_values(calibration[phys[0]]["Gate length (ns)"])
            assert phys[1] in rates and phys[1] in times
            rate, duration_ns = rates[phys[1]], times[phys[1]]
        else:
            field = {"rx": "RX error", "sx": "√x (sx) error", "x": "Pauli-X error", "id": "ID error"}[name]
            rate = float(calibration[phys[0]][field])
            duration_ns = float(calibration[phys[0]]["Single-qubit gate length (ns)"])
        relaxation = None
        truncated = []
        for index in phys:
            t1 = 1000*float(calibration[index]["T1 (us)"])
            raw_t2 = 1000*float(calibration[index]["T2 (us)"])
            t2 = min(raw_t2, 2*t1)
            if t2 != raw_t2:
                truncated.append(index)
            channel = thermal_relaxation_error(t1, t2, duration_ns, excited_state_population=0)
            relaxation = channel if relaxation is None else relaxation.expand(channel)
        f_relax = float(average_gate_fidelity(relaxation))
        d = 2**len(qubits)
        residual = max(0., d*(rate - (1-f_relax))/(d*f_relax-1))
        assert residual <= d*d/(d*d-1)
        combined = relaxation if residual == 0 else depolarizing_error(residual, len(qubits)).compose(relaxation)
        fidelity = float(average_gate_fidelity(combined))
        if rate >= 1-f_relax:
            assert math.isclose(1-fidelity, rate, abs_tol=1e-10)
        model.add_quantum_error(combined, name, list(qubits))
        rows.append({"gate": name, "physical_qubits": ",".join(map(str, phys)), "duration_ns": duration_ns,
                     "reported_infidelity": rate, "thermal_infidelity": 1-f_relax,
                     "residual_depolarizing_lambda": residual, "combined_infidelity": 1-fidelity,
                     "thermal_exceeds_reported": rate < 1-f_relax, "t2_truncated_qubits": str(truncated)})
    return model, rows


def readout(probability, mapping, physical, calibration):
    # Apply exact independent assignment probabilities AFTER quantum evolution.
    # No measurement-duration relaxation is added: assignment data include readout.
    result = np.zeros(4)
    for true in range(4):
        for measured in range(4):
            factor = probability[true]
            for bit in range(2):
                row = calibration[physical[mapping[bit]]]
                error_01 = float(row["Prob meas1 prep0"])
                error_10 = float(row["Prob meas0 prep1"])
                a, b = (true >> bit) & 1, (measured >> bit) & 1
                factor *= ([[1-error_01, error_01], [error_10, 1-error_10]])[a][b]
            result[measured] += factor
    assert np.isclose(result.sum(), 1)
    return result


def process(info_path, protocol, calibration):
    info = json.loads(info_path.read_text())
    job = info["id"]
    assert info["backend"] == "ibm_marrakesh" and info["status"] == "Completed"
    result_path = info_path.with_name(info_path.name.replace("-info.json", "-result.json"))
    arrays, counts = decode_result(result_path)
    physical_text, compact_text, full, physical, segments = physical_circuits(info)
    (OUT / f"{job}-fisico.qasm").write_text(physical_text)
    (OUT / f"{job}-compactado.qasm").write_text(compact_text)
    ideal = {name: probabilities(circuit, mapping) for name, circuit, mapping in segments}
    targets = [int(np.argmax(ideal[name])) for name, *_ in segments]
    matches = [i for i, block in enumerate(protocol["blocks"], 1)
               if targets == [entry["target"] for entry in block["segments"]]]
    assert len(matches) == 1, (job, targets, matches)
    block_id = matches[0]
    block = protocol["blocks"][block_id-1]
    assert hashlib.sha256((COMPOSER / block["file"]).read_bytes()).hexdigest() == block["sha256"]
    # Full sequence check preserves all resets and measurements.
    full_result = AerSimulator(method="density_matrix", max_parallel_threads=2).run(full, shots=32, seed_simulator=20261111).result()
    assert full_result.get_counts() == {block["ideal_expected"]: 32}
    noise, noise_rows = calibration_model(full, physical, calibration)
    result_rows, validation = [], []
    for (register, circuit, mapping), planned in zip(segments, block["segments"]):
        assert register == planned["register"]
        target = planned["target"]
        assert np.isclose(ideal[register][target], 1, atol=1e-10)
        model_gate = probabilities(circuit, mapping, noise)
        model_full = readout(model_gate, mapping, physical, calibration)
        controls_only = readout(ideal[register], mapping, physical, calibration)
        n = sum(counts[register].values())
        k = counts[register][f"{target:02b}"]
        low, high = wilson(k, n)
        operations = dict(circuit.count_ops())
        variant = planned["experiment"].rsplit("_", 1)[0]
        record = {"job": job, "block": block_id, "register": register, "variant": variant,
                  "target": target, "shots": n, "success": k, "p": k/n, "wilson_low": low,
                  "wilson_high": high, "ideal_p": float(ideal[register][target]),
                  "model_gate_p": float(model_gate[target]), "model_readout_only_p": float(controls_only[target]),
                  "model_gate_readout_p": float(model_full[target]),
                  "cz": operations.get("cz", 0), "depth_with_reset_measure": circuit.depth(),
                  "measure_c0_physical": physical[mapping[0]], "measure_c1_physical": physical[mapping[1]],
                  **{f"count_{state}": counts[register][state] for state in STATES},
                  **{f"model_p_{state}": float(model_full[i]) for i, state in enumerate(STATES)}}
        result_rows.append(record)
        validation.append({"register": register, "experiment": planned["experiment"],
                           "physical_measurement_map": {str(k): physical[v] for k, v in mapping.items()},
                           "ideal_distribution": ideal[register].tolist(), "operations": operations,
                           "model_distribution": model_full.tolist()})
    metadata = {"job": job, "block": block_id, "created_utc": info["created"], "active_physical_qubits": physical,
                "full_operations": dict(full.count_ops()), "full_depth": full.depth(),
                "full_ideal_sequence_counts": full_result.get_counts(), "segments": validation,
                "input_hashes": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in (info_path, result_path)},
                "decoder": "base64 -> zlib -> numpy.unpackbits big-endian -> shape(512,2), c1c0"}
    (OUT / f"{job}-validacao.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False))
    for row in noise_rows:
        row["job"] = job
    paired = []
    for target in range(4):
        a = next(r for r in result_rows if r["variant"] == "original" and r["target"] == target)
        b = next(r for r in result_rows if r["variant"] == "gray_cancelado" and r["target"] == target)
        hits_a, hits_b = arrays[a["register"]] == target, arrays[b["register"]] == target
        paired.append({"block": block_id, "target": target, "both_success": int(np.sum(hits_a & hits_b)),
                       "gray_only_success": int(np.sum(~hits_a & hits_b)),
                       "original_only_success": int(np.sum(hits_a & ~hits_b)),
                       "neither_success": int(np.sum(~hits_a & ~hits_b)), "difference": b["p"]-a["p"]})
    return result_rows, noise_rows, paired


def plot(rows, pooled):
    spec = importlib.util.spec_from_file_location("editorial", ROOT / "gerar-figuras.py")
    editorial = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(editorial)
    editorial.style()
    import matplotlib.pyplot as plt
    blocks = sorted({r["block"] for r in rows})
    fig, axes = plt.subplots(1, 2, figsize=(6.95, 3.3), gridspec_kw={"width_ratios": [1.8, 1]})
    fig.subplots_adjust(left=.075, right=.985, bottom=.20, top=.81, wspace=.18)
    groups = [("original", "Original", editorial.GRAY, "o", -.13),
              ("gray_cancelado", "Gray + cancelamento", editorial.BLUE, "^", .13),
              ("controle", "Preparação / reset / leitura", editorial.OCHRE, "s", 0)]
    for variant, label, color, marker, offset in groups:
        ax = axes[1] if variant == "controle" else axes[0]
        points = [next(r for r in pooled if r["variant"] == variant and r["target"] == i) for i in range(4)]
        y = np.array([r["p"] for r in points])*100
        error = np.array([[r["p"]-r["wilson_low"] for r in points],
                          [r["wilson_high"]-r["p"] for r in points]])*100
        ax.errorbar(np.arange(4)+offset, y, yerr=error, color=color, marker=marker,
                    linestyle="none", markersize=5, capsize=2, linewidth=.8, label=label, zorder=4)
        for block, shift in zip(blocks if len(blocks) > 1 else [], np.linspace(-.05, .05, len(blocks))):
            part = [next(r for r in rows if r["block"] == block and r["variant"] == variant and r["target"] == i) for i in range(4)]
            ax.scatter(np.arange(4)+offset+shift, [r["p"]*100 for r in part], s=9,
                       marker=marker, facecolors="white", edgecolors=color, linewidths=.55, alpha=.8, zorder=3)
    for ax in axes:
        ax.set_axisbelow(True)
        ax.set(xticks=range(4), xticklabels=STATES, ylim=(0, 105), xlim=(-.45, 3.45), yticks=[0,25,50,75,100])
    axes[0].axhline(100*8/9, color=editorial.INK, linestyle=(0, (4,3)), linewidth=.7)
    axes[0].set_xlabel("Posição divergente")
    axes[1].set_xlabel("Estado preparado")
    axes[0].set_ylabel("Acerto observado (%)")
    axes[1].tick_params(labelleft=False)
    axes[0].legend(loc="lower left", bbox_to_anchor=(-.015,1.02), frameon=False, ncol=2, fontsize=9)
    axes[1].set_title("Controles", fontsize=10, pad=13)
    dimensions = editorial.save(fig, "ibm-repeticoes")
    metadata = {**dimensions, "blocks_observed": blocks, "shots_per_target_variant": 512*len(blocks),
                "confidence_intervals": "marginal Wilson 95%; no block-drift adjustment",
                "complete_design": blocks == [1, 2, 3], "hollow_markers": "individual blocks if more than one",
                "source_sha256": hashlib.sha256((OUT / "resultados-por-bloco.csv").read_bytes()).hexdigest()}
    (ROOT / "figuras/manifesto-ibm-repeticoes.json").write_text(json.dumps(metadata, indent=2))


def main():
    OUT.mkdir(exist_ok=True)
    protocol = json.loads((COMPOSER / "protocolo.json").read_text())
    files = sorted((COMPOSER / "brutos").glob("job-*-info.json"))
    assert files
    calibration_files = list((ROOT / "revisao/calibracao").glob("*.csv"))
    assert len(calibration_files) == 1, "Selecionar explicitamente a calibração se houver mais de uma."
    calibration_path = calibration_files[0]
    with calibration_path.open(newline="") as handle:
        calibration = {int(row["Qubit"]): row for row in csv.DictReader(handle)}
    rows, gates, paired = [], [], []
    for path in files:
        a, b, c = process(path, protocol, calibration)
        rows.extend(a); gates.extend(b); paired.extend(c)
        print(path.name, "validado", flush=True)
    ui_path = COMPOSER / "consumo-interface.json"
    ui_validation = None
    if ui_path.exists():
        ui = json.loads(ui_path.read_text())
        check = ui["ui_count_check"]
        matching = [r for r in rows if r["job"] == check["job"] and r["register"] == check["register"]]
        assert len(matching) == 1
        assert {state: matching[0][f"count_{state}"] for state in STATES} == check["counts"]
        assert {r["job"] for r in rows} == {j["id"] for j in ui["jobs"]}
        assert sum(j["qpu_seconds_displayed"] for j in ui["jobs"]) == ui["total_qpu_seconds_displayed"]
        ui_validation = {"job": check["job"], "register": check["register"], "counts_match": True,
                         "displayed_qpu_seconds": ui["total_qpu_seconds_displayed"],
                         "source_sha256": hashlib.sha256(ui_path.read_bytes()).hexdigest()}
    blocks = sorted({r["block"] for r in rows})
    assert len(rows) == 12*len(blocks), "Submissão duplicada de bloco: não selecionar silenciosamente."
    pooled = []
    for variant in ("original", "gray_cancelado", "controle"):
        for target in range(4):
            group = [r for r in rows if r["variant"] == variant and r["target"] == target]
            success, shots = sum(r["success"] for r in group), sum(r["shots"] for r in group)
            low, high = wilson(success, shots)
            pooled.append({"variant": variant, "target": target, "blocks": len(group), "shots": shots,
                           "success": success, "p": success/shots, "wilson_low": low, "wilson_high": high,
                           "block_p_min": min(r["p"] for r in group), "block_p_max": max(r["p"] for r in group),
                           "mean_model_p": float(np.mean([r["model_gate_readout_p"] for r in group]))})
    write_csv("resultados-por-bloco.csv", rows)
    write_csv("resultados-agregados.csv", pooled)
    write_csv("modelo-portas.csv", gates)
    write_csv("comparacao-pareada.csv", paired)
    summary = {"blocks_observed": blocks, "complete_three_block_design": blocks == [1,2,3],
               "ui_validation": ui_validation,
               "segments_validated": len(rows), "all_physical_ideal_targets_verified": True,
               "all_full_reset_sequences_verified": True, "shots_per_segment_per_block": 512,
               "calibration_file": str(calibration_path.relative_to(ROOT)),
               "calibration_sha256": hashlib.sha256(calibration_path.read_bytes()).hexdigest(),
               "model_reference": SOURCE,
               "model": "gate relaxation + residual depolarization fitted to reported average infidelity; independent readout assignment",
               "limitations": ["Calibration snapshot predates these jobs and does not reconstruct the November 6 run.",
                   "Each segment starts independently at zero with ideal reset in the model; hardware segments share a shot.",
                   "No idle scheduling, reset error, leakage, crosstalk, coherent error, drift or inter-segment memory.",
                   "RX/SX/X use the single-qubit gate duration in the CSV; this is an approximation.",
                   "T2 is capped at 2*T1 if necessary; excess thermal infidelity is logged, not counted twice.",
                   "No extra thermal channel during readout: assignment probabilities already describe readout.",
                   "Wilson intervals are marginal descriptive binomial intervals; pooling does not model block drift.",
                   "Physical mapping and compiled gate sequences can differ between blocks; block variation does not isolate temporal drift.",
                   "Controls combine preparation, reset and readout; they do not isolate readout alone.",
                   "The approximation is not a causal diagnosis or a fit to the observed counts."],
               "pooled_results": pooled}
    (OUT / "resumo.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    plot(rows, pooled)
    print(json.dumps({k:summary[k] for k in ["blocks_observed", "segments_validated", "complete_three_block_design"]}))


if __name__ == "__main__":
    main()
