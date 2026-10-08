"""Export the complete measured low cohomology modules and distinct residual return vectors."""
import argparse,ast,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--modules',required=True);p.add_argument('--vectors',required=True);p.add_argument('--out',required=True);p.add_argument('--refined');p.add_argument('--gap-out');a=p.parse_args()
s=Path(a.modules).read_text();prefix='LOW_MULTIPLIER_PRECISION := 10;\nLOW_MULTIPLIER_MODULES := '
assert s.startswith(prefix) and s.rstrip().endswith(';')
rows=ast.literal_eval(s[len(prefix):].strip()[:-1]);assert len(rows)==4
selected=[]
for b in (2,3):
 v=list(map(int,(Path(a.vectors)/f'base-{b}-vectors.txt').read_text().split()));assert v[:2]==[81,769] and len(v)==2+81*771
 seen=set()
 for k in range(1,82):
  pos=2+(k-1)*771;assert v[pos]==k
  if k%3:continue
  degree=v[pos+1];vec=tuple(v[pos+2:pos+771]);assert degree in (9,27)
  if vec not in seen:selected.append([b,k,degree,list(vec)]);seen.add(vec)
assert len(selected)==8
extra=''
if a.refined:
 refined=Path(a.refined).read_text();prefix11='LOW_MULTIPLIER_PRECISION := 11;\nLOW_MULTIPLIER_MODULES := '
 assert refined.startswith(prefix11) and refined.rstrip().endswith(';')
 refined_rows=ast.literal_eval(refined[len(prefix11):].strip()[:-1]);assert len(refined_rows)==1 and refined_rows[0][:3]==[3,4,108]
 extra='LM_REFINED='+json.dumps(refined_rows[0])+';\n'
Path(a.out).write_text('{\nLM_PRECISION=10;\nLM_MODULES='+json.dumps(rows)+';\nLM_VECTORS='+json.dumps(selected)+';\n'+extra+'}\n')
if a.gap_out:
 Path(a.gap_out).write_text('LOW_RETURN_VECTORS := '+json.dumps(selected)+';\n')
print('LOW_COMPARISON_INPUT_COMPLETE modules4 distinct_residual_vectors8 precision10')
