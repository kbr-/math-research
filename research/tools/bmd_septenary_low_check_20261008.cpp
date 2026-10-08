// Independently reconstruct all original n9 p7 low-degree matrices using Givaro and FFPACK.
#include <givaro/gfq.h>
#include <fflas-ffpack/fflas-ffpack.h>
#include <fstream>
#include <iostream>
#include <vector>
#include <stdexcept>
using Field=Givaro::GFqDom<int64_t>;using E=Field::Element;
void ck(bool b,const char*s){if(!b)throw std::runtime_error(s);}
int rank(const Field&F,std::vector<E>A,int N){std::vector<size_t>P(N),Q(N);return FFPACK::LUdivine_gauss(F,FFLAS::FflasNonUnit,N,N,A.data(),N,P.data(),Q.data());}
int lucas(int n,int k){int v=1;while(n||k){int r=n%7,s=k%7;if(s>r)return 0;int b=1;for(int i=1;i<=s;i++)b=b*(r-i+1)/i;v=v*b%7;n/=7;k/=7;}return v;}
int main(int argc,char**argv){try{ck(argc==2,"input required");std::ifstream in(argv[1]);int f;in>>f;ck(f==2,"field degree");std::vector<int64_t>mod(3);for(auto&x:mod)in>>x;Field F(7,2,mod);std::vector<E>sl(9);for(auto&x:sl){int c;in>>c;x=F.padic2zech(c);}std::vector<std::vector<E>>add(49,std::vector<E>(49)),mul=add;for(int i=0;i<49;i++)for(int j=0;j<49;j++){F.add(add[i][j],i,j);F.mul(mul[i][j],i,j);}
 auto prefixes=[&](const std::vector<E>&labels,int N){std::vector<std::vector<E>>roots(9,std::vector<E>(N,F.zero)),co(512,std::vector<E>(N,F.zero));for(int i=0;i<9;i++){E power=F.one;for(int j=0;j<N;j++){roots[i][j]=mul[F.padic2zech(lucas(1201,j))][power];power=mul[power][labels[i]];}for(int k=0;k<N;k++){E v=F.zero;for(int j=0;j<=k;j++)v=add[v][mul[roots[i][j]][roots[i][k-j]]];ck(v==(k==0?F.one:k==1?labels[i]:F.zero),"independent root-square identity");}}co[0][0]=F.one;for(int s=1;s<512;s++)if(__builtin_popcount((unsigned)s)<=6){int bit=__builtin_ctz((unsigned)s),parent=s^(1<<bit);for(int j=0;j<N;j++)if(roots[bit][j]!=F.zero)for(int k=0;k<N-j;k++)if(co[parent][k]!=F.zero)co[s][j+k]=add[co[s][j+k]][mul[roots[bit][j]][co[parent][k]]];}return co;};
 auto matrix=[&](const std::vector<std::vector<E>>&co,int d,int N){std::vector<std::pair<int,int>>cols;for(int s=0;s<512;s++)if(__builtin_popcount((unsigned)s)<=d)for(int j=0;2*j+__builtin_popcount((unsigned)s)<=d;j++)cols.push_back({s,j});ck((int)cols.size()==N,"complete original source count");std::vector<E>A(N*N,F.zero);for(int j=0;j<N;j++)for(int i=cols[j].second;i<N;i++)A[i*N+j]=co[cols[j].first][i-cols[j].second];return A;};
 auto co=prefixes(sl,769);for(int d=2;d<=6;d++){int dd,N,det;in>>dd>>N>>det;ck(dd==d&&det>0,"retained nonzero PARI determinant");int r=rank(F,matrix(co,d,N),N);ck(r==N,"independent original rank");std::cout<<"ORIGINAL d="<<d<<" rank="<<r<<"\n";}sl[8]=sl[7];auto bad=prefixes(sl,47);ck(rank(F,matrix(bad,2,47),47)<47,"duplicate-root negative control");std::cout<<"COMPLETE all five original low degrees independently full rank; negative control passed.\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}return 0;}
