#include <algorithm>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <utility>
#include <vector>
using Row = std::vector<uint64_t>;
struct Rank {
  int bits, words, value=0;
  std::vector<Row> basis;
  explicit Rank(int n): bits(n),words((n+63)/64),basis(n) {}
  Row row() const {return Row(words);}
  void add(Row x) {
    for(int p=bits-1;p>=0;--p) if((x[p/64]>>(p%64))&1) {
      if(basis[p].empty()){basis[p]=std::move(x);++value;return;}
      for(int j=0;j<=p/64;++j)x[j]^=basis[p][j];
    }
  }
};
void toggle(Row& x,int i){x[i/64]^=uint64_t(1)<<(i%64);}
int choose3(int n){return n*(n-1)*(n-2)/6;}
int main(int argc,char** argv){
  if(argc!=3 || std::string(argv[1])!="--out"){
    std::cerr<<"usage: check_conflict_cubic_dimension --out NEW.jsonl\n";return 2;}
  if(std::ifstream(argv[2]).good()){std::cerr<<"output already exists\n";return 2;}
  std::ofstream out(argv[2]);if(!out)return 2;
  int cases=0,failures=0;
  for(int N=5;N<=12;++N){
    int t=N-1,ambient=t*t*t;Rank rank(ambient);int generators=0;
    for(int pair=0;pair<3;++pair)for(int g=0;g<=t;++g)for(int q=0;q<t;++q){
      Row row=rank.row();
      for(int a=0;a<t;++a)for(int b=0;b<t;++b)if(g==t || (a==g && b==g)){
        int i=pair==2?q:a,j=pair==0?b:(pair==1?q:a),k=pair==0?q:b;
        toggle(row,(i*t+j)*t+k);
      }
      rank.add(std::move(row));++generators;
    }
    int expected=3*N*(N-1)-2*N;bool ok=rank.value==expected;
    out<<"{\"kind\":\"three_row_tensor\",\"N\":"<<N
       <<",\"ambient\":"<<ambient<<",\"generators\":"<<generators
       <<",\"rank\":"<<rank.value<<",\"expected_rank\":"<<expected
       <<",\"kernel\":"<<generators-rank.value<<",\"passed\":"<<(ok?"true":"false")<<"}\n";
    ++cases;failures+=!ok;
  }
  for(int N=5;N<=6;++N){
    int m=N+1,t=N-1,v=m*t,ambient=choose3(v);
    std::vector<std::vector<std::pair<int,int>>> gens;
    for(int i=0;i<m;++i)for(int a=0;a<t;++a)for(int b=a+1;b<t;++b)
      gens.push_back({{i*t+a,i*t+b}});
    for(int i=0;i<m;++i)for(int j=i+1;j<m;++j){
      for(int a=0;a<t;++a)gens.push_back({{i*t+a,j*t+a}});
      std::vector<std::pair<int,int>> all;
      for(int a=0;a<t;++a)for(int b=0;b<t;++b)all.push_back({i*t+a,j*t+b});
      gens.push_back(std::move(all));
    }
    std::vector<int> index(v*v*v,-1);int next=0;
    for(int i=0;i<v;++i)for(int j=i+1;j<v;++j)for(int k=j+1;k<v;++k)
      index[(i*v+j)*v+k]=next++;
    Rank rank(ambient);
    for(const auto& gen:gens)for(int q=0;q<v;++q){
      Row row=rank.row();
      for(auto [a,b]:gen)if(q!=a && q!=b){
        int c=q;if(a>b)std::swap(a,b);if(b>c)std::swap(b,c);if(a>b)std::swap(a,b);
        toggle(row,index[(a*v+b)*v+c]);
      }
      rank.add(std::move(row));
    }
    int expected=ambient-choose3(m)*(N*N*N-6*N*N+8*N-1);
    int syzygies=v*int(gens.size())-rank.value;
    int expected_syzygies=N*(N*N-1)*(5*N-2)/3;
    bool ok=rank.value==expected && syzygies==expected_syzygies;
    out<<"{\"kind\":\"full_conflict_space\",\"N\":"<<N<<",\"rows\":"<<m
       <<",\"v\":"<<v<<",\"quadratic_generators\":"<<gens.size()
       <<",\"ambient_cubics\":"<<ambient<<",\"rank\":"<<rank.value
       <<",\"expected_rank\":"<<expected<<",\"linear_syzygies\":"<<syzygies
       <<",\"expected_syzygies\":"<<expected_syzygies
       <<",\"passed\":"<<(ok?"true":"false")<<"}\n";
    ++cases;failures+=!ok;
  }
  out.close();if(!out)return 2;
  std::cout<<"{\"cases\":"<<cases<<",\"failures\":"<<failures<<"}\n";
  return failures?1:0;
}
