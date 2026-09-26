# Pointwise check over F_3 of the carry-chain identities (at L in {0,1,2}), and a brute-force check of the
# substitution on a small graph: every Boolean collision-free y satisfying the source rows
# maps to a target assignment satisfying all target axioms.
import itertools, random
p=3
def ind_ne0(L): return (L*L)%3
def ind_eq2(L): return (2*L*(L-1))%3
for L in range(3):
    assert (ind_ne0(L)+ind_eq2(L))%3==L%3
    assert ind_ne0(L) in (0,1) and ind_eq2(L) in (0,1)
    assert ind_ne0(L)+ind_eq2(L)==L   # integer carry value
random.seed(1)
def check(nR,nH,deg,parts):
    edges=[(i,u) for i in range(nR) for u in random.sample(range(nH),deg)]
    E=sorted(set(edges))
    q=len(parts); ok=0; tot=0
    for bits in itertools.product((0,1),repeat=len(E)):
        y=dict(zip(E,bits))
        # source: collisions and rows mod 3
        if any(sum(y[(i,u)] for i in range(nR) if (i,u) in y)>1 for u in range(nH)): continue
        if any(sum(y[(i,u)] for u in range(nH) if (i,u) in y)%3!=1 for i in range(nR)): continue
        tot+=1
        C=[sum(y[(i,u)] for i in range(nR) if (i,u) in y) for u in range(nH)]
        # carries
        L=[None]*q; prev=2
        for k in range(q-1):
            S=sum(C[u] for u in parts[k]); L[k]=(prev+S-len(parts[k])-1)%3; prev=L[k]
        # target assignment
        x_z=[{} for _ in range(q)]
        for k in range(q):
            for u in parts[k]: x_z[k][('h',u)]=1-C[u]
            if k<q-1: x_z[k][('a',k)]=ind_ne0(L[k]); x_z[k][('b',k)]=ind_eq2(L[k])
            if k>0: x_z[k][('a',k-1)]=1-ind_ne0(L[k-1]); x_z[k][('b',k-1)]=1-ind_eq2(L[k-1])
        good=all(sum(d.values())%3==1 for d in x_z)
        good&=all(v in (0,1) for d in x_z for v in d.values())
        for u in range(nH):
            owner=[k for k in range(q) if u in parts[k]]
            good&= C[u]+x_z[owner[0]][('h',u)]==1
        for k in range(q-1):
            good&= x_z[k][('a',k)]+x_z[k+1][('a',k)]==1 and x_z[k][('b',k)]+x_z[k+1][('b',k)]==1
        ok+=good
    return tot,ok
# count condition: |R| + q = |H| + 2(q-1) mod 3; first cases satisfy it, last two are controls
for (nR,nH,deg,parts) in [(2,5,2,[[0,1,2],[3,4]]),(3,4,2,[[0],[1],[2],[3]]),(3,4,2,[[0,1,2,3]]),(4,6,3,[[0,1],[2,3],[4,5]]),(4,6,2,[[0,1,2],[3],[4,5]]),(2,5,2,[[0,1,2,3,4]]),(4,6,3,[[0,1],[2,3,4,5]])]:
    q=len(parts); cond=(nR+q-(nH+2*(q-1)))%3
    print(nR,nH,q,'count cond',cond,'->',check(nR,nH,deg,parts))
