"""Extract the previously verified 466 character Weil polynomials, without recounting points."""
import argparse,re,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("--source",required=True)
p.add_argument("--out",required=True)
a=p.parse_args()
raw=Path(a.source).read_bytes();text=raw.decode()
rows=re.findall(r"^QUOTIENT_ORDER subset=(\d+) genus=(\d+) order=(\d+) charpoly=([x0-9 ^*+\-]+)$",text,re.M)
assert len(rows)==466 and len({int(s) for s,_,_,_ in rows})==466
assert sum(int(g) for _,g,_,_ in rows)==769
for s,g,o,poly in rows:
    assert int(s).bit_count() in (2*int(g)+1,2*int(g)+2)
p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True)
p.write_text("{\nRETURN_POLYNOMIALS=["+",\n".join(f"[{s},{g},{o},{poly}]" for s,g,o,poly in rows)+"];\n}\n")
p.with_suffix(".json").write_text(json.dumps({"source":a.source,"sha256":hashlib.sha256(raw).hexdigest(),"characters":len(rows),"genus_sum":769,"modulus":243,"return_power":9360},indent=2)+"\n")
print("Extracted466 verified character polynomials, total genus769.")
