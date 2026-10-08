"""Export all81 short-return leading components on three independent reference characters."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--vectors',required=True);p.add_argument('--old-vectors',required=True);p.add_argument('--out',required=True);a=p.parse_args()
def read_vectors(path,n):
 v=list(map(int,Path(path).read_text().split()));assert v[:2]==[n,769] and len(v)==2+n*771
 rows=[]
 for k in range(n):
  pos=2+k*771;assert v[pos]==k+1
  rows.append([v[pos+1],v[pos+2:pos+771]])
 return rows
series=[read_vectors(Path(a.vectors)/f'base-{b}-vectors.txt',81) for b in range(1,5)]
old=read_vectors(a.old_vectors,27)
assert series[3][26]==old[17]
data=list(map(int,Path(a.input).read_text().split()));assert data[0]==466
pos=1;offset=0;selected=[]
for _ in range(466):
 mask,g=data[pos:pos+2];pos+=2
 rows=[data[pos+i*2*g:pos+(i+1)*2*g] for i in range(81)];pos+=81*2*g
 if mask in (7,83,511):
  selected.append([mask,g,rows,[[row[1][offset:offset+g] for row in base] for base in series]])
 offset+=g
assert pos==len(data) and offset==769 and len(selected)==3
for b,base in enumerate(series,1):
 for k,(degree,row) in enumerate(base,1):
  v=0;t=k
  while t%3==0:v+=1;t//=3
  assert degree==3**min(1+v,b)
Path(a.out).write_text('{\nSHORT_ORDERS='+json.dumps([[r[0] for r in base] for base in series])+';\nSHORT_CASES='+json.dumps(selected)+';\n}\n')
print('SHORT_COMPONENT_INPUT_COMPLETE returns81 bases4 masks7_83_511=true order_formula=true exceptional_vector_matches_previous=true')
