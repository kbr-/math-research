// Static span of single-orbit covers of F_2^n under the affine group of Z_p, p = n+1 prime.
//
// Statement tested (side notebook near-half-pc-degree, entry-2026-10-09-orbit-cover-span): for a linear subspace
// V of codimension w of the space of two-colourings of Z_p modulo complement whose orbit under AGL(1,p) covers
// the space, the span S_D of the multiples m*R (R a row indicator, m a monomial of degree <= D-w) contains 1 at
// the degree where the dimension count M*C(n-w,<=D-w) >= C(n,<=D) first allows S_D to be everything, i.e. the
// family behaves generically.  The alternative, a proper S_D without 1 beyond that degree, would be the rank
// deficiency a barrier needs.  S_D is contained in the PC closure C_D, so 1 in S_D gives PC degree <= D.
//
// Coordinates: a point is a colouring c of Z_p with c(0) = 0, bits y_1..y_n.  g(i) = a*i+b acts by
// c -> c o g followed by normalisation; a form with support L becomes the form with j in L toggling g(j), g(0).
// The program searches random V until the orbit covers (checked at every point) and eliminates over F_2 with pivots by highest monomial index in the order
// (degree, mask), so that 1 is in the span iff a pivot leads at index 0.
//
// rank_in_degree_below_D = dim(S_D within degree <= D-1); when it equals the rank of S_{D-1}, C_D = S_D.
// Usage: orbit_span P W SEED TRIES DMAX      Output: JSON lines (cover, one line per D, summary).
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <vector>
#include <random>
#include <algorithm>
#include <set>
using namespace std;
typedef uint64_t u64; typedef uint32_t u32;
static int P, N, W;
static u32 act(u32 mask, int a, int b){ u32 r=0; int g0=b%P;
  for(int j=1;j<=N;j++) if(mask>>(j-1)&1){ int gj=(a*j+b)%P; if(gj) r^=1u<<(gj-1); if(g0) r^=1u<<(g0-1); }
  return r; }
static int rankof(vector<u32> v){ int r=0; for(size_t i=0;i<v.size();i++){ if(!v[i]) continue; r++; u32 low=v[i]&-v[i];
    for(size_t k=i+1;k<v.size();k++) if(v[k]&low) v[k]^=v[i]; } return r; }
static u64 binomle(int n,int d){ if(d<0) return 0; u64 s=0,c=1; for(int j=0;j<=d&&j<=n;j++){ s+=c; c=c*(n-j)/(j+1); } return s; }
int main(int argc,char**argv){
  if(argc!=6) return 2; P=atoi(argv[1]); W=atoi(argv[2]); u64 seed=atoll(argv[3]); int tries=atoi(argv[4]), DMAX=atoi(argv[5]);
  N=P-1; if(N>18||N<4||DMAX>N) return 2; for(int q=2;q*q<=P;q++) if(P%q==0) return 2;
  { int ord=1,x=2%P; while(x!=1){ x=2*x%P; ord++; } if(ord!=P-1) return 2; }   // 2 must be a primitive root
  mt19937_64 rng(seed); u32 full=(1u<<N)-1; vector<vector<u32>> rows; int used=0;
  for(int t=1;t<=tries&&rows.empty();t++){ used=t; vector<u32> base(W); do{ for(auto&f:base) f=rng()&full; }while(rankof(base)<W);
    set<vector<u32>> seen; vector<vector<u32>> orb;
    for(int a=1;a<P;a++) for(int b=0;b<P;b++){ vector<u32> f(W); for(int k=0;k<W;k++) f[k]=act(base[k],a,b);
      // canonical basis of the span of the forms: reduced echelon, so equal subspaces compare equal
      for(int i=0;i<W;i++){ u32 top=1u<<(31-__builtin_clz(f[i])); for(int k=0;k<W;k++) if(k!=i&&(f[k]&top)) f[k]^=f[i]; }
      sort(f.begin(),f.end()); if(seen.insert(f).second) orb.push_back(f); }
    bool cover=true;
    for(u32 y=0;y<=full&&cover;y++){ bool in=false; for(auto&f:orb){ bool ok=true; for(int k=0;k<W&&ok;k++) if(__builtin_parity(f[k]&y)) ok=false; if(ok){ in=true; break; } } if(!in) cover=false; }
    if(cover) rows=orb; }
  if(rows.empty()){ printf("{\"p\":%d,\"w\":%d,\"cover_found\":false,\"tries\":%d}\n",P,W,used); return 0; }
  int M=rows.size(); printf("{\"p\":%d,\"n\":%d,\"w\":%d,\"cover_found\":true,\"tries\":%d,\"rows\":%d,\"cover\":\"",P,N,W,used,M);
  if(N<=10) for(auto&f:rows){ printf("%d",W); for(u32 m:f) printf(" %u 0",m); printf(" ; "); }
  printf("\"}\n"); fflush(stdout);
  // monomial index for (degree, mask)
  vector<u32> monos; for(u32 m=0;m<=full;m++) if(__builtin_popcount(m)<=DMAX) monos.push_back(m);
  sort(monos.begin(),monos.end(),[](u32 a,u32 b){ int x=__builtin_popcount(a),y=__builtin_popcount(b); return x!=y?x<y:a<b; });
  vector<int> idx(full+1,-1); for(size_t i=0;i<monos.size();i++) idx[monos[i]]=i; int dim=monos.size(), words=(dim+63)/64;
  // row polynomials as monomial lists
  vector<vector<u32>> poly(M); vector<char> bits(full+1);
  for(int r=0;r<M;r++){ fill(bits.begin(),bits.end(),0); bits[0]=1; vector<u32> cur{0};
    for(int k=0;k<W;k++){ vector<u32> nxt; // multiply by (form + 1): keep p, add x_j*p for j in form
      vector<char> nb(bits); for(u32 m:cur) for(int j=0;j<N;j++) if(rows[r][k]>>j&1) nb[m|1u<<j]^=1;
      set<u32> cand(cur.begin(),cur.end()); for(u32 m:cur) for(int j=0;j<N;j++) if(rows[r][k]>>j&1) cand.insert(m|1u<<j);
      for(u32 m:cand) if(nb[m]) nxt.push_back(m); for(u32 m:cand) bits[m]=0; for(u32 m:nxt) bits[m]=1; cur=nxt; }
    for(u32 m:cur) bits[m]=0; poly[r]=cur; }
  vector<u64*> pivot(dim,nullptr); long rank=0; vector<u64> v(words);
  auto reduce_insert=[&](){ int wi=words-1; for(;;){ while(wi>=0&&!v[wi]) wi--; if(wi<0) return false; int lead=wi*64+63-__builtin_clzll(v[wi]);
      u64*pv=pivot[lead]; if(!pv){ u64*s=(u64*)malloc(8*words); memcpy(s,v.data(),8*words); pivot[lead]=s; rank++; return true; }
      for(int i=0;i<=wi;i++) v[i]^=pv[i]; } };
  for(int D=W;D<=DMAX;D++){ int d=D-W; long one_row=0;
    for(int r=0;r<M;r++){ long before=rank;
      for(u32 m:monos){ int dm=__builtin_popcount(m); if(dm>d) break; if(dm<d) continue;
        fill(v.begin(),v.end(),0); for(u32 t:poly[r]){ int i=idx[t|m]; if(i<0){ fprintf(stderr,"degree overflow\n"); return 3; } v[i>>6]^=1ULL<<(i&63); }
        reduce_insert(); }
      if(r==0) one_row=rank-before; }
    u64 dimD=binomle(N,D), bound=(u64)M*binomle(N-W,d);
    // pivots whose leading monomial has degree < D: the dimension of S_D intersected with degree <= D-1.
    // If it equals the rank of S_{D-1}, S_D is closed under the PC rule at degree D, so C_D = S_D.
    long low=0; for(u64 i=0;i<binomle(N,D-1);i++) if(pivot[i]) low++;
    printf("{\"p\":%d,\"w\":%d,\"D\":%d,\"static_rank\":%ld,\"dim\":%llu,\"count_bound\":%llu,\"first_row_new_rank_at_this_degree\":%ld,\"rank_in_degree_below_D\":%ld,\"one_in_span\":%s}\n",
      P,W,D,rank,(unsigned long long)dimD,(unsigned long long)bound,one_row,low,pivot[0]?"true":"false"); fflush(stdout);
    if(pivot[0]) break; }
  return 0; }
