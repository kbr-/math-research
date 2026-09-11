// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
#include "ens_symbolic.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <set>
#include <string>
using namespace ens_symbolic;
void need(bool ok,const std::string& reason) {if(!ok)throw std::runtime_error(reason);}
void save_map(std::ostream& out,const std::map<int,Polynomial>& images) {
    out<<'[';bool comma=false;
    for(const auto& [v,q]:images) {
        if(comma)out<<',';
        comma=true;out<<"{\"variable\":"<<v<<",\"image\":";write_json(out,q);out<<'}';
    }
    out<<']';
}
void ns(std::ostream& out,const Ring& ring,const std::string& name,const Polynomial& target,
        const std::vector<Polynomial>& axioms,const std::vector<Polynomial>& cof,int bound) {
    need(axioms.size()==cof.size(),"NS arity");Polynomial sum;int used=0;
    for(size_t i=0;i<cof.size();i++) {
        auto term=ring.multiply(cof[i],axioms[i]);ring.accumulate(sum,term);used=std::max(used,degree(term));
    }
    need(sum==target && used<=bound,"NS identity "+name);
    out<<"{\"record\":\"certificate\",\"name\":\""<<name<<"\",\"target\":";write_json(out,target);
    out<<",\"axioms\":";write_polynomials(out,axioms);out<<",\"cofactors\":";write_polynomials(out,cof);
    out<<",\"degree\":"<<used<<",\"bound\":"<<bound<<"}\n";
}
void basis_case(std::ostream& out,int p,int h) {
    Ring ring(p,64);auto one=ring.constant(1),x=ring.variable(0),y=ring.variable(1);
    auto xy=ring.multiply(x,y),difference=ring.subtract(x,xy);int next=2;
    Block a=make_block(ring,{x,xy,difference},h,next);
    Block b=make_block(ring,{xy,difference},h,next);
    Block good=make_block(ring,{x,xy},h,next);
    Block bad=make_block(ring,{xy,difference},h,next);
    std::map<int,Polynomial> images,bad_images;
    for(int u=0;u<h;u++) {
        auto s0=ring.variable(good.variables[u][0]),s1=ring.variable(good.variables[u][1]);
        images[a.variables[u][0]]=s0;images[a.variables[u][1]]=s1;images[a.variables[u][2]]={};
        images[b.variables[u][0]]=ring.add(s0,s1);images[b.variables[u][1]]=s0;
        bad_images[a.variables[u][0]]={};
        bad_images[a.variables[u][1]]=ring.variable(bad.variables[u][0]);
        bad_images[a.variables[u][2]]=ring.variable(bad.variables[u][1]);
    }
    need(ring.substitute(a.product,images)==good.product && ring.substitute(b.product,images)==good.product,
         "common span product");
    need(ring.substitute(a.product,bad_images)==bad.product,"bad-basis product image");
    out<<"{\"record\":\"basis_case\",\"p\":"<<p<<",\"accuracy\":"<<h<<",\"source_A\":";
    write_block(out,a);out<<",\"source_B\":";write_block(out,b);out<<",\"degree_adapted_basis\":";
    write_block(out,good);out<<",\"unadapted_basis\":";write_block(out,bad);
    out<<",\"images\":";save_map(out,images);out<<",\"bad_images\":";save_map(out,bad_images);out<<"}\n";
    std::vector<std::vector<int>> rows={{1,0},{0,1},{1,-1},{0,1},{1,-1}};
    size_t row=0;
    for(const Block* source:{&a,&b}) for(size_t i=0;i<source->companions.size();i++,row++) {
        std::vector<Polynomial> cof{ring.constant(rows[row][0]),ring.constant(rows[row][1])};
        auto image=ring.substitute(source->companions[i],images);
        ns(out,ring,"graded_companion_image",image,good.companions,cof,degree(source->companions[i]));
    }
    for(const auto& [variable,image]:images) {
        auto old=ring.variable(variable),lhs=ring.subtract(ring.power(image,p),image);Polynomial rhs;
        for(const auto& [monomial,c]:image) {
            need(monomial.size()==1,"field image should be linear");
            auto s=ring.variable(monomial[0]);
            ring.accumulate(rhs,ring.subtract(ring.power(s,p),s),c);
        }
        need(lhs==rhs && degree(lhs)<=p,"linear field image");
        need(ring.substitute(ring.subtract(ring.power(old,p),old),images)==lhs,"field substitution");
    }
    auto bad_target=ring.multiply(x,bad.product);int ceiling=3*h+1;
    need(degree(bad_target)==ceiling,"bad-basis target degree");
    for(const auto& f:bad.companions) need(degree(f)>ceiling,"bad companion should be unavailable");
    std::map<int,int> point;for(int i=0;i<next;i++)point[i]=0;point[0]=1;
    need(ring.evaluate(bad_target,point)==1,"degree-specific bad-basis countermodel");
    out<<"{\"record\":\"unadapted_degree_control\",\"target\":";write_json(out,bad_target);
    out<<",\"degree\":"<<ceiling<<",\"all_companion_degrees\":[";
    for(size_t i=0;i<bad.companions.size();i++) {if(i)out<<',';out<<degree(bad.companions[i]);}
    out<<"],\"model\":\"x=1,y=0,all coefficient variables=0\","
           "\"all_available_degree_bounded_axioms_zero\":true,\"target_value\":1}\n";
    auto hx=ring.subtract(ring.multiply(x,x),x),hy=ring.subtract(ring.multiply(y,y),y);
    auto hxy=ring.subtract(ring.multiply(xy,xy),xy);
    ns(out,ring,"Boolean_basis_input",hxy,{hx,hy},{ring.multiply(y,y),x},4);
    if(h>=2) {
        auto nx=ring.subtract(one,x),nxy=ring.subtract(one,xy),packed=ring.multiply(nx,nxy);
        std::vector<Polynomial> c0{ring.subtract({},nxy),{}};
        std::vector<Polynomial> c1{ring.subtract({},ring.multiply(nx,ring.multiply(y,y))),
                                   ring.subtract({},ring.multiply(nx,x))};
        ns(out,ring,"rank_packed_low_input",ring.multiply(x,packed),{hx,hy},c0,degree(a.companions[0]));
        ns(out,ring,"rank_packed_high_input",ring.multiply(xy,packed),{hx,hy},c1,degree(a.companions[1]));
        std::vector<Polynomial> c2{ring.subtract(c0[0],c1[0]),ring.subtract(c0[1],c1[1])};
        ns(out,ring,"rank_packed_dependent_input",ring.multiply(difference,packed),{hx,hy},c2,
           degree(a.companions[2]));
    }
}
void ideal_case(std::ostream& out,int p,int width,int h) {
    Ring ring(p);auto one=ring.constant(1),x=ring.variable(0);
    std::vector<Polynomial> inputs{x},quotients{one};
    std::set<Monomial> monomials;monomials.insert(inputs[0].begin()->first);
    for(int j=1;j<=width;j++) {
        auto y=ring.variable(j);inputs.push_back(ring.multiply(x,y));quotients.push_back(y);
        need(inputs.back().size()==1,"monomial input");
        monomials.insert(inputs.back().begin()->first);
    }
    need(monomials.size()==inputs.size(),"linear rank control");
    int next=width+1;std::vector<std::vector<int>> variables;
    std::map<int,Polynomial> images;
    for(int u=0;u<h;u++) {
        std::vector<int> ids;
        for(size_t i=0;i<inputs.size();i++) {
            int id=next++;ids.push_back(id);images[id]=ring.constant(u==0 && i==0?1:0);
        }
        variables.push_back(ids);
    }
    auto packed=ring.subtract(one,x),hx=ring.subtract(ring.multiply(x,x),x);
    out<<"{\"record\":\"ideal_case\",\"p\":"<<p<<",\"accuracy\":"<<h<<",\"inputs\":";
    write_polynomials(out,inputs);out<<",\"original_product_degree\":"<<3*h
        <<",\"linear_rank\":"<<inputs.size()<<",\"Boolean_ideal_generators\":[0],"
          "\"coefficient_variables\":[";
    for(size_t u=0;u<variables.size();u++) {
        if(u)out<<',';
        out<<'[';for(size_t i=0;i<variables[u].size();i++) {if(i)out<<',';out<<variables[u][i];}out<<']';
    }
    out<<"],\"images\":";save_map(out,images);
    out<<",\"product_image\":";write_json(out,packed);out<<"}\n";
    for(size_t i=0;i<inputs.size();i++) {
        need(ring.multiply(quotients[i],x)==inputs[i],"ideal witness");
        auto target=ring.multiply(inputs[i],packed);
        ns(out,ring,"ideal_cover_companion",target,{hx},{ring.subtract({},quotients[i])},
           degree(inputs[i])+3*h);
        out<<"{\"record\":\"input_ideal_witness\",\"input\":"<<i<<",\"cofactor\":";
        write_json(out,quotients[i]);out<<",\"certificate_degree\":"<<degree(inputs[i])<<"}\n";
    }
    need(ring.subtract(ring.multiply(packed,packed),packed)==hx,"packed root Booleanity");
    for(const auto& [variable,value]:images) {
        (void)variable;need(ring.subtract(ring.power(value,p),value).empty(),"constant field image");
    }
}
void nonboolean_control(std::ostream& out) {
    Ring ring(3);auto one=ring.constant(1),x=ring.variable(0),y=ring.variable(1);
    auto f=ring.add(x,y),g=ring.subtract(x,y);
    auto product=ring.multiply(ring.subtract(one,f),ring.subtract(one,g));
    std::map<int,int> point{{0,1},{1,1}};
    need(ring.evaluate(product,point)==2,"non-Boolean basis product control");
    need(ring.evaluate(ring.multiply(f,product),point)==1,"non-Boolean companion control");
    out<<"{\"record\":\"nonboolean_basis_control\",\"p\":3,\"basis\":";
    write_polynomials(out,{f,g});out<<",\"product\":";write_json(out,product);
    out<<",\"Boolean_domain_point\":[1,1],\"product_value\":2,\"companion_value\":1,"
           "\"basis_invertible\":true}\n";
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");
        auto parent=std::filesystem::path(argv[2]).parent_path();
        if(!parent.empty())std::filesystem::create_directories(parent);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"input_generator_cover\",\"seed\":null}\n";
        for(int p:{2,3,5,7})for(int h:{1,2})basis_case(out,p,h);
        for(int p:{2,3,5,7})for(int width:{2,7,31})for(int h:{1,2})ideal_case(out,p,width,h);
        nonboolean_control(out);
        out<<"{\"record\":\"summary\",\"basis_cases\":8,\"ideal_cases\":24,"
               "\"nonboolean_controls\":1,\"all_passed\":true}\n";
        out.close();need(bool(out),"write output failed");
        std::cout<<"Eight basis cases, 24 ideal covers, and the non-Boolean basis control passed.\n";
    } catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}
}
