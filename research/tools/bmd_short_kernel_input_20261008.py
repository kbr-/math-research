"""Checked export of complete low signed-family cups and kernels to plain field codes."""
import argparse,ast
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True);a=p.parse_args()
s=Path(a.source).read_text();assert s.startswith('LOW_DATA := ') and s.rstrip().endswith(';')
rows=ast.literal_eval(s[len('LOW_DATA := '):].strip()[:-1]);assert len(rows)==4
with open(a.out,'w') as f:
 f.write('4\n')
 for j,(base,q,J,C,K) in enumerate(rows,1):
  h=[137,131,113,61][j-1];assert base==j and q==3**j
  assert len(J)==q and all(len(r)==140 for r in J)
  assert len(C)==len(K)==140 and all(len(r)==140 for r in C) and all(len(r)==h for r in K)
  f.write(f'{j} {h}\n')
  for A in (C,K):
   for row in A:
    assert all(isinstance(v,int) and 0<=v<27 for v in row)
    f.write(' '.join(map(str,row))+'\n')
print('SHORT_KERNEL_INPUT_COMPLETE bases4 complete_cups_and_kernels=true')
