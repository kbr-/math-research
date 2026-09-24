# Brute force delta_q(n,k,l): least degree of P over F_q, Hasse mult >=k at nonzero pts, exactly l at 0.
import numpy as np, itertools, sys
from math import comb
def field(q):
    if q in (2,3,5,7):
        add=np.array([[(a+b)%q for b in range(q)] for a in range(q)],dtype=np.int8)
        mul=np.array([[(a*b)%q for b in range(q)] for a in range(q)],dtype=np.int8)
        p=q
    elif q==4:
        add=np.array([[a^b for b in range(4)] for a in range(4)],dtype=np.int8)
        def m(a,b):
            r=0
            for i in range(2):
                if b>>i&1: r^=a<<i
            if r&4: r^=0b111
            return r
        mul=np.array([[m(a,b) for b in range(4)] for a in range(4)],dtype=np.int8); p=2
    elif q==9:
        def dec(x): return x%3,x//3
        def enc(a,b): return a%3+3*(b%3)
        add=np.array([[enc(dec(x)[0]+dec(y)[0],dec(x)[1]+dec(y)[1]) for y in range(9)] for x in range(9)],dtype=np.int8)
        def m(x,y):
            a,b=dec(x);c,d=dec(y); return enc(a*c-b*d,a*d+b*c)
        mul=np.array([[m(x,y) for y in range(9)] for x in range(9)],dtype=np.int8); p=3
    neg=np.array([ [b for b in range(q) if add[a,b]==0][0] for a in range(q)],dtype=np.int8)
    inv=np.array([0]+[[b for b in range(q) if mul[a,b]==1][0] for a in range(1,q)],dtype=np.int8)
    return add,mul,neg,inv,p
def rank(A,F):
    add,mul,neg,inv,p=F
    A=A.copy(); r=0; R,C=A.shape
    for c in range(C):
        if r==R: break
        piv=np.nonzero(A[r:,c])[0]
        if len(piv)==0: continue
        pr=r+piv[0]; A[[r,pr]]=A[[pr,r]]
        A[r]=mul[inv[A[r,c]],A[r]]
        rows=np.nonzero(A[:,c])[0]; rows=rows[rows!=r]
        if len(rows):
            f=neg[A[rows,c]]
            A[rows]=add[A[rows],mul[f[:,None],A[r][None,:]]]
        r+=1
    return r
def fpow(a,e,F):
    add,mul,neg,inv,p=F; r=1
    for _ in range(e): r=mul[r,a]
    return int(r)
def intel(b,F):
    add=F[0]; be=0
    for _ in range(b): be=add[be,1]
    return be
def conds(n,k,D,q,F,pts_k,l0):
    add,mul,neg,inv,p=F
    mons=[m for d in range(D+1) for m in itertools.product(range(d+1),repeat=n) if sum(m)==d]
    def rowfor(a,beta):
        row=[]
        for al in mons:
            if any(al[i]<beta[i] for i in range(n)): row.append(0);continue
            c=1
            for i in range(n):
                c=mul[c,intel(comb(al[i],beta[i])%p,F)]; c=mul[c,fpow(a[i],al[i]-beta[i],F)]
            row.append(int(c))
        return row
    betas=lambda K:[b for d in range(K) for b in itertools.product(range(d+1),repeat=n) if sum(b)==d]
    rows=[rowfor(a,b) for a in pts_k for b in betas(k)]
    base=np.array(rows,dtype=np.int8).reshape(-1,len(mons))
    o=tuple([0]*n)
    r1=np.array([rowfor(o,b) for b in betas(l0)],dtype=np.int8).reshape(-1,len(mons))
    r2=np.array([rowfor(o,b) for b in betas(l0+1)],dtype=np.int8).reshape(-1,len(mons))
    return rank(np.vstack([base,r1]),F)<rank(np.vstack([base,r2]),F)
def s_q(m,q):
    s=0
    while m: s+=m%q; m//=q
    return s
def Phi(n,k,l,q):
    return n*(q-1)+q*l+(q-1)*sum((k-l-1)//q**j for j in range(n))
if __name__=="__main__":
    q=int(sys.argv[1]); n=int(sys.argv[2]); K=int(sys.argv[3]); kmin=int(sys.argv[4]) if len(sys.argv)>4 else 1
    F=field(q)
    pts=[a for a in itertools.product(range(q),repeat=n) if any(a)]
    for k in range(kmin,K+1):
        for l in range(k):
            ph=Phi(n,k,l,q)
            m=k-l-1;Q,r=divmod(m,q**n); h=q*Q+s_q(r,q)
            assert ph==n*(q-1)+q*(k-1)-h
            ok_hi=conds(n,k,ph,q,F,pts,l); ok_lo=conds(n,k,ph-1,q,F,pts,l)
            print(q,n,k,l,ph,ok_hi,ok_lo,'OK' if ok_hi and not ok_lo else 'MISMATCH',flush=True)
