// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact full-image check: three rows, old degree 2 -> 3, one bit predicate per row.
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
 constexpr int n=16,np=n*(n-1),nt=n*(n-1)*(n-2);
 std::cout<<"Fixed N=16, three rows, d=2, one low-bit predicate per row; B=6 and affine support >=8. Largest matrix 1440 x 3360 bytes plus copies; three exact ranks per prime 2,3,5.\n";
 auto pair_index=[](int a,int b){return a*(n-1)+b-(b>a);};
 std::vector<std::array<int,3>> triples;
 for(int a=0;a<n;++a)for(int b=0;b<n;++b)for(int c=0;c<n;++c)if(a!=b&&a!=c&&b!=c)triples.push_back({a,b,c});
 need(int(triples.size())==nt,"triple enumeration mismatch");
 Mat marginal(3*np,Row(nt,0)),image(3*np,Row(nt,0));
 for(int q=0;q<nt;++q)for(int i=0;i<3;++i){
  std::vector<int> other;for(int j=0;j<3;++j)if(i!=j)other.push_back(j);
  int row=i*np+pair_index(triples[q][other[0]],triples[q][other[1]]);
  marginal[row][q]=1;image[row][q]=uint8_t(triples[q][i]&1);
 }
 std::ofstream out(argv[2]);need(bool(out),"cannot open output");
 out<<"{\"labels\":16,\"rows\":3,\"old_degree\":2,\"new_degree\":3,\"predicate\":\"label & 1 on each row\",\"deletion_budget\":6,\"minimum_affine_support\":8,\"source_columns\":3360,\"target_columns\":720,\"cases\":[";
 bool comma=false;
 for(int p:{2,3,5}){
  Mat compatibility;
  for(int i=0;i<3;++i)for(int pos=0;pos<2;++pos)for(int label=0;label<n;++label){
   Row row(3*np,0);for(int a=0;a<n;++a)for(int b=0;b<n;++b)if(a!=b&&(pos==0?a:b)==label)row[i*np+pair_index(a,b)]=1;
   compatibility.push_back(row);
  }
  for(int i=0;i<3;++i)for(int j=i+1;j<3;++j){
   int rest=3-i-j;
   for(int r=0;r<n;++r){
    Row row(3*np,0);
    for(int which=0;which<2;++which){
     int target=which==0?i:j,conditioning=which==0?j:i;
     std::vector<int> other;for(int k=0;k<3;++k)if(k!=target)other.push_back(k);
     for(int l=0;l<n;++l)if(l!=r){std::array<int,3> labels{};labels[rest]=r;labels[conditioning]=l;
      int col=target*np+pair_index(labels[other[0]],labels[other[1]]);
      row[col]=uint8_t(which==0?(l&1):(p-(l&1))%p);
     }
    }
    compatibility.push_back(row);
   }
  }
  Mat stack=marginal;stack.insert(stack.end(),image.begin(),image.end());
  auto pm=pivots(marginal,p),ps=pivots(stack,p),pc=pivots(compatibility,p);
  int actual=int(ps.size()-pm.size()),desired=3*np-int(pc.size());
  need(actual==desired,"compatible targets fail full-image surjectivity");need(actual>0,"vacuous image");
  if(comma)out<<',';
  comma=true;out<<"{\"prime\":"<<p<<",\"marginal_rank\":"<<pm.size()<<",\"stack_rank\":"<<ps.size()<<",\"compatibility_rank\":"<<pc.size()<<",\"image_dimension\":"<<actual<<",\"compatible_dimension\":"<<desired<<",\"marginal_pivots\":";
  ints(out,pm);out<<",\"stack_pivots\":";ints(out,ps);out<<",\"compatibility_pivots\":";ints(out,pc);out<<",\"passed\":true}";
  std::cout<<"F"<<p<<": source marginals rank "<<pm.size()<<", joint rank "<<ps.size()<<", compatible target dimension "<<desired<<", image dimension "<<actual<<"; passed\n";
 }
 out<<"]}\n";need(bool(out),"output write failed");
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
