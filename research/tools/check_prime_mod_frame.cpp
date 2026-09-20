// Exact bivariate MOD-recursion NS certificates over four prime fields.
// Exponents are [t, a]; all arithmetic is reduced modulo p after each operation.
#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <utility>
using E=std::pair<int,int>;
using Poly=std::map<E,int>;
static int p;
static void addterm(Poly& f,E e,int c){c=(c%p+p)%p; int v=(f[e]+c)%p;if(v)f[e]=v;else f.erase(e);}
static Poly add(Poly f,const Poly& g,int sign=1){for(auto [e,c]:g)addterm(f,e,sign*c);return f;}
static Poly mul(const Poly& f,const Poly& g){Poly q;for(auto [a,c]:f)for(auto [b,d]:g)addterm(q,{a.first+b.first,a.second+b.second},c*d);return q;}
static Poly pow(Poly f,int n){Poly q={{{0,0},1}};while(n){if(n&1)q=mul(q,f);n>>=1;if(n)f=mul(f,f);}return q;}
static int degree(const Poly& f){int n=-1;for(auto [e,c]:f)n=std::max(n,e.first+e.second);return n;}
static int val(const Poly& f,int t,int a){int z=0;for(auto [e,c]:f){int w=c;for(int i=0;i<e.first;++i)w=w*t%p;for(int i=0;i<e.second;++i)w=w*a%p;z=(z+w)%p;}return z;}
// Divide by z^d-z, with z equal to a or t, preserving total-degree bounds.
static std::pair<Poly,Poly> divide(Poly f,bool in_a,int d){Poly q;while(true){auto it=std::find_if(f.rbegin(),f.rend(),[&](const auto& term){return (in_a?term.first.second:term.first.first)>=d;});if(it==f.rend())break;E e=it->first;int c=it->second;E b=e;if(in_a)b.second-=d;else b.first-=d;addterm(q,b,c);addterm(f,e,-c);if(in_a)++b.second;else ++b.first;addterm(f,b,c);}return {q,f};}
static void emit(std::ostream& o,const Poly& f){o<<'[';bool first=true;for(auto [e,c]:f){if(!first)o<<',';first=false;o<<'['<<e.first<<','<<e.second<<','<<c<<']';}o<<']';}
static void require(bool good,const char* s){if(!good)throw std::runtime_error(s);}
int main(int argc,char** argv){try{
 if(argc!=3||std::string(argv[1])!="--out")throw std::runtime_error("Usage: check_prime_mod_frame --out FILE");
 std::ofstream out(argv[2]);require(bool(out),"Cannot open output");
 out<<"{\"schema\":1,\"variables\":[\"t\",\"a\"],\"term_encoding\":\"[t_exponent,a_exponent,coefficient]\",\"cases\":[\n";
 bool first=true;
 for(int prime:{2,3,5,7}){p=prime;
 const Poly one={{{0,0},1}},t={{{1,0},1}},a={{{0,1},1}};
 auto b=pow(t,p-1), c=pow(add(t,one,-1),p-1), m=pow(add(add(t,a),one,-1),p-1);
 auto l=mul(a,add(one,b,-1)),r=mul(add(one,a,-1),add(one,c,-1));
 auto q=mul(add(one,l,-1),add(one,r,-1));
 auto forward=mul(add(one,m,-1),q),backward=mul(m,add(one,q,-1));
 auto F=add(one,mul(add(one,forward,-1),add(one,backward,-1)),-1);
 auto Ha=add(pow(a,2),a,-1),Ht=add(pow(t,p),t,-1);
 auto [A,after_a]=divide(F,true,2);auto [B,remainder]=divide(after_a,false,p);
 require(remainder.empty(),"MOD frame division left nonzero remainder");
 require(add(mul(A,Ha),mul(B,Ht))==F,"Certificate identity failed");
 int K=10*(p-1);
 require(degree(F)<=K && (A.empty()||degree(A)+2<=K) && (B.empty()||degree(B)+p<=K),"Degree budget failed");
 for(int ti=0;ti<p;++ti)for(int ai=0;ai<2;++ai)require(val(F,ti,ai)==0,"Grid vanishing failed");
 require(!after_a.empty()&&!B.empty(),"Missing field-relation control was vacuous");
 auto J=add(add(m,mul(a,b),-1),mul(add(one,a,-1),c),-1);
 auto [R,Jrem]=divide(J,true,2);require(Jrem.empty(),"Interpolation division failed");
 require(mul(R,Ha)==J,"Interpolation certificate identity failed");
 require((p==2&&R.empty())||(p>2&&(R.empty()||degree(R)<=p-3)),"Interpolation degree failed");
 if(!first){out<<",\n";}
 first=false;
 out<<"{\"p\":"<<p<<",\"budget\":"<<K<<",\"frame_degree\":"<<degree(F)<<",\"a_cofactor_degree\":"<<degree(A)<<",\"field_cofactor_degree\":"<<degree(B)<<",\"F\":";emit(out,F);
 out<<",\"A\":";emit(out,A);out<<",\"B\":";emit(out,B);out<<",\"a_relation\":";emit(out,Ha);out<<",\"field_relation\":";emit(out,Ht);
 out<<",\"without_field_relation_remainder\":";emit(out,after_a);out<<",\"interpolation_target\":";emit(out,J);out<<",\"interpolation_cofactor\":";emit(out,R);
 out<<",\"all_checks_passed\":true}";
 std::cout<<"p="<<p<<": exact frame degree "<<degree(F)<<", budget "<<K<<", certificate terms "<<A.size()<<'+'<<B.size()<<"; missing-field control nonzero\n";
 }
 out<<"\n]}\n";require(bool(out),"Output write failed");return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
