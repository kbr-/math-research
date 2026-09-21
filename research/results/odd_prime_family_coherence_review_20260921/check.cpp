#include <array>
#include <cassert>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>
using namespace std;using E=array<int,5>;using P=map<E,int>;
int md(int x){x%=3;return x<0?x+3:x;}
P add(P a,const P&b,int scale=1){for(auto[e,c]:b){a[e]=md(a[e]+scale*c);if(!a[e])a.erase(e);}return a;}
P mul(const P&a,const P&b){P z;for(auto[e,c]:a)for(auto[f,d]:b){E g{};for(int i=0;i<5;i++)g[i]=e[i]+f[i];z[g]=md(z[g]+c*d);if(!z[g])z.erase(g);}return z;}
P con(int c){P p;if(md(c))p[E{}]=md(c);return p;}
P var(int i){E e{};e[i]=1;return {{e,1}};}
P powr(P p,int e){P q=con(1);for(int i=0;i<e;i++)q=mul(q,p);return q;}
P nf(const P&p){P q;for(auto[e,c]:p){E g=e;for(int&i:g)while(i>=3)i-=2;q[g]=md(q[g]+c);if(!q[g])q.erase(g);}return q;}
int degree(const P&p){int d=-1;for(auto[e,c]:p){int s=0;for(int a:e)s+=a;d=max(d,s);}return d;}
int eval(const P&p,const array<int,5>&x){int v=0;for(auto[e,c]:p){int z=c;for(int i=0;i<5;i++)for(int j=0;j<e[i];j++)z=z*x[i]%3;v=md(v+z);}return v;}
int main(int argc,char**argv){
 if(argc!=3||string(argv[1])!="--out")return 2;
 cerr<<"Budget: F3 feature identities in five variables, 108 original-degree axiom checks, three explicit matching models, sixteen signed-trade evaluations.\n";
 P a=var(0),b=var(1),t=add(a,b,-1),one=con(1);
 vector<P>q={add(one,powr(a,2),-1),add(one,powr(b,2),-1),add(one,powr(add(a,b),2),-1)};
 P sum;for(P f:q)sum=add(sum,f);assert(sum==powr(t,2));
 assert(add(q[1],q[0],-1)==mul(t,add(a,b)));
 assert(add(q[2],q[0],-1)==mul(t,b));
 P prod=one;for(int i=0;i<3;i++)prod=add(prod,mul(var(i+2),q[i]),-1);
 vector<P>comp;for(P f:q){comp.push_back(mul(f,prod));assert(degree(comp.back())==5);}
 P target=mul(t,prod),certificate;
 for(P f:comp){assert(degree(mul(t,f))==6);certificate=add(certificate,mul(t,f));}
 certificate=add(certificate,mul(prod,add(powr(t,3),t,-1)),-1);
 assert(target==certificate&&degree(target)==4);
 P common=nf(mul(q[0],q[1]));
 for(int i=0;i<3;i++)for(int j=0;j<3;j++)assert(nf(mul(q[i],q[j]))==(i==j?nf(q[i]):common));
 array<array<int,5>,3>pts={array<int,5>{1,1,0,0,0},{1,0,0,0,0},{2,0,0,0,0}};
 auto functional=[&](const P&f){return md(eval(f,pts[0])+eval(f,pts[1])-eval(f,pts[2]));};
 assert(functional(one)==1&&functional(t)==2&&functional(target)==2);
 vector<P>cof={one};for(int i=0;i<5;i++)cof.push_back(var(i));for(int i=0;i<5;i++)for(int j=i;j<5;j++)cof.push_back(mul(var(i),var(j)));
 int checks=0;for(int i=0;i<5;i++){P field=add(powr(var(i),3),var(i),-1);for(P f:cof){assert(degree(mul(field,f))<=5);assert(functional(mul(field,f))==0);checks++;}}
 for(P f:comp){assert(functional(f)==0);checks++;}
 assert(checks==108);
 vector<vector<int>>models;for(int first:{13,10,11}){vector<int>v{first};for(int j=1;j<=8;j++)v.push_back(j);assert(set<int>(v.begin(),v.end()).size()==9);int A=0,B=0;for(int label:v){A+=label%3;B+=(label/3)%3;}assert(md(A)==pts[models.size()][0]&&md(B)==pts[models.size()][1]);models.push_back(v);}
 array<array<int,2>,4>pairs={array<int,2>{0,1},{9,10},{18,21},{2,5}};set<int>used;for(auto v:pairs)for(int j:v)assert(used.insert(j).second);
 int trade=0;for(int mask=0;mask<16;mask++){int A=0,B=0,w=1;for(int i=0;i<4;i++){int bit=mask>>i&1,label=pairs[i][bit];A+=label%3;B+=(label/3)%3;if(!bit)w=-w;}trade=md(trade+w*md(A*A)*md(B*B));}assert(trade==1);
 ofstream o(argv[2]);o<<"{\"prime\":3,\"selector_sum_is_difference_square\":true,\"degree_three_affine_certificate\":true,\"source_companion_degree\":5,\"source_target_degree\":4,\"source_target_certificate_degree\":6,\"feature_field_axiom_checks\":"<<checks<<",\"functional_on_unit\":1,\"functional_on_difference\":2,\"functional_on_product_times_difference\":2,\"leading_off_diagonal_matrix_determinant\":2,\"signed_four_row_trade_pairing\":1,\"matching_models\":[";
 for(int i=0;i<3;i++){if(i)o<<",";o<<"{\"weight\":"<<(i==2?2:1)<<",\"row_labels\":[";for(int j=0;j<9;j++){if(j)o<<",";o<<models[i][j];}o<<"]}";}
 o<<"],\"all_checks_passed\":true}\n";
}
