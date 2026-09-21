// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact Boolean F2 degree-filtered NS/PC test for two accuracy-two copies.
// Heavy loops are compiled; use compute.sh. No PHP axioms are imposed.
#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using Mask=uint32_t;
using Poly=std::set<Mask>;
using Row=std::vector<uint64_t>;
static void need(bool b,const std::string& s){if(!b)throw std::runtime_error(s);}
static int wt(Mask m){return __builtin_popcount(m);}
static void toggle(Poly& p,Mask m){if(!p.erase(m))p.insert(m);}
static Poly add(Poly a,const Poly& b){for(auto m:b)toggle(a,m);return a;}
static Poly mul(const Poly& a,const Poly& b){Poly c;for(auto x:a)for(auto y:b)toggle(c,x|y);return c;}
static Poly var(int i){return {Mask(1)<<i};}
static int degree(const Poly& p){int d=0;for(auto m:p)d=std::max(d,wt(m));return d;}
struct Block{Poly p;std::vector<Poly> cof;};
// p = 1 + sum_i cof[i]*x_i, by prefix expansion; all arrays Boolean-reduced.
static Block block(int r,int h,int& next){
  Block b{{0},std::vector<Poly>(r)};
  for(int u=0;u<h;++u){Poly factor{0};
    for(int i=0;i<r;++i){Poly c=var(next++);b.cof[i]=add(b.cof[i],mul(b.p,c));factor=add(factor,mul(c,var(i)));}
    b.p=mul(b.p,factor);
  }return b;
}
struct Space{
  int n,D,W;std::vector<Mask> col;std::vector<int> index;
  std::map<int,Row> basis;std::vector<int> queue;size_t done=0;uint64_t insertions=0,multiplications=0;
  Space(int nv,int d):n(nv),D(d),index(size_t(1)<<nv,-1){
    need(n<=20 && D<=6,"enumeration cap: at most 20 variables and degree 6");
    for(int k=D;k>=0;--k)for(Mask m=0;m<(Mask(1)<<n);++m)if(wt(m)==k){index[m]=int(col.size());col.push_back(m);}
    W=int((col.size()+63)/64);
    uint64_t worst=uint64_t(col.size())*W*8;
    need(worst<600000000,"basis memory cap exceeded");
    std::cout<<"n="<<n<<" D="<<D<<" columns="<<col.size()<<" worst_dense_basis_bytes="<<worst<<std::endl;
  }
  static int lead(const Row& r){for(size_t w=0;w<r.size();++w)if(r[w])return int(64*w+__builtin_ctzll(r[w]));return -1;}
  Row vec(const Poly& p)const{Row r(W);for(auto m:p){int i=index.at(m);need(i>=0,"polynomial outside degree window");r[i/64]^=uint64_t(1)<<(i%64);}return r;}
  Row reduce(Row r)const{for(;;){int p=lead(r);auto it=basis.find(p);if(p<0||it==basis.end())return r;for(int w=p/64;w<W;++w)r[w]^=it->second[w];}}
  void insert(Row r){++insertions;r=reduce(std::move(r));int p=lead(r);if(p<0)return;basis.emplace(p,std::move(r));if(wt(col[p])<D)queue.push_back(p);}
  bool contains(const Poly& p)const{return lead(reduce(vec(p)))<0;}
  Row times(const Row& a,int v)const{Row b(W);for(int w=0;w<W;++w){uint64_t t=a[w];while(t){int i=64*w+__builtin_ctzll(t);t&=t-1;int j=index[col[i]|(Mask(1)<<v)];need(j>=0,"illegal PC multiplication");b[j/64]^=uint64_t(1)<<(j%64);}}return b;}
  void close(){while(done<queue.size()){int p=queue[done++];const Row& row=basis.at(p);for(int v=0;v<n;++v){++multiplications;insert(times(row,v));}}}
  static int dot(const Row&a,const Row&b){int p=0;for(size_t w=0;w<a.size();++w)p^=__builtin_parityll(a[w]&b[w]);return p;}
  Row dual(const Poly& p)const{Row rem=reduce(vec(p)),d(W);int f=lead(rem);need(f>=0,"cannot separate member");d[f/64]|=uint64_t(1)<<(f%64);
    for(auto it=basis.rbegin();it!=basis.rend();++it)if(dot(it->second,d))d[it->first/64]^=uint64_t(1)<<(it->first%64);
    need(dot(d,vec(p))==1,"dual target pairing");for(auto& kv:basis)need(dot(d,kv.second)==0,"dual basis pairing");return d;
  }
  void write_dual(std::ostream&o,const Poly&p)const{auto d=dual(p);o<<'[';bool comma=false;for(size_t i=0;i<col.size();++i)if((d[i/64]>>(i%64))&1){if(comma)o<<',';comma=true;o<<col[i];}o<<']';}
};
static void write_poly(std::ostream&o,const Poly&p){o<<'[';bool comma=false;for(auto m:p){if(comma)o<<',';comma=true;o<<m;}o<<']';}
int main(int argc,char**argv){try{
  need(argc==5&&std::string(argv[1])=="--rank"&&std::string(argv[3])=="--out","usage: --rank 3|4 --out NEW_PATH");
  int r=std::stoi(argv[2]);need(r==3||r==4,"rank must be 3 or 4");need(!std::filesystem::exists(argv[4]),"refusing overwrite");
  int next=r;Block P=block(r,2,next),Q=block(r,2,next);int n=next;Poly target=add(P.p,Q.p);std::vector<Poly> gens;
  for(auto b:{P,Q})for(int i=0;i<r;++i)gens.push_back(mul(var(i),b.p));
  need(degree(P.p)==4&&degree(Q.p)==4&&degree(target)==4,"product degree");for(auto&g:gens)need(degree(g)==5,"companion degree");
  std::ofstream o(argv[4]);need(bool(o),"cannot open output");o<<"{\"field\":2,\"rank\":"<<r<<",\"accuracy\":2,\"variables\":"<<n<<",\"scope\":\"Boolean domains only, no PHP\",\"variable_order\":\"x[rank], P coefficients row-major [2*rank], Q coefficients row-major [2*rank]\",\"mask_encoding\":\"integer bit i denotes variable i; set lists are F2 monomial supports\",\"P\":";write_poly(o,P.p);o<<",\"Q\":";write_poly(o,Q.p);o<<",\"target\":";write_poly(o,target);o<<",\"original_companion_degree\":5,\"windows\":[";o.flush();
  for(int D:{5,6}){Space sp(n,D);uint64_t multiples=0;
    for(const auto&g:gens)for(auto m:sp.col)if(wt(m)<=D-5){sp.insert(sp.vec(mul(Poly{m},g)));++multiples;}
    size_t nsrank=sp.basis.size();bool ns=sp.contains(target);need(!ns,"analytic NS lower bound contradicted");
    o<<(D==5?"":",")<<"{\"degree\":"<<D<<",\"columns\":"<<sp.col.size()<<",\"ns_multiples\":"<<multiples<<",\"ns_rank\":"<<nsrank<<",\"ns_target\":false,\"ns_dual_support\":";sp.write_dual(o,target);o.flush();
    sp.close();bool pc=sp.contains(target);o<<",\"pc_rank\":"<<sp.basis.size()<<",\"pc_target\":"<<(pc?"true":"false")<<",\"pc_multiplications\":"<<sp.multiplications<<",\"eligible_basis_rows\":"<<sp.queue.size()<<",\"closure_exhausted\":"<<(sp.done==sp.queue.size()?"true":"false");
    if(!pc){o<<",\"pc_dual_support\":";sp.write_dual(o,target);}
    // Independent post-closure invariant check; only eligible rows may multiply.
    for(int p:sp.queue)for(int v=0;v<n;++v)need(Space::lead(sp.reduce(sp.times(sp.basis.at(p),v)))<0,"PC closure verification");
    o<<",\"closure_verified\":true}";o.flush();std::cout<<"NS rank="<<nsrank<<" PC rank="<<sp.basis.size()<<" P+Q NS="<<ns<<" PC="<<pc<<std::endl;
  }
  // Explicit helper identity P+Q = P(1+R)+R(1+P)+Q(1+R)+R(1+Q).
  Block R=block(r,1,next);Poly sum;int ceiling=0;o<<"],\"helper\":{\"accuracy\":1,\"coefficients_start\":"<<n<<",\"cofactors\":[";
  for(int i=0;i<r;++i){Poly s=var(n+i),c=add(P.cof[i],Q.cof[i]);sum=add(sum,mul(s,mul(var(i),target)));sum=add(sum,mul(c,mul(var(i),R.p)));ceiling=std::max({ceiling,degree(s)+5,degree(c)+3});if(i)o<<',';write_poly(o,c);}
  need(sum==target&&ceiling==6,"helper degree-six certificate");o<<"],\"certificate_degree\":6,\"identity_verified\":true}}\n";
  need(bool(o),"output failure");return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
