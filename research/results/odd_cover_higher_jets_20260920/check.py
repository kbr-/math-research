import importlib.util,itertools,json,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('jets',ROOT/'research/results/odd_cover_source_audit_20260920/check_jets.py');j=importlib.util.module_from_spec(spec);spec.loader.exec_module(j)
rows=[]
for q,n in [(3,1),(3,2),(3,3),(5,2)]:
 field=j.tables(q);p,add,mul,neg,inv=field;k=3;d=n*(q-1)+2*(q-1)
 points=np.array(list(itertools.product(range(q),repeat=n)),dtype=np.int64)
 e=np.array(j.exponents(n,d),dtype=np.int64)
 powers=np.ones((q,d+1),dtype=np.int64)
 for t in range(1,d+1):powers[:,t]=mul[powers[:,t-1],np.arange(q)]
 blocks=[]
 for beta in j.exponents(n,k-1):
  values=np.ones((len(points),len(e)),dtype=np.int64)
  for i in range(n):
   coeff=np.array([math.comb(int(a),beta[i])%p if a>=beta[i] else 0 for a in e[:,i]])
   values=mul[values,mul[powers[points[:,i,None],np.maximum(e[None,:,i]-beta[i],0)],coeff[None,:]]]
  blocks.append(values)
 off=np.concatenate([v[1:] for v in blocks]);base=j.rank(off,field)
 value=np.ones((1,len(e)),dtype=np.int64)
 for i in range(n):value=mul[value,powers[0,e[None,:,i]]]
 extended=j.rank(np.concatenate([off,value]),field)
 assert extended==base+1
 rows.append(dict(q=q,n=n,k=k,degree=d,cover_target=n*(q-1)+2*q-1,columns=len(e),off_jet_rows=len(off),off_rank=base,rank_with_origin_value=extended))
out=Path(__file__).with_name('checks.json');out.write_text(json.dumps(dict(passed=True,scope='Exact finite polynomial-relaxation feasibility; no affine factorization tested.',cases=rows),indent=2)+'\n');print(out)
