// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Joint global parity images: collective distance versus individually wide forms.
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
 constexpr int n=16,p=2,ns=3*n*(n-1),target=2*3*n;
 std::cout<<"Fixed F2 board: three rows, N=16, d=1, two parity operators. At most 192 x 720 byte matrices. Compare full compatible target space with joint image; no large search.\n";
 struct Cell{int i,j,a,b;};std::vector<Cell> cells;
 for(int i=0;i<3;++i)for(int j=i+1;j<3;++j)for(int a=0;a<n;++a)for(int b=0;b<n;++b)if(a!=b)cells.push_back({i,j,a,b});
 need(int(cells.size())==ns,"source enumeration mismatch");
 Mat marginal(6*n,Row(ns,0));
 for(int q=0;q<ns;++q){auto c=cells[q];int pair=c.i==0?(c.j==1?0:1):2;marginal[(2*pair)*n+c.a][q]=1;marginal[(2*pair+1)*n+c.b][q]=1;}
 auto pm=pivots(marginal,p);
 std::ofstream out(argv[2]);need(bool(out),"cannot open output");
 out<<"{\"field\":2,\"labels\":16,\"rows\":3,\"degree\":1,\"family_dimension\":2,\"cases\":[";bool comma=false;
 for(bool positive:{true,false}){
  std::array<std::array<int,3>,2> masks{{{1,1,1},positive?std::array<int,3>{2,2,2}:std::array<int,3>{3,1,1}}};
  auto f=[&](int t,int i,int label){return __builtin_parity(unsigned(masks[t][i]&label));};
  Mat image(target,Row(ns,0));for(int q=0;q<ns;++q){auto c=cells[q];for(int t=0;t<2;++t){image[t*3*n+c.j*n+c.b][q]=uint8_t(f(t,c.i,c.a));image[t*3*n+c.i*n+c.a][q]=uint8_t(f(t,c.j,c.b));}}
  Mat constraints;
  for(int t=0;t<2;++t)for(int i=0;i<3;++i){Row r(target,0);for(int j=0;j<n;++j)r[t*3*n+i*n+j]=1;constraints.push_back(r);}
  for(int t=0;t<2;++t){Row r(target,0);for(int i=0;i<3;++i)for(int j=0;j<n;++j)r[t*3*n+i*n+j]=uint8_t(f(t,i,j));constraints.push_back(r);}
  Row cross(target,0);for(int t=0;t<2;++t)for(int i=0;i<3;++i)for(int j=0;j<n;++j)cross[t*3*n+i*n+j]=uint8_t(f(1-t,i,j));constraints.push_back(cross);
  Mat stack=marginal;stack.insert(stack.end(),image.begin(),image.end());auto ps=pivots(stack,p),pc=pivots(constraints,p);
  int actual=int(ps.size()-pm.size()),compatible=target-int(pc.size()),delta=4;std::vector<int> widths;
  for(int c=1;c<4;++c){int width=0;for(int i=0;i<3;++i){int v=0;for(int t=0;t<2;++t)if(c&(1<<t))v^=masks[t][i];width+=v!=0;}widths.push_back(width);if(width<delta)delta=width;}
  if(positive)need(delta==3&&actual==compatible&&compatible==87,"collective positive case failed");
  else need(delta==1&&actual<compatible,"cancellation control did not obstruct lifting");
  if(comma)out<<',';
  comma=true;out<<"{\"kind\":\""<<(positive?"collective_distance":"individual_width_only")<<"\",\"row_bit_masks\":[";
  for(int t=0;t<2;++t){if(t)out<<',';out<<'[';for(int i=0;i<3;++i){if(i)out<<',';out<<masks[t][i];}out<<']';}out<<"],\"nonzero_combination_widths\":";ints(out,widths);
  out<<",\"minimum_row_distance\":"<<delta<<",\"marginal_rank\":"<<pm.size()<<",\"joint_rank\":"<<ps.size()<<",\"target_constraint_rank\":"<<pc.size()<<",\"image_dimension\":"<<actual<<",\"compatible_dimension\":"<<compatible<<",\"joint_pivots\":";ints(out,ps);out<<",\"constraint_pivots\":";ints(out,pc);
  if(!positive){
   Row z(target,0);z[3*n]=z[3*n+4]=1;for(const auto&r:constraints){int sum=0;for(int j=0;j<target;++j)sum+=r[j]*z[j];need(sum%2==0,"negative target violates compatibility");}
   for(int q=0;q<ns;++q)need((image[0][q]+image[3*n][q])%2==0,"coordinate-sum dual does not annihilate joint image");
   need((z[0]+z[3*n])%2==1,"dual does not reject target");out<<",\"nonliftable_target_sparse\":[[48,1],[52,1]],\"dual_target_indices\":[0,48],\"dual_value\":1";
  }
  out<<",\"passed\":true}";
  std::cout<<(positive?"Collective":"Individual-only")<<": widths ";for(int w:widths)std::cout<<w<<' ';std::cout<<" image "<<actual<<" compatible "<<compatible<<"; passed\n";
 }
 out<<"]}\n";need(bool(out),"output write failed");
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
