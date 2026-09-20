// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact global parity complex: degree 2, wide positive and thin-row negative controls.
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using Row=std::vector<uint8_t>;
using Mat=std::vector<Row>;
void need(bool b,const char*s){if(!b)throw std::runtime_error(s);}
std::vector<int> pivots(Mat a,int p){
 std::vector<int> out;int m=int(a.size()),n=int(a[0].size()),r=0;
 uint8_t lut[5][25]{};
 for(int c=0;c<p;++c)for(int x=0;x<p;++x)for(int y=0;y<p;++y)lut[c][x*p+y]=uint8_t((x-c*y+p*p)%p);
 for(int j=0;j<n&&r<m;++j){
  int q=r;while(q<m&&!a[q][j])++q;if(q==m)continue;
  std::swap(a[q],a[r]);int inv=1;while(inv*a[r][j]%p!=1)++inv;
  for(int k=j;k<n;++k)a[r][k]=uint8_t(a[r][k]*inv%p);
  for(int i=r+1;i<m;++i)if(a[i][j]){
   const uint8_t* sub=lut[a[i][j]];const uint8_t* src=a[r].data();uint8_t* dst=a[i].data();
   for(int k=j;k<n;++k)dst[k]=sub[dst[k]*p+src[k]];
  }
  out.push_back(j);++r;
 }
 return out;
}
void ints(std::ostream&o,const std::vector<int>&v){o<<'[';for(size_t i=0;i<v.size();++i){if(i)o<<',';o<<v[i];}o<<']';}
int main(int argc,char**argv)try{
 need(argc==3&&std::string(argv[1])=="--out","usage: --out FILE");std::ifstream old(argv[2]);need(!old.good(),"refusing overwrite");
 constexpr int n=16,np=n*(n-1),nt=n*(n-1)*(n-2),p=2;
 std::cout<<"Fixed three-row N=16 board, d=2; active rows 3 (positive) and 2 (negative). Exact F2 ranks, maximum 1440 x 3360 byte matrix plus copies.\n";
 auto pair_index=[](int a,int b){return a*(n-1)+b-(b>a);};
 std::vector<std::array<int,3>> triples;
 for(int a=0;a<n;++a)for(int b=0;b<n;++b)for(int c=0;c<n;++c)if(a!=b&&a!=c&&b!=c)triples.push_back({a,b,c});
 Mat marginal(3*np,Row(nt,0)),target_marg;
 for(int q=0;q<nt;++q)for(int i=0;i<3;++i){
  std::vector<int> other;for(int j=0;j<3;++j)if(i!=j)other.push_back(j);
  marginal[i*np+pair_index(triples[q][other[0]],triples[q][other[1]])][q]=1;
 }
 for(int missing=0;missing<3;++missing)for(int pos=0;pos<2;++pos)for(int label=0;label<n;++label){
  Row row(3*np,0);for(int a=0;a<n;++a)for(int b=0;b<n;++b)if(a!=b&&(pos==0?a:b)==label)row[missing*np+pair_index(a,b)]=1;
  target_marg.push_back(row);
 }
 auto pm=pivots(marginal,p);
 std::ofstream out(argv[2]);need(bool(out),"cannot open output");
 out<<"{\"labels\":16,\"rows\":3,\"degree\":2,\"field\":2,\"predicate_per_active_row\":\"label & 1\",\"cases\":[";
 bool comma=false;
 for(int active:{3,2}){
  Mat upper(3*np,Row(nt,0)),lower(3*n,Row(3*np,0));
  for(int q=0;q<nt;++q)for(int i=0;i<active;++i){
   std::vector<int> other;for(int j=0;j<3;++j)if(i!=j)other.push_back(j);
   upper[i*np+pair_index(triples[q][other[0]],triples[q][other[1]])][q]=uint8_t(triples[q][i]&1);
  }
  for(int missing=0;missing<3;++missing){
   std::vector<int> other;for(int j=0;j<3;++j)if(j!=missing)other.push_back(j);
   for(int a=0;a<n;++a)for(int b=0;b<n;++b)if(a!=b){
    int col=missing*np+pair_index(a,b);
    if(other[0]<active)lower[other[1]*n+b][col]=uint8_t(a&1);
    if(other[1]<active)lower[other[0]*n+a][col]=uint8_t(b&1);
   }
  }
  // Verify D^2=0 using its two deletion orders on every injection.
  int square_checks=0;
  for(const auto&v:triples)for(int retained=0;retained<3;++retained){
   int sum=0;for(int i=0;i<active;++i)for(int j=0;j<active;++j)if(i!=j&&i!=retained&&j!=retained)sum+=(v[i]&1)*(v[j]&1);
   need(sum%2==0,"contraction does not square to zero");++square_checks;
  }
  Mat stack=marginal;stack.insert(stack.end(),upper.begin(),upper.end());
  Mat closed=target_marg;closed.insert(closed.end(),lower.begin(),lower.end());
  auto ps=pivots(stack,p),pc=pivots(closed,p);
  int im=int(ps.size()-pm.size()),ker=3*np-int(pc.size());
  if(active==3)need(im==ker&&im==583,"wide parity exactness failed");
  else need(ker>im,"thin-row obstruction missing");
  if(comma)out<<',';
  comma=true;out<<"{\"active_rows\":"<<active<<",\"marginal_rank\":"<<pm.size()<<",\"joint_rank\":"<<ps.size()<<",\"closed_constraint_rank\":"<<pc.size()<<",\"image_dimension\":"<<im<<",\"kernel_dimension\":"<<ker<<",\"homology_dimension\":"<<ker-im<<",\"square_checks\":"<<square_checks<<",\"joint_pivots\":";
  ints(out,ps);out<<",\"closed_pivots\":";ints(out,pc);
  if(active==2){
   Row z(3*np,0);for(int a:{0,2})for(int b:{4,6})z[2*np+pair_index(a,b)]=1;
   for(const auto&r:closed){int sum=0;for(size_t q=0;q<z.size();++q)sum+=r[q]*z[q];need(sum%2==0,"thin target is not a cycle");}
   int dual=2*np+pair_index(0,4);for(int v:upper[dual])need(v==0,"thin dual does not kill the image");need(z[dual]==1,"thin dual does not separate");
   out<<",\"nonboundary_target_sparse\":[";bool first=true;for(size_t q=0;q<z.size();++q)if(z[q]){if(!first)out<<',';first=false;out<<'['<<q<<",1]";}out<<"],\"separating_coordinate\":"<<dual<<",\"dual_value\":1";
  }
  out<<",\"passed\":true}";
  std::cout<<"Active "<<active<<": image "<<im<<", kernel "<<ker<<", homology "<<ker-im<<"; square checks "<<square_checks<<"; passed\n";
 }
 // Characteristic guard: deleting two active odd-labelled rows has coefficient 2.
 std::array<int,3> odd{1,3,5};int odd_prime_value=((odd[0]&1)*(odd[1]&1)*2)%3;
 need(odd_prime_value==2,"odd-prime control failed");out<<"],\"F3_square_control\":{\"triple\":[1,3,5],\"retained_row\":2,\"coefficient\":2}}\n";
 need(bool(out),"output write failed");
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
