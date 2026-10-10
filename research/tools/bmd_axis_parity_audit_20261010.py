"""Stage a complete one-root parity certificate for independent PARI replay."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--input',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args()
d=json.loads(a.input.read_text())
assert d['status']=='certified'
data=[d[k] for k in ['cube_dimension','prime','field_degree','modulus','intercept','direction','original_degree_bound','bound_penalty','norm_determinant','norm_adjacent_minor','norm_vandermonde','gcd']]
data.append([[v['replaced_column'],v['norm']] for v in d['additional_norm_minors']])
with a.out.open('x') as f:f.write('DATA='+json.dumps(data,separators=(',',':'))+';\n')
print('Staged full certificate; independent polynomial verification still required.')
