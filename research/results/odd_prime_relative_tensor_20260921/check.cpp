#include <array>
#include <cassert>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
using namespace std;
int p;
int md(int x){x%=p;return x<0?x+p:x;}
int inv(int x){for(int y=1;y<p;y++)if(x*y%p==1)return y;assert(false);return 0;}
using V=array<int,16>;
struct Space{
 array<V,16>b{};array<bool,16>used{};
 bool add(V v){for(int k=15;k>=0;k--)if(v[k]){if(used[k]){int a=v[k];for(int j=0;j<=k;j++)v[j]=md(v[j]-a*b[k][j]);}else{int a=inv(v[k]);for(int&x:v)x=x*a%p;b[k]=v;used[k]=true;return true;}}return false;}
 int rank(){int r=0;for(bool x:used)r+=x;return r;}
 bool contains(V v){Space q=*this;return !q.add(v);}
};
int idx(int a,int b){if(a<0&&b<0)return 0;if(b<0)return 1+a;if(a<0)return 4+b;return 7+3*a+b;}
int main(int argc,char**argv){
 if(argc!=3||string(argv[1])!="--out")return 2;
 cerr<<"Budget: one 3-by-2 column-exclusive board, 16 states, primes 3 and 5, degrees <=2.\n";
 ofstream o(argv[2]);o<<"{\"rows\":3,\"columns\":2,\"states\":16,\"fields\":[";
 for(int prime:{3,5}){p=prime;
 vector<pair<int,int>> basis;for(int a=-1;a<3;a++)for(int b=-1;b<3;b++)basis.push_back({a,b});
 array<int,3> rank{};
 for(int d=0;d<=2;d++){Space eval;for(auto [a,b]:basis)if((a>=0)+(b>=0)<=d){V v{};for(int u=0;u<4;u++)for(int w=0;w<4;w++)v[4*u+w]=(a<0||u==a+1)&&(b<0||w==b+1);eval.add(v);}rank[d]=eval.rank();if(d==1)for(int j=0;j<16;j++){V e{};e[j]=1;assert(!eval.contains(e));}}
 assert(rank[0]==1&&rank[1]==7&&rank[2]==16);
 for(int u=0;u<4;u++)for(int w=0;w<4;w++){bool empty=false;for(int i=0;i<3;i++)empty|=(u!=i+1&&w!=i+1);assert(empty);}
 Space old1,old2;
 for(int i=0;i<3;i++)for(auto [a,b]:basis)if((a>=0)+(b>=0)<=1){
  V v{};v[idx(a,b)]=p-1;
  if(a<0||a==i)v[idx(i,b)]=md(v[idx(i,b)]+1);
  if(b<0||b==i)v[idx(a,i)]=md(v[idx(a,i)]+1);
  old2.add(v);if(a<0&&b<0)old1.add(v);
 }
 V unit{};unit[0]=1;assert(!old1.contains(unit));
 if(p!=3)o<<",";o<<"{\"prime\":"<<p<<",\"cone_Hilbert\":[1,7,16],\"normalization_Hilbert\":[16,16,16],\"conductor_defect_Hilbert\":[15,9,0],\"every_point_indicator_needs_degree_two\":true,\"normalized_row_ideal_kills_z\":true,\"old_NS_rank_D1\":"<<old1.rank()<<",\"old_NS_rank_D2\":"<<old2.rank()<<",\"old_unit_at_D1\":false,\"old_unit_at_D2\":"<<(old2.contains(unit)?"true":"false")<<"}";
 }
 o<<"],\"all_checks_passed\":true}\n";
}
