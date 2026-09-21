#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <set>
#include <string>
#include <vector>
using V=std::vector<int>;
struct Check {
 int p,n=4,m=5,v=20,dim=231; std::vector<V> basis;std::vector<int> piv;std::set<std::string> allowed; long tested=0,positive=0;
 int mod(int a) const {a%=p;return a<0?a+p:a;}
 int pair(int i,int j)const {if(i>j)std::swap(i,j);return 1+v+i*v-i*(i-1)/2+(j-i);}
 void reduce(V& a)const{for(size_t q=0;q<basis.size();q++){int c=a[piv[q]];if(c)for(int j=piv[q];j<dim;j++)a[j]=mod(a[j]-c*basis[q][j]);}}
 void add(V a){reduce(a);int j=0;while(j<dim&&!a[j])j++;if(j==dim)return;int inv=1;while(mod(inv*a[j])!=1)inv++;for(int k=j;k<dim;k++)a[k]=mod(a[k]*inv);auto at=std::lower_bound(piv.begin(),piv.end(),j)-piv.begin();piv.insert(piv.begin()+at,j);basis.insert(basis.begin()+at,a);}
 std::string key(int c,V a)const{for(int i=0;i<m;i++){int t=a[i*n+n-1];c=mod(c+t);for(int j=0;j<n;j++)a[i*n+j]=mod(a[i*n+j]-t);}std::string s(1,char(c));for(int x:a)s+=char(x);return s;}
 explicit Check(int field):p(field){
  for(int i=0;i<v;i++){V q(dim);q[pair(i,i)]=1;q[1+i]=p-1;add(q);}
  for(int r=0;r<m;r++)for(int mult=-1;mult<v;mult++){V q(dim);if(mult<0){q[0]=p-1;for(int j=0;j<n;j++)q[1+r*n+j]=1;}else{q[1+mult]=p-1;for(int j=0;j<n;j++)q[pair(mult,r*n+j)]=mod(q[pair(mult,r*n+j)]+1);}add(q);}
  for(int i=0;i<v;i++)for(int j=i+1;j<v;j++)if(i/n==j/n||i%n==j%n){V q(dim);q[pair(i,j)]=1;add(q);}
  for(int r=0;r<m;r++)for(int mask=0;mask<(1<<n);mask++){V a(v);for(int j=0;j<n;j++)if(mask>>j&1)a[r*n+j]=1;allowed.insert(key(0,a));}
  for(int j=0;j<n;j++)for(int mask=0;mask<(1<<m);mask++)for(int comp=0;comp<2;comp++){V a(v);for(int i=0;i<m;i++)if(mask>>i&1)a[i*n+j]=comp?p-1:1;allowed.insert(key(comp,a));}
 }
 bool test(int c,const V& a){V q(dim);q[0]=mod(c*c-c);for(int i=0;i<v;i++){q[1+i]=mod((2*c-1)*a[i]);q[pair(i,i)]=mod(a[i]*a[i]);for(int j=i+1;j<v;j++)q[pair(i,j)]=mod(2*a[i]*a[j]);}reduce(q);bool found=std::all_of(q.begin(),q.end(),[](int x){return x==0;});bool expected=allowed.count(key(c,a));tested++;positive+=found;if(found!=expected){std::cerr<<"Mismatch p="<<p<<" c="<<c<<"\n";std::exit(2);}return found;}
 void slice(const V& positions){int count=p;for(size_t i=0;i<positions.size();i++)count*=p;if(count>3000)std::exit(3);for(int code=0;code<count;code++){int t=code,c=t%p;t/=p;V a(v);for(int i:positions){a[i]=t%p;t/=p;}test(c,a);}}
 void run(){slice(p==3?V{0,1,2,4,5,6}:V{0,1,2});if(p==3)for(int j=0;j<n;j++)slice(V{j,4+j,8+j,12+j,16+j});uint32_t seed=1234567;for(int t=0;t<500;t++){V a(v);for(int& x:a){seed=1664525u*seed+1013904223u;x=int(seed%uint32_t(p));}seed=1664525u*seed+1013904223u;test(int(seed%uint32_t(p)),a);}V row(v);row[0]=row[1]=1;if(!test(0,row))std::exit(4);V cross(v);cross[0]=cross[5]=1;if(test(0,cross))std::exit(5);}
 void emit(std::ostream& o)const{o<<"{\"p\":"<<p<<",\"holes\":4,\"rows\":5,\"ordinary_degree\":2,\"monomial_columns\":"<<dim<<",\"NS_rank\":"<<basis.size()<<",\"classified_affine_classes\":"<<allowed.size()<<",\"tested\":"<<tested<<",\"positive\":"<<positive<<",\"passed\":true}";}
};
int main(int argc,char**argv){if(argc!=2)return 1;std::cout<<"Bounded slices: 5605 ternary and 1127 quinary targets; at most 231 polynomial coordinates.\n";Check a(3);a.run();Check b(5);b.run();std::ofstream out(argv[1]);out<<"[";a.emit(out);out<<",";b.emit(out);out<<"]\n";a.emit(std::cout);std::cout<<"\n";b.emit(std::cout);std::cout<<"\n";}
