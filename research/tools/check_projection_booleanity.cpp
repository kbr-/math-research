// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Flattened projection normalizers and their exact Booleanity-only interface.
#include "domain_polynomial.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
using namespace domain_polynomial;
void need(bool condition,const std::string& why){if(!condition)throw std::runtime_error(why);}
int certify(const Ring& ring,const Polynomial& target,const std::vector<Polynomial>& axioms,
            const std::vector<Polynomial>& coefficients){
    need(axioms.size()==coefficients.size(),"certificate arity");Polynomial sum;int result=0;
    for(size_t i=0;i<axioms.size();i++)if(!coefficients[i].empty() && !axioms[i].empty()){
        auto term=ring.multiply(coefficients[i],axioms[i]);ring.accumulate(sum,term);
        result=std::max(result,degree(term));
    }
    need(sum==target,"exact certificate reconstruction");return result;
}
void save(std::ostream& out,const std::string& name,const Polynomial& target,
          const std::vector<Polynomial>& axioms,const std::vector<Polynomial>& coefficients,int d){
    out<<"{\"record\":\"certificate\",\"name\":\""<<name<<"\",\"degree\":"<<d<<",\"target\":";
    write_json(out,target);out<<",\"axioms\":";write_polynomials(out,axioms);
    out<<",\"cofactors\":";write_polynomials(out,coefficients);out<<"}\n";
}
void run_case(std::ostream& out,int p,int arity){
    Ring ring(p,64);auto one=ring.constant(1),zero=ring.constant(0);const int h=2;
    std::vector<Polynomial> inputs;
    for(int j=0;j<arity;j++)inputs.push_back(ring.variable(j));
    auto b=ring.variable(arity);int fresh=arity+1;
    Block argument=make_block(ring,inputs,h,fresh);auto a=argument.product;
    Block inner=make_block(ring,{a,b},h,fresh);
    std::vector<Polynomial> original_root_inputs{ring.subtract(one,inner.product)};
    original_root_inputs.insert(original_root_inputs.end(),inputs.begin(),inputs.end());
    // Preserve the original root in factored form to avoid expanding a large
    // product that is immediately specialized. All companion images are explicit.
    out<<"{\"record\":\"case\",\"p\":"<<p<<",\"h\":"<<h<<",\"argument_arity\":"<<arity
       <<",\"flattened_root_arity\":"<<arity+1<<",\"wrapped_root_arity\":2,\"argument\":";
    write_block(out,argument);out<<",\"inner\":";write_block(out,inner);
    out<<",\"root_inputs\":";write_polynomials(out,original_root_inputs);
    int root_product_degree=h*(degree(inner.product)+1);
    out<<",\"root_product_degree\":"<<root_product_degree<<"}\n";
    Polynomial Ha=ring.subtract(ring.multiply(a,a),a),Hb=ring.subtract(ring.multiply(b,b),b);
    std::vector<Polynomial> bool_cofactors;
    for(const auto& q:argument.prefix)bool_cofactors.push_back(ring.subtract(zero,q));
    int bool_degree=certify(ring,Ha,argument.companions,bool_cofactors);
    need(bool_degree==2*degree(a),"sharp argument Booleanity degree");
    save(out,"argument_booleanity",Ha,argument.companions,bool_cofactors,bool_degree);
    std::map<int,Polynomial> packing;
    for(int u=0;u<h;u++)for(int j=0;j<2;j++)packing[inner.variables[u][j]]=ring.constant(u==j?1:0);
    auto packed=ring.substitute(inner.product,packing);
    need(packed==ring.multiply(ring.subtract(one,a),ring.subtract(one,b)),"inner packing");
    std::vector<Polynomial> root_inputs{ring.subtract(one,packed)};
    root_inputs.insert(root_inputs.end(),inputs.begin(),inputs.end());
    std::vector<Polynomial> beta{a};beta.insert(beta.end(),argument.prefix.begin(),argument.prefix.end());
    auto H=normalizer_error(ring,root_inputs,beta);
    auto minus_one_b=ring.subtract(b,one);
    need(H==ring.multiply(minus_one_b,Ha),"flattened projection error");
    for(size_t i=0;i<root_inputs.size();i++){
        auto target=ring.multiply(root_inputs[i],H);
        std::vector<Polynomial> macro_axioms{Ha,Hb},cof{ring.multiply(root_inputs[i],minus_one_b),zero};
        int d=certify(ring,target,macro_axioms,cof);
        int original=degree(original_root_inputs[i])+root_product_degree;
        need(d<=original,"projection original companion budget");
        save(out,"root_image_via_booleanity",target,macro_axioms,cof,d);
        std::vector<Polynomial> flat;
        for(const auto& q:bool_cofactors)flat.push_back(ring.multiply(cof[0],q));
        int flat_degree=certify(ring,target,argument.companions,flat);
        need(flat_degree<=original,"flattened Booleanity budget");
        save(out,"root_image_flattened",target,argument.companions,flat,flat_degree);
    }
    for(int j=0;j<2;j++){
        auto target=ring.substitute(inner.companions[j],packing);
        std::vector<Polynomial> cof{zero,zero};cof[j]=j==0?minus_one_b:ring.subtract(a,one);
        int d=certify(ring,target,{Ha,Hb},cof);need(d<=degree(inner.companions[j]),"inner image budget");
        save(out,"inner_image_via_booleanity",target,{Ha,Hb},cof,d);
    }
    // The unflattened two-input assignment cannot be applied as if the other
    // root coordinates were absent.
    std::vector<Polynomial> wrong(root_inputs.size());wrong[0]=a;wrong[1]=one;
    auto wrong_error=normalizer_error(ring,root_inputs,wrong);
    need(!(wrong_error==H),"flattening control is vacuous");
    std::map<int,Polynomial> zeros;
    for(const auto& row:argument.variables)for(int v:row)zeros[v]=zero;
    need(ring.substitute(a,zeros)==one && ring.substitute(Ha,zeros).empty(),"Booleanity port after zero");
    need(ring.substitute(H,zeros).empty(),"projection error after zero");
    need(ring.substitute(packed,zeros).empty(),"inner product after zero");
    auto direct=ring.substitute(argument.companions[0],zeros);
    need(direct==inputs[0] && !direct.empty(),"direct companion must not disappear");
    std::map<int,int> model;for(int j=0;j<=arity;j++)model[j]=j==0?1:0;
    need(ring.evaluate(direct,model)==1,"direct companion countermodel");
    for(int j=0;j<=arity;j++){
        auto x=ring.variable(j);need(ring.evaluate(ring.subtract(ring.multiply(x,x),x),model)==0,"control Boolean domain");
    }
    out<<"{\"record\":\"controls\",\"flattening_error\":";write_json(out,ring.subtract(wrong_error,H));
    out<<",\"booleanity_image_is_zero\":true,\"direct_companion_image\":";write_json(out,direct);
    out<<",\"domain_model\":[";
    for(int j=0;j<=arity;j++){if(j)out<<',';out<<model[j];}
    out<<"],\"direct_companion_value\":1}\n";
    // All upper coefficient-field images use domains only. Argument zeroing
    // turns beta=(a,V_1,...) into (1,0,...), so these targets then vanish.
    std::vector<int> powers(argument.variables.back().back()+1,p);
    for(int j=0;j<=arity;j++)powers[j]=2;
    for(size_t i=0;i<beta.size();i++){
        auto f=ring.subtract(ring.power(beta[i],p),beta[i]);auto reduction=domain_reduce(ring,f,powers);
        verify_reduction(ring,f,powers,reduction);need(reduction.remainder.empty(),"upper field-image certificate");
        need(ring.substitute(f,zeros).empty(),"field target after zero");
        out<<"{\"record\":\"upper_field_image\",\"coordinate\":"<<i<<",\"target\":";write_json(out,f);
        out<<",\"domain_powers\":[";
        for(size_t j=0;j<powers.size();j++){if(j)out<<',';out<<powers[j];}
        out<<"],\"certificate\":";write_reduction(out,reduction);out<<"}\n";
    }
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");std::ofstream out(argv[2]);need(bool(out),"open output");
        out<<"{\"schema\":1,\"suite\":\"projection_booleanity\",\"seed\":null,\"scope\":\"local source-shaped identities and Booleanity interfaces, not a PHP refutation\"}\n";
        for(int p:{2,3})for(int arity:{3,4})run_case(out,p,arity);
        out<<"{\"record\":\"summary\",\"cases\":4,\"all_passed\":true}\n";
        out.close();need(bool(out),"write output");std::cout<<"Four flattened projection and Booleanity-interface cases passed.\n";
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
