from math import lgamma, log, exp, sqrt
def lC(a,b):
    if b<0 or b>a: return float('-inf')
    return lgamma(a+1)-lgamma(b+1)-lgamma(a-b+1)
def lsum(ls):
    m=max(ls); return m+log(sum(exp(x-m) for x in ls))
def lb(v,k): return lsum([lC(v,j) for j in range(max(0,k-60),k+1)])  # top terms dominate
def lm(N,j): return lC(N+1,j)+lC(N,j)+lgamma(j+1)
for N,D in [(1024,10),(2**14,14),(2**20,20)]:
    v=N*(N+1); M=N*N; kmax=N//(2*D)
    best=None
    for k in sorted(set([2,4,8,16,32,64,128,256,512,1024,2048,4096,kmax]+[int(c*sqrt(N*log(4*M))) for c in (0.25,0.5,0.75,1,1.5,2)])):
        if k>kmax or k<2: continue
        lu=lsum([lm(N,j) for j in range(max(0,k-60),k+1)])
        lt=log(N+1)+lb(v,k-1)
        if lu<=lt+1e-9: 
            print(N,D,k,'u_k<=t_k bound: vacuous'); continue
        lrhs=lu+log(1-exp(lt-lu))
        # smallest r with ln M + lb(v-r,k) < lrhs, bisection
        lo,hi=0,v
        while hi-lo>1:
            mid=(lo+hi)//2
            if log(M)+lb(v-mid,k)<lrhs: hi=mid
            else: lo=mid
        print(N,D,k,'r >',hi,' r/N=%.1f'%(hi/N),' claimed edge 2D(N+1)ln4M=%d'%(2*D*(N+1)*log(4*M)))
        if best is None or hi<best[1]: best=(k,hi)
    print('best',best,'ratio to claimed %.1f'%(best[1]/(2*D*(N+1)*log(4*M))),' N^1.5*2*sqrt(ln4M)=%d'%(2*N**1.5*sqrt(log(4*M))))
