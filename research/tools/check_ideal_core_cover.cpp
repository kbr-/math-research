// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
#include "ens_symbolic.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace ens_symbolic;
void need(bool ok,const std::string& reason) {if(!ok)throw std::runtime_error(reason);}
void run(std::ostream& out,int p,int width,int residuals) {
    Ring ring(p,64);auto one=ring.constant(1);const int h=2;
    std::vector<Polynomial> f;
    for(int j=0;j<width;j++)f.push_back(ring.variable(j));
    int next=width+residuals;
    Block core=make_block(ring,f,h,next);auto a=core.product,na=ring.subtract(one,a);
    std::vector<Polynomial> inputs=f;
    std::vector<std::vector<Polynomial>> witnesses;
    for(int i=0;i<width;i++) {
        std::vector<Polynomial> row(width);row[i]=one;witnesses.push_back(row);
    }
    for(int j=0;j<residuals;j++) {
        auto nb=ring.subtract(one,ring.variable(width+j));
        inputs.push_back(ring.multiply(na,nb));
        std::vector<Polynomial> row;
        for(const auto& v:core.prefix)row.push_back(ring.multiply(nb,v));
        witnesses.push_back(row);
    }
    std::vector<std::vector<int>> parent_variables;
    std::map<int,Polynomial> images;
    for(int u=0;u<h;u++) {
        std::vector<int> ids;
        for(size_t j=0;j<inputs.size();j++) {
            int id=next++;ids.push_back(id);
            images[id]=j<f.size()?ring.variable(core.variables[u][j]):Polynomial{};
        }
        parent_variables.push_back(ids);
    }
    int delta=0;for(const auto& input:inputs)delta=std::max(delta,degree(input));
    int source_product_degree=h*(delta+1);
    Polynomial realized=one;
    for(int u=0;u<h;u++) {
        Polynomial factor=one;
        for(size_t j=0;j<inputs.size();j++)
            ring.accumulate(factor,ring.multiply(images.at(parent_variables[u][j]),inputs[j]),-1);
        realized=ring.multiply(realized,factor);
    }
    need(realized==a,"parent does not become retained core");
    out<<"{\"record\":\"case\",\"p\":"<<p<<",\"accuracy\":2,\"core_arity\":"<<width
       <<",\"residual_count\":"<<residuals<<",\"core\":";write_block(out,core);
    out<<",\"parent_inputs\":";write_polynomials(out,inputs);
    out<<",\"parent_product_degree\":"<<source_product_degree<<",\"parent_coefficient_variables\":[";
    for(size_t u=0;u<parent_variables.size();u++) {
        if(u)out<<',';
        out<<'[';for(size_t j=0;j<parent_variables[u].size();j++) {if(j)out<<',';out<<parent_variables[u][j];}
        out<<']';
    }
    out<<"],\"images\":[";
    bool comma=false;
    for(const auto& [v,q]:images) {
        if(comma)out<<',';
        comma=true;out<<"{\"variable\":"<<v<<",\"image\":";write_json(out,q);out<<'}';
        auto lhs=ring.subtract(ring.power(q,p),q);
        need(q.empty() || q.size()==1,"field map is not a variable or zero");
        if(q.empty())need(lhs.empty(),"zero field image");
        else {
            need(q.begin()->first.size()==1 && q.begin()->second==1,"unexpected coefficient map");
            auto r=ring.variable(q.begin()->first[0]);
            need(lhs==ring.subtract(ring.power(r,p),r),"retained field image");
        }
    }
    out<<"],\"product_image\":";write_json(out,a);out<<"}\n";
    for(size_t i=0;i<inputs.size();i++) {
        Polynomial reconstructed,image;int witness_degree=0,image_degree=0;
        for(size_t j=0;j<f.size();j++) {
            auto term=ring.multiply(witnesses[i][j],f[j]);
            ring.accumulate(reconstructed,term);witness_degree=std::max(witness_degree,degree(term));
            auto lifted=ring.multiply(witnesses[i][j],core.companions[j]);
            ring.accumulate(image,lifted);image_degree=std::max(image_degree,degree(lifted));
        }
        need(reconstructed==inputs[i],"input ideal witness");
        auto target=ring.multiply(inputs[i],a);
        int original=degree(inputs[i])+source_product_degree;
        need(image==target && witness_degree+degree(a)<=original && image_degree<=original,"image budget");
        out<<"{\"record\":\"ideal_core_certificate\",\"coordinate\":"<<i<<",\"input\":";write_json(out,inputs[i]);
        out<<",\"generator_cofactors\":";write_polynomials(out,witnesses[i]);
        out<<",\"target_image\":";write_json(out,target);
        out<<",\"input_witness_degree\":"<<witness_degree<<",\"image_degree\":"<<image_degree
           <<",\"original_degree\":"<<original<<"}\n";
    }
    // A residual is not in the Fp-linear span of the core's x_i inputs.
    bool residual_has_b=false;
    for(const auto& [monomial,c]:inputs[width]) {
        (void)c;
        if(std::find(monomial.begin(),monomial.end(),width)!=monomial.end())residual_has_b=true;
    }
    need(residual_has_b,"linear-span control became trivial");
    for(int value=0;value<2;value++) {
        std::map<int,int> point;for(int i=0;i<next;i++)point[i]=0;
        if(value==0) {point[0]=1;point[core.variables[0][0]]=1;}
        for(const auto& companion:core.companions)need(ring.evaluate(companion,point)==0,"core model");
        need(ring.evaluate(a,point)==value,"retained core cannot attain requested value");
        for(const auto& input:inputs)
            need(ring.evaluate(ring.multiply(input,a),point)==0,"parent image model");
        out<<"{\"record\":\"core_model\",\"core_value\":"<<value<<",\"assignment\":[";
        for(int i=0;i<next;i++) {if(i)out<<',';out<<point[i];}
        out<<"],\"all_core_companions_and_parent_images_zero\":true}\n";
    }
    out<<"{\"record\":\"controls\",\"residual_outside_linear_core_span\":true,"
           "\"retained_factors\":2,\"spare_parent_factors\":0,"
           "\"all_residuals_removed_without_extra_factors\":true}\n";
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");
        auto parent=std::filesystem::path(argv[2]).parent_path();
        if(!parent.empty())std::filesystem::create_directories(parent);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"ideal_core_cover\",\"seed\":null,"
               "\"scope\":\"absorption inputs after earlier constant packing\"}\n";
        for(int p:{2,3,5,7})for(int width:{3,7})for(int residuals:{1,5,17})run(out,p,width,residuals);
        out<<"{\"record\":\"summary\",\"cases\":24,\"all_passed\":true}\n";
        out.close();need(bool(out),"write output failed");
        std::cout<<"Twenty-four ideal-core absorption covers and nonconstant-core controls passed.\n";
    } catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}
}
