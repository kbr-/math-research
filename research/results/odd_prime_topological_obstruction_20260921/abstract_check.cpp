#include <cassert>
#include <fstream>
#include <iostream>
#include <map>
#include <string>
#include <utility>
#include <vector>
using namespace std;
int p;
int md(int x){x%=p;return x<0?x+p:x;}
int inv(int x){for(int i=1;i<p;i++)if(x*i%p==1)return i;assert(false);return 0;}
struct Space{
 int n,r=0;vector<vector<int>>b;
 Space(int N):n(N),b(N){}
 bool add(vector<int>v){for(int k=n-1;k>=0;k--)if(v[k]){if(!b[k].empty()){int a=v[k];for(int j=0;j<=k;j++)v[j]=md(v[j]-a*b[k][j]);}else{int a=inv(v[k]);for(int&x:v)x=x*a%p;b[k]=v;r++;return true;}}return false;}
 bool contains(vector<int>v){Space c=*this;return !c.add(v);}
};
vector<pair<int,int>> mons(int cap,int d){vector<pair<int,int>>a;for(int i=0;i<p;i++)for(int j=0;j<cap;j++)if(i+j==d)a.push_back({i,j});return a;}
int main(int argc,char**argv){
 if(argc!=3||string(argv[1])!="--out")return 2;
 cerr<<"Budget: p=3,5; two truncated-polynomial modules; target degrees 0,1,2; <=15 target coordinates.\n";
 ofstream o(argv[2]);o<<"{\"cases\":[";bool first=true;
 for(int prime:{3,5}){p=prime;for(int thin=0;thin<2;thin++)for(int d=0;d<=2;d++){
  int cap=thin?2:p,delta=p-1;auto src=mons(cap,d+delta),tgt=mons(cap,d),low=mons(cap,d-1);
  map<pair<int,int>,int>ti,li;for(int i=0;i<(int)tgt.size();i++)ti[tgt[i]]=i;for(int i=0;i<(int)low.size();i++)li[low[i]]=i;
  int nt=tgt.size(),nl=low.size(),out=p*nt;
  // D1 lowers the first exponent. D2 lowers second in free control, first+second in thin control.
  auto step=[&](map<pair<int,int>,int>v,int op){map<pair<int,int>,int>w;for(auto [ab,c]:v){auto[a,b]=ab;if((op==0||thin)&&a)w[{a-1,b}]=md(w[{a-1,b}]+c);if(op==1&&b)w[{a,b-1}]=md(w[{a,b-1}]+c);}return w;};
  auto closure=[&](vector<int>v){vector<int>w((p+1)*nl);for(int j=0;j<p;j++)for(int k=0;k<nt;k++)if(v[j*nt+k])for(int op=0;op<2;op++){
   auto z=step({{tgt[k],v[j*nt+k]}},op);for(auto[ab,c]:z)if(c)w[(j+op)*nl+li.at(ab)]=md(w[(j+op)*nl+li.at(ab)]+c);
  }return w;};
  Space image(out),cl((p+1)*nl);vector<vector<int>>cols;
  for(auto ab:src){vector<int>col(out);for(int j=0;j<p;j++){
    map<pair<int,int>,int>v{{ab,1}};for(int k=0;k<delta-j;k++)v=step(v,0);for(int k=0;k<j;k++)v=step(v,1);
    int bin=(j%2)?p-1:1; // binomial(p-1,j)=(-1)^j mod p.
    for(auto[cd,c]:v)if(c)col[j*nt+ti.at(cd)]=bin*c%p;
   }
   auto closed=closure(col);for(int z:closed)assert(z==0);image.add(col);cols.push_back(col);
  }
  for(int j=0;j<out;j++){vector<int>e(out);e[j]=1;cl.add(closure(e));}
  int compatible=out-cl.r;if(!thin)assert(image.r==compatible);
  int witness=-1;if(thin&&d==0){assert(image.r==2&&compatible==p);for(int j=0;j<out;j++){vector<int>e(out);e[j]=1;if(!image.contains(e)){witness=j;break;}}assert(witness>=0);}
  if(!first)o<<",";first=false;o<<"{\"p\":"<<p<<",\"model\":\""<<(thin?"short_bad_pencil":"free_two_generator")<<"\",\"d\":"<<d<<",\"source_dimension\":"<<src.size()<<",\"target_dimension\":"<<out<<",\"compatible_dimension\":"<<compatible<<",\"image_rank\":"<<image.r<<",\"closed_unit_target_outside_image\":"<<witness<<"}";
 }}
 o<<"],\"all_checks_passed\":true}\n";
}
