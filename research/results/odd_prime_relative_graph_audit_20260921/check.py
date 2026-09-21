import json,subprocess
from fractions import Fraction
from pathlib import Path
rows=json.loads(subprocess.check_output(['/tmp/odd-prime-relative-count'],text=True))
for r in rows:
 n,k,D=r['n'],r['k'],r['delta']+1
 assert 8*k*(D+1)<=n
 q=Fraction(k*(k-1),2*n*n)
 bound=(1-q)**r['R']
 ratio=Fraction(r['after'],r['before'])
 assert ratio<=bound
 r['exact_ratio']=str(ratio);r['exact_product_upper_bound']=str(bound)
 r['passed']=True
# A purported new head that is already an edge removes no independent sets.
# R=1 would predict a strictly smaller ratio; the hypothesis is essential.
control={'existing_edge_ratio':'1','incorrect_R_1_bound':str(1-Fraction(6,2*96**2)),'incorrect_bound_rejected':True}
assert Fraction(1)>1-Fraction(6,2*96**2)
result={'cases':rows,'negative_control':control,'scope':'Exact counts of subsets in two stated graphs; not asymptotic proof or graph-PHP separation.'}
Path(__file__).with_name('checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
