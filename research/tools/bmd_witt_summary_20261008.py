"""Check the exhaustive exponent/multiplier grid and summarize actual stopping obstructions."""
import argparse,ast,json
from collections import Counter
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args()
root=Path('research/results/bmd-exception-cubic-obstruction-20261008');rows=[]
for name in ['section-pilot.g','section-full.g']:
 s=(root/name).read_text();assert s.startswith('BOUNDED_SECTION_RESULTS := ') and s.rstrip().endswith(';')
 rows+=ast.literal_eval(s.split(':=',1)[1].strip()[:-1])
base=[670,937,1091,3180,3735,3749,3893,4240];units=[1,2,4,5,7,8]
target=[r for r in rows if not r[2]];controls=[r for r in rows if r[2]]
assert len(target)==144 and {(r[0],r[1]) for r in target}=={(s+4680*j,n) for s in base for j in range(3) for n in units}
assert len(controls)==6 and {(r[0],r[1]) for r in controls}=={(s,n) for s in [2,4] for n in [1,2,8]}
assert all(r[3] in [3,4] and r[4]!=0 and len(r[7])==r[3] for r in target)
assert all((r[3]==3 and r[4]==r[5]!=0) if r[1]==2 else (r[3]==0 and len(r[7])==9) for r in controls)
quartic=[[r[0],r[1],r[4]] for r in target if r[3]==4];assert quartic==[[10451,2,25],[10451,7,14]]
summary={'jet_period':14040,'stable_from':6,'unit_modulus':9,'target_cases':len(target),'control_cases':len(controls),'first_nonzero_orders':dict(Counter(r[3] for r in target)),
 'quartic_cases':quartic,'unresolved_cases':[],
 'all_obstructions':[[r[0],r[1],r[3],r[4],r[5]] for r in target],
 'original_scope':'Dimension-nine characteristic-three normality at d=3+M*h for every positive h; no complete exception pair or cutoff.',
 'annihilator_M':'373626052793651569891069437246726104678400'}
Path(a.out).write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='all_obstructions'}));print('WITT_OBSTRUCTION_TABLE_COMPLETE')
