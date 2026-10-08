// First nonlinear return vectors from integral Picard logarithm residues.
// FLINT performs every polynomial multiplication. Shared low ternary prefixes
// make the cost logarithmic in the coefficient index; no giant series is formed.
#include <flint/nmod_poly.h>
#include <omp.h>
#include <array>
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <set>
#include <stdexcept>
#include <vector>
using Clock=std::chrono::steady_clock;
using E=std::array<long,3>;
void ck(bool c,const char*s){if(!c)throw std::runtime_error(s);}
double elapsed(Clock::time_point t){return std::chrono::duration<double>(Clock::now()-t).count();}
struct Ring{
 long mod;int K;E sa;
 E add(E a,E b)const{for(int i=0;i<3;i++)a[i]=(a[i]+b[i])%mod;return a;}
 E neg(E a)const{for(auto&x:a)x=(mod-x)%mod;return a;}
 E sub(E a,E b)const{return add(a,neg(b));}
 E scalar(E a,long c)const{c=(c%mod+mod)%mod;for(auto&x:a)x=x*c%mod;return a;}
 E mul(E a,E b)const{
  long v[5]={};for(int i=0;i<3;i++)for(int j=0;j<3;j++)v[i+j]+=a[i]*b[j];
  return {(v[0]+v[3])%mod,(v[1]+v[3]+v[4])%mod,(v[2]+v[4])%mod};
 }
 E pow(E a,uint64_t n)const{E r={1,0,0};while(n){if(n&1)r=mul(r,a);n>>=1;if(n)a=mul(a,a);}return r;}
 E sigma(E a)const{return add(E{a[0],0,0},add(scalar(sa,a[1]),scalar(mul(sa,sa),a[2])));}
 explicit Ring(int k):mod(1),K(k),sa{1,1,0}{
  for(int i=0;i<K;i++)mod*=3;
  for(int j=0;j<K;j++){
   E f=sub(sub(pow(sa,3),sa),E{1,0,0}),t=scalar(mul(sa,sa),3),sum={0,0,0},v={1,0,0};
   for(int i=0;i<K;i++){sum=add(sum,v);v=mul(v,t);}
   sa=add(sa,mul(f,sum));
  }
  ck(sub(sub(pow(sa,3),sa),E{1,0,0})==E{0,0,0},"Frobenius root");
  ck(sigma(sigma(sa))==E{0,1,0},"Frobenius order");
 }
};
struct NP{
 nmod_poly_struct p;
 explicit NP(long m){nmod_poly_init(&p,m);}~NP(){nmod_poly_clear(&p);}
 NP(const NP&)=delete;NP&operator=(const NP&)=delete;
};
struct Poly{
 long mod;nmod_poly_struct c[3];
 explicit Poly(long m):mod(m){for(auto&x:c)nmod_poly_init(&x,m);}
 ~Poly(){for(auto&x:c)nmod_poly_clear(&x);}
 Poly(const Poly&o):Poly(o.mod){for(int i=0;i<3;i++)nmod_poly_set(c+i,o.c+i);}
 Poly(Poly&&o)noexcept:Poly(o.mod){for(int i=0;i<3;i++)nmod_poly_swap(c+i,o.c+i);}
 Poly&operator=(const Poly&o){
  if(this==&o)return *this;
  if(mod!=o.mod){for(auto&x:c)nmod_poly_clear(&x);mod=o.mod;for(auto&x:c)nmod_poly_init(&x,mod);}
  for(int i=0;i<3;i++)nmod_poly_set(c+i,o.c+i);return *this;
 }
 Poly&operator=(Poly&&o)noexcept{
  if(this==&o)return *this;
  if(mod!=o.mod){for(auto&x:c)nmod_poly_clear(&x);mod=o.mod;for(auto&x:c)nmod_poly_init(&x,mod);}
  for(int i=0;i<3;i++)nmod_poly_swap(c+i,o.c+i);return *this;
 }
 E coeff(int j)const{E e;for(int i=0;i<3;i++)e[i]=nmod_poly_get_coeff_ui(c+i,j);return e;}
 void set(int j,E e){for(int i=0;i<3;i++)nmod_poly_set_coeff_ui(c+i,j,e[i]);}
 long degree()const{return std::max({nmod_poly_degree(c),nmod_poly_degree(c+1),nmod_poly_degree(c+2)});}
};
Poly mul(const Poly&u,const Poly&v){
 ck(u.mod==v.mod,"same coefficient ring");long m=u.mod;
 NP a0(m),a1(m),a2(m),b01(m),b02(m),b12(m),x(m),y(m);
 nmod_poly_mul(&a0.p,u.c,v.c);nmod_poly_mul(&a1.p,u.c+1,v.c+1);nmod_poly_mul(&a2.p,u.c+2,v.c+2);
 auto cross=[&](nmod_poly_struct*out,int i,int j,nmod_poly_struct*ai,nmod_poly_struct*aj){
  nmod_poly_add(&x.p,u.c+i,u.c+j);nmod_poly_add(&y.p,v.c+i,v.c+j);
  nmod_poly_mul(out,&x.p,&y.p);nmod_poly_sub(out,out,ai);nmod_poly_sub(out,out,aj);
 };
 cross(&b01.p,0,1,&a0.p,&a1.p);cross(&b02.p,0,2,&a0.p,&a2.p);cross(&b12.p,1,2,&a1.p,&a2.p);
 Poly r(m);nmod_poly_add(r.c,&a0.p,&b12.p);
 nmod_poly_add(r.c+1,&b01.p,&b12.p);nmod_poly_add(r.c+1,r.c+1,&a2.p);
 nmod_poly_add(r.c+2,&a1.p,&b02.p);nmod_poly_add(r.c+2,r.c+2,&a2.p);
 return r;
}
Poly power(Poly a,int n){
 Poly r(a.mod);r.set(0,{1,0,0});while(n){if(n&1)r=mul(r,a);n>>=1;if(n)a=mul(a,a);}return r;
}
Poly sigma(const Poly&p,const Ring&r){Poly q(r.mod);for(int i=0;i<=p.degree();i++)q.set(i,r.sigma(p.coeff(i)));return q;}
Poly rootpoly(int mask,const Ring&r){
 Poly p(r.mod);p.set(0,{1,0,0});
 if(mask==0){Poly t(r.mod);t.set(0,{1,0,0});t.set(1,{2,1,0});return mul(t,t);}
 E a={0,1,0},b={1,0,0};
 for(int i=0;i<9;i++){
  if(mask&(1<<i)){Poly t(r.mod);t.set(0,{1,0,0});t.set(1,b);p=mul(p,t);}
  b=r.mul(b,a);
 }return p;
}
struct Context{
 Ring ring;Poly base;std::vector<Poly>Q;int bound;
 Context(int mask,int K):ring(K),base(ring.mod){
  auto R=rootpoly(mask,ring);int A=1;for(int i=1;i<K;i++)A*=3;
  base=power(R,(A-1)/2);Q.push_back(power(R,A));Q.push_back(sigma(Q[0],ring));Q.push_back(sigma(Q[1],ring));
  bound=A*R.degree()/2;
 }
 Poly step(const Poly&H,int j,int digit)const{
  auto p=mul(H,Q[j%3]);Poly r(ring.mod);
  for(int i=digit;i<=p.degree();i+=3)r.set((i-digit)/3,p.coeff(i));
  ck(r.degree()<=bound,"bounded Cartier state");return r;
 }
 E coeff(uint64_t N)const{
  Poly H=base;int j=0;while(N){H=step(H,j,N%3);N/=3;j++;}return H.coeff(0);
 }
};
struct Frame{
 int mask,g,offset;std::vector<std::vector<int>>c;
 std::array<std::unique_ptr<Context>,6>ctx;
 std::array<std::vector<std::vector<Poly>>,6>prefix;
 Context&prepare(int K){
  if(ctx[K])return *ctx[K];
  ctx[K]=std::make_unique<Context>(mask,K);auto&q=*ctx[K];
  prefix[K].resize(g);
  for(int ell=0;ell<g;ell++){
   Poly H=q.base;int rest=ell;
   for(int digit=0;digit<4+3*(2*g-1);digit++){
    H=q.step(H,digit,2-rest%3);rest/=3;
    if(digit+1>=4&&(digit+1-4)%3==0)prefix[K][ell].push_back(H);
   }
   ck((int)prefix[K][ell].size()==2*g,"complete shared prefixes");
  }
  return q;
 }
 E coefficient(int K,int ell,int j,int m){
  auto&q=prepare(K);Poly H=prefix[K][ell][j];int digit=4+3*j,rest=m-1;
  while(rest){H=q.step(H,digit,rest%3);rest/=3;digit++;}
  return H.coeff(0);
 }
};
void controls(const char*path){
 std::ifstream in(path);int n;in>>n;ck(n==195,"all reference controls");
 std::array<std::array<std::unique_ptr<Context>,512>,6>cache;
 for(int i=0;i<n;i++){
  int K,mask;uint64_t N;E expected;in>>K>>mask>>N>>expected[0]>>expected[1]>>expected[2];
  ck(in.good()&&K>=1&&K<=5&&mask>=0&&mask<512,"control input");
  if(!cache[K][mask])cache[K][mask]=std::make_unique<Context>(mask,K);
  ck(cache[K][mask]->coeff(N)==expected,"independent PARI/FLINT coefficient mismatch");
 }
 std::cout<<"COEFFICIENT_LIBRARY_CONTROLS count195 matched=true\n"<<std::flush;
}
int main(int argc,char**argv){
 try{
  ck(argc==5,"usage vector-input coefficient-controls output-directory pilot-count-or0");
  controls(argv[2]);int pilot=std::stoi(argv[4]);ck(pilot==0||(pilot>=4&&pilot<=32),"bounded pilot");
  omp_set_dynamic(0);omp_set_num_threads(14);
  std::ifstream in(argv[1]);int n;in>>n;ck(n==466,"all character inputs");
  std::vector<Frame>frames;frames.reserve(n);int total=0;
  for(int i=0;i<n;i++){
   Frame f;in>>f.mask>>f.g;ck(f.mask>0&&f.mask<512&&f.g>0&&f.g<=4,"character bounds");
   f.offset=total;total+=f.g;f.c.resize(27,std::vector<int>(2*f.g));
   for(auto&row:f.c)for(auto&v:row){in>>v;ck(in.good()&&v>=0&&v<243,"reduced endomorphism coefficient");}
   frames.push_back(std::move(f));
  }ck(total==769,"complete holomorphic source");
  auto start=Clock::now();std::exception_ptr failure;
  if(pilot){
   std::set<int>chosen;for(int i=0;i<pilot;i++)chosen.insert(i*(n-1)/(pilot-1));
   std::vector<int>jobs(chosen.begin(),chosen.end());
   #pragma omp parallel for schedule(dynamic)
   for(int ji=0;ji<(int)jobs.size();ji++)try{
    auto&f=frames[jobs[ji]];
    for(int m=3;m<=81;m+=3){int K=1,v=m;while(v%3==0){K++;v/=3;}
     f.prepare(K);
     for(int ell=0;ell<f.g;ell++)for(int j=0;j<2*f.g;j++)(void)f.coefficient(K,ell,j,m);
    }
   }catch(...){
    #pragma omp critical
    {if(!failure)failure=std::current_exception();}
   }
   if(failure)std::rethrow_exception(failure);
   std::cout<<"RETURN_VECTOR_PILOT characters="<<jobs.size()<<" includes_genus4=true all27_degrees=true seconds="<<elapsed(start)<<"\n";
   return 0;
  }
  std::array<bool,27>active;active.fill(true);
  std::array<int,27>orders{};std::array<std::vector<int>,27>vectors;
  for(auto&v:vectors)v.resize(total);
  int remaining=27;
  for(int m=3;m<=81&&remaining;m+=3){
   auto stage=Clock::now();int v=m,K=1,divisor=1;while(v%3==0){K++;v/=3;divisor*=3;}
   int invunit=v%3; // inverse of 1 or2 modulo3
   #pragma omp parallel for schedule(dynamic,1)
   for(int fi=0;fi<n;fi++)try{
    auto&f=frames[fi];auto&q=f.prepare(K);
    for(int ell=0;ell<f.g;ell++){
     std::array<E,27>sum{};
     for(int j=0;j<2*f.g;j++){
      E value=f.coefficient(K,ell,j,m);
      for(int k=0;k<27;k++)if(active[k])sum[k]=q.ring.add(sum[k],q.ring.scalar(value,f.c[k][j]-(j==0)));
     }
     for(int k=0;k<27;k++)if(active[k]){
      int code=0,power3=1;
      for(int t=0;t<3;t++){
       ck(sum[k][t]%divisor==0,"nonintegral pre-leading Picard logarithm");
       int z=(sum[k][t]/divisor*invunit)%3;code+=power3*z;power3*=3;
      }vectors[k][f.offset+ell]=code;
     }
    }
   }catch(...){
    #pragma omp critical
    {if(!failure)failure=std::current_exception();}
   }
   if(failure)std::rethrow_exception(failure);
   for(int k=0;k<27;k++)if(active[k]&&std::any_of(vectors[k].begin(),vectors[k].end(),[](int x){return x!=0;})){
    orders[k]=m;active[k]=false;remaining--;
   }
   std::cout<<"RETURN_VECTOR_STAGE m="<<m<<" remaining="<<remaining<<" seconds="<<elapsed(stage)<<"\n"<<std::flush;
  }
  ck(remaining==0,"order81 witness was not recovered");
  std::filesystem::create_directories(argv[3]);std::ofstream out(std::string(argv[3])+"/vectors.txt");
  out<<"27 769\n";for(int k=0;k<27;k++){out<<k+1<<" "<<orders[k]<<"\n";for(auto x:vectors[k])out<<x<<" ";out<<"\n";}
  std::cout<<"RETURN_VECTORS_COMPLETE orders";for(auto o:orders)std::cout<<" "<<o;
  std::cout<<" seconds="<<elapsed(start)<<"\n";
 }catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<"\n";return 1;}
}
