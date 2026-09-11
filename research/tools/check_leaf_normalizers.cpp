// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact positive-leaf unit extraction and triangular witness degree controls.
#include "domain_polynomial.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
using namespace domain_polynomial;
void need(bool value,const std::string& why){if(!value)throw std::runtime_error(why);}
int certificate(const Ring& ring,const Polynomial& target,const std::vector<Polynomial>& axioms,
                const std::vector<Polynomial>& cofactors){
    need(axioms.size()==cofactors.size(),"certificate arity");Polynomial sum;int d=0;
    for(size_t i=0;i<axioms.size();i++)if(!cofactors[i].empty() && !axioms[i].empty()){
        auto term=ring.multiply(cofactors[i],axioms[i]);ring.accumulate(sum,term);d=std::max(d,degree(term));
    }
    need(sum==target,"certificate reconstruction");return d;
}
void write_certificate(std::ostream& out,const std::string& name,const Polynomial& target,
                       const std::vector<Polynomial>& axioms,const std::vector<Polynomial>& cofactors,int d){
    out<<"{\"record\":\"certificate\",\"name\":\""<<name<<"\",\"degree\":"<<d<<",\"target\":";
    write_json(out,target);out<<",\"axioms\":";write_polynomials(out,axioms);
    out<<",\"cofactors\":";write_polynomials(out,cofactors);out<<"}\n";
}
void write_images(std::ostream& out,const std::map<int,Polynomial>& images){
    out<<'[';bool comma=false;for(const auto& [id,value]:images){
        if(comma)out<<',';
        comma=true;out<<'['<<id<<',';write_json(out,value);out<<']';
    }out<<']';
}
void leaf(std::ostream& out,const Ring& ring,const Polynomial& value,const Block& inner,
          const Block& proper,const Block& private_copy,const std::map<int,Polynomial>& earlier,
          const std::vector<int>& old_powers){
    auto one=ring.constant(1);
    // U = (1-value)U + value*(1-P)U + U*(value P).
    std::vector<Polynomial> axioms{inner.companions[0],private_copy.companions[0],private_copy.companions[1]};
    std::vector<Polynomial> cofactors{private_copy.product,value,one};
    int source_degree=certificate(ring,private_copy.product,axioms,cofactors);
    write_certificate(out,"positive_source_leaf",private_copy.product,axioms,cofactors,source_degree);
    auto zeros=coefficient_images(ring,private_copy,std::vector<Polynomial>(2));
    std::vector<Polynomial> unit_axioms,unit_cofactors;
    for(const auto& f:axioms)unit_axioms.push_back(ring.substitute(f,zeros));
    for(const auto& q:cofactors)unit_cofactors.push_back(ring.substitute(q,zeros));
    int unit_degree=certificate(ring,one,unit_axioms,unit_cofactors);
    write_certificate(out,"extracted_unit",one,unit_axioms,unit_cofactors,unit_degree);
    std::vector<Polynomial> beta{unit_cofactors[1],unit_cofactors[2]};
    auto H=normalizer_error(ring,proper.inputs,beta);
    need(H==inner.companions[0],"normalizer error is older companion");
    auto local=coefficient_images(ring,proper,beta);
    auto total=earlier;
    for(const auto& [variable,q]:local)total[variable]=ring.substitute(q,earlier);
    out<<"{\"record\":\"normalizer\",\"source_degree\":"<<source_degree<<",\"unit_degree\":"<<unit_degree
       <<",\"local_images\":";write_images(out,local);out<<",\"composed_images\":";write_images(out,total);out<<"}\n";
    for(size_t i=0;i<proper.inputs.size();i++){
        Polynomial target=ring.substitute(proper.companions[i],local);
        std::vector<Polynomial> old{inner.companions[0]},q{proper.inputs[i]};
        int d=certificate(ring,target,old,q);
        write_certificate(out,"local_companion_image",target,old,q,d);
        auto final_target=ring.substitute(target,earlier);
        std::vector<Polynomial> final_old{ring.substitute(old[0],earlier)},final_q{ring.substitute(q[0],earlier)};
        int final_degree=certificate(ring,final_target,final_old,final_q);
        write_certificate(out,"composed_companion_image",final_target,final_old,final_q,final_degree);
        need(ring.substitute(proper.companions[i],total)==final_target,"simultaneous companion composition");
    }
    for(const auto& b:beta){
        auto field=ring.subtract(ring.power(b,ring.p),b);auto proof=domain_reduce(ring,field,old_powers);
        verify_reduction(ring,field,old_powers,proof);need(proof.remainder.empty(),"coefficient field image");
        out<<"{\"record\":\"local_field_image\",\"target\":";write_json(out,field);
        out<<",\"domain_powers\":[";
        for(size_t i=0;i<old_powers.size();i++){if(i)out<<',';out<<old_powers[i];}
        out<<"],\"certificate\":";write_reduction(out,proof);out<<"}\n";
    }
    need(!H.empty(),"nonzero older-error control");
    need(!(ring.substitute(proper.product,total)==proper.product),"stale proper value control");
}
void source_cases(std::ostream& out,int p){
    Ring ring(p,64);auto one=ring.constant(1),x=ring.variable(0),y=ring.variable(1);int fresh=2;
    Block inner0=make_block(ring,{x,y},1,fresh);
    Block proper0=make_block(ring,{ring.subtract(one,inner0.product),ring.subtract(one,x)},1,fresh);
    Block inner1=make_block(ring,{proper0.product,y},1,fresh);
    Block proper1=make_block(ring,{ring.subtract(one,inner1.product),ring.subtract(one,proper0.product)},1,fresh);
    int proper_variables=fresh;Block private0=make_block(ring,proper0.inputs,1,fresh);
    Block private1=make_block(ring,proper1.inputs,1,fresh);
    out<<"{\"record\":\"source_case\",\"p\":"<<p<<",\"h\":1,\"proper_variables\":"<<proper_variables
       <<",\"blocks\":[";
    for(const Block* b:{&inner0,&proper0,&inner1,&proper1,&private0,&private1}){
        if(b!=&inner0)out<<',';
        write_block(out,*b);
    }out<<"]}\n";
    std::vector<int> powers0(4,p);powers0[0]=powers0[1]=2;
    leaf(out,ring,x,inner0,proper0,private0,{},powers0);
    auto earlier=coefficient_images(ring,proper0,{x,one});
    std::vector<int> powers1(8,p);powers1[0]=powers1[1]=2;
    leaf(out,ring,proper0.product,inner1,proper1,private1,earlier,powers1);
    auto all=earlier;
    for(const auto& [id,q]:coefficient_images(ring,proper1,{proper0.product,one}))
        all[id]=ring.substitute(q,earlier);
    need(ring.substitute(proper1.product,all)==ring.multiply(ring.substitute(proper0.product,all),
                                                          ring.substitute(inner1.product,all)),"nested proper image");
    need(!(ring.substitute(inner1.companions[0],all)==inner1.companions[0]),"retained later input control");
    out<<"{\"record\":\"source_passed\",\"p\":"<<p<<",\"nonzero_errors\":2,\"stale_input_rejected\":true}\n";
}
void growth_control(std::ostream& out,int p){
    Ring ring(p,64);auto one=ring.constant(1),x=ring.variable(0),y=ring.variable(1),g1=ring.subtract(one,x);
    int fresh=2;Block first=make_block(ring,{x,g1},1,fresh),second=make_block(ring,{x,g1},1,fresh);
    auto r=ring.variable(first.variables[0][0]);
    auto witness=[&](const Polynomial& z){auto square=ring.power(z,2);return std::vector<Polynomial>{
        ring.add(one,ring.multiply(square,g1)),ring.subtract(one,ring.multiply(square,x))};};
    auto beta0=witness(y),beta1=witness(r);
    need(normalizer_error(ring,first.inputs,beta0).empty(),"first syzygy unit");
    need(normalizer_error(ring,second.inputs,beta1).empty(),"second syzygy unit");
    auto images=coefficient_images(ring,first,beta0);
    for(const auto& [id,q]:coefficient_images(ring,second,beta1))images[id]=ring.substitute(q,images);
    int composed=0;
    for(const auto& [id,q]:images){(void)id;composed=std::max(composed,degree(q));}
    need(composed==7 && composed>3 && composed<=9,"triangular degree-growth control");
    for(const Block* b:{&first,&second})for(const auto& e:b->companions)
        need(ring.substitute(e,images).empty(),"zero companion image");
    out<<"{\"record\":\"growth_control\",\"p\":"<<p<<",\"local_degree\":3,\"levels\":2,"
          "\"composed_degree\":"<<composed<<",\"degree_bound\":9,\"raw_local_degree_bound_rejected\":true,"
          "\"scope\":\"prescribed witnesses only; constant alternative normalizers also exist\",\"images\":";
    write_images(out,images);out<<"}\n";
    for(const auto& [id,q]:images){
        auto field=ring.subtract(ring.power(q,p),q);auto cert=domain_reduce(ring,field,{2,2});
        verify_reduction(ring,field,{2,2},cert);need(cert.remainder.empty(),"composed field image");
        out<<"{\"record\":\"composed_field_image\",\"variable\":"<<id<<",\"target\":";write_json(out,field);
        out<<",\"certificate\":";write_reduction(out,cert);out<<"}\n";
    }
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");std::ofstream out(argv[2]);need(bool(out),"open output");
        out<<"{\"schema\":1,\"suite\":\"leaf_normalizers\",\"seed\":null,\"arithmetic\":\"exact ordinary polynomials\"}\n";
        for(int p:{2,3}){source_cases(out,p);growth_control(out,p);}
        out<<"{\"record\":\"summary\",\"nested_source_cases\":2,\"extracted_leaves\":4,\"degree_growth_controls\":2,\"all_passed\":true}\n";
        out.close();need(bool(out),"write output");
        std::cout<<"Four leaf extractions and two triangular degree-growth controls passed over F2/F3.\n";
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
