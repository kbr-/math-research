// Complete fibre-scalar local-cut rank period of the actual four-pair source in characteristic thirty-one over F31.
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
 auto started=std::chrono::steady_clock::now();std::ifstream in(argv[1]);int f;in>>f;ck(f==2,"F961 input");std::vector<int64_t>mod(3);for(auto&x:mod)in>>x;Fld F(31,2,mod);const Fld&K=F;
 auto read=[&](){int n;in>>n;ck(in.good()&&n>=0&&n<961,"field input");return F.padic2zech(n);};E eta=read();
 std::vector<std::vector<E>>add(961,std::vector<E>(961)),mul=add;for(int i=0;i<961;i++)for(int j=0;j<961;j++){F.add(add[i][j],i,j);F.mul(mul[i][j],i,j);}
 ck(eta==F.zero,"unused embedding marker");std::array<int,961>small;std::array<E,961>large{};small.fill(-1);for(int c=0;c<31;c++){E z=F.padic2zech(c);small[z]=z;large[z]=z;}
 std::array<std::vector<int>,24> selections;for(auto&v:selections){v.resize(H);for(auto&x:v){in>>x;ck(x>=0&&x<R,"cut row selection");}}
 std::vector<E>phi(D);for(auto&x:phi)x=read();std::array<std::vector<E>,3>B,refs;for(auto&v:B){v.resize(D*H);for(auto&x:v)x=read();}
 std::vector<E>W(R*D);for(auto&x:W)x=read();for(auto&v:refs){v.resize(H*H);for(auto&x:v)x=read();}std::string extra;ck(!(in>>extra),"exact input shape");
 std::vector<int>starts,ls;std::array<int,D>start{},length{};int off=0;for(int L:{15,15,15,15,4})for(int p=0;p<8;p++){starts.push_back(off);ls.push_back(L);for(int j=0;j<L;j++){start[off+j]=off;length[off+j]=L;}off+=L;}ck(off==D,"all local points");
 std::vector<E>identity(D,F.zero);for(auto s:starts)identity[s]=F.one;
 E originalConstant=phi[0],gamma;F.inv(gamma,originalConstant);for(auto&x:phi)x=mul[gamma][x];
 std::vector<std::vector<E>>powers{identity};int period=0;
 for(int h=1;h<=29760;h++){std::vector<E>v(D,F.zero);for(size_t k=0;k<starts.size();k++){int s=starts[k],L=ls[k];for(int i=0;i<L;i++)for(int j=0;j<=i;j++)v[s+i]=add[v[s+i]][mul[powers.back()[s+j]][phi[s+i-j]]];}if(v==identity){period=h;break;}powers.push_back(std::move(v));}
 ck(period>0&&29760%period==0,"normalized exact local period closes");
 int constantOrder=0;E current=F.one;do{current=mul[current][originalConstant];constantOrder++;ck(constantOrder<=960,"nonzero local constant order");}while(current!=F.one);
 std::vector<E>unscales(period,F.one);for(int h=1;h<period;h++)unscales[h]=mul[unscales[h-1]][originalConstant];
 std::cout<<"LOCAL_PERIOD "<<period<<" DEGREE_PERIOD "<<3*period<<" NORMALIZATION_CODE "<<F.zech2padic(gamma)<<" RAW_ENTRYWISE_PERIOD "<<std::lcm(period,constantOrder)<<"\n"<<std::flush;

 std::vector<std::vector<Term>>weights(R);for(int i=0;i<R;i++)for(int j=0;j<D;j++)if(W[i*D+j]!=F.zero)weights[i].push_back({j,W[i*D+j]});
 auto assemble=[&](int h,int z){std::vector<E>A(R*H,F.zero);for(int row=0;row<R;row++){std::array<E,D>v;v.fill(F.zero);for(auto t:weights[row]){int s=start[t.j],k=t.j-s;for(int j=0;j<=k;j++)v[s+j]=add[v[s+j]][mul[t.v][powers[h][s+k-j]]];}for(int j=0;j<D;j++)if(v[j]!=F.zero){const auto&table=mul[v[j]];auto b=B[z].data()+j*H,a=A.data()+row*H;for(int c=0;c<H;c++)a[c]=add[a[c]][table[b[c]]];}}return A;};
 auto select=[&](const std::vector<E>&pool,int order){std::vector<E>A(H*H);for(int i=0;i<H;i++)std::copy_n(pool.data()+selections[order][i]*H,H,A.data()+i*H);return A;};
 fq_nmod_ctx_t ctx;nmod_poly_t p;nmod_poly_init(p,31);for(int j=0;j<=2;j++)nmod_poly_set_coeff_ui(p,j,mod[j]);fq_nmod_ctx_init_modulus(ctx,p,"b");
 auto independent=[&](const std::vector<E>&A){nmod_poly_t pp;nmod_poly_init(pp,31);fq_nmod_mat_t M;fq_nmod_mat_init(M,H,H,ctx);for(int i=0;i<H;i++)for(int j=0;j<H;j++){int v=F.zech2padic(A[i*H+j]);nmod_poly_zero(pp);for(int k=0;k<2;k++){nmod_poly_set_coeff_ui(pp,k,v%31);v/=31;}fq_nmod_set_nmod_poly(fq_nmod_mat_entry(M,i,j),pp,ctx);}int r=fq_nmod_mat_rank(M,ctx);fq_nmod_mat_clear(M,ctx);nmod_poly_clear(pp);return r;};

 for(int z=0;z<3;z++){auto A=select(assemble(0,z),0);ck(A==refs[z],"all GP reference matrix entries");int r=rankGF(F,A,H);ck(r==independent(A),"FLINT reference rank");std::cout<<"CONTROL degree="<<z+3<<" rank="<<r<<" all_entries=true\n";auto C=A;for(int j=0;j<H;j++)C[(H-1)*H+j]=C[j];ck(rankGF(F,C,H)==independent(C),"duplicate-row backend control");}
 for(int z=0;z<3;z++){auto A=select(assemble(1,z),0);int r=rankGF(F,A,H);ck(r==independent(A),"FLINT shifted rank");std::cout<<"CONTROL degree="<<z+6<<" rank="<<r<<"\n";}
 
 std::vector<int>jobs;int priorPeriod=1;std::vector<bool>need(1,true);if(argc==6){std::ifstream prior(argv[5]);std::string line;std::getline(prior,line);std::vector<std::pair<int,int>> rows;int maxResidue=-1;while(std::getline(prior,line)){std::replace(line.begin(),line.end(),',',' ');std::istringstream ss(line);int residue,rep,rank,order;ss>>residue>>rep>>rank>>order;ck(ss.good()||ss.eof(),"prior CSV row");ck(residue>=0&&rank>=0&&rank<=H,"prior row range");rows.push_back({residue,rank});maxResidue=std::max(maxResidue,residue);}priorPeriod=maxResidue+1;ck((int)rows.size()==priorPeriod,"complete prior cover");need.assign(priorPeriod,false);std::vector<bool>seen(priorPeriod,false);for(auto row:rows){ck(!seen[row.first],"unique prior residues");seen[row.first]=true;need[row.first]=row.second<H;}}int commonPeriod=std::lcm(priorPeriod,3*period);std::set<int>keys;for(int d=0;d<commonPeriod;d++)if(need[d%priorPeriod])keys.insert((d-3+3*period)%(3*period));jobs.assign(keys.begin(),keys.end());std::cout<<"PRIOR_PERIOD "<<priorPeriod<<" COMMON_PERIOD "<<commonPeriod<<" UNIQUE_REQUIRED_STATES "<<jobs.size()<<"\n";int count=pilot?std::min(pilot,(int)jobs.size()):(int)jobs.size();std::vector<int>ranks(count,-1),chosen(count,-1);
 #pragma omp parallel for schedule(dynamic)
 for(int job=0;job<count;job++){int h=jobs[job]/3,z=jobs[job]%3;auto pool=assemble(h,z);for(auto&x:pool){if(small[mul[unscales[h]][x]]<0)throw std::runtime_error("cut fails prime-field descent after undoing normalization");}int best=-1;for(int order=0;order<24;order++){int r=rankGF(K,select(pool,order),H);if(r>best){best=r;chosen[job]=order;}if(r==H)break;}ranks[job]=best;auto witness=select(pool,chosen[job]);ck(independent(witness)==best,"every selected full-period rank independently verified by FLINT");}
 fq_nmod_ctx_clear(ctx);nmod_poly_clear(p);
 std::ofstream out(argv[2]);out<<"degree_residue,representative,rank,order_index\n";std::array<int,H+1>hist{};for(int j=0;j<count;j++){hist[ranks[j]]++;out<<(jobs[j]+3)%(3*period)<<','<<jobs[j]+3<<','<<ranks[j]<<','<<chosen[j]<<'\n';}out.close();
 for(int r=0;r<=H;r++)if(hist[r])std::cout<<"RANK "<<r<<" count="<<hist[r]<<"\n";
 std::cout<<"COMPLETE all_selected_ranks_FLINT_verified=true count="<<count<<" full="<<(count==(int)jobs.size())<<" seconds="<<std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count()<<"\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}return 0;}
