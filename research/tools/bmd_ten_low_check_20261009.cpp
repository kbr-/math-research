// Independent original n10 complements: FLINT polynomial products and FFPACK nested determinants.
// LUdivine_gauss scans rows, records column interchanges P and row indices Q.
// For a full-rank square matrix Q is identity. Pivots staying inside a leading block
// certify that block; its signed diagonal product gives its determinant.
#include <givaro/gfq.h>
#include <fflas-ffpack/fflas-ffpack.h>
#include <flint/fq_nmod_poly.h>
#include <omp.h>
#include <algorithm>
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>
using Field=Givaro::GFqDom<int64_t>;using E=Field::Element;
void ck(bool b,const std::string&s){if(!b)throw std::runtime_error(s);}
struct Case{int d,N,det;};struct Group{std::vector<int>labels;std::vector<Case>cases;};
struct Job{int p,f;std::vector<int64_t>mod;std::vector<Group>groups;};
Job readJob(const std::string&path,int cap){std::ifstream in(path);Job j;in>>j.p>>j.f;ck(j.p>=3&&j.p<=97&&j.p%2&&j.f>=1&&j.f<=6,"field scope");j.mod.resize(j.f+1);for(auto&x:j.mod)in>>x;ck(j.mod.back()==1,"monic field modulus");int n;in>>n;for(int z=0;z<n;z++){Group g;g.labels.resize(10);for(auto&x:g.labels)in>>x;int count;in>>count;for(int k=0;k<count;k++){Case c;in>>c.d>>c.N>>c.det;if(c.d<=cap)g.cases.push_back(c);}if(!g.cases.empty())j.groups.push_back(g);}ck(in.good()||in.eof(),"input parse");ck(!j.groups.empty(),"nonempty selected cases");return j;}
std::vector<std::pair<int,int>> columns(int d){std::vector<std::pair<int,int>>v;for(int s=0;s<1024;s++)if(__builtin_popcount((unsigned)s)<=d)for(int q=0;2*q+__builtin_popcount((unsigned)s)<=d;q++)v.push_back({s,q});return v;}
std::vector<E> prefixes(const Job&j,const Field&F,const std::vector<int>&labels,int N,int maxd){
 int qfield=1;for(int i=0;i<j.f;i++){qfield*=j.p;ck(qfield<=100000,"bounded field allocation");}
 std::vector<int>C(j.p*j.p);for(int i=0;i<j.p;i++){C[i*j.p]=1;C[i*j.p+i]=1;for(int k=1;k<i;k++)C[i*j.p+k]=(C[(i-1)*j.p+k-1]+C[(i-1)*j.p+k])%j.p;}
 int ppow=1;while(ppow<N)ppow*=j.p;int half=(ppow+1)/2;
 auto binom=[&](int k){int n=half,v=1;while(n||k){int a=n%j.p,b=k%j.p;if(b>a)return 0;v=v*C[a*j.p+b]%j.p;n/=j.p;k/=j.p;}return v;};
 nmod_poly_t modulus,codepoly;nmod_poly_init(modulus,j.p);nmod_poly_init(codepoly,j.p);for(int k=0;k<=j.f;k++)nmod_poly_set_coeff_ui(modulus,k,j.mod[k]);fq_nmod_ctx_t ctx;fq_nmod_ctx_init_modulus(ctx,modulus,"a");fq_nmod_t element;fq_nmod_init(element,ctx);
 auto setCode=[&](int code){ck(code>=0&&code<qfield,"field code");nmod_poly_zero(codepoly);for(int k=0;k<j.f;k++){nmod_poly_set_coeff_ui(codepoly,k,code%j.p);code/=j.p;}fq_nmod_set_nmod_poly(element,codepoly,ctx);};
 std::vector<fq_nmod_poly_struct>roots(10),prod(1024);for(auto&x:roots)fq_nmod_poly_init(&x,ctx);for(auto&x:prod)fq_nmod_poly_init(&x,ctx);
 fq_nmod_poly_t square,linear;fq_nmod_poly_init(square,ctx);fq_nmod_poly_init(linear,ctx);
 for(int i=0;i<10;i++){E slope=F.padic2zech(labels[i]),power=F.one;for(int k=0;k<N;k++){E value,next;F.mul(value,F.padic2zech(binom(k)),power);setCode(F.zech2padic(value));fq_nmod_poly_set_coeff(&roots[i],k,element,ctx);F.mul(next,power,slope);power=next;}
 fq_nmod_poly_mullow(square,&roots[i],&roots[i],N,ctx);fq_nmod_poly_zero(linear,ctx);setCode(1);fq_nmod_poly_set_coeff(linear,0,element,ctx);setCode(labels[i]);fq_nmod_poly_set_coeff(linear,1,element,ctx);ck(fq_nmod_poly_equal(square,linear,ctx),"independent normalized root-square identity");}
 fq_nmod_poly_one(&prod[0],ctx);for(int s=1;s<1024;s++)if(__builtin_popcount((unsigned)s)<=maxd){int bit=__builtin_ctz((unsigned)s),parent=s^(1<<bit);fq_nmod_poly_mullow(&prod[s],&prod[parent],&roots[bit],N,ctx);}
 std::vector<E>co(1024*N,F.zero);for(int s=0;s<1024;s++)if(__builtin_popcount((unsigned)s)<=maxd)for(int k=0;k<N;k++){fq_nmod_poly_get_coeff(element,&prod[s],k,ctx);int code=0,mult=1;for(int b=0;b<j.f;b++){code+=mult*nmod_poly_get_coeff_ui(element,b);mult*=j.p;}co[s*N+k]=F.padic2zech(code);}
 for(auto&x:prod)fq_nmod_poly_clear(&x,ctx);for(auto&x:roots)fq_nmod_poly_clear(&x,ctx);fq_nmod_poly_clear(square,ctx);fq_nmod_poly_clear(linear,ctx);fq_nmod_clear(element,ctx);fq_nmod_ctx_clear(ctx);nmod_poly_clear(codepoly);nmod_poly_clear(modulus);return co;}
std::vector<E> matrix(const Field&F,const std::vector<E>&co,int stride,const std::vector<std::pair<int,int>>&cols,int N){ck((int)cols.size()==N,"complete original source count");std::vector<E>A(N*N,F.zero);for(int row=0;row<N;row++){auto[s,q]=cols[row];std::copy_n(co.data()+s*stride,N-q,A.data()+row*N+q);}return A;}
bool reorderSign(const std::vector<std::pair<int,int>>&sorted,int N,int d){auto old=columns(d);ck((int)old.size()==N,"degree dimension");std::vector<int>position(8192,-1);for(int i=0;i<N;i++)position[old[i].first*8+old[i].second]=i;std::vector<int>perm(N);for(int i=0;i<N;i++){perm[i]=position[sorted[i].first*8+sorted[i].second];ck(perm[i]>=0,"exact degree prefix");}std::vector<bool>seen(N);int cycles=0;for(int i=0;i<N;i++)if(!seen[i]){cycles++;for(int k=i;!seen[k];k=perm[k])seen[k]=true;}return (N-cycles)%2;}
int run(const Job&j,const std::filesystem::path&outdir){Field F(j.p,j.f,j.mod);int checked=0;bool negative=false;std::ofstream out(outdir/("p"+std::to_string(j.p)+"-f"+std::to_string(j.f)+".txt"));auto begin=std::chrono::steady_clock::now();
 for(const auto&g:j.groups){int maxd=0,N=0;for(auto c:g.cases){maxd=std::max(maxd,c.d);N=std::max(N,c.N);}auto co=prefixes(j,F,g.labels,N,maxd);auto cols=columns(maxd);std::sort(cols.begin(),cols.end(),[](auto a,auto b){return std::make_tuple(2*a.second+__builtin_popcount((unsigned)a.first),a.first,a.second)<std::make_tuple(2*b.second+__builtin_popcount((unsigned)b.first),b.first,b.second);});auto A=matrix(F,co,N,cols,N);std::vector<size_t>P(N),Q(N);int rank=FFPACK::LUdivine_gauss(F,FFLAS::FflasNonUnit,N,N,A.data(),N,P.data(),Q.data());ck(rank==N,"largest original determinant nonzero");
 std::vector<E>diagonal(N+1,F.one);for(int k=0;k<N;k++){ck(Q[k]==(size_t)k&&P[k]>=(size_t)k&&P[k]<(size_t)N,"documented full-rank column-swap convention");F.mul(diagonal[k+1],diagonal[k],A[k*N+k]);}
 for(auto c:g.cases){bool sign=reorderSign(cols,c.N,c.d);for(int k=0;k<c.N;k++){ck(P[k]<(size_t)c.N,"all leading-block pivots stay in the degree block");if(P[k]!=(size_t)k)sign=!sign;}E det=diagonal[c.N];if(sign){E v;F.mul(v,det,F.mOne);det=v;}ck(F.zech2padic(det)==c.det&&det!=F.zero,"exact independent determinant matches PARI");out<<"CERTIFIED p="<<j.p<<" d="<<c.d<<" rank="<<c.N<<" determinant_code="<<c.det<<" exact_match=true\n";checked++;}
 if(!negative){auto c=*std::min_element(g.cases.begin(),g.cases.end(),[](auto a,auto b){return a.d<b.d;});auto labels=g.labels;labels[9]=labels[8];auto bad=prefixes(j,F,labels,c.N,c.d);auto bc=columns(c.d);auto B=matrix(F,bad,c.N,bc,c.N);std::vector<size_t>p(c.N),q(c.N);ck(FFPACK::LUdivine_gauss(F,FFLAS::FflasNonUnit,c.N,c.N,B.data(),c.N,p.data(),q.data())<(size_t)c.N,"duplicated-root deficient control");negative=true;out<<"NEGATIVE_CONTROL repeated_root_deficient=true\n";}}
 out<<"COMPLETE count="<<checked<<" one_full_LU_per_point=true seconds="<<std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count()<<"\n";return checked;}
int main(int argc,char**argv){try{ck(argc==5,"manifest outdir max-degree threads");std::ifstream list(argv[1]);std::vector<Job>jobs;std::string path;int cap=std::stoi(argv[3]),threads=std::stoi(argv[4]);ck(cap>=2&&cap<=7&&threads>=1&&threads<=3,"bounded series");while(std::getline(list,path))if(!path.empty())jobs.push_back(readJob(path,cap));ck(!jobs.empty(),"manifest");std::filesystem::create_directories(argv[2]);std::vector<int>counts(jobs.size());std::vector<std::string>errors(jobs.size());omp_set_num_threads(threads);
 #pragma omp parallel for schedule(dynamic)
 for(int i=0;i<(int)jobs.size();i++){try{counts[i]=run(jobs[i],argv[2]);}catch(const std::exception&e){errors[i]=e.what();}}
 int total=0;for(size_t i=0;i<jobs.size();i++){ck(errors[i].empty(),"p"+std::to_string(jobs[i].p)+": "+errors[i]);total+=counts[i];std::cout<<"FIELD p="<<jobs[i].p<<" independently_matched="<<counts[i]<<'\n';}std::cout<<"COMPLETE independently_matched="<<total<<" max_degree="<<cap<<" FLINT_products_FFPACK_nested_LU=true\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}return 0;}
