"""Lê o resultado IBM já exportado. Não acessa conta nem envia circuitos."""
import base64
import hashlib
import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from experimento import read_data, wilson

ROOT = Path(__file__).resolve().parent
result = json.loads((ROOT / "dados/ibm-result.json").read_text())
meta = json.loads((ROOT / "dados/ibm.json").read_text())
register = result["data"][0]["results"]["registro"]
assert register["shape"] == [2048, 2] and register["dtype"] == "bool"
packed = np.frombuffer(base64.b64decode(register["data"], validate=True), dtype=np.uint8)
assert packed.size == 512
bits = np.unpackbits(packed).reshape(2048, 2)
counts = dict(Counter("".join(map(str, pair)) for pair in bits))
# A ordem dos bits foi conferida contra a tabela de resultados da interface IBM.
assert counts == meta["counts"]
assert hashlib.sha256((ROOT / "dados/entrada.json").read_bytes()).hexdigest() == meta["input_sha256"]
data = read_data()
target = next(row["index"] for row in data["records"] if row["rdv"] != row["bu_test"])
success = counts[f"{target:02b}"]
p = success / 2048
lo, hi = wilson(success, 2048)
analysis = dict(success=success, shots=2048, p=p, p_low=lo, p_high=hi,
                queries=2/p, q_low=2/hi, q_high=2/lo)
(ROOT / "dados/analise-ibm.json").write_text(json.dumps(analysis, indent=2))

plt.rcParams.update({"font.size": 11, "axes.spines.top": False,
                     "axes.spines.right": False, "savefig.dpi": 220})
fig, ax = plt.subplots(figsize=(5.4, 3.5), layout="constrained")
x = np.arange(4)
ideal = [100 if i == target else 0 for i in x]
physical = [100 * counts[f"{i:02b}"] / 2048 for i in x]
ax.bar(x-.18, ideal, .36, label="Simulação ideal", color="#184b75")
ax.bar(x+.18, physical, .36, label="IBM: equipamento real", color="#b97535")
for i, value in enumerate(physical):
    ax.text(i+.18, value+2, f"{value:.1f}%".replace(".", ","), ha="center", fontsize=9)
ax.set_xticks(x, [f"{i:02b}" + ("*" if i == target else "") for i in x])
ax.set(xlabel="Posição da linha (* diferença introduzida)",
       ylabel="Frequência das respostas (%)", ylim=(0, 113))
ax.legend(fontsize=9, loc="upper right")
fig.savefig(ROOT / "figuras/ibm.png")
plt.close(fig)
print(json.dumps(analysis, indent=2))
