import importlib.util,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('jets',ROOT/'research/results/odd_cover_source_audit_20260920/check_jets.py');j=importlib.util.module_from_spec(spec);spec.loader.exec_module(j)
rows=[]
for r in json.loads((ROOT/'research/results/odd_cover_lift_test_20260920/lifted-covers.json').read_text()):
 A=np.array(r['normal_list'],dtype=np.int64)
 assert np.all(A.sum(axis=0)%3==0) and np.all(A.T@A%3==0)
 assert j.rank(A,j.tables(3))==r['n']
 rows.append(dict(n=r['n'],m=len(A),sum_zero=True,gram_zero=True,rank=r['n']))
controls=[]
for t in [3,4,5]:
 U=np.array([1,1,1,0]);V=np.array([0,1,2,1]);vectors=[]
 for W in [U,V]:
  for i in range(t-1):
   a=np.zeros(4*t,dtype=np.int64);a[4*i:4*i+4]=W;a[-4:]=(-W)%3;vectors.append(a)
 G=np.array(vectors,dtype=np.int64)
 target=np.zeros(4*t,dtype=np.int64)
 for i in range(3):target[4*i:4*i+4]=U
 assert np.all(G@G.T%3==0) and np.all(G.sum(axis=1)%3==0) and np.all(np.any(G!=0,axis=0))
 rank=j.rank(G,j.tables(3));assert rank==2*t-2 and j.rank(np.concatenate([G,target[None,:]]),j.tables(3))==rank
 assert set(target)<=set([0,1]) and target.any()
 controls.append(dict(t=t,n=rank,m=4*t,generator=G.tolist(),nonzero_binary_word=target.tolist(),full_support=True,gram_zero=True,sum_zero=True))
result=dict(passed=True,witness_moment_checks=rows,infinite_family_controls=controls,scope='Exact checks of new moment consequences and the explicit control; general proofs are in the notebook.')
Path(__file__).with_name('checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,cover_cases=len(rows),control_cases=len(controls))))
