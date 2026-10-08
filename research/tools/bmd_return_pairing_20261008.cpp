// Exact diagnostic pairings of the full nonlinear return tangent vectors.
// Does not assert that these are the complete higher section obstructions.
#define main preceding_period_main
#include "bmd_period_cover_20261008.cpp"
#undef main
int main(int argc,char**argv){
 try{
  ck(argc==6,"usage period-input kernel-input vector-input vectors output-directory");
  std::ifstream in(argv[1]);int nc,f,bf,L;in>>nc>>f>>bf>>L;ck(nc==2&&f==6&&bf==3,"retained nonordinary field");
  std::vector<int64_t>mod(f+1);for(auto&v:mod)in>>v;Curve c(f,bf,L,mod);
  for(auto&v:c.labels)v=c.read(in);
  for(int b=0;b<4;b++){
   auto&ca=c.cases[b];in>>ca.b>>ca.n>>ca.h>>ca.ref>>ca.expected;
   if(b){ca.K.resize(ca.n*ca.h);for(auto&v:ca.K)v=c.read(in);}
   ca.reference.resize(ca.n*ca.h);for(auto&v:ca.reference)v=c.read(in);
  }c.prepare();c.cycle.resize(c.total);
  std::ifstream order(argv[3]);int n;order>>n;ck(n==466,"all characters");
  int off=0;
  for(int i=0;i<n;i++){
   int mask,g,v;order>>mask>>g;ck(c.offset[mask]==off&&c.dim[mask]==g,"identical holomorphic basis order");off+=g;
   for(int j=0;j<27*2*g;j++)order>>v;
  }ck(off==769,"complete basis");
  auto embed=[&](int x){ck(x>=0&&x<27,"F27 code");El a=c.labels[1],z=c.F.padic2zech(x%3),t;
   c.F.mul(t,c.F.padic2zech(x/3%3),a);c.F.addin(z,t);
   c.F.mul(t,c.F.padic2zech(x/9),power(c.F,a,2));c.F.addin(z,t);return z;};
  std::ifstream ki(argv[2]);int rows,cols;ki>>rows>>cols;ck(rows==140&&cols==61,"actual kernel");
  std::vector<El>K(140*61);for(auto&v:K){int x;ki>>x;v=embed(x);}ck(ki.good(),"kernel input");
  std::ifstream vi(argv[4]);int nv,dim;vi>>nv>>dim;ck(nv==27&&dim==769,"all return vectors");
  std::filesystem::create_directories(argv[5]);
  std::ofstream out(std::string(argv[5])+"/pairings.txt");
  std::vector<std::vector<int>>known;
  for(int ii=0;ii<27;ii++){
   int k,m;vi>>k>>m;std::vector<int>v(dim);for(auto&x:v)vi>>x;ck(vi.good()&&k==ii+1,"complete return row");
   auto it=std::find(known.begin(),known.end(),v);
   if(it!=known.end()){out<<"ALIAS "<<k<<" "<<1+(it-known.begin())<<"\n";continue;}
   known.push_back(v);int id=known.size();
   for(int j=0;j<dim;j++)c.cycle[j]=embed(v[j]);
   auto C=c.assemble(0,0);std::vector<El>D(140*61),A(61*61);
   for(int j=0;j<61;j++)FFLAS::fgemv(c.F,FFLAS::FflasNoTrans,140,140,c.F.one,C.data(),140,K.data()+j,61,c.F.zero,D.data()+j,61);
   for(int j=0;j<61;j++)FFLAS::fgemv(c.F,FFLAS::FflasTrans,140,61,c.F.one,K.data(),61,D.data()+j,61,c.F.zero,A.data()+j,61);
   int rc=rankGF(c.F,C,140,140),ra=rankGF(c.F,A,61,61);
   ck(c.rankFlint(C,140)==rc&&c.rankFlint(A,61)==ra,"independent full/restricted ranks");
   for(int i=0;i<61;i++)for(int j=0;j<61;j++)ck(A[i*61+j]==A[j*61+i],"symmetric restricted pairing");
   out<<"PAIR "<<id<<" "<<k<<" "<<m<<" "<<rc<<" "<<ra<<"\n";
   out<<"FULL 140\n";for(auto x:C)out<<c.F.zech2padic(x)<<" ";out<<"\nRESTRICTED 61\n";
   for(auto x:A)out<<c.F.zech2padic(x)<<" ";out<<"\n";
   std::cout<<"RETURN_PAIRING k="<<k<<" order="<<m<<" full_rank="<<rc<<" restricted_rank="<<ra<<" FFPACK_FLINT=matched\n";
  }
  std::cout<<"RETURN_PAIRINGS_COMPLETED distinct_vectors="<<known.size()<<" full_source140 actual_kernel61=true\n";
 }catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<"\n";return 1;}
}
