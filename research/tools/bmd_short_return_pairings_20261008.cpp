// Complete surviving-module cups for every distinct short-return leading vector.
#define main previous_period_cover_main
#include "bmd_period_cover_20261008.cpp"
#undef main
std::vector<El> restrictCup(const Curve&c,const std::vector<El>&C,const std::vector<El>&K,int h){
 std::vector<El>D(140*h),A(h*h);
 for(int j=0;j<h;j++)FFLAS::fgemv(c.F,FFLAS::FflasNoTrans,140,140,c.F.one,C.data(),140,K.data()+j,h,c.F.zero,D.data()+j,h);
 for(int j=0;j<h;j++)FFLAS::fgemv(c.F,FFLAS::FflasTrans,140,h,c.F.one,K.data(),h,D.data()+j,h,c.F.zero,A.data()+j,h);
 return A;
}
int main(int argc,char**argv){
 try{
  ck(argc==5,"usage period-input kernel-input vector-directory out");
  std::ifstream in(argv[1]);int nc,f,bf,L;in>>nc>>f>>bf>>L;ck(nc==2&&f==6&&bf==3,"retained field");
  std::vector<int64_t>mod(f+1);for(auto&v:mod)in>>v;Curve c(f,bf,L,mod);
  for(auto&v:c.labels)v=c.read(in);
  for(int b=0;b<4;b++){
   auto&ca=c.cases[b];in>>ca.b>>ca.n>>ca.h>>ca.ref>>ca.expected;
   if(b){ca.K.resize(ca.n*ca.h);for(auto&v:ca.K)v=c.read(in);}
   ca.reference.resize(ca.n*ca.h);for(auto&v:ca.reference)v=c.read(in);
  }c.prepare();c.buildCycle();
  auto embed=[&](int x){ck(x>=0&&x<27,"F27 code");El a=c.labels[1],z=c.F.padic2zech(x%3),t;
   c.F.mul(t,c.F.padic2zech(x/3%3),a);c.F.addin(z,t);c.F.mul(t,c.F.padic2zech(x/9),power(c.F,a,2));c.F.addin(z,t);return z;};
  std::array<std::vector<El>,9>baseCup;for(int j=1;j<=8;j++)baseCup[j]=c.assemble(0,j);
  std::ifstream ki(argv[2]);int nb;ki>>nb;ck(nb==4,"four actual kernels");
  std::ofstream out(argv[4]);int all=0;
  for(int b=1;b<=4;b++){
   int j,h;ki>>j>>h;ck(j==b&&h==std::array<int,4>{137,131,113,61}[b-1],"signed dimensions");
   std::vector<El>C0(140*140),K(140*h);for(auto&v:C0){int x;ki>>x;v=embed(x);}for(auto&v:K){int x;ki>>x;v=embed(x);}
   ck(ki.good()&&C0==baseCup[b],"full initial cup equals stable coefficient cup");
   for(int v=1;v<b;v++){auto A=restrictCup(c,baseCup[b+v],K,h);int r=rankGF(c.F,A,h,h);ck(c.rankFlint(A,h)==r,"departure rank");std::cout<<"UNIT_DEPARTURE base="<<b<<" valuation="<<v<<" rank="<<r<<" needed="<<h<<"\n";}
   std::ifstream vi(std::string(argv[3])+"/base-"+std::to_string(b)+"-vectors.txt");int nv,dim;vi>>nv>>dim;ck(nv==81&&dim==769,"full vector series");
   std::vector<std::vector<int>>seen;
   for(int ii=0;ii<nv;ii++){
    int k,m;vi>>k>>m;std::vector<int>vec(dim);for(auto&x:vec)vi>>x;ck(vi.good()&&k==ii+1,"complete vector row");
    if(std::find(seen.begin(),seen.end(),vec)!=seen.end())continue;seen.push_back(vec);
    int d=0,mm=m;while(mm%3==0){d++;mm/=3;}ck(mm==1&&d>=1&&d<=b,"nonlinear order bound");
    for(int z=0;z<dim;z++)c.cycle[z]=embed(vec[z]);
    auto C=c.assemble(0,0),A=restrictCup(c,C,K,h),D=restrictCup(c,baseCup[b+d],K,h);
    for(int sign:{0,1,-1}){
     auto mix=A;for(size_t z=0;z<mix.size();z++){if(sign==1)c.F.addin(mix[z],D[z]);if(sign==-1)c.F.subin(mix[z],D[z]);}
     int r=rankGF(c.F,mix,h,h);ck(c.rankFlint(mix,h)==r,"independent full survivor rank");
     std::cout<<"SHORT_PAIRING base="<<b<<" k="<<k<<" order="<<m<<" sign="<<sign<<" rank="<<r<<" needed="<<h<<"\n";
     out<<b<<" "<<k<<" "<<m<<" "<<sign<<" "<<h<<" "<<r<<"\n";for(auto x:mix)out<<c.F.zech2padic(x)<<" ";out<<"\n";all++;
    }
   }
  }
  std::cout<<"SHORT_PAIRINGS_COMPLETE matrices="<<all<<" all_FFPACK_FLINT_matched=true\n";
 }catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<"\n";return 1;}
}
