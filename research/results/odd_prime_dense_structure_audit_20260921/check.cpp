#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>
#include <vector>
using namespace std;
int rankmod(vector<vector<int>> a,int p){
 int r=0;
 for(int j=0;j<6&&r<(int)a.size();j++){
  int k=r;while(k<(int)a.size()&&!a[k][j])k++;if(k==(int)a.size())continue;
  swap(a[k],a[r]);int inv=1;while(inv*a[r][j]%p!=1)inv++;
  for(int c=j;c<6;c++)a[r][c]=a[r][c]*inv%p;
  for(int i=r+1;i<(int)a.size();i++){int f=a[i][j];for(int c=j;c<6;c++)a[i][c]=(a[i][c]-f*a[r][c]%p+p)%p;}r++;
 }
 return r;
}
vector<vector<int>> powers(int p){
 vector<vector<int>> a;for(int x=0;x<p;x++)for(int y=0;y<p;y++)for(int z=0;z<p;z++)
 a.push_back({x*x%p,y*y%p,z*z%p,2*x*y%p,2*x*z%p,2*y*z%p});
 return a;
}
int main(int argc,char**argv){
 if(argc!=2)throw runtime_error("usage check OUTPUT.json");
 // Fixed budget: 728 nonzero functionals times 27 points and 729 coefficient assignments.
 auto v=powers(3);map<int,int> hist;
 for(int code=1;code<729;code++){
  vector<int>b(6);int a=code;for(int j=0;j<6;j++){b[j]=a%3;a/=3;}
  int support=0;for(auto x:v){int z=0;for(int j=0;j<6;j++)z+=b[j]*x[j];support+=(z%3!=0);}
  if(support<9)throw runtime_error("quadratic support bound");
  hist[support]++;
 }
 int r3=rankmod(v,3),r2=rankmod(powers(2),2);
 if(r3!=6||r2!=3)throw runtime_error("Veronese rank/control");
 vector<int>counts(243);
 for(int code=0;code<729;code++){
  int c=code;vector<int>a(6);for(int j=0;j<6;j++){a[j]=c%3;c/=3;}
  vector<int>b={(a[1]-a[0]+3)%3,(a[2]-a[0]+3)%3,(a[4]-a[3]+3)%3,(a[5]-a[3]+3)%3,(a[0]+a[3])%3};
  int key=0,place=1;for(int z:b){key+=place*z;place*=3;}counts[key]++;
 }
 if(*min_element(counts.begin(),counts.end())!=3||*max_element(counts.begin(),counts.end())!=3)throw runtime_error("row projection distribution");
 ofstream out(argv[1]);if(!out)throw runtime_error("output");
 out<<"{\"field\":3,\"variables\":3,\"nonzero_functionals\":728,\"points_per_functional\":27,\"support_histogram\":{";
 bool first=true;for(auto [k,v]:hist){if(!first)out<<",";first=false;out<<"\""<<k<<"\":"<<v;}
 out<<"},\"veronese_rank_F3\":"<<r3<<",\"veronese_rank_F2_negative_control\":"<<r2<<",\"projection\":{\"rows\":2,\"neighbors\":3,\"coefficient_assignments\":729,\"projected_coefficient_and_constant_values\":243,\"every_fiber_size\":3},\"scope\":\"Exact local anti-concentration and uniform-projection controls, not an exhaustive sample of the asymptotic graph family\"}\n";
 cout<<"728 quadratic functionals checked; minimum support "<<hist.begin()->first<<"/27. F3 rank 6; F2 control rank 3. All 243 projection fibers have size 3.\n";
}
