#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
using M=uint64_t;using P=map<M,int>;
struct Term{int c;char kind;int a,b;M m;};
int p,n,r,v,maxdeg;vector<Term> cert;P sum;
M X(int j){return M(1)<<(4*j);}
int deg(M m){int d=0;for(int j=0;j<v;j++)d+=(m>>(4*j))&15;return d;}
void add(P&f,M m,int c){int z=(f[m]+c)%p;if(z<0)z+=p;if(z)f[m]=z;else f.erase(m);}
P mul(const P&a,const P&b){P z;for(auto [m,c]:a)for(auto [l,d]:b)add(z,m+l,c*d);return z;}
P ax(char kind,int a,int b){P z;if(kind=='B'){add(z,2*X(a),1);add(z,X(a),-1);}else if(kind=='R'){add(z,0,-1);for(int j=0;j<n;j++)add(z,X(a*n+j),1);}else add(z,X(a)+X(b),1);return z;}
void rec(int c,char kind,int a,int b,M m){c=(c%p+p)%p;if(!c)return;cert.push_back({c,kind,a,b,m});P g=ax(kind,a,b);for(auto [l,d]:g)add(sum,m+l,c*d);maxdeg=max(maxdeg,deg(m)+(kind=='R'?1:2));}
int eval(const P&f,const vector<int>&x){int z=0;for(auto [m,c]:f){int y=c;for(int j=0;j<v;j++)if(((m>>(4*j))&15)&&!x[j]){y=0;break;}z=(z+y)%p;}return z;}
void poly(ostream&o,const P&f){o<<"[";bool first=true;for(auto [m,c]:f){if(!first)o<<",";first=false;o<<"["<<c<<","<<m<<"]";}o<<"]";}
void check(ostream&out,int prime,int rows,int cols){
 p=prime;r=rows;n=cols;v=r*n;if(v>12||p>5||r>3)throw runtime_error("fixed budget exceeded");
 cert.clear();sum.clear();maxdeg=0;
 P L;add(L,0,2);for(int i=0;i<r;i++)for(int j=0;j<n;j++)add(L,X(i*n+j),i+2*j+1);
 P power{{0,1}};for(int j=0;j<p-1;j++)power=mul(power,L);
 P q{{0,1}};for(auto [m,c]:power)add(q,m,-c);
 P local;
 for(auto [original,c]:q){
  M m=original;
  for(int j=0;j<v;j++){int e=(m>>(4*j))&15;if(e>=2){M other=m-e*X(j);for(int l=0;l<=e-2;l++)rec(c,'B',j,-1,other+l*X(j));m=other+X(j);}}
  bool killed=false;
  for(int i=0;i<r&&!killed;i++){int first=-1;for(int j=0;j<n;j++)if(m&X(i*n+j)){if(first<0)first=i*n+j;else{int b=i*n+j;rec(c,'S',first,b,m-X(first)-X(b));killed=true;break;}}}
  if(!killed)add(local,m,c);
 }
 P full;
 for(auto [m,c]:local){
  P cur{{m,c}};
  for(int i=0;i<r;i++){
   bool present=false;for(int j=0;j<n;j++)present|=(m&X(i*n+j))!=0;
   if(present)continue;
   P next;for(auto [a,b]:cur){rec(-b,'R',i,-1,a);for(int j=0;j<n;j++)add(next,a+X(i*n+j),b);}cur=move(next);
  }
  for(auto [a,b]:cur)add(full,a,b);
 }
 P target;
 for(auto [m,c]:full){
  bool killed=false;
  for(int j=0;j<n&&!killed;j++){int first=-1;for(int i=0;i<r;i++)if(m&X(i*n+j)){if(first<0)first=i*n+j;else{int b=i*n+j;rec(c,'C',first,b,m-X(first)-X(b));killed=true;break;}}}
  if(!killed){if(c!=1)throw runtime_error("non-indicator coefficient");add(target,m,c);}
 }
 P residual=q;for(auto [m,c]:target)add(residual,m,-c);for(auto [m,c]:sum)add(residual,m,-c);
 if(!residual.empty()||maxdeg>max(p-1,r))throw runtime_error("ordinary NS identity or degree failed");
 bool bad_control=false;
 if(!target.empty()){
  P bad=target;add(bad,bad.begin()->first,-1);P diff=q;for(auto [m,c]:bad)add(diff,m,-c);for(auto [m,c]:sum)add(diff,m,-c);bad_control=!diff.empty();
  if(!bad_control)throw runtime_error("omission control");
 }
 out<<"{\"p\":"<<p<<",\"rows\":"<<r<<",\"columns\":"<<n<<",\"variable_encoding\":\"4-bit exponents, row-major, uint64 monomial keys\",\"form\":";poly(out,L);
 out<<",\"selector\":";poly(out,q);out<<",\"matching_indicator_expansion\":";poly(out,target);
 out<<",\"max_certificate_degree\":"<<maxdeg<<",\"certificate_terms\":[";
 bool first=true;for(auto t:cert){if(!first)out<<",";first=false;out<<"["<<t.c<<",\""<<t.kind<<"\","<<t.a<<","<<t.b<<","<<t.m<<"]";}
 out<<"],\"certificate_schema\":\"[coefficient, axiom B=Boolean R=row S=same-row C=same-column, first index, second index, multiplier monomial]; R first index is row, others are variable indices\",\"ordinary_identity_checked\":true,\"omitted_term_control_rejected\":"<<(bad_control?"true":"false")<<"}";
 cout<<"p="<<p<<" rows="<<r<<" terms="<<target.size()<<" certificate_degree="<<maxdeg<<" identity passed\n";
}
int main(int argc,char**argv){
 if(argc!=2)throw runtime_error("usage check OUTPUT");
 ofstream out(argv[1]);if(!out)throw runtime_error("output");
 out<<"{\"checks\":[";check(out,3,1,4);out<<",";check(out,3,2,4);out<<",";check(out,3,3,4);out<<",";check(out,5,3,4);
 // Weak functional-omission control: first row has four ones, second row its fifth column.
 // All Boolean, row-sum (mod 3), and column-collision axioms hold; same-row does not.
 vector<int> w={1,1,1,1,0,0,0,0,0,1};
 for(int a:w)if(a*(a-1)%3)throw runtime_error("weak Booleanity");
 for(int i=0;i<2;i++){int total=0;for(int j=0;j<5;j++)total+=w[5*i+j];if(total%3!=1)throw runtime_error("weak row");}
 for(int j=0;j<5;j++)if(w[j]!=0 && w[5+j]!=0)throw runtime_error("weak column");
 if(w[0]==0 || w[1]==0)throw runtime_error("missing same-row failure");
 int L=w[0]+w[1],q=(1-L*L)%3;if(q<0)q+=3;
 int G=(w[2]+w[3]+w[4])*(w[5]+w[6]+w[7]+w[8]+w[9])%3;
 if(q==G)throw runtime_error("functionality negative control");
 out<<"],\"weak_row_control\":{\"p\":3,\"rows\":2,\"columns\":5,\"ones\":[[0,0],[0,1],[0,2],[0,3],[1,4]],\"form\":\"X_00+X_01\",\"selector_value\":"<<q<<",\"row_state_expansion_value\":"<<G<<",\"boolean_rows_columns_hold\":true,\"same_row_exclusions_fail\":true},\"scope\":\"Exact original-polynomial NS interpolation identities; no new numerical verification of switching or asymptotic lower bounds\"}\n";
}
