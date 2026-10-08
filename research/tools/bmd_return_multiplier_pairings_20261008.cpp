// Exhaustive equal-order competition between unit departure and nonlinear return.
// Uses the complete kernel and exact stored return vectors; FFPACK and FLINT ranks.
#define main preceding_period_main
#include "bmd_period_cover_20261008.cpp"
#undef main
std::vector<El> restrictMatrix(const Curve&c,const std::vector<El>&C,const std::vector<El>&K){
 std::vector<El>D(140*61),A(61*61);
 for(int j=0;j<61;j++)FFLAS::fgemv(c.F,FFLAS::FflasNoTrans,140,140,c.F.one,C.data(),140,K.data()+j,61,c.F.zero,D.data()+j,61);
 for(int j=0;j<61;j++)FFLAS::fgemv(c.F,FFLAS::FflasTrans,140,61,c.F.one,K.data(),61,D.data()+j,61,c.F.zero,A.data()+j,61);
 return A;
}
int main(int argc,char**argv){
 try{
  ck(argc==6,"usage period-input kernel-input vector-input vectors output-directory");
  std::ifstream in(argv[1]);int nc,f,bf,L;in>>nc>>f>>bf>>L;ck(nc==2&&f==6&&bf==3,"retained field");
  std::vector<int64_t>mod(f+1);for(auto&v:mod)in>>v;Curve c(f,bf,L,mod);
  for(auto&v:c.labels)v=c.read(in);
  for(int b=0;b<4;b++){
   auto&ca=c.cases[b];in>>ca.b>>ca.n>>ca.h>>ca.ref>>ca.expected;
   if(b){ca.K.resize(ca.n*ca.h);for(auto&v:ca.K)v=c.read(in);}
   ca.reference.resize(ca.n*ca.h);for(auto&v:ca.reference)v=c.read(in);
  }c.prepare();c.buildCycle();
  std::ifstream oi(argv[3]);int n;oi>>n;ck(n==466,"all characters");int off=0;
  for(int i=0;i<n;i++){int mask,g,x;oi>>mask>>g;ck(c.offset[mask]==off&&c.dim[mask]==g,"same basis");off+=g;for(int j=0;j<27*2*g;j++)oi>>x;}
  ck(off==769,"full differential basis");
  auto embed=[&](int x){ck(x>=0&&x<27,"F27 code");El a=c.labels[1],z=c.F.padic2zech(x%3),t;
   c.F.mul(t,c.F.padic2zech(x/3%3),a);c.F.addin(z,t);c.F.mul(t,c.F.padic2zech(x/9),power(c.F,a,2));c.F.addin(z,t);return z;};
  std::ifstream ki(argv[2]);int rows,cols;ki>>rows>>cols;ck(rows==140&&cols==61,"actual kernel");
  std::vector<El>K(140*61);for(auto&v:K){int x;ki>>x;v=embed(x);}ck(ki.good(),"kernel input");
  std::array<std::vector<El>,5>base,fullbase;
  for(int d=1;d<=4;d++){
   fullbase[d]=c.assemble(0,4+d);
   base[d]=restrictMatrix(c,fullbase[d],K);
   ck(rankGF(c.F,base[d],61,61)==61&&c.rankFlint(base[d],61)==61,"earlier unit-departure pairings");
  }
  std::ifstream vi(argv[4]);int nv,dim;vi>>nv>>dim;ck(nv==27&&dim==769,"all return vectors");
  std::filesystem::create_directories(argv[5]);std::ofstream out(std::string(argv[5])+"/combinations.txt");
  std::vector<std::vector<int>>known;int count=0,failed=0;
  for(int ii=0;ii<27;ii++){
   int k,m;vi>>k>>m;std::vector<int>v(dim);for(auto&x:v)vi>>x;ck(vi.good()&&k==ii+1,"complete row");
   auto it=std::find(known.begin(),known.end(),v);
   if(it!=known.end()){out<<"ALIAS "<<k<<" "<<1+(it-known.begin())<<"\n";continue;}
   known.push_back(v);int d=0,mm=m;while(mm%3==0){mm/=3;d++;}ck(mm==1&&d>=2&&d<=4,"return degree");
   for(int j=0;j<dim;j++)c.cycle[j]=embed(v[j]);
   auto fullA=c.assemble(0,0);
   auto A=restrictMatrix(c,fullA,K);
   ck(rankGF(c.F,A,61,61)==61,"retained return reference");
   for(int sign:{1,-1}){
    auto mix=A;for(size_t j=0;j<mix.size();j++){
     if(sign==1)c.F.addin(mix[j],base[d][j]);else c.F.subin(mix[j],base[d][j]);
    }
    int r=rankGF(c.F,mix,61,61);ck(c.rankFlint(mix,61)==r,"independent mixed rank");count++;if(r!=61){
     failed++;auto fullmix=fullA;
     for(size_t j=0;j<fullmix.size();j++){if(sign==1)c.F.addin(fullmix[j],fullbase[d][j]);else c.F.subin(fullmix[j],fullbase[d][j]);}
     std::array<int,729>code;code.fill(-1);for(int x=0;x<27;x++)code[c.F.zech2padic(embed(x))]=x;
     std::ofstream gp(std::string(argv[5])+"/failed-tangent.gp");gp<<"{\nMIXED_TANGENT=[";
     for(int i=0;i<140;i++){if(i)gp<<",";gp<<"[";for(int j=0;j<140;j++){if(j)gp<<",";int value=code[c.F.zech2padic(fullmix[i*140+j])];ck(value>=0,"F27 tangent descent");gp<<value;}gp<<"]";}
     gp<<"];\nMIXED_K="<<k<<"; MIXED_SIGN="<<sign<<";\n}\n";
    }
    out<<"COMBINATION "<<known.size()<<" "<<k<<" "<<d<<" "<<sign<<" "<<r<<"\n";
    for(auto x:mix)out<<c.F.zech2padic(x)<<" ";out<<"\n";
    std::cout<<"MULTIPLIER_PAIRING k="<<k<<" d="<<d<<" sign="<<sign<<" rank="<<r<<" FFPACK_FLINT=matched\n";
   }
  }
  std::cout<<"MULTIPLIER_PAIRINGS_COMPLETE combinations="<<count<<" failures="<<failed<<" complete_kernel61=true\n";
 }catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<"\n";return 1;}
}
