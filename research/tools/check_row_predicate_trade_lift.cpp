// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact one-row bit-predicate lifts and literal-MP moment fan controls.
#include <array>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using Key=uint32_t;using Sparse=std::map<Key,int>;
constexpr int ROWS=4,COLS=16,D=2,BITS=4;
void need(bool b,const char*s){if(!b)throw std::runtime_error(s);}
int label(Key k,int row){return int((k>>(5*row))&31)-1;}
int degree(Key k){int d=0;for(int i=0;i<ROWS;++i)d+=label(k,i)>=0;return d;}
Key cell(int row,int col){return Key(col+1)<<(5*row);}
Key join(Key k,int row,int col){
 int old=label(k,row);if(old>=0)return old==col?k:UINT32_MAX;
 for(int i=0;i<ROWS;++i)if(label(k,i)==col)return UINT32_MAX;
 return k|cell(row,col);
}
struct Field{
 int p;int mod(int v)const{v%=p;return v<0?v+p:v;}
 int inverse(int x)const{for(int i=1;i<p;++i)if(mod(i*x)==1)return i;throw std::runtime_error("no inverse");}
 void add(Sparse&s,Key k,int v)const{int a=mod(s[k]+v);if(a)s[k]=a;else s.erase(k);}
 int at(const Sparse&s,Key k)const{auto it=s.find(k);return it==s.end()?0:it->second;}
 // Free variables are zero; pivot positions depend only on the evaluation matrix.
 bool solve(std::vector<std::vector<int>>a,std::vector<int>b,std::vector<int>&solution)const{
  int m=int(a.size()),n=int(a[0].size()),rank=0;std::vector<int>pivots;
  for(int i=0;i<m;++i)a[i].push_back(mod(b[i]));
  for(int j=0;j<n&&rank<m;++j){int pivot=rank;while(pivot<m&&mod(a[pivot][j])==0)++pivot;if(pivot==m)continue;std::swap(a[pivot],a[rank]);int inv=inverse(a[rank][j]);
   for(int k=j;k<=n;++k)a[rank][k]=mod(a[rank][k]*inv);
   for(int i=0;i<m;++i)if(i!=rank){int c=mod(a[i][j]);for(int k=j;k<=n;++k)a[i][k]=mod(a[i][k]-c*a[rank][k]);}
   pivots.push_back(j);++rank;
  }
  for(int i=rank;i<m;++i)if(mod(a[i][n]))return false;
  solution.assign(n,0);for(int i=0;i<rank;++i)solution[pivots[i]]=mod(a[i][n]);return true;
 }
};
std::vector<Key> matchings(){
 std::vector<Key>v;std::function<void(int,int,Key,uint32_t)>rec=[&](int row,int count,Key k,uint32_t used){
  if(row==ROWS){v.push_back(k);return;}rec(row+1,count,k,used);
  if(count<3)for(int j=0;j<COLS;++j)if(!(used>>j&1))rec(row+1,count+1,k|cell(row,j),used|(1u<<j));
 };rec(0,0,0,0);return v;
}
void sparse(std::ostream&o,const Sparse&s){o<<'[';bool c=false;for(auto [k,v]:s){if(c)o<<',';c=true;o<<'['<<k<<','<<v<<']';}o<<']';}
void vector_out(std::ostream&o,const std::vector<int>&v){o<<'[';for(size_t i=0;i<v.size();++i){if(i)o<<',';o<<v[i];}o<<']';}
int main(int argc,char**argv)try{
 need(argc==3&&std::string(argv[1])=="--out","usage: --out FILE");std::ifstream old(argv[2]);need(!old.good(),"refusing overwrite");
 auto all=matchings();std::cout<<"Fixed workload: four rows, sixteen labels, old degree two lifted to three; four row-bit predicates; primes 2,3,5. "<<all.size()<<" matching monomials through degree three.\n";
 std::ofstream out(argv[2]);need(bool(out),"cannot open output");out<<"{\"scope\":\"one-row trade corrections and a local MP fan; not a full compiled-source design\",\"rows\":4,\"labels\":16,\"old_degree\":2,\"encoding\":\"matching key uses five bits per row: zero absent, otherwise label+1; sparse omissions mean zero\",\"base_point\":[9,0,1,2],\"cases\":[";
 bool comma=false;
 for(int prime:{2,3,5}){
  Field f{prime};Sparse v;std::array<Sparse,BITS>z;std::array<int,ROWS>point={9,0,1,2};
  auto point_value=[&](Key k){for(int i=0;i<ROWS;++i)if(label(k,i)>=0&&label(k,i)!=point[i])return 0;return 1;};
  // [row_a,row_b,label_a0,label_a1,label_b0,label_b1]
  std::array<std::array<int,6>,3>trades={{{1,2,3,4,5,6},{1,3,1,7,10,12},{2,3,0,8,11,15}}};
  if(comma)out<<',';
  comma=true;out<<"{\"prime\":"<<prime<<",\"trade_lifts\":[";
  for(int q=0;q<3;++q){auto t=trades[q];Sparse eta;std::set<int>used={t[2],t[3],t[4],t[5]};
   for(int a=0;a<2;++a)for(int b=0;b<2;++b)f.add(eta,cell(t[0],t[2+a])|cell(t[1],t[4+b]),(a+b)%2?-1:1);
   std::vector<int>available;for(int j=0;j<COLS;++j)if(!used.count(j))available.push_back(j);
   std::vector<std::vector<int>>matrix(BITS+1,std::vector<int>(available.size(),1));
   for(int t0=0;t0<BITS;++t0)for(size_t j=0;j<available.size();++j)matrix[t0+1][j]=(available[j]>>t0)&1;
   std::vector<int>rhs(BITS+1,0);rhs[q+1]=1;rhs[(q+1)%BITS+1]=1;std::vector<int>coeff;
   need(f.solve(matrix,rhs,coeff),"robust bit evaluation matrix lost rank");
   std::vector<int>linear(coeff.size(),0);
   for(int t0=0;t0<BITS;++t0){std::vector<int>unit(BITS+1,0),c;unit[t0+1]=1;need(f.solve(matrix,unit,c),"unit row predicate not liftable");for(size_t j=0;j<c.size();++j)linear[j]=f.mod(linear[j]+rhs[t0+1]*c[j]);}
   need(linear==coeff,"chosen right inverse not linear");
   for(int i=0;i<=BITS;++i){int sum=0;for(size_t j=0;j<coeff.size();++j)sum=f.mod(sum+matrix[i][j]*coeff[j]);need(sum==rhs[i],"row-factor moment mismatch");}
   for(auto [k,c]:eta){for(size_t j=0;j<available.size();++j)if(coeff[j]){Key joined=join(k,0,available[j]);need(joined!=UINT32_MAX,"trade support collision");f.add(v,joined,c*coeff[j]);}for(int t0=0;t0<BITS;++t0)f.add(z[t0],k,c*rhs[t0+1]);}
   if(q)out<<',';
   out<<"{\"trade\":";sparse(out,eta);out<<",\"available_labels\":";vector_out(out,available);out<<",\"desired_moments_with_total_first\":";vector_out(out,rhs);out<<",\"row_factor\":";vector_out(out,coeff);out<<'}';
  }
  auto B=[&](Key k){return f.mod(point_value(k)+f.at(v,k));};
  auto C=[&](int t,Key k){return f.mod((1-((point[0]>>t)&1))*point_value(k)-f.at(z[t],k));};
  long marginal_checks=0,contraction_checks=0,module_checks=0,omission_failures=0;
  auto marginals=[&](const std::function<int(Key)>&mu,int ceiling){for(Key k:all)if(degree(k)<ceiling)for(int i=0;i<ROWS;++i)if(label(k,i)<0){int sum=0;for(int j=0;j<COLS;++j){Key a=join(k,i,j);if(a!=UINT32_MAX)sum=f.mod(sum+mu(a));}need(sum==mu(k),"old row marginal failed");++marginal_checks;}};
  marginals(B,3);for(int t=0;t<BITS;++t)marginals([&](Key k){return C(t,k);},2);
  for(Key k:all)if(degree(k)<=D)for(int t=0;t<BITS;++t){int contraction=0,bound=0,uncorrected=0;
   for(int j=0;j<COLS;++j)if(j>>t&1){Key a=join(k,0,j);if(a!=UINT32_MAX){contraction=f.mod(contraction+f.at(v,a));bound=f.mod(bound+B(a));uncorrected=f.mod(uncorrected+point_value(a));}}
   need(contraction==f.at(z[t],k),"trade contraction differs from target");++contraction_checks;
   need(f.mod(C(t,k)-B(k)+bound)==0,"literal-MP fan relation failed");++module_checks;
   if(f.mod(C(t,k)-point_value(k)+uncorrected))++omission_failures;
  }
  need(omission_failures>0,"omitted-correction control failed");
  // Indicator of label 3 vanishes outside the first trade's deleted labels.
  std::set<int>bad_used={3,4,5,6};std::vector<int>available;for(int j=0;j<COLS;++j)if(!bad_used.count(j))available.push_back(j);
  std::vector<std::vector<int>>bad(2,std::vector<int>(available.size(),1));for(size_t j=0;j<available.size();++j)bad[1][j]=available[j]==3;
  std::vector<int>no_solution;need(!f.solve(bad,{0,1},no_solution),"failed-rank control accepted");
  Key impossible=cell(1,3)|cell(2,5);need(join(impossible,0,3)==UINT32_MAX,"bad target must be forbidden by column collision");
  out<<"],\"top_trade_correction\":";sparse(out,v);out<<",\"target_defects\":[";for(int t=0;t<BITS;++t){if(t)out<<',';sparse(out,z[t]);}
  out<<"],\"row_marginal_checks\":"<<marginal_checks<<",\"contraction_checks\":"<<contraction_checks<<",\"MP_module_checks\":"<<module_checks<<",\"omitted_correction_failures\":"<<omission_failures<<",\"failed_rank_control\":{\"predicate\":\"indicator of label 3\",\"deleted_labels\":[3,4,5,6],\"inconsistent_target\":[0,1],\"forbidden_matching\":"<<impossible<<"},\"all_passed\":true}";
  std::cout<<"F"<<prime<<": "<<marginal_checks<<" marginals, "<<contraction_checks<<" contractions, "<<module_checks<<" MP equations passed; "<<omission_failures<<" omitted-correction violations; rank-loss control rejected\n";
 }
 out<<"]}\n";need(bool(out),"output write failed");
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
