// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact ordinary NS certificates for one-level balanced-minimum ENS sources.
#include "sparse_polynomial.hpp"
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <string>
using namespace sparse_polynomial;
using P=Polynomial;
using Certificate=std::map<int,P>;
void need(bool b,const char*s){if(!b)throw std::runtime_error(s);}
struct Block{P value;std::map<int,P>prefix;std::map<int,int>companion;};
struct Node{std::vector<int>vertices;std::map<int,Block>blocks;P sum;Certificate partition;};
struct Case{
 Ring ring;int h,next=0;P one;std::map<std::pair<int,int>,int>variables,booleans;
 std::vector<P>generators;std::vector<int>costs;std::vector<std::string>names;
 std::vector<int>fresh_variables;std::map<std::tuple<int,int,int>,int>triangles;
 std::map<int,int>minimum;std::map<int,std::vector<int>>neighbors;
 struct Record{std::string name;P target;Certificate cof;int budget;};std::vector<Record>records;
 explicit Case(int p,int accuracy):ring(p,32),h(accuracy),one(ring.constant(1)){
  for(int i=0;i<4;++i)for(int j=i+1;j<4;++j)variables[{i,j}]=next++;
  for(auto [pair,id]:variables){P x=ring.variable(id);booleans[pair]=axiom(sub(mul(x,x),x),2,"old-Boolean");}
  for(int i=0;i<4;++i)for(int j=i+1;j<4;++j)for(int k=j+1;k<4;++k){
   triangles[{i,j,k}]=axiom(mul(t(i,j),mul(t(j,k),t(k,i))),3,"cyclic-order");
   triangles[{i,k,j}]=axiom(mul(t(i,k),mul(t(k,j),t(j,i))),3,"cyclic-order");
  }
  neighbors={{0,{1}},{1,{0,2}},{2,{1,3}},{3,{2}}};
  for(int i=0;i<4;++i){P f=one;for(int j:neighbors[i])f=mul(f,t(i,j));minimum[i]=axiom(f,int(neighbors[i].size()),"no-local-minimum");}
 }
 P add(const P&a,const P&b)const{return ring.add(a,b);}P sub(const P&a,const P&b)const{return ring.subtract(a,b);}P mul(const P&a,const P&b)const{return ring.multiply(a,b);}
 P t(int i,int j)const{need(i!=j,"diagonal order literal");auto pair=std::minmax(i,j);P x=ring.variable(variables.at(pair));return i<j?x:sub(one,x);}
 P g(int i,int j)const{return sub(one,t(i,j));}
 int axiom(const P&p,int cost,const std::string&name){int id=int(generators.size());generators.push_back(p);costs.push_back(cost);names.push_back(name);return id;}
 void term(Certificate&c,int id,const P&q)const{if(q.empty())return;ring.accumulate(c[id],q);if(c[id].empty())c.erase(id);}
 void combine(Certificate&c,const Certificate&d,const P&q)const{for(auto [id,p]:d)term(c,id,mul(q,p));}
 int triangle(int i,int j,int k)const{std::tuple<int,int,int>a{i,j,k},b{j,k,i},c{k,i,j};return triangles.at(std::min(a,std::min(b,c)));}
 Block block(const std::vector<int>&set,int i){
  Block b;b.value=one;if(set.size()==1)return b;
  for(int row=0;row<h;++row){P factor=one;for(int j:set)if(j!=i){int id=next++;fresh_variables.push_back(id);P r=ring.variable(id);ring.accumulate(b.prefix[j],mul(r,b.value));factor=sub(factor,mul(r,g(i,j)));}b.value=mul(b.value,factor);}
  P prefix_sum;for(auto [j,q]:b.prefix)prefix_sum=add(prefix_sum,mul(q,g(i,j)));need(prefix_sum==sub(one,b.value),"prefix identity failed");
  for(int j:set)if(j!=i)b.companion[j]=axiom(mul(g(i,j),b.value),2*h+1,"minimum-companion");
  return b;
 }
 Certificate compare(const Node&A,const Node&B,const Node&Z,int i,int j)const{
  const auto&X=A.blocks.at(i);const auto&Y=B.blocks.at(j);const auto&W=Z.blocks.at(i);P tij=t(i,j);Certificate c;
  for(auto [l,u]:X.prefix)term(c,W.companion.at(l),mul(u,Y.value));
  term(c,W.companion.at(j),mul(X.value,Y.value));
  for(auto [l,u]:W.prefix){Certificate local;
   if(X.companion.count(l))term(local,X.companion.at(l),mul(tij,Y.value));
   else if(l==j){auto pair=std::minmax(i,j);term(local,booleans.at(pair),sub(P{},mul(X.value,Y.value)));}
   else{
    term(local,Y.companion.at(l),mul(X.value,mul(tij,g(i,l))));
    term(local,triangle(i,j,l),mul(X.value,Y.value));
   }
   combine(c,local,sub(P{},u));
  }return c;
 }
 Node tree(const std::vector<int>&vertices){
  if(vertices.size()==1){Node n;n.vertices=vertices;n.blocks[vertices[0]]=block(vertices,vertices[0]);n.sum=one;return n;}
  size_t m=vertices.size()/2;Node a=tree({vertices.begin(),vertices.begin()+m}),b=tree({vertices.begin()+m,vertices.end()}),z;z.vertices=vertices;
  for(int i:vertices){z.blocks[i]=block(vertices,i);z.sum=add(z.sum,z.blocks[i].value);}
  Certificate merge;
  for(int i:a.vertices)for(int j:b.vertices){
   auto left=compare(a,b,z,i,j),right=compare(b,a,z,j,i);
   records.push_back({"comparison-"+std::to_string(vertices.size())+"-"+std::to_string(i)+"-"+std::to_string(j),sub(mul(z.blocks.at(i).value,b.blocks.at(j).value),mul(t(i,j),mul(a.blocks.at(i).value,b.blocks.at(j).value))),left,6*h+2});
   combine(merge,left,one);combine(merge,right,one);
  }
  P za,zb;for(int i:a.vertices)za=add(za,z.blocks.at(i).value);for(int j:b.vertices)zb=add(zb,z.blocks.at(j).value);
  z.partition=merge;combine(z.partition,b.partition,sub(a.sum,za));combine(z.partition,a.partition,sub(one,zb));
  int height=vertices.size()==2?1:2;records.push_back({"partition-"+std::to_string(vertices.size())+"-"+std::to_string(vertices[0]),sub(z.sum,one),z.partition,(2*height+4)*h+2});return z;
 }
 std::pair<P,int> check(const P&target,const Certificate&cof)const{
  P p;int cost=degree(target);for(auto [id,q]:cof){p=add(p,mul(q,generators.at(id)));cost=std::max(cost,degree(q)+costs.at(id));}return {sub(p,target),cost};
 }
 Certificate refutation(const Node&root){Certificate c;
  for(int i:root.vertices){const auto&b=root.blocks.at(i);term(c,minimum.at(i),b.value);P prefix=one;for(int j:neighbors.at(i)){term(c,b.companion.at(j),prefix);prefix=mul(prefix,t(i,j));}}
  combine(c,root.partition,sub(P{},one));return c;
 }
};
void emit_polys(std::ostream&o,const std::vector<P>&v){o<<'[';for(size_t i=0;i<v.size();++i){if(i)o<<',';write_json(o,v[i]);}o<<']';}
int main(int argc,char**argv)try{
 need(argc==3&&std::string(argv[1])=="--out","usage: --out FILE");std::ifstream old(argv[2]);need(!old.good(),"refusing overwrite");
 std::cout<<"Fixed workload: four ordered vertices, balanced partition tree, path local-minimum axioms; primes 2,3,5 and accuracies 1,2. No search or matrix enumeration.\n";
 std::ofstream out(argv[2]);need(bool(out),"cannot open output");out<<"{\"scope\":\"exact complete-source upper certificates on a four-vertex control, not an expander lower-bound test\",\"encoding\":\"[coefficient,[sorted variable ids with repetition]]; ids and axiom arrays are case-local\",\"cases\":[";
 bool comma=false;int count=0;
 for(int p:{2,3,5})for(int h:{1,2}){
  Case c(p,h);auto root=c.tree({0,1,2,3});auto proof=c.refutation(root);c.records.push_back({"full-refutation",c.one,proof,8*h+2});
  // Complete coefficient field equations are supplied but unnecessary in these identities.
  for(int id:c.fresh_variables){P r=c.ring.variable(id);c.axiom(c.sub(c.ring.power(r,p),r),p,"coefficient-field");}
  if(comma)out<<',';
  comma=true;out<<"{\"prime\":"<<p<<",\"accuracy\":"<<h<<",\"variables\":"<<c.next<<",\"old_pairs\":[";
  bool paircomma=false;for(auto [pair,id]:c.variables){if(paircomma)out<<',';paircomma=true;out<<'['<<pair.first<<','<<pair.second<<','<<id<<']';}out<<"],\"generators\":";emit_polys(out,c.generators);
  out<<",\"generator_costs\":[";for(size_t i=0;i<c.costs.size();++i){if(i)out<<',';out<<c.costs[i];}out<<"],\"certificates\":[";bool reccomma=false;
  for(const auto&r:c.records){auto [residual,cost]=c.check(r.target,r.cof);need(residual.empty(),"ordinary identity failed");need(cost<=r.budget,"original degree budget failed");
   if(reccomma)out<<',';
   reccomma=true;out<<"{\"name\":\""<<r.name<<"\",\"budget\":"<<r.budget<<",\"actual_ceiling\":"<<cost<<",\"target\":";write_json(out,r.target);out<<",\"cofactors\":[";bool cfcomma=false;for(auto [id,q]:r.cof){if(cfcomma)out<<',';cfcomma=true;out<<'['<<id<<',';write_json(out,q);out<<']';}out<<"]}";++count;
  }
  Certificate wrong=proof;bool removed=false;for(auto it=wrong.begin();it!=wrong.end();)if(c.names[it->first]=="cyclic-order"){removed=true;it=wrong.erase(it);}else ++it;
  need(removed,"no transitivity terms to test");auto [bad,unused]=c.check(c.one,wrong);need(!bad.empty(),"omitted transitivity control failed");
  out<<"],\"omitted_transitivity_residual\":";write_json(out,bad);out<<",\"coefficient_fields_unused\":true}";
  std::cout<<"p="<<p<<" h="<<h<<": "<<c.records.size()<<" ordinary certificates and transitivity control passed\n";
 }
 out<<"],\"verified_certificates\":"<<count<<",\"all_passed\":true}\n";need(bool(out),"output failed");
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
