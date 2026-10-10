// One-root parity certificates with a universal support/linear-matroid degree bound.
// Reuse accepted FLINT source, field representation, and compound Cramer helpers.
#define main boundary_reference_main
#include "bmd_boundary_complement_20261006.cpp"
#undef main
struct AxisBound {int upper=0, penalty=0, selected=0;std::vector<int> support;};
static AxisBound axis_bound(int n,U p){
 int m=rows(n);auto bs=binomials(m,p);AxisBound ans;int sum=0;
 for(int i=0;i<m;i++)if(bs[i]){ans.support.push_back(i);sum+=i;}
 int t=int(ans.support.size());need(t>=n,"enough degree-one supported columns");
 // A nonzero degree-one minor must include index0, so its identity column is absent.
 int cols=t-1+m;ans.upper=m*m;
 for(int penalty=-2*m;penalty<=2*m;penalty++){
  std::vector<std::pair<int,int>> order; // label< t-1 = identity; other labels = transfer columns
  for(int j=1;j<t;j++)order.push_back({ans.support[j],j-1});
  for(int j=0;j<m;j++)order.push_back({j+penalty,t-1+j});
  std::stable_sort(order.begin(),order.end(),[](auto a,auto b){return a.first>b.first;});
  nmod_mat_t B;nmod_mat_init(B,t,cols,p);
  for(int c=0;c<cols;c++){int label=order[c].second;
   if(label<t-1)nmod_mat_entry(B,label+1,c)=1;
   else {int out=label-(t-1);for(int i=0;i<t;i++)if(out>=ans.support[i])nmod_mat_entry(B,i,c)=bs[out-ans.support[i]];}
  }
  need(nmod_mat_rref(B)==t,"full linear-matroid row rank");
  int weight=0,count=0;
  for(int i=0;i<t;i++){int j=0;while(j<cols&&!nmod_mat_entry(B,i,j))j++;need(j<cols,"rref pivot");weight+=order[j].first;count+=order[j].second>=t-1;}
  nmod_mat_clear(B);int bound=weight-sum-penalty*n;
  if(bound<ans.upper){ans.upper=bound;ans.penalty=penalty;ans.selected=count;}
 }
 std::cout<<"AXIS_BOUND n="<<n<<" p="<<p<<" original="<<ans.upper<<" reduced="<<ans.upper-n*(n+1)<<" penalty="<<ans.penalty<<" greedy_transfer_count="<<ans.selected<<std::endl;
 return ans;
}
static void axis_input(std::ostream&f,int n,U p,int e,const Poly&mod,const std::vector<FieldVector>&al,const std::vector<FieldVector>&be,const AxisBound&bd){
 f<<"\"cube_dimension\":"<<n<<",\"prime\":"<<p<<",\"field_degree\":"<<e<<",\"modulus\":";write_poly(f,mod.v);
 f<<",\"intercept\":";write_fields(f,al,n);f<<",\"direction\":";write_fields(f,be,n);
 f<<",\"original_degree_bound\":"<<bd.upper<<",\"reduced_degree_bound\":"<<bd.upper-n*(n+1)<<",\"bound_penalty\":"<<bd.penalty<<",\"greedy_transfer_count\":"<<bd.selected;
 f<<",\"support\":[";for(size_t i=0;i<bd.support.size();i++){if(i)f<<',';f<<bd.support[i];}f<<"]";
}
static bool axis_case(int n,U p,int e,const fs::path&out){
 fs::create_directories(out);int m=rows(n),q=e*m,N=n+1;auto bd=axis_bound(n,p);auto bs=binomials(m,p);
 need(bd.upper>=n*N,"nonnegative reduced degree bound");
 uint64_t seed=20261010ULL^(uint64_t(p)<<16)^uint64_t(n);std::mt19937_64 rng(seed);
 Poly mod(p);flint_rand_t state;flint_randinit(state);flint_randseed(state,seed,seed+17);
 if(e==1)nmod_poly_set_coeff_ui(mod.v,1,1);else nmod_poly_randtest_monic_irreducible(mod.v,state,e+1);
 flint_randclear(state);need(nmod_poly_is_irreducible(mod.v),"field modulus");
 for(int attempt=1;attempt<=3;attempt++){
  std::vector<FieldVector>al(n+1,FieldVector(e)),be=al;be[n][0]=1;
  FieldVector one(e);one[0]=1;std::set<FieldVector>used{FieldVector(e),one};
  for(int i=1;i<n;i++){do{for(int j=0;j<e;j++)al[i][j]=rng()%p;}while(used.count(al[i]));used.insert(al[i]);}
  auto stem="n"+std::to_string(n)+"-p"+std::to_string(p)+"-axis"+std::to_string(attempt);
  auto input=out/(stem+"-input.json");need(!fs::exists(input),"refuse input overwrite");
  {std::ofstream f(input);f<<"{";axis_input(f,n,p,e,mod,al,be,bd);f<<",\"seed\":"<<seed<<"}\n";need(bool(f),"input write");}
  auto start=std::chrono::steady_clock::now();std::cout<<"AXIS_BUILD "<<stem<<" norm_dimension="<<q<<" norm_bound="<<e*bd.upper<<std::endl;
  Mat source(q,q+e,p),A(q,q,p),rhs(q,e,p),LU(q,q,p),X(q,e,p);
  build_source(source,n,al,be,bs,mod,e,p);
  int oldr=m-n;std::vector<int>oldrows{0,1};int rr=2;
  for(int i=0;i<N;i++)for(int j=i+1;j<N;j++,rr++)if(j<n)oldrows.push_back(rr);
  need(int(oldrows.size())==oldr,"old source rows");
  nmod_mat_t oldprefix;nmod_mat_init(oldprefix,e*oldr,e*oldr,p);
  for(int i=0;i<e*oldr;i++)for(int j=0;j<e*oldr;j++)
   nmod_mat_entry(oldprefix,i,j)=nmod_poly_get_coeff_ui(nmod_poly_mat_entry(source.v,e*oldrows[i/e]+i%e,j),0);
  slong oldrank=nmod_mat_rank(oldprefix);nmod_mat_clear(oldprefix);
  std::cout<<"OLD_PREFIX_SCREEN "<<stem<<" rank="<<oldrank<<" expected="<<e*oldr<<std::endl;
  if(oldrank!=e*oldr)continue;
  for(int i=0;i<q;i++){for(int j=0;j<q;j++)nmod_poly_set(nmod_poly_mat_entry(A.v,i,j),nmod_poly_mat_entry(source.v,i,j));for(int j=0;j<e;j++)nmod_poly_set(nmod_poly_mat_entry(rhs.v,i,j),nmod_poly_mat_entry(source.v,i,q+j));}
  Poly den(p),D(p),D1(p),Dpow(p),normV(p),VP(p),fac(p),G(p),quot(p),rem(p);
  std::vector<slong>perm(q);for(int i=0;i<q;i++)perm[i]=i;
  std::cout<<"AXIS_FFLU "<<stem<<std::endl;slong rank=nmod_poly_mat_fflu(LU.v,den.v,perm.data(),A.v,0);
  nmod_poly_set(D.v,den.v);
  need(rank<q||nmod_poly_degree(D.v)<=e*bd.upper,"universal upper bound");
  if(rank<q||nmod_poly_degree(D.v)!=e*bd.upper){
   auto path=out/(stem+".json");std::ofstream f(path);f<<"{\"status\":\""<<(rank<q?"rank_deficient":"degree_drop")<<"\",";
   axis_input(f,n,p,e,mod,al,be,bd);f<<",\"rank\":"<<rank<<",\""<<(rank<q?"last_nonzero_factor_pivot":"norm_determinant")<<"\":";
   write_poly(f,D.v);f<<"}\n";
   if(rank<q){std::cout<<"AXIS_RANK_DROP rank="<<rank<<" expected="<<q<<std::endl;continue;}
   std::cout<<"AXIS_DEGREE_DROP degree="<<nmod_poly_degree(D.v)<<" upper="<<e*bd.upper<<std::endl;return false;
  }
  nmod_poly_mat_solve_fflu_precomp(X.v,perm.data(),LU.v,rhs.v);
  Mat AX(q,e,p),scaled(q,e,p);nmod_poly_mat_mul(AX.v,A.v,X.v);nmod_poly_mat_scalar_mul_nmod_poly(scaled.v,rhs.v,den.v);need(nmod_poly_mat_equal(AX.v,scaled.v),"full polynomial solve identity");
  nmod_poly_pow(Dpow.v,D.v,e-1);compound_minor(D1,X,m-1,e,Dpow,p);
  nmod_poly_one(normV.v);
  for(int i=0;i<N;i++)for(int j=i+1;j<N;j++){
   FieldVector da(e),db(e);for(int k=0;k<e;k++){da[k]=(al[j][k]+p-al[i][k])%p;db[k]=(be[j][k]+p-be[i][k])%p;}
   Mat L(e,e,p);linear_block(L,da,db,mod,e,p);nmod_poly_mat_det(fac.v,L.v);nmod_poly_mul(normV.v,normV.v,fac.v);
  }
  need(nmod_poly_degree(normV.v)==e*n,"axis Vandermonde degree");nmod_poly_pow(VP.v,normV.v,N);nmod_poly_make_monic(VP.v,VP.v);
  for(auto z:{D.v,D1.v}){nmod_poly_divrem(quot.v,rem.v,z,VP.v);need(nmod_poly_is_zero(rem.v),"exact axis frame division");}
  nmod_poly_gcd(G.v,D.v,D1.v);std::vector<int>extra;std::vector<std::unique_ptr<Poly>>more;
  for(int j=m-2;j>=2&&!nmod_poly_equal(G.v,VP.v);j--){
   more.emplace_back(new Poly(p));compound_minor(*more.back(),X,j,e,Dpow,p);extra.push_back(j);
   nmod_poly_divrem(quot.v,rem.v,more.back()->v,VP.v);need(nmod_poly_is_zero(rem.v),"additional frame division");nmod_poly_gcd(G.v,G.v,more.back()->v);
  }
  bool ok=nmod_poly_equal(G.v,VP.v);U scale=n_invmod(nmod_poly_get_coeff_ui(D.v,e*bd.upper),p);
  nmod_poly_scalar_mul_nmod(D.v,D.v,scale);nmod_poly_scalar_mul_nmod(D1.v,D1.v,scale);for(auto&z:more)nmod_poly_scalar_mul_nmod(z->v,z->v,scale);
  double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  auto path=out/(stem+".json");need(!fs::exists(path),"refuse result overwrite");std::ofstream f(path);
  f<<"{\"status\":\""<<(ok?"certified":"inconclusive")<<"\",";axis_input(f,n,p,e,mod,al,be,bd);
  f<<",\"seed\":"<<seed<<",\"attempt\":"<<attempt<<",\"seconds\":"<<seconds<<",\"threshold\":"<<3*choose4(N)<<",\"norm_determinant\":";write_poly(f,D.v);
  f<<",\"norm_adjacent_minor\":";write_poly(f,D1.v);f<<",\"norm_vandermonde\":";write_poly(f,normV.v);f<<",\"gcd\":";write_poly(f,G.v);
  f<<",\"additional_norm_minors\":[";for(size_t j=0;j<more.size();j++){if(j)f<<',';f<<"{\"replaced_column\":"<<extra[j]<<",\"norm\":";write_poly(f,more[j]->v);f<<"}";}f<<"]}\n";f.close();need(bool(f),"certificate write");
  std::cout<<(ok?"AXIS_CERTIFIED ":"AXIS_INCONCLUSIVE ")<<stem<<" extra_minors="<<more.size()<<" excess_norm_gcd="<<nmod_poly_degree(G.v)-e*n*N<<" seconds="<<seconds<<std::endl;
  if(ok)return true;
 }return false;
}
int main(int argc,char**argv){try{
 flint_set_num_threads(1);need(argc==3,"usage --bounds/--control/--target OUTDIR");
 fs::path out=argv[2];
 if(std::string(argv[1])=="--bounds"){axis_bound(4,101);axis_bound(9,5);}
 else if(std::string(argv[1])=="--control")need(axis_case(4,101,1,out),"control unresolved");
 else if(std::string(argv[1])=="--target")need(axis_case(9,5,3,out),"target unresolved");
 else throw std::runtime_error("unknown mode");
 std::cout<<"AXIS_PARITY_COMPLETED"<<std::endl;return 0;
}catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<std::endl;return 1;}}
