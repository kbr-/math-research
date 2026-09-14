// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact weighted zero-selector images and source profiles over retained clamps.
#include "domain_polynomial.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace domain_polynomial;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
struct Context {
    Ring r;
    std::string name;
    std::vector<Polynomial> axioms;
    int certificates=0;
    Context(int p,std::string label):r(p,80),name(std::move(label)){}
    int axiom(const Polynomial& f){axioms.push_back(f);return int(axioms.size())-1;}
    void setup(std::ostream& out){
        out<<"{\"record\":\"system\",\"case\":\""<<name<<"\",\"field\":"<<r.p<<",\"axioms\":";
        write_polynomials(out,axioms);out<<"}\n";
    }
    void certificate(std::ostream& out,const std::string& label,const Polynomial& target,
                     const std::map<int,Polynomial>& cof,int budget){
        Polynomial sum;int used=0;bool comma=false;
        out<<"{\"record\":\"NS_certificate\",\"case\":\""<<name<<"\",\"name\":\""<<label
           <<"\",\"target\":";write_json(out,target);out<<",\"budget\":"<<budget<<",\"terms\":[";
        for(const auto& [id,q]:cof)if(!q.empty()){
            r.accumulate(sum,r.multiply(q,axioms.at(id)));
            used=std::max(used,degree(q)+degree(axioms[id]));
            if(comma)out<<',';
            comma=true;out<<"{\"axiom_id\":"<<id<<",\"cofactor\":";write_json(out,q);out<<'}';
        }
        need(sum==target && used<=budget,"NS identity or budget: "+label);
        out<<"],\"witness_degree\":"<<used<<"}\n";++certificates;
    }
    void Boolean(std::ostream& out,const std::string& label,const Polynomial& target,int old,int budget){
        std::vector<int> powers(old,2);auto red=domain_reduce(r,target,powers);
        verify_reduction(r,target,powers,red);need(red.remainder.empty(),"Boolean remainder");
        std::map<int,Polynomial> cof;
        for(int i=0;i<old;++i)if(!red.coefficients[i].empty())cof[i]=red.coefficients[i];
        certificate(out,label,target,cof,budget);
    }
    void model(std::ostream& out,const std::string& label,const std::map<int,int>& point,
               int variables,int omitted,const Polynomial& target,int expected){
        for(std::size_t i=0;i<axioms.size();++i)
            need(int(i)==omitted || r.evaluate(axioms[i],point)==0,"retained model");
        need(r.evaluate(target,point)==expected,"model target");
        out<<"{\"record\":\"model\",\"case\":\""<<name<<"\",\"name\":\""<<label
           <<"\",\"omitted_axiom\":"<<omitted<<",\"assignment\":[";
        for(int i=0;i<variables;++i){if(i)out<<',';out<<point.at(i);}
        out<<"],\"target\":";write_json(out,target);out<<",\"target_value\":"<<expected<<"}\n";
    }
};
int weighted_images(std::ostream& out,int p){
    Context c(p,"simultaneous_weighted_images_F"+std::to_string(p));auto& r=c.r;
    auto x=[&](int i){return r.variable(i);};auto one=r.constant(1);
    for(int i=0;i<4;++i)c.axiom(r.subtract(r.power(x(i),2),x(i)));
    c.setup(out);int fresh=4,h=2*(p-1);
    auto B0=make_block(r,{x(0),x(2)},h,fresh);
    auto B1=make_block(r,{x(1),x(3)},h,fresh);
    auto f=r.add(r.multiply(x(0),x(1)),r.multiply(x(2),x(3)));
    auto ideal=r.subtract(one,r.power(f,p-1));
    out<<"{\"record\":\"image_setup\",\"case\":\""<<c.name<<"\",\"accuracy\":"<<h
       <<",\"multiplier\":";write_json(out,f);
    out<<",\"source_blocks\":[";write_block(out,B0);out<<',';write_block(out,B1);
    out<<"],\"scope\":\"local image identities; rank-two tuples do not meet the asymptotic high-rank hypothesis\"}\n";
    for(int b=0;b<2;++b){
        const auto& block=b?B1:B0;
        std::vector<Polynomial> a=b?std::vector<Polynomial>{x(0),x(2)}:
                                       std::vector<Polynomial>{x(1),x(3)};
        std::map<int,Polynomial> images;
        out<<"{\"record\":\"coefficient_map\",\"case\":\""<<c.name<<"\",\"block\":"<<b<<",\"images\":[";
        bool comma=false;
        for(int u=0;u<h;++u)for(int i=0;i<2;++i){
            int id=block.variables[u][i];
            auto beta=u<p-1?r.multiply(r.constant(u+1),a[i]):Polynomial{};
            images[id]=beta;
            if(comma)out<<',';
            comma=true;out<<'['<<id<<',';write_json(out,beta);out<<']';
        }
        out<<"]}\n";
        auto mapped=r.substitute(block.product,images);need(mapped==ideal,"mapped product");
        auto weighted=r.multiply(f,mapped);
        need(weighted==r.subtract(f,r.power(f,p)),"common weighted zero");
        c.Boolean(out,"weighted_clamp_"+std::to_string(b),weighted,4,2*p);
        for(int i=0;i<2;++i)
            c.Boolean(out,"weighted_companion_"+std::to_string(b)+"_"+std::to_string(i),
                      r.multiply(f,r.substitute(block.companions[i],images)),4,2*p+1);
        for(const auto& [id,beta]:images)
            c.Boolean(out,"weighted_field_"+std::to_string(id),
                      r.multiply(f,r.subtract(r.power(beta,p),beta)),4,2*(p+1));
        std::map<int,int> zero;for(int i=0;i<4;++i)zero[i]=0;
        need(r.evaluate(mapped,zero)==1 && r.evaluate(weighted,zero)==0,"weight is necessary");
        out<<"{\"record\":\"unweighted_zero_counter\",\"case\":\""<<c.name<<"\",\"block\":"<<b
           <<",\"old_assignment\":[0,0,0,0],\"mapped_product_value\":1,\"weighted_value\":0}\n";
        if(p==3){
            std::map<int,int> point;for(int i=0;i<4;++i)point[i]=i<2?1:0;
            int largest=0;for(const auto& [id,beta]:images){(void)id;largest=std::max(largest,r.evaluate(beta,point));}
            need(largest==2,"non-Boolean coefficient control");
            out<<"{\"record\":\"coefficient_domain_control\",\"case\":\""<<c.name<<"\",\"block\":"<<b
               <<",\"old_assignment\":[1,1,0,0],\"largest_mapped_coefficient\":2}\n";
        }
    }
    return c.certificates;
}
void assign(const Ring& r,const Block& b,std::map<int,int>& point){
    for(const auto& row:b.variables)for(int id:row)point[id]=0;
    for(std::size_t i=0;i<b.inputs.size();++i)
        if(r.evaluate(b.inputs[i],point)){point[b.variables[0][i]]=1;break;}
}
int rank(std::vector<unsigned> rows){
    unsigned pivots[32]{};int answer=0;
    for(unsigned row:rows)while(row){
        int bit=31-__builtin_clz(row);
        if(pivots[bit])row^=pivots[bit];else{pivots[bit]=row;++answer;break;}
    }
    return answer;
}
int source_profiles(std::ostream& out){
    Context c(2,"two_level_clamped_source_profile");auto& r=c.r;
    auto x=[&](int i){return r.variable(i);};auto one=r.constant(1);
    int fresh=8;auto B0=make_block(r,{x(4),x(5)},2,fresh);
    auto B1=make_block(r,{x(6),x(7)},2,fresh);
    auto A=make_block(r,{x(0),x(1),x(2),x(3)},2,fresh);
    for(int i=0;i<fresh;++i)c.axiom(r.subtract(r.power(x(i),2),x(i)));
    for(const auto& block:{B0,B1})for(const auto& f:block.companions)c.axiom(f);
    std::vector<int> ac;for(const auto& f:A.companions)ac.push_back(c.axiom(f));
    std::vector<int> clamp={c.axiom(B0.product),c.axiom(B1.product)};
    c.setup(out);
    std::vector<Polynomial> G;for(int i=0;i<4;++i)G.push_back(r.add(x(i),i<2?B0.product:B1.product));
    need(rank({1,1,2,2})==2 && rank({0,0,0,0})==0,"projected source rank");
    for(const auto& g:G)need(degree(g)==4,"original source input degree");
    out<<"{\"record\":\"source_profile_setup\",\"case\":\""<<c.name
       <<"\",\"accuracy\":2,\"original_input_degrees\":[4,4,4,4],\"original_weight\":10"
         ",\"original_selector_rank\":2,\"after_clamp_rank\":0,\"inputs\":";
    write_polynomials(out,G);out<<",\"bottom_blocks\":[";write_block(out,B0);out<<',';write_block(out,B1);
    out<<"],\"affine_core\":";write_block(out,A);
    out<<",\"scope\":\"conditional source-profile component; the small bottom tuples are not asymptotic high-rank blocks\"}\n";
    for(int b=0;b<2;++b){
        const auto& block=b?B1:B0;auto residual=one;
        for(int i=0;i<2;++i)r.accumulate(residual,r.multiply(block.prefix[i],block.inputs[i]),-1);
        need(residual==block.product,"zero-profile residual");
        c.certificate(out,"zero_value_prefix_"+std::to_string(b),residual,{{clamp[b],one}},4);
    }
    for(int i=0;i<4;++i)
        c.certificate(out,"input_projection_"+std::to_string(i),r.subtract(G[i],x(i)),{{clamp[i/2],one}},4);
    auto residual=r.subtract(one,A.product);std::map<int,Polynomial> prefix_cof;
    for(int i=0;i<4;++i){
        need(degree(A.prefix[i])+4<=10,"original-input prefix budget");
        r.accumulate(residual,r.multiply(A.prefix[i],G[i]),-1);
        r.accumulate(prefix_cof[clamp[i/2]],A.prefix[i],-1);
    }
    c.certificate(out,"parent_original_input_prefix",residual,prefix_cof,10);
    for(int i=0;i<4;++i)
        c.certificate(out,"parent_companion_"+std::to_string(i),r.multiply(G[i],A.product),
                      {{ac[i],one},{clamp[i/2],A.product}},14);
    std::map<int,Polynomial> bool_cof;
    for(int i=0;i<4;++i)bool_cof[ac[i]]=r.multiply(r.constant(-1),A.prefix[i]);
    c.certificate(out,"parent_Booleanity",r.subtract(r.power(A.product,2),A.product),bool_cof,20);
    int models=0,ones=0;
    for(int bits=0;bits<256;++bits){
        std::map<int,int> point;for(int i=0;i<8;++i)point[i]=(bits>>i)&1;
        assign(r,B0,point);assign(r,B1,point);assign(r,A,point);
        if(r.evaluate(B0.product,point) || r.evaluate(B1.product,point))continue;
        int value=r.evaluate(A.product,point);
        c.model(out,"clamped_old_point_"+std::to_string(bits),point,fresh,-1,A.product,value);
        ++models;ones+=value;
    }
    need(models==144 && ones==9,"complete canonical clamped models");
    std::map<int,int> missing;for(int i=0;i<8;++i)missing[i]=int(i==6);
    assign(r,B0,missing);assign(r,B1,missing);assign(r,A,missing);
    c.model(out,"missing_first_clamp",missing,fresh,clamp[0],r.multiply(G[0],A.product),1);
    out<<"{\"record\":\"profile_summary\",\"models\":"<<models<<",\"value_one_models\":"<<ones
       <<",\"missing_clamp_models\":1,\"NS_certificates\":"<<c.certificates<<"}\n";
    return c.certificates;
}
int low_rank_counter(std::ostream& out,int p){
    Context c(p,"low_rank_clamp_counter_F"+std::to_string(p));auto& r=c.r;
    auto b=r.variable(0),one=r.constant(1);int fresh=1;
    auto block=make_block(r,{b},2,fresh);
    c.axiom(r.subtract(r.power(b,2),b));
    for(int i=1;i<fresh;++i)c.axiom(r.subtract(r.power(r.variable(i),p),r.variable(i)));
    int comp=c.axiom(block.companions[0]),clamp=c.axiom(block.product);
    c.setup(out);
    c.certificate(out,"clamp_forces_old_bit_one",r.subtract(b,one),
                  {{comp,one},{0,block.prefix[0]},{clamp,r.constant(-1)}},5);
    std::map<int,int> point;for(int i=0;i<fresh;++i)point[i]=0;point[0]=point[1]=1;
    c.model(out,"satisfying_clamped_literal",point,fresh,-1,b,1);
    return c.certificates;
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");
        out<<"{\"record\":\"schema\",\"version\":1,\"polynomials\":\"[coefficient,[variable IDs with repetitions]]\","
             "\"scope\":\"exact local weighted images, conditional source profiles, and missing-hypothesis controls\"}\n";
        int count=weighted_images(out,2);
        count+=weighted_images(out,3);
        count+=source_profiles(out);
        count+=low_rank_counter(out,2);
        count+=low_rank_counter(out,3);
        out<<"{\"record\":\"summary\",\"NS_certificates\":"<<count<<",\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<count<<" exact NS certificates passed; 144 clamped profile models and scope controls passed.\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
