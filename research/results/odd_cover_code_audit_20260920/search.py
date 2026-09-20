import itertools,json
from pathlib import Path
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
reports=[]
for n in [3,4]:
 points=np.array([x for x in itertools.product(range(3),repeat=n) if any(x)],dtype=np.int64)
 incidence=(points@points.T%3==1).astype(np.int64);budget=2*n+4
 result=milp(np.ones(len(points)),integrality=np.ones(len(points)),bounds=Bounds(0,3),constraints=[LinearConstraint(incidence,3,np.inf),LinearConstraint(np.ones((1,len(points))),0,budget)],options={'time_limit':35,'mip_rel_gap':0})
 report=dict(q=3,n=n,budget=budget,solver_status=int(result.status),message=result.message,scope='Solver searches only; reported integer witnesses are checked exactly. Infeasibility is not a proof certificate.')
 if result.x is not None:
  counts=np.rint(result.x).astype(np.int64)
  assert np.max(np.abs(result.x-counts))<1e-5
  assert np.all(counts>=0) and counts.sum()<=budget
  coverage=incidence@counts;assert np.all(coverage>=3)
  paired=all(counts[i]==counts[np.flatnonzero(np.all(points==(-a)%3,axis=1))[0]] for i,a in enumerate(points))
  report.update(planes=int(counts.sum()),normal_counts=[dict(normal=a.tolist(),count=int(c)) for a,c in zip(points,counts) if c],coverage=coverage.tolist(),scalar_paired=paired,exactly_verified=True)
 reports.append(report)
out=Path(__file__).with_name('search.json');out.write_text(json.dumps(reports,indent=2)+'\n');print(json.dumps([{k:v for k,v in r.items() if k not in ['normal_counts','coverage']} for r in reports],indent=2))
