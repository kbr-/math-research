// Compare installed rank libraries on retained actual cup matrices, including a zero-row control.
// No custom elimination. Givaro GFq + FFPACK, FLINT fq_nmod, and restriction to F3 + FFPACK.
// Input: degree, n, expected rank; degree+1 modulus coefficients; n*n base-three field codes.
// All field encodings are checked by roundtrip. Timings include a fresh destructive-rank copy.
#include <givaro/gfq.h>
#include <givaro/modular.h>
#include <fflas-ffpack/fflas-ffpack.h>
#include <flint/fq_nmod_mat.h>
#include <chrono>
#include <fstream>
#include <iostream>
#include <vector>
#include <stdexcept>
#include <iomanip>
using Clock=std::chrono::steady_clock;
double elapsed(Clock::time_point t){return std::chrono::duration<double>(Clock::now()-t).count();}
void check(bool c,const char* m){if(!c)throw std::runtime_error(m);}
int main(int argc,char**argv){
 try {
  check(argc==3,"usage input repetitions");
  std::ifstream in(argv[1]); int f,n,expected,reps=std::stoi(argv[2]);in>>f>>n>>expected;
  check(in.good() && f>=1 && f<=8 && n>=1 && n<=140 && reps>=1 && reps<=64,"bounded input");
  std::vector<int64_t> mod(f+1);for(auto &x:mod)in>>x;
  int q=1;for(int i=0;i<f;i++)q*=3;
  std::vector<int> code(n*n);for(auto&x:code){in>>x;check(x>=0&&x<q,"field code");}
  check(!in.fail(),"complete input");
  using Field=Givaro::GFqDom<int64_t>;Field F(3,f,mod);
  for(int x=0;x<q;x++)check(F.zech2padic(F.padic2zech(x))==(uint64_t)x,"field roundtrip");
  std::vector<Field::Element>A(n*n);for(int i=0;i<n*n;i++)A[i]=F.padic2zech(code[i]);
  auto direct=[&](bool bad){auto X=A;if(bad)for(int j=0;j<n;j++)X[j]=F.zero;std::vector<size_t>P(n),Q(n);return (int)FFPACK::LUdivine_gauss(F,FFLAS::FflasNonUnit,n,n,X.data(),n,P.data(),Q.data());};
  check(direct(false)==expected && direct(true)==expected-1,"Givaro rank/control");
  auto t=Clock::now();for(int k=0;k<reps;k++)check(direct(false)==expected,"repeated Givaro rank");double gd=elapsed(t)/reps;
  nmod_poly_t poly; nmod_poly_init(poly,3);for(int i=0;i<=f;i++)nmod_poly_set_coeff_ui(poly,i,mod[i]);
  fq_nmod_ctx_t ctx;fq_nmod_ctx_init_modulus(ctx,poly,"a");
  fq_nmod_mat_t M;fq_nmod_mat_init(M,n,n,ctx);
  nmod_poly_t val;nmod_poly_init(val,3);
  for(int i=0;i<n;i++)for(int j=0;j<n;j++){
   int x=code[i*n+j];nmod_poly_zero(val);for(int k=0;k<f;k++){nmod_poly_set_coeff_ui(val,k,x%3);x/=3;}
   fq_nmod_set_nmod_poly(fq_nmod_mat_entry(M,i,j),val,ctx);
  }
  t=Clock::now();int fr=fq_nmod_mat_rank(M,ctx);double fl=elapsed(t);
  check(fr==expected,"FLINT rank");for(int j=0;j<n;j++)fq_nmod_zero(fq_nmod_mat_entry(M,0,j),ctx);
  check(fq_nmod_mat_rank(M,ctx)==expected-1,"FLINT corruption");
  fq_nmod_mat_clear(M,ctx);nmod_poly_clear(val);fq_nmod_ctx_clear(ctx);nmod_poly_clear(poly);
  t=Clock::now();int N=n*f;std::vector<double> expanded((size_t)N*N);
  for(int i=0;i<n;i++)for(int j=0;j<n;j++){
   int basis=1;for(int k=0;k<f;k++){
    Field::Element product;F.mul(product,A[i*n+j],F.padic2zech(basis));int v=F.zech2padic(product);
    for(int r=0;r<f;r++){expanded[(size_t)(i*f+r)*N+j*f+k]=v%3;v/=3;}basis*=3;
   }
  }
  double expand=elapsed(t);Givaro::Modular<double> F3(3.0);
  auto scalar=[&](bool bad){auto X=expanded;if(bad)for(int r=0;r<f;r++)for(int j=0;j<N;j++)X[(size_t)r*N+j]=0;return (int)FFPACK::Rank(F3,N,N,X.data(),N);};
  check(scalar(false)==f*expected && scalar(true)==f*(expected-1),"restriction of scalars");
  t=Clock::now();for(int k=0;k<reps;k++)check(scalar(false)==f*expected,"repeated scalar rank");double sc=elapsed(t)/reps;
  std::cout<<std::setprecision(9)<<"BACKEND degree="<<f<<" n="<<n<<" repetitions="<<reps
   <<" givaro_ffpack_seconds="<<gd<<" flint_fq_seconds="<<fl
   <<" scalar_ffpack_seconds="<<sc<<" expansion_seconds="<<expand
   <<" all_ranks="<<expected<<" corruption_rank="<<expected-1<<"\n";
  std::cout<<"RANK_BACKEND_COMPLETED\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}
}
