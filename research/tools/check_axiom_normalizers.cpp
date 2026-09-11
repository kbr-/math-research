// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Check exact covered-disjunction witnesses and earlier-axiom normalizers.
#include "ens_symbolic.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace ens_symbolic;
void need(bool condition,const std::string& message){
    if(!condition)throw std::runtime_error(message);
}
void check_covered(std::ostream& out){
    int cases=0,images_checked=0;
    for(int p:{2,3,5,7})for(int h:{1,2}){
        Ring ring(p);int fresh=3;
        std::vector<Polynomial> g{ring.subtract(ring.constant(1),ring.variable(0)),
                                  ring.subtract(ring.constant(1),ring.variable(1))};
        Block a=make_block(ring,g,h,fresh);
        std::vector<Polynomial> outer_inputs=g;outer_inputs.push_back(a.product);
        outer_inputs.push_back(ring.variable(2));
        Block outer=make_block(ring,outer_inputs,h,fresh);
        std::vector<Polynomial> beta=a.prefix;beta.push_back(ring.constant(1));beta.push_back(ring.constant(0));
        need(normalizer_error(ring,outer_inputs,beta).empty(),"covered-disjunction unit identity");
        auto images=coefficient_images(ring,outer,beta);
        need(ring.substitute(outer.product,images).empty(),"covered product image");
        for(const Polynomial& companion:outer.companions){
            need(ring.substitute(companion,images).empty(),"covered companion image");images_checked++;
        }
        auto missing=beta;missing[2]=ring.constant(0);
        need(!normalizer_error(ring,outer_inputs,missing).empty(),"omitted product input control");
        missing=beta;missing[0]=ring.constant(0);
        need(!normalizer_error(ring,outer_inputs,missing).empty(),"omitted prefix control");
        int maximum=1;
        for(const Polynomial& coefficient:beta)maximum=std::max(maximum,degree(coefficient));
        out<<"{\"record\":\"covered_disjunction\",\"p\":"<<p<<",\"h\":"<<h<<",\"old_variables\":3,\"A_block\":";
        write_block(out,a);out<<",\"outer_block\":";write_block(out,outer);
        out<<",\"normalizer_coefficients\":";write_polynomials(out,beta);
        out<<",\"substitution_degree\":"<<maximum
           <<",\"all_companions_vanish\":true,\"omission_controls\":2}\n";cases++;
    }
    out<<"{\"record\":\"covered_summary\",\"cases\":"<<cases<<",\"companion_images\":"<<images_checked<<"}\n";
    std::cout<<cases<<" covered disjunctions, "<<images_checked<<" identically zero companion images.\n";
}
void distribution_case(std::ostream& out,int p,int h,bool b_disjunction,bool c_disjunction,
                       int& compatible,int& incompatible){
    Ring ring(p);int fresh=5;
    Polynomial a=ring.variable(0),b,c=ring.variable(3);
    std::vector<Polynomial> b_inputs,c_inputs;
    Block b_block;
    if(b_disjunction){
        b_inputs={ring.subtract(ring.constant(1),ring.variable(1)),
                  ring.subtract(ring.constant(1),ring.variable(2))};
        b_block=make_block(ring,b_inputs,h,fresh);b=b_block.product;
    }else{
        b=ring.variable(1);b_inputs={ring.subtract(ring.constant(1),b)};
    }
    if(c_disjunction){
        c_inputs={ring.subtract(ring.constant(1),c),
                  ring.subtract(ring.constant(1),ring.variable(4))};
    }else{
        c_inputs={ring.subtract(ring.constant(1),c)};
    }
    std::vector<Polynomial> u_inputs{a,b};u_inputs.insert(u_inputs.end(),c_inputs.begin(),c_inputs.end());
    std::vector<Polynomial> v_inputs{a};v_inputs.insert(v_inputs.end(),b_inputs.begin(),b_inputs.end());
    Block u=make_block(ring,u_inputs,h,fresh),v=make_block(ring,v_inputs,h,fresh);
    std::vector<Polynomial> outer_inputs{u.product,v.product,a};
    outer_inputs.insert(outer_inputs.end(),c_inputs.begin(),c_inputs.end());
    Polynomial ub_times_b=ring.multiply(u.prefix[1],b);
    std::vector<Polynomial> beta{ring.constant(1),ub_times_b,
        ring.add(u.prefix[0],ring.multiply(ub_times_b,v.prefix[0]))};
    for(size_t j=0;j<c_inputs.size();j++)beta.push_back(u.prefix[j+2]);
    Polynomial h_poly=normalizer_error(ring,outer_inputs,beta),rhs;
    std::vector<Polynomial> cofactor,axiom;
    if(b_disjunction){
        for(size_t j=0;j<b_inputs.size();j++){
            cofactor.push_back(ring.multiply(u.prefix[1],v.prefix[j+1]));
            axiom.push_back(b_block.companions[j]);
        }
    }else{
        cofactor.push_back(ring.multiply(ring.constant(-1),ring.multiply(u.prefix[1],v.prefix[1])));
        axiom.push_back(ring.subtract(ring.multiply(b,b),b));
    }
    int certificate_degree=0;
    for(size_t j=0;j<cofactor.size();j++){
        ring.accumulate(rhs,ring.multiply(cofactor[j],axiom[j]));
        certificate_degree=std::max(certificate_degree,degree(cofactor[j])+degree(axiom[j]));
    }
    need(h_poly==rhs,"distribution normalizer identity");
    need(!h_poly.empty(),"earlier-axiom error control is vacuous");
    int delta=0,beta_degree=0;
    for(const Polynomial& g:outer_inputs)delta=std::max(delta,degree(g));
    for(const Polynomial& coefficient:beta)beta_degree=std::max(beta_degree,degree(coefficient));
    need(beta_degree<=3*delta && certificate_degree<=4*delta,"uniform local degree bounds");
    const int headroom=h*(delta+1);bool fits=certificate_degree<=headroom;
    if(fits)compatible++;else incompatible++;
    if(h>=4)need(fits,"large-accuracy original degree budget");
    out<<"{\"record\":\"distribution_normalizer\",\"p\":"<<p<<",\"h\":"<<h
       <<",\"B_is_disjunction\":"<<(b_disjunction?"true":"false")
       <<",\"C_is_disjunction\":"<<(c_disjunction?"true":"false")<<",\"old_variables\":5";
    if(b_disjunction){out<<",\"B_block\":";write_block(out,b_block);}
    out<<",\"U_block\":";write_block(out,u);out<<",\"V_block\":";write_block(out,v);
    out<<",\"outer_inputs\":";write_polynomials(out,outer_inputs);
    out<<",\"normalizer_coefficients\":";write_polynomials(out,beta);
    out<<",\"H\":";write_json(out,h_poly);
    out<<",\"certificate_cofactors\":";write_polynomials(out,cofactor);
    out<<",\"certificate_axioms\":";write_polynomials(out,axiom);
    out<<",\"input_degree\":"<<delta<<",\"coefficient_degree\":"<<beta_degree
       <<",\"H_certificate_degree\":"<<certificate_degree<<",\"original_factor_degree\":"<<headroom
       <<",\"fits_original_companion_budget\":"<<(fits?"true":"false")
       <<",\"omitted_earlier_axiom_error_nonzero\":true}\n";
}
void check_composition(std::ostream& out){
    for(int p:{2,3,5,7}){
        Ring ring(p);int fresh=2;
        Block base=make_block(ring,{ring.variable(0),ring.variable(1)},2,fresh);
        std::vector<Polynomial> inputs=base.inputs;inputs.push_back(base.product);
        Block first=make_block(ring,inputs,2,fresh);
        std::vector<Polynomial> beta=base.prefix;beta.push_back(ring.constant(1));
        auto phi=coefficient_images(ring,first,beta);
        std::vector<Polynomial> upper_inputs=inputs;upper_inputs.push_back(first.product);
        std::vector<Polynomial> raw_upper=first.prefix;raw_upper.push_back(ring.constant(1));
        need(normalizer_error(ring,upper_inputs,raw_upper).empty(),"upper source normalizer");
        std::vector<Polynomial> mapped_inputs,mapped_beta;
        for(const Polynomial& polynomial:upper_inputs)mapped_inputs.push_back(ring.substitute(polynomial,phi));
        for(const Polynomial& polynomial:raw_upper)mapped_beta.push_back(ring.substitute(polynomial,phi));
        need(normalizer_error(ring,mapped_inputs,mapped_beta).empty(),"composed upper normalizer");
        for(size_t j=0;j<first.prefix.size();j++){
            need(mapped_beta[j]==beta[j],"selected block prefix does not collapse to first coefficients");
        }
        need(!normalizer_error(ring,mapped_inputs,raw_upper).empty(),"uncomposed coefficient control");
        int actual=1,first_degree=1,raw_second_degree=1;
        for(const Polynomial& polynomial:beta)first_degree=std::max(first_degree,degree(polynomial));
        for(const Polynomial& polynomial:raw_upper)raw_second_degree=std::max(raw_second_degree,degree(polynomial));
        for(const Polynomial& polynomial:mapped_beta)actual=std::max(actual,degree(polynomial));
        actual=std::max(actual,first_degree);
        out<<"{\"record\":\"triangular_composition\",\"p\":"<<p<<",\"h\":2,\"base_block\":";
        write_block(out,base);out<<",\"first_selected_block\":";write_block(out,first);
        out<<",\"first_coefficients\":";write_polynomials(out,beta);
        out<<",\"upper_source_inputs\":";write_polynomials(out,upper_inputs);
        out<<",\"upper_raw_coefficients\":";write_polynomials(out,raw_upper);
        out<<",\"upper_composed_coefficients\":";write_polynomials(out,mapped_beta);
        out<<",\"coarse_product_bound\":"<<first_degree*raw_second_degree
           <<",\"actual_substitution_degree\":"<<actual
           <<",\"uncomposed_coefficient_control_rejected\":true}\n";
    }
    std::cout<<"Four triangular compositions: selected prefixes collapse to their first coefficient vectors.\n";
}
int main(int argc,char** argv){
    try{
        std::string path;
        for(int j=1;j<argc;j++){
            std::string arg=argv[j];
            if(arg=="--out" && j+1<argc)path=argv[++j];
            else throw std::runtime_error("Usage: check_axiom_normalizers --out NEW_PATH");
        }
        need(!path.empty() && !std::filesystem::exists(path),"new --out required");
        std::ofstream out(path);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"axiom_normalizers\",\"arithmetic\":\"exact\"}\n";
        check_covered(out);int cases=0,compatible=0,incompatible=0;
        for(int p:{2,3,5,7}){
            for(int h:{1,2})for(bool b:{false,true})for(bool c:{false,true}){
                distribution_case(out,p,h,b,c,compatible,incompatible);cases++;
            }
            distribution_case(out,p,4,false,false,compatible,incompatible);cases++;
        }
        out<<"{\"record\":\"distribution_summary\",\"cases\":"<<cases
           <<",\"compatible_certificates\":"<<compatible
           <<",\"local_certificates_exceeding_original_budget\":"<<incompatible<<"}\n";
        std::cout<<cases<<" distribution identities: "<<compatible<<" fit original factor budgets; "
                 <<incompatible<<" small-accuracy certificates require extra accounting.\n";
        check_composition(out);out<<"{\"record\":\"summary\",\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failure");return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
