// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Hybrid image: local row predicates plus a collectively wide quotient parity.
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
 constexpr int n=16,p=2,ops=4,ns=3*n*(n-1),target=ops*3*n;
 std::cout<<"Fixed F2 board, three rows, N=16, d=1: three local low-bit maps and one global second-bit map. Maximum 288 x 720 byte matrix.\n";
 std::array<std::array<int,3>,ops> masks{{{1,0,0},{0,1,0},{0,0,1},{2,2,2}}};
 auto f=[&](int t,int i,int label){return __builtin_parity(unsigned(masks[t][i]&label));};
 struct Cell{int i,j,a,b;};std::vector<Cell> cells;
 for(int i=0;i<3;++i)for(int j=i+1;j<3;++j)for(int a=0;a<n;++a)for(int b=0;b<n;++b)if(a!=b)cells.push_back({i,j,a,b});
 Mat marginal(6*n,Row(ns,0)),image(target,Row(ns,0));
 for(int q=0;q<ns;++q){auto c=cells[q];int pair=c.i==0?(c.j==1?0:1):2;marginal[2*pair*n+c.a][q]=1;marginal[(2*pair+1)*n+c.b][q]=1;
  for(int t=0;t<ops;++t){image[t*3*n+c.j*n+c.b][q]=uint8_t(f(t,c.i,c.a));image[t*3*n+c.i*n+c.a][q]=uint8_t(f(t,c.j,c.b));}
 }
 Mat weak,mixed;
 for(int t=0;t<ops;++t)for(int i=0;i<3;++i){Row r(target,0);for(int j=0;j<n;++j)r[t*3*n+i*n+j]=1;weak.push_back(r);}
 for(int t=0;t<3;++t)for(int j=0;j<n;++j){Row r(target,0);r[t*3*n+t*n+j]=1;weak.push_back(r);}
 for(int t=0;t<ops;++t){Row r(target,0);for(int i=0;i<3;++i)for(int j=0;j<n;++j)r[t*3*n+i*n+j]=uint8_t(f(t,i,j));weak.push_back(r);}
 for(int t=0;t<ops;++t)for(int u=t+1;u<ops;++u){Row r(target,0);for(int i=0;i<3;++i)for(int j=0;j<n;++j){r[t*3*n+i*n+j]=uint8_t(f(u,i,j));r[u*3*n+i*n+j]=uint8_t(f(t,i,j));}
  if(u==3)mixed.push_back(r);else weak.push_back(r);
 }
 Mat closed=weak;closed.insert(closed.end(),mixed.begin(),mixed.end());Mat stack=marginal;stack.insert(stack.end(),image.begin(),image.end());
 auto pm=pivots(marginal,p),ps=pivots(stack,p),pw=pivots(weak,p),pc=pivots(closed,p);
 int actual=int(ps.size()-pm.size()),compatible=target-int(pc.size()),weakdim=target-int(pw.size());
 need(actual==compatible&&actual>0,"hybrid joint lifting failed");need(weakdim>compatible,"mixed equations are vacuous");
 Row bad(target,0);bad[3*3*n]=bad[3*3*n+1]=1;
 auto dot=[&](const Row&r){int sum=0;for(int j=0;j<target;++j)sum+=r[j]*bad[j];return sum%2;};
 for(const auto&r:weak)need(dot(r)==0,"control fails even the weakened conditions");
 int failures=0;for(const auto&r:mixed)failures+=dot(r);need(failures==1,"control does not isolate a mixed failure");
 std::ofstream out(argv[2]);need(bool(out),"cannot open output");
 out<<"{\"field\":2,\"labels\":16,\"rows\":3,\"degree\":1,\"local_dimensions\":[1,1,1],\"wide_dimension\":1,\"relative_row_distance\":3,\"row_bit_masks\":[[1,0,0],[0,1,0],[0,0,1],[2,2,2]],\"marginal_rank\":"<<pm.size()<<",\"joint_rank\":"<<ps.size()<<",\"image_dimension\":"<<actual<<",\"compatible_dimension\":"<<compatible<<",\"without_mixed_equations_dimension\":"<<weakdim<<",\"joint_pivots\":";
 ints(out,ps);out<<",\"compatibility_pivots\":";ints(out,pc);out<<",\"weakened_pivots\":";ints(out,pw);
 out<<",\"bad_target_sparse\":[[144,1],[145,1]],\"mixed_violations\":"<<failures<<",\"passed\":true}\n";
 need(bool(out),"output write failed");std::cout<<"Image "<<actual<<", compatible "<<compatible<<", omitting mixed constraints "<<weakdim<<"; explicit control violates "<<failures<<" mixed equation; passed\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
