#include <algorithm>
#include <array>
#include <bit>
#include <cassert>
#include <fstream>
#include <functional>
#include <iostream>
#include <string>
#include <vector>
using namespace std;
long long C(int n,int k){if(k<0||k>n)return 0; long long v=1;for(int i=1;i<=k;i++)v=v*(n-i+1)/i;return v;}
int main(int argc,char**argv){
 if(argc!=3||string(argv[1])!="--out")return 2;
 constexpr int m=9,n=8,R=4,H=3;
 long long pairs=C(m,R)*C(n,H);if(pairs>10000)return 3;
 cerr<<"Budget: six fixtures, "<<pairs<<" survivor pairs each, <=3-edge matching tails; exact int64.\n";
 ofstream out(argv[2]);out<<"{\"rows\":9,\"columns\":8,\"live_rows\":4,\"live_columns\":3,\"pairs_per_fixture\":"<<pairs<<",\"fixtures\":[";
 for(int f=0;f<6;f++){
  array<int,m> a{};int edges=0;
  for(int i=0;i<m;i++)for(int j=0;j<n;j++){
   bool e=f==0?i==0:f==1?j==0:f==2?i==j:f==3?i<4&&j<4:f==4?i==0||j==0:true;
   if(e){a[i]|=1<<j;edges++;}
  }
  array<long long,1<<n> dp{};dp[0]=1;
  for(int i=0;i<m;i++){auto next=dp;for(int s=0;s<(1<<n);s++)for(int j=0;j<n;j++)if((a[i]>>j&1)&&!(s>>j&1))next[s|1<<j]+=dp[s];dp=next;}
  array<long long,4> match{},bad{};for(int s=0;s<(1<<n);s++)if(popcount((unsigned)s)<=3)match[popcount((unsigned)s)]+=dp[s];
  int maxedges=0,maxnu=0,maxcover=0;
  for(int rs=0;rs<(1<<m);rs++)if(popcount((unsigned)rs)==R)
   for(int cs=0;cs<(1<<n);cs++)if(popcount((unsigned)cs)==H){
    array<int,n> owner;owner.fill(-1);
    function<bool(int,int&)> aug=[&](int i,int &seen){for(int j=0;j<n;j++)if((cs&a[i])>>j&1)if(!(seen>>j&1)){seen|=1<<j;if(owner[j]<0||aug(owner[j],seen)){owner[j]=i;return true;}}return false;};
    int nu=0,ec=0,gr=0,gc=0;
    for(int i=0;i<m;i++)if(rs>>i&1){int seen=0;nu+=aug(i,seen);ec+=popcount((unsigned)(a[i]&cs));for(int j=0;j<n;j++)if((a[i]&cs)>>j&1)if(!(gr>>i&1)&&!(gc>>j&1)){gr|=1<<i;gc|=1<<j;}}
    int cover=popcount((unsigned)gr)+popcount((unsigned)gc);assert(cover<=2*nu);
    for(int i=0;i<m;i++)if(rs>>i&1)assert((gr>>i&1)||!(a[i]&cs&~gc));
    for(int k=1;k<=3;k++)bad[k]+=nu>=k;
    maxedges=max(maxedges,ec);maxnu=max(maxnu,nu);maxcover=max(maxcover,cover);
   }
  if(f)out<<",";out<<"{\"name\":\""<<array<string,6>{"row_star","column_star","matching","four_by_four","two_stars","complete"}[f]<<"\",\"edges\":"<<edges<<",\"max_residual_edges\":"<<maxedges<<",\"max_matching\":"<<maxnu<<",\"max_greedy_cover\":"<<maxcover<<",\"tails\":[";
  for(int k=1;k<=3;k++){long long bound=match[k]*C(m-k,R-k)*C(n-k,H-k);assert(bad[k]<=bound);if(k>1)out<<",";out<<"{\"k\":"<<k<<",\"bad_pairs\":"<<bad[k]<<",\"original_k_matchings\":"<<match[k]<<",\"union_bound_pairs\":"<<bound<<"}";}
  out<<"]}";if(f==0)assert(maxedges==3&&maxnu==1);if(f==5)assert(bad[3]==pairs);
 }
 out<<"],\"all_checks_passed\":true}\n";
}
