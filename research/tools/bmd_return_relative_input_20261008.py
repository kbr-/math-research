"""Export exactly the retained first cup and kernel from GAP syntax to PARI syntax."""
import argparse,ast,re,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--source",required=True);p.add_argument("--out",required=True);p.add_argument("--vectors",required=True);p.add_argument("--gap-out",required=True);a=p.parse_args()
s=Path(a.source).read_text();parts=[]
for name,cols in (("LIFT_C",140),("LIFT_K",61)):
    matches=re.findall(r"^"+name+r" := (.*);$",s,re.M);assert len(matches)==1
    m=ast.literal_eval(matches[0]);assert len(m)==140 and all(len(r)==cols for r in m)
    assert all(isinstance(x,int) and 0<=x<27 for r in m for x in r)
    parts.append(name+"="+json.dumps(m)+";")
Path(a.out).write_text("{\n"+"\n".join(parts)+"\n}\n")
print("Exported exact140-square first cup and140x61 kernel.")

v=list(map(int,Path(a.vectors).read_text().split()))
assert v[:2]==[27,769] and len(v)==2+27*771
pos=2+17*771
assert v[pos:pos+2]==[18,81]
row=v[pos+2:pos+771]
assert len(row)==769 and all(0<=x<27 for x in row)
Path(a.gap_out).write_text("REL_VECTOR := "+json.dumps(row)+";\n")
