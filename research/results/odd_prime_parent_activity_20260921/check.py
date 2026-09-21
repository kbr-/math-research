"""A finite dual witness showing that the larger retained cutoff is necessary."""
import itertools,json
from pathlib import Path
import numpy as np
p=3
points=np.array(list(itertools.product((0,1),repeat=4)),dtype=np.int64)
x,y,u,v=points.T
g=(x*y+u*v)%p; g2=g*g%p
A=np.vstack((np.ones(16,dtype=np.int64),g2,points.T*g2,g))%p
b=np.array([1,0,0,0,0,0,1],dtype=np.int64)
aug=np.column_stack((A,b)); row=0;pivots=[]
for col in range(16):
 q=np.flatnonzero(aug[row:,col])
 if not len(q):continue
 i=row+int(q[0]);aug[[row,i]]=aug[[i,row]]
 aug[row]=aug[row]*pow(int(aug[row,col]),-1,p)%p
 for j in range(len(aug)):
  if j!=row:aug[j]=(aug[j]-aug[j,col]*aug[row])%p
 pivots.append(col);row+=1
 if row==len(aug):break
assert not any(not np.any(r[:-1]) and r[-1] for r in aug)
weights=np.zeros(16,dtype=np.int64)
for j,c in enumerate(pivots):weights[c]=aug[j,-1]
assert np.array_equal(A@weights%p,b)
# Test whether an affine cofactor can represent G modulo Booleanity.
M=(points.T*g2).T
C=np.column_stack((g2,M));has=False
for coeff in itertools.product(range(3),repeat=5):
 if np.array_equal(C@np.array(coeff,dtype=np.int64)%3,g):has=True;break
assert not has
out={'field':3,'variables':['x','y','u','v'],'G':'xy+uv','old_extra_axiom':'G^2',
 'point_weights':[{'point':pt.tolist(),'weight':int(w)} for pt,w in zip(points,weights)],
 'moments_order':['1','G^2','xG^2','yG^2','uG^2','vG^2','G'],
 'moments':(A@weights%p).tolist(),'affine_cofactor_candidates':3**5,
 'affine_cofactor_exists':has,
 'scope':'Weights annihilate every original degree-five old NS generator multiple, but evaluate G to one. A singleton parent derives G through five. The general positive lift is proved separately.'}
Path(__file__).with_name('checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
