// Version 2 of odd_prime_direct_sum_20260924/direct_sum.cpp: capped rejection sampling with a reservoir-sample scan for
// sparse allowed sets, and randomized kernel verification (below). Revalidated on every recorded value (revalidate_v2.json).
// One-row closed row freeness via the direct-sum form of the closed algebra (lem:closure-saturation).
// G = sum_S y_S Q_S, Q_S = gr F^{Z_S} (functions on the allowed patterns with holes S occupied, as functions of the
// other holes' occupancy), rho(mu y_S) = sum_{j not in S, j not in mu} [mu]_{S+j} y_{S+j}.
// Kernel verification is randomized: 40 random combinations of the kernel rows are checked exactly on every allowed
// point of the subcube, so a wrong kernel survives with probability at most 3^-40 per block.
// Tested statement: ker(rho: G_k -> G_{k+1}) = rho^{p-1}(G_{k-p+1}) for k <= D-1 (the one-row closure-gluing
// hypothesis); output excess_k = dim ker - dim im, as closed_row_freeness.py reports.
// Q_{S,e} = Mon_e(S^c) / a_{S,e}, a_{S,e} = degree-e parts of polynomials of degree <= e vanishing on Z_S.
// Vanishing polynomials: kernel of evaluation on a random sample of Z_S points (reservoir sample from a full scan when
// Z_S is sparse); random combinations of the kernel vectors are checked on every point of the subcube by a subset-sum
// (zeta) transform, and failures add points and repeat (see the note above on the error bound).
// Input (stdin): p N D m T, then T clauses: k, then k forms (N coefficients) and k values.
// then an integer e3 (-1 for none; otherwise e_3(c) = C(|c|,3) must equal it mod p).
// A pattern c is allowed iff popcount(c) = m mod p, the e3 pin holds, and no clause has all forms equal to its values.
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <vector>
#include <map>
#include <random>
#include <algorithm>
using namespace std;
typedef vector<uint8_t> Vec;
static int P, N, D, M, T, E3 = -1;
static vector<vector<vector<int>>> F; static vector<vector<int>> V;
static int md(int a){ a%=P; return a<0?a+P:a; }
static int inv(int a){ for(int b=1;b<P;b++) if(a*b%P==1) return b; return 0; }
static bool allowed(uint32_t c){
  if(__builtin_popcount(c)%P!=md(M)) return false;
  if(E3>=0){ long w=__builtin_popcount(c); long b=w*(w-1)*(w-2)/6; if(md((int)(b%P))!=E3) return false; }
  for(int t=0;t<T;t++){ bool all=true;
    for(size_t b=0;b<F[t].size()&&all;b++){ int s=0; for(int j=0;j<N;j++) if(c>>j&1) s+=F[t][b][j]; if(md(s)!=V[t][b]) all=false; }
    if(all) return false; }
  return true; }
// row-reduce rows (in place), return pivot columns; rows become reduced echelon
static vector<int> rref(vector<Vec>& R, int ncol){
  vector<int> piv; size_t r=0;
  for(int c=0;c<ncol&&r<R.size();c++){
    size_t q=r; while(q<R.size()&&!R[q][c]) q++; if(q==R.size()) continue; swap(R[r],R[q]);
    int iv=inv(R[r][c]); for(int x=0;x<ncol;x++) R[r][x]=R[r][x]*iv%P;
    for(size_t i=0;i<R.size();i++) if(i!=r&&R[i][c]){ int f=R[i][c]; for(int x=0;x<ncol;x++) R[i][x]=md(R[i][x]-f*R[r][x]); }
    piv.push_back(c); r++; }
  R.resize(r); return piv; }
static int rankOf(vector<Vec> R, int ncol){ return (int)rref(R,ncol).size(); }
struct Block { uint32_t S; int e; vector<uint32_t> mons; map<uint32_t,int> idx; vector<Vec> ech; vector<int> piv; vector<int> basisMon; map<int,int> bpos; };
static map<pair<uint32_t,int>,Block> blocks;
static vector<uint8_t> ALW;
static vector<uint32_t> monsOf(uint32_t S,int e){ vector<uint32_t> out; vector<int> rest; for(int j=0;j<N;j++) if(!(S>>j&1)) rest.push_back(j);
  vector<int> c(e); function<void(int,int)> rec=[&](int st,int d){ if(d==e){ uint32_t m=0; for(int x:c) m|=1u<<x; out.push_back(m); return; }
    for(int i=st;i<(int)rest.size();i++){ c[d]=rest[i]; rec(i+1,d+1);} }; rec(0,0); return out; }
static mt19937_64 rng(12345);
// all points of the subcube containing S that are allowed
static void subcubePoints(uint32_t S, vector<uint32_t>& pts){ vector<int> rest; for(int j=0;j<N;j++) if(!(S>>j&1)) rest.push_back(j);
  uint64_t n=1ull<<rest.size(); for(uint64_t a=0;a<n;a++){ uint32_t c=S; for(size_t i=0;i<rest.size();i++) if(a>>i&1) c|=1u<<rest[i]; if(allowed(c)) pts.push_back(c);} }
static Block& getBlock(uint32_t S,int e){
  auto key=make_pair(S,e); auto it=blocks.find(key); if(it!=blocks.end()) return it->second;
  Block B; B.S=S; B.e=e;
  vector<int> rest; for(int j=0;j<N;j++) if(!(S>>j&1)) rest.push_back(j); int nr=rest.size();
  auto lift=[&](uint64_t a){ uint32_t c=S; for(int i=0;i<nr;i++) if(a>>i&1) c|=1u<<rest[i]; return c; };
  vector<uint32_t> all; for(int d=0;d<=e;d++){ auto ms=monsOf(S,d); all.insert(all.end(),ms.begin(),ms.end()); }
  int nm=all.size(); vector<Vec> kerRows;
  // existence of an allowed point in the subcube, and a random sample
  uint64_t n=1ull<<nr; bool any=false; for(uint64_t a=0;a<n&&!any;a++) if(ALW[lift(a)]) any=true;
  if(!any){ for(int i=0;i<nm;i++){ Vec v(nm,0); v[i]=1; kerRows.push_back(v);} }
  else if(e==0){ /* constants do not vanish on a nonempty set */ }
  else {
    vector<uint32_t> sample; size_t want=3*nm+20; uint64_t tries=0;
    while(sample.size()<want&&tries<64ull*want){ uint64_t a=rng()&(n-1); tries++; uint32_t c=lift(a); if(ALW[c]) sample.push_back(c); }
    if(sample.size()<want){ // sparse allowed set: one scan of the subcube with a uniform reservoir sample
      sample.clear(); uint64_t seen=0;
      for(uint64_t a=0;a<n;a++){ uint32_t c=lift(a); if(!ALW[c]) continue; seen++;
        if(sample.size()<want) sample.push_back(c); else { uint64_t r=rng()%seen; if(r<want) sample[r]=c; } } }
    // local index of monomials within the subcube coordinates
    vector<uint64_t> loc(nm); for(int i=0;i<nm;i++){ uint64_t a=0; for(int q=0;q<nr;q++) if(all[i]>>rest[q]&1) a|=1ull<<q; loc[i]=a; }
    while(true){
      int ns=sample.size(); vector<Vec> A(nm,Vec(ns+nm,0));
      for(int i=0;i<nm;i++){ for(int t=0;t<ns;t++) A[i][t]=((sample[t]&all[i])==all[i]); A[i][ns+i]=1; }
      size_t r=0; for(int c=0;c<ns&&r<A.size();c++){ size_t q=r; while(q<A.size()&&!A[q][c]) q++; if(q==A.size()) continue; swap(A[r],A[q]);
        int iv=inv(A[r][c]); for(auto& x:A[r]) x=x*iv%P;
        #pragma omp parallel for
        for(size_t i=0;i<A.size();i++) if(i!=r&&A[i][c]){ int f=A[i][c]; for(int x=0;x<ns+nm;x++) A[i][x]=md(A[i][x]-f*A[r][x]); } r++; }
      kerRows.clear(); for(size_t i=r;i<A.size();i++) kerRows.push_back(Vec(A[i].begin()+ns,A[i].end()));
      // verification: VERIFY random combinations of the kernel rows (all of them when there are fewer); a kernel row
      // nonzero at an allowed point makes a random combination nonzero there with probability 2/3, so all VERIFY
      // combinations miss it with probability at most 3^-VERIFY
      const size_t VERIFY=40; vector<Vec> checks;
      if(kerRows.size()<=VERIFY) checks=kerRows;
      else for(size_t q=0;q<VERIFY;q++){ Vec v(nm,0); for(auto& kr:kerRows){ int r=rng()%P; if(r) for(int i=0;i<nm;i++) if(kr[i]) v[i]=md(v[i]+r*kr[i]); } checks.push_back(v); }
      vector<uint32_t> add(checks.size(),0); vector<char> bad(checks.size(),0);
      #pragma omp parallel for schedule(dynamic)
      for(size_t k=0;k<checks.size();k++){
        vector<uint8_t> a(n,0); for(int i=0;i<nm;i++) if(checks[k][i]) a[loc[i]]=checks[k][i];
        for(int b=0;b<nr;b++){ uint64_t bit=1ull<<b; for(uint64_t x=0;x<n;x++) if(x&bit) a[x]=(a[x]+a[x^bit])%P; }
        for(uint64_t x=0;x<n;x++) if(a[x]){ uint32_t c=lift(x); if(ALW[c]){ bad[k]=1; add[k]=c; break; } } }
      bool ok=true; for(size_t k=0;k<checks.size();k++) if(bad[k]){ ok=false; sample.push_back(add[k]); }
      if(ok) break;
    }
  }
  auto top=monsOf(S,e); B.mons=top; for(size_t i=0;i<top.size();i++) B.idx[top[i]]=i;
  int off=nm-(int)top.size();
  vector<Vec> tr; for(auto& kv:kerRows){ Vec v(kv.begin()+off,kv.end()); bool nz=false; for(auto x:v) if(x) nz=true; if(nz) tr.push_back(v); }
  B.piv=rref(tr,top.size()); B.ech=tr;
  vector<char> isp(top.size(),0); for(int c:B.piv) isp[c]=1;
  for(size_t i=0;i<top.size();i++) if(!isp[i]){ B.bpos[i]=B.basisMon.size(); B.basisMon.push_back(i); }
  return blocks.emplace(key,B).first->second; }
// reduce a unit monomial of block (S,e) to basis coordinates
static void addReduced(Block& B, uint32_t mono, int coef, Vec& out, int base){
  auto it=B.idx.find(mono); if(it==B.idx.end()) return; int col=it->second;
  Vec v(B.mons.size(),0); v[col]=md(coef);
  for(size_t r=0;r<B.ech.size();r++){ int c=B.piv[r]; if(v[c]){ int f=v[c]; for(size_t x=0;x<v.size();x++) v[x]=md(v[x]-f*B.ech[r][x]); } }
  for(auto& kv:B.bpos) if(v[kv.first]) out[base+kv.second]=md(out[base+kv.second]+v[kv.first]); }
static vector<uint32_t> subsets(int t){ vector<uint32_t> out; vector<int> c(t); function<void(int,int)> rec=[&](int st,int d){ if(d==t){ uint32_t m=0; for(int x:c) m|=1u<<x; out.push_back(m); return;} for(int i=st;i<N;i++){ c[d]=i; rec(i+1,d+1);} }; rec(0,0); return out; }
struct Level { vector<pair<uint32_t,int>> blk; vector<int> off; int dim=0; map<pair<uint32_t,int>,int> pos; };
static Level level(int k){ Level L; for(int t=0;t<=k;t++) for(uint32_t S:subsets(t)){ Block& B=getBlock(S,k-t); L.pos[{S,k-t}]=L.blk.size(); L.blk.push_back({S,k-t}); L.off.push_back(L.dim); L.dim+=B.basisMon.size(); } return L; }
// matrix of rho: rows = basis of level k, cols = basis of level k+1
static vector<Vec> rhoMat(Level& A, Level& Bl){
  vector<Vec> R;
  for(size_t b=0;b<A.blk.size();b++){ uint32_t S=A.blk[b].first; int e=A.blk[b].second; Block& X=getBlock(S,e);
    for(int bm:X.basisMon){ uint32_t mu=X.mons[bm]; Vec row(Bl.dim,0);
      for(int j=0;j<N;j++) if(!(S>>j&1)&&!(mu>>j&1)){ uint32_t S2=S|1u<<j; auto it=Bl.pos.find({S2,e}); if(it==Bl.pos.end()) continue; Block& Y=getBlock(S2,e); addReduced(Y,mu,1,row,Bl.off[it->second]); }
      R.push_back(row); } }
  return R; }
static vector<Vec> mul(const vector<Vec>& A,const vector<Vec>& B,int ncol){ vector<Vec> C(A.size(),Vec(ncol,0));
  for(size_t i=0;i<A.size();i++) for(size_t k=0;k<B.size();k++) if(A[i][k]) for(int j=0;j<ncol;j++) if(B[k][j]) C[i][j]=md(C[i][j]+A[i][k]*B[k][j]); return C; }
int main(){
  if(scanf("%d %d %d %d %d",&P,&N,&D,&M,&T)!=5) return 1; F.resize(T); V.resize(T);
  for(int t=0;t<T;t++){ int k; if(scanf("%d",&k)!=1) return 1; F[t].assign(k,vector<int>(N)); V[t].resize(k);
    for(int b=0;b<k;b++) for(int j=0;j<N;j++) if(scanf("%d",&F[t][b][j])!=1) return 1; for(int b=0;b<k;b++) if(scanf("%d",&V[t][b])!=1) return 1; }
  if(scanf("%d",&E3)!=1) E3=-1;
  ALW.assign(1ull<<N,0);
  #pragma omp parallel for
  for(long long c=0;c<(1ll<<N);c++) ALW[c]=allowed((uint32_t)c);
  vector<Level> Ls; for(int k=0;k<=D;k++){ Ls.push_back(level(k)); fprintf(stderr,"level %d dim %d\n",k,Ls[k].dim); }
  vector<vector<Vec>> rho(D); for(int k=0;k<D;k++) rho[k]=rhoMat(Ls[k],Ls[k+1]);
  printf("{\"dims\": ["); for(int k=0;k<=D;k++) printf("%s%d",k?", ":"",Ls[k].dim); printf("], \"excess\": [");
  for(int k=0;k<D;k++){ int rk=rankOf(rho[k],Ls[k+1].dim); int ker=Ls[k].dim-rk; int im=0;
    if(k-(P-1)>=0){ vector<Vec> C=rho[k-(P-1)]; for(int s=k-(P-1)+1;s<k;s++) C=mul(C,rho[s],Ls[s+1].dim); im=rankOf(C,Ls[k].dim); }
    printf("%s%d",k?", ":"",ker-im); fflush(stdout); }
  printf("]}\n"); return 0; }
