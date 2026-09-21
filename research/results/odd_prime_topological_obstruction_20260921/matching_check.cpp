#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <string>
#include <vector>
using namespace std;
using V=vector<uint8_t>;
struct Space{
 int n,r=0;vector<V>b;
 Space(int N):n(N),b(N){}
 void reduce(V&v)const{for(int i=n-1;i>=0;i--)if(v[i]&&!b[i].empty()){
  if(v[i]==1){for(int j=0;j<=i;j++){int a=int(v[j])-int(b[i][j]);v[j]=a<0?a+3:a;}}
  else{for(int j=0;j<=i;j++){int a=v[j]+b[i][j];v[j]=a>=3?a-3:a;}}
 }}
 bool add(V v){reduce(v);for(int i=n-1;i>=0;i--)if(v[i]){if(v[i]==2)for(auto&x:v)x=x?3-x:0;b[i]=move(v);r++;return true;}return false;}
};
int main(int argc,char**argv){
 if(argc!=3||string(argv[1])!="--out")return 2;
 constexpr int N=9; // Labels are F3^2. One representative nonzero F3-linear predicate.
 vector<array<int,3>> trip;map<array<int,3>,int>idx;
 for(int a=0;a<N;a++)for(int b=0;b<N;b++)for(int c=0;c<N;c++)if(a!=b&&a!=c&&b!=c){idx[{a,b,c}]=trip.size();trip.push_back({a,b,c});}
 Space rel(trip.size());
 for(int omitted=0;omitted<3;omitted++)for(int a=0;a<N;a++)for(int b=0;b<N;b++)if(a!=b){
  V v(trip.size());for(int c=0;c<N;c++)if(c!=a&&c!=b){array<int,3>q{};int t=0;for(int k=0;k<3;k++)q[k]=k==omitted?c:(t++==0?a:b);v[idx[q]]=1;}rel.add(v);
 }
 vector<int>free;for(int j=0;j<(int)trip.size();j++)if(rel.b[j].empty())free.push_back(j);
 assert(free.size()==314);
 cerr<<"Budget: N=9, m=4,5, 504 coordinates per row triple, at most 3140 output coordinates and 720 input columns per rank; F3 exact.\n";
 ofstream o(argv[2]);o<<"{\"prime\":3,\"labels\":9,\"row_triple_relation_rank\":"<<rel.r<<",\"row_triple_quotient_dimension\":"<<free.size()<<",\"cases\":[";
 for(int m:{4,5}){
  vector<array<int,3>>rows;map<array<int,3>,int>ridx;
  for(int a=0;a<m;a++)for(int b=a+1;b<m;b++)for(int c=b+1;c<m;c++){ridx[{a,b,c}]=rows.size();rows.push_back({a,b,c});}
  int outdim=rows.size()*free.size(),coldim=m*(m-1)/2*N*(N-1);
  if(outdim>3200||coldim>720)return 3;
  Space im(outdim);
  for(int a=0;a<m;a++)for(int b=a+1;b<m;b++)for(int u=0;u<N;u++)for(int v=0;v<N;v++)if(u!=v){
   V col(outdim);
   for(int c=0;c<m;c++)if(c!=a&&c!=b){
    array<int,3>rs={a,b,c};sort(rs.begin(),rs.end());V local(trip.size());
    for(int w=0;w<N;w++)if(w!=u&&w!=v){array<int,3>q{};for(int j=0;j<3;j++)q[j]=rs[j]==a?u:rs[j]==b?v:w;local[idx[q]]=w%3;}
    rel.reduce(local);int off=ridx[rs]*free.size();for(int k=0;k<(int)free.size();k++)col[off+k]=local[free[k]];
   }
   im.add(move(col));
  }
  int dimG2=m*(m-1)/2*55;
  // One row-pair quotient: 72 injection monomials, 18 marginal relations of rank17.
  vector<pair<int,int>>pairs;map<pair<int,int>,int>pi;
  for(int a=0;a<N;a++)for(int b=0;b<N;b++)if(a!=b){pi[{a,b}]=pairs.size();pairs.push_back({a,b});}
  Space r2(pairs.size());for(int row=0;row<2;row++)for(int a=0;a<N;a++){V z(pairs.size());for(int b=0;b<N;b++)if(a!=b)z[pi[row==0?make_pair(a,b):make_pair(b,a)]]=1;r2.add(z);}
  assert(r2.r==17);
  Space joint(pairs.size());for(auto&v:r2.b)if(!v.empty())joint.add(v);
  for(int h=0;h<3;h++){V z(pairs.size());for(int j=0;j<(int)pairs.size();j++){
   auto[a,b]=pairs[j];int x=a%3,y=a/3,X=b%3,Y=b/3;
   z[j]=h==0?2*x*X%3:h==1?(x*Y+y*X)%3:2*y*Y%3;
  }joint.add(z);}
  int polar=joint.r-r2.r;assert(polar==3);
  V square(pairs.size());for(int j=0;j<(int)pairs.size();j++)square[j]=2*(pairs[j].first%3)*(pairs[j].second%3)%3;
  r2.reduce(square);bool nz=false;for(int a:square)nz|=a!=0;assert(nz);
  if(m!=4)o<<",";o<<"{\"rows\":"<<m<<",\"G2_dimension\":"<<dimG2<<",\"G3_dimension\":"<<outdim<<",\"linear_G2_to_G3_rank\":"<<im.r<<",\"square_G0_to_G2_rank\":1,\"amplitude_defect_at_K2\":"<<dimG2-1-im.r<<",\"joint_polarized_target_rank_at_K0\":"<<polar<<"}";
  cerr<<"m="<<m<<" rank="<<im.r<<" dimG2="<<dimG2<<" defect="<<dimG2-1-im.r<<"\n";
 }
 o<<"],\"note\":\"F3-pencil directions are equivalent by GL2(F3) label permutations; no algebraic-closure exactness inferred.\"}\n";
}
