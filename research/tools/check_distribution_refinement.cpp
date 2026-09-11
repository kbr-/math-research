// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Refined distribution budgets and coordinate-weighted recursive prefixes.
#include "domain_polynomial.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace domain_polynomial;
void need(bool ok,const std::string& text) {if(!ok)throw std::runtime_error(text);}
Polynomial frobenius(const Ring& ring,const Polynomial& q) {
    Polynomial result;
    for(const auto& [monomial,c]:q) {
        Monomial power;
        for(int v:monomial)for(int j=0;j<ring.p;j++)power.push_back(v);
        need(power.size()<=size_t(ring.degree_limit),"Frobenius degree guard");
        result.emplace(std::move(power),c);
    }
    return result;
}
int certificate(std::ostream& out,const Ring& ring,const std::string& name,
                const Polynomial& target,const std::vector<Polynomial>& axioms,
                const std::vector<Polynomial>& cof,int bound) {
    need(axioms.size()==cof.size(),"certificate arity");
    Polynomial sum;int used=0;
    for(size_t i=0;i<cof.size();i++) {
        auto term=ring.multiply(cof[i],axioms[i]);ring.accumulate(sum,term);used=std::max(used,degree(term));
    }
    need(sum==target && used<=bound,"certificate "+name);
    out<<"{\"record\":\"certificate\",\"name\":\""<<name<<"\",\"target\":";write_json(out,target);
    out<<",\"axioms\":";write_polynomials(out,axioms);out<<",\"cofactors\":";write_polynomials(out,cof);
    out<<",\"degree\":"<<used<<",\"bound\":"<<bound<<"}\n";return used;
}
std::vector<Polynomial> beta(const Ring& ring,const std::vector<Polynomial>& U,
                             const std::vector<Polynomial>& V,const Polynomial& b) {
    std::vector<Polynomial> result{ring.constant(1),ring.multiply(U[1],b),
        ring.add(U[0],ring.multiply(ring.multiply(U[1],b),V[0]))};
    result.insert(result.end(),U.begin()+2,U.end());return result;
}
int weighted_prefix_max(const std::vector<Polynomial>& values,const std::vector<int>& weights) {
    need(values.size()==weights.size(),"prefix weight arity");int result=0;
    for(size_t i=0;i<values.size();i++)if(!values[i].empty())result=std::max(result,degree(values[i])+weights[i]);
    return result;
}
void local(std::ostream& out,int p,int h,bool wrapped,bool C_or,bool high_A=false) {
    Ring ring(p,96);auto one=ring.constant(1);const int width=3,old_Boolean=width+4;
    auto a=ring.variable(0);
    if(high_A)a=ring.power(ring.add(ring.power(ring.variable(0),2),ring.variable(1)),2);
    std::vector<Polynomial> g;
    for(int j=0;j<width;j++)g.push_back(ring.variable(2+j));
    std::vector<Polynomial> f=C_or?std::vector<Polynomial>{ring.variable(width+2),ring.variable(width+3)}
                                  :std::vector<Polynomial>{ring.subtract(one,ring.variable(width+2))};
    int next=old_Boolean;Block B=make_block(ring,g,h,next);auto b=B.product;
    std::vector<Polynomial> ui{a,b};ui.insert(ui.end(),f.begin(),f.end());
    std::vector<Polynomial> vi{a};
    if(wrapped)vi.push_back(ring.subtract(one,b));else vi.insert(vi.end(),g.begin(),g.end());
    Block U=make_block(ring,ui,h,next),V=make_block(ring,vi,h,next);
    std::vector<Polynomial> root_inputs{U.product,V.product,a};root_inputs.insert(root_inputs.end(),f.begin(),f.end());
    auto coefficients=beta(ring,U.prefix,V.prefix,b);
    auto H=normalizer_error(ring,root_inputs,coefficients);
    int sU=degree(U.product),sV=degree(V.product),Delta=0;
    std::vector<int> weights;for(const auto& input:root_inputs) {
        weights.push_back(degree(input));Delta=std::max(Delta,degree(input));
    }
    int root_budget=h*(Delta+1),weighted=weighted_prefix_max(coefficients,weights);
    out<<"{\"record\":\"local_case\",\"p\":"<<p<<",\"accuracy\":"<<h<<",\"B_wrapped\":"
       <<(wrapped?"true":"false")<<",\"C_OR\":"<<(C_or?"true":"false")
       <<",\"high_A\":"<<(high_A?"true":"false")<<",\"B\":";write_block(out,B);
    out<<",\"U\":";write_block(out,U);out<<",\"V\":";write_block(out,V);
    out<<",\"outer_inputs\":";write_polynomials(out,root_inputs);
    out<<",\"outer_first_vector_images\":";write_polynomials(out,coefficients);
    out<<",\"outer_product_budget\":"<<root_budget<<",\"refined_H_bound\":"<<sU+sV
       <<",\"weighted_prefix_max\":"<<weighted<<"}\n";
    std::vector<Polynomial> Hcof;
    if(wrapped) {
        auto hb=ring.subtract(ring.multiply(b,b),b),macro=ring.subtract({},ring.multiply(U.prefix[1],V.prefix[1]));
        certificate(out,ring,"Booleanity_port_error",H,{hb},{macro},sU+sV);
        for(const auto& prefix:B.prefix)Hcof.push_back(ring.multiply(ring.multiply(U.prefix[1],V.prefix[1]),prefix));
    } else {
        for(size_t j=0;j<g.size();j++)Hcof.push_back(ring.multiply(U.prefix[1],V.prefix[j+1]));
    }
    int Hdegree=certificate(out,ring,"flattened_argument_error",H,B.companions,Hcof,sU+sV);
    std::vector<Polynomial> all_axioms=root_inputs,all_cof=coefficients;
    all_axioms.insert(all_axioms.end(),B.companions.begin(),B.companions.end());
    all_cof.insert(all_cof.end(),Hcof.begin(),Hcof.end());
    certificate(out,ring,"distribution_input_unit",one,all_axioms,all_cof,sU+sV);
    bool fits=Hdegree<=root_budget;
    if(h>=2)need(fits && weighted<=root_budget,"h=2 refinement failed");
    if(h==1 && !high_A)need(!fits && degree(H)>root_budget,"h=1 nonadmissibility control");
    if(high_A)need(h==1 && fits && weighted>root_budget,"local/global h=1 distinction");
    out<<"{\"record\":\"local_budget\",\"normalizer_admissible\":"<<(fits?"true":"false")
       <<",\"intermediate_UV_companions_used\":false,\"argument_access\":\""
       <<(wrapped?"Booleanity_port":"direct_companions")<<"\"}\n";
    std::vector<int> powers(next,p);for(int i=0;i<old_Boolean;i++)powers[i]=2;
    for(size_t j=0;j<coefficients.size();j++) {
        const auto& q=coefficients[j];auto image=ring.subtract(frobenius(ring,q),q);
        if(q.size()<20)need(frobenius(ring,q)==ring.power(q,p),"small Frobenius control");
        auto proof=domain_reduce(ring,image,powers);verify_reduction(ring,image,powers,proof);
        need(proof.remainder.empty() && proof.degree<=p*degree(q),"local coefficient field");
        if(image.empty())continue;
        out<<"{\"record\":\"local_field_image\",\"coordinate\":"<<j<<",\"domain_powers\":[";
        for(size_t i=0;i<powers.size();i++) {if(i)out<<',';out<<powers[i];}
        out<<"],\"target\":";write_json(out,image);out<<",\"proof\":";write_reduction(out,proof);out<<"}\n";
    }
    // Match the exact remaining obligation, rather than dropping all B information.
    if(!wrapped || p==3) {
        std::map<int,int> point;for(int i=0;i<next;i++)point[i]=0;
        point[2]=1;if(!C_or)point[width+2]=1;
        int bvalue=wrapped?2:1;
        point[B.variables[0][0]]=ring.residue(1-bvalue);
        point[U.variables[0][1]]=wrapped?2:1;
        point[V.variables[0][1]]=wrapped?2:1;
        for(const auto& input:root_inputs)need(ring.evaluate(input,point)==0,"input-control model");
        auto hb=ring.subtract(ring.multiply(b,b),b);
        need(ring.evaluate(b,point)==bvalue,"controlled argument value");
        need(ring.evaluate(hb,point)==(wrapped?2:0),"argument obligation control");
        out<<"{\"record\":\"missing_argument_information\",\"wrapped\":"<<(wrapped?"true":"false")
           <<",\"B_value\":"<<bvalue<<",\"B_Booleanity_value\":"<<(wrapped?2:0)
           <<",\"all_outer_inputs_zero\":true,\"assignment\":[";
        for(int i=0;i<next;i++) {if(i)out<<',';out<<point[i];}
        out<<"]}\n";
    }
}
void recursive(std::ostream& out,int p) {
    Ring ring(p,96);auto one=ring.constant(1),x=ring.variable(0),y=ring.variable(1),z=ring.variable(2);
    int next=3;const int h=2;
    Block u0=make_block(ring,{x,y,ring.subtract(one,z)},h,next);
    Block v0=make_block(ring,{x,ring.subtract(one,y)},h,next);
    std::vector<Polynomial> psi_inputs{u0.product,v0.product,x,ring.subtract(one,z)};
    int lambda_u=4,lambda_v=4,lambda_psi=10;
    auto beta_psi=beta(ring,u0.prefix,v0.prefix,y);
    auto Hpsi=normalizer_error(ring,psi_inputs,beta_psi);
    auto Hy=ring.subtract(ring.multiply(y,y),y);
    auto psi_cof=ring.subtract({},ring.multiply(u0.prefix[1],v0.prefix[1]));
    certificate(out,ring,"recursive_inner_error",Hpsi,{Hy},{psi_cof},lambda_u+lambda_v);
    // Save the selected source root as a factored block; its later vectors are zero.
    std::vector<std::vector<int>> psi_variables;
    std::map<int,Polynomial> images;
    for(int u=0;u<h;u++) {
        std::vector<int> row;
        for(size_t j=0;j<psi_inputs.size();j++) {
            int id=next++;row.push_back(id);images[id]=u==0?beta_psi[j]:Polynomial{};
        }
        psi_variables.push_back(row);
    }
    Block v_outer=make_block(ring,{u0.product,x,ring.subtract(one,y)},h,next);
    std::vector<Polynomial> outer_inputs{Hpsi,v_outer.product,u0.product,x,ring.subtract(one,z)};
    auto beta_outer=beta(ring,beta_psi,v_outer.prefix,v0.product);
    auto Houter=normalizer_error(ring,outer_inputs,beta_outer);
    std::vector<Polynomial> Hcof;
    for(size_t i=0;i<v0.inputs.size();i++)Hcof.push_back(ring.multiply(beta_psi[1],v_outer.prefix[i+1]));
    certificate(out,ring,"recursive_outer_error",Houter,v0.companions,Hcof,20);
    std::vector<Polynomial> unit_axioms=outer_inputs,unit_cof=beta_outer;
    unit_axioms.insert(unit_axioms.end(),v0.companions.begin(),v0.companions.end());
    unit_cof.insert(unit_cof.end(),Hcof.begin(),Hcof.end());
    certificate(out,ring,"recursive_outer_unit",one,unit_axioms,unit_cof,20);
    int inner_weighted=weighted_prefix_max(beta_psi,{4,4,1,1});
    int outer_weighted=weighted_prefix_max(beta_outer,{10,10,4,1,1});
    need(inner_weighted<=lambda_psi && outer_weighted<=22 && degree(Hpsi)<=10 && degree(Houter)<=22,
         "recursive structural degree invariant");
    need(degree(beta_psi[2])>lambda_psi-4,"fresh-prefix shortcut was not falsified");
    int outer_start=next;
    for(int u=0;u<h;u++)for(size_t j=0;j<beta_outer.size();j++)
        images[next++]=u==0?beta_outer[j]:Polynomial{};
    out<<"{\"record\":\"recursive_case\",\"p\":"<<p<<",\"accuracy\":2,"
           "\"source_pattern\":\"D(U0,V0,W0), U0=X->(Y->Z), V0=X->Y, W0=X->Z\","
           "\"u0\":";write_block(out,u0);out<<",\"v0\":";write_block(out,v0);
    out<<",\"v_outer\":";write_block(out,v_outer);
    out<<",\"psi_inputs\":";write_polynomials(out,psi_inputs);
    out<<",\"psi_coefficient_variables\":[";
    for(size_t u=0;u<psi_variables.size();u++) {
        if(u)out<<',';
        out<<'[';for(size_t j=0;j<psi_variables[u].size();j++) {if(j)out<<',';out<<psi_variables[u][j];}out<<']';
    }
    out<<"],\"outer_first_variable\":"<<outer_start<<",\"outer_arity\":5,"
           "\"outer_inputs_after_inner_substitution\":";write_polynomials(out,outer_inputs);
    out<<",\"beta_inner\":";write_polynomials(out,beta_psi);
    out<<",\"beta_outer\":";write_polynomials(out,beta_outer);
    out<<",\"inner_product_degree\":"<<degree(Hpsi)<<",\"outer_product_degree\":"<<degree(Houter)
       <<",\"inner_weighted_prefix_max\":"<<inner_weighted<<",\"outer_weighted_prefix_max\":"<<outer_weighted
       <<",\"assigned_inner_prefix_degree\":"<<degree(beta_psi[2])
       <<",\"invalid_fresh_prefix_ceiling\":"<<lambda_psi-4<<"}\n";
    std::vector<int> powers(next,p);for(int i=0;i<3;i++)powers[i]=2;
    for(const auto& [variable,q]:images) {
        auto image=ring.subtract(frobenius(ring,q),q);
        auto proof=domain_reduce(ring,image,powers);verify_reduction(ring,image,powers,proof);
        need(proof.remainder.empty() && proof.degree<=p*degree(q),"recursive field proof");
        for(const auto& [removed,unused]:images) {
            (void)unused;need(proof.coefficients[removed].empty(),"recursive field proof used a removed field axiom");
        }
        if(image.empty())continue;
        out<<"{\"record\":\"recursive_field_image\",\"variable\":"<<variable<<",\"domain_powers\":[";
        for(size_t i=0;i<powers.size();i++) {if(i)out<<',';out<<powers[i];}
        out<<"],\"target\":";write_json(out,image);out<<",\"proof\":";write_reduction(out,proof);out<<"}\n";
    }
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");
        auto parent=std::filesystem::path(argv[2]).parent_path();
        if(!parent.empty())std::filesystem::create_directories(parent);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"distribution_refinement\",\"seed\":null,"
               "\"field_power_method\":\"exact Frobenius map in characteristic p\"}\n";
        for(int p:{2,3})for(int h:{1,2})for(bool wrapped:{false,true})for(bool C_or:{false,true})
            local(out,p,h,wrapped,C_or);
        local(out,3,1,false,false,true);
        for(int p:{2,3})recursive(out,p);
        out<<"{\"record\":\"summary\",\"local_cases\":17,\"recursive_cases\":2,\"all_passed\":true}\n";
        out.close();need(bool(out),"write output failed");
        std::cout<<"Seventeen local distribution cases and two recursive weighted-prefix cases passed.\n";
    } catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}
}
