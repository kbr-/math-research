// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Factored source-image certificates after bottom-level hybrid specialization.
#include "ens_symbolic.hpp"
#include "binary_php.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <numeric>
#include <string>
using namespace ens_symbolic;
namespace bp=binary_php;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
template<class T>void array(std::ostream& out,const std::vector<T>& values){
    out<<'[';
    for(std::size_t i=0;i<values.size();++i){if(i)out<<',';out<<values[i];}
    out<<']';
}
struct Cert{Polynomial target;std::vector<Polynomial> cofactors;};
int certificate_count=0;
Cert boolean_division(const Ring& ring,const Polynomial& target,const std::vector<int>& domains){
    Cert result{target,std::vector<Polynomial>(domains.size())};
    Polynomial pending=target;
    std::map<int,int> index;
    for(std::size_t i=0;i<domains.size();++i)index[domains[i]]=int(i);
    while(true){
        auto found=pending.end();int variable=-1;
        for(auto it=pending.begin();it!=pending.end();++it){
            for(std::size_t j=1;j<it->first.size();++j)
                if(it->first[j]==it->first[j-1]&&index.count(it->first[j])){
                    found=it;variable=it->first[j];break;
                }
            if(found!=pending.end())break;
        }
        if(found==pending.end())break;
        auto monomial=found->first;int scalar=found->second;
        for(int j=0;j<2;++j)monomial.erase(std::find(monomial.begin(),monomial.end(),variable));
        Polynomial q{{monomial,scalar}};
        ring.accumulate(result.cofactors[index.at(variable)],q);
        auto x=ring.variable(variable);
        ring.accumulate(pending,ring.multiply(q,ring.subtract(ring.multiply(x,x),x)),-1);
    }
    need(pending.empty(),"nonzero Boolean remainder");
    return result;
}
void emit_certificate(std::ostream& out,const Ring& ring,const std::string& name,
                      const Cert& cert,const std::vector<int>& domains,
                      const Polynomial& condition,int bound){
    bool conditioned=!condition.empty();
    need(cert.cofactors.size()==domains.size()+conditioned,"cofactor count");
    Polynomial sum;int used=0;
    for(std::size_t j=0;j<cert.cofactors.size();++j){
        Polynomial axiom;
        if(j==domains.size())axiom=condition;
        else{
            auto x=ring.variable(domains[j]);axiom=ring.subtract(ring.multiply(x,x),x);
        }
        auto term=ring.multiply(cert.cofactors[j],axiom);
        ring.accumulate(sum,term);used=std::max(used,degree(term));
    }
    need(sum==cert.target&&used<=bound,"NS certificate: "+name);
    out<<"{\"type\":\"NS_certificate\",\"name\":\""<<name<<"\",\"domains\":";
    array(out,domains);out<<",\"condition\":";write_json(out,condition);
    out<<",\"target\":";write_json(out,cert.target);
    out<<",\"cofactors\":";write_polynomials(out,cert.cofactors);
    out<<",\"degree\":"<<used<<",\"bound\":"<<bound<<"}\n";
    ++certificate_count;
}
Cert multiply_certificate(const Ring& ring,const Cert& cert,const Polynomial& q){
    Cert result{ring.multiply(cert.target,q),{}};
    for(const auto& c:cert.cofactors)result.cofactors.push_back(ring.multiply(c,q));
    return result;
}
int weighted_degree(const Polynomial& f,int low,int high,int weight){
    int result=0;
    for(const auto& [monomial,coefficient]:f){
        (void)coefficient;int d=0;
        for(int variable:monomial)d+=variable==low||variable==high?weight:1;
        result=std::max(result,d);
    }
    return result;
}
void comparison(std::ostream& out,const Ring& ring,const std::string& name,
                const Polynomial& formal,int low,int high,int h,int k,
                const std::map<int,Polynomial>& evaluations,
                const Cert& weighted_core,const Cert& conditioned_core,
                const std::vector<int>& old_domains,const Polynomial& condition){
    auto reduced=ring.substitute(formal,{{high,ring.constant(0)}});
    auto difference=ring.subtract(formal,reduced);
    Polynomial quotient;
    for(const auto& [term,coefficient]:difference){
        auto monomial=term;auto found=std::find(monomial.begin(),monomial.end(),high);
        need(found!=monomial.end(),"high selector did not divide difference");
        monomial.erase(found);ring.accumulate(quotient,Polynomial{{monomial,coefficient}});
    }
    need(ring.multiply(ring.variable(high),quotient)==difference,"formal division identity");
    int original=weighted_degree(formal,low,high,2*h);
    auto q=ring.substitute(quotient,evaluations);
    need(difference.empty()||degree(q)<=k*(original-2*h),"quotient degree");
    out<<"{\"type\":\"formal_comparison\",\"name\":\""<<name
       <<"\",\"original_degree\":"<<original<<",\"formal\":";
    write_json(out,formal);out<<",\"high_zero_formal\":";write_json(out,reduced);
    out<<",\"formal_quotient\":";write_json(out,quotient);
    out<<",\"evaluated_quotient\":";write_json(out,q);out<<"}\n";
    emit_certificate(out,ring,name+"/weighted",
                     multiply_certificate(ring,weighted_core,q),old_domains,{},k*original);
    emit_certificate(out,ring,name+"/conditioned",
                     multiply_certificate(ring,conditioned_core,q),old_domains,condition,k*original);
}
void fixture(int h,std::ostream& out){
    constexpr int k=3;
    int low_rank=4*h,high_rank=low_rank+1;
    int q0=high_rank+2,q1=high_rank+3,low_start=high_rank+4,old=low_start+low_rank;
    int low_symbol=old,high_symbol=old+1,fresh=old+2;
    Ring ring(2,64);auto one=ring.constant(1),zero=ring.constant(0);
    auto f=ring.multiply(ring.multiply(ring.variable(0),ring.variable(1)),ring.variable(2));
    auto condition=ring.subtract(one,f);
    std::vector<int> old_domains(old);std::iota(old_domains.begin(),old_domains.end(),0);
    std::vector<Polynomial> low_inputs,high_inputs;
    for(int i=0;i<low_rank;++i)low_inputs.push_back(ring.variable(low_start+i));
    high_inputs={ring.add(ring.variable(0),ring.variable(3)),ring.variable(3)};
    for(int j=2;j<high_rank;++j)high_inputs.push_back(ring.variable(j+2));
    Block low=make_block(ring,low_inputs,h,fresh),high=make_block(ring,high_inputs,h,fresh);
    std::map<int,Polynomial> coefficients;
    for(int id=old+2;id<fresh;++id)coefficients[id]=zero;
    Polynomial chi=one;
    for(const auto& g:low_inputs)chi=ring.multiply(chi,ring.subtract(one,g));
    for(int row=0;row<h;++row){
        Polynomial prefix=one;
        for(int j=4*row;j<4*(row+1);++j){
            coefficients[low.variables[row][j]]=prefix;
            prefix=ring.multiply(prefix,ring.subtract(one,low_inputs[j]));
        }
    }
    auto a=ring.multiply(ring.variable(1),ring.variable(2)),x3=ring.variable(3);
    coefficients[high.variables[0][0]]=ring.add(a,ring.subtract(ring.multiply(x3,x3),x3));
    coefficients[high.variables[0][1]]=a;
    Polynomial H;
    for(std::size_t j=0;j<high.inputs.size();++j)
        ring.accumulate(H,ring.multiply(coefficients.at(high.variables[0][j]),high.inputs[j]));
    auto S=ring.subtract(one,H);
    need(ring.substitute(low.product,coefficients)==chi,"low product image");
    need(ring.substitute(high.product,coefficients)==S,"high product image");
    Cert weighted_core=boolean_division(ring,ring.multiply(f,S),old_domains);
    Cert membership=boolean_division(ring,ring.subtract(f,H),old_domains);
    Cert conditioned_core{S,membership.cofactors};
    conditioned_core.cofactors.push_back(one);
    std::string tag="h"+std::to_string(h);
    out<<"{\"type\":\"fixture\",\"name\":\""<<tag<<"\",\"h\":"<<h<<",\"k\":3,"
         "\"old_variables\":"<<old<<",\"formal_low_selector\":"<<low_symbol
       <<",\"formal_high_selector\":"<<high_symbol<<",\"low_rank\":"<<low_rank
       <<",\"high_rank\":"<<high_rank<<",\"weight\":";
    write_json(out,f);out<<",\"condition\":";write_json(out,condition);
    out<<",\"low_block\":";write_block(out,low);out<<",\"high_block\":";write_block(out,high);
    out<<",\"low_image\":";write_json(out,chi);out<<",\"high_image\":";write_json(out,S);
    out<<",\"coefficient_images\":[";
    bool comma=false;
    for(const auto& [id,value]:coefficients){
        if(comma)out<<',';
        comma=true;
        out<<'['<<id<<',';write_json(out,value);out<<']';
    }
    out<<"]}\n";
    emit_certificate(out,ring,tag+"/weighted-core",weighted_core,old_domains,{},2*k);
    emit_certificate(out,ring,tag+"/conditioned-core",conditioned_core,old_domains,condition,k);
    emit_certificate(out,ring,tag+"/condition-weight",
                     boolean_division(ring,ring.multiply(f,condition),old_domains),old_domains,{},2*k);
    std::map<int,Polynomial> evaluations{{low_symbol,chi},{high_symbol,S}};
    std::map<int,Polynomial> virtual_values{{low_symbol,chi},{high_symbol,zero}};
    auto L=ring.variable(low_symbol),Z=ring.variable(high_symbol);
    std::vector<Polynomial> inputs={
        ring.add(L,Z),ring.add(ring.variable(q0),Z),
        ring.add(one,ring.add(ring.variable(q1),L))};
    std::vector<int> domains=old_domains;
    Polynomial previous_product;
    int max_original=0,parent_first_coefficient=-1;
    for(int level=2;level<=(h==1?3:2);++level){
        if(level==3)inputs={
            ring.add(previous_product,ring.variable(q0)),
            ring.add(one,ring.add(previous_product,L))};
        std::vector<Polynomial> actual_virtual_inputs;
        for(std::size_t j=0;j<inputs.size();++j){
            auto value=ring.substitute(inputs[j],virtual_values);
            actual_virtual_inputs.push_back(value);
            comparison(out,ring,tag+"/L"+std::to_string(level)+"/input-"+std::to_string(j),
                       inputs[j],low_symbol,high_symbol,h,k,evaluations,
                       weighted_core,conditioned_core,old_domains,condition);
            emit_certificate(out,ring,tag+"/L"+std::to_string(level)+"/input-Boolean-"+std::to_string(j),
                boolean_division(ring,ring.subtract(ring.multiply(value,value),value),domains),
                domains,{},2*degree(value));
        }
        Block block=make_block(ring,inputs,h,fresh);
        if(level==2)parent_first_coefficient=block.variables[0][0];
        int delta=0;
        for(const auto& g:actual_virtual_inputs)delta=std::max(delta,degree(g));
        out<<"{\"type\":\"later_block\",\"fixture\":\""<<tag<<"\",\"original_level\":"<<level
           <<",\"formal_block\":";write_block(out,block);
        out<<",\"virtual_inputs\":";write_polynomials(out,actual_virtual_inputs);
        out<<",\"virtual_product_degree\":"<<h*(delta+1)<<",\"virtual_companion_degrees\":[";
        for(std::size_t j=0;j<inputs.size();++j){
            if(j)out<<',';
            out<<degree(actual_virtual_inputs[j])+h*(delta+1);
        }
        out<<"]}\n";
        comparison(out,ring,tag+"/L"+std::to_string(level)+"/product",block.product,
                   low_symbol,high_symbol,h,k,evaluations,
                   weighted_core,conditioned_core,old_domains,condition);
        for(std::size_t j=0;j<block.companions.size();++j){
            int original=weighted_degree(block.companions[j],low_symbol,high_symbol,2*h);
            max_original=std::max(max_original,original);
            need(degree(actual_virtual_inputs[j])+h*(delta+1)<=k*original,"new companion degree");
            comparison(out,ring,tag+"/L"+std::to_string(level)+"/companion-"+std::to_string(j),
                       block.companions[j],low_symbol,high_symbol,h,k,evaluations,
                       weighted_core,conditioned_core,old_domains,condition);
        }
        if(level==2){
            std::map<int,int> point;
            for(int id=0;id<fresh;++id)point[id]=0;
            point[low_symbol]=1;point[high_symbol]=1;point[parent_first_coefficient]=1;
            int actual=ring.evaluate(block.product,point);
            point[high_symbol]=0;
            int virt=ring.evaluate(block.product,point);
            need(actual==1&&virt==0,"unweighted deletion control");
            out<<"{\"type\":\"unweighted_control\",\"fixture\":\""<<tag
               <<"\",\"old_bits_all_zero\":true,\"parent_coefficient_one\":"
               <<parent_first_coefficient<<",\"actual_product\":1,\"virtual_product\":0,"
                 "\"weight_value\":0,\"condition_value\":1}\n";
        }
        for(const auto& row:block.variables)domains.insert(domains.end(),row.begin(),row.end());
        previous_product=block.product;
    }
    out<<"{\"type\":\"fixture_summary\",\"name\":\""<<tag
       <<"\",\"maximum_original_companion_degree\":"<<max_original
       <<",\"conditioned_refutation_ceiling\":"<<k*max_original
       <<",\"weighted_target_ceiling\":"<<k*(max_original+1)<<",\"passed\":true}\n";
}
void nonlinear_control(std::ostream& out){
    Ring ring(2,32);auto one=ring.constant(1);
    constexpr int free_variables=7,rank=6,old=10;
    auto f=ring.multiply(ring.multiply(ring.variable(7),ring.variable(8)),ring.variable(9));
    std::vector<int> domains(old);std::iota(domains.begin(),domains.end(),0);
    std::vector<Polynomial> inputs;
    int fresh=old;
    out<<"{\"type\":\"nonlinear_control\",\"free_variables\":7,\"input_rank\":6,"
         "\"conditioning_weight\":";
    write_json(out,f);out<<",\"source_flats\":[";
    for(int j=1;j<=rank;++j){
        Block bottom=make_block(ring,{ring.subtract(one,ring.variable(0)),
                                     ring.subtract(one,ring.variable(j))},1,fresh);
        std::map<int,Polynomial> map{{bottom.variables[0][0],one},
                                    {bottom.variables[0][1],ring.variable(0)}};
        auto image=ring.substitute(bottom.product,map);
        need(image==ring.multiply(ring.variable(0),ring.variable(j)),"quadratic source image");
        inputs.push_back(image);
        if(j>1)out<<',';
        out<<"{\"block\":";write_block(out,bottom);
        out<<",\"coefficient_images\":[["<<bottom.variables[0][0]<<',';
        write_json(out,one);out<<"],["<<bottom.variables[0][1]<<',';
        write_json(out,ring.variable(0));out<<"]],\"image\":";
        write_json(out,image);out<<'}';
    }
    out<<"]}\n";
    for(int j=0;j<rank;++j)
        emit_certificate(out,ring,"nonlinear/input-Boolean-"+std::to_string(j),
            boolean_division(ring,ring.subtract(ring.multiply(inputs[j],inputs[j]),inputs[j]),domains),
            domains,{},4);
    std::vector<int> zero_points,monomials;
    for(int mask=0;mask<(1<<free_variables);++mask)
        if(!(mask&1)||(mask&~1)==0)zero_points.push_back(mask|(7<<7));
    for(int mask=0;mask<(1<<free_variables);++mask)
        if(__builtin_popcount(unsigned(mask))<=2)monomials.push_back(mask);
    need(zero_points.size()==65&&monomials.size()==29,"nonlinear domain counts");
    out<<"{\"type\":\"restriction_space\",\"zero_points\":";
    array(out,zero_points);out<<",\"monomials\":";array(out,monomials);out<<"}\n";
    bp::Space image(int(zero_points.size()));
    for(std::size_t j=0;j<monomials.size();++j){
        auto raw=bp::blank(int(zero_points.size()));
        for(std::size_t i=0;i<zero_points.size();++i)
            if((zero_points[i]&monomials[j])==monomials[j])bp::flip(raw,int(i));
        std::vector<int> trace;
        auto reduced=image.reduce(raw,&trace);
        int pivot=bp::highest(reduced);
        if(pivot>=0)image.insert_reduced(reduced,pivot);
        out<<"{\"type\":\"restriction_column\",\"monomial\":"<<monomials[j]<<",\"raw\":";
        bp::sparse_json(out,raw);out<<",\"trace\":";array(out,trace);
        out<<",\"pivot\":"<<pivot<<",\"reduced\":";bp::sparse_json(out,reduced);out<<"}\n";
    }
    need(image.rank==23,"actual nonlinear restriction dimension");
    auto opposite=ring.subtract(one,ring.variable(7));
    emit_certificate(out,ring,"nonzero-factors-zero-product",
                     boolean_division(ring,ring.multiply(f,opposite),domains),domains,{},4);
    out<<"{\"type\":\"nonlinear_summary\",\"input_rank\":6,\"zero_points_on_weight_one_slice\":65,"
         "\"degree_two_restriction_rank\":23,\"affine_rank_prediction\":2,"
         "\"conditioning_leaves_free_variables_unchanged\":true,"
         "\"nonzero_product_control\":";
    write_polynomials(out,{f,opposite});out<<",\"passed\":true}\n";
}
int main(int argc,char** argv){
    try{
        need(argc==3&&std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];
        need(!std::filesystem::exists(path),"refusing existing output");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot create output");
        out<<"{\"type\":\"schema\",\"version\":1,\"field\":2,"
               "\"representation\":\"later polynomials formal in bottom selectors; differences factored before evaluation\","
               "\"scope\":\"exact source images and nonlinear dimension controls, not a full PHP refutation\"}\n";
        fixture(1,out);fixture(2,out);nonlinear_control(out);
        out<<"{\"type\":\"summary\",\"fixtures\":2,\"NS_certificates\":"<<certificate_count
           <<",\"unweighted_controls\":2,\"nonlinear_restriction_rank\":23,\"passed\":true}\n";
        out.close();need(bool(out),"write failed");
        std::cout<<"Passed "<<certificate_count<<" complete source-image NS certificates; "
                    "the nonlinear rank-six tuple has restriction rank 23 rather than two.\n";
    }catch(const std::exception& error){std::cerr<<"ERROR: "<<error.what()<<'\n';return 1;}
}
