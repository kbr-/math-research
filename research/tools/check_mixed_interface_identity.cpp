// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Hand-built mixed-interface NS certificates; no matrix search or Boolean-degree reset.
#include "sparse_polynomial.hpp"
#include <fstream>
#include <iostream>
#include <string>
using namespace sparse_polynomial;
using P=Polynomial;
Ring ring(2,32);
P plus(const P&a,const P&b){return ring.add(a,b);}
P times(const P&a,const P&b){return ring.multiply(a,b);}
P one=ring.constant(1);
void need(bool b,const char*s){if(!b)throw std::runtime_error(s);}
P prod(const std::vector<P>&z,int from=0){P p=one;for(int i=from;i<int(z.size());++i)p=times(p,z[i]);return p;}
std::vector<P> complements(const std::vector<P>&z){auto p=z;for(auto&x:p)x=plus(one,x);return p;}
P cor(const std::vector<P>&z){return plus(one,prod(complements(z)));}
P suffix(const std::vector<P>&z,int i){return prod(complements(z),i+1);}
P hybrid(const std::vector<P>&left,const std::vector<P>&right,int i){P p=one;for(int j=0;j<int(left.size());++j)if(j!=i)p=times(p,plus(one,j<i?left[j]:right[j]));return p;}
void addto(P&a,const P&b){ring.accumulate(a,b);}
struct Fixture {
 int r,n;std::vector<P>x,y,a,b,s,g,gens;std::vector<int>cost;P u,v,L,K,A,B,E,G,c,d,e,U,V,S,F,Q,target;std::vector<P>q;
 explicit Fixture(int rank):r(rank),n(5*r+2){
  for(int i=0;i<r;++i){x.push_back(ring.variable(i));y.push_back(ring.variable(r+i));a.push_back(ring.variable(2*r+i));b.push_back(ring.variable(3*r+i));s.push_back(ring.variable(4*r+2+i));g.push_back(plus(x[i],y[i]));}
  u=ring.variable(4*r);v=ring.variable(4*r+1);S=plus(u,v);G=one;
  for(int i=0;i<r;++i){addto(L,times(a[i],x[i]));addto(K,times(b[i],y[i]));addto(U,times(a[i],g[i]));addto(V,times(b[i],g[i]));addto(G,times(s[i],g[i]));}
  A=plus(one,L);B=plus(one,K);E=plus(one,plus(times(u,L),times(v,K)));
  c=cor(x);d=cor(y);e=cor(g);F=plus(prod(g),plus(prod(x),prod(y)));target=times(E,F);
  Q=plus(plus(c,plus(d,e)),times(S,plus(e,plus(times(B,U),times(A,V)))));
  for(int i=0;i<r;++i)q.push_back(plus(plus(hybrid(x,y,i),suffix(g,i)),times(S,plus(suffix(g,i),plus(times(a[i],B),times(b[i],A))))));
  for(int i=0;i<r;++i){gens.push_back(times(x[i],A));cost.push_back(3);}
  for(int i=0;i<r;++i){gens.push_back(times(y[i],B));cost.push_back(3);}
  gens.push_back(times(L,E));cost.push_back(5);gens.push_back(times(K,E));cost.push_back(5);
  for(int i=0;i<r;++i){gens.push_back(times(g[i],G));cost.push_back(3);}
 }
 std::vector<P> blank()const{return std::vector<P>(gens.size());}
 std::vector<P> annihilator(int j)const{
  auto z=blank();
  addto(z[r+j],times(S,U));addto(z[j],times(S,B));
  addto(z[j],times(S,V));addto(z[r+j],times(S,A));
  for(int i=0;i<r;++i){
   addto(z[r+i],times(S,times(a[i],x[j])));addto(z[i],times(S,times(b[i],y[j])));
   addto(z[r+i],times(x[j],suffix(y,i)));addto(z[i],times(y[j],suffix(x,i)));
  }
  addto(z[2*r],y[j]);addto(z[2*r+1],x[j]);
  addto(z[r+j],times(v,L));addto(z[j],times(u,K));return z;
 }
 // A certificate for E times any old-only polynomial with zero constant term.
 std::vector<P> kill_old(const P&H)const{
  auto z=blank();
  for(const auto&[m,c0]:H){need(!m.empty()&&c0==1,"old polynomial must have zero constant");int j=m.front();need(j<2*r,"old polynomial has a coefficient variable");auto rest=m;rest.erase(rest.begin());P f={{rest,1}};
   addto(z[j],times(E,f));addto(z[2*r+(j>=r)],times(ring.variable(j),f));
  }return z;
 }
 std::vector<P> difference()const{
  auto z=kill_old(plus(F,plus(c,plus(d,e))));
  for(int i=0;i<r;++i){
   addto(z[i],plus(times(u,hybrid(g,y,i)),plus(times(v,suffix(x,i)),times(S,b[i]))));
   addto(z[r+i],plus(times(v,hybrid(g,x,i)),plus(times(u,suffix(y,i)),times(S,a[i]))));
  }return z;
 }
};
struct Checked{P residual;std::vector<P>boolean;int ceiling=0;};
Checked check(const Fixture&f,const P&target,const std::vector<P>&cof){
 Checked c;c.boolean.resize(f.n);P work=target;
 for(size_t i=0;i<cof.size();++i)if(!cof[i].empty()){addto(work,times(cof[i],f.gens[i]));c.ceiling=std::max(c.ceiling,degree(cof[i])+f.cost[i]);}
 while(!work.empty()){
  auto it=std::prev(work.end());auto m=it->first;work.erase(it);auto repeat=std::adjacent_find(m.begin(),m.end());
  if(repeat==m.end()){ring.accumulate(c.residual,P{{m,1}});continue;}
  int id=*repeat;auto pos=repeat-m.begin();auto rest=m;rest.erase(rest.begin()+pos,rest.begin()+pos+2);
  addto(c.boolean[id],P{{rest,1}});m.erase(m.begin()+pos);addto(work,P{{m,1}});
 }
 P reconstruction=c.residual;
 for(int i=0;i<f.n;++i)if(!c.boolean[i].empty()){
  P z=ring.variable(i);addto(reconstruction,times(c.boolean[i],plus(times(z,z),z)));c.ceiling=std::max(c.ceiling,degree(c.boolean[i])+2);
 }
 for(size_t i=0;i<cof.size();++i)addto(reconstruction,times(cof[i],f.gens[i]));
 need(reconstruction==target,"ordinary reconstruction failed");return c;
}
void polynomials(std::ostream&o,const std::vector<P>&v){o<<'[';for(size_t i=0;i<v.size();++i){if(i)o<<',';write_json(o,v[i]);}o<<']';}
int main(int argc,char**argv)try{
 need(argc==3&&std::string(argv[1])=="--out","usage: --out FILE");std::ifstream old(argv[2]);need(!old.good(),"refusing overwrite");
 std::cout<<"Bounded ranks 3,4,5; at most 27 variables and degree 10; sparse exact identities, no assignment or matrix enumeration.\n";
 std::ofstream out(argv[2]);need(bool(out),"cannot open output");out<<"{\"encoding\":\"[coefficient,[sorted variable ids with repetition]] over F2; ids x,y,a,b in rank-sized groups, then u,v, then s\",\"scope\":\"explicit certificates only, no least-degree or general-conservativity assertion\",\"cases\":[";
 int total=0;
 for(int r:{3,4,5}){
  Fixture f(r);if(r!=3)out<<',';out<<"{\"rank\":"<<r<<",\"variables\":"<<f.n<<",\"generators\":";polynomials(out,f.gens);out<<",\"generator_costs\":[";
  for(size_t i=0;i<f.cost.size();++i){if(i)out<<',';out<<f.cost[i];}out<<"],\"input_cofactors\":";polynomials(out,f.q);
  P sum;for(int i=0;i<r;++i)addto(sum,times(f.q[i],f.g[i]));need(sum==f.Q,"Q input identity failed");
  auto diff=f.difference(),aug=diff;for(int i=0;i<r;++i){addto(aug[2*r+2+i],f.q[i]);auto z=f.annihilator(i);for(size_t j=0;j<z.size();++j)addto(aug[j],times(f.s[i],z[j]));}
  out<<",\"certificates\":[";bool comma=false;
  auto emit=[&](const std::string&name,const P&t,const std::vector<P>&z,int budget){Checked c=check(f,t,z);need(c.residual.empty(),"nonzero Boolean remainder");need(c.ceiling<=budget,"certificate degree exceeded");if(comma)out<<',';comma=true;
   out<<"{\"name\":\""<<name<<"\",\"budget\":"<<budget<<",\"actual_ceiling\":"<<c.ceiling<<",\"target\":";write_json(out,t);out<<",\"companion_cofactors\":";polynomials(out,z);out<<",\"boolean_cofactors\":";polynomials(out,c.boolean);out<<'}';++total;};
  for(int i=0;i<r;++i)emit("input-annihilator-"+std::to_string(i),times(f.g[i],f.Q),f.annihilator(i),std::max(r+3,6));
  emit("target-difference",plus(f.target,f.Q),diff,r+4);emit("augmented-target",f.target,aug,r+4);emit("retained-target",f.target,f.kill_old(f.F),r+5);
  auto wrong=aug;auto z=f.annihilator(0);for(size_t j=0;j<z.size();++j)addto(wrong[j],times(f.s[0],z[j]));auto control=check(f,f.target,wrong);need(!control.residual.empty(),"omitted annihilator not detected");
  auto exact=check(f,f.target,aug);need(exact.ceiling>r+3,"undercharged budget control failed");
  out<<"],\"omitted_annihilator_remainder\":";write_json(out,control.residual);out<<",\"undercharged_budget_rejected\":true}";
  std::cout<<"rank "<<r<<": "<<r+3<<" certificates reconstructed, ceilings "<<r+4<<"/"<<r+5<<", both controls detected\n";
 }
 out<<"],\"certificates_verified\":"<<total<<",\"all_passed\":true}\n";need(bool(out),"output failed");
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
