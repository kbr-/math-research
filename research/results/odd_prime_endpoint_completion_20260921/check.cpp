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
 if(v[i]==1){for(int j=0;j<=i;j++){int x=int(v[j])-int(b[i][j]);v[j]=x<0?x+3:x;}}
 else{for(int j=0;j<=i;j++){int x=v[j]+b[i][j];v[j]=x>=3?x-3:x;}}
 }}
 bool add(V v){reduce(v);for(int i=n-1;i>=0;i--)if(v[i]){if(v[i]==2)for(auto&x:v)x=x?3-x:0;b[i]=move(v);r++;return true;}return false;}
};
int main(int argc,char**argv){
 if(argc!=3||string(argv[1])!="--out")return 2;
 constexpr int m=9,N=27;
 vector<array<int,2>>labels,rows;map<array<int,2>,int>li,ri;
 for(int a=0;a<N;a++)for(int b=0;b<N;b++)if(a!=b){li[{a,b}]=labels.size();labels.push_back({a,b});}
 Space rel(labels.size());
 for(int row=0;row<2;row++)for(int a=0;a<N;a++){V v(labels.size());for(int b=0;b<N;b++)if(a!=b)v[li[row==0?array<int,2>{a,b}:array<int,2>{b,a}]]=1;rel.add(v);}
 vector<int>free;for(int j=0;j<(int)labels.size();j++)if(rel.b[j].empty())free.push_back(j);assert(free.size()==649);
 for(int a=0;a<m;a++)for(int b=a+1;b<m;b++){ri[{a,b}]=rows.size();rows.push_back({a,b});}
 int outdim=rows.size()*free.size(),cols=2*m*N;assert(outdim<=23500&&cols<=500);
 cerr<<"Budget: F3, 9 rows, 27 labels; two maps with 23364 quotient coordinates and 486 raw columns; under 30 MB for echelon rows.\n";
 ofstream o(argv[2]);o<<"{\"prime\":3,\"rows\":9,\"labels\":27,\"G1_dimension\":234,\"G2_dimension\":"<<outdim<<",\"cases\":[";
 for(int thin=0;thin<2;thin++){
 Space im(outdim);V koszul(outdim);vector<V>rowsums(2*m,V(outdim));
 auto f=[&](int which,int row,int label){int a=label%3,b=(label/3)%3;return which==0?a:thin?(a+(row==0?b:0))%3:b;};
 for(int which=0;which<2;which++)for(int i=0;i<m;i++)for(int h=0;h<N;h++){
  V col(outdim);
  for(int j=0;j<m;j++)if(j!=i){array<int,2>rr={i,j};sort(rr.begin(),rr.end());V local(labels.size());
   for(int k=0;k<N;k++)if(k!=h){array<int,2>ab={rr[0]==i?h:k,rr[1]==i?h:k};local[li.at(ab)]=f(which,j,k);}
   rel.reduce(local);int off=ri.at(rr)*free.size();for(int k=0;k<(int)free.size();k++)col[off+k]=local[free[k]];
  }
  int weight=which==0?f(1,i,h):(3-f(0,i,h))%3;
  for(int j=0;j<outdim;j++){rowsums[which*m+i][j]=(rowsums[which*m+i][j]+col[j])%3;koszul[j]=(koszul[j]+weight*col[j])%3;}
  im.add(move(col));
 }
 for(auto&v:rowsums)for(int x:v)assert(!x);for(int x:koszul)assert(!x);
 int compatible=2*m*(N-1)-1;if(!thin)assert(im.r==compatible);else assert(im.r<compatible);
 if(thin)o<<",";o<<"{\"model\":\""<<(thin?"individually_wide_thin_difference":"collectively_wide")<<"\",\"joint_linear_image_rank\":"<<im.r<<",\"compatible_target_dimension\":"<<compatible<<",\"defect\":"<<compatible-im.r<<",\"collective_row_distance\":"<<(thin?1:m)<<"}";
 cerr<<(thin?"thin":"wide")<<" rank="<<im.r<<" compatible="<<compatible<<"\n";
 }
 o<<"],\"all_checks_passed\":true}\n";
}
