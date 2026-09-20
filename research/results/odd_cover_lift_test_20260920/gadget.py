import itertools,json
from pathlib import Path
import numpy as np
from scipy.optimize import milp,linprog,Bounds,LinearConstraint
points=np.array(list(itertools.product(range(3),repeat=3)),dtype=np.int64)
normals=np.array([a for a in itertools.product(range(3),repeat=3) if a[2]],dtype=np.int64)
A=(points@normals.T%3==1).astype(np.int64)
need=np.count_nonzero(points[:,:2],axis=1);need[(points[:,0]==0)&(points[:,1]==0)&(points[:,2]!=0)]=3
result=milp(np.ones(len(normals)),integrality=np.ones(len(normals)),bounds=Bounds(0,6),constraints=[LinearConstraint(A,need,np.inf),LinearConstraint(np.ones((1,len(normals))),0,6)],options={'time_limit':30})
report=dict(status=int(result.status),message=result.message,points=points.tolist(),normals=normals.tolist(),requirements=need.tolist())
if result.x is not None:
 x=np.rint(result.x).astype(np.int64);assert np.max(abs(result.x-x))<1e-5;assert x.sum()<=6 and np.all(A@x>=need)
 report.update(witness=x.tolist(),coverage=(A@x).tolist(),exactly_verified=True)
else:
 lp=linprog(np.ones(len(normals)),A_ub=-A,b_ub=-need,bounds=(0,None),method='highs')
 report.update(lp_status=int(lp.status),lp_minimum=None if lp.fun is None else float(lp.fun),lp_dual=None if lp.fun is None else (-lp.ineqlin.marginals).tolist())
Path(__file__).with_name('gadget.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['points','normals','requirements','coverage','lp_dual']},indent=2))
