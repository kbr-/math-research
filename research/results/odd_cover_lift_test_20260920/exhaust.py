import itertools,json,math
from pathlib import Path
import numpy as np
reports=[]
for n in [2,3]:
 pts=np.array(list(itertools.product(range(3),repeat=n)),dtype=np.int64)
 normals=np.array([a for a in itertools.product(range(3),repeat=n) if a[-1]],dtype=np.int64)
 A=(pts@normals.T%3==1).astype(np.int64)
 need=(2*(pts[:,0]!=0) if n==2 else np.count_nonzero(pts[:,:2],axis=1))
 need[np.all(pts[:,:-1]==0,axis=1)&(pts[:,-1]!=0)]=3
 pairs=[(i,int(np.flatnonzero(np.all(normals==(-a)%3,axis=1))[0])) for i,a in enumerate(normals) if a[-1]==1]
 stream=itertools.combinations_with_replacement(range(len(normals)),6);seen=0;valid=[];pair_counts=[]
 while True:
  batch=list(itertools.islice(stream,8192))
  if not batch:break
  idx=np.array(batch,dtype=np.int64);seen+=len(idx)
  coverage=A[:,idx].sum(axis=2).T
  good=idx[np.all(coverage>=need,axis=1)]
  if len(good):
   counts=np.stack([(good==j).sum(axis=1) for j in range(len(normals))],axis=1)
   b=sum(np.minimum(counts[:,i],counts[:,j]) for i,j in pairs)
   valid.extend(good.tolist());pair_counts.extend(b.tolist())
 assert seen==math.comb(len(normals)+5,6)
 if n==3:assert max(pair_counts)==1
 else:assert len(valid)==1 and valid[0]==list(range(6))
 reports.append(dict(independent_inputs=n-1,candidates=seen,normal_order=normals.tolist(),valid_gadgets=valid,paired_bundles=pair_counts,maximum_paired_bundles=max(pair_counts)))
Path(__file__).with_name('exhaustive.json').write_text(json.dumps(dict(passed=True,cases=reports),indent=2)+'\n');print(json.dumps([{k:v for k,v in r.items() if k not in ['normal_order','valid_gadgets','paired_bundles']}|{'valid_count':len(r['valid_gadgets'])} for r in reports],indent=2))
