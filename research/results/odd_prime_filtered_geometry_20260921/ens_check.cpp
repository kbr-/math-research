#include <array>
#include <cassert>
#include <fstream>
#include <iostream>
#include <map>
#include <string>
#include <vector>
using namespace std;
constexpr int P=3,D=3;
using V=array<int,10>;
int md(int x){x%=P;return x<0?x+P:x;}
struct Space{
 array<V,10>b{};array<bool,10>used{};
 bool add(V v){for(int k=9;k>=0;k--)if(v[k]){
 if(used[k]){int a=v[k];for(int j=0;j<=k;j++)v[j]=md(v[j]-a*b[k][j]);}
 else{int a=v[k]==1?1:2;for(int&x:v)x=x*a%P;b[k]=v;used[k]=true;return true;}}return false;}
 int rank(){int n=0;for(bool x:used)n+=x;return n;}
 bool contains(V v){Space c=*this;return !c.add(v);}
};
int main(int argc,char**argv){
 if(argc!=3||string(argv[1])!="--out")return 2;
 cerr<<"Budget: one F3 complete affine ENS block, ten monomials at degree three.\n";
 vector<pair<int,int>>mons;map<pair<int,int>,int>idx;
 for(int d=0;d<=D;d++)for(int a=0;a<=d;a++){idx[{a,d-a}]=mons.size();mons.push_back({a,d-a});}
 auto mono=[&](int a,int b,int c=1){V v{};v[idx[{a,b}]]=md(c);return v;};
 auto minus=[&](V a,V b){for(int i=0;i<10;i++)a[i]=md(a[i]-b[i]);return a;};
 auto mul=[&](V a,int v){V out{};for(int j=0;j<10;j++)if(a[j]){auto [x,r]=mons[j];if(v==0)x++;else r++;assert(x+r<=D);out[idx[{x,r}]]=a[j];}return out;};
 V boolean=minus(mono(2,0),mono(1,0)),field=minus(mono(0,3),mono(0,1)),comp=minus(mono(1,0),mono(2,1));
 Space ns;ns.add(boolean);ns.add(mul(boolean,0));ns.add(mul(boolean,1));ns.add(field);ns.add(comp);
 Space pc=ns;bool change=true;int rounds=0;
 while(change){change=false;Space old=pc;for(int k=0;k<10;k++)if(old.used[k]&&mons[k].first+mons[k].second<D)for(int v=0;v<2;v++)change|=pc.add(mul(old.b[k],v));rounds++;}
 V q=minus(mono(1,0),mono(1,1)),rq=mul(q,1);
 assert(ns.contains(q)&&!ns.contains(rq)&&pc.contains(rq));assert(!pc.contains(mono(0,0)));
 Space nsplus=ns,pcplus=pc;for(int a=0;a<=D;a++){nsplus.add(mono(a,0));pcplus.add(mono(a,0));}
 int oldns=ns.rank()+4-nsplus.rank(),oldpc=pc.rank()+4-pcplus.rank();assert(oldns==2&&oldpc==2);
 ofstream o(argv[2]);o<<"{\"prime\":3,\"degree\":3,\"monomials\":10,\"NS_rank\":"<<ns.rank()<<",\"PC_rank\":"<<pc.rank()<<",\"closure_rounds_including_final\":"<<rounds<<",\"old_NS_intersection_dimension\":"<<oldns<<",\"old_PC_intersection_dimension\":"<<oldpc<<",\"q_in_NS\":true,\"rq_in_NS\":false,\"rq_in_PC\":true,\"unit_in_PC\":false,\"all_checks_passed\":true}\n";
}
