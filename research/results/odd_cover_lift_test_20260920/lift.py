import itertools,json
from pathlib import Path
import numpy as np
normals=[tuple((s*np.array(a))%3) for a in [(1,0),(0,1),(1,1),(1,2)] for s in [1,2]]
gadget=[(0,0,1),(1,0,1),(1,0,2),(1,1,2),(1,2,2),(2,0,1)]
reports=[]
for n in range(2,6):
 pts=np.array([a for a in itertools.product(range(3),repeat=n) if any(a)],dtype=np.int64)
 normals=[tuple(int(v) for v in a) for a in normals]
 cov=(pts@np.array(normals).T%3==1).sum(axis=1);assert np.min(cov)>=3
 pairs=[a for a in sorted(set(normals)) if next(x for x in a if x)==1 and tuple((-np.array(a))%3) in normals]
 reports.append(dict(n=n,planes=len(normals),normal_list=[list(a) for a in normals],coverage=cov.tolist(),scalar_pairs=len(pairs)))
 if n==5:break
 u,v=pairs[:2]
 for a in [u,v,tuple((-np.array(u))%3),tuple((-np.array(v))%3)]:normals.remove(a)
 normals=[a+(0,) for a in normals]+[tuple((a*np.array(u)+b*np.array(v))%3)+(t,) for a,b,t in gadget]
Path(__file__).with_name('lifted-covers.json').write_text(json.dumps(reports,indent=2)+'\n');print([(r['n'],r['planes'],r['scalar_pairs']) for r in reports])
