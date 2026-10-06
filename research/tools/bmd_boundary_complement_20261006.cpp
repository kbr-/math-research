// Exact99-case complement of the boundary-prime theorem, dimensions4..8.
// Linear restrictions over F_(p^e), p^e>=4096. Regular-representation blocks turn
// each field-valued polynomial matrix into a prime-field polynomial matrix.
// Its determinant is the field norm. Full norm degree preserves every factor;
// gcd of norms equal to Norm(V)^(n+1) implies primitive original cofactors.
// One FLINT fraction-free factorization and a precomputed solve supply compound
// Cramer minors. No hand-written elimination or extension-field multiplication.
// Root powers are shared across all requested dimensions at one prime.
// --case n p OUTDIR [e]: control/sizing. --series OUTDIR [4:17,8:11]: exact99
// pairs, optionally reusing only these two saved, independently checked pilots.
#include <flint/nmod_poly_mat.h>
#include <flint/nmod_poly_factor.h>
#include <flint/nmod_mat.h>
#include <flint/ulong_extras.h>
#include <algorithm>
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <mutex>
#include <random>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <omp.h>
using U=mp_limb_t;using FieldVector=std::vector<U>;
namespace fs=std::filesystem;
static std::mutex output_mutex;
static void need(bool c,const std::string&s){if(!c)throw std::runtime_error(s);}
struct Poly{nmod_poly_t v;explicit Poly(U p){nmod_poly_init(v,p);}~Poly(){nmod_poly_clear(v);}Poly(const Poly&)=delete;};
struct Mat{nmod_poly_mat_t v;Mat(int r,int c,U p){nmod_poly_mat_init(v,r,c,p);}~Mat(){nmod_poly_mat_clear(v);}Mat(const Mat&)=delete;};
static int rows(int n){return n*(n+1)/2+2;}
static int choose4(int N){return N*(N-1)*(N-2)*(N-3)/24;}
static U mul(U a,U b,U p){return a*b%p;}
static std::vector<U> binomials(int m,U p){
 std::vector<U>b(m+1);b[0]=1;b[1]=(p+1)/2;
 for(int k=2;k<=m;k++){U z=0;for(int j=1;j<k;j++)z=(z+mul(b[j],b[k-j],p))%p;b[k]=mul((p-z)%p,(p+1)/2,p);}
 for(int k=0;k<=m;k++){U z=0;for(int j=0;j<=k;j++)z=(z+mul(b[j],b[k-j],p))%p;need(z==U(k<=1),"square-root coefficient identity");}return b;
}
static void write_poly(std::ostream&o,const nmod_poly_struct*p){o<<'[';for(slong i=0;i<p->length;i++){if(i)o<<',';o<<nmod_poly_get_coeff_ui(p,i);}o<<']';}
static void write_fields(std::ostream&o,const std::vector<FieldVector>&v,int n){o<<'[';for(int i=1;i<=n;i++){if(i>1)o<<',';o<<'[';for(size_t j=0;j<v[i].size();j++){if(j)o<<',';o<<v[i][j];}o<<']';}o<<']';}
static fs::path result_path(const fs::path&out,int n,U p){return out/("n"+std::to_string(n)+"-p"+std::to_string(p)+".json");}
// Multiplication by alpha+X beta in F_p[z]/(modulus), in basis1,z,...,z^(e-1).
static void linear_block(Mat&L,const FieldVector&alpha,const FieldVector&beta,const Poly&modulus,int e,U p){
 Poly a(p),b(p),shift(p),rem(p);for(int i=0;i<e;i++){nmod_poly_set_coeff_ui(a.v,i,alpha[i]);nmod_poly_set_coeff_ui(b.v,i,beta[i]);}
 for(int j=0;j<e;j++){
  nmod_poly_shift_left(shift.v,a.v,j);nmod_poly_rem(rem.v,shift.v,modulus.v);
  for(int i=0;i<e;i++)nmod_poly_set_coeff_ui(nmod_poly_mat_entry(L.v,i,j),0,nmod_poly_get_coeff_ui(rem.v,i));
  nmod_poly_shift_left(shift.v,b.v,j);nmod_poly_rem(rem.v,shift.v,modulus.v);
  for(int i=0;i<e;i++)nmod_poly_set_coeff_ui(nmod_poly_mat_entry(L.v,i,j),1,nmod_poly_get_coeff_ui(rem.v,i));
 }
}
static void build_source(Mat&A,int n,const std::vector<FieldVector>&alpha,const std::vector<FieldVector>&beta,const std::vector<U>&b,const Poly&modulus,int e,U p){
 int m=rows(n),N=n+1;std::vector<std::unique_ptr<Mat>> pw;pw.reserve(size_t(N)*(m+1));
 for(int i=0;i<N;i++){
  Mat L(e,e,p);linear_block(L,alpha[i],beta[i],modulus,e,p);
  for(int k=0;k<=m;k++){pw.emplace_back(new Mat(e,e,p));if(!k)nmod_poly_mat_one(pw.back()->v);else nmod_poly_mat_mul(pw.back()->v,pw[size_t(i)*(m+1)+k-1]->v,L.v);}
 }
 for(int z=0;z<e;z++){nmod_poly_one(nmod_poly_mat_entry(A.v,z,z));nmod_poly_one(nmod_poly_mat_entry(A.v,e+z,e+z));}
 Mat product(e,e,p);int rr=2;
 for(int i=0;i<N;i++)for(int j=i+1;j<N;j++,rr++)for(int k=0;k<=m;k++)for(int l=0;l<=k;l++){
  U c=mul(b[l],b[k-l],p);if(!c)continue;
  nmod_poly_mat_mul(product.v,pw[size_t(i)*(m+1)+l]->v,pw[size_t(j)*(m+1)+k-l]->v);
  nmod_poly_mat_scalar_mul_nmod(product.v,product.v,c);
  for(int u=0;u<e;u++)for(int v=0;v<e;v++){
   auto dst=nmod_poly_mat_entry(A.v,rr*e+u,k*e+v);nmod_poly_add(dst,dst,nmod_poly_mat_entry(product.v,u,v));
  }
 }
 need(rr==m,"all original pair rows");
}
static void extract_source(Mat&A,const Mat&full,int n,int maxn,int e){
 int m=rows(n);for(int rr=0;rr<2;rr++)for(int k=0;k<=m;k++)for(int u=0;u<e;u++)for(int v=0;v<e;v++)nmod_poly_set(nmod_poly_mat_entry(A.v,rr*e+u,k*e+v),nmod_poly_mat_entry(full.v,rr*e+u,k*e+v));
 int rr=2,src=2;for(int i=0;i<=maxn;i++)for(int j=i+1;j<=maxn;j++,src++)if(j<=n){for(int k=0;k<=m;k++)for(int u=0;u<e;u++)for(int v=0;v<e;v++)nmod_poly_set(nmod_poly_mat_entry(A.v,rr*e+u,k*e+v),nmod_poly_mat_entry(full.v,src*e+u,k*e+v));rr++;}
 need(rr==m,"nested source extraction");
}
static U constant_det(const Mat&A,int m,int e,U p,int point,bool companion=false){
 int q=m*e;nmod_mat_t M;nmod_mat_init(M,q,q,p);
 for(int i=0;i<q;i++)for(int j=0;j<q;j++){
  int source=(companion&&j>=q-e)?j+e:j;auto poly=nmod_poly_mat_entry(A.v,i,source);U value;
  if(point<0){value=i<2*e?(i==j?1:0):nmod_poly_get_coeff_ui(poly,source/e);}else value=nmod_poly_evaluate_nmod(poly,U(point));
  nmod_mat_entry(M,i,j)=value;
 }
 U d=nmod_mat_det(M);nmod_mat_clear(M);return d;
}
static void compound_minor(Poly&result,const Mat&X,int column,int e,const Poly&Dpower,U p){
 Mat block(e,e,p);Poly numerator(p),rem(p);for(int i=0;i<e;i++)for(int j=0;j<e;j++)nmod_poly_set(nmod_poly_mat_entry(block.v,i,j),nmod_poly_mat_entry(X.v,column*e+i,j));
 nmod_poly_mat_det(numerator.v,block.v);nmod_poly_divrem(result.v,rem.v,numerator.v,Dpower.v);need(nmod_poly_is_zero(rem.v),"compound Cramer division");
}
static bool certify(const Mat&A,int n,U p,int e,const Poly&modulus,const std::vector<FieldVector>&alpha,const std::vector<FieldVector>&beta,int attempt,uint64_t seed,const fs::path&out){
 auto start=std::chrono::steady_clock::now();int N=n+1,m=rows(n),q=e*m,R=N*(N-1)/2,lambda=3*choose4(N),degree=N*R+lambda;
 U direction_det=constant_det(A,m,e,p,-1);if(!direction_det)return false;
 Mat LU(q,q+e,p),square(q,q,p),factors(q,q,p),rhs(q,e,p),X(q,e,p);Poly den(p),D(p),Dp(p),Dpower(p),normV(p),VP(p),factor(p),gcd(p),quot(p),rem(p);
 std::vector<slong>perm(q);for(int i=0;i<q;i++)perm[i]=i;
 slong rank=nmod_poly_mat_fflu(LU.v,den.v,perm.data(),A.v,0);need(rank==q,"full norm rank after direction test");
 nmod_poly_set(D.v,nmod_poly_mat_entry(LU.v,q-1,q-1));need(nmod_poly_equal(D.v,den.v),"norm denominator pivot");need(nmod_poly_degree(D.v)==e*degree,"full norm degree");
 for(int i=0;i<q;i++){
  for(int j=0;j<q;j++){nmod_poly_set(nmod_poly_mat_entry(square.v,i,j),nmod_poly_mat_entry(A.v,i,j));nmod_poly_set(nmod_poly_mat_entry(factors.v,i,j),nmod_poly_mat_entry(LU.v,i,j));}
  for(int j=0;j<e;j++)nmod_poly_set(nmod_poly_mat_entry(rhs.v,i,j),nmod_poly_mat_entry(A.v,i,q+j));
 }
 nmod_poly_mat_solve_fflu_precomp(X.v,perm.data(),factors.v,rhs.v);
 if(n==4&&p==17){Mat AX(q,e,p),scaled(q,e,p);nmod_poly_mat_mul(AX.v,square.v,X.v);nmod_poly_mat_scalar_mul_nmod_poly(scaled.v,rhs.v,den.v);need(nmod_poly_mat_equal(AX.v,scaled.v),"complete control adjugate identity");}
 nmod_poly_pow(Dpower.v,D.v,e-1);compound_minor(Dp,X,m-1,e,Dpower,p);
 nmod_poly_one(normV.v);for(int i=0;i<N;i++)for(int j=i+1;j<N;j++){
  FieldVector da(e),db(e);for(int k=0;k<e;k++){da[k]=(alpha[j][k]+p-alpha[i][k])%p;db[k]=(beta[j][k]+p-beta[i][k])%p;}
  Mat L(e,e,p);linear_block(L,da,db,modulus,e,p);nmod_poly_mat_det(factor.v,L.v);nmod_poly_mul(normV.v,normV.v,factor.v);
 }
 need(nmod_poly_degree(normV.v)==e*R,"full norm Vandermonde degree");nmod_poly_pow(VP.v,normV.v,N);nmod_poly_make_monic(VP.v,VP.v);
 nmod_poly_divrem(quot.v,rem.v,D.v,VP.v);need(nmod_poly_is_zero(rem.v),"initial norm frame division");
 nmod_poly_divrem(quot.v,rem.v,Dp.v,VP.v);need(nmod_poly_is_zero(rem.v),"adjacent norm frame division");
 nmod_poly_gcd(gcd.v,D.v,Dp.v);bool all=!nmod_poly_equal(gcd.v,VP.v);std::vector<std::unique_ptr<Poly>>more;
 if(all){for(int j=0;j<m;j++){more.emplace_back(new Poly(p));compound_minor(*more.back(),X,j,e,Dpower,p);nmod_poly_divrem(quot.v,rem.v,more.back()->v,VP.v);need(nmod_poly_is_zero(rem.v),"all norm frame divisions");nmod_poly_gcd(gcd.v,gcd.v,more.back()->v);}}
 if(!nmod_poly_equal(gcd.v,VP.v)){std::lock_guard<std::mutex>lock(output_mutex);std::cout<<"INCONCLUSIVE n="<<n<<" p="<<p<<" line="<<attempt<<" excess_norm_gcd="<<nmod_poly_degree(gcd.v)-e*N*R<<std::endl;return false;}
 U scale=n_invmod(nmod_poly_get_coeff_ui(D.v,e*degree),p);nmod_poly_scalar_mul_nmod(D.v,D.v,scale);nmod_poly_scalar_mul_nmod(Dp.v,Dp.v,scale);
 for(int x=0;x<=1;x++){
  U first=mul(constant_det(A,m,e,p,x),n_invmod(direction_det,p),p),second=mul(constant_det(A,m,e,p,x,true),n_invmod(direction_det,p),p);
  need(nmod_poly_evaluate_nmod(D.v,x)==first&&nmod_poly_evaluate_nmod(Dp.v,x)==second,"two independent constant-matrix determinant controls");
 }
 auto path=result_path(out,n,p);need(!fs::exists(path),"refusing overwrite "+path.string());std::ofstream f(path);need(bool(f),"open certificate");double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
 f<<"{\n\"status\":\"certified\",\"cube_dimension\":"<<n<<",\"prime\":"<<p<<",\"field_degree\":"<<e<<",\"matrix_dimension\":"<<m<<",\"norm_matrix_dimension\":"<<q<<",\"full_degree\":"<<degree<<",\"norm_degree\":"<<e*degree<<",\"gcd_degree\":"<<e*N*R<<",\"threshold\":"<<lambda<<",\"line_attempt\":"<<attempt<<",\"seed\":"<<seed<<",\"seconds\":"<<seconds<<",\"all_cofactors\":"<<(all?"true":"false")<<",\n\"modulus\":";write_poly(f,modulus.v);
 f<<",\n\"intercept\":";write_fields(f,alpha,n);f<<",\n\"direction\":";write_fields(f,beta,n);f<<",\n\"norm_determinant\":";write_poly(f,D.v);f<<",\n\"norm_adjacent_minor\":";write_poly(f,Dp.v);f<<",\n\"norm_vandermonde\":";write_poly(f,normV.v);f<<",\n\"gcd\":";write_poly(f,gcd.v);
 f<<",\n\"additional_norm_minors\":[";for(size_t j=0;j<more.size();j++){if(j)f<<',';nmod_poly_scalar_mul_nmod(more[j]->v,more[j]->v,scale);write_poly(f,more[j]->v);}f<<"]\n}\n";f.close();need(bool(f),"write certificate");
 {std::lock_guard<std::mutex>lock(output_mutex);std::cout<<"PASS n="<<n<<" p="<<p<<" e="<<e<<" norm_dimension="<<q<<" degree="<<e*degree<<" gcd_degree="<<e*N*R<<" all_cofactors="<<all<<" line="<<attempt<<" seconds="<<seconds<<std::endl;}return true;
}
static bool group(U p,std::vector<int>ns,const fs::path&out,int forced_e=0){
 int maxn=*std::max_element(ns.begin(),ns.end()),m=rows(maxn),e=1;U order=p;while(order<4096){order*=p;e++;}if(forced_e)e=forced_e;
 need(p>2&&p<1000000000UL&&n_is_prime(p)&&e>=1&&e<=4,"admissible finite field");
 uint64_t seed=20261006ULL^(uint64_t(p)<<16)^uint64_t(maxn);std::mt19937_64 rng(seed);flint_rand_t state;flint_randinit(state);flint_randseed(state,seed,seed+17);Poly modulus(p);
 if(e==1)nmod_poly_set_coeff_ui(modulus.v,1,1);else nmod_poly_randtest_monic_irreducible(modulus.v,state,e+1);flint_randclear(state);need(nmod_poly_is_irreducible(modulus.v),"irreducible field modulus");
 auto bs=binomials(m,p);std::vector<FieldVector>alpha(maxn+1,FieldVector(e)),beta=alpha;
 for(int attempt=1;attempt<=6&&!ns.empty();attempt++){
  std::set<FieldVector>used{FieldVector(e)};for(int i=1;i<=maxn;i++){do{for(int j=0;j<e;j++)beta[i][j]=rng()%p;}while(used.count(beta[i]));used.insert(beta[i]);for(int j=0;j<e;j++)alpha[i][j]=rng()%p;}
  Mat full(e*m,e*(m+1),p);build_source(full,maxn,alpha,beta,bs,modulus,e,p);std::vector<int>pending;
  for(int n:ns){Mat A(e*rows(n),e*(rows(n)+1),p);extract_source(A,full,n,maxn,e);if(!certify(A,n,p,e,modulus,alpha,beta,attempt,seed,out))pending.push_back(n);}ns.swap(pending);
 }
 if(!ns.empty()){std::lock_guard<std::mutex>lock(output_mutex);for(int n:ns)std::cout<<"UNRESOLVED n="<<n<<" p="<<p<<" after6 lines"<<std::endl;return false;}return true;
}
int main(int argc,char**argv){try{
 std::map<U,std::vector<int>>groups;std::set<std::pair<int,U>>exclude;fs::path out;bool series=false;int forced_e=0;
 if((argc==5||argc==6)&&std::string(argv[1])=="--case"){int n=std::stoi(argv[2]);U p=std::stoul(argv[3]);need(n>=4&&n<=8,"cube dimension4..8");out=argv[4];groups[p].push_back(n);if(argc==6)forced_e=std::stoi(argv[5]);}
 else if((argc==3||argc==4)&&std::string(argv[1])=="--series"){
  series=true;out=argv[2];if(argc==4){std::stringstream q(argv[3]);std::string item;while(std::getline(q,item,',')){auto c=item.find(':');need(c!=std::string::npos,"pilot exclusion syntax");exclude.insert({std::stoi(item.substr(0,c)),std::stoul(item.substr(c+1))});}}
  int total=0;for(int n=4;n<=8;n++){int N=n+1,bound=std::max(N*(N-1)+1,3*choose4(N)),old=n<=7?(1<<n):7;for(U p=old+1;p<=U(bound);p++)if(n_is_prime(p)){total++;if(exclude.count({n,p})){need(fs::exists(result_path(out,n,p)),"excluded pilot missing");continue;}groups[p].push_back(n);}}
  need(total==99,"exact finite complement inventory");need(exclude.size()<=2,"at most two verified pilots");for(auto np:exclude)need((np.first==4&&np.second==17)||(np.first==8&&np.second==11),"unexpected pilot exclusion");
  std::cout<<"INVENTORY total99 reused="<<exclude.size()<<" new="<<99-exclude.size()<<" prime_groups="<<groups.size()<<std::endl;
 }else throw std::runtime_error("usage: --case n p OUTDIR [e] | --series OUTDIR [4:17,8:11]");
 fs::create_directories(out);for(auto&g:groups)for(int n:g.second)need(!fs::exists(result_path(out,n,g.first)),"output already exists");
 flint_set_num_threads(1);std::vector<std::pair<U,std::vector<int>>>jobs(groups.begin(),groups.end());int failed=0,workers=series?4:1;
 #pragma omp parallel for schedule(dynamic) num_threads(workers) reduction(+:failed)
 for(size_t i=0;i<jobs.size();i++){try{if(!group(jobs[i].first,jobs[i].second,out,forced_e))failed++;}catch(const std::exception&e){std::lock_guard<std::mutex>lock(output_mutex);std::cerr<<"ERROR p="<<jobs[i].first<<" "<<e.what()<<std::endl;failed++;}}
 std::cout<<"DONE failed_groups="<<failed<<std::endl;return failed?2:0;
}catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<std::endl;return 1;}}
