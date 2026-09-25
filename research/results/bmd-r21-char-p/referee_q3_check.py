import random, itertools
p,a=3,5; q=3; n=2
def pmod(A,M):
    A=A[:]
    while len(A)>=len(M):
        c=A[-1]
        if c:
            sh=len(A)-len(M)
            for i,m in enumerate(M): A[sh+i]=(A[sh+i]-c*m)%p
        A.pop()
    return A
def irreducible(M):
    for c in itertools.product(range(p),repeat=2):
        f=[c[0],c[1],1]
        if not any(pmod(M,f)): return False
    for r0 in range(p):
        if sum(M[i]*r0**i for i in range(len(M)))%p==0: return False
    return True
for c in itertools.product(range(p),repeat=5):
    M=list(c)+[1]
    if c[0] and irreducible(M): break
def mul(A,B):
    R=[0]*(2*a-1)
    for i,x in enumerate(A):
        if x:
            for j,y in enumerate(B): R[i+j]=(R[i+j]+x*y)%p
    R=pmod(R,M); return tuple(R+[0]*(a-len(R)))
def add(A,B): return tuple((x+y)%p for x,y in zip(A,B))
def neg(A): return tuple((-x)%p for x in A)
Z=tuple([0]*a); ONE=tuple([1]+[0]*(a-1))
def pw(A,e):
    R=ONE
    while e:
        if e&1: R=mul(R,A)
        A=mul(A,A); e>>=1
    return R
def inv(A): return pw(A,p**a-2)
N=60
def smul(F,G):
    R=[Z]*N
    for i,x in enumerate(F):
        if x!=Z:
            for j in range(N-i):
                if G[j]!=Z: R[i+j]=add(R[i+j],mul(x,G[j]))
    return R
def orders(vecs):
    piv={}
    for r in vecs:
        r=list(r)
        while True:
            lead=next((i for i,x in enumerate(r) if x!=Z),None)
            if lead is None: break
            if lead in piv:
                b=piv[lead]; c=mul(r[lead],inv(b[lead]))
                r=[add(x,neg(mul(c,y))) for x,y in zip(r,b)]
            else: piv[lead]=r; break
    return set(piv)
def s3(m):
    t=0
    while m: t+=m%3; m//=3
    return t
H=lambda m:3*(m//9)+s3(m%9)
print("modulus",M)
for trial in range(3):
    ys=[tuple(random.randrange(p) for _ in range(a)) for _ in range(n)]
    zs=[]
    for y in ys:
        z=[Z]*N; u=0
        while 3**u<N: z[3**u]=neg(pw(y,3**u)); u+=1
        zs.append(z)
    z=zs[0]; z3=smul(smul(z,z),z); L=[add(x,neg(w)) for x,w in zip(z3,z)]
    assert L[1]==ys[0] and all(L[i]==Z for i in range(N) if i!=1)
    for d in range(0,5):
        vecs=[]
        for e in itertools.product(range(d+1),repeat=n):
            if sum(e)<=d:
                v=[ONE]+[Z]*(N-1)
                for i,ei in enumerate(e):
                    for _ in range(ei): v=smul(v,zs[i])
                vecs.append(v)
        o=orders(vecs); pred={m for m in range(N) if H(m)<=d}
        print(trial,ys,d,o==pred,sorted(o))
