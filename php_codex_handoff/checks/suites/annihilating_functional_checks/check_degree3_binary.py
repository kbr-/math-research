"""Degree-three checks over F2; bit-packed compiled linear algebra, parallel instances."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations_with_replacement, permutations
import json,time
import numpy as np
from numba import njit

@njit(cache=True)
def parity(x):
    x ^= x >> np.uint64(32)
    x ^= x >> np.uint64(16)
    x ^= x >> np.uint64(8)
    x ^= x >> np.uint64(4)
    x ^= x >> np.uint64(2)
    x ^= x >> np.uint64(1)
    return int(x & np.uint64(1))

@njit(cache=True)
def binary_solve(a, nv):
    mat=a.copy(); nr,nw=mat.shape
    piv=np.empty(min(nr,nv),dtype=np.int64)
    rank=0
    for col in range(nv):
        word=col//64; mask=np.uint64(1)<<np.uint64(col%64)
        pr=-1
        for r in range(rank,nr):
            if mat[r,word]&mask:
                pr=r;break
        if pr<0: continue
        if pr!=rank:
            for w in range(word,nw):
                tmp=mat[pr,w];mat[pr,w]=mat[rank,w];mat[rank,w]=tmp
        for r in range(rank+1,nr):
            if mat[r,word]&mask:
                for w in range(word,nw): mat[r,w]^=mat[rank,w]
        piv[rank]=col;rank+=1
        if rank==nr:break
    rhsword=nv//64; rhsmask=np.uint64(1)<<np.uint64(nv%64)
    for r in range(rank,nr):
        if mat[r,rhsword]&rhsmask:
            return False,rank,np.zeros(nw,dtype=np.uint64)
    sol=np.zeros(nw,dtype=np.uint64)
    for r in range(rank-1,-1,-1):
        acc=np.uint64(0)
        for w in range(piv[r]//64,nw):acc^=mat[r,w]&sol[w]
        bit=int(bool(mat[r,rhsword]&rhsmask))^parity(acc)
        if bit:sol[piv[r]//64]|=np.uint64(1)<<np.uint64(piv[r]%64)
    return True,rank,sol

@njit(cache=True)
def verify(a,sol,nv):
    for r in range(a.shape[0]):
        acc=np.uint64(0)
        for w in range(a.shape[1]):acc^=a[r,w]&sol[w]
        rhs=int((a[r,nv//64]>>np.uint64(nv%64))&np.uint64(1))
        if parity(acc)!=rhs:return False
    return True

def basis(n,d):
    q=n*(n+1)
    B=np.array(list(combinations_with_replacement(range(q),d)),dtype=np.int64)
    keep=np.ones(len(B),dtype=bool)
    for i in range(d):
        for j in range(i):keep&=(B[:,i]==B[:,j])|((B[:,i]%n)!=(B[:,j]%n))
    B=B[keep]
    keys=B@q**np.arange(d,dtype=np.int64)
    order=np.argsort(keys)
    return B[order],keys[order]

def case(args):
    n,t,mode,seed=args; start=time.perf_counter();d=3;p=2;m=n+1;q=m*n
    B,keys=basis(n,3);B2,_=basis(n,2);N=len(B);N2=len(B2)
    prod=np.empty((q,N2,3),dtype=np.int64)
    prod[:,:,0]=np.arange(q)[:,None];prod[:,:,1:]=B2[None,:,:]
    prod.sort(axis=2)
    valid=np.ones((q,N2),dtype=bool)
    for i in range(3):
        for j in range(i):valid&=(prod[:,:,i]==prod[:,:,j])|((prod[:,:,i]%n)!=(prod[:,:,j]%n))
    pkeys=prod@(q**np.arange(3,dtype=np.int64))
    ids=np.searchsorted(keys,pkeys)
    forms=np.zeros((n+t,q),dtype=np.uint8)
    for i in range(1,m):forms[i-1,:n]=1;forms[i-1,i*n:(i+1)*n]=1
    if mode=='seed':
        for s in range(t):forms[n+s,s::n]=1
    elif mode=='bad':forms[n:,:n]=1
    else:forms[n:]=np.random.default_rng(seed).integers(0,2,size=(t,q),dtype=np.uint8)
    nbits=64*((N+1+63)//64)
    dense=np.zeros(((n+t)*N2+1,nbits),dtype=np.uint8)
    vi,mu=np.where(valid)
    rr=np.arange(n+t)[:,None]*N2+mu[None,:]
    dense[rr,ids[vi,mu][None,:]]=forms[:,vi]
    z3=(np.all(B<n,axis=1)&((B[:,0]==B[:,1])|(B[:,1]==B[:,2]))).astype(np.uint8)
    dense[-1,:N]=z3;dense[-1,N]=1
    A=np.packbits(dense,axis=1,bitorder='little').view(np.uint64)
    del dense
    ok,rank,lam=binary_solve(A,N)
    verified=bool(ok and verify(A,lam,N))
    # Independent, uncompressed trilinear moment tensor checks.
    vals=np.unpackbits(lam.view(np.uint8),bitorder='little')[:N].astype(np.int64)
    T=np.zeros((q,q,q),dtype=np.int64)
    for perm in permutations(range(3)):
        T[B[:,perm[0]],B[:,perm[1]],B[:,perm[2]]]=vals
    independent=bool(ok and np.all((forms.astype(np.int64)@T.reshape(q,-1))%2==0) and int(T[:n,:n,:n].sum()%2)==1)
    # Coefficient of (1+n*u)^n(1-u)^t in degree 3.
    from math import comb
    H=sum((-1)**a*comb(t,a)*comb(n,3-a)*n**(3-a) for a in range(min(3,t)+1))
    return {'n':n,'d':3,'t':t,'p':2,'mode':mode,'seed':seed,
      'feasible':bool(ok),'verified':verified,'independent_moment_check':independent,'relation_rank':int(rank-1) if ok else int(rank),
      'predicted_generic_rank':N-H,'seconds':round(time.perf_counter()-start,3)}

if __name__=='__main__':
    binary_solve(np.array([[3]],dtype=np.uint64),1)
    verify(np.array([[3]],dtype=np.uint64),np.array([1],dtype=np.uint64),1)
    cases=[(6,1,'seed',0),(6,1,'random',4711),(6,1,'random',8821),(6,1,'bad',0)]
    with ProcessPoolExecutor(max_workers=4) as pool:out=list(pool.map(case,cases))
    with open('/mnt/data/research_work/degree3_binary_checks.json','w') as f:json.dump(out,f,indent=2)
    print(json.dumps(out,indent=2))
