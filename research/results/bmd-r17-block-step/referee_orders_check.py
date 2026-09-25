import random, sys
MOD=0b1000011  # x^6+x+1
def mul(a,b):
    r=0
    while b:
        if b&1: r^=a
        b>>=1; a<<=1
        if a&64: a^=MOD
    return r
def pw(a,e):
    r=1
    while e:
        if e&1: r=mul(r,a)
        a=mul(a,a); e>>=1
    return r
def inv(a): return pw(a,62)
al=2
S=[0,1,al,al^1]
# L coefficients: product (x-t)
poly=[1]
for t in S:
    new=[0]*(len(poly)+1)
    for i,c in enumerate(poly):
        new[i+1]^=c; new[i]^=mul(c,t)
    poly=new
assert poly[3]==0 and poly[0]==0 and poly[4]==1
c0,c1=poly[1],poly[2]; assert c1!=0
N=48
a=[inv(c0)]
for u in range(1,7):
    s=mul(c1,pw(a[u-1],2))
    if u>=2: s^=pw(a[u-2],4)
    a.append(mul(inv(c0),s))
def pmul(p,q):
    r=[0]*N
    for i,x in enumerate(p):
        if x:
            for j,y in enumerate(q[:N-i]):
                if y: r[i+j]^=mul(x,y)
    return r
def H(m): return 2*(m//8)+(-(-(m%8)//2))
def run(y1,y2,D):
    z=[]
    for y in (y1,y2):
        v=[0]*N
        for u,au in enumerate(a):
            if 2**u<N: v[2**u]^=mul(au,pw(y,2**u))
        z.append(v)
    # check L(z)=yT
    for i,y in enumerate((y1,y2)):
        z2=pmul(z[i],z[i]); z4=pmul(z2,z2)
        Lz=[z4[j]^mul(c1,z2[j])^mul(c0,z[i][j]) for j in range(N)]
        assert Lz[1]==y and all(Lz[j]==0 for j in range(N) if j!=1 and j<2**7), Lz[:10]
    P1=[[1]+[0]*(N-1)]
    for e in range(1,D+1): P1.append(pmul(P1[-1],z[0]))
    P2=[[1]+[0]*(N-1)]
    for e in range(1,D+1): P2.append(pmul(P2[-1],z[1]))
    out=[]
    for d in range(D+1):
        rows=[pmul(P1[i],P2[j]) for i in range(d+1) for j in range(d+1-i)]
        piv={}
        for r in rows:
            r=r[:]
            while True:
                o=next((j for j,x in enumerate(r) if x),None)
                if o is None or o not in piv: break
                p=piv[o]; f=mul(r[o],inv(p[o]))
                r=[x^mul(f,y) for x,y in zip(r,p)]
            if o is not None: piv[o]=r
        out.append(sorted(piv))
    return out
random.seed(1)
D=5
good=0
for trial in range(20):
    y1=random.randrange(1,64); y2=random.randrange(1,64)
    if y1==y2: continue
    o=run(y1,y2,D)
    ok=all(o[d]==[m for m in range(60) if H(m)<=d] for d in range(D+1))
    good+=ok
    print(y1,y2,ok,[len(x) for x in o], o[D] if not ok else '')
print('pred',[[m for m in range(60) if H(m)<=d] for d in range(D+1)][D])
print('count check',all(sum(1 for m in range(1000) if H(m)<=d)==( (d+2)*(d+1)//2 - (max(d-2,0)*max(d-3,0)//2)) for d in range(41)))
