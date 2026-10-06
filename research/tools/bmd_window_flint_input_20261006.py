#!/usr/bin/env python3
"""Lossless sparse text conversion of selected retained GP polynomial matrices."""
import argparse,re
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
a=ap.parse_args();cases=[];current=None
for s in a.input.read_text().splitlines():
 if s.startswith('CASE '): current={k:int(v) for k,v in re.findall(r'(exponent_class|precision|reduced_dimension)=(\d+)',s)}
 elif s.startswith('matrix=') and current['exponent_class'] in [5,18,23]:
  raw=s[len('matrix=['):-1];cells=[];depth=0;start=0
  for pos,ch in enumerate(raw):
   if ch=='(': depth+=1
   elif ch==')': depth-=1
   elif ch in ',;' and depth==0:
    cells.append(raw[start:pos].strip());start=pos+1
  cells.append(raw[start:].strip())
  cells=[(re.fullmatch(r'Mod\((.*), (?:Mod\(1, 3\)\*)?u\^192\)',x)[1] if x.endswith('u^192)') else x) for x in cells]
  assert len(cells)==current['reduced_dimension']**2
  cases.append((current,cells))
assert [c['exponent_class'] for c,_ in cases]==[5,18,23]
with a.out.open('w') as out:
 print(len(cases),file=out)
 for c,cells in cases:
  print(c['exponent_class'],c['reduced_dimension'],c['precision'],file=out)
  for cell in cells:
   terms=[]
   for m in re.finditer(r'Mod\(([12]), 3\)(\*u(?:\^(\d+))?)?',cell):
    exponent=int(m[3]) if m[3] else (1 if m[2] else 0)
    terms.append((exponent,int(m[1])))
   residue=re.sub(r'Mod\(([12]), 3\)(\*u(?:\^(\d+))?)?','',cell).replace(' + ','').replace('Mod(0, 3)','0').strip()
   assert residue in ('','0'),cell
   assert len({e for e,_ in terms})==len(terms)
   print(len(terms),*(item for pair in terms for item in pair),file=out)
print('PASS lossless conversion of classes5,18,23')
