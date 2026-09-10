"""Exact finite-field checks; vectorized assembly, compiled elimination, parallel cases."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from concurrent.futures import ProcessPoolExecutor
import json, time
import numpy as np
from numba import njit

@njit(cache=True)
def solve_exact(a, p):
    """Solve Ax=b in F_p; use compiled modular elimination, no float ranks."""
    mat=a.copy()
    nr,nc=mat.shape
    nv=nc-1
    pivots=np.empty(min(nr,nv),dtype=np.int64)
    rank=0
    for col in range(nv):
        pr=-1
        for r in range(rank,nr):
            if mat[r,col] != 0:
                pr=r; break
        if pr<0:
            continue
        if pr!=rank:
            for j in range(col,nc):
                tmp=mat[pr,j]; mat[pr,j]=mat[rank,j]; mat[rank,j]=tmp
        # Prime-field inverse via integer Euclid.
        aa=int(mat[rank,col]); bb=p; u=1; v=0
        while bb:
            q=aa//bb; aa,bb=bb,aa-q*bb; u,v=v,u-q*v
        inv=u%p
        for j in range(col,nc):
            mat[rank,j]=(mat[rank,j]*inv)%p
        for r in range(nr):
            if r==rank:
                continue
            f=mat[r,col]
            if f:
                for j in range(col+1,nc):
                    mat[r,j]=(mat[r,j]-f*mat[rank,j])%p
                mat[r,col]=0
        pivots[rank]=col
        rank+=1
        if rank==nr:
            break
    for r in range(rank,nr):
        if mat[r,nv]!=0:
            return False,rank,np.zeros(nv,dtype=np.int64)
    sol=np.zeros(nv,dtype=np.int64)
    for r in range(rank):
        sol[pivots[r]]=mat[r,nv]
    return True,rank,sol

def basis_and_relations(n, t, p, mode, seed):
    m=n+1; q=m*n
    a,b=np.triu_indices(q)
    keep=(a==b)|((a%n)!=(b%n))
    a,b=a[keep],b[keep]
    N=len(a)
    mult=np.full((q,q),-1,dtype=np.int64)
    mult[a,b]=np.arange(N); mult[b,a]=np.arange(N)
    forms=np.zeros((n+t,q),dtype=np.int64)
    for i in range(1,m):
        forms[i-1,:n]=-1
        forms[i-1,i*n:(i+1)*n]=1
    if mode=='seed':
        for s in range(t):
            forms[n+s,s::n]=1
    elif mode=='two_row_collision':
        forms[n,1:n]=1
        forms[n+1,n+1:2*n]=1
    else:
        forms[n:]=np.random.default_rng(seed).integers(0,p,size=(t,q))
    forms%=p
    va,vb=np.where(mult>=0)
    rr=mult[va,vb]
    cc=np.arange(n+t)[:,None]*q+vb[None,:]
    M=np.zeros((N,(n+t)*q),dtype=np.int64)
    M[rr[None,:],cc]=forms[:,va]
    z2=np.where((a<n)&(b<n),np.where(a==b,1,2),0)%p
    return M,z2,forms,a,b

def case(args):
    n,t,p,mode,seed=args
    start=time.perf_counter()
    M,v,forms,a,b=basis_and_relations(n,t,p,mode,seed)
    mat=np.zeros((M.shape[1]+1,M.shape[0]+1),dtype=np.int64)
    mat[:-1,:-1]=M.T
    mat[-1,:-1]=v; mat[-1,-1]=1
    ok,rank,lam=solve_exact(mat,p)
    verified=bool(ok and np.all((lam@M)%p==0) and int(lam@v%p)==1)
    # Independent reconstruction of a symmetric moment matrix.
    q=n*(n+1)
    T=np.zeros((q,q),dtype=np.int64)
    T[a,b]=lam; T[b,a]=lam
    independent=bool(ok and np.all((forms@T)%p==0) and int(T[:n,:n].sum()%p)==1)
    H2=(n*(n-1)//2)*n*n-t*n*n+t*(t-1)//2
    expected=M.shape[0]-H2
    return {'n':n,'d':2,'t':t,'p':p,'mode':mode,'seed':seed,
            'feasible':bool(ok),'verified':verified,'independent_moment_check':independent,'relation_rank':int(rank-1) if ok else None,
            'predicted_max_rank':expected,'nonzero_lambda_entries':int(np.count_nonzero(lam)),
            'seconds':round(time.perf_counter()-start,3)}

if __name__=='__main__':
    # Compile once; children reuse the compiled cache.
    solve_exact(np.array([[1,1]],dtype=np.int64),3)
    cases=[(n,n-3,p,mode,seed)
        for n in (4,5,6)
        for p in (2,3,101)
        for mode,seed in (('seed',0),('random',4711),('random',8821))]
    cases += [(5,2,p,'two_row_collision',0) for p in (2,3,101)]
    with ProcessPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(case,cases))
    path='/mnt/data/research_work/generic_functional_checks.json'
    with open(path,'w') as f: json.dump(results,f,indent=2)
    print(json.dumps(results,indent=2))
    print('verified',sum(r['verified'] for r in results),'/',len(results))
    print('ranks match',sum(r['relation_rank']==r['predicted_max_rank'] for r in results),'/',len(results))
