import json
from pathlib import Path
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
r=json.loads(Path(__file__).with_name('gadget.json').read_text());pts=np.array(r['points']);normals=np.array(r['normals']);A=(pts@normals.T%3==1).astype(np.int64)
pairs=[(i,int(np.flatnonzero(np.all(normals==(-a)%3,axis=1))[0])) for i,a in enumerate(normals) if a[2]==1]
constraints=[LinearConstraint(np.pad(A,((0,0),(0,len(pairs)))),r['requirements'],np.inf),LinearConstraint(np.array([[1]*18+[0]*9]),0,6),LinearConstraint(np.array([[0]*18+[1]*9]),2,np.inf)]
for j,(a,b) in enumerate(pairs):
 for i in [a,b]:
  row=np.zeros(27);row[18+j]=1;row[i]=-1;constraints.append(LinearConstraint(row,-np.inf,0))
s=milp(np.array([1]*18+[0]*9),integrality=np.ones(27),bounds=Bounds(0,6),constraints=constraints,options={'time_limit':40})
report=dict(status=int(s.status),message=s.message,scope='At least two returned scalar pairs are required for repeatable use of the tested domination rule.')
if s.x is not None:
 x=np.rint(s.x).astype(int);assert max(abs(x-s.x))<1e-5
 assert x[:18].sum()<=6 and np.all(A@x[:18]>=r['requirements'])
 assert sum(min(x[a],x[b]) for a,b in pairs)>=2
 report.update(witness=x.tolist(),normals=normals.tolist(),coverage=(A@x[:18]).tolist(),exactly_verified=True)
Path(__file__).with_name('iterable.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
