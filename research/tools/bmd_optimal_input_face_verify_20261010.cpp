// Exact n9,p5 optimal transfer-face audit using FLINT ordered RREF.
// All supported high identity columns have weight >=25, every transfer <=21.
// Thus any term attaining U(-26) uses only the twelve supported inputs <=13.
// Enumerate all 165 possible nine-input sets containing zero, all 48 omissions.
#include <flint/nmod_mat.h>
#include <algorithm>
#include <iostream>
#include <numeric>
#include <vector>
using V=std::vector<long>;
std::vector<V> subsets;
void choose(const V&s,int pos,int left,V j){if(!left){subsets.push_back(j);return;}for(int i=pos;i+left<=(int)s.size();++i){V q=j;q.push_back(s[i]);choose(s,i+1,left-1,q);}}
void show(const V&v){std::cout<<"[";for(size_t i=0;i<v.size();++i)std::cout<<(i?", ":"")<<v[i];std::cout<<"]";}
V pivots(const std::vector<V>&cols,int rows){nmod_mat_t A;nmod_mat_init(A,rows,cols.size(),5);for(size_t j=0;j<cols.size();++j)for(int i=0;i<rows;++i)nmod_mat_entry(A,i,j)=cols[j][i];long rank=nmod_mat_rref(A);V out;for(int i=0;i<rank;++i){size_t j=0;while(j<cols.size()&&!nmod_mat_entry(A,i,j))++j;if(j==cols.size())abort();out.push_back(j);}nmod_mat_clear(A);return out;}
int main(){V b(48);b[0]=1;for(int k=1;k<48;++k){long a=(k==1?1:0);for(int i=1;i<k;++i)a-=b[i]*b[k-i];b[k]=((a%5+5)%5)*3%5;}V gamma;for(int j=0;j<48;++j)if(b[j])gamma.push_back(j);long sum=std::accumulate(gamma.begin(),gamma.end(),0L);V low;for(long j:gamma)if(j&&j<25)low.push_back(j);choose(low,0,8,V{0});if(subsets.size()!=165)abort();
for(int omitted=0;omitted<48;++omitted){std::vector<V> cols;V weights;for(size_t i=1;i<gamma.size();++i){V v(gamma.size());v[i]=1;cols.push_back(v);weights.push_back(gamma[i]);}for(int k=0;k<48;++k)if(k!=omitted){V v;for(long j:gamma)v.push_back(k>=j?b[k-j]:0);cols.push_back(v);weights.push_back(k-26);}V order(cols.size());std::iota(order.begin(),order.end(),0);std::stable_sort(order.begin(),order.end(),[&](long i,long j){return weights[i]>weights[j];});std::vector<V> sorted;for(long i:order)sorted.push_back(cols[i]);V basis=pivots(sorted,gamma.size());if(basis.size()!=gamma.size())abort();long w=0;for(long i:basis)w+=weights[order[i]];long upper=w-sum+26*9;std::cout<<"BOUND omit="<<omitted<<" weight="<<w<<" upper="<<upper<<"\n";long hits=0,best=-1;
for(const V&J:subsets){V ks;std::vector<V>A;for(int k=47;k>=0;--k)if(k!=omitted){ks.push_back(k);V v;for(long j:J)v.push_back(k>=j?b[k-j]:0);A.push_back(v);}V pc=pivots(A,9);if(pc.size()!=9)abort();V K;long d=-std::accumulate(J.begin(),J.end(),0L);for(long i:pc){K.push_back(ks[i]);d+=ks[i];}std::sort(K.begin(),K.end());best=std::max(best,d);if(d>upper)abort();if(d==upper){++hits;nmod_mat_t M;nmod_mat_init(M,9,9,5);for(int i=0;i<9;++i)for(int k=0;k<9;++k)nmod_mat_entry(M,i,k)=K[k]>=J[i]?b[K[k]-J[i]]:0;long scalar=nmod_mat_det(M);nmod_mat_clear(M);if(!scalar)abort();std::cout<<"OPT omit="<<omitted<<" J=";show(J);std::cout<<" K=";show(K);std::cout<<" degree="<<d<<" scalar="<<scalar<<"\n";}}
std::cout<<"SUMMARY omit="<<omitted<<" inputs=165 hits="<<hits<<" best="<<best<<"\n";
}std::cout<<"FLINT_OPTIMAL_INPUT_FACE_COMPLETED\n";}
