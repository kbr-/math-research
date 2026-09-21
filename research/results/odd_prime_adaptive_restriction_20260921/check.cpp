#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
using namespace std;
uint64_t choose(int n,int k){if(k<0||k>n)return 0;uint64_t z=1;for(int i=1;i<=k;i++)z=z*(n-i+1)/i;return z;}
uint64_t power(uint64_t a,int b){uint64_t z=1;for(int i=0;i<b;i++)z*=a;return z;}
int main(int argc,char**argv){
 if(argc!=2)throw runtime_error("usage check OUTPUT.json");
 const int m=16,k=5;if(m>16)throw runtime_error("enumeration budget");
 uint64_t total=choose(m,k);ofstream out(argv[1]);if(!out)throw runtime_error("output");
 out<<"{\"rows\":16,\"live_rows\":5,\"total_live_sets\":"<<total<<",\"cases\":[";
 bool first=true;int cases=0;
 for(int R:{1,4,8,16})for(int u=1;u<=5;u++){
  uint64_t bad=0,maskA=(uint64_t(1)<<R)-1;
  for(unsigned mask=0;mask<(1u<<m);mask++)if(__builtin_popcount(mask)==k&&__builtin_popcountll(mask&maskA)>=u)bad++;
  uint64_t exact=0;for(int j=u;j<=k;j++)exact+=choose(R,j)*choose(m-R,k-j);
  uint64_t witnesses=choose(R,u)*choose(m-u,k-u);
  if(bad!=exact||bad>witnesses)throw runtime_error("hypergeometric identity/bound");
  if(bad*power(m,u)>choose(R,u)*power(k,u)*total)throw runtime_error("power bound");
  if(!first)out<<",";
  first=false;cases++;
  out<<"{\"support_rows\":"<<R<<",\"threshold\":"<<u<<",\"bad_live_sets\":"<<bad<<",\"witness_union_bound\":"<<witnesses<<"}";
 }
 out<<"],\"full_support_control\":\"All live sets retain all five rows of a full support; no constant thinning at growing live size is inferred\",\"scope\":\"Exact finite row-survival bounds only, not an asymptotic source proof\"}\n";
 cout<<cases<<" exact cases on "<<total<<" live row sets passed, including full-support control.\n";
}
