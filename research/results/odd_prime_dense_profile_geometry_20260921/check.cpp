#include <array>
#include <cassert>
#include <fstream>
#include <iostream>
#include <string>
using namespace std;
int mod(int x,int p){x%=p;return x<0?x+p:x;}
int power(int x,int k,int p){int y=1;for(;k;k--)y=y*x%p;return y;}
int main(int argc,char**argv){
 if(argc!=3||string(argv[1])!="--out")return 2;
 cerr<<"Budget: primes 3 and 5, 64 Boolean assignments each, <=45 local/probe states.\n";
 ofstream o(argv[2]);o<<"{\"board_rows\":2,\"board_columns\":3,\"tests\":[";
 for(int p:{3,5}){
 int field=0,models=0,nonbool=0,emptyfail=0;
 for(int mask=0;mask<64;mask++){
  array<int,6>x{};for(int i=0;i<6;i++)x[i]=mask>>i&1;
  int U=mod(x[0]+2*x[1]+x[2]+2*x[3]+x[4]+2*x[5],p);
  int g1=mod(1-power(mod(U+x[1]+2*x[3],p),p-1,p),p),g2=mod(U+2*x[2]+x[3],p);
  array<int,2>b{},bad{};int partition=0;
  for(int j=0;j<3;j++)for(int a=-1;a<2;a++){
   if((j==0&&a!=0)||(j!=0&&a==0))continue;
   int pi=x[j]*(a<0?mod(1-x[0]-x[3],p):x[3*a]);
   for(int u=0;u<p;u++){
    int chi=mod(1-power(mod(U-u,p),p-1,p),p), w=mod(pi*chi,p);
    int v1=mod(1-power(mod(u+(j==1)+2*(a==1),p),p-1,p),p);
    int v2=mod(u+2*(j==2)+(a==1),p);
    array<int,2>coef{};if(v1)coef[0]=power(v1,p-2,p);else if(v2)coef[1]=power(v2,p-2,p);
    partition=mod(partition+w,p);
    for(int i=0;i<2;i++){b[i]=mod(b[i]+w*coef[i],p);if(a>=0)bad[i]=mod(bad[i]+w*coef[i],p);}
   }
  }
  for(int z:b){assert(mod(power(z,p,p)-z,p)==0);field++;if(mod(z*z-z,p))nonbool++;}
  bool valid=x[0]+x[1]+x[2]==1&&x[3]+x[4]+x[5]==1;
  for(int j=0;j<3;j++)valid&=x[j]+x[j+3]<=1;
  if(valid){
   models++;assert(partition==1);
   int P=mod(1-b[0]*g1-b[1]*g2,p);assert(g1*P%p==0&&g2*P%p==0);
   int Q=mod(1-bad[0]*g1-bad[1]*g2,p);emptyfail+=(g1*Q%p!=0||g2*Q%p!=0);
  }
 }
 assert(models==6&&emptyfail>0&&nonbool>0);
 if(p!=3)o<<",";o<<"{\"prime\":"<<p<<",\"Boolean_assignments\":64,\"field_checks\":"<<field<<",\"matching_models\":"<<models<<",\"nonBoolean_coefficient_values\":"<<nonbool<<",\"omitted_empty_state_failures\":"<<emptyfail<<"}";
 }
 o<<"],\"all_checks_passed\":true}\n";
}
