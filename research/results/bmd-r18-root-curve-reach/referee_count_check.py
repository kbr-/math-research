from itertools import product
def N(s,n,d):
    return sum(1 for r in product(range(s),repeat=n) for Q in range(d+1) if s*Q+sum(r)<=d)
def sq(x,q):
    t=0
    while x: t+=x%q; x//=q
    return t
def Hq(m,q,n): Q,r=divmod(m,q**n); return q*Q+sq(r,q)
def H4(m): return 2*(m//8)+(-(-(m%8)//2))
ok=True
for (q,n) in [(2,1),(2,2),(2,3),(2,4),(4,1),(4,2),(4,3)]:
    for d in range(31):
        c=sum(1 for m in range(q**n*(d+2)) if Hq(m,q,n)<=d)
        if c!=N(q,n,d): ok=False; print('fail',q,n,d)
    # savings vs delta
    s=q; delta=q.bit_length()-1
    for k in range(1,40):
        for l in range(k):
            m=k-l-1
            dl = n*(q-1)+q*l+(q-1)*sum(m//q**j for j in range(n))
            if n*(q-1)+q*(k-1)-dl!=Hq(m,q,n): ok=False; print('sav',q,n,k,l)
for d in range(31):
    c=sum(1 for m in range(8*(d+2)) if H4(m)<=d)
    if c!=N(4,2,d): ok=False; print('f4',d,c,N(4,2,d))
print(ok, [N(4,2,d) for d in range(8)])
