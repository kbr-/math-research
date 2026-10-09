#!/usr/bin/env python3
"""Convert bounded native frame rows into a PARI-readable coefficient record."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
with a.input.open() as f:
 prime,pole,nref=map(int,f.readline().split());slopes=list(map(int,f.readline().split()));assert len(slopes)==4
 first=list(map(int,f.readline().split()));mod=first if len(first)==3 else [36,1,1];pending=None if len(first)==3 else first
 assert len(first)==3 or prime==37
 frames=[]
 for k in range(nref+1):
  M,N,U,dim=pending if pending is not None else map(int,f.readline().split());pending=None;flat=list(map(int,f.readline().split()));assert len(flat)==2*U
  cols=[flat[i:i+2] for i in range(0,len(flat),2)];rows=[list(map(int,f.readline().split())) for j in range(dim)]
  assert all(len(row)==U and all(0<=v<prime**2 for v in row) for row in rows)
  frames.append([M,N,cols,rows])
 assert not f.read().strip()
a.out.write_text('fieldPrime='+str(prime)+';modCodes='+json.dumps(mod)+';slCodes='+json.dumps(slopes,separators=(',',':'))+';torsionPole='+str(pole)+';frames='+json.dumps(frames,separators=(',',':'))+';\n')
print('Converted',len(frames),'full exact coefficient frames')
