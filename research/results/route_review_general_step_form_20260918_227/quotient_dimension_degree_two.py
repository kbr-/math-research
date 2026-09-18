import itertools, sys
def rank(rows):
    piv={}; r=0
    for v in rows:
        while v:
            h=v.bit_length()-1
            if h in piv: v^=piv[h]
            else: piv[h]=v; r+=1; break
    return r
for N in (6,7,8):
    R=N+1
    cells=[(i,j) for i in range(R) for j in range(N)]
    mons=[()]+[(c,) for c in cells]+[tuple(sorted((a,b))) for a,b in itertools.combinations(cells,2) if a[0]!=b[0] and a[1]!=b[1]]
    idx={m:k for k,m in enumerate(mons)}
    rels=[]
    for i in range(R):
        v=1<<idx[()]
        for j in range(N): v^=1<<idx[((i,j),)]
        rels.append(v)
        for e in cells:
            if e[0]==i: continue
            v=1<<idx[(e,)]
            for j in range(N):
                if j!=e[1]: v^=1<<idx[tuple(sorted((e,(i,j))))]
            rels.append(v)
    rk=rank(rels); c1=1+R*N-R; c2=len(mons)-rk
    print('N',N,'u2',len(mons),'rank',rk,'c1',c1,'c2',c2,'pred level-two increment c2-2c1+3 =',c2-2*c1+3)
