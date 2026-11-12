"""Prepara o recorte presidencial e uma cópia com diferença artificial de um voto."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
source = json.loads((ROOT / "fontes-tse/amostra-presidencia-2026-2t.json").read_text())
with (ROOT / "fontes-tse/comparacao-completa-2026.csv").open() as stream:
    checked = list(csv.DictReader(stream))
assert len(checked) == 8
assert all(r["votos_rdv"] == r["votos_bu"] for r in checked)
records = []
for i, row in enumerate(source["registros"]):
    matches = [r for r in checked if r["eleicao"] == "6258" and
               r["cargo"] == "presidente" and r["tipo"] == row["tipo"] and
               r["codigo"] == str(row["codigo"])]
    assert len(matches) == 1
    match = matches[0]
    assert int(match["votos_rdv"]) == row["votos_rdv"]
    assert int(match["votos_bu"]) == row["votos_bu"]
    records.append(dict(index=i, category=row["categoria"], candidate=row["codigo"],
                        rdv=row["votos_rdv"], bu=row["votos_bu"], bu_test=row["votos_bu"]))
assert [r["rdv"] for r in records] == [68, 149, 2, 13]
records[1]["bu_test"] -= 1
values = sorted({r[key] for r in records for key in ("rdv", "bu", "bu_test")})
assert values == [2, 13, 68, 148, 149]
encoding = {str(value): index for index, value in enumerate(values)}
assert len(set(encoding.values())) == len(values)
source["arquivos"] = {name: hashlib.sha256((ROOT / "fontes-tse" / name).read_bytes()).hexdigest()
                      for name in ("o03221ac0100700090001-bu.dat", "o03221ac0100700090001-rdv.dat")}
data = dict(source=source, records=records, encoding=encoding,
            modification="Cópia experimental: reduzir de 149 para 148 o segundo registro; arquivos oficiais intactos.")
(ROOT / "dados/entrada.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))
print("Quatro categorias presidenciais verificadas; diferença artificial de um voto em cópia.")
