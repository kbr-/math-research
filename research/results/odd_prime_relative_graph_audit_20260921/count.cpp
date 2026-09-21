#include <cstdint>
#include <iostream>
#include <vector>
using Graph=std::vector<std::vector<bool>>;
uint64_t count(const Graph& a,int left,int next,std::vector<int>& chosen){
 if(!left)return 1;
 uint64_t z=0;
 for(int v=next;v<=int(a.size())-left;++v){bool ok=true;for(int u:chosen)if(a[u][v]){ok=false;break;}
 if(ok){chosen.push_back(v);z+=count(a,left-1,v+1,chosen);chosen.pop_back();}}
 return z;
}
int main(){
 std::cout<<"[";
 for(int c=0;c<2;c++){
  int n=c?96:64,k=c?3:4;Graph g(n,std::vector<bool>(n));
  if(c)for(int i=0;i<n;i++)g[i][(i+1)%n]=g[(i+1)%n][i]=true;
  Graph h=g;for(int i=0;i<n/2;i++)h[i][i+n/2]=h[i+n/2][i]=true;
  std::vector<int> chosen;auto a=count(g,k,0,chosen),b=count(h,k,0,chosen);
  if(c)std::cout<<",";
  std::cout<<"{\"n\":"<<n<<",\"delta\":"<<(c?2:0)<<",\"k\":"<<k<<",\"R\":"<<n/2<<",\"before\":"<<a<<",\"after\":"<<b<<"}";
 }
 std::cout<<"]\n";
}
