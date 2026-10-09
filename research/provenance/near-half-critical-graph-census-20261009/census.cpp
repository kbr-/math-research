// Census of small vertex-critical non-four-colourable graphs: game value against forced edges.
//
// Statement tested (side notebook near-half-pc-degree, entry-2026-10-09-critical-graph-census): every graph that
// is not four-colourable, all of whose vertex-deleted subgraphs are four-colourable, and whose first-bit game
// value tau is at least N - 1, has an edge uv whose colour difference lies in the span Lambda_4 of the
// four-clique sums (so that the two-bit four-colouring system is refuted in degree at most 9 by
// prop:clique-sum-ceiling).  Input: graph6 lines (nauty-geng -c -d4 N); every five-critical graph is connected
// with minimum degree at least 4, so the input covers all such graphs on N vertices.  Usage: census N [N ...].  The program checks both
// hypotheses for each graph and skips the others.
//
// Output: one JSON line per vertex-critical non-four-colourable graph, then a summary line.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <vector>
using namespace std;
static int N; static uint32_t adj[16]; static vector<char> bip; static vector<uint8_t> memo; static uint32_t pw[16];
static bool bipartite(uint32_t mask){ int col[16]; for(int i=0;i<N;i++) col[i]=-1;
  for(int s=0;s<N;s++) if((mask>>s&1)&&col[s]<0){ int st[16],top=0; st[top++]=s; col[s]=0;
    while(top){ int u=st[--top]; uint32_t nb=adj[u]&mask; while(nb){ int v=__builtin_ctz(nb); nb&=nb-1;
      if(col[v]<0){ col[v]=col[u]^1; st[top++]=v; } else if(col[v]==col[u]) return false; } } }
  return true; }
static bool fourcol(uint32_t mask){ for(uint32_t s=mask;;s=(s-1)&mask){ if(bip[s]&&bip[mask&~s]) return true; if(!s) break; } return false; }
static int value(uint32_t a,uint32_t b,uint32_t code){     // as in bit_game.cpp
  if(memo[code]) return memo[code];
  uint32_t freev=~(a|b)&((1u<<N)-1); int best=255;
  for(uint32_t f=freev;f;f&=f-1){ int u=__builtin_ctz(f); if(!bip[a|1u<<u]&&!bip[b|1u<<u]){ best=1; break; } }
  if(best!=1) for(uint32_t f=freev;f;f&=f-1){ int u=__builtin_ctz(f); int worst=0;
    if(bip[a|1u<<u]){ int v=1+value(a|1u<<u,b,code+pw[u]); if(v>worst) worst=v; }
    if(worst<best && bip[b|1u<<u]){ int v=1+value(a,b|1u<<u,code+2*pw[u]); if(v>worst) worst=v; }
    if(worst<best) best=worst; if(best==2) break; }
  memo[code]=(uint8_t)best; return best; }
static int census(FILE*in){
  char line[256]; long total=0,crit=0,high=0,high_unforced=0,unforced=0,k4free=0; int hist[20][20]; memset(hist,0,sizeof hist);
  int mindef_unforced=99;
  while(fgets(line,sizeof line,in)){ N=line[0]-63; if(N<1||N>15) continue; total++;
    for(int i=0;i<N;i++) adj[i]=0; int k=0; const char*p=line+1; int bits=0,cur=0;
    for(int j=1;j<N;j++) for(int i=0;i<j;i++){ if(bits==0){ cur=*p++-63; bits=6; } bits--; if(cur>>bits&1){ adj[i]|=1u<<j; adj[j]|=1u<<i; } k++; }
    bip.assign(1u<<N,0); for(uint32_t m=0;m<(1u<<N);m++) bip[m]=bipartite(m);
    uint32_t all=(1u<<N)-1; if(fourcol(all)) continue; bool critical=true;
    for(int v=0;v<N&&critical;v++) if(!fourcol(all&~(1u<<v))) critical=false;
    if(!critical) continue; crit++;
    // independence number
    int alpha=0; for(uint32_t m=1;m<=all;m++){ bool ind=true; for(uint32_t r=m;r&&ind;r&=r-1){ int u=__builtin_ctz(r); if(adj[u]&m) ind=false; } if(ind){ int c=__builtin_popcount(m); if(c>alpha) alpha=c; } }
    // four-clique sums and forced edges
    vector<uint32_t> basis; int nk4=0;
    for(int a=0;a<N;a++) for(int b=a+1;b<N;b++) if(adj[a]>>b&1) for(int c=b+1;c<N;c++) if((adj[a]>>c&1)&&(adj[b]>>c&1)) for(int d=c+1;d<N;d++)
      if((adj[a]>>d&1)&&(adj[b]>>d&1)&&(adj[c]>>d&1)){ nk4++; uint32_t v=1u<<a|1u<<b|1u<<c|1u<<d; for(uint32_t x:basis) if((v^x)<v) v^=x; if(v){ basis.push_back(v); } }
    auto inspan=[&](uint32_t v){ // basis already has distinct leading bits; the rebuild below is redundant and harmless
      vector<uint32_t> ech; for(uint32_t x:basis){ for(uint32_t y:ech) if((x^y)<x) x^=y; if(x) ech.push_back(x); }
      for(;;){ bool ch=false; for(uint32_t y:ech) if((v^y)<v){ v^=y; ch=true; } if(!ch) break; } return v==0; };
    bool forced=false; for(int u=0;u<N&&!forced;u++) for(int v=u+1;v<N&&!forced;v++) if((adj[u]>>v&1)&&inspan(1u<<u|1u<<v)) forced=true;
    pw[0]=1; for(int i=1;i<N;i++) pw[i]=pw[i-1]*3; memo.assign((size_t)pw[N-1]*3,0); int tau=value(0,0,0);
    int edges=0; for(int i=0;i<N;i++) edges+=__builtin_popcount(adj[i]); edges/=2;
    hist[N-tau][forced?1:0]++; if(!forced){ unforced++; if(N-tau<mindef_unforced) mindef_unforced=N-tau; } if(nk4==0) k4free++;
    if(tau>=N-1){ high++; if(!forced) high_unforced++; }
    line[strcspn(line,"\n")]=0; char esc[512]; int e=0; for(const char*c=line;*c;c++){ if(*c=='\\'||*c=='"') esc[e++]='\\'; esc[e++]=*c; } esc[e]=0;
    printf("{\"N\":%d,\"edges\":%d,\"alpha\":%d,\"tau\":%d,\"four_cliques\":%d,\"forced_edge\":%s,\"g6\":\"%s\"}\n",N,edges,alpha,tau,nk4,forced?"true":"false",esc);
  }
  printf("{\"summary\":true,\"N\":%d,\"graphs_read\":%ld,\"critical\":%ld,\"tau_at_least_N_minus_1\":%ld,\"of_those_without_forced_edge\":%ld,\"without_forced_edge\":%ld,\"least_N_minus_tau_without_forced_edge\":%d,\"four_clique_free\":%ld,\"hist_N_minus_tau_unforced_forced\":[",N,total,crit,high,high_unforced,unforced,unforced?mindef_unforced:-1,k4free);
  for(int d=0;d<12;d++) printf("[%d,%d]%s",hist[d][0],hist[d][1],d<11?",":""); printf("]}\n");
  return 0; }
// One series invocation: census N [N ...] runs nauty-geng -q -c -d4 N for each size.
int main(int argc,char**argv){ for(int i=1;i<argc;i++){ int n=atoi(argv[i]); if(n<5||n>12) return 2; char cmd[64]; snprintf(cmd,64,"nauty-geng -q -c -d4 %d",n);
    FILE*in=popen(cmd,"r"); if(!in) return 3; census(in); pclose(in); fflush(stdout); } return 0; }
