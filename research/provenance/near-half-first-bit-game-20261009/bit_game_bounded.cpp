// Bounded search for the first-bit game on circular cliques K_{(4q+1)/q} (see bit_game.cpp for the game and
// the statement tested): for each q, the least t <= TMAX such that the algorithm wins within t queries, or
// that no such t exists up to TMAX.  The first query is vertex 0 put in class 0, by vertex-transitivity and
// the symmetry of the classes.  States are (class 0, class 1) with a transposition table.
//
// Usage: bit_game_bounded TMAX Q [Q ...]     (N = 4Q+1 <= 32)
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
using namespace std;
static int N,q; static uint32_t adj[32];
static bool bipartite(uint32_t mask){
  int col[32]; for(int i=0;i<N;i++) col[i]=-1;
  for(uint32_t r=mask;r;r&=r-1){ int s=__builtin_ctz(r); if(col[s]>=0) continue; int st[32],top=0; st[top++]=s; col[s]=0;
    while(top){ int u=st[--top]; uint32_t nb=adj[u]&mask; while(nb){ int v=__builtin_ctz(nb); nb&=nb-1;
        if(col[v]<0){ col[v]=col[u]^1; st[top++]=v; } else if(col[v]==col[u]) return false; } } }
  return true;
}
// open-addressing table: key (a,b) -> lo (largest budget known to fail), hi (smallest budget known to win)
static vector<uint64_t> keys; static vector<uint8_t> lo,hi; static uint64_t maskT; static uint64_t used;
static size_t slot(uint64_t k){ uint64_t h=k*0x9E3779B97F4A7C15ULL; size_t i=(h>>20)&maskT;
  while(keys[i]!=~0ULL&&keys[i]!=k) i=(i+1)&maskT; return i; }
static bool win(uint32_t a,uint32_t b,int t){
  if(t<=0) return false;
  uint64_t k=((uint64_t)a<<32)|b; size_t i=slot(k);
  if(keys[i]==k){ if(t<=lo[i]) return false; if(t>=hi[i]) return true; }
  else { if(used*2>maskT){ fprintf(stderr,"table full\n"); exit(3); } keys[i]=k; lo[i]=0; hi[i]=255; used++; }
  uint32_t all=N==32?~0u:((1u<<N)-1), freev=~(a|b)&all; bool res=false;
  uint32_t la=0,lb=0;
  for(uint32_t f=freev;f;f&=f-1){ int u=__builtin_ctz(f); bool x=bipartite(a|1u<<u), y=bipartite(b|1u<<u);
    if(!x&&!y){ res=true; break; } if(x) la|=1u<<u; if(y) lb|=1u<<u; }
  if(!res&&t>1) for(uint32_t f=freev;f&&!res;f&=f-1){ int u=__builtin_ctz(f);
    if((la>>u&1)&&!win(a|1u<<u,b,t-1)) continue;
    if((lb>>u&1)&&!win(a,b|1u<<u,t-1)) continue;
    res=true; }
  i=slot(k); if(res){ if(t<hi[i]) hi[i]=t; } else { if(t>lo[i]) lo[i]=t; }
  return res;
}
int main(int argc,char**argv){
  if(argc<3) return 2; int tmax=atoi(argv[1]);
  for(int ai=2;ai<argc;ai++){ q=atoi(argv[ai]); N=4*q+1; if(q<1||N>32) return 2;
    for(int i=0;i<N;i++){ adj[i]=0; for(int j=0;j<N;j++) if(i!=j){ int d=abs(i-j); if(d>N-d) d=N-d; if(d>=q) adj[i]|=1u<<j; } }
    maskT=(1ULL<<27)-1; keys.assign(maskT+1,~0ULL); lo.assign(maskT+1,0); hi.assign(maskT+1,255); used=0;
    int found=-1; for(int t=1;t<=tmax&&found<0;t++){ if(win(1u,0u,t-1)) found=t;
      fprintf(stderr,"q=%d t=%d %s states=%llu\n",q,t,found<0?"no":"yes",(unsigned long long)used); }
    printf("{\"q\":%d,\"N\":%d,\"tmax\":%d,\"within_tmax\":%s,\"game_value_or_tmax\":%d,\"states\":%llu}\n",q,N,tmax,found<0?"false":"true",found<0?tmax:found,(unsigned long long)used); fflush(stdout); }
  return 0;
}
