# brute force delta_S(n=2,k,l) over GF(8), mod x^3+x+1, S={0,1,2,3}
from math import comb
MOD=0b1011
def mul(a,b):
    r=0
    while b:
        if b&1: r^=a
        b>>=1; a<<=1
        if a&8: a^=MOD
    return r
def inv(a):
    for b in range(1,8):
        if mul(a,b)==1: return b
def pw(a,e):
    r=1
    for _ in range(e): r=mul(r,a)
    return r
S=[0,1,2,3]
def reduce(r,piv,N):
    for c in range(N):
        if r[c] and c in piv:
            p=piv[c]; f=r[c]; r=[x^mul(f,y) for x,y in zip(r,p)]
    return r
def echelon(rows,N):
    piv={}
    for r in rows:
        r=reduce(r[:],piv,N)
        for c in range(N):
            if r[c]:
                f=inv(r[c]); piv[c]=[mul(f,x) for x in r]; break
    return piv
def feasible(D,k,l):
    mons=[(i,j) for i in range(D+1) for j in range(D+1-i)]
    N=len(mons); rows=[]
    for a in S:
        for b in S:
            if a==0 and b==0: continue
            for u in range(k):
                for v in range(k-u):
                    rows.append([(mul(pw(a,i-u),pw(b,j-v)) if (i>=u and j>=v and comb(i,u)%2 and comb(j,v)%2) else 0) for (i,j) in mons])
    for idx,(i,j) in enumerate(mons):
        if i+j<l:
            r=[0]*N; r[idx]=1; rows.append(r)
    piv=echelon(rows,N)
    for idx,(i,j) in enumerate(mons):
        if i+j==l:
            r=[0]*N; r[idx]=1
            if any(reduce(r,piv,N)): return True
    return False
for k in (3,4):
    l=k-3; D=l
    while not feasible(D,k,l): D+=1
    print("k",k,"l",l,"delta",D,"expected",2*3+4*(k-1)-1, flush=True)
