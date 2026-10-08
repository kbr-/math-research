// Exact Phi_(4+r) classification on kerPhi4, not an exception-set computation.
// Reuse verified coefficient engine, FFLAS contractions, FFPACK ranks and FLINT controls.
#define main previous_period_cover_main
#include "bmd_period_cover_20261008.cpp"
#undef main
std::vector<El> restrictCup(const Curve&c,const std::vector<El>&K,int s){
 auto C=c.assemble(0,s); const auto&F=c.F;
 std::vector<El>D(140*61),A(61*61);
 for(int j=0;j<61;j++)FFLAS::fgemv(F,FFLAS::FflasNoTrans,140,140,F.one,C.data(),140,K.data()+j,61,F.zero,D.data()+j,61);
 for(int j=0;j<61;j++)FFLAS::fgemv(F,FFLAS::FflasTrans,140,61,F.one,K.data(),61,D.data()+j,61,F.zero,A.data()+j,61);
 return A;
}
int main(int argc,char**argv){
 try{
  ck(argc==6,"usage period-inputs kernel-input output-directory pilot-count-or-0 max-seconds");
  int pilot=std::stoi(argv[4]);double limit=std::stod(argv[5]);
  ck(pilot>=0&&pilot<=256&&limit>0&&limit<=1700,"bounded sizing");
  omp_set_dynamic(0);omp_set_num_threads(14);
  auto start=Clock::now();std::ifstream in(argv[1]);int nc,f,bf,L;in>>nc>>f>>bf>>L;
  ck(nc==2&&f==6&&bf==3&&L==28080,"retained first nonordinary curve");
  std::vector<int64_t>mod(f+1);for(auto&x:mod)in>>x;Curve c(f,bf,L,mod);
  for(auto&x:c.labels)x=c.read(in);
  for(int b=0;b<4;b++){
   auto&ca=c.cases[b];in>>ca.b>>ca.n>>ca.h>>ca.ref>>ca.expected;
   ck(ca.b==b&&ca.n<=769&&ca.h<=140,"case dimensions");
   if(b){ca.K.resize(ca.n*ca.h);for(auto&x:ca.K)x=c.read(in);}
   ca.reference.resize(ca.n*ca.h);for(auto&x:ca.reference)x=c.read(in);
  }
  c.prepare();c.buildCycle();
  std::ifstream kin(argv[2]);int rows,cols;kin>>rows>>cols;ck(rows==140&&cols==61,"full surviving kernel");
  auto embed=[&](int x){ck(x>=0&&x<27,"F27 code");El a=c.labels[1],val=c.F.padic2zech(x%3),v;
    c.F.mul(v,c.F.padic2zech((x/3)%3),a);c.F.addin(val,v);
    c.F.mul(v,c.F.padic2zech(x/9),power(c.F,a,2));c.F.addin(val,v);return val;};
  std::vector<El>K(140*61),reference(61*61);
  for(auto&x:K){int code;kin>>code;x=embed(code);}
  for(auto&x:reference){int code;kin>>code;x=embed(code);}
  ck(kin.good(),"complete exported matrices");
  std::vector<El>Kt(K.size());for(int i=0;i<140;i++)for(int j=0;j<61;j++)Kt[j*140+i]=K[i*61+j];
  ck(rankGF(c.F,Kt,61,140)==61,"kernel independence");
  auto control=restrictCup(c,K,5);ck(control==reference,"all GAP/PARI reference coefficients");
  ck(rankGF(c.F,control,61,61)==61&&c.rankFlint(control,61)==61,"independent reference ranks");
  auto zero=restrictCup(c,K,4);ck(rankGF(c.F,zero,61,61)==0&&c.rankFlint(zero,61)==0,"zero-return control");
  for(int j=0;j<61;j++)control[j]=c.F.zero;
  ck(rankGF(c.F,control,61,61)==60&&c.rankFlint(control,61)==60,"corrupted row control");
  double setup=sec(start);int count=pilot?pilot:L;
  ck(pilot||limit>=10,"full run needs measured allowance");
  std::vector<int>residues(count),ranks(count);
  for(int i=0;i<count;i++)residues[i]=pilot?(4+i*109)%L:i;
  double validation=0;auto phase=Clock::now();
  #pragma omp parallel for schedule(dynamic,8)
  for(int i=0;i<count;i++){
   auto A=restrictCup(c,K,residues[i]);ranks[i]=rankGF(c.F,A,61,61);
  }
  double elapsed=sec(phase);
  if(pilot){
   phase=Clock::now();
   for(int i=0;i<std::min(count,16);i++)ck(c.rankFlint(restrictCup(c,K,residues[i]),61)==ranks[i],"independent pilot ranks");
   std::set<int>checked;
   for(int i=0;i<count;i++)if(checked.insert(ranks[i]).second){
    ck(c.rankFlint(restrictCup(c,K,residues[i]),61)==ranks[i],"independent rank-stratum control");
    std::cout<<"STRATUM_CONTROL residue="<<residues[i]<<" rank="<<ranks[i]<<" FLINT=matched\n";
   }
   validation=sec(phase);
  }
  std::filesystem::create_directories(argv[3]);
  std::ofstream out(std::string(argv[3])+"/ranks.csv");out<<"coefficient_residue,rank\n";
  std::array<int,62>hist{};for(int i=0;i<count;i++){out<<residues[i]<<","<<ranks[i]<<"\n";hist[ranks[i]]++;}
  std::cout<<"UNIT_PERIOD_COMPLETE count="<<count<<" setup_seconds="<<setup<<" matrix_seconds="<<elapsed
    <<" independent_validation_seconds="<<validation<<" total_seconds="<<sec(start)<<"\n";
  for(int r=0;r<=61;r++)if(hist[r])std::cout<<"RANK "<<r<<" COUNT "<<hist[r]<<"\n";
  ck(sec(start)<=limit,"measured computation exceeded explicit allowance");
 }catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<"\n";return 1;}
}
