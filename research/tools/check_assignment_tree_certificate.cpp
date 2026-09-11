// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact NS splitting identities and a complete two-variable assignment tree.
#include "ens_symbolic.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace ens_symbolic;
using Cofactors=std::vector<Polynomial>;
void need(bool ok,const std::string& why) {if(!ok)throw std::runtime_error(why);}
void add_cof(const Ring& ring,Cofactors& a,const Cofactors& b) {
    need(a.size()==b.size(),"cofactor dimensions");
    for(size_t i=0;i<a.size();i++)ring.accumulate(a[i],b[i]);
}
void certificate(std::ostream& out,const Ring& ring,const std::string& name,
                 const Polynomial& target,const std::vector<Polynomial>& axioms,
                 const Cofactors& cof,int bound) {
    need(axioms.size()==cof.size(),"certificate dimensions");Polynomial sum;int used=0;
    for(size_t i=0;i<cof.size();i++) {
        auto term=ring.multiply(cof[i],axioms[i]);ring.accumulate(sum,term);used=std::max(used,degree(term));
    }
    need(sum==target && used<=bound,"certificate "+name);
    out<<"{\"record\":\"certificate\",\"name\":\""<<name<<"\",\"target\":";write_json(out,target);
    out<<",\"cofactors\":";write_polynomials(out,cof);out<<",\"degree\":"<<used<<",\"bound\":"<<bound<<"}\n";
}
Block empty_prefix(const Ring& ring,int h) {Block b;b.product=ring.constant(1);b.accuracy=h;return b;}
Cofactors split(const Ring& ring,const Block& A,const Block& B,const Block& C,int x_id,
                size_t count,int a_start,int b_start,int c_start,int boolean_index) {
    auto one=ring.constant(1),x=ring.variable(x_id),q=ring.subtract(one,x);
    int k=int(A.inputs.size());Cofactors cof(count);
    for(int i=0;i<k;i++) {
        ring.accumulate(cof.at(a_start+i),ring.add(ring.multiply(B.prefix[i],q),ring.multiply(C.prefix[i],x)));
        ring.accumulate(cof.at(b_start+i),A.prefix[i],-1);
        ring.accumulate(cof.at(c_start+i),A.prefix[i],-1);
    }
    ring.accumulate(cof.at(b_start+k),A.product,-1);
    ring.accumulate(cof.at(c_start+k),A.product,-1);
    ring.accumulate(cof.at(boolean_index),ring.multiply(A.product,ring.add(B.prefix[k],C.prefix[k])),-1);
    return cof;
}
void point_record(std::ostream& out,const Ring& ring,const std::string& name,
                  const std::vector<Polynomial>& axioms,const std::vector<Polynomial>& fields,
                  const std::map<int,int>& point,const Polynomial& target,int omitted=-1,int expected=0) {
    for(size_t i=0;i<axioms.size();i++)if(int(i)!=omitted)need(ring.evaluate(axioms[i],point)==0,"point axiom "+name);
    for(const auto& f:fields)need(ring.evaluate(f,point)==0,"point field "+name);
    need(ring.evaluate(target,point)==expected,"point target "+name);
    out<<"{\"record\":\"point\",\"name\":\""<<name<<"\",\"omitted_axiom\":"<<omitted
       <<",\"target_value\":"<<expected<<",\"assignment\":[";
    bool comma=false;for(const auto& [id,value]:point) {if(comma)out<<',';comma=true;out<<'['<<id<<','<<value<<']';}
    out<<"]}\n";
}
void local(std::ostream& out,int p,int h,int k) {
    Ring ring(p,64);auto one=ring.constant(1);int next=k+1;
    std::vector<Polynomial> g,axioms,fields;
    for(int i=0;i<k;i++) {auto x=ring.variable(i);g.push_back(i%2?ring.subtract(one,x):x);}
    Block A=k?make_block(ring,g,h,next):empty_prefix(ring,h);
    auto x=ring.variable(k),q=ring.subtract(one,x);auto left=g,right=g;left.push_back(x);right.push_back(q);
    Block B=make_block(ring,left,h,next),C=make_block(ring,right,h,next);
    for(int i=0;i<=k;i++) {auto v=ring.variable(i);axioms.push_back(ring.subtract(ring.multiply(v,v),v));}
    int ai=int(axioms.size());axioms.insert(axioms.end(),A.companions.begin(),A.companions.end());
    int bi=int(axioms.size());axioms.insert(axioms.end(),B.companions.begin(),B.companions.end());
    int ci=int(axioms.size());axioms.insert(axioms.end(),C.companions.begin(),C.companions.end());
    for(int i=k+1;i<next;i++) {auto r=ring.variable(i);fields.push_back(ring.subtract(ring.power(r,p),r));}
    auto target=ring.subtract(ring.subtract(A.product,B.product),C.product);
    auto cof=split(ring,A,B,C,k,axioms.size(),ai,bi,ci,k);
    out<<"{\"record\":\"local_case\",\"p\":"<<p<<",\"accuracy\":"<<h<<",\"prefix_length\":"<<k
       <<",\"A\":";write_block(out,A);out<<",\"B\":";write_block(out,B);out<<",\"C\":";write_block(out,C);
    out<<",\"axioms\":";write_polynomials(out,axioms);out<<",\"unused_field_axioms\":";write_polynomials(out,fields);out<<"}\n";
    certificate(out,ring,"parent_partition",target,axioms,cof,k?4*h+1:2*h+1);
    for(int value:{0,1}) {
        std::map<int,int> point;for(int i=0;i<next;i++)point[i]=0;
        for(int i=0;i<k;i++)point[i]=i%2;
        point[k]=value;
        if(value)point[B.variables[0][k]]=1;else point[C.variables[0][k]]=1;
        need(ring.evaluate(A.product,point)==1 && ring.evaluate(B.product,point)==1-value && ring.evaluate(C.product,point)==value,"partition model values");
        point_record(out,ring,"matching_prefix",axioms,fields,point,target);
    }
    if(k) {
        std::map<int,int> point;for(int i=0;i<next;i++)point[i]=0;
        for(int i=0;i<k;i++)point[i]=i%2;
        point[0]=1;point[A.variables[0][0]]=point[B.variables[0][0]]=point[C.variables[0][0]]=1;
        point_record(out,ring,"mismatching_prefix",axioms,fields,point,target);
    }
    if(p>2) {
        std::map<int,int> point;for(int i=0;i<next;i++)point[i]=0;
        for(int i=0;i<k;i++)point[i]=i%2;
        point[k]=2;int inverse=1;for(int j=0;j<p-2;j++)inverse=inverse*2%p;
        point[B.variables[0][k]]=inverse;point[C.variables[0][k]]=p-1;
        point_record(out,ring,"missing_split_booleanity",axioms,fields,point,target,k,1);
    }
}
void complete(std::ostream& out,int p,int h) {
    Ring ring(p,64);auto one=ring.constant(1);int next=2;
    std::map<std::string,Block> blocks;blocks.emplace("",empty_prefix(ring,h));
    std::vector<std::string> names{"0","1","00","01","10","11"};
    for(const auto& name:names) {
        std::vector<Polynomial> g;
        for(size_t i=0;i<name.size();i++) {auto x=ring.variable(int(i));g.push_back(name[i]=='0'?x:ring.subtract(one,x));}
        blocks.emplace(name,make_block(ring,g,h,next));
    }
    std::vector<Polynomial> axioms;for(int i=0;i<2;i++) {auto x=ring.variable(i);axioms.push_back(ring.subtract(ring.multiply(x,x),x));}
    std::vector<std::string> leaves{"00","01","10","11"};std::map<std::string,int> base,starts;
    for(const auto& leaf:leaves) {
        auto f=one;for(const auto& g:blocks.at(leaf).inputs)f=ring.multiply(f,ring.subtract(one,g));
        base[leaf]=int(axioms.size());axioms.push_back(f);
    }
    for(const auto& name:names) {starts[name]=int(axioms.size());const auto& b=blocks.at(name);axioms.insert(axioms.end(),b.companions.begin(),b.companions.end());}
    out<<"{\"record\":\"complete_case\",\"p\":"<<p<<",\"accuracy\":"<<h
       <<",\"old_boolean_variables\":2,\"base_description\":\"four assignment indicators, all required to be zero\",\"blocks\":[";
    bool comma=false;for(const auto& name:names) {if(comma)out<<',';comma=true;out<<"{\"prefix\":\""<<name<<"\",\"first_companion\":"<<starts.at(name)<<",\"block\":";write_block(out,blocks.at(name));out<<'}';}
    out<<"],\"axioms\":";write_polynomials(out,axioms);out<<"}\n";
    Cofactors total(axioms.size());
    for(const std::string parent:{"","0","1"}) {
        const auto& A=blocks.at(parent);const auto& B=blocks.at(parent+"0");const auto& C=blocks.at(parent+"1");
        int ai=parent.empty()?0:starts.at(parent);
        auto cof=split(ring,A,B,C,int(parent.size()),axioms.size(),ai,starts.at(parent+"0"),starts.at(parent+"1"),int(parent.size()));
        certificate(out,ring,"split_"+parent,ring.subtract(ring.subtract(A.product,B.product),C.product),axioms,cof,parent.empty()?2*h+1:4*h+1);
        add_cof(ring,total,cof);
    }
    for(const auto& leaf:leaves) {
        const auto& b=blocks.at(leaf);Cofactors cof(axioms.size());cof[base.at(leaf)]=b.product;
        auto prefix=one;
        for(size_t i=0;i<b.inputs.size();i++) {cof[starts.at(leaf)+i]=prefix;prefix=ring.multiply(prefix,ring.subtract(one,b.inputs[i]));}
        certificate(out,ring,"leaf_"+leaf,b.product,axioms,cof,2*h+2);add_cof(ring,total,cof);
    }
    certificate(out,ring,"complete_refutation",one,axioms,total,4*h+1);
    out<<"{\"record\":\"complete_verified\",\"prefix_blocks\":6,\"companions\":10,\"field_axioms_used\":0,\"bound\":"<<4*h+1<<"}\n";
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");need(!std::filesystem::exists(argv[2]),"output exists");
        auto parent=std::filesystem::path(argv[2]).parent_path();if(!parent.empty())std::filesystem::create_directories(parent);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"assignment_tree_certificate\",\"seed\":null,\"scope\":\"exact local identities and small full certificates, not a finite PHP degree separation\"}\n";
        for(int p:{2,3,5})for(int h:{1,2})for(int k:{0,1,2})local(out,p,h,k);
        for(int p:{2,3,5})for(int h:{1,2})complete(out,p,h);
        out<<"{\"record\":\"summary\",\"local_cases\":18,\"satisfying_models\":48,\"missing_booleanity_controls\":12,\"complete_certificates\":6,\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failed");
        std::cout<<"Eighteen split identities, 48 models, 12 Booleanity controls, and six full NS certificates passed.\n";
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
