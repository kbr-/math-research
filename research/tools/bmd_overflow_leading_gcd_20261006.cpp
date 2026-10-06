// Test polynomial primitivity of the actual overflow leading-cofactor vector.
// Reuses the reviewed FLINT norm/compound-Cramer primitives, not its case series.
#define main archived_boundary_main
#include "bmd_boundary_complement_20261006.cpp"
#undef main
static void overflow_source(Mat&H,int n,int q,const std::vector<FieldVector>&a,const std::vector<FieldVector>&b,const Poly&modulus,int e){
 const U p=3;int m=rows(n),r=rows(n-1),alpha=(q+1)/2,t=m-q;auto bs=binomials(q-1,p);
 std::vector<std::unique_ptr<Mat>> pw;pw.reserve(n*q);
 for(int i=0;i<n;i++){Mat L(e,e,p);linear_block(L,a[i],b[i],modulus,e,p);for(int k=0;k<q;k++){pw.emplace_back(new Mat(e,e,p));if(!k)nmod_poly_mat_one(pw.back()->v);else nmod_poly_mat_mul(pw.back()->v,pw[i*q+k-1]->v,L.v);}}
 for(int z=0;z<e;z++){nmod_poly_one(nmod_poly_mat_entry(H.v,z,z));nmod_poly_one(nmod_poly_mat_entry(H.v,e+z,e+z));}
 Mat term(e,e,p);int rr=2;
 for(int i=0;i<n;i++)for(int j=i+1;j<n;j++,rr++)for(int k=0;k<q;k++)for(int l=0;l<=k;l++){
  U c=mul(bs[l],bs[k-l],p);if(!c)continue;nmod_poly_mat_mul(term.v,pw[i*q+l]->v,pw[j*q+k-l]->v);nmod_poly_mat_scalar_mul_nmod(term.v,term.v,c);
  for(int u=0;u<e;u++)for(int v=0;v<e;v++){auto dst=nmod_poly_mat_entry(H.v,rr*e+u,k*e+v);nmod_poly_add(dst,dst,nmod_poly_mat_entry(term.v,u,v));}
 }
 need(rr==r,"exact old degree-two block");
 for(int i=0;i<n;i++)for(int k=0;k<=m;k++){
  int degree=k<q?k-alpha:k-q;if(degree<0)continue;need(degree<q,"F degree range");
  for(int u=0;u<e;u++)for(int v=0;v<e;v++)nmod_poly_scalar_mul_nmod(nmod_poly_mat_entry(H.v,(r+i)*e+u,k*e+v),nmod_poly_mat_entry(pw[i*q+degree]->v,u,v),bs[degree]);
 }
 need(t+1<=n&&t<(q-1)/2,"overflow hypothesis");
}
int main(int argc,char**argv){try{
 need(argc==3,"usage: binary control|target OUT.json");std::string mode=argv[1];int n=mode=="control"?4:7,q=mode=="control"?9:27,e=mode=="control"?3:4;need(mode=="control"||mode=="target","mode");fs::path out=argv[2];need(!fs::exists(out),"refuse overwrite");const U p=3;int m=rows(n),dim=m*e,ref=2,alpha=(q+1)/2,tail=m-q,a_count=tail+1,D=n*alpha+a_count*(q-alpha),degree=m*(m+1)/2-ref-1-D;
 uint64_t seed=2026100617ULL+n;std::mt19937_64 rng(seed);flint_rand_t state;flint_randinit(state);flint_randseed(state,seed,seed+17);Poly modulus(p);nmod_poly_randtest_monic_irreducible(modulus.v,state,e+1);flint_randclear(state);need(nmod_poly_is_irreducible(modulus.v),"field");
 std::vector<FieldVector>av(n,FieldVector(e)),bv=av;std::set<FieldVector>used{FieldVector(e)};for(int i=1;i<n;i++){do{for(int j=0;j<e;j++)bv[i][j]=rng()%p;}while(used.count(bv[i]));used.insert(bv[i]);for(int j=0;j<e;j++)av[i][j]=rng()%p;}
 Mat H(dim,dim+e,p),A(dim,dim+e,p);overflow_source(H,n,q,av,bv,modulus,e);std::vector<int>order;for(int j=0;j<=m;j++)if(j!=ref)order.push_back(j);order.push_back(ref);
 for(int j=0;j<=m;j++)for(int i=0;i<dim;i++)for(int k=0;k<e;k++)nmod_poly_set(nmod_poly_mat_entry(A.v,i,j*e+k),nmod_poly_mat_entry(H.v,i,order[j]*e+k));
 std::cout<<"SOURCE n="<<n<<" q="<<q<<" e="<<e<<" norm_dimension="<<dim<<" reference_degree="<<degree*e<<std::endl;
 Mat LU(dim,dim+e,p),factors(dim,dim,p),rhs(dim,e,p),X(dim,e,p);Poly den(p),det(p),dpow(p),gcd(p),normV(p),frame(p),factor(p),quot(p),rem(p);std::vector<slong>perm(dim);for(int i=0;i<dim;i++)perm[i]=i;
 slong rank=nmod_poly_mat_fflu(LU.v,den.v,perm.data(),A.v,0);need(rank==dim,"reference full rank");nmod_poly_set(det.v,den.v);need(nmod_poly_degree(det.v)==e*degree,"reference retains full weight");
 for(int i=0;i<dim;i++){for(int j=0;j<dim;j++)nmod_poly_set(nmod_poly_mat_entry(factors.v,i,j),nmod_poly_mat_entry(LU.v,i,j));for(int j=0;j<e;j++)nmod_poly_set(nmod_poly_mat_entry(rhs.v,i,j),nmod_poly_mat_entry(A.v,i,dim+j));}
 nmod_poly_mat_solve_fflu_precomp(X.v,perm.data(),factors.v,rhs.v);nmod_poly_pow(dpow.v,det.v,e-1);nmod_poly_one(normV.v);
 for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){FieldVector da(e),db(e);for(int k=0;k<e;k++){da[k]=(av[j][k]+p-av[i][k])%p;db[k]=(bv[j][k]+p-bv[i][k])%p;}Mat L(e,e,p);linear_block(L,da,db,modulus,e,p);nmod_poly_mat_det(factor.v,L.v);nmod_poly_mul(normV.v,normV.v,factor.v);}
 need(nmod_poly_degree(normV.v)==e*n*(n-1)/2,"Vandermonde full degree");nmod_poly_pow(frame.v,normV.v,n+1);nmod_poly_make_monic(frame.v,frame.v);nmod_poly_make_monic(gcd.v,det.v);
 std::vector<std::unique_ptr<Poly>> minors;std::vector<int>omitted;
 for(int j=2;j<q;j++){minors.emplace_back(new Poly(p));auto&c=*minors.back();if(j==ref)nmod_poly_set(c.v,det.v);else{int pos=std::find(order.begin(),order.end(),j)-order.begin();compound_minor(c,X,pos,e,dpow,p);}nmod_poly_divrem(quot.v,rem.v,c.v,frame.v);need(nmod_poly_is_zero(rem.v),"exact known frame");if(!nmod_poly_is_zero(c.v))nmod_poly_make_monic(c.v,c.v);nmod_poly_gcd(gcd.v,gcd.v,c.v);omitted.push_back(j);}
 bool pass=nmod_poly_equal(gcd.v,frame.v);std::ofstream f(out);need(bool(f),"open output");f<<"{\"status\":\""<<(pass?"primitive":"inconclusive")<<"\",\"n\":"<<n<<",\"q\":"<<q<<",\"p\":3,\"e\":"<<e<<",\"seed\":"<<seed<<",\"reference_omit\":2,\"reference_degree\":"<<e*degree<<",\"frame_degree\":"<<nmod_poly_degree(frame.v)<<",\"gcd_degree\":"<<nmod_poly_degree(gcd.v)<<",\"modulus\":";write_poly(f,modulus.v);f<<",\"intercept\":";write_fields(f,av,n-1);f<<",\"direction\":";write_fields(f,bv,n-1);f<<",\"norm_vandermonde\":";write_poly(f,normV.v);f<<",\"frame\":";write_poly(f,frame.v);f<<",\"gcd\":";write_poly(f,gcd.v);f<<",\"minors\":[";for(size_t i=0;i<minors.size();i++){if(i)f<<',';f<<"{\"omit\":"<<omitted[i]<<",\"norm\":";write_poly(f,minors[i]->v);f<<'}';}f<<"]}\n";f.close();need(bool(f),"saved result");std::cout<<(pass?"PASS":"INCONCLUSIVE")<<" n="<<n<<" norm_degree="<<e*degree<<" frame_degree="<<nmod_poly_degree(frame.v)<<" gcd_degree="<<nmod_poly_degree(gcd.v)<<std::endl;return 0;
}catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<std::endl;return 1;}}
