// Native prime-field verification for the all-prime original low complement.
// Reuse the validated source ordering and permutation code. FLINT nmod polynomials
// reconstruct prime-field roots and products; exact modular doubles use the BLAS backend.
#define main archived_original_checker_main
#include "bmd_nineteen_low_check_20261009.cpp"
#undef main
#include <givaro/modular.h>
#include <flint/ulong_extras.h>
#include <numeric>
using Prime=Givaro::Modular<double>;
Job readPrimeJob(const std::string&path){
 std::ifstream in(path);Job j;in>>j.n>>j.p>>j.f;
 ck((j.n==9||j.n==10)&&j.p>=101&&j.p<=2046&&n_is_prime(j.p)&&j.f==1,"proved prime-field remainder scope");
 j.mod.resize(2);for(auto&x:j.mod)in>>x;ck(j.mod[0]==0&&j.mod[1]==1,"canonical prime-field encoding");
 int groups;in>>groups;ck(groups>=1&&groups<=2,"bounded point retries");
 for(int i=0;i<groups;i++){
  Group g;g.labels.resize(j.n);for(auto&v:g.labels){in>>v;ck(v>0&&v<j.p,"nonzero prime-field slope");}
  auto labels=g.labels;std::sort(labels.begin(),labels.end());ck(std::adjacent_find(labels.begin(),labels.end())==labels.end(),"distinct slopes");
  int count;in>>count;ck(count>=1&&count<=6,"nonempty degree group");
  for(int k=0;k<count;k++){Case c;in>>c.d>>c.N>>c.det;ck(c.d>=2&&c.d<=j.n-3&&c.N>0&&c.N<=1793&&c.det>0&&c.det<j.p,"complete original case scope");g.cases.push_back(c);}
  j.groups.push_back(g);
 }
 ck(!in.fail(),"complete input");return j;
}
std::vector<double> primePrefixes(const Job&j,const std::vector<int>&labels,int N,int maxd){
 std::vector<nmod_poly_struct> roots(j.n),products(1<<j.n);
 for(auto&x:roots)nmod_poly_init(&x,j.p);for(auto&x:products)nmod_poly_init(&x,j.p);
 nmod_poly_t square,linear;nmod_poly_init(square,j.p);nmod_poly_init(linear,j.p);
 for(int i=0;i<j.n;i++){
  nmod_poly_zero(linear);nmod_poly_set_coeff_ui(linear,0,1);nmod_poly_set_coeff_ui(linear,1,labels[i]);
  nmod_poly_sqrt_series(&roots[i],linear,N);nmod_poly_mullow(square,&roots[i],&roots[i],N);
  ck(nmod_poly_get_coeff_ui(&roots[i],0)==1&&nmod_poly_equal(square,linear),"independent normalized prime root identity");
 }
 nmod_poly_one(&products[0]);
 for(int mask=1;mask<(1<<j.n);mask++)if(__builtin_popcount((unsigned)mask)<=maxd){int bit=__builtin_ctz((unsigned)mask),parent=mask^(1<<bit);nmod_poly_mullow(&products[mask],&products[parent],&roots[bit],N);}
 std::vector<double>co((size_t)(1<<j.n)*N);
 for(int mask=0;mask<(1<<j.n);mask++)if(__builtin_popcount((unsigned)mask)<=maxd)for(int k=0;k<N;k++)co[(size_t)mask*N+k]=nmod_poly_get_coeff_ui(&products[mask],k);
 for(auto&x:products)nmod_poly_clear(&x);for(auto&x:roots)nmod_poly_clear(&x);nmod_poly_clear(square);nmod_poly_clear(linear);
 return co;
}
std::vector<double> primeMatrix(const std::vector<double>&co,int stride,const std::vector<std::pair<int,int>>&cols,int N){
 ck((int)cols.size()==N,"exact source dimension");std::vector<double>A((size_t)N*N);
 for(int row=0;row<N;row++){auto[s,q]=cols[row];std::copy_n(co.data()+(size_t)s*stride,N-q,A.data()+(size_t)row*N+q);}
 return A;
}
int verifyPrime(const Job&j,const std::filesystem::path&outdir){
 Prime K(j.p);int count=0;bool negative=false;
 auto begin=std::chrono::steady_clock::now();
 std::ofstream out(outdir/("n"+std::to_string(j.n)+"-p"+std::to_string(j.p)+".txt"));ck(out.good(),"output file");
 for(const auto&g:j.groups){
  int maxd=0,N=0;for(auto c:g.cases){maxd=std::max(maxd,c.d);N=std::max(N,c.N);}
  ck(1.0*j.p*j.p*N<9007199254740992.0,"exact integer dot-product mantissa bound");
  auto co=primePrefixes(j,g.labels,N,maxd);auto cols=columns(maxd,j.n);
  std::sort(cols.begin(),cols.end(),[](auto a,auto b){return std::make_tuple(2*a.second+__builtin_popcount((unsigned)a.first),a.first,a.second)<std::make_tuple(2*b.second+__builtin_popcount((unsigned)b.first),b.first,b.second);});
  auto A=primeMatrix(co,N,cols,N);std::vector<size_t>P(N),Q(N);std::iota(P.begin(),P.end(),0);std::iota(Q.begin(),Q.end(),0);
  size_t rank=FFPACK::LUdivine(K,FFLAS::FflasNonUnit,FFLAS::FflasNoTrans,N,N,A.data(),N,P.data(),Q.data());
  ck(rank==(size_t)N,"largest original determinant nonzero");std::vector<double>diagonal(N+1,K.one);
  for(int k=0;k<N;k++){ck(Q[k]==(size_t)k&&P[k]>=(size_t)k&&P[k]<(size_t)N,"full-rank rank-profile and swap convention");K.mul(diagonal[k+1],diagonal[k],A[(size_t)k*N+k]);}
  for(auto c:g.cases){
   bool sign=reorderSign(cols,c.N,c.d,j.n);for(int k=0;k<c.N;k++){ck(P[k]<(size_t)c.N,"nested pivots remain inside their degree block");if(P[k]!=(size_t)k)sign=!sign;}
   double det=diagonal[c.N];if(sign){double tmp;K.neg(tmp,det);det=tmp;}
   ck(K.areEqual(det,(double)c.det)&&!K.isZero(det),"exact prime determinant matches PARI");
   out<<"CERTIFIED n="<<j.n<<" p="<<j.p<<" d="<<c.d<<" rank="<<c.N<<" determinant_code="<<c.det<<" exact_match=true\n";count++;
  }
  if(!negative){
   auto c=*std::min_element(g.cases.begin(),g.cases.end(),[](auto a,auto b){return a.d<b.d;});auto labels=g.labels;labels[j.n-1]=labels[j.n-2];
   auto bad=primePrefixes(j,labels,c.N,c.d);auto bc=columns(c.d,j.n);auto B=primeMatrix(bad,c.N,bc,c.N);
   ck(FFPACK::Rank(K,c.N,c.N,B.data(),c.N)<(size_t)c.N,"duplicated-root deficient control");
   negative=true;out<<"NEGATIVE_CONTROL repeated_root_deficient=true\n";
  }
 }
 out<<"COMPLETE count="<<count<<" one_prime_LU_per_point=true seconds="<<std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count()<<"\n";
 return count;
}
int main(int argc,char**argv){try{
 ck(argc==4,"manifest output-directory workers");int workers=std::stoi(argv[3]);ck(workers>=1&&workers<=4,"four bounded prime workers");
 std::ifstream list(argv[1]);std::vector<Job>jobs;std::string path;while(std::getline(list,path))if(!path.empty())jobs.push_back(readPrimeJob(path));ck(!jobs.empty(),"nonempty manifest");
 std::filesystem::create_directories(argv[2]);std::vector<int>counts(jobs.size());std::vector<std::string>errors(jobs.size());omp_set_num_threads(workers);
 #pragma omp parallel for schedule(dynamic)
 for(int i=0;i<(int)jobs.size();i++){try{counts[i]=verifyPrime(jobs[i],argv[2]);}catch(const std::exception&e){errors[i]=e.what();}}
 int total=0;for(size_t i=0;i<jobs.size();i++){ck(errors[i].empty(),"n"+std::to_string(jobs[i].n)+" p"+std::to_string(jobs[i].p)+": "+errors[i]);total+=counts[i];std::cout<<"FIELD n="<<jobs[i].n<<" p="<<jobs[i].p<<" matched="<<counts[i]<<'\n';}
 std::cout<<"COMPLETE independent_prime_determinants="<<total<<" fields="<<jobs.size()<<" exact_modular_BLAS=true\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}return 0;}
