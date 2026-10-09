#!/usr/bin/env python3
"""Export the full geometric torsion germs for an independent scalar-period check."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('period',type=int);p.add_argument('out',type=Path);p.add_argument('--sparse',action='store_true');a=p.parse_args()
assert a.period>0
with a.input.open() as f:
    header=list(map(int,f.readline().split()));degree=header[0]
    assert degree in (2,4) and len(header)==degree+2
    embedding=int(f.readline())
    if a.sparse:
        spec=list(map(int,f.readline().split()));assert len(spec)==spec[0]+1 and len(set(spec[1:]))==spec[0]
    for _ in range(24):
        rows=list(map(int,f.readline().split()));assert len(rows)==188 and len(set(rows))==188 and all(0<=r<460 for r in rows)
    germs=list(map(int,f.readline().split()));assert len(germs)==512 and all(0<=v<37**degree for v in germs)
a.out.write_text('LOCAL_CERTIFICATE := '+json.dumps([degree,header[1:],embedding,germs,a.period])+';\n')
print('Exported all 512 local coefficients and the exact field modulus; period',a.period)
