#include <algorithm>
#include <cassert>
#include <fstream>
#include <iostream>
#include <map>
#include <string>
#include <vector>
using namespace std;using V=vector<int>;
int md(int x){x%=3;return x<0?x+3:x;}
struct Space{
 int n,r=0;vector<V>b;Space(int N):n(N),b(N){}
 bool add(V v){for(int k=n-1;k>=0;k--)if(v[k]){
 if(!b[k].empty()){int a=v[k];for(int j=0;j<=k;j++)v[j]=md(v[j]-a*b[k][j]);}
 else{if(v[k]==2)for(int&x:v)x=md(2*x);b[k]=v;r++;return true;}}return false;}
 bool contains(V v){Space c=*this;return !c.add(v);}
};
int main(int argc,char**argv){
 if(argc!=3||string(argv[1])!="--out")return 2;
 constexpr int m=3,N=9,v=m*N;
 vector<pair<int,int>>mon{{-1,-1}};for(int a=0;a<v;a++)mon.push_back({a,-1});
 map<pair<int,int>,int>pairs;
 for(int a=0;a<v;a++)for(int b=a+1;b<v;b++)if(a/N!=b/N&&a%N!=b%N){pairs[{a,b}]=mon.size();mon.push_back({a,b});}
 int n=mon.size();assert(n==244);
 auto mult=[&](const V&f,int x){V g(n);g[1+x]=f[0];for(int a=0;a<v;a++)if(f[1+a]){
 int idx=-1;if(a==x)idx=1+a;else if(a/N!=x/N&&a%N!=x%N)idx=pairs.at(minmax(a,x));
 if(idx>=0)g[idx]=md(g[idx]+f[1+a]);}return g;};
 vector<V>rows;for(int i=0;i<m;i++){V f(n);f[0]=2;for(int j=0;j<N;j++)f[1+i*N+j]=1;rows.push_back(f);}
 cerr<<"Budget: one satisfiable 3-by-9 matching board, F3, four conditions, 244 matching normal-form monomials through degree two.\n";
 ofstream o(argv[2]);o<<"{\"prime\":3,\"rows\":3,\"labels\":9,\"degree\":2,\"normal_form_dimension\":244,\"cases\":[";
 for(int alpha=0;alpha<4;alpha++){
 vector<V>gen=rows;V q(n);q[0]=md(-(alpha<3?alpha:2));if(alpha<3)for(int a=0;a<v;a++)q[1+a]=(a%N)%3;else q[1]=1;gen.push_back(q);
 Space ns1(n),ns2(n);for(V f:gen){ns1.add(f);ns2.add(f);for(int x=0;x<v;x++)ns2.add(mult(f,x));}
 Space pc=ns2;bool change=true;while(change){change=false;auto old=pc.b;for(int k=0;k<=v;k++)if(!old[k].empty())for(int x=0;x<v;x++)change|=pc.add(mult(old[k],x));}
 Space extended=ns2;for(int k=0;k<=v;k++){V f(n);f[k]=1;extended.add(f);}int low=ns2.r+(v+1)-extended.r;
 V one(n);one[0]=1;bool unit=ns2.contains(one);
 if(alpha<3){assert(low==ns1.r&&pc.r==ns2.r&&!unit);}else assert(unit&&pc.contains(one));
 if(alpha)o<<",";o<<"{\"condition\":\""<<(alpha<3?"wide_L":"single_cell")<<"\",\"value\":"<<(alpha<3?alpha:2)<<",\"NS1_rank\":"<<ns1.r<<",\"NS2_rank\":"<<ns2.r<<",\"PC2_rank\":"<<pc.r<<",\"NS2_intersection_degree1_dimension\":"<<low<<",\"NS2_contains_unit\":"<<(unit?"true":"false")<<"}";
 }
 o<<"],\"all_checks_passed\":true}\n";
}
