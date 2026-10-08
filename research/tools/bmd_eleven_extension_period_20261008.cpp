// Complete local-cut rank period of the actual four-pair source over F121.
// Givaro supplies native arithmetic without quadratic-size field tables; FFPACK performs elimination; FLINT controls ranks.
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
#include <sstream>
#include <set>
#include <numeric>
#include <vector>
using Fld=Givaro::GFqDom<int64_t>;using E=Fld::Element;
void ck(bool x,const std::string&s){if(!x)throw std::runtime_error(s);}
int rankGF(const Fld&F,std::vector<E>A,int n){std::vector<size_t>P(n),Q(n);return FFPACK::LUdivine_gauss(F,FFLAS::FflasNonUnit,n,n,A.data(),n,P.data(),Q.data());}
constexpr int H=188,D=512,R=460;
struct Term{int j;E v;};
int main(int argc,char**argv){try{
 ck(argc==5||argc==6,"usage input out pilot-count threads [previous-csv]; pilot-count0 means full");int pilot=std::stoi(argv[3]),nt=std::stoi(argv[4]);ck(nt>=1&&nt<=14,"shared CPU budget");omp_set_num_threads(nt);
 auto started=std::chrono::steady_clock::now();std::ifstream in(argv[1]);int f;in>>f;ck(f==4,"F14641 input");std::vector<int64_t>mod(5);for(auto&x:mod)in>>x;Fld F(11,4,mod);const Fld&K=F;
 auto read=[&](){int n;in>>n;ck(in.good()&&n>=0&&n<14641,"field input");return F.padic2zech(n);};E eta=read();
 auto add=[&](E x,E y){E z;F.add(z,x,y);return z;};auto mul=[&](E x,E y){E z;F.mul(z,x,y);return z;};
 ck(add(add(mul(eta,eta),eta),F.one)==F.zero,"F121 embedding polynomial");std::array<int,14641>small;std::array<E,14641>large{};small.fill(-1);for(int c=0;c<121;c++){E z=add(F.padic2zech(c%11),mul(F.padic2zech(c/11),eta));small[z]=z;large[z]=z;}

 std::array<std::vector<int>,24> selections;for(auto&v:selections){v.resize(H);for(auto&x:v){in>>x;ck(x>=0&&x<R,"cut row selection");}}
 std::vector<E>phi(D);for(auto&x:phi)x=read();std::array<std::vector<E>,3>B,refs;for(auto&v:B){v.resize(D*H);for(auto&x:v)x=read();}
 std::vector<E>W(R*D);for(auto&x:W)x=read();for(auto&v:refs){v.resize(H*H);for(auto&x:v)x=read();}std::string extra;ck(!(in>>extra),"exact input shape");
 std::vector<int>starts,ls;std::array<int,D>start{},length{};int off=0;for(int L:{15,15,15,15,4})for(int p=0;p<8;p++){starts.push_back(off);ls.push_back(L);for(int j=0;j<L;j++){start[off+j]=off;length[off+j]=L;}off+=L;}ck(off==D,"all local points");
 std::vector<E>identity(D,F.zero);for(auto s:starts)identity[s]=F.one;
 auto product=[&](const std::vector<E>&a,const std::vector<E>&b){std::vector<E>v(D,F.zero);for(size_t k=0;k<starts.size();k++){int off=starts[k],L=ls[k];for(int i=0;i<L;i++)for(int j=0;j<=i;j++)v[off+i]=add(v[off+i],mul(a[off+j],b[off+i-j]));}return v;};
 std::vector<std::vector<E>>binary{phi};for(int i=1;i<22;i++)binary.push_back(product(binary.back(),binary.back()));
 auto power=[&](int h){auto v=identity;for(int i=0;h;h>>=1,i++)if(h&1)v=product(v,binary[i]);return v;};
 int period=1771440;ck(power(period)==identity,"universal period");for(int prime:{2,3,5,11,61})while(period%prime==0&&power(period/prime)==identity)period/=prime;
 auto projective=[&](const std::vector<E>&v){int off=0;for(int L:{15,15,15,15,4}){E scale=v[off];if(scale==F.zero)return false;for(int sign=0;sign<8;sign++){if(v[off]!=scale)return false;for(int j=1;j<L;j++)if(v[off+j]!=F.zero)return false;off+=L;}}return true;};
 int projectivePeriod=period;for(int prime:{2,3,5,11,61})while(projectivePeriod%prime==0&&projective(power(projectivePeriod/prime)))projectivePeriod/=prime;
 std::cout<<"LOCAL_PERIOD "<<period<<" DEGREE_PERIOD "<<3*period<<" PROJECTIVE_CANDIDATE "<<projectivePeriod<<"\n"<<std::flush;
 std::vector<std::vector<Term>>weights(R);for(int i=0;i<R;i++)for(int j=0;j<D;j++)if(W[i*D+j]!=F.zero)weights[i].push_back({j,W[i*D+j]});
 auto assemble=[&](int h,int z){const auto ph=power(h);std::vector<E>A(R*H,F.zero);for(int row=0;row<R;row++){std::array<E,D>v;v.fill(F.zero);for(auto t:weights[row]){int s=start[t.j],k=t.j-s;for(int j=0;j<=k;j++)v[s+j]=add(v[s+j],mul(t.v,ph[s+k-j]));}for(int j=0;j<D;j++)if(v[j]!=F.zero){auto b=B[z].data()+j*H,a=A.data()+row*H;for(int c=0;c<H;c++)a[c]=add(a[c],mul(v[j],b[c]));}}return A;};
 auto select=[&](const std::vector<E>&pool,int order){std::vector<E>A(H*H);for(int i=0;i<H;i++)std::copy_n(pool.data()+selections[order][i]*H,H,A.data()+i*H);return A;};
 fq_nmod_ctx_t ctx;nmod_poly_t p;nmod_poly_init(p,11);for(int j=0;j<=4;j++)nmod_poly_set_coeff_ui(p,j,mod[j]);fq_nmod_ctx_init_modulus(ctx,p,"b");
 auto independent=[&](const std::vector<E>&A){nmod_poly_t pp;nmod_poly_init(pp,11);fq_nmod_mat_t M;fq_nmod_mat_init(M,H,H,ctx);for(int i=0;i<H;i++)for(int j=0;j<H;j++){int v=F.zech2padic(A[i*H+j]);nmod_poly_zero(pp);for(int k=0;k<4;k++){nmod_poly_set_coeff_ui(pp,k,v%11);v/=11;}fq_nmod_set_nmod_poly(fq_nmod_mat_entry(M,i,j),pp,ctx);}int r=fq_nmod_mat_rank(M,ctx);fq_nmod_mat_clear(M,ctx);nmod_poly_clear(pp);return r;};
 for(int z=0;z<3;z++){auto A=select(assemble(0,z),0);ck(A==refs[z],"all GP reference matrix entries");int r=rankGF(F,A,H);ck(r==independent(A),"FLINT reference rank");std::cout<<"CONTROL degree="<<z+3<<" rank="<<r<<" all_entries=true\n";auto C=A;for(int j=0;j<H;j++)C[(H-1)*H+j]=C[j];ck(rankGF(F,C,H)==independent(C),"duplicate-row backend control");}
 for(int z=0;z<3;z++){auto A=select(assemble(1,z),0);int r=rankGF(F,A,H);ck(r==independent(A),"FLINT shifted rank");std::cout<<"CONTROL degree="<<z+6<<" rank="<<r<<"\n";}
 
 std::vector<int>jobs;int priorPeriod=1;std::vector<bool>need(1,true);if(argc==6){std::ifstream prior(argv[5]);std::string line;std::getline(prior,line);std::vector<std::pair<int,int>> rows;int maxResidue=-1;while(std::getline(prior,line)){std::replace(line.begin(),line.end(),',',' ');std::istringstream ss(line);int residue,rep,rank,order;ss>>residue>>rep>>rank>>order;ck(ss.good()||ss.eof(),"prior CSV row");ck(residue>=0&&rank>=0&&rank<=H,"prior row range");rows.push_back({residue,rank});maxResidue=std::max(maxResidue,residue);}priorPeriod=maxResidue+1;ck((int)rows.size()==priorPeriod,"complete prior cover");need.assign(priorPeriod,false);std::vector<bool>seen(priorPeriod,false);for(auto row:rows){ck(!seen[row.first],"unique prior residues");seen[row.first]=true;need[row.first]=row.second<H;}}int commonPeriod=std::lcm(priorPeriod,3*period);std::set<int>keys;for(int d=0;d<commonPeriod;d++)if(need[d%priorPeriod])keys.insert((d-3+3*period)%(3*period));jobs.assign(keys.begin(),keys.end());std::cout<<"PRIOR_PERIOD "<<priorPeriod<<" COMMON_PERIOD "<<commonPeriod<<" UNIQUE_REQUIRED_STATES "<<jobs.size()<<"\n";int count=pilot?std::min(pilot,(int)jobs.size()):(int)jobs.size();std::vector<int>ranks(count,-1),chosen(count,-1);
 #pragma omp parallel for schedule(dynamic)
 for(int job=0;job<count;job++){int h=jobs[job]/3,z=jobs[job]%3;auto pool=assemble(h,z);for(auto&x:pool){if(small[x]<0)throw std::runtime_error("cut entry left F121");x=small[x];}int best=-1;for(int order=0;order<24;order++){int r=rankGF(K,select(pool,order),H);if(r>best){best=r;chosen[job]=order;}if(r==H)break;}ranks[job]=best;auto witness=select(pool,chosen[job]);for(auto&x:witness)x=large[x];ck(independent(witness)==best,"every selected full-period rank independently verified by FLINT");}
 fq_nmod_ctx_clear(ctx);nmod_poly_clear(p);
 std::ofstream out(argv[2]);out<<"degree_residue,representative,rank,order_index\n";std::array<int,H+1>hist{};for(int j=0;j<count;j++){hist[ranks[j]]++;out<<(jobs[j]+3)%(3*period)<<','<<jobs[j]+3<<','<<ranks[j]<<','<<chosen[j]<<'\n';}out.close();
 for(int r=0;r<=H;r++)if(hist[r])std::cout<<"RANK "<<r<<" count="<<hist[r]<<"\n";
 std::cout<<"COMPLETE all_selected_ranks_FLINT_verified=true count="<<count<<" full="<<(count==(int)jobs.size())<<" seconds="<<std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count()<<"\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}return 0;}
