// Exact polynomial-calculus degree over F_2 of covers of F_2^n by affine subspaces of codimension <= w.
//
// Statement tested (side notebook near-half-pc-degree, entry-2026-10-09-covering-form-review, decisive test):
//   every minimal cover of F_2^n by affine subspaces of codimension at most w is refuted by polynomial
//   calculus within degree ceil(n/2) + w.
// A cover is a list of subspaces {x : m_j.x = t_j, j < k}, k <= w, with independent masks m_j; its axiom is the
// indicator prod_j (m_j.x + t_j + 1), a multilinear polynomial of degree <= k.  The program checks in code that
// each instance is a cover (unsatisfiable) and minimal.  The degree-D closure C_D is computed exactly: the
// least subspace of multilinear polynomials of degree <= D containing the axioms of degree <= D and x_i*p for
// every p in it of degree <= D-1.  It is kept in echelon form for the order (degree, mask), for which the
// elements of degree <= D-1 are spanned by the basis elements with leading degree <= D-1.
//
// Usage: cover_degree SEED RESTARTS STEPS N:W:CLASS [N:W:CLASS ...]   (CLASS: general | subcube | pool | pairs)
//        cover_degree --check N < covers     (one cover per line: "k m1 t1 ... ; k m1 t1 ... ;", prints degree)
// Output: JSON lines, one per restart, with the best cover found by hill climbing, and a summary line.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <vector>
#include <string>
#include <random>
#include <algorithm>
#include <omp.h>
using namespace std;
typedef uint64_t u64;
static int n, NW;            // variables; words per polynomial (2^n / 64, n >= 6)
struct Poly { u64 w[16]; };  // n <= 10
static Poly DEG[11], HAS[10];
static inline bool zero(const Poly&p){ for(int i=0;i<NW;i++) if(p.w[i]) return false; return true; }
static inline void xr(Poly&a,const Poly&b){ for(int i=0;i<NW;i++) a.w[i]^=b.w[i]; }
static inline bool get(const Poly&p,int m){ return p.w[m>>6]>>(m&63)&1; }
static inline void flip(Poly&p,int m){ p.w[m>>6]^=1ULL<<(m&63); }
static int lead(const Poly&p){              // largest monomial for (degree, mask), or -1
  for(int k=n;k>=0;k--) for(int i=NW-1;i>=0;i--){ u64 q=p.w[i]&DEG[k].w[i]; if(q) return i*64+63-__builtin_clzll(q); }
  return -1;
}
static Poly mulvar(const Poly&p,int v){     // multilinear product with x_v
  Poly r; int s=1<<v;
  for(int i=0;i<NW;i++) r.w[i]=p.w[i]&HAS[v].w[i];
  for(int m=0;m<(1<<n);m++) if(!(m&s) && get(p,m)) flip(r,m|s);
  return r;
}
static Poly mulform(const Poly&p,int mask,int c){ // product with the affine form mask.x + c
  Poly r; memset(&r,0,sizeof r); if(c) r=p;
  for(int v=0;v<n;v++) if(mask>>v&1){ Poly q=mulvar(p,v); xr(r,q); }
  return r;
}
struct Sub { int k; int m[3], t[3]; };
static Poly axiom(const Sub&s){ Poly p; memset(&p,0,sizeof p); p.w[0]=1; for(int j=0;j<s.k;j++) p=mulform(p,s.m[j],s.t[j]^1); return p; }
static int degof(const Poly&p){ int l=lead(p); return l<0?-1:__builtin_popcount(l); }
// true iff 1 lies in the degree-D closure of the axioms
static bool refuted(const vector<Poly>&ax,int D){
  int N=1<<n; vector<Poly> basis(N); vector<char> has(N,0); vector<int> work;
  auto insert=[&](Poly v)->bool{
    for(;;){ int l=lead(v); if(l<0) return false;
      if(has[l]) xr(v,basis[l]);
      else { basis[l]=v; has[l]=1; if(__builtin_popcount(l)<=D-1) work.push_back(l); return l==0; } }
  };
  for(const Poly&a:ax) if(degof(a)<=D) if(insert(a)) return true;
  while(!work.empty()){ int l=work.back(); work.pop_back(); Poly b=basis[l];
    for(int v=0;v<n;v++) if(insert(mulvar(b,v))) return true; }
  return false;
}
static int pcdegree(const vector<Sub>&cover){
  vector<Poly> ax; for(const Sub&s:cover) ax.push_back(axiom(s));
  for(int D=0;D<=n;D++) if(refuted(ax,D)) return D;
  return -1;                                 // not a cover
}
static bool contains(const Sub&s,int x){ for(int j=0;j<s.k;j++) if((__builtin_popcount(s.m[j]&x)&1)!=s.t[j]) return false; return true; }
static bool covers(const vector<Sub>&c){ for(int x=0;x<(1<<n);x++){ bool ok=false; for(const Sub&s:c) if(contains(s,x)){ok=true;break;} if(!ok) return false; } return true; }
static bool minimal(const vector<Sub>&c){ for(size_t i=0;i<c.size();i++){ vector<Sub> d=c; d.erase(d.begin()+i); if(covers(d)) return false; } return true; }
static bool independent(const Sub&s){ if(s.k>=1&&!s.m[0]) return false; if(s.k>=2&&(!s.m[1]||s.m[1]==s.m[0])) return false;
  if(s.k==3&&(!s.m[2]||s.m[2]==s.m[0]||s.m[2]==s.m[1]||s.m[2]==(s.m[0]^s.m[1]))) return false; return true; }
struct Gen { int w, cls; vector<int> pool; mt19937_64 rng;
  int mask(){ int N=(1<<n)-1;
    if(cls==1) return 1<<(rng()%n);
    if(cls==2) return pool[rng()%pool.size()];
    if(cls==3){ int a=rng()%n,b=rng()%n; return (1<<a)|(1<<b); }
    return 1+rng()%N; }
  Sub sub(){ for(;;){ Sub s; s.k=w; for(int j=0;j<w;j++){ s.m[j]=mask(); s.t[j]=rng()&1; } if(independent(s)) return s; } }
  void fill(vector<Sub>&c){ while(!covers(c)) c.push_back(sub()); }
  void minimalize(vector<Sub>&c){ shuffle(c.begin(),c.end(),rng);
    for(size_t i=0;i<c.size();){ vector<Sub> d=c; d.erase(d.begin()+i); if(covers(d)) c=d; else i++; } }
};
static string show(const vector<Sub>&c){ string o; char b[64];
  for(const Sub&s:c){ snprintf(b,64,"%d",s.k); o+=b; for(int j=0;j<s.k;j++){ snprintf(b,64," %d %d",s.m[j],s.t[j]); o+=b; } o+=" ; "; } return o; }
static void setup(){ NW=(1<<n)/64; memset(DEG,0,sizeof DEG); memset(HAS,0,sizeof HAS);
  for(int m=0;m<(1<<n);m++){ flip(DEG[__builtin_popcount(m)],m); for(int v=0;v<n;v++) if(m>>v&1) flip(HAS[v],m); } }
int main(int argc,char**argv){
  if(argc==3&&!strcmp(argv[1],"--check")){ n=atoi(argv[2]); setup(); char line[1<<16];
    while(fgets(line,sizeof line,stdin)){ vector<Sub> c; char*p=line; for(;;){ Sub s; int used;
        if(sscanf(p,"%d%n",&s.k,&used)!=1) break; p+=used;
        for(int j=0;j<s.k;j++){ sscanf(p,"%d %d%n",&s.m[j],&s.t[j],&used); p+=used; }
        while(*p==' '||*p==';') p++; c.push_back(s); }
      if(c.empty()) continue; printf("%d %d\n",pcdegree(c),(int)(covers(c)&&minimal(c))); }
    return 0; }
  if(argc<5){ fprintf(stderr,"usage\n"); return 2; }
  long seed=atol(argv[1]); int restarts=atoi(argv[2]), steps=atoi(argv[3]);
  for(int a=4;a<argc;a++){                   // one series invocation: N:W:CLASS ...
    int w; char clb[32]; if(sscanf(argv[a],"%d:%d:%31s",&n,&w,clb)!=3) return 2; string cl=clb;
    if(n<6||n>10||w<1||w>3){ fprintf(stderr,"need 6<=n<=10, 1<=w<=3\n"); return 2; }
    int cls=cl=="general"?0:cl=="subcube"?1:cl=="pool"?2:cl=="pairs"?3:-1; if(cls<0) return 2;
    setup(); vector<int> hist(n+2,0); int best=-1; long evaluated=0;
    #pragma omp parallel for schedule(dynamic)
    for(int r=0;r<restarts;r++){
      Gen g; g.w=w; g.cls=cls; g.rng.seed(seed*1000003+r*131+a);
      if(cls==2){ int p=n+2+(int)(g.rng()%(n+1)); for(int i=0;i<p;i++) g.pool.push_back(1+g.rng()%((1<<n)-1)); }
      vector<Sub> c; g.fill(c); g.minimalize(c); int d=pcdegree(c); long ev=1; int first=d;
      for(int s=0;s<steps;s++){ vector<Sub> e=c; int drop=1+g.rng()%2;
        for(int q=0;q<drop&&e.size()>1;q++) e.erase(e.begin()+g.rng()%e.size());
        g.fill(e); g.minimalize(e); int de=pcdegree(e); ev++; if(de>=d){ c=e; d=de; } }
      bool ok=covers(c)&&minimal(c);
      #pragma omp critical
      { hist[first]++; evaluated+=ev; if(d>best) best=d;
        printf("{\"n\":%d,\"w\":%d,\"class\":\"%s\",\"restart\":%d,\"first_degree\":%d,\"climbed_degree\":%d,\"size\":%d,\"valid\":%d,\"cover\":\"%s\"}\n",
               n,w,cl.c_str(),r,first,d,(int)c.size(),(int)ok,show(c).c_str()); fflush(stdout); }
    }
    printf("{\"summary\":true,\"n\":%d,\"w\":%d,\"class\":\"%s\",\"restarts\":%d,\"steps\":%d,\"evaluated\":%ld,\"best_degree\":%d,\"hypothesis\":%d,\"first_degree_histogram\":[",n,w,cl.c_str(),restarts,steps,evaluated,best,(n+1)/2+w);
    for(int i=0;i<=n;i++) printf("%d%s",hist[i],i<n?",":""); printf("]}\n"); fflush(stdout);
  }
  return 0;
}
