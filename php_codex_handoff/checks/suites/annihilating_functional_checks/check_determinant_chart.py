"""Check the fixed-pivot rational functional itself, not just linear solvability."""
import sys,json
sys.path.insert(0,'/mnt/data/research_work')
from check_generic_functional import basis_and_relations,solve_exact
import numpy as np
from numba import njit

@njit(cache=True)
def pivots(a,p):
    A=a.copy(); nr,nc=A.shape; r=0
    J=np.empty(min(nr,nc),dtype=np.int64)
    for c in range(nc):
        pr=-1
        for i in range(r,nr):
            if A[i,c]:pr=i;break
        if pr<0:continue
        for j in range(c,nc):
            tmp=A[pr,j];A[pr,j]=A[r,j];A[r,j]=tmp
        aa=int(A[r,c]);bb=p;u=1;v=0
        while bb:
            q=aa//bb;aa,bb=bb,aa-q*bb;u,v=v,u-q*v
        inv=u%p
        for j in range(c,nc):A[r,j]=(A[r,j]*inv)%p
        for i in range(r+1,nr):
            f=A[i,c]
            if f:
                for j in range(c+1,nc):A[i,j]=(A[i,j]-f*A[r,j])%p
                A[i,c]=0
        J[r]=c;r+=1
        if r==nr:break
    return J[:r]

@njit(cache=True)
def determinant(a,p):
    A=a.copy(); n=A.shape[0]; det=1
    for c in range(n):
        pr=-1
        for i in range(c,n):
            if A[i,c]:pr=i;break
        if pr<0:return 0
        if pr!=c:
            det=(-det)%p
            for j in range(c,n):
                tmp=A[pr,j];A[pr,j]=A[c,j];A[c,j]=tmp
        f=int(A[c,c]);det=(det*f)%p
        aa=f;bb=p;u=1;v=0
        while bb:
            q=aa//bb;aa,bb=bb,aa-q*bb;u,v=v,u-q*v
        inv=u%p
        for i in range(c+1,n):
            factor=(A[i,c]*inv)%p
            for j in range(c+1,n):A[i,j]=(A[i,j]-factor*A[c,j])%p
            A[i,c]=0
    return det

n=4;t=1;p=101
M0,v,*_=basis_and_relations(n,t,p,'seed',0)
J=pivots(M0,p); G0=np.column_stack((M0[:,J],v))
R=pivots(G0.T,p)
result=[]
for mode,seed in [('seed',0),('random',4711),('random',8821)]:
    M,v,*_=basis_and_relations(n,t,p,mode,seed)
    W=np.column_stack((M[np.ix_(R,J)],v[R]))
    Delta=int(determinant(W,p)); verified=False
    if Delta:
        eq=np.column_stack((W.T,np.eye(len(R),dtype=np.int64)[:,-1]))
        ok,rank,w=solve_exact(eq,p)
        lam=np.zeros(len(v),dtype=np.int64);lam[R]=w
        verified=bool(ok and rank==len(R) and np.all(lam@M%p==0) and int(lam@v%p)==1)
    result.append({'n':n,'t':t,'d':2,'p':p,'mode':mode,'seed':seed,
        'rank_at_seed':len(J),'minor_size':len(R),'Delta':Delta,'formula_verified':verified})
print(json.dumps(result,indent=2))
json.dump(result,open('/mnt/data/research_work/determinant_chart_checks.json','w'),indent=2)
