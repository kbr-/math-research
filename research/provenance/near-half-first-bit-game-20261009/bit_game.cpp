// Value of the first-bit game on a graph: the least depth of a decision tree that queries vertices' first
// colour bits and at every leaf has an odd cycle inside one bit class of the queried vertices.
//
// Statement tested (side notebook near-half-pc-degree, entry-2026-10-09-first-bit-game): for the circular
// clique K_{(4q+1)/q} (vertices Z_p, p = 4q+1, i ~ j iff the circular distance is at least q), which is not
// four-colourable while every proper induced subgraph is, the game value tau is at least N - c for a constant
// c.  The two-bit four-colouring of a graph has polynomial-calculus degree at most tau + 2 over F_2, so the
// hypothesis is necessary for that family to have a degree barrier near N = n/2.
// The program asserts that the graph is not four-colourable and that every vertex-deleted subgraph is.
//
// Game: the algorithm names an unqueried vertex; the adversary puts it in class 0 or 1 so that both classes
// stay bipartite; if neither class works the algorithm has won.  value(state) = number of further queries the
// algorithm needs, including the winning one, under optimal play: min over vertices of 1 + max over legal
// classes, or 1 if some vertex has no legal class.
//
// Usage: bit_game Q [Q ...]      (one series invocation; N = 4Q+1 <= 17)
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
using namespace std;
static int N; static vector<uint32_t> adj; static vector<char> bip; static vector<uint8_t> memo; static vector<uint32_t> pw;
static bool bipartite(uint32_t mask){
  int col[20]; for(int i=0;i<N;i++) col[i]=-1;
  for(int s=0;s<N;s++) if((mask>>s&1)&&col[s]<0){ int st[20],top=0; st[top++]=s; col[s]=0;
    while(top){ int u=st[--top]; uint32_t nb=adj[u]&mask; while(nb){ int v=__builtin_ctz(nb); nb&=nb-1;
        if(col[v]<0){ col[v]=col[u]^1; st[top++]=v; } else if(col[v]==col[u]) return false; } } }
  return true;
}
static int value(uint32_t a,uint32_t b,uint32_t code){
  if(memo[code]) return memo[code];
  uint32_t freev=~(a|b)&((1u<<N)-1); int best=255;
  for(uint32_t f=freev;f;f&=f-1){ int u=__builtin_ctz(f); bool la=bip[a|1u<<u], lb=bip[b|1u<<u];
    if(!la&&!lb){ best=1; break; } }
  if(best!=1) for(uint32_t f=freev;f;f&=f-1){ int u=__builtin_ctz(f); int worst=0;
    if(bip[a|1u<<u]){ int v=1+value(a|1u<<u,b,code+pw[u]); if(v>worst) worst=v; }
    if(worst<best && bip[b|1u<<u]){ int v=1+value(a,b|1u<<u,code+2*pw[u]); if(v>worst) worst=v; }
    if(worst<best) best=worst; if(best==2) break; }
  memo[code]=(uint8_t)best; return best;
}
static bool fourcol(uint32_t mask){           // is G[mask] four-colourable: two disjoint bipartite parts
  for(uint32_t s=mask;;s=(s-1)&mask){ if(bip[s]&&bip[mask&~s]) return true; if(!s) break; }
  return false;
}
int main(int argc,char**argv){
  for(int ai=1;ai<argc;ai++){ bool window=argv[ai][0]=='H'; int q=atoi(argv[ai]+(window?1:0));
    // "HL": the window graph on indices 0..L-1 with i ~ j iff |i-j| = 1 or |i-j| mod 4 in {2,3}.  It is the
    // subgraph of K_{(4q+1)/q} induced on the vertices a_j = j*q mod (4q+1), 0 <= j < L, whenever L <= 4q.
    N=window?q:4*q+1; if(q<1||N>17){ fprintf(stderr,"need N<=17\n"); return 2; }
    adj.assign(N,0); for(int i=0;i<N;i++) for(int j=0;j<N;j++) if(i!=j){ int d=abs(i-j);
      if(window){ if(d==1||d%4==2||d%4==3) adj[i]|=1u<<j; } else { if(d>N-d) d=N-d; if(d>=q) adj[i]|=1u<<j; } }
    bip.assign(1u<<N,0); for(uint32_t m=0;m<(1u<<N);m++) bip[m]=bipartite(m);
    uint32_t all=(1u<<N)-1; bool whole=fourcol(all), critical=true;
    for(int v=0;v<N;v++) if(!fourcol(all&~(1u<<v))) critical=false;
    if(window){ pw.assign(N,1); for(int i=1;i<N;i++) pw[i]=pw[i-1]*3; memo.assign((size_t)pw[N-1]*3,0);
      int tw=value(0,0,0);   // 255: the adversary survives every query (possible only if four-colourable)
      printf("{\"window\":%d,\"four_colourable\":%s,\"game_value\":%d}\n",N,whole?"true":"false",tw); fflush(stdout); continue; }
    if(whole||!critical){ fprintf(stderr,"hypotheses fail at q=%d\n",q); return 1; }
    pw.assign(N,1); for(int i=1;i<N;i++) pw[i]=pw[i-1]*3; memo.assign((size_t)pw[N-1]*3,0);
    int tau=value(0,0,0); size_t visited=0; for(uint8_t x:memo) if(x) visited++;
    // an optimal strategy, as lines "depth: classes so far -> query u" (vertices written a*q+b)
    if(getenv("BIT_GAME_TREE")||true){ struct F{ static void go(uint32_t a,uint32_t b,uint32_t code,int depth,int q,int lim){
        uint32_t freev=~(a|b)&((1u<<N)-1); int best=value(a,b,code), pick=-1;
        for(uint32_t f=freev;f&&pick<0;f&=f-1){ int u=__builtin_ctz(f); bool la=bip[a|1u<<u], lb=bip[b|1u<<u];
          int worst=(!la&&!lb)?1:0; if(la){ int v=1+value(a|1u<<u,b,code+pw[u]); if(v>worst) worst=v; }
          if(lb){ int v=1+value(a,b|1u<<u,code+2*pw[u]); if(v>worst) worst=v; } if(worst==best) pick=u; }
        printf("# %*s", depth*2, ""); printf("A={"); for(int i=0;i<N;i++) if(a>>i&1) printf("%d ",i); printf("} B={");
        for(int i=0;i<N;i++) if(b>>i&1) printf("%d ",i); printf("} query %d (=%dq%+d) value %d\n",pick,(pick+q/2)/q,pick-((pick+q/2)/q)*q,best);
        if(depth>=lim) return;
        if(bip[a|1u<<pick]) go(a|1u<<pick,b,code+pw[pick],depth+1,q,lim);
        if(depth>0 && bip[b|1u<<pick]) go(a,b|1u<<pick,code+2*pw[pick],depth+1,q,lim); } };
      F::go(0,0,0,0,q,tau); }
    printf("{\"q\":%d,\"N\":%d,\"not_four_colourable\":true,\"vertex_critical\":true,\"game_value\":%d,\"states_visited\":%zu}\n",q,N,tau,visited); fflush(stdout); }
  return 0;
}
