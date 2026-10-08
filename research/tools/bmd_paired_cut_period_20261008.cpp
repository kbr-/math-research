// Complete local-cut rank period of the actual four-pair source over F9.
// Givaro builds all arithmetic tables; FFPACK performs elimination; FLINT controls ranks.
#include <givaro/gfq.h>
#include <fflas-ffpack/fflas-ffpack.h>
#include <flint/fq_nmod_mat.h>
#include <omp.h>
#include <array>
#include <chrono>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using Fld=Givaro::GFqDom<int64_t>;using E=Fld::Element;
void ck(bool x,const std::string&s){if(!x)throw std::runtime_error(s);}
int rankGF(const Fld&F,std::vector<E>A,int n){std::vector<size_t>P(n),Q(n);return FFPACK::LUdivine_gauss(F,FFLAS::FflasNonUnit,n,n,A.data(),n,P.data(),Q.data());}
constexpr int H=188,D=416;
struct Term{int j;E v;};
int main(int argc,char**argv){try{
 ck(argc==5,"usage input out pilot-count threads; pilot-count0 means full");int pilot=std::stoi(argv[3]),nt=std::stoi(argv[4]);ck(nt>=1&&nt<=14,"shared CPU budget");omp_set_num_threads(nt);
 auto started=std::chrono::steady_clock::now();std::ifstream in(argv[1]);int f;in>>f;ck(f==4,"F81 input");std::vector<int64_t>mod(5);for(auto&x:mod)in>>x;Fld F(3,4,mod),K(3,2,std::vector<int64_t>{1,0,1});
 auto read=[&](){int n;in>>n;ck(in.good()&&n>=0&&n<81,"field input");return F.padic2zech(n);};E eta=read();
 std::array<std::array<E,81>,81>add,mul;for(int i=0;i<81;i++)for(int j=0;j<81;j++){F.add(add[i][j],i,j);F.mul(mul[i][j],i,j);}
 ck(add[mul[eta][eta]][F.one]==F.zero,"F9 embedding polynomial");std::array<int,81>small;small.fill(-1);for(int c=0;c<9;c++){E z=add[F.padic2zech(c%3)][mul[F.padic2zech(c/3)][eta]];small[z]=K.padic2zech(c);}
 std::vector<E>phi(D);for(auto&x:phi)x=read();std::array<std::vector<E>,3>B,refs;for(auto&v:B){v.resize(D*H);for(auto&x:v)x=read();}
 std::vector<E>W(H*D);for(auto&x:W)x=read();for(auto&v:refs){v.resize(H*H);for(auto&x:v)x=read();}std::string extra;ck(!(in>>extra),"exact input shape");
 std::vector<int>starts,ls;std::array<int,D>start{},length{};int off=0;for(int L:{7,11,15,15,4})for(int p=0;p<8;p++){starts.push_back(off);ls.push_back(L);for(int j=0;j<L;j++){start[off+j]=off;length[off+j]=L;}off+=L;}ck(off==D,"all local points");
 std::vector<E>identity(D,F.zero);for(auto s:starts)identity[s]=F.one;
 std::vector<std::vector<E>>powers{identity};int period=0;
 for(int h=1;h<=2160;h++){std::vector<E>v(D,F.zero);for(size_t k=0;k<starts.size();k++){int s=starts[k],L=ls[k];for(int i=0;i<L;i++)for(int j=0;j<=i;j++)v[s+i]=add[v[s+i]][mul[powers.back()[s+j]][phi[s+i-j]]];}if(v==identity){period=h;break;}powers.push_back(std::move(v));}
 ck(period>0&&2160%period==0,"full cut period closes");std::cout<<"LOCAL_PERIOD "<<period<<" DEGREE_PERIOD "<<3*period<<"\n"<<std::flush;
 std::vector<std::vector<Term>>weights(H);for(int i=0;i<H;i++)for(int j=0;j<D;j++)if(W[i*D+j]!=F.zero)weights[i].push_back({j,W[i*D+j]});
 auto assemble=[&](int h,int z){std::vector<E>A(H*H,F.zero);for(int row=0;row<H;row++){std::array<E,D>v;v.fill(F.zero);for(auto t:weights[row]){int s=start[t.j],k=t.j-s;for(int j=0;j<=k;j++)v[s+j]=add[v[s+j]][mul[t.v][powers[h][s+k-j]]];}for(int j=0;j<D;j++)if(v[j]!=F.zero){const auto&table=mul[v[j]];auto b=B[z].data()+j*H,a=A.data()+row*H;for(int c=0;c<H;c++)a[c]=add[a[c]][table[b[c]]];}}return A;};
 fq_nmod_ctx_t ctx;nmod_poly_t p;nmod_poly_init(p,3);for(int j=0;j<=4;j++)nmod_poly_set_coeff_ui(p,j,mod[j]);fq_nmod_ctx_init_modulus(ctx,p,"b");
 auto independent=[&](const std::vector<E>&A){fq_nmod_mat_t M;fq_nmod_mat_init(M,H,H,ctx);for(int i=0;i<H;i++)for(int j=0;j<H;j++){int v=F.zech2padic(A[i*H+j]);nmod_poly_zero(p);for(int k=0;k<4;k++){nmod_poly_set_coeff_ui(p,k,v%3);v/=3;}fq_nmod_set_nmod_poly(fq_nmod_mat_entry(M,i,j),p,ctx);}int r=fq_nmod_mat_rank(M,ctx);fq_nmod_mat_clear(M,ctx);return r;};
 for(int z=0;z<3;z++){auto A=assemble(0,z);ck(A==refs[z],"all GP reference matrix entries");int r=rankGF(F,A,H);ck(r==independent(A),"FLINT reference rank");std::cout<<"CONTROL degree="<<z+3<<" rank="<<r<<" all_entries=true\n";auto C=A;for(int j=0;j<H;j++)C[(H-1)*H+j]=C[j];ck(rankGF(F,C,H)==independent(C),"duplicate-row backend control");}
 for(int z=0;z<3;z++){auto A=assemble(1,z);int r=rankGF(F,A,H);ck(r==independent(A),"FLINT shifted rank");std::cout<<"CONTROL degree="<<z+6<<" rank="<<r<<"\n";}
 fq_nmod_ctx_clear(ctx);nmod_poly_clear(p);
 int count=pilot?std::min(pilot,3*period):3*period;std::vector<int>ranks(count,-1);
 #pragma omp parallel for schedule(dynamic)
 for(int job=0;job<count;job++){int h=job/3,z=job%3;auto A=assemble(h,z);for(auto&x:A){if(small[x]<0)throw std::runtime_error("cut entry left F9");x=small[x];}ranks[job]=rankGF(K,std::move(A),H);}
 std::ofstream out(argv[2]);out<<"degree_residue,representative,rank\n";std::array<int,H+1>hist{};for(int j=0;j<count;j++){hist[ranks[j]]++;out<<(j+3)%(3*period)<<','<<j+3<<','<<ranks[j]<<'\n';}out.close();
 for(int r=0;r<=H;r++)if(hist[r])std::cout<<"RANK "<<r<<" count="<<hist[r]<<"\n";
 std::cout<<"COMPLETE count="<<count<<" full="<<(count==3*period)<<" seconds="<<std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count()<<"\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}return 0;}
