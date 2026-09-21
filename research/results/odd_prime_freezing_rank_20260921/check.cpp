#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <vector>
using namespace std;
int mod(int z){z%=3;return z<0?z+3:z;}
int rank3(vector<array<int,3>> a){
 int r=0;
 for(int j=0;j<3 && r<(int)a.size();j++){
  int k=r;while(k<(int)a.size()&&!a[k][j])k++;
  if(k==(int)a.size())continue;
  swap(a[k],a[r]);int inv=a[r][j];
  for(int c=j;c<3;c++)a[r][c]=a[r][c]*inv%3;
  for(int i=r+1;i<(int)a.size();i++){int f=a[i][j];for(int c=j;c<3;c++)a[i][c]=mod(a[i][c]-f*a[r][c]);}
  r++;
 }
 return r;
}
int main(int argc,char**argv){
 if(argc!=2)throw runtime_error("usage check OUTPUT.json");
 constexpr int n=30,h=3;
 // Fixed budget: 26 words, 202275 rectangles x 30 blocks x 3 basis coordinates,
 // plus at most 1024 sign assignments in each scalar check.
 vector<array<int,h>> C(n+1);
 for(int i=0;i<27;i++){int z=i;for(int j=0;j<h;j++){C[i][j]=z%3;z/=3;}}
 int minweight=n,minrect=n;
 for(int a=1;a<27;a++){
  int z=a;array<int,h> v{};for(int j=0;j<h;j++){v[j]=z%3;z/=3;}
  int weight=0,c1=0,c2=0;
  for(int i=0;i<n;i++){
   int b=0;for(int j=0;j<h;j++)b+=v[j]*C[i][j];b%=3;
   weight+=(b!=0);c1+=(b==1);c2+=(b==2);
  }
  minweight=min(minweight,weight);
  minrect=min(minrect,max(c1,c2)/2);
 }
 if(minweight<n/3||minrect<n/12)throw runtime_error("code/rectangle lower bound");
 auto entry=[&](int block,int row,int col,int j){return row<n&&col==(row+block)%n?C[row][j]:0;};
 vector<long long> hist(5);long long rectangles=0;
 for(int a=0;a<=n;a++)for(int b=a+1;b<=n;b++)for(int c=0;c<n;c++)for(int d=c+1;d<n;d++){
  int active=0;
  for(int block=0;block<n;block++){
   bool nonzero=false;
   for(int j=0;j<h;j++)nonzero|=mod(entry(block,a,c,j)-entry(block,b,c,j)-entry(block,a,d,j)+entry(block,b,d,j))!=0;
   active+=nonzero;
  }
  if(active>4)throw runtime_error("four-cell support bound");
  hist[active]++;rectangles++;
 }
 vector<array<int,3>> offdiag;
 for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)offdiag.push_back({C[i][0]*C[j][0]%3,C[i][1]*C[j][1]%3,C[i][2]*C[j][2]%3});
 int nonlinear_rank=rank3(offdiag);
 array<array<int,3>,3> coordinate_basis{{{1,0,0},{0,1,0},{0,0,1}}};
 vector<array<int,3>> identity_control;
 for(int i=0;i<3;i++)for(int j=i+1;j<3;j++)identity_control.push_back({coordinate_basis[i][0]*coordinate_basis[j][0],coordinate_basis[i][1]*coordinate_basis[j][1],coordinate_basis[i][2]*coordinate_basis[j][2]});
 int identity_nonlinear_rank=rank3(identity_control);
 if(nonlinear_rank!=h || identity_nonlinear_rank!=0)throw runtime_error("nonlinear rank controls");
 ofstream out(argv[1]);if(!out)throw runtime_error("output");
 out<<"{\"field\":3,\"columns\":30,\"pigeon_rows\":31,\"blocks\":30,\"code_dimension\":3,\"code_definition\":\"rows 0..26 enumerate F3^3 in base-three order; rows 27..30 zero\",\"minimum_nonzero_code_weight\":"<<minweight<<",\"minimum_equal-value_disjoint_rectangle_count\":"<<minrect<<",\"rectangles_checked\":"<<rectangles<<",\"active_block_histogram\":[";
 for(int j=0;j<5;j++){if(j)out<<",";out<<hist[j];}
 out<<"],\"signed_sum_counts\":[";
 for(int r=1;r<=10;r++){
  array<int,3> counts{};
  for(int bits=0;bits<(1<<r);bits++){int z=0;for(int j=0;j<r;j++)z+=(bits>>j&1)?1:-1;counts[mod(z)]++;}
  for(int c:counts)if(abs(3*c-(1<<r))>2)throw runtime_error("exact F3 Fourier bound");
  if(r>1)out<<",";
  out<<"{\"nonzero_switches\":"<<r<<",\"counts\":["<<counts[0]<<","<<counts[1]<<","<<counts[2]<<"]}";
 }
 // If zero differences are incorrectly counted as ten active switches, the claimed
 // integer discrepancy bound 2 fails: the sum is constant on all 1024 choices.
 int zero_count=0;array<bool,2> parity_values{};
 for(int bits=0;bits<(1<<10);bits++){
  int zero_sum=0,parity_sum=0;
  for(int j=0;j<10;j++){int sign=(bits>>j&1)?1:-1;zero_sum+=sign*0;parity_sum+=sign;}
  zero_count+=(zero_sum==0);parity_values[(parity_sum%2+2)%2]=true;
 }
 bool zero_rejected=abs(3*zero_count-(1<<10))>2;
 int parity_distinct_values=(int)parity_values[0]+(int)parity_values[1];
 if(!zero_rejected||parity_distinct_values!=1)throw runtime_error("controls");
 out<<"],\"off_diagonal_square_rank\":"<<nonlinear_rank<<",\"coordinate_basis_negative_control_rank\":"<<identity_nonlinear_rank<<",\"zero_difference_control_rejected\":true,\"F2_sign_switch_distinct_values\":1,\"scope\":\"Exact finite code, rectangle-incidence and scalar Fourier checks; not a universal rank condenser\"}\n";
 cout<<"Code min weight "<<minweight<<", disjoint rectangle witness "<<minrect<<"; "<<rectangles<<" rectangles satisfy the four-block bound. Ten signed-sum checks passed.\n";
}
