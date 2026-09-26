"""Summarize the slot Hilbert-function runs: cases with |Z| >= 2*full, removed vs quadric count/span."""
import json, sys
from pathlib import Path
d = Path(__file__).parent
rows = []
for f in ["hf_small.json", "hf_large.json", "hf_span.json"]:
    data = json.loads((d / f).read_text())
    data = data if isinstance(data, list) else data.get("cases", data)
    for c in data:
        c["file"] = f
        rows.append(c)
seen = {}
for c in rows:  # hf_span repeats cases of the other files with the same seeds; keep one per case
    key = (c["v"], c["k"], c["r"], c["seed"])
    if key not in seen or "quadric_span" in c:
        seen[key] = c
rows = list(seen.values())
reg = [c for c in rows if c["points"] >= 2 * c["full"]]
print("all cases", len(rows), "regime cases", len(reg))
print("removed<=qm in regime:", all(c["removed"] <= c["quadric_multiples"] for c in reg))
print("removed/qm range:", min(c["removed"] / c["quadric_multiples"] for c in reg), max(c["removed"] / c["quadric_multiples"] for c in reg))
print("F2/removed range:", min(c["f2_removed"] / c["removed"] for c in reg if c["removed"]), max(c["f2_removed"] / c["removed"] for c in reg if c["removed"]))
sp = [c for c in reg if "quadric_span" in c]
print("regime with span", len(sp), "max removed-qspan", max(c["removed"] - c["quadric_span"] for c in sp))
print("zero-removed regime cases", sum(1 for c in reg if c["removed"] == 0))
for c in rows:
    print(c["file"], c["v"], c["k"], c["r"], c["seed"], c["points"], c["full"], c["removed"], c.get("quadric_span"), c["quadric_multiples"], c["f2_removed"], "REG" if c in reg else "")
