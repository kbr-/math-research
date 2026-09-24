# Brute force: least deg of P in F_p[x1,x2], Hasse mult >=k at (1,0),(0,1),(1,1), order exactly l at 0.
from math import comb
def rank(rows,p):
    rows=[r[:] for r in rows]; r=0
    if not rows: return 0
    ncol=len(rows[0])
    for c in range(ncol):
        piv=next((i for i in range(r,len(rows)) if rows[i][c]%p),None)
        if piv is None: continue
        rows[r],rows[piv]=rows[piv],rows[r]
        inv=pow(rows[r][c],p-2,p)
        rows[r]=[v*inv%p for v in rows[r]]
        for i in range(len(rows)):
            if i!=r and rows[i][c]%p:
                f=rows[i][c]; rows[i]=[(a-f*b)%p for a,b in zip(rows[i],rows[r])]
        r+=1
    return r
def hasse(g,b,a):
    return comb(g,b)*a**(g-b) if g>=b else 0
def delta(p,k,l):
    for d in range(0,2*k+2):
        mons=[(a,b) for a in range(d+1) for b in range(d+1-a)]
        A=[]
        for pt in [(1,0),(0,1),(1,1)]:
            for b1 in range(k):
                for b2 in range(k-b1):
                    A.append([hasse(g1,b1,pt[0])*hasse(g2,b2,pt[1])%p for g1,g2 in mons])
        for m0 in mons:
            if sum(m0)<l: A.append([1 if m==m0 else 0 for m in mons])
        B=A+[[1 if m==m0 else 0 for m in mons] for m0 in mons if sum(m0)==l]
        if rank(A,p)<rank(B,p): return d
    return None
bad=0; n=0
for p in [2,3,7]:
    for k in range(1,9):
        for l in range(k):
            m=k-l-1; t=2*k-(m+1)//2; d=delta(p,k,l); n+=1
            if d!=t: bad+=1; print("MISMATCH",p,k,l,d,t)
    print("done",p,flush=True)
print("cases",n,"mismatches",bad)
