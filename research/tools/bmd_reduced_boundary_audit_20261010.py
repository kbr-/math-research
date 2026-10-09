"""Stage exact reduced-boundary certificates for independent PARI verification."""
import argparse, json
from math import comb
from pathlib import Path
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--directory',type=Path,required=True)
ap.add_argument('--out',type=Path,required=True)
ap.add_argument('--full',action='store_true')
ap.add_argument('--full-reduced',action='store_true')
args=ap.parse_args()
assert not (args.full and args.full_reduced)
data=[]
for path in sorted(args.directory.glob('n*-line*.json')):
    if path.name.endswith('-input.json'): continue
    d=json.loads(path.read_text())
    if d['status']!='certified': continue
    n,p,e=d['cube_dimension'],d['prime'],d['field_degree']
    R=comb(n+1,2); threshold=3*comb(n+1,4)
    assert d['pairs']==R and d['threshold']==threshold
    assert d['norm_degree']==e*threshold and len(d['norm_determinant'])==e*threshold+1
    assert d['norm_determinant'][-1]==1 and d['gcd']==[1]
    assert d['norm_factor_dimension']==e*(R-d['unit_columns'])
    assert all(0<=x['replaced_column']<R-1 for x in d['additional_minors'])
    data.append([n,p,e,d['modulus'],d['intercept'],d['direction'],
                 d['norm_determinant'],d['norm_adjacent_minor'],
                 [[x['replaced_column'],x['norm']] for x in d['additional_minors']],
                 int(d.get('separated_collisions',False))])
assert data, 'no certified inputs'
args.out.parent.mkdir(parents=True,exist_ok=True)
with args.out.open('x') as f:
    f.write('FULL_CONTROL='+str(2 if args.full_reduced else int(args.full))+';\n')
    f.write('DATA='+json.dumps(data,separators=(',',':'))+';\n')
print(f'Staged {len(data)} certificates; algebra verification remains required.')
