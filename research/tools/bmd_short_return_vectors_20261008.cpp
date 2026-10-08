// Reuse the verified lifted coefficient library; extend its shared prefixes to bases1..4.
#define main previous_return_vector_main
#include "bmd_return_vectors_20261008.cpp"
#undef main
struct ShortFrame:Frame{
 Context&prepare(int K){
  if(ctx[K])return *ctx[K];
  ctx[K]=std::make_unique<Context>(mask,K);auto&q=*ctx[K];prefix[K].resize(g);
  for(int ell=0;ell<g;ell++){
   Poly H=q.base;int borrow=ell;
   for(int digit=0;digit<4+3*(2*g-1);digit++){
    H=q.step(H,digit,2-borrow%3);borrow/=3;prefix[K][ell].push_back(H);
   }
  }return q;
 }
 E coefficient(int K,int ell,int j,int m,int base){
  auto&q=prepare(K);int exponent=base+3*j,borrow=ell;
  for(int z=0;z<exponent;z++)borrow/=3;
  int rest=m-1-borrow;ck(rest>=0,"nonnegative shifted coefficient");
  Poly H=prefix[K][ell][exponent-1];int digit=exponent;
  while(rest){H=q.step(H,digit,rest%3);rest/=3;digit++;}return H.coeff(0);
 }
};
int main(int argc,char**argv){
 try{
  ck(argc==5,"usage short-vector-input coefficient-controls output-directory pilot-count-or0");
  controls(argv[2]);int pilot=std::stoi(argv[4]);ck(pilot==0||(pilot>=4&&pilot<=32),"bounded pilot");
  omp_set_dynamic(0);omp_set_num_threads(14);
  std::ifstream in(argv[1]);int n;in>>n;ck(n==466,"complete characters");
  std::vector<ShortFrame>frames;frames.reserve(n);int total=0;
  for(int i=0;i<n;i++){
   ShortFrame f;in>>f.mask>>f.g;ck(f.mask>0&&f.mask<512&&f.g>=1&&f.g<=4,"character scope");
   f.offset=total;total+=f.g;f.c.resize(81,std::vector<int>(2*f.g));
   for(auto&row:f.c)for(auto&v:row){in>>v;ck(in.good()&&v>=0&&v<243,"canonical integer coefficients");}
   frames.push_back(std::move(f));
  }ck(total==769,"complete source");auto start=Clock::now();std::exception_ptr failure;
  if(pilot){
   std::vector<int>jobs;for(int i=0;i<pilot;i++)jobs.push_back(i*(n-1)/(pilot-1));
   #pragma omp parallel for schedule(dynamic)
   for(int ii=0;ii<(int)jobs.size();ii++)try{
    auto&f=frames[jobs[ii]];
    for(int base=1,limit=3;base<=4;base++,limit*=3)for(int m=3;m<=limit;m+=3){
     int K=1,t=m;while(t%3==0){K++;t/=3;}
     for(int ell=0;ell<f.g;ell++)for(int j=0;j<2*f.g;j++){
      auto got=f.coefficient(K,ell,j,m,base);
      if((m==3||m==limit)&&j==0){uint64_t q=1;for(int k=0;k<base;k++)q*=3;
       ck(got==f.prepare(K).coeff(m*q-1-ell),"independent unshared prefix/borrow control");}
     }
    }
   }catch(...){
    #pragma omp critical
    {if(!failure)failure=std::current_exception();}
   }
   if(failure)std::rethrow_exception(failure);
   std::cout<<"SHORT_VECTOR_PILOT characters="<<pilot<<" bases1to4=true borrow_controls=true seconds="<<elapsed(start)<<"\n";return 0;
  }
  std::filesystem::create_directories(argv[3]);
  for(int base=1,limit=3;base<=4;base++,limit*=3){
   std::vector<bool>active(81,true);std::vector<int>orders(81);std::vector<std::vector<int>>vectors(81,std::vector<int>(769));int remaining=81;
   for(int m=3;m<=limit&&remaining;m+=3){
    auto phase=Clock::now();int unit=m,K=1,divisor=1;while(unit%3==0){K++;unit/=3;divisor*=3;}
    #pragma omp parallel for schedule(dynamic,1)
    for(int fi=0;fi<n;fi++)try{
     auto&f=frames[fi];auto&q=f.prepare(K);
     for(int ell=0;ell<f.g;ell++){
      std::vector<E>sum(81);
      for(int j=0;j<2*f.g;j++){
       E value=f.coefficient(K,ell,j,m,base);
       for(int k=0;k<81;k++)if(active[k])sum[k]=q.ring.add(sum[k],q.ring.scalar(value,f.c[k][j]-(j==0)));
      }
      for(int k=0;k<81;k++)if(active[k]){
       int code=0,power3=1;for(int t=0;t<3;t++){
        ck(sum[k][t]%divisor==0,"integral pre-leading logarithm");code+=power3*(sum[k][t]/divisor*(unit%3)%3);power3*=3;
       }vectors[k][f.offset+ell]=code;
      }
     }
    }catch(...){
     #pragma omp critical
     {if(!failure)failure=std::current_exception();}
    }
    if(failure)std::rethrow_exception(failure);
    for(int k=0;k<81;k++)if(active[k]&&std::any_of(vectors[k].begin(),vectors[k].end(),[](int x){return x!=0;})){active[k]=false;orders[k]=m;remaining--;}
    std::cout<<"SHORT_VECTOR_STAGE base="<<base<<" m="<<m<<" remaining="<<remaining<<" seconds="<<elapsed(phase)<<"\n"<<std::flush;
   }
   ck(remaining==0,"supersingular order bound recovered");
   std::ofstream out(std::string(argv[3])+"/base-"+std::to_string(base)+"-vectors.txt");out<<"81 769\n";
   for(int k=0;k<81;k++){out<<k+1<<" "<<orders[k]<<"\n";for(auto v:vectors[k])out<<v<<" ";out<<"\n";}
   std::set<std::vector<int>>distinct(vectors.begin(),vectors.end());std::set<int>degrees(orders.begin(),orders.end());
   std::cout<<"SHORT_VECTOR_BASE_COMPLETE base="<<base<<" distinct="<<distinct.size()<<" orders";for(auto d:degrees)std::cout<<" "<<d;std::cout<<"\n"<<std::flush;
  }
  std::cout<<"SHORT_VECTORS_COMPLETE returns81 bases4 seconds="<<elapsed(start)<<"\n";
 }catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<"\n";return 1;}
}
