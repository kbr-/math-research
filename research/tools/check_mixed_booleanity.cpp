// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Mixed unit-product, packed, and base-zero modes with exact NS image proofs.
#include "ens_symbolic.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace ens_symbolic;
void need(bool b,const std::string& text) {if(!b) throw std::runtime_error(text);}
using Cofactors=std::vector<Polynomial>;
Cofactors scaled(const Ring& ring,const Cofactors& cof,const Polynomial& by) {
    Cofactors result;for(const auto& q:cof) result.push_back(ring.multiply(q,by));return result;
}
Cofactors plus(const Ring& ring,Cofactors a,const Cofactors& b) {
    need(a.size()==b.size(),"cofactor size");
    for(size_t i=0;i<a.size();i++) ring.accumulate(a[i],b[i]);
    return a;
}
void certificate(std::ostream& out,const Ring& ring,const std::string& name,
                 const Polynomial& target,const std::vector<Polynomial>& axioms,
                 const Cofactors& cof,int ceiling) {
    Polynomial sum;int degree_used=0;
    for(size_t i=0;i<cof.size();i++) {
        auto term=ring.multiply(cof[i],axioms.at(i));ring.accumulate(sum,term);
        degree_used=std::max(degree_used,degree(term));
    }
    need(sum==target && degree_used<=ceiling,"certificate "+name);
    Polynomial corrupted=ring.add(sum,ring.constant(1));
    need(corrupted!=target,"corruption control "+name);
    out<<"{\"record\":\"certificate\",\"name\":\""<<name<<"\",\"degree\":"<<degree_used
       <<",\"ceiling\":"<<ceiling<<",\"target\":";write_json(out,target);
    out<<",\"cofactors\":";write_polynomials(out,cof);
    out<<",\"corruption_rejected\":true}\n";
}
void run_case(std::ostream& out,int p,int width,int mode) {
    Ring ring(p,64);auto one=ring.constant(1);int h=2;
    std::vector<Polynomial> inputs,axioms;Polynomial rho;
    for(int j=0;j<width;j++) {
        auto x=ring.variable(j);inputs.push_back(x);ring.accumulate(rho,x);
        axioms.push_back(ring.subtract(ring.multiply(x,x),x));
    }
    auto b=ring.variable(width),c=ring.variable(width+1);
    axioms.push_back(ring.subtract(ring.multiply(b,b),b));
    axioms.push_back(ring.subtract(ring.multiply(c,c),c));
    int next=width+2;Block argument=make_block(ring,inputs,h,next);
    std::map<int,Polynomial> images;
    if(mode) for(int u=0;u<h;u++) for(int j=0;j<width;j++)
        images[argument.variables[u][j]]=ring.constant(mode==2 && u==0?1:0);
    auto a=ring.substitute(argument.product,images);
    int argument_companion_start=-1,row=-1;
    if(mode==0) {
        for(const auto& line:argument.variables) for(int variable:line) {
            auto r=ring.variable(variable);axioms.push_back(ring.subtract(ring.power(r,p),r));
        }
        argument_companion_start=int(axioms.size());
        axioms.insert(axioms.end(),argument.companions.begin(),argument.companions.end());
    }
    if(mode==2) {row=int(axioms.size());axioms.push_back(ring.subtract(rho,one));}
    Cofactors ha(axioms.size()),hb(axioms.size()),hc(axioms.size());
    if(mode==0) for(int j=0;j<width;j++)
        ha[argument_companion_start+j]=ring.subtract({},argument.prefix[j]);
    if(mode==2) ha[row]=rho;
    hb[width]=one;hc[width+1]=one;
    auto Ha=ring.subtract(ring.multiply(a,a),a);
    auto Hb=ring.subtract(ring.multiply(b,b),b),Hc=ring.subtract(ring.multiply(c,c),c);
    auto na=ring.subtract(one,a),nb=ring.subtract(one,b),nc=ring.subtract(one,c);
    auto packed_i=ring.multiply(na,nb),ni=ring.subtract(one,packed_i);
    auto packed_j=ring.multiply(ni,nc);
    auto hi=plus(ring,scaled(ring,ha,ring.multiply(nb,nb)),scaled(ring,hb,na));
    auto hj=plus(ring,scaled(ring,hi,ring.multiply(nc,nc)),scaled(ring,hc,ni));
    int da=degree(argument.product),di=h*(da+1),dj=h*(di+1);
    std::vector<std::vector<int>> iv,jv;
    for(auto* vars:{&iv,&jv}) for(int u=0;u<h;u++) {
        std::vector<int> ids;
        for(int j=0;j<2;j++) {int id=next++;ids.push_back(id);images[id]=ring.constant(u==j?1:0);}
        vars->push_back(ids);
    }
    // The original I/J gates are retained as a complete factored DAG, avoiding
    // expansion of a product that is immediately specialized.
    out<<"{\"record\":\"case\",\"p\":"<<p<<",\"width\":"<<width<<",\"accuracy\":2,"
           "\"mode\":\""<<(mode==0?"retain":mode==1?"unit":"base_zero")<<"\","
           "\"argument\":";write_block(out,argument);
    out<<",\"source_gates\":[{\"name\":\"I\",\"inputs\":[{\"product_of\":\"argument\"},"
          "{\"variable\":"<<width<<"}],\"coefficient_variables\":[";
    for(size_t u=0;u<iv.size();u++) {if(u)out<<',';out<<'['<<iv[u][0]<<','<<iv[u][1]<<']';}
    out<<"],\"product_degree\":"<<di<<"},{\"name\":\"J\",\"inputs\":[{\"product_of\":\"I\"},"
          "{\"variable\":"<<width+1<<"}],\"coefficient_variables\":[";
    for(size_t u=0;u<jv.size();u++) {if(u)out<<',';out<<'['<<jv[u][0]<<','<<jv[u][1]<<']';}
    out<<"],\"product_degree\":"<<dj<<"}],\"images\":[";
    bool comma=false;
    for(const auto& [variable,image]:images) {
        if(comma)out<<',';
        comma=true;out<<"{\"variable\":"<<variable<<",\"image\":";write_json(out,image);out<<'}';
        auto r=ring.variable(variable);
        need(ring.substitute(ring.subtract(ring.power(r,p),r),images).empty(),"selected field image");
    }
    out<<"],\"specialized_products\":";write_polynomials(out,{a,packed_i,packed_j});
    out<<",\"axioms\":";write_polynomials(out,axioms);out<<"}\n";
    certificate(out,ring,"argument_booleanity",Ha,axioms,ha,2*degree(a));
    certificate(out,ring,"first_packed_booleanity",ring.subtract(ring.multiply(packed_i,packed_i),packed_i),
                axioms,hi,2*degree(packed_i));
    certificate(out,ring,"second_packed_booleanity",ring.subtract(ring.multiply(packed_j,packed_j),packed_j),
                axioms,hj,2*degree(packed_j));
    certificate(out,ring,"I_companion_a",ring.multiply(a,packed_i),axioms,
                scaled(ring,ha,ring.subtract({},nb)),da+di);
    certificate(out,ring,"I_companion_b",ring.multiply(b,packed_i),axioms,
                scaled(ring,hb,ring.subtract({},na)),1+di);
    certificate(out,ring,"J_companion_I",ring.multiply(packed_i,packed_j),axioms,
                scaled(ring,hi,ring.subtract({},nc)),di+dj);
    certificate(out,ring,"J_companion_c",ring.multiply(c,packed_j),axioms,
                scaled(ring,hc,ring.subtract({},ni)),1+dj);
    if(mode==2) {
        for(int j=0;j<width;j++) {
            Cofactors co(axioms.size());co[row]=ring.subtract({},inputs[j]);
            certificate(out,ring,"base_zero_argument_companion",
                        ring.multiply(inputs[j],a),axioms,co,1+da);
        }
    }
    if(mode==1) {
        need(a==one && packed_i.empty() && packed_j==nc,"unit plus packing images");
        auto direct=ring.substitute(argument.companions[0],images);
        need(direct==inputs[0] && !direct.empty(),"unit direct companion cannot be dropped");
    }
    std::map<int,int> point;
    for(int i=0;i<next;i++) point[i]=0;
    int direct_coordinate=0;
    if(mode==2) {point[0]=1;point[width]=1;direct_coordinate=1;}
    for(const auto& axiom:axioms) need(ring.evaluate(axiom,point)==0,"role-control old model");
    auto bad_companion=direct_coordinate?b:a;
    need(ring.evaluate(bad_companion,point)==1,"unit I should violate a direct request");
    need(ring.evaluate(packed_i,point)==0,"packed I does not resolve the control");
    out<<"{\"record\":\"role_control\",\"unit_I_booleanity_is_zero\":true,"
           "\"unit_I_direct_companion\":";write_json(out,bad_companion);
    out<<",\"direct_coordinate\":"<<direct_coordinate<<",\"companion_value\":1,"
           "\"packed_I_value\":0,\"old_axioms_zero\":true,\"assignment\":[";
    for(int i=0;i<next;i++) {if(i)out<<',';out<<point.at(i);}
    out<<"]}\n";
    (void)Hb;(void)Hc;
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");
        auto parent=std::filesystem::path(argv[2]).parent_path();
        if(!parent.empty())std::filesystem::create_directories(parent);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"mixed_booleanity\",\"seed\":null,"
               "\"scope\":\"exact NS image certificates and role controls; no full PHP compiler\"}\n";
        for(int p:{2,3})for(int width:{3,7})for(int mode:{0,1,2})run_case(out,p,width,mode);
        out<<"{\"record\":\"summary\",\"cases\":12,\"all_passed\":true}\n";
        out.close();need(bool(out),"write output failed");
        std::cout<<"Twelve mixed Booleanity cases and canonical-role controls passed.\n";
    } catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}
}
