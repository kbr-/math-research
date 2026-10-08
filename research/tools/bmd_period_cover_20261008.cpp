// Complete coefficient-period certificate at the retained actual marks, not a degree-exception search.
// Installed Givaro GFq arithmetic and FFPACK LUdivine_gauss/fgemv; FLINT validates reference ranks.
// Kernel bases and reference product matrices come from bmd_period_data_20261008.gp.
// Generate each coefficient cycle once. Test the nonordinary curve first for b0..2 and
// ordinary b3 first; test the other curve only on failure residues, reusing CRT duplicates.
// --pilot N measures the entire matrix-construction/rank path before --full is authorized/sized.
#include <givaro/gfq.h>
#include <fflas-ffpack/fflas-ffpack.h>
#include <flint/fq_nmod_mat.h>
#include <omp.h>
#include <array>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <memory>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using Field=Givaro::GFqDom<int64_t>;
using El=Field::Element;
using Clock=std::chrono::steady_clock;
double sec(Clock::time_point t){return std::chrono::duration<double>(Clock::now()-t).count();}
void ck(bool v,const std::string&m){if(!v)throw std::runtime_error(m);}
El power(const Field&F,El a,int n){El r=F.one,t;while(n){if(n&1){F.mul(t,r,a);r=t;}n>>=1;if(n){F.mul(t,a,a);a=t;}}return r;}
struct Mono{int mask,j;};
std::vector<Mono> basis(int d){std::vector<Mono>v;for(int S=0;S<512;S++)if(__builtin_popcount((unsigned)S)<=d)for(int j=0;2*j+__builtin_popcount((unsigned)S)<=d;j++)v.push_back({S,j});return v;}
int rankGF(const Field&F,std::vector<El>A,int r,int c){
 ck(r<=c,"library generic LU is used only with rows<=columns");
 std::vector<size_t>P(c),Q(r);
 return FFPACK::LUdivine_gauss(F,FFLAS::FflasNonUnit,r,c,A.data(),c,P.data(),Q.data());
}
struct Term{uint16_t index,coefficient;};
struct Descriptor{uint8_t count=0;std::array<Term,4>terms;};
struct Case{int b=0,n=0,h=0,ref=0,expected=0;std::vector<El>K,reference;std::vector<Descriptor>descriptors;};
struct Block{int size,offset;std::vector<El>B;};
struct Curve{
 int f,basef,period,q,total=0;
 std::vector<int64_t>mod;
 Field F;
 std::array<El,9>labels;
 std::array<std::vector<El>,512>poly;
 std::array<int,512>offset{},dim{};
 std::vector<Block>blocks;
 std::array<Case,4>cases;
 std::vector<uint16_t>cycle,cubes;
 std::array<std::vector<int16_t>,4>ranks;
 fq_nmod_ctx_t flint;
 Curve(int f_,int bf,int per,std::vector<int64_t>m):f(f_),basef(bf),period(per),q(1),mod(std::move(m)),F(3,f,mod){
  for(int i=0;i<f;i++)q*=3;
  ck((f==6&&basef==3&&period==28080)||(f==8&&basef==8&&period==74880),"fixed reviewed periods");
  ck(f!=8 || mod==std::vector<int64_t>({1,2,2,1,0,0,2,1,1}),"retained ordinary field modulus");
  for(int x=0;x<q;x++)ck(F.zech2padic(F.padic2zech(x))==(uint64_t)x,"field roundtrip");
  nmod_poly_t p;nmod_poly_init(p,3);for(int i=0;i<=f;i++)nmod_poly_set_coeff_ui(p,i,mod[i]);
  fq_nmod_ctx_init_modulus(flint,p,"a");nmod_poly_clear(p);
  for(auto&r:ranks)r.assign(period,-1);
 }
 ~Curve(){fq_nmod_ctx_clear(flint);}
 El read(std::istream&in){int x;in>>x;ck(in.good()&&x>=0&&x<q,"encoded field input");return F.padic2zech(x);}
 void prepare(){
  std::set<El>distinct(labels.begin(),labels.end());ck(distinct.size()==9&&!distinct.count(F.zero),"admissible labels");
  if(basef==3){
   El a=labels[1],v=power(F,a,3),t;F.mul(t,F.padic2zech(2),a);F.addin(v,t);F.addin(v,F.padic2zech(2));ck(F.isZero(v),"recorded F27 generator polynomial");
   for(int i=0;i<9;i++)ck(labels[i]==power(F,a,i)&&power(F,labels[i],27)==labels[i],"recorded nonordinary tuple");
  }else{std::array<int,9>codes={508,5690,5164,3098,2894,6147,276,4463,174};for(int i=0;i<9;i++)ck(labels[i]==F.padic2zech(codes[i]),"recorded ordinary tuple");}
  poly[0]={F.one};
  for(int S=1;S<512;S++){
   int bit=__builtin_ctz((unsigned)S),parent=S^(1<<bit);
   poly[S].assign(poly[parent].size()+1,F.zero);
   for(size_t j=0;j<poly[parent].size();j++){F.addin(poly[S][j],poly[parent][j]);El t;F.mul(t,poly[parent][j],labels[bit]);F.addin(poly[S][j+1],t);}
  }
  offset.fill(-1);dim.fill(0);
  for(int S=0;S<512;S++){
   int g=(__builtin_popcount((unsigned)S)-1)/2;if(g<=0)continue;
   offset[S]=total;dim[S]=g;Block bl{g,total,{}};total+=g;
   bl.B.assign(g*g,F.zero);
   for(int i=0;i<g;i++)for(int j=0;j<g;j++){int k=3*i+2-j;if(k>=0&&k<(int)poly[S].size())bl.B[i*g+j]=poly[S][k];}
   blocks.push_back(std::move(bl));
  }
  ck(total==769&&blocks.size()==466,"complete holomorphic characters");
  cubes.resize(q);for(int x=0;x<q;x++)cubes[x]=power(F,x,3);
  for(auto&ca:cases){
   auto I=basis(3+ca.b),II=basis(3-ca.b);ck((int)I.size()==ca.n&&(int)II.size()==ca.h,"complete source dimensions");
   ck(ca.n==256*ca.b+ca.h,"source RR count");
   if(ca.b){std::vector<El>kt(ca.n*ca.h);for(int i=0;i<ca.n;i++)for(int j=0;j<ca.h;j++)kt[j*ca.n+i]=ca.K[i*ca.h+j];ck(rankGF(F,std::move(kt),ca.h,ca.n)==ca.h,"independent kernel columns");}
   ca.descriptors.resize(ca.n*ca.h);
   for(int i=0;i<ca.n;i++)for(int j=0;j<ca.h;j++){
    int U=511^(I[i].mask^II[j].mask),common=I[i].mask&II[j].mask,shift=I[i].j+II[j].j;
    auto&ds=ca.descriptors[i*ca.h+j];ck(offset[U]>=0,"holomorphic character");
    for(size_t k=0;k<poly[common].size();k++)if(!F.isZero(poly[common][k])){
     ck(shift+(int)k<dim[U]&&ds.count<4,"holomorphic product degree");
     ds.terms[ds.count++]={(uint16_t)(offset[U]+shift+k),(uint16_t)poly[common][k]};
    }
   }
  }
 }
 void buildCycle(){
  cycle.resize((size_t)period*total);std::vector<uint16_t>r(total,0),next(total);
  for(const auto&bl:blocks)r[bl.offset]=F.one;
  int begin=basef==3?4:0,last=basef==3?period+4:period;
  std::vector<bool>seen(period,false);
  for(int s=0;s<=last;s++){
   if(s>=begin){
    int residue=s%period;auto dst=cycle.data()+(size_t)residue*total;
    if(seen[residue])ck(std::equal(r.begin(),r.end(),dst),"coefficient cycle closes");
    else{std::copy(r.begin(),r.end(),dst);seen[residue]=true;}
   }
   if(s==last)break;
   for(const auto&bl:blocks)for(int j=0;j<bl.size;j++){
    El sum=F.zero,t;
    for(int i=0;i<bl.size;i++){F.mul(t,cubes[r[bl.offset+i]],bl.B[i*bl.size+j]);F.addin(sum,t);}
    next[bl.offset+j]=sum;
   }
   r.swap(next);
  }
  ck(std::all_of(seen.begin(),seen.end(),[](bool x){return x;}),"complete coefficient cycle");
 }
 std::vector<El>assemble(int b,int s)const{
  const auto&ca=cases[b];auto row=cycle.data()+(size_t)s*total;std::vector<El>C(ca.n*ca.h);
  for(size_t i=0;i<C.size();i++){
   El val=F.zero,tmp;const auto&ds=ca.descriptors[i];
   for(int j=0;j<ds.count;j++){auto t=ds.terms[j];F.mul(tmp,row[t.index],t.coefficient);F.addin(val,tmp);}C[i]=val;
  }
  return C;
 }
 std::vector<El>pair(int b,const std::vector<El>&C)const{
  const auto&ca=cases[b];if(b==0)return C;
  std::vector<El>A(ca.h*ca.h);
  for(int j=0;j<ca.h;j++)FFLAS::fgemv(F,FFLAS::FflasTrans,ca.n,ca.h,F.one,ca.K.data(),ca.h,C.data()+j,ca.h,F.zero,A.data()+j,ca.h);
  return A;
 }
 int rankFlint(const std::vector<El>&A,int h)const{
  fq_nmod_mat_t M;fq_nmod_mat_init(M,h,h,flint);nmod_poly_t p;nmod_poly_init(p,3);
  for(int i=0;i<h;i++)for(int j=0;j<h;j++){
   int v=F.zech2padic(A[i*h+j]);nmod_poly_zero(p);
   for(int k=0;k<f;k++){nmod_poly_set_coeff_ui(p,k,v%3);v/=3;}
   fq_nmod_set_nmod_poly(fq_nmod_mat_entry(M,i,j),p,flint);
  }
  int r=fq_nmod_mat_rank(M,flint);nmod_poly_clear(p);fq_nmod_mat_clear(M,flint);return r;
 }
 void references()const{
  auto low=pair(0,assemble(0,4));int lowrank=rankGF(F,low,140,140);
  ck(lowrank<=81&&rankFlint(low,140)==lowrank,"rank bound for the repeated81-jet central form");
  std::cout<<"LOW_JET_CONTROL base_degree="<<basef<<" residue4_rank="<<lowrank<<" bound81=true\n";
  for(int b=0;b<4;b++){
   const auto&ca=cases[b];auto C=assemble(b,ca.ref);ck(C==ca.reference,"all reference product coefficients match");
   auto A=pair(b,C);int r=rankGF(F,A,ca.h,ca.h);
   ck(r==ca.expected&&rankFlint(A,ca.h)==r,"PARI/Givaro/FLINT reference ranks agree");
   if(r==ca.h){for(int j=0;j<ca.h;j++)A[j]=F.zero;ck(rankGF(F,A,ca.h,ca.h)==r-1&&rankFlint(A,ca.h)==r-1,"reference zero-row control");}
  }
 }
};
struct Job{int curve,b,s;};
struct Measurement{double assembly=0,rank=0;};
int main(int argc,char**argv){
 try{
  ck(argc==6,"usage inputs output-directory workers pilot-count-or-0(full) max-seconds");
  int workers=std::stoi(argv[3]),pilot=std::stoi(argv[4]);double maxSeconds=std::stod(argv[5]);
  ck(workers>=1&&workers<=14&&pilot>=0&&pilot<=256&&maxSeconds>0&&maxSeconds<=1700,"resource bounds");
  omp_set_dynamic(0);omp_set_num_threads(workers);
  auto start=Clock::now();std::ifstream in(argv[1]);int nc;in>>nc;ck(nc==2,"two curves");
  std::vector<std::unique_ptr<Curve>>curves;
  for(int ci=0;ci<nc;ci++){
   int f,bf,L;in>>f>>bf>>L;std::vector<int64_t>mod(f+1);for(auto&x:mod)in>>x;
   auto c=std::make_unique<Curve>(f,bf,L,mod);
   for(auto&x:c->labels)x=c->read(in);
   for(int b=0;b<4;b++){
    auto&ca=c->cases[b];in>>ca.b>>ca.n>>ca.h>>ca.ref>>ca.expected;
    ck(ca.b==b&&ca.ref>=0&&ca.ref<L&&ca.n<=769&&ca.h<=140,"case bounds");
    if(b){ca.K.resize(ca.n*ca.h);for(auto&x:ca.K)x=c->read(in);}
    ca.reference.resize(ca.n*ca.h);for(auto&x:ca.reference)x=c->read(in);
   }
   ck(in.good(),"complete input");c->prepare();curves.push_back(std::move(c));
  }
  double load=sec(start);auto phase=Clock::now();
  for(auto&c:curves)c->buildCycle();double cycleTime=sec(phase);phase=Clock::now();
  for(auto&c:curves)c->references();double refTime=sec(phase);
  std::cout<<std::setprecision(9)<<"SETUP load_seconds="<<load<<" cycle_seconds="<<cycleTime<<" reference_seconds="<<refTime<<" workers="<<workers<<"\n"<<std::flush;
  std::filesystem::create_directories(argv[2]);std::string out=argv[2];
  std::array<std::array<double,4>,2>at{},rt{};std::array<std::array<long,4>,2>counts{};
  auto run=[&](const std::vector<Job>&jobs,const char*name){
   std::vector<Measurement>measure(jobs.size());auto t=Clock::now();
   #pragma omp parallel for schedule(dynamic,16)
   for(size_t i=0;i<jobs.size();i++){
    const auto job=jobs[i];auto&c=*curves[job.curve];const auto&ca=c.cases[job.b];
    auto s0=Clock::now();auto C=c.assemble(job.b,job.s);auto A=c.pair(job.b,C);
    measure[i].assembly=sec(s0);s0=Clock::now();
    c.ranks[job.b][job.s]=rankGF(c.F,std::move(A),ca.h,ca.h);measure[i].rank=sec(s0);
   }
   for(size_t i=0;i<jobs.size();i++){const auto j=jobs[i];at[j.curve][j.b]+=measure[i].assembly;rt[j.curve][j.b]+=measure[i].rank;counts[j.curve][j.b]++;}
   std::cout<<"STAGE name="<<name<<" jobs="<<jobs.size()<<" wall_seconds="<<sec(t)<<"\n"<<std::flush;
   ck(sec(start)<maxSeconds,"measured stage exceeds declared budget");
  };
  if(pilot){
   std::vector<Job>jobs;
   for(int ci=0;ci<2;ci++)for(int b=0;b<4;b++){
    std::set<int>used;for(int j=0;j<pilot;j++){int s=(j*7919)%curves[ci]->period;ck(used.insert(s).second,"distinct pilot residues");jobs.push_back({ci,b,s});}
   }
   run(jobs,"pilot");
   // Additional independently ranked pipeline samples include non-reference residue classes.
   for(int ci=0;ci<2;ci++)for(int b=0;b<4;b++)for(int j=0;j<std::min(4,pilot);j++){
    auto&c=*curves[ci];int s=j*7919%c.period;auto A=c.pair(b,c.assemble(b,s));
    ck(c.rankFlint(A,c.cases[b].h)==c.ranks[b][s],"independent pilot rank");
   }
  }else{
   std::vector<Job>first;
   for(int s=0;s<curves[0]->period;s++)for(int b=0;b<3;b++)first.push_back({0,b,s});
   for(int s=0;s<curves[1]->period;s++)first.push_back({1,3,s});
   run(first,"primary");
   int common=std::lcm(curves[0]->period,curves[1]->period);ck(common==224640,"reviewed common period");
   std::vector<Job>second;std::array<std::array<std::vector<bool>,4>,2>needed;
   for(int ci=0;ci<2;ci++)for(int b=0;b<4;b++)needed[ci][b].assign(curves[ci]->period,false);
   for(int s=0;s<common;s++){
    int r0=s%curves[0]->period,r1=s%curves[1]->period;
    for(int b=0;b<3;b++)if(curves[0]->ranks[b][r0]<curves[0]->cases[b].h)needed[1][b][r1]=true;
    if(curves[1]->ranks[3][r1]<1)needed[0][3][r0]=true;
   }
   for(int ci=0;ci<2;ci++)for(int b=0;b<4;b++)for(int s=0;s<curves[ci]->period;s++)if(needed[ci][b][s])second.push_back({ci,b,s});
   run(second,"secondary");
   std::ofstream uncovered(out+"/uncovered.csv");uncovered<<"b,exponent_residue,nonordinary_rank,ordinary_rank\n";
   std::array<long,4>bad{};
   for(int s=0;s<common;s++)for(int b=0;b<4;b++){
    int r0=curves[0]->ranks[b][s%curves[0]->period],r1=curves[1]->ranks[b][s%curves[1]->period],h=curves[0]->cases[b].h;
    if(r0!=h&&r1!=h){ck(r0>=0&&r1>=0,"both uncovered alternatives evaluated");uncovered<<b<<","<<s<<","<<r0<<","<<r1<<"\n";bad[b]++;}
   }
   std::cout<<"COVERAGE common_period="<<common<<" uncovered_by_b="<<bad[0]<<","<<bad[1]<<","<<bad[2]<<","<<bad[3]<<"\n";
  }
  double serialUpper=0;
  std::ofstream times(out+"/timings.csv");times<<"curve,b,jobs,assembly_seconds,rank_seconds\n";
  for(int ci=0;ci<2;ci++){
   std::ofstream ranks(out+"/curve-"+std::to_string(ci)+"-ranks.csv");ranks<<"exponent_residue,b0,b1,b2,b3\n";
   for(int s=0;s<curves[ci]->period;s++){ranks<<s;for(int b=0;b<4;b++)ranks<<","<<curves[ci]->ranks[b][s];ranks<<"\n";}
   for(int b=0;b<4;b++){
    times<<std::setprecision(9)<<ci<<","<<b<<","<<counts[ci][b]<<","<<at[ci][b]<<","<<rt[ci][b]<<"\n";
    if(counts[ci][b])serialUpper+=(at[ci][b]+rt[ci][b])*curves[ci]->period/counts[ci][b];
    std::cout<<"COST curve="<<ci<<" b="<<b<<" jobs="<<counts[ci][b]<<" assembly_seconds="<<at[ci][b]<<" rank_seconds="<<rt[ci][b]<<"\n";
   }
  }
  std::cout<<"PERIOD_COVER_COMPLETED mode="<<(pilot?"pilot":"full")<<" wall_seconds="<<sec(start)
   <<" conservative_all_cases_seconds="<<load+cycleTime+refTime+2*serialUpper/workers
   <<" actual_degree_coverage_not_claimed=true\n";
 }catch(const std::exception&e){std::cerr<<"PERIOD_COVER_FAILED "<<e.what()<<"\n";return 1;}
}
