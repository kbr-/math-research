// Reduced monic boundary-line certificates; original kernels and last coordinate.
// Reuse FLINT wrappers, finite-field regular representation, square-root scalars,
// polynomial output and compound Cramer solve from the accepted norm generator.
// Stages: reduced alternant source; universal constant pivots; full-degree screen;
// one FLINT factorization/solve; norm-gcd certificate. No custom elimination.
#define main legacy_boundary_main
#include "bmd_boundary_complement_20261006.cpp"
#undef main
using MP=std::unique_ptr<Mat>;
static MP mat(int r,int c,U p){return MP(new Mat(r,c,p));}
static std::vector<MP> blocks(int n,int e,U p){std::vector<MP>v;for(int i=0;i<n;i++)v.push_back(mat(e,e,p));return v;}
static void copy_block(Mat&to,int r,int c,const Mat&from,int e){
 for(int i=0;i<e;i++)for(int j=0;j<e;j++)nmod_poly_set(nmod_poly_mat_entry(to.v,r*e+i,c*e+j),nmod_poly_mat_entry(from.v,i,j));
}
static void matrix_slice(Mat&to,const Mat&from,const std::vector<int>&rr,const std::vector<int>&cc,int e){
 for(size_t i=0;i<rr.size();i++)for(size_t j=0;j<cc.size();j++)for(int a=0;a<e;a++)for(int b=0;b<e;b++)
 nmod_poly_set(nmod_poly_mat_entry(to.v,int(i)*e+a,int(j)*e+b),nmod_poly_mat_entry(from.v,rr[i]*e+a,cc[j]*e+b));
}
struct Reduced{
 MP full,small;std::vector<std::pair<int,int>>pairs;
 std::vector<int>ur,uc,fr,fc;int R=0;
};
static Reduced reduced_source(int n,U p,int e,const Poly&mod,const std::vector<FieldVector>&al,const std::vector<FieldVector>&be,bool control){
 int N=n+1,R=N*(N-1)/2;auto bs=binomials(R+2,p);Reduced out;out.R=R;
 for(int i=0;i<N;i++)for(int j=i+1;j<N;j++)out.pairs.push_back({i,j});
 auto coeff=blocks(N+1,e,p);nmod_poly_mat_one(coeff[0]->v);
 std::vector<MP>root;for(int i=0;i<N;i++){root.push_back(mat(e,e,p));linear_block(*root.back(),al[i],be[i],mod,e,p);}
 Mat tmp(e,e,p),tmp2(e,e,p),dif(e,e,p);
 for(int i=0;i<N;i++){
  auto next=blocks(N+1,e,p);
  for(int j=0;j<=i+1;j++){
   if(j)nmod_poly_mat_set(next[j]->v,coeff[j-1]->v);
   if(j<=i){nmod_poly_mat_mul(tmp.v,root[i]->v,coeff[j]->v);nmod_poly_mat_sub(next[j]->v,next[j]->v,tmp.v);}
  }coeff.swap(next);
 }
 auto pw=blocks((R+2)*N,e,p);
 auto power=[&](int k,int i)->Mat&{return *pw[k*N+i];};
 nmod_poly_mat_one(power(0,0).v);
 for(int k=1;k<=R+1;k++)for(int i=0;i<N;i++){
  nmod_poly_mat_mul(tmp.v,coeff[i]->v,power(k-1,N-1).v);
  if(i)nmod_poly_mat_sub(power(k,i).v,power(k-1,i-1).v,tmp.v);
  else nmod_poly_mat_neg(power(k,i).v,tmp.v);
 }
 out.full=mat(e*R,e*(R+1),p);
 for(int j=0;j<=R;j++){
  int k=j+2;std::vector<U>d(k);U acc=0;
  for(int h=0;h<k;h++){acc=(acc+mul(bs[h],bs[k-h],p))%p;d[h]=acc;}
  for(int h=0;h<k;h++)need((d[h]+d[k-1-h])%p==0,"alternant scalar symmetry");
  bool picked=false;
  for(int h=0;2*h<k-1;h++){
   int v=k-1-h;U c=d[h];if(!c)continue;
   if(!picked&&j<R&&h<N&&v<N){
    auto it=std::find(out.pairs.begin(),out.pairs.end(),std::make_pair(h,v));
    need(it!=out.pairs.end(),"unit row");out.ur.push_back(int(it-out.pairs.begin()));out.uc.push_back(j);picked=true;
   }
   for(int r=0;r<R;r++){
    auto [a,b]=out.pairs[r];
    nmod_poly_mat_mul(tmp.v,power(h,a).v,power(v,b).v);
    nmod_poly_mat_mul(tmp2.v,power(v,a).v,power(h,b).v);
    nmod_poly_mat_sub(dif.v,tmp.v,tmp2.v);nmod_poly_mat_scalar_mul_nmod(dif.v,dif.v,c);
    for(int x=0;x<e;x++)for(int y=0;y<e;y++){
     auto dst=nmod_poly_mat_entry(out.full->v,r*e+x,j*e+y);
     nmod_poly_add(dst,dst,nmod_poly_mat_entry(dif.v,x,y));
    }
   }
  }
 }
 for(int r=0;r<R;r++)for(int c=0;c<=R;c++)for(int i=0;i<e;i++)for(int j=0;j<e;j++)
  need(nmod_poly_is_zero(nmod_poly_mat_entry(out.full->v,r*e+i,c*e+j))||nmod_poly_degree(nmod_poly_mat_entry(out.full->v,r*e+i,c*e+j))<=c+1-out.pairs[r].first-out.pairs[r].second,"reduced source weight");
 if(control){
  int m=R+2;Mat original(e*m,e*(m+1),p);build_source(original,n,al,be,bs,mod,e,p);
  auto rp=blocks(N*N,e,p);
  for(int i=0;i<N;i++)for(int j=0;j<N;j++){if(!j)nmod_poly_mat_one(rp[i*N+j]->v);else nmod_poly_mat_mul(rp[i*N+j]->v,rp[i*N+j-1]->v,root[i]->v);}
  Mat frame(e*R,e*R,p),diffroot(e,e,p),prod(e,e,p);
  for(int r=0;r<R;r++){auto [i,j]=out.pairs[r];nmod_poly_mat_sub(diffroot.v,root[j]->v,root[i]->v);
   for(int c=0;c<R;c++){auto [u,v]=out.pairs[c];
    nmod_poly_mat_mul(tmp.v,rp[i*N+u]->v,rp[j*N+v]->v);
    nmod_poly_mat_mul(tmp2.v,rp[i*N+v]->v,rp[j*N+u]->v);
    nmod_poly_mat_sub(dif.v,tmp.v,tmp2.v);nmod_poly_mat_mul(prod.v,diffroot.v,dif.v);copy_block(frame,r,c,prod,e);
   }
  }
  Mat product(e*R,e*(R+1),p);nmod_poly_mat_mul(product.v,frame.v,out.full->v);
  for(int i=0;i<e*R;i++)for(int j=0;j<e*(R+1);j++)
   need(nmod_poly_equal(nmod_poly_mat_entry(product.v,i,j),nmod_poly_mat_entry(original.v,i+2*e,j+2*e)),"complete original/frame identity");
  std::cout<<"FRAME_CONTROL n="<<n<<" p="<<p<<" polynomial_entries="<<e*e*R*(R+1)<<std::endl;
 }
 std::set<int>rs(out.ur.begin(),out.ur.end()),cs(out.uc.begin(),out.uc.end());
 for(int r=0;r<R;r++)if(!rs.count(r))out.fr.push_back(r);
 for(int c=0;c<=R;c++)if(!cs.count(c))out.fc.push_back(c);
 need(out.fc.back()==R&&out.fc[out.fc.size()-2]==R-1,"marked/adjacent coordinates retained");
 int k=int(out.ur.size()),z=R-k;need(k>0&&z>0,"nontrivial unit reduction");
 Mat UU(e*k,e*k,p),UE(e*k,e*(z+1),p),CU(e*z,e*k,p),DD(e*z,e*(z+1),p),Inv(e*k,e*k,p),IE(e*k,e*(z+1),p),Prod(e*z,e*(z+1),p);Poly den(p);
 matrix_slice(UU,*out.full,out.ur,out.uc,e);matrix_slice(UE,*out.full,out.ur,out.fc,e);
 matrix_slice(CU,*out.full,out.fr,out.uc,e);matrix_slice(DD,*out.full,out.fr,out.fc,e);
 need(nmod_poly_mat_inv(Inv.v,den.v,UU.v),"unit inverse");
 need(nmod_poly_degree(den.v)==0,"constant unit determinant");
 nmod_poly_mat_scalar_mul_nmod(Inv.v,Inv.v,n_invmod(nmod_poly_get_coeff_ui(den.v,0),p));
 Mat identity(e*k,e*k,p);nmod_poly_mat_mul(identity.v,UU.v,Inv.v);need(nmod_poly_mat_is_one(identity.v),"unit inverse identity");
 nmod_poly_mat_mul(IE.v,Inv.v,UE.v);nmod_poly_mat_mul(Prod.v,CU.v,IE.v);
 out.small=mat(e*z,e*(z+1),p);nmod_poly_mat_sub(out.small->v,DD.v,Prod.v);
 for(int r=0;r<z;r++)for(int c=0;c<=z;c++)for(int i=0;i<e;i++)for(int j=0;j<e;j++)
  need(nmod_poly_is_zero(nmod_poly_mat_entry(out.small->v,r*e+i,c*e+j))||nmod_poly_degree(nmod_poly_mat_entry(out.small->v,r*e+i,c*e+j))<=out.fc[c]+1-out.pairs[out.fr[r]].first-out.pairs[out.fr[r]].second,"Schur weight");
 std::cout<<"SOURCE n="<<n<<" p="<<p<<" e="<<e<<" pairs="<<R<<" unit_columns="<<k<<" norm_factor_dimension="<<e*z<<std::endl;
 return out;
}
static U rd_det(const Reduced&src,int e,U p,int point,bool adjacent=false){
 int z=int(src.fr.size()),q=e*z;nmod_mat_t M;nmod_mat_init(M,q,q,p);
 for(int i=0;i<q;i++)for(int j=0;j<q;j++){
  int c=adjacent&&j>=q-e?j+e:j;auto P=nmod_poly_mat_entry(src.small->v,i,c);
  int wt=src.fc[c/e]+1-src.pairs[src.fr[i/e]].first-src.pairs[src.fr[i/e]].second;
  nmod_mat_entry(M,i,j)=point<0?(wt<0?0:nmod_poly_get_coeff_ui(P,wt)):nmod_poly_evaluate_nmod(P,U(point));
 }
 U d=nmod_mat_det(M);nmod_mat_clear(M);return d;
}
static void write_input(std::ostream&f,int n,U p,int e,const Poly&mod,const std::vector<FieldVector>&al,const std::vector<FieldVector>&be){
 f<<"\"cube_dimension\":"<<n<<",\"prime\":"<<p<<",\"field_degree\":"<<e<<",\"modulus\":";write_poly(f,mod.v);
 f<<",\"intercept\":";write_fields(f,al,n);f<<",\"direction\":";write_fields(f,be,n);
}
static FieldVector collision_parameter(const FieldVector&a,const FieldVector&b,const FieldVector&c,const FieldVector&d,const Poly&mod,int e,U p){
 Poly num(p),den(p),inv(p),value(p);
 for(int j=0;j<e;j++){
  nmod_poly_set_coeff_ui(num.v,j,(c[j]+p-a[j])%p);
  nmod_poly_set_coeff_ui(den.v,j,(b[j]+p-d[j])%p);
 }
 need(nmod_poly_invmod(inv.v,den.v,mod.v),"nonzero slope difference");
 nmod_poly_mulmod(value.v,num.v,inv.v,mod.v);
 FieldVector out(e);for(int j=0;j<e;j++)out[j]=nmod_poly_get_coeff_ui(value.v,j);return out;
}
static void separated_line(int n,U p,int e,const Poly&mod,std::mt19937_64&rng,std::vector<FieldVector>&al,std::vector<FieldVector>&be){
 size_t trials=0;
 for(int restart=0;restart<20;restart++){
  al.assign(n+1,FieldVector(e));be=al;
  std::set<FieldVector>betas{FieldVector(e)},roots;bool complete=true;
  for(int i=1;i<=n;i++){
   bool accepted=false;
   for(int trial=0;trial<10000;trial++){
    trials++;FieldVector a(e),b(e);for(int j=0;j<e;j++){a[j]=rng()%p;b[j]=rng()%p;}
    if(betas.count(b))continue;
    std::set<FieldVector>added;bool good=true;
    for(int j=0;j<i;j++){auto root=collision_parameter(a,b,al[j],be[j],mod,e,p);if(roots.count(root)||!added.insert(root).second){good=false;break;}}
    if(!good)continue;
    al[i]=a;be[i]=b;betas.insert(b);roots.insert(added.begin(),added.end());accepted=true;break;
   }
   if(!accepted){complete=false;break;}
  }
  if(complete){need(roots.size()==size_t(n*(n+1)/2),"every collision parameter distinct");std::cout<<"SEPARATED_LINE point_trials="<<trials<<" restarts="<<restart<<" collision_parameters="<<roots.size()<<std::endl;return;}
 }
 throw std::runtime_error("bounded separated-line design exhausted");
}
static bool rd_case(int n,U p,int e,const fs::path&out,bool control,bool separated=false){
 need(n>=4&&n<=9&&p>2&&p<1000&&n_is_prime(p)&&e>=1&&e<=4,"bounded case domain");
 fs::create_directories(out);uint64_t seed=20261010ULL^(uint64_t(p)<<16)^uint64_t(n);std::mt19937_64 rng(seed);
 Poly mod(p);flint_rand_t state;flint_randinit(state);flint_randseed(state,seed,seed+17);
 if(e==1)nmod_poly_set_coeff_ui(mod.v,1,1);else nmod_poly_randtest_monic_irreducible(mod.v,state,e+1);
 flint_randclear(state);need(nmod_poly_is_irreducible(mod.v),"field modulus");
 U order=1;for(int j=0;j<e;j++)order*=p;need(order>U(n),"enough distinct directions");
 for(int attempt=1;attempt<=3;attempt++){
  std::vector<FieldVector>al(n+1,FieldVector(e)),be=al;std::set<FieldVector>used{FieldVector(e)};
  if(separated)separated_line(n,p,e,mod,rng,al,be);else for(int i=1;i<=n;i++){do{for(int j=0;j<e;j++)be[i][j]=rng()%p;}while(used.count(be[i]));used.insert(be[i]);for(int j=0;j<e;j++)al[i][j]=rng()%p;}
  std::string stem="n"+std::to_string(n)+"-p"+std::to_string(p)+"-line"+std::to_string(attempt);
  auto input=out/(stem+"-input.json");need(!fs::exists(input),"refuse input overwrite");{std::ofstream f(input);f<<"{";write_input(f,n,p,e,mod,al,be);f<<",\"seed\":"<<seed<<",\"attempt\":"<<attempt<<",\"separated_collisions\":"<<(separated?"true":"false")<<"}\n";need(bool(f),"input write");}
  auto start=std::chrono::steady_clock::now();std::cout<<"BUILD_START "<<stem<<std::endl;
  auto src=reduced_source(n,p,e,mod,al,be,control);U direction=rd_det(src,e,p,-1);
  if(!direction){std::cout<<"DIRECTION_ZERO "<<stem<<std::endl;continue;}
  int z=int(src.fr.size()),q=e*z,lambda=3*choose4(n+1);
  Mat LU(q,q+e,p),factors(q,q,p),rhs(q,e,p),X(q,e,p);Poly den(p),D0(p),D1(p),Dpow(p),G(p);
  std::vector<slong>perm(q);for(int i=0;i<q;i++)perm[i]=i;
  std::cout<<"FFLU_START "<<stem<<" norm_degree="<<e*lambda<<std::endl;
  need(nmod_poly_mat_fflu(LU.v,den.v,perm.data(),src.small->v,0)==q,"full factor rank");
  nmod_poly_set(D0.v,den.v);need(nmod_poly_degree(D0.v)==e*lambda,"full reduced norm degree");
  for(int i=0;i<q;i++){for(int j=0;j<q;j++)nmod_poly_set(nmod_poly_mat_entry(factors.v,i,j),nmod_poly_mat_entry(LU.v,i,j));for(int j=0;j<e;j++)nmod_poly_set(nmod_poly_mat_entry(rhs.v,i,j),nmod_poly_mat_entry(src.small->v,i,q+j));}
  nmod_poly_mat_solve_fflu_precomp(X.v,perm.data(),factors.v,rhs.v);
  if(control){Mat sq(q,q,p),prod(q,e,p),scaled(q,e,p);for(int i=0;i<q;i++)for(int j=0;j<q;j++)nmod_poly_set(nmod_poly_mat_entry(sq.v,i,j),nmod_poly_mat_entry(src.small->v,i,j));nmod_poly_mat_mul(prod.v,sq.v,X.v);nmod_poly_mat_scalar_mul_nmod_poly(scaled.v,rhs.v,den.v);need(nmod_poly_mat_equal(prod.v,scaled.v),"full solve control");}
  nmod_poly_pow(Dpow.v,D0.v,e-1);compound_minor(D1,X,z-1,e,Dpow,p);nmod_poly_gcd(G.v,D0.v,D1.v);
  std::vector<int>extra_columns;std::vector<std::unique_ptr<Poly>>extras;
  for(int j=z-2;j>=0&&nmod_poly_degree(G.v)>0;j--){extras.emplace_back(new Poly(p));compound_minor(*extras.back(),X,j,e,Dpow,p);extra_columns.push_back(src.fc[j]);nmod_poly_gcd(G.v,G.v,extras.back()->v);}
  U scale=n_invmod(nmod_poly_get_coeff_ui(D0.v,e*lambda),p);nmod_poly_scalar_mul_nmod(D0.v,D0.v,scale);nmod_poly_scalar_mul_nmod(D1.v,D1.v,scale);for(auto&v:extras)nmod_poly_scalar_mul_nmod(v->v,v->v,scale);
  for(int x=0;x<=1;x++){need(nmod_poly_evaluate_nmod(D0.v,x)==mul(rd_det(src,e,p,x),n_invmod(direction,p),p),"initial point control");need(nmod_poly_evaluate_nmod(D1.v,x)==mul(rd_det(src,e,p,x,true),n_invmod(direction,p),p),"adjacent point control");}
  bool ok=nmod_poly_degree(G.v)==0;double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  auto path=out/(stem+".json");need(!fs::exists(path),"refuse certificate overwrite");std::ofstream f(path);
  f<<"{\"status\":\""<<(ok?"certified":"inconclusive")<<"\",";write_input(f,n,p,e,mod,al,be);
  f<<",\"separated_collisions\":"<<(separated?"true":"false")<<",\"seed\":"<<seed<<",\"line_attempt\":"<<attempt<<",\"source\":\"reduced_alternant\",\"pairs\":"<<src.R<<",\"unit_columns\":"<<src.ur.size()<<",\"norm_factor_dimension\":"<<q<<",\"threshold\":"<<lambda<<",\"norm_degree\":"<<e*lambda<<",\"seconds\":"<<seconds<<",\"norm_determinant\":";write_poly(f,D0.v);
  f<<",\"norm_adjacent_minor\":";write_poly(f,D1.v);f<<",\"gcd\":";write_poly(f,G.v);f<<",\"additional_minors\":[";
  for(size_t j=0;j<extras.size();j++){if(j)f<<',';f<<"{\"replaced_column\":"<<extra_columns[j]<<",\"norm\":";write_poly(f,extras[j]->v);f<<'}';}f<<"]}\n";f.close();need(bool(f),"certificate write");
  std::cout<<(ok?"CERTIFIED ":"INCONCLUSIVE ")<<stem<<" gcd_degree="<<nmod_poly_degree(G.v)<<" extra_minors="<<extras.size()<<" seconds="<<seconds<<" path="<<path<<std::endl;
  if(ok)return true;
 }
 return false;
}
int main(int argc,char**argv){try{flint_set_num_threads(1);
 if(argc==3&&std::string(argv[1])=="--controls"){need(rd_case(5,3,4,argv[2],true),"ternary control");need(rd_case(4,5,2,argv[2],true),"quinary control");}
 else if(argc==6&&(std::string(argv[1])=="--case"||std::string(argv[1])=="--separated")){need(rd_case(std::stoi(argv[2]),std::stoul(argv[3]),std::stoi(argv[4]),argv[5],false,std::string(argv[1])=="--separated"),"unresolved after bounded lines");}
 else throw std::runtime_error("usage: --controls OUTDIR | --case/--separated n p e OUTDIR");
 std::cout<<"REDUCED_BOUNDARY_COMPLETED"<<std::endl;return 0;
}catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<std::endl;return 1;}}
