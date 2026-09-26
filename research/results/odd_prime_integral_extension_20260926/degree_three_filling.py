"""Reviewer check of thm:integral-design-extension (odd-prime thread, 26 Sept 2026): builds the degree-2 integer
design of prop:integral-degree-two-certificate for 6 pigeons and 5 holes, fills each 3-row chessboard cycle over Z
with PARI matsolvemod, and counts violations of the degree-3 design equations. Written by the fresh-context reviewer."""
import itertools, subprocess
P, n = 6, 5
z = {(): 1}
for i in range(P):
    for j in range(n): z[((i,j),)] = 1 if j==0 else 0
for i in range(P):
    for i2 in range(i+1,P):
        for j in range(n):
            for j2 in range(n):
                if j==j2: continue
                v = 0
                if (j,j2)==(0,2) or (j,j2)==(1,0): v=1
                if (j,j2)==(1,2): v=-1
                z[((i,j),(i2,j2))]=v
def key(cells): return tuple(sorted(cells))
def check(maxT):
    bad=0
    for t in range(maxT+1):
        for rows in itertools.combinations(range(P),t):
            for cols in itertools.permutations(range(n),t):
                T=key(zip(rows,cols))
                for i in range(P):
                    if i in rows: continue
                    s=sum(z[key(T+((i,j),))] for j in range(n) if j not in cols)
                    if s!=z[T]: bad+=1
    return bad
print("deg2 violations", check(1))
k=3
def matchings(R,size):
    out=[]
    for rows in itertools.combinations(R,size):
        for cols in itertools.permutations(range(n),size):
            out.append(key(zip(rows,cols)))
    return out
gp=[]
jobs=[]
for R in itertools.combinations(range(P),k):
    pos={c:t for t,c in enumerate(R)}
    top=matchings(R,k); mid=matchings(R,k-1)
    ti={U:a for a,U in enumerate(top)}
    # boundary matrix mid x top
    M=[[0]*len(top) for _ in mid]
    for a,U in enumerate(top):
        for t,cell in enumerate(U):  # U sorted by row = row order
            F=key([c for c in U if c!=cell])
            M[mid.index(F)][a]+= (-1)**t
    zeta=[]
    for F in mid:
        c=[r for r in R if r not in [x[0] for x in F]][0]
        zeta.append((-1)**pos[c]*z[F])
    jobs.append((R,top))
    gp.append("print(matsolvemod(%s,0,%s~));"%( "["+";".join(",".join(map(str,row)) for row in M)+"]", "["+",".join(map(str,zeta))+"]"))
out=subprocess.run(["gp","-q","-D","parisize=100000000"],input="\n".join(gp)+"\n",capture_output=True,text=True).stdout.strip().split("\n")
assert len(out)==len(jobs), out[:3]
for (R,top),line in zip(jobs,out):
    assert line!="0", ("no integer solution", R)
    vals=[int(x) for x in line.strip("[]~").split(",")]
    for U,v in zip(top,vals): z[U]=v
print("deg3 violations", check(2))
print("max |z|", max(abs(v) for v in z.values()))
