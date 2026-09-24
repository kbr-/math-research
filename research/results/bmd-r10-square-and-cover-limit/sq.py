from math import comb
def rank(rows,p):
    rows=[r[:] for r in rows]; r=0
    ncol=len(rows[0]) if rows else 0
    for c in range(ncol):
        piv=None
        for i in range(r,len(rows)):
            if rows[i][c]%p: piv=i;break
        if piv is None: continue
        rows[r],rows[piv]=rows[piv],rows[r]
        inv=pow(rows[r][c],p-2,p)
        rows[r]=[x*inv%p for x in rows[r]]
        for i in range(len(rows)):
            if i!=r and rows[i][c]%p:
                f=rows[i][c]; rows[i]=[(a-f*b)%p for a,b in zip(rows[i],rows[r])]
        r+=1
    return r
def T(c): return 2*c-(c//2)  # ceil((c-1)/2) = floor(c/2)
def coef(a,b,i,j,u,v,p):
    if a<i or b<j: return 0
    return comb(a,i)*comb(b,j)*pow(u,a-i)*pow(v,b-j)%p
def mind(c,p):
    pts=[(1,0),(0,1),(1,1)]
    for d in range(0,3*c+3):
        mons=[(a,b) for a in range(d+1) for b in range(d+1-a)]
        rows=[[coef(a,b,i,j,u,v,p) for (a,b) in mons] for (u,v) in pts for i in range(c) for j in range(c-i)]
        e0=[1 if m==(0,0) else 0 for m in mons]
        if rank(rows+[e0],p)>rank(rows,p): return d
for p in (2,3,7):
    for c in range(1,10):
        print(p,c,mind(c,p),T(c),flush=True)
