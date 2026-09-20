#include <algorithm>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>
using Bits=std::vector<uint64_t>;
static bool bit(const Bits& x,int p){return (x[p/64]>>(p%64))&1;}
static void flip(Bits& x,int p){x[p/64]^=uint64_t(1)<<(p%64);}
static void add(Bits& x,const Bits& y){for(size_t j=0;j<x.size();++j)x[j]^=y[j];}
struct Basis {
  int size,words,rank=0;std::vector<Bits> rows;
  explicit Basis(int n):size(n),words((n+63)/64),rows(n){}
  bool insert(Bits x,int floor=0){
    for(int p=size-1;p>=floor;--p)if(bit(x,p)){
      if(rows[p].empty()){rows[p]=std::move(x);++rank;return true;}
      add(x,rows[p]);
    }return false;
  }
  Bits reduce(Bits x,int floor=0)const{
    for(int p=size-1;p>=floor;--p)if(bit(x,p)&&!rows[p].empty())add(x,rows[p]);
    return x;
  }
};
struct Affine {uint64_t free=0,parameter=0;int constant=0;};
struct Pair {Affine a,b;};
struct SharedRow {Bits top,lower;};
static void require(bool ok,const char* msg){if(!ok)throw std::runtime_error(msg);}
static int c3(int x){return x*(x-1)*(x-2)/6;}
static void numbers(std::ostream& out,const std::vector<uint64_t>& xs){
  out<<'[';for(size_t i=0;i<xs.size();++i){if(i)out<<',';out<<xs[i];}out<<']';
}
int main(int argc,char** argv){try{
  int N=6,M=6;uint64_t seed=1;std::string dest;
  for(int i=1;i+1<argc;i+=2){std::string a=argv[i];
    if(a=="--holes")N=std::stoi(argv[i+1]);
    else if(a=="--constraints")M=std::stoi(argv[i+1]);
    else if(a=="--seed")seed=std::stoull(argv[i+1]);
    else if(a=="--out")dest=argv[i+1];
    else throw std::runtime_error("unknown option");
  }
  require(argc%2==1&&!dest.empty(),"supply --out NEW.json");
  require(N>=5&&N<=6&&M>=0&&M<=6,"bounded checker requires holes 5..6 and constraints 0..6");
  require(!std::ifstream(dest).good(),"output exists");
  int rows=N+1,t=N-1,v=rows*t,d=v-M,count=1<<M;
  int low=1+d+d*(d-1)/2,lowwords=(low+63)/64,cubes=c3(d),topwords=(cubes+63)/64;
  int quadratic_start=d+1;
  std::vector<int> pair_index(d*d,-1),triple_index(d*d*d,-1);
  std::vector<std::pair<int,int>> pairs;
  int next=quadratic_start;
  for(int i=0;i<d;++i)for(int j=i+1;j<d;++j){pair_index[i*d+j]=pair_index[j*d+i]=next++;pairs.push_back({i,j});}
  next=0;for(int i=0;i<d;++i)for(int j=i+1;j<d;++j)for(int k=j+1;k<d;++k)triple_index[(i*d+j)*d+k]=next++;
  // Fixed independent linear parts in the row-quotient coordinates.
  std::mt19937_64 rng(seed);std::vector<uint64_t> original,rankrows(v);
  for(int attempts=0;int(original.size())<M&&attempts<10000;++attempts){
    uint64_t x=rng()&((uint64_t(1)<<v)-1),z=x;
    for(int j=v-1;j>=0;--j)if((z>>j)&1){if(rankrows[j])z^=rankrows[j];else{rankrows[j]=z;original.push_back(x);break;}}
  }require(int(original.size())==M,"failed independent constraint generation");
  auto reduced=original;std::vector<uint64_t> transform(M);std::vector<int> pivots;
  for(int i=0;i<M;++i)transform[i]=uint64_t(1)<<i;
  int r=0;
  for(int col=0;col<v&&r<M;++col){int pick=r;while(pick<M&&!((reduced[pick]>>col)&1))++pick;if(pick==M)continue;
    std::swap(reduced[r],reduced[pick]);std::swap(transform[r],transform[pick]);
    for(int j=0;j<M;++j)if(j!=r&&((reduced[j]>>col)&1)){reduced[j]^=reduced[r];transform[j]^=transform[r];}
    pivots.push_back(col);++r;
  }require(r==M,"constraint rank mismatch");
  std::vector<int> freecols;for(int j=0;j<v;++j)if(std::find(pivots.begin(),pivots.end(),j)==pivots.end())freecols.push_back(j);
  std::vector<Affine> image(v);
  for(int j=0;j<d;++j)image[freecols[j]].free=uint64_t(1)<<j;
  for(int i=0;i<M;++i){image[pivots[i]].parameter=transform[i];for(int j=0;j<d;++j)if((reduced[i]>>freecols[j])&1)image[pivots[i]].free^=uint64_t(1)<<j;}
  for(int i=0;i<M;++i){uint64_t f=0,p=0;for(int j=0;j<v;++j)if((original[i]>>j)&1){f^=image[j].free;p^=image[j].parameter;}require(f==0&&p==(uint64_t(1)<<i),"affine quotient verification failed");}
  std::vector<Pair> generators;
  for(int i=0;i<rows;++i)for(int a=0;a<t;++a)for(int b=a+1;b<t;++b)generators.push_back({image[i*t+a],image[i*t+b]});
  for(int i=0;i<rows;++i)for(int j=i+1;j<rows;++j){
    for(int a=0;a<t;++a)generators.push_back({image[i*t+a],image[j*t+a]});
    Affine a,b;a.constant=b.constant=1;
    for(int k=0;k<t;++k){a.free^=image[i*t+k].free;a.parameter^=image[i*t+k].parameter;b.free^=image[j*t+k].free;b.parameter^=image[j*t+k].parameter;}
    generators.push_back({a,b});
  }
  int k2=generators.size();require(k2==(N+1)*(2*N*N-3*N+2)/2,"quadratic inventory mismatch");
  uint64_t memory_estimate=uint64_t(cubes)*(topwords+count*lowwords)*8+uint64_t(d)*k2*count*lowwords*8;
  require(memory_estimate<200000000,"checker preflight memory estimate exceeds 200 MB");
  auto product=[&](const Pair& g,int c){Bits q(lowwords);int a=g.a.constant^(std::popcount(g.a.parameter&uint64_t(c))&1),b=g.b.constant^(std::popcount(g.b.parameter&uint64_t(c))&1);
    if(a&&b)flip(q,0);
    for(int i=0;i<d;++i){if(a&&((g.b.free>>i)&1))flip(q,1+i);if(b&&((g.a.free>>i)&1))flip(q,1+i);}
    for(int i=0;i<d;++i)if((g.a.free>>i)&1)for(int j=0;j<d;++j)if((g.b.free>>j)&1)flip(q,i==j?1+i:pair_index[i*d+j]);
    return q;
  };
  std::vector<std::vector<Bits>> q(count);std::vector<Basis> qbases;
  for(int c=0;c<count;++c){qbases.emplace_back(low);for(const auto& g:generators){auto z=product(g,c);q[c].push_back(z);qbases.back().insert(std::move(z),quadratic_start);}require(qbases.back().rank==k2,"sample is not quadratically faithful");}
  std::vector<SharedRow> leading_basis(cubes);std::vector<Bits> kernel_lower;int leading_rank=0;
  for(int g=0;g<k2;++g)for(int x=0;x<d;++x){
    SharedRow z{Bits(topwords),Bits(count*lowwords)};
    for(int j=0;j<int(pairs.size());++j)if(bit(q[0][g],quadratic_start+j)){
      auto [a,b]=pairs[j];if(x==a||x==b)continue;int c=x;if(b>c)std::swap(b,c);if(a>b)std::swap(a,b);flip(z.top,triple_index[(a*d+b)*d+c]);
    }
    for(int c=0;c<count;++c){Bits lo(lowwords);const auto& poly=q[c][g];if(bit(poly,0))flip(lo,1+x);
      for(int j=0;j<d;++j)if(bit(poly,1+j))flip(lo,j==x?1+x:pair_index[x*d+j]);
      for(int j=0;j<int(pairs.size());++j)if(bit(poly,quadratic_start+j)){auto [a,b]=pairs[j];if(x==a||x==b)flip(lo,quadratic_start+j);}
      std::copy(lo.begin(),lo.end(),z.lower.begin()+c*lowwords);
    }
    bool stored=false;
    for(int p=cubes-1;p>=0;--p)if(bit(z.top,p)){
      if(leading_basis[p].top.empty()){leading_basis[p]=std::move(z);++leading_rank;stored=true;break;}
      add(z.top,leading_basis[p].top);add(z.lower,leading_basis[p].lower);
    }
    if(!stored)kernel_lower.push_back(std::move(z.lower));
  }
  require(int(kernel_lower.size())==d*k2-leading_rank,"leading-kernel dimension mismatch");
  std::vector<Basis> falls;for(int c=0;c<count;++c)falls.emplace_back(low);
  std::vector<bool> equations(1<<(M+1));uint64_t variation_checks=0;
  for(const auto& packed:kernel_lower){std::vector<Bits> residues(count);
    for(int c=0;c<count;++c){Bits row(packed.begin()+c*lowwords,packed.begin()+(c+1)*lowwords);residues[c]=qbases[c].reduce(std::move(row),quadratic_start);falls[c].insert(residues[c]);}
    for(int p=quadratic_start;p<low;++p){int constant=bit(residues[0],p);uint64_t mask=0;
      for(int j=0;j<M;++j)if(bit(residues[1<<j],p)!=constant)mask|=uint64_t(1)<<j;
      equations[mask|(uint64_t(constant)<<M)]=true;
      for(int c=0;c<count;++c){require((constant^(std::popcount(mask&uint64_t(c))&1))==bit(residues[c],p),"quadratic variation not affine");++variation_checks;}
    }
  }
  std::vector<uint64_t> eq_basis(M),eq_rhs(M);int variation_rank=0;bool inconsistent=false;
  std::vector<uint64_t> unique_equations;
  for(int enc=0;enc<int(equations.size());++enc)if(equations[enc]&&enc){unique_equations.push_back(enc);uint64_t a=enc&((1<<M)-1),b=(enc>>M)&1;
    for(int j=M-1;j>=0;--j)if((a>>j)&1){if(eq_basis[j]){a^=eq_basis[j];b^=eq_rhs[j];}else{eq_basis[j]=a;eq_rhs[j]=b;++variation_rank;a=0;b=0;break;}}
    if(a==0&&b)inconsistent=true;
  }
  int quadratic_zero=0,no_fall=0;std::ofstream out(dest);require(bool(out),"cannot open output");
  out<<"{\n\"scope\":\"Exact fixed-space PHP residue test; one common cubic elimination, all right-hand sides; no formal certificate\",\n\"holes\":"<<N<<",\"constraints\":"<<M<<",\"seed\":"<<seed<<",\"v\":"<<v<<",\"d\":"<<d<<",\n\"linear_parts\":";numbers(out,original);
  out<<",\n\"old_coordinate_images\":[";for(int j=0;j<v;++j){if(j)out<<',';out<<"{\"free_mask\":"<<image[j].free<<",\"rhs_mask\":"<<image[j].parameter<<'}';}out<<"],\n";
  out<<"\"quadratic_rank\":"<<k2<<",\"leading_cubic_rank\":"<<leading_rank<<",\"leading_relation_count\":"<<kernel_lower.size()<<",\"variation_rank\":"<<variation_rank<<",\"quadratic_affine_consistent\":"<<(inconsistent?"false":"true")<<",\n\"affine_equations\":";numbers(out,unique_equations);
  out<<",\n\"rhs_results\":[\n";
  for(int c=0;c<count;++c){int qrank=0,lrank=0;for(int p=0;p<low;++p)if(!falls[c].rows[p].empty()){if(p>=quadratic_start)++qrank;else ++lrank;}
    bool satisfies=true;for(auto eq:unique_equations)if((std::popcount((eq&((1<<M)-1))&uint64_t(c))&1)!=int(eq>>M))satisfies=false;
    require(satisfies==(qrank==0),"affine solution-set mismatch");quadratic_zero+=qrank==0;no_fall+=falls[c].rank==0;
    if(c)out<<",\n";out<<"{\"rhs\":"<<c<<",\"fall_dimension\":"<<falls[c].rank<<",\"quadratic_fall_rank\":"<<qrank<<",\"lower_fall_rank\":"<<lrank<<",\"one_in_G3\":"<<(!falls[c].rows[0].empty()?"true":"false")<<'}';
  }
  int predicted=inconsistent?0:(1<<(M-variation_rank));require(predicted==quadratic_zero,"affine count mismatch");
  if(M==0){require(no_fall==1,"old-base stability control failed");require(leading_rank==c3(v)-c3(rows)*(N*N*N-6*N*N+8*N-1),"old cubic dimension control failed");}
  out<<"\n],\n\"quadratic_zero_count\":"<<quadratic_zero<<",\"no_fall_count\":"<<no_fall<<",\"variation_checks\":"<<variation_checks<<",\"estimated_primary_bytes\":"<<memory_estimate<<",\"passed\":true\n}\n";out.close();require(bool(out),"output write failure");
  std::cout<<"{\"holes\":"<<N<<",\"constraints\":"<<M<<",\"quadratic_rank\":"<<k2<<",\"variation_rank\":"<<variation_rank<<",\"quadratic_zero_count\":"<<quadratic_zero<<",\"no_fall_count\":"<<no_fall<<",\"rhs_count\":"<<count<<",\"passed\":true}\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
