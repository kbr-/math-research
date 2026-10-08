"""Export bounded actual components for independent PARI checks of the FLINT vectors."""
import argparse,json,hashlib
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("--input",required=True);p.add_argument("--vectors",required=True);p.add_argument("--out",required=True)
a=p.parse_args()
data=list(map(int,Path(a.input).read_text().split()));assert data[0]==466
v=list(map(int,Path(a.vectors).read_text().split()));assert v[:2]==[27,769]
orders=[];vectors=[];pos=2
for k in range(1,28):
    kk,m=v[pos:pos+2];assert kk==k
    orders.append(m);vectors.append(v[pos+2:pos+771]);pos+=771
assert pos==len(v) and all(len(x)==769 for x in vectors)
pos=1;offset=0;selected=[]
for _ in range(466):
    mask,g=data[pos:pos+2];pos+=2
    rows=[data[pos+i*2*g:pos+(i+1)*2*g] for i in range(27)];pos+=27*2*g
    if mask in (7,83,511):
        selected.append([mask,g,rows,[row[offset:offset+g] for row in vectors]])
    offset+=g
assert pos==len(data) and offset==769 and len(selected)==3
Path(a.out).write_text("{\nVECTOR_CHECK_ORDERS="+json.dumps(orders)+";\nVECTOR_CHECK_CASES="+json.dumps(selected)+";\n}\n")
print("Exported all27 leading components on masks7,83,511; largest genus4 retained.")
