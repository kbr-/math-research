#include <algorithm>
#include <cassert>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
using namespace std;
int p;
int md(int a){a%=p;return a<0?a+p:a;}
int inv(int a){for(int b=1;b<p;b++)if(a*b%p==1)return b;assert(false);return 0;}
struct Space{
 int d;vector<vector<int>>b;
 Space(int D):d(D),b(D+1){}
 bool add(vector<int>v){for(int k=d;k>=0;k--){v[k]=md(v[k]);if(!v[k])continue;if(!b[k].empty()){int a=v[k];for(int j=0;j<=k;j++)v[j]=md(v[j]-a*b[k][j]);}
 else{int a=inv(v[k]);for(int&x:v)x=md(x*a);b[k]=v;return true;}}return false;}
 int rank(){int r=0;for(auto&v:b)r+=!v.empty();return r;}
 bool unit(){vector<int>v(d+1);v[0]=1;Space c=*this;return !c.add(v);}
};
int main(int argc,char**argv){
 if(argc!=3||string(argv[1])!="--out")return 2;
 cerr<<"Budget: fields 3,5,7; all 15 parameter fibers plus 3 benign controls; degree <=5, at most six monomials.\n";
 ofstream o(argv[2]);o<<"{\"max_degree\":5,\"fibers\":[";bool first=true;
 for(int prime:{3,5,7}){p=prime;for(int lam=-1;lam<p;lam++){
  if(!first)o<<",";first=false;o<<"{\"p\":"<<p<<",\"parameter\":"<<lam<<",\"benign_control\":"<<(lam<0?"true":"false")<<",\"degrees\":[";
  for(int D=0;D<=5;D++){
   Space ns(D);if(D>=2)for(int t=0;t<=D-2;t++){
    vector<int>a(D+1),b(D+1);a[t+1]=p-1;a[t+2]=1;
    b[t]=lam<0?0:p-1;b[t+1]=lam<0?0:md(lam-1);b[t+2]=1;ns.add(a);ns.add(b);
   }
   Space pc=ns;bool change=true;while(change){change=false;auto old=pc.b;for(int k=0;k<D;k++)if(!old[k].empty()){vector<int>v(D+1);for(int j=0;j<D;j++)v[j+1]=old[k][j];change|=pc.add(v);}}
   bool nsunit=ns.unit(),pcunit=pc.unit();int H=D+1-ns.rank();
   if(lam<0){assert(!nsunit&&!pcunit);assert(ns.rank()==pc.rank());}
   else if(lam==1){assert(!nsunit&&!pcunit);}
   else{assert(nsunit==(D>=(lam==0?2:3)));assert(pcunit==(D>=2));assert(H==(D==0?1:D==1?2:D==2?1:0));}
   if(D)o<<",";o<<"{\"D\":"<<D<<",\"NS_rank\":"<<ns.rank()<<",\"PC_rank\":"<<pc.rank()<<",\"Hilbert\":"<<H<<",\"NS_unit\":"<<(nsunit?"true":"false")<<",\"PC_unit\":"<<(pcunit?"true":"false")<<"}";
  }
  o<<"]}";
 }
 }o<<"],\"all_checks_passed\":true}\n";
}
