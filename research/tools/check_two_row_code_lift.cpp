// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact two-row degree-one conditioning images, product codes and diagonal obstructions.
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
using Vec=std::vector<int>;using Mat=std::vector<Vec>;
void need(bool ok,const char*text){if(!ok)throw std::runtime_error(text);}
struct Field{
 int p;int mod(int x)const{x%=p;return x<0?x+p:x;}
 int inverse(int x)const{for(int i=1;i<p;++i)if(mod(i*x)==1)return i;throw std::runtime_error("noninvertible pivot");}
 std::vector<int> reduce(Mat&a)const{
  if(a.empty())return {};
  int m=int(a.size()),n=int(a[0].size()),r=0;std::vector<int>piv;
  for(int col=0;col<n&&r<m;++col){int q=r;while(q<m&&!mod(a[q][col]))++q;if(q==m)continue;std::swap(a[q],a[r]);int inv=inverse(a[r][col]);
   for(int j=col;j<n;++j)a[r][j]=mod(a[r][j]*inv);
   for(int i=0;i<m;++i)if(i!=r){int c=mod(a[i][col]);if(c)for(int j=col;j<n;++j)a[i][j]=mod(a[i][j]-c*a[r][j]);}
   piv.push_back(col);++r;
  }return piv;
 }
 int rank(Mat a)const{return int(reduce(a).size());}
 Mat kernel(Mat a)const{
  int n=int(a[0].size());auto piv=reduce(a);std::vector<bool>used(n,false);for(int j:piv)used[j]=true;Mat out;
  for(int j=0;j<n;++j)if(!used[j]){Vec v(n,0);v[j]=1;for(size_t i=0;i<piv.size();++i)v[piv[i]]=mod(-a[i][j]);out.push_back(v);}
  return out;
 }
 int dot(const Vec&a,const Vec&b)const{int sum=0;for(size_t i=0;i<a.size();++i)sum=mod(sum+a[i]*b[i]);return sum;}
};
void vector_out(std::ostream&o,const Vec&v){o<<'[';for(size_t i=0;i<v.size();++i){if(i)o<<',';o<<v[i];}o<<']';}
void matrix_out(std::ostream&o,const Mat&a){o<<'[';for(size_t i=0;i<a.size();++i){if(i)o<<',';vector_out(o,a[i]);}o<<']';}
int main(int argc,char**argv)try{
 need(argc==3&&std::string(argv[1])=="--out","usage: --out FILE");std::ifstream old(argv[2]);need(!old.good(),"refusing overwrite");
 std::cout<<"Fixed cases: eight/sixteen labels, three/four bit predicates, primes 2,3,5; at most 240 off-diagonal unknowns and 160 equation rows. No large parameter or assignment search.\n";
 std::ofstream out(argv[2]);need(bool(out),"cannot open output");out<<"{\"scope\":\"two-row top matching moments from degree one to two; no full source design or higher-degree theorem\",\"cases\":[";bool comma=false;
 for(int p:{2,3,5})for(int ell:{3,4}){
  Field f{p};int n=1<<ell;Mat eval(ell+1,Vec(n,1));for(int a=0;a<ell;++a)for(int k=0;k<n;++k)eval[a+1][k]=(k>>a)&1;
  need(f.rank(eval)==ell+1,"evaluation rank incorrect");Mat code=f.kernel(eval),products;
  for(size_t a=0;a<code.size();++a)for(size_t b=a;b<code.size();++b){Vec v(n);for(int k=0;k<n;++k)v[k]=f.mod(code[a][k]*code[b][k]);products.push_back(v);}
  int schur=f.rank(products);std::vector<std::pair<int,int>>cells;for(int k=0;k<n;++k)for(int l=0;l<n;++l)if(k!=l)cells.push_back({k,l});
  Mat marg(2*n,Vec(cells.size(),0)),image(2*ell*n,Vec(cells.size(),0));
  for(size_t q=0;q<cells.size();++q){auto [k,l]=cells[q];marg[k][q]=1;marg[n+l][q]=1;for(int a=0;a<ell;++a){image[a*n+l][q]=(k>>a)&1;image[ell*n+a*n+k][q]=(l>>a)&1;}}
  Mat stack=marg;stack.insert(stack.end(),image.begin(),image.end());int marginal_rank=f.rank(marg),stack_rank=f.rank(stack),actual=stack_rank-marginal_rank;
  Mat conditions;
  for(int a=0;a<2*ell;++a){Vec row(2*ell*n,0);for(int k=0;k<n;++k)row[a*n+k]=1;conditions.push_back(row);}
  for(int a=0;a<ell;++a)for(int b=0;b<ell;++b){Vec row(2*ell*n,0);for(int l=0;l<n;++l)row[a*n+l]=(l>>b)&1;for(int k=0;k<n;++k)row[ell*n+b*n+k]=f.mod(-((k>>a)&1));conditions.push_back(row);}
  int compatible=2*ell*n-f.rank(conditions);need(compatible==2*ell*(n-1)-ell*ell,"compatible dimension formula failed");need(compatible-actual==n-schur,"product-code deficit formula failed");
  if(comma)out<<',';
  comma=true;out<<"{\"prime\":"<<p<<",\"ell\":"<<ell<<",\"labels\":"<<n<<",\"evaluation_matrix\":";matrix_out(out,eval);out<<",\"code_basis\":";matrix_out(out,code);out<<",\"product_generators\":";matrix_out(out,products);
  out<<",\"marginal_rank\":"<<marginal_rank<<",\"stack_rank\":"<<stack_rank<<",\"compatible_target_dimension\":"<<compatible<<",\"actual_image_dimension\":"<<actual<<",\"product_code_rank\":"<<schur;
  if(ell==3){
   Vec target(2*ell*n,0);for(int l=0;l<n;++l)if(l&1)target[l]=f.mod((((l>>1)&1)+((l>>2)&1))%2?-1:1);
   for(const auto&row:conditions)need(f.dot(row,target)==0,"counterexample violates a stated compatibility condition");
   Vec dual(2*n+2*ell*n,0);
   for(int k=0;k<n;++k){int a=k&1,b=(k>>1)&1,c=(k>>2)&1;dual[k]=f.mod(a*b+a*c+b*c-a*b*c);dual[n+k]=(1-a)*(1-b)*(1-c);}
   for(int a=0;a<ell;++a)for(int l=0;l<n;++l){int prod=1;for(int b=0;b<ell;++b)if(b!=a)prod*=1-((l>>b)&1);dual[2*n+a*n+l]=f.mod(-prod);}
   for(int b=0;b<ell;++b)for(int k=0;k<n;++k){int prod=1;for(int a=0;a<ell;++a)if(a!=b)prod*=((k>>a)&1);dual[2*n+ell*n+b*n+k]=f.mod(-prod);}
   for(size_t q=0;q<cells.size();++q){int v=0;for(size_t i=0;i<stack.size();++i)v=f.mod(v+dual[i]*stack[i][q]);need(v==0,"diagonal dual does not annihilate matching columns");}
   Vec rhs(2*n,0);rhs.insert(rhs.end(),target.begin(),target.end());int value=f.dot(dual,rhs);need(value==f.mod(-1),"dual counterexample value wrong");
   Mat augmented=stack;for(size_t i=0;i<augmented.size();++i)augmented[i].push_back(rhs[i]);need(f.rank(augmented)==stack_rank+1,"bad target unexpectedly solvable");
   need(actual==32&&compatible==33&&schur==7,"eight-label ranks changed");
   out<<",\"nonliftable_target_z_then_w\":";vector_out(out,target);out<<",\"dual_on_marginals_then_conditioning\":";vector_out(out,dual);out<<",\"dual_value\":"<<value;
  }else{
   need(actual==104&&compatible==104&&schur==16,"sixteen-label ranks changed");out<<",\"coordinate_unit_product_witnesses\":[";
   for(int j=0;j<n;++j){Vec a(n,0),b(n,0);a[j]=b[j]=1;a[j^1]=a[j^2]=f.mod(-1);a[j^3]=1;b[j^4]=b[j^8]=f.mod(-1);b[j^12]=1;
    for(const auto&r:eval){need(f.dot(r,a)==0&&f.dot(r,b)==0,"square is not in evaluation kernel");}
    for(int k=0;k<n;++k)need(f.mod(a[k]*b[k])==(k==j),"kernel product is not coordinate unit");
    if(j)out<<',';
    out<<"{\"label\":"<<j<<",\"left\":";vector_out(out,a);out<<",\"right\":";vector_out(out,b);out<<'}';
   }out<<']';
  }
  out<<",\"all_passed\":true}";
  std::cout<<"F"<<p<<" labels="<<n<<": image="<<actual<<" compatible="<<compatible<<" product-code rank="<<schur<<(ell==3?"; explicit dual rejects target":"; every coordinate unit has a kernel-product witness")<<'\n';
 }
 out<<"]}\n";need(bool(out),"output write failed");
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
