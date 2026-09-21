#include <algorithm>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <vector>
using namespace std;
int rankmod(vector<vector<int>> a,int p){
 int row=0,n=a.size(),m=a.empty()?0:a[0].size();
 for(int j=0;j<m&&row<n;j++){
  int b=row;while(b<n&&!a[b][j])b++;
  if(b==n)continue;
  swap(a[b],a[row]);int inv=1;while(inv*a[row][j]%p!=1)inv++;
  for(int c=j;c<m;c++)a[row][c]=a[row][c]*inv%p;
  for(int i=row+1;i<n;i++)if(a[i][j]){
   int f=a[i][j];for(int c=j;c<m;c++)a[i][c]=(a[i][c]-f*a[row][c]%p+p)%p;
  }
  row++;
 }
 return row;
}
vector<int> ranks(int p,int r){
 int v=3*r;if(v>6)throw runtime_error("Budget: at most 64 points and 64 monomials");
 vector<int> pts;
 for(int x=0;x<(1<<v);x++){
  bool ok=true;for(int i=0;i<r;i++)ok&=(__builtin_popcount((unsigned)((x>>(3*i))&7))%p!=0);
  if(ok)pts.push_back(x);
 }
 vector<int> result;
 for(int k=0;k<=v;k++){
  vector<int> cols;for(int t=0;t<(1<<v);t++)if(__builtin_popcount((unsigned)t)<=k)cols.push_back(t);
  vector<vector<int>> a(pts.size(),vector<int>(cols.size()));
  for(unsigned i=0;i<pts.size();i++)for(unsigned j=0;j<cols.size();j++)a[i][j]=((pts[i]&cols[j])==cols[j]);
  result.push_back(rankmod(a,p));
 }
 return result;
}
void printarr(ostream& out,const vector<int>& v){out<<"[";for(unsigned i=0;i<v.size();i++){if(i)out<<",";out<<v[i];}out<<"]";}
int main(int argc,char**argv){
 if(argc!=2)throw runtime_error("usage: check OUTPUT.json");
 ofstream out(argv[1]);if(!out)throw runtime_error("output");
 auto a=ranks(3,1),b=ranks(3,2),c=ranks(5,1);
 if(a!=vector<int>({1,4,6,6})||b!=vector<int>({1,7,20,32,36,36,36}))throw runtime_error("Hilbert mismatch");
 if(c!=vector<int>({1,4,7,7}))throw runtime_error("negative field control");
 out<<"{\"max_cube_points\":64,\"exact_modular_checks\":[{\"p\":3,\"triples\":1,\"filtered_ranks\":";
 printarr(out,a);out<<"},{\"p\":3,\"triples\":2,\"filtered_ranks\":";printarr(out,b);
 out<<"}],\"p5_negative_control\":";printarr(out,c);
 out<<",\"ternary_formula_fails_at_p5\":true,\"scope\":\"Boolean-only actual selector false sets, not PHP-restricted ranks or asymptotic separator verification\"}\n";
 cout<<"Exact F3 ranks passed; F5 field-change control rejected the ternary formula.\n";
}
