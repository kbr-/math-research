"""Check complete outer-exponent coverage from retained exact quadratic and first-cup data."""
import argparse,ast,csv,json
from collections import Counter
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();root=Path('research/results/bmd-exception-outer-cups-20261008');data=[]
for name in ['pilot.g','remainder.g']:
 s=(root/name).read_text();assert s.startswith('OUTER_QUADRATIC_DATA := ') and s.rstrip().endswith(';')
 data+=ast.literal_eval(s.split(':=',1)[1].strip()[:-1])
assert len(data)==184 and len({r[0] for r in data})==184
with Path('research/results/bmd-exception-period-cover-20261008/full/curve-0-ranks.csv').open() as f: rows=list(csv.DictReader(f))
ranks={int(r['exponent_residue']):int(r['b0']) for r in rows};assert len(ranks)==28080
assert all(ranks[s]==ranks[s%4680] for s in ranks)
expected={s for s in range(5,4680) if ranks[s] in (138,139)}-{3834};assert set(r[0] for r in data)==expected
assert all(r[1]==ranks[r[0]] and len(r[2])==2 and all(len(v)==769 for v in r[2]) for r in data)
old=Path('research/results/bmd-exception-cup-radical-20261008/data.g').read_text()
olddata=ast.literal_eval(old.split('RADICAL_DATA := ',1)[1].strip()[:-1]);assert len(olddata)==6 and all(r[-1]!=0 for r in olddata)
passed={r[0] for r in data if r[1]==139 and r[4][0][0]!=0}|{3834}
zero=sorted(r[0] for r in data if r[1]==139 and r[4][0][0]==0)
two=sorted(r[0] for r in data if r[1]==138)
failed=sorted(set(range(4680))-{s for s in range(4680) if ranks[s]==140}-passed-{1,2,3,4})
assert failed==sorted(zero+two) and len(failed)==10
# Both rank-two forms are independently proved anisotropic over the retained F27.
assert {r[0]:r[4] for r in data if r[1]==138}=={2809:[[2,0],[0,18]],3745:[[24,11],[11,25]]}
failed=zero
summary={'coefficient_period':4680,'first_cup_ranks':dict(Counter(ranks[s] for s in range(4680))),
 'quadratic_passed':sorted(passed),'quadratic_zero':zero,'anisotropic_rank_two':two,'unresolved_exponents':failed,
 'unresolved_outer_valuations':sorted((s-4)%4680 for s in failed),
 'certified_exponent_classes':4680-len(failed),'scope':'For every actual exponent s>=5, all unit multipliers are certified outside the listed classes; no nonnormality assertion.'}
Path(a.out).write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='quadratic_passed'}));print('OUTER_COVER_COMPLETE quadratic_passed',len(passed))
