// Exact support test for the degree-two cofactor expansion, not a rank certificate.
// For each omitted output j>=2, maximize sum(K)-sum(J), with 0 in J,
// J in the nonzero square-root coefficient support, K avoiding 0,1,j,
// and det(binomial(1/2,k-i))_(i in J,k in K) nonzero modulo p.
// E-minors may still vanish or cancel; the result is only an upper bound.
#include <flint/nmod_mat.h>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <numeric>
#include <vector>
#include <functional>
using V=std::vector<long>;
long sum(const V&v){return std::accumulate(v.begin(),v.end(),0L);}
void vec(std::ostream&o,const V&v){o<<'[';for(size_t i=0;i<v.size();++i){if(i)o<<',';o<<v[i];}o<<']';}
void choose(const V&a,long count,const std::function<void(const V&)>&f){V v;std::function<void(size_t)> rec=[&](size_t i){if((long)v.size()==count){f(v);return;}for(size_t k=i;k+count-v.size()<=a.size();++k){v.push_back(a[k]);rec(k+1);v.pop_back();}};rec(0);}
V coefficients(long m,long p){long q=p;while(q<=m)q*=p;long alpha=(q+1)/2;V b(m+1);for(long k=0;k<=m;++k){long a=alpha,t=k,z=1;while(t||a){long u=a%p,v=t%p;if(v>u){z=0;break;}long c=1;for(long i=1;i<=v;++i)c=c*(u-i+1)/i;z=z*(c%p)%p;a/=p;t/=p;}b[k]=z;}return b;}
long entry(const V&b,long i,long k){return k<i?0:b[k-i];}
struct Choice{V J,K;};
struct Result{long n,p,m,s,candidates=0,rrefs=0;V b,allowed,best;std::vector<std::vector<Choice>> choices;};
Result solve(long n,long p,bool brute){long s=n,r=n*(n-1)/2+2,m=r+s;Result out{n,p,m,s};out.b=coefficients(m,p);V positive;for(long i=0;i<=m;++i)if(out.b[i]){out.allowed.push_back(i);if(i)positive.push_back(i);}out.best=V(m+1,-100000);out.choices.resize(m+1);
choose(positive,s-1,[&](const V&tail){V J{0};J.insert(J.end(),tail.begin(),tail.end());++out.candidates;
for(long omit=2;omit<=m;++omit){V outputs;for(long k=m;k>=2;--k)if(k!=omit)outputs.push_back(k);nmod_mat_t a;nmod_mat_init(a,s,outputs.size(),p);for(long i=0;i<s;++i)for(size_t k=0;k<outputs.size();++k)nmod_mat_entry(a,i,k)=entry(out.b,J[i],outputs[k]);long rank=nmod_mat_rref(a);++out.rrefs;V K;if(rank==s){for(long i=0;i<s;++i){long k=0;while(k<(long)outputs.size()&&!nmod_mat_entry(a,i,k))++k;if(k==(long)outputs.size())abort();K.push_back(outputs[k]);}std::sort(K.begin(),K.end());}nmod_mat_clear(a);
if(brute){V ascending=outputs;std::sort(ascending.begin(),ascending.end());long largest=-100000;V BK;choose(ascending,s,[&](const V&cand){nmod_mat_t t;nmod_mat_init(t,s,s,p);for(long i=0;i<s;++i)for(long k=0;k<s;++k)nmod_mat_entry(t,i,k)=entry(out.b,J[i],cand[k]);if(nmod_mat_det(t)&&sum(cand)>largest){largest=sum(cand);BK=cand;}nmod_mat_clear(t);});if((rank==s)!=(largest>-100000)||(rank==s&&K!=BK)){std::cerr<<"brute control failed\n";exit(2);}}
if(rank==s){long value=sum(K)-sum(J);if(value>out.best[omit]){out.best[omit]=value;out.choices[omit].clear();}if(value==out.best[omit])out.choices[omit].push_back({J,K});}}
});return out;}
void emit(std::ostream&o,const Result&r){o<<"{\"n\":"<<r.n<<",\"p\":"<<r.p<<",\"m\":"<<r.m<<",\"input_sets\":"<<r.candidates<<",\"rrefs\":"<<r.rrefs<<",\"support\":";vec(o,r.allowed);o<<",\"cofactors\":[";for(long j=2;j<=r.m;++j){if(j>2)o<<',';o<<"{\"omit\":"<<j<<",\"bound\":"<<r.best[j]<<",\"maximizers\":[";for(size_t k=0;k<r.choices[j].size();++k){if(k)o<<',';o<<"{\"J\":";vec(o,r.choices[j][k].J);o<<",\"K\":";vec(o,r.choices[j][k].K);o<<'}';}o<<"]}";}o<<"]}";}
int main(int argc,char**argv){if(argc!=3){std::cerr<<"usage: binary control|target OUT\n";return 2;}std::ofstream out(argv[2]);if(!out)return 2;std::string mode=argv[1];if(mode=="control"){out<<'[';emit(out,solve(2,3,true));out<<',';emit(out,solve(3,3,true));out<<"]\n";std::cout<<"PASS: all greedy output choices match exhaustive FLINT determinant controls at n=2,3, p=3\n";}else if(mode=="target"){auto r=solve(7,3,false);emit(out,r);out<<'\n';std::cout<<"PASS: n=7,p=3; input sets="<<r.candidates<<"; RREFs="<<r.rrefs<<"\n";for(long j=2;j<=r.m;++j)std::cout<<"omit="<<j<<" bound="<<r.best[j]<<" maximizing_pairs="<<r.choices[j].size()<<'\n';}else return 2;}
