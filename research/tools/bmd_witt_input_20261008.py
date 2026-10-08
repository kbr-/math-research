"""Translate the retained exact GAP-format character export to checked GP input."""
import argparse,ast,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--assembly',action='store_true');p.add_argument('--eight',action='store_true');a=p.parse_args()
s=Path('research/results/bmd-exception-cubic-obstruction-20261008/characters.g').read_text()
first,second=s.split('WITT_CHARACTERS := ',1)
exponents=ast.literal_eval(first.split(':=',1)[1].strip()[:-1]);rows=ast.literal_eval(second.strip()[:-1])
assert len(exponents)==30 and len(rows)==466 and len({r[0] for r in rows})==466
assert all(len(r[4])==30 and all(len(v)==3 for v in r[4]) for r in rows)
if a.eight and not a.assembly:
 raw=Path('research/results/bmd-exception-cubic-obstruction-20261008/characters8.g').read_text()
 e,rest=raw.split('JET8_E := ',1);ec,body=rest.split('JET8_CHARACTERS := ',1)
 assert ast.literal_eval(e.split(':=',1)[1].strip()[:-1])==exponents
 eight=ast.literal_eval(body.strip()[:-1]);assert [r[0] for r in eight]==[r[0] for r in rows]
 for old,new in zip(rows,eight): old[4]=new[1]
 E=ast.literal_eval(ec.strip()[:-1])
 Path(a.out).write_text('{\nJW_EXPONENTS='+json.dumps(exponents)+';\nJW_E8='+json.dumps(E)+';\nJW_CHARACTERS='+json.dumps(rows)+';\n}\n')
 print('WITT_EIGHT_INPUT_COMPLETE characters466 exponents30');raise SystemExit(0)
if a.assembly:
 states=[];all_exponents=[]
 for name in (['assembly8-pilot.g','assembly8-full.g'] if a.eight else ['assembly-pilot.g','assembly-full.g']):
  raw=Path('research/results/bmd-exception-cubic-obstruction-20261008/'+name).read_text()
  e,rest=raw.split('CUBIC_CHARACTERS := ',1);chars,body=rest.split('CUBIC_STATES := ',1)
  ids=ast.literal_eval(chars.strip()[:-1]);assert ids==[r[0] for r in rows]
  all_exponents+=ast.literal_eval(e.split(':=',1)[1].strip()[:-1]);states+=ast.literal_eval(body.strip()[:-1])
 assert all_exponents==exponents and len(states)==30
 kernels=[]
 for name in ['pilot.g','remainder.g']:
  raw=Path('research/results/bmd-exception-outer-cups-20261008/'+name).read_text()
  kernels += [r for r in ast.literal_eval(raw.split(':=',1)[1].strip()[:-1]) if r[1]==139 and r[4]==[[0]]]
 assert len(kernels)==8
 Path(a.out).write_text('{\nJC_EXPONENTS='+json.dumps(exponents)+';\nJC_CHARACTERS='+json.dumps(ids)+';\nJC_STATES='+json.dumps(states)+';\nJC_KERNELS='+json.dumps(kernels)+';\n}\n')
 print('CUBIC_ASSEMBLY_INPUT_COMPLETE states30 kernels8');raise SystemExit(0)
Path(a.out).write_text('{\nJW_EXPONENTS='+json.dumps(exponents)+';\nJW_CHARACTERS='+json.dumps(rows)+';\n}\n')
print('WITT_INPUT_COMPLETE characters466 exponents30')
