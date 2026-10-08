"""Export the two already verified F27 matrices; no numerical computation."""
import argparse, ast, re
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("--source", required=True)
p.add_argument("--out", required=True)
a=p.parse_args()
text=Path(a.source).read_text()
def matrix(name, rows, cols):
    matches=re.findall(r"^"+name+r" := (.*);$",text,re.M)
    assert len(matches)==1
    m=ast.literal_eval(matches[0])
    assert len(m)==rows and all(len(row)==cols for row in m)
    assert all(isinstance(x,int) and 0<=x<27 for row in m for x in row)
    return m
k=matrix("LIFT_K",140,61)
c=matrix("LIFT_THIRD",61,61)
Path(a.out).parent.mkdir(parents=True,exist_ok=True)
Path(a.out).write_text("140 61\n"+"\n".join(" ".join(map(str,row)) for m in (k,c) for row in m)+"\n")
print("Exported full 140x61 kernel and 61x61 reference pairing.")
