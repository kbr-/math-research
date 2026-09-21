#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <string>
#include <vector>
using namespace std;using V=vector<uint8_t>;
struct Space{
 int n,r=0;vector<V>b;Space(int N):n(N),b(N){}
 void reduce(V&v)const{for(int i=n-1;i>=0;i--)if(v[i]&&!b[i].empty()){
 if(v[i]==1){for(int j=0;j<=i;j++){int a=int(v[j])-int(b[i][j]);v[j]=a<0?a+3:a;}}
 else{for(int j=0;j<=i;j++){int a=v[j]+b[i][j];v[j]=a>=3?a-3:a;}}
 }}
 bool add(V v){reduce(v);for(int i=n-1;i>=0;i--)if(v[i]){if(v[i]==2)for(auto&x:v)x=x?3-x:0;b[i]=move(v);r++;return true;}return false;}
};
struct Quot{
 int n,s;vector<vector<int>>mons;map<vector<int>,int>idx;Space rel;vector<int>free;
 static vector<vector<int>>generate(int n,int s){vector<vector<int>>out;vector<int>a(s);auto rec=[&](auto&&self,int i)->void{if(i==s){out.push_back(a);return;}for(int j=0;j<n;j++){bool ok=true;for(int k=0;k<i;k++)ok&=a[k]!=j;if(ok){a[i]=j;self(self,i+1);}}};rec(rec,0);return out;}
 Quot(int N,int S):n(N),s(S),mons(generate(N,S)),rel(mons.size()){
 for(int j=0;j<(int)mons.size();j++)idx[mons[j]]=j;
 for(int omit=0;omit<s;omit++)for(auto a:generate(n,s-1)){
 V v(mons.size());for(int j=0;j<n;j++){bool ok=true;for(int k:a)ok&=j!=k;if(ok){vector<int>b(s);int t=0;for(int k=0;k<s;k++)b[k]=k==omit?j:a[t++];v[idx[b]]=1;}}rel.add(v);}
 for(int j=0;j<(int)mons.size();j++)if(rel.b[j].empty())free.push_back(j);
 }
 V nf(V v){rel.reduce(v);V out;for(int i:free)out.push_back(v[i]);return out;}
};
int main(int argc,char**argv){
 if(argc!=3||string(argv[1])!="--out")return 2;
 const int N=12;Quot q2(N,2),q3(N,3);assert(q2.free.size()==109&&q3.free.size()==959);
 cerr<<"Budget: F3, 12 labels, m=2,3,4; quotient blocks <=1320 columns, map <=3836 by 48; target moment degree one.\n";
 ofstream out(argv[2]);out<<"{\"prime\":3,\"labels\":12,\"predicate_value_multiplicity\":4,\"deletion_robustness\":7,\"row_pair_quotient_dimension\":109,\"row_triple_quotient_dimension\":959,\"cases\":[";
 for(int m=2;m<=4;m++){
 vector<array<int,2>>rp;vector<array<int,3>>rt;map<array<int,2>,int>ip;map<array<int,3>,int>it;
 for(int a=0;a<m;a++)for(int b=a+1;b<m;b++){ip[{a,b}]=rp.size();rp.push_back({a,b});for(int c=b+1;c<m;c++){it[{a,b,c}]=rt.size();rt.push_back({a,b,c});}}
 int dim2=rp.size()*q2.free.size(),dim3=rt.size()*q3.free.size();assert(dim3<=3836);
 Space l(dim2),square(dim3);
 vector<V>lincols,sqcols;
 for(int i=0;i<m;i++)for(int h=0;h<N;h++){
  V c2(dim2),c3(dim3);
  for(int j=0;j<m;j++)if(j!=i){array<int,2>rr={i,j};sort(rr.begin(),rr.end());V local(q2.mons.size());
   for(int k=0;k<N;k++)if(k!=h){vector<int>a={rr[0]==i?h:k,rr[1]==i?h:k};local[q2.idx.at(a)]=k%3;}
   V v=q2.nf(local);int off=ip.at(rr)*v.size();copy(v.begin(),v.end(),c2.begin()+off);
  }
  for(int j=0;j<m;j++)for(int k=j+1;k<m;k++)if(j!=i&&k!=i){array<int,3>rr={i,j,k};sort(rr.begin(),rr.end());V local(q3.mons.size());
   for(int u=0;u<N;u++)for(int v=0;v<N;v++)if(u!=v&&u!=h&&v!=h){vector<int>a(3);for(int b=0;b<3;b++)a[b]=rr[b]==i?h:rr[b]==j?u:v;local[q3.idx.at(a)]=2*(u%3)*(v%3)%3;}
   V v=q3.nf(local);int off=it.at(rr)*v.size();copy(v.begin(),v.end(),c3.begin()+off);
  }
  l.add(c2);square.add(c3);lincols.push_back(move(c2));sqcols.push_back(move(c3));
 }
 // Both operators factor through each row's sum relation in G1.
 for(int i=0;i<m;i++){V s2(dim2),s3(dim3);for(int h=0;h<N;h++){for(int j=0;j<dim2;j++)s2[j]=(s2[j]+lincols[i*N+h][j])%3;for(int j=0;j<dim3;j++)s3[j]=(s3[j]+sqcols[i*N+h][j])%3;}for(int x:s2)assert(!x);for(int x:s3)assert(!x);}
 int dim1=m*(N-1),a1=dim1-1-square.r,a2=dim1-l.r;
 if(m>=3)assert(a2==0);if(m==4)assert(a1==0);if(m==2)assert(a2>0);if(m==3)assert(a1>0);
 if(m>2)out<<",";out<<"{\"active_rows\":"<<m<<",\"G1_dimension\":"<<dim1<<",\"G2_dimension\":"<<dim2<<",\"G3_dimension\":"<<dim3<<",\"linear_G1_to_G2_rank\":"<<l.r<<",\"square_G1_to_G3_rank\":"<<square.r<<",\"amplitude_1_defect_at_K1\":"<<a1<<",\"amplitude_2_defect_at_K1\":"<<a2<<"}";
 cerr<<"m="<<m<<" amplitude1 defect="<<a1<<" amplitude2 defect="<<a2<<"\n";
 }
 out<<"],\"all_checks_passed\":true}\n";
}
