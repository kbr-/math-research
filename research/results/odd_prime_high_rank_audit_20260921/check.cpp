#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <vector>
int mod(int a,int p){a%=p;return a<0?a+p:a;}
int rank(std::vector<std::vector<int>> a,int p){int n=int(a.size()),r=0;for(int c=0;c<n;c++){int k=r;while(k<n&&!a[k][c])k++;if(k==n)continue;std::swap(a[k],a[r]);int inv=1;while(mod(inv*a[r][c],p)!=1)inv++;for(int j=c;j<n;j++)a[r][j]=mod(a[r][j]*inv,p);for(int i=r+1;i<n;i++){int z=a[i][c];if(z)for(int j=c;j<n;j++)a[i][j]=mod(a[i][j]-z*a[r][j],p);}r++;if(r==n)break;}return r;}
using Poly=std::array<int,64>;
Poly mul(const Poly&a,const Poly&b,int p){Poly c{};for(int i=0;i<64;i++)if(a[i])for(int j=0;j<64;j++)if(b[j]&&!(i&j))c[i|j]=mod(c[i|j]+a[i]*b[j],p);return c;}
int main(int argc,char**argv){if(argc!=2)return 1;const int groups=3,block=38,n=groups*block;std::ofstream out(argv[1]);out<<"{\"groups\":3,\"block_size\":38,\"variables\":114,\"required_rank\":36,\"combinations\":[";int minrank=n;bool first=true;std::cout<<"26 matrices of order 114; six-variable square-zero controls only.\n";
for(int code=1;code<27;code++){int t=code;std::array<int,3> c{};for(int&i:c){i=t%3;t/=3;}std::vector<int>a(n);for(int i=0;i<n;i++)a[i]=c[i/block];std::vector<std::vector<int>> raw(n,std::vector<int>(n)),red=raw;for(int i=0;i<n;i++)for(int j=0;j<n;j++){raw[i][j]=mod(a[i]+a[j],3);red[i][j]=mod(a[i]+a[j]-(i==j?2*a[i]:0),3);}int rr=rank(raw,3),rb=rank(red,3);if(rr>2||rb<36)return 2;minrank=std::min(minrank,rb);if(!first)out<<",";first=false;out<<"{\"coefficients\":["<<c[0]<<","<<c[1]<<","<<c[2]<<"],\"raw_polar_rank\":"<<rr<<",\"Boolean_reduced_polar_rank\":"<<rb<<"}";}
out<<"],\"minimum_reduced_rank\":"<<minrank<<",\"square_zero_controls\":[";
for(int p:{3,5}){Poly L{};for(int j=0;j<6;j++)L[1<<j]=1;Poly product{};product[0]=1;for(int i=0;i<3;i++){Poly Li{};Li[1<<(2*i)]=Li[1<<(2*i+1)]=1;product=mul(product,mul(L,Li,p),p);}int count=0;for(int z:product)count+=z!=0;if((p==3&&count)||(p==5&&count==0))return 3;if(p==5)out<<",";out<<"{\"p\":"<<p<<",\"nonzero_product_terms\":"<<count<<",\"full_support_coefficient\":"<<product[63]<<"}";}
out<<"],\"passed\":true,\"scope\":\"Exact finite rank and nilpotence controls; the all-parameter and coordinate-change obstruction is proved in the notebook.\"}\n";std::cout<<"Minimum reduced rank "<<minrank<<"; raw rank at most two; characteristic-three product zero and characteristic-five control nonzero.\n";return 0;}
