// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact retained-core factor sharing, packing, image budgets, and controls.
#include "domain_polynomial.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <numeric>
#include <string>
using namespace ens_symbolic;
using namespace domain_polynomial;
void need(bool condition,const std::string& why){
    if(!condition)throw std::runtime_error(why);
}
struct Counts{int cases=0,companions=0,fields=0,booleans=0,later=0,omissions=0,sharp=0;};
struct Fundamental{Polynomial factor;std::vector<Polynomial> coefficients;int weight;};

void certificate(std::ostream& out,const Ring& ring,const Polynomial& original,
                 const Polynomial& image,const std::vector<Polynomial>& axioms,
                 const std::vector<Polynomial>& cofactors,int T){
    Polynomial sum;int budget=0;
    need(axioms.size()==cofactors.size(),"NS coefficient arity");
    for(size_t j=0;j<axioms.size();j++){
        Polynomial term=ring.multiply(axioms[j],cofactors[j]);
        ring.accumulate(sum,term);budget=std::max(budget,degree(term));
    }
    need(sum==image,"NS image reconstruction");
    need(budget<=T*degree(original),"original image-certificate budget");
    out<<"{\"original\":";write_json(out,original);out<<",\"image\":";write_json(out,image);
    out<<",\"original_degree\":"<<degree(original)<<",\"certificate_degree\":"<<budget;
    out<<",\"cofactors\":";write_polynomials(out,cofactors);out<<'}';
}

void check_case(std::ostream& out,int p,int h,int t,int k,bool nonlinear,Counts& count){
    Ring ring(p,64);Polynomial one=ring.constant(1),zero;
    int old_count=nonlinear?4:2+k;
    std::vector<Polynomial> core={ring.variable(0),ring.variable(1)},residual;
    for(int j=0;j<k;j++)residual.push_back(nonlinear?
        ring.multiply(ring.variable(2),ring.variable(3)):ring.variable(2+j));
    std::vector<Polynomial> inputs=core;
    inputs.insert(inputs.end(),residual.begin(),residual.end());
    int fresh=old_count,root_start=fresh;
    Block root=make_block(ring,core,h,fresh);
    int reduced_start=root_start;
    Block kept=make_block(ring,core,t,reduced_start);
    Block selected=make_block(ring,inputs,h,fresh);
    int T=nonlinear?1:std::max(1,(2*t+k+h-1)/h-1);
    int capacity=T+1;
    std::vector<Fundamental> fundamental;
    std::vector<std::vector<int>> bins(h);
    std::vector<int> weights(h);
    for(int u=0;u<t;u++){
        std::vector<Polynomial> beta(inputs.size());Polynomial factor=one;
        for(size_t i=0;i<core.size();i++){
            beta[i]=ring.variable(root.variables[u][i]);
            ring.accumulate(factor,ring.multiply(beta[i],core[i]),-1);
        }
        bins[u].push_back(int(fundamental.size()));weights[u]=2;
        fundamental.push_back({factor,beta,2});
    }
    for(int j=0;j<k;j++){
        std::vector<Polynomial> beta(inputs.size());beta[core.size()+j]=one;
        int weight=degree(residual[j]),slot=-1;
        for(int u=0;u<h;u++)if(weights[u]+weight<=capacity){slot=u;break;}
        need(slot>=0,"factor packing capacity");
        bins[slot].push_back(int(fundamental.size()));weights[slot]+=weight;
        fundamental.push_back({ring.subtract(one,residual[j]),beta,weight});
    }
    std::map<int,Polynomial> images;
    for(int u=t;u<h;u++)for(int v:root.variables[u])images[v]=zero;
    int actual_T=1;
    for(int u=0;u<h;u++){
        Polynomial prefix=one;std::vector<Polynomial> beta(inputs.size());
        for(int f:bins[u]){
            for(size_t j=0;j<inputs.size();j++)
                ring.accumulate(beta[j],ring.multiply(prefix,fundamental[f].coefficients[j]));
            prefix=ring.multiply(prefix,fundamental[f].factor);
        }
        need(normalizer_error(ring,inputs,beta)==prefix,"factor telescope");
        for(size_t j=0;j<inputs.size();j++){
            actual_T=std::max(actual_T,degree(beta[j]));
            images[selected.variables[u][j]]=beta[j];
        }
    }
    need(actual_T<=T,"coefficient degree");
    Polynomial Z=one;
    for(const auto& a:residual)Z=ring.multiply(Z,ring.subtract(one,a));
    Polynomial target=ring.multiply(kept.product,Z);
    need(ring.substitute(selected.product,images)==target,"prescribed product");
    need(ring.substitute(root.product,images)==kept.product,"shortened retained core");
    if(!nonlinear){
        need(degree(target)==2*t+k,"independent-input target degree");
        need(actual_T==T,"attain the optimal coefficient degree");
        if(T>1)need(degree(target)>h*T,"one-smaller degree must fail");
        count.sharp++;
    }
    std::vector<int> domain_powers(fresh,p);
    for(int j=0;j<old_count;j++)domain_powers[j]=2;
    std::vector<Polynomial> axioms=kept.companions;
    for(int j=0;j<old_count;j++){
        Polynomial x=ring.variable(j);axioms.push_back(ring.subtract(ring.power(x,2),x));
    }
    std::vector<Reduction> booleanity;
    for(const auto& a:residual){
        Polynomial error=ring.subtract(ring.multiply(a,a),a);
        Reduction r=domain_reduce(ring,error,std::vector<int>(old_count,2));
        verify_reduction(ring,error,std::vector<int>(old_count,2),r);
        need(r.remainder.empty() && r.degree<=2*degree(a),"old Booleanity budget");
        booleanity.push_back(r);count.booleans++;
    }
    out<<"{\"record\":\"core_case\",\"p\":"<<p<<",\"h\":"<<h<<",\"t\":"<<t
       <<",\"k\":"<<k<<",\"nonlinear_residual\":"<<(nonlinear?"true":"false")
       <<",\"coefficient_degree_bound\":"<<T<<",\"actual_coefficient_degree\":"<<actual_T
       <<",\"old_variable_count\":"<<old_count<<",\"inputs\":";write_polynomials(out,inputs);
    out<<",\"root_original\":";write_block(out,root);
    out<<",\"root_retained\":";write_block(out,kept);
    out<<",\"selected\":";write_block(out,selected);
    out<<",\"target_product\":";write_json(out,target);
    out<<",\"factor_bins\":[";
    for(int u=0;u<h;u++){
        if(u)out<<',';
        out<<"{\"weight\":"<<weights[u]<<",\"fundamental_indices\":[";
        for(size_t j=0;j<bins[u].size();j++){if(j)out<<',';out<<bins[u][j];}
        out<<"]}";
    }
    out<<"],\"fundamental_factors\":[";
    for(size_t j=0;j<fundamental.size();j++){
        if(j)out<<',';
        out<<"{\"factor\":";write_json(out,fundamental[j].factor);
        out<<",\"input_coefficients\":";write_polynomials(out,fundamental[j].coefficients);
        out<<",\"weight\":"<<fundamental[j].weight<<'}';
    }
    out<<"],\"coefficient_images\":[";bool comma=false;
    for(const auto& [v,poly]:images){
        if(comma)out<<',';
        comma=true;out<<'['<<v<<',';write_json(out,poly);out<<']';
    }
    out<<"],\"new_certificate_axioms\":";write_polynomials(out,axioms);
    out<<",\"old_booleanity_certificates\":[";
    for(size_t j=0;j<booleanity.size();j++){if(j)out<<',';write_reduction(out,booleanity[j]);}
    out<<"],\"root_image_certificates\":[";
    for(size_t i=0;i<root.companions.size();i++){
        if(i)out<<',';
        std::vector<Polynomial> q(axioms.size());q[i]=one;
        certificate(out,ring,root.companions[i],ring.substitute(root.companions[i],images),axioms,q,T);
        count.companions++;
    }
    out<<"],\"selected_image_certificates\":[";
    for(size_t i=0;i<selected.companions.size();i++){
        if(i)out<<',';
        std::vector<Polynomial> q(axioms.size());
        if(i<core.size())q[i]=Z;
        else{
            size_t j=i-core.size();Polynomial multiplier=kept.product;
            for(size_t u=0;u<residual.size();u++)if(u!=j)
                multiplier=ring.multiply(multiplier,ring.subtract(one,residual[u]));
            for(int v=0;v<old_count;v++)
                q[core.size()+v]=ring.subtract(zero,ring.multiply(multiplier,booleanity[j].coefficients[v]));
        }
        certificate(out,ring,selected.companions[i],ring.substitute(selected.companions[i],images),axioms,q,T);
        count.companions++;
    }
    out<<"],\"domain_powers\":[";
    for(size_t j=0;j<domain_powers.size();j++){if(j)out<<',';out<<domain_powers[j];}
    out<<"],\"field_image_certificates\":[";comma=false;
    for(const auto& [v,poly]:images){
        if(comma)out<<',';
        comma=true;
        Polynomial error=ring.subtract(ring.power(poly,p),poly);
        Reduction r=domain_reduce(ring,error,domain_powers);
        verify_reduction(ring,error,domain_powers,r);
        need(r.remainder.empty() && r.degree<=p*T,"field image certificate");
        for(const auto& [removed,unused]:images){
            (void)unused;
            need(r.coefficients[removed].empty(),"field certificate used a removed variable domain");
        }
        out<<"{\"variable\":"<<v<<",\"image\":";write_json(out,error);
        out<<",\"certificate\":";write_reduction(out,r);out<<'}';count.fields++;
    }
    out<<']';
    if(!nonlinear && h==2){
        int later_first=fresh;
        Block later=make_block(ring,{selected.product},1,fresh);
        Block mapped=make_block(ring,{target},1,later_first);
        need(ring.substitute(later.companions[0],images)==mapped.companions[0],"later-input reconstruction");
        need(later.companions[0]!=mapped.companions[0],"unchanged later input control");
        need(degree(mapped.companions[0])<=T*degree(later.companions[0]),"later companion budget");
        out<<",\"later_original\":";write_block(out,later);
        out<<",\"later_specialized\":";write_block(out,mapped);
        out<<",\"unchanged_later_control_rejected\":true";count.later++;
    }
    if(!nonlinear && h==2 && t==1 && k==2){
        Polynomial omitted=ring.multiply(residual[1],
            ring.multiply(kept.product,ring.subtract(one,residual[0])));
        std::map<int,int> assignment;
        for(int v=0;v<fresh;v++)assignment[v]=0;
        assignment[3]=1;
        for(const auto& e:kept.companions)need(ring.evaluate(e,assignment)==0,"root control premise");
        need(ring.evaluate(omitted,assignment)==1,"omitted residual countermodel");
        out<<",\"omitted_residual_image\":";write_json(out,omitted);
        out<<",\"omission_witness\":{\"one_variables\":[3],\"other_variables\":0,\"image_value\":1}";
        count.omissions++;
    }
    out<<",\"sharp_prescribed_product_bound\":"<<(!nonlinear?"true":"false")<<"}\n";count.cases++;
}

int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","Usage: check_relative_core_cover --out NEW_PATH");
        std::string path=argv[2];need(!std::filesystem::exists(path),"output must be new");
        std::ofstream out(path);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"relative_core_cover\",\"scope\":\"local ENS data, not PHP refutations\"}\n";
        Counts c;
        for(int p:{2,3,5,7}){
            for(auto config:std::vector<std::vector<int>>{{2,1,1},{2,1,2},{2,2,1},{3,1,4},{3,2,2},{3,2,5}})
                check_case(out,p,config[0],config[1],config[2],false,c);
            check_case(out,p,2,1,1,true,c);
        }
        out<<"{\"record\":\"summary\",\"cases\":"<<c.cases<<",\"companion_certificates\":"<<c.companions
           <<",\"field_certificates\":"<<c.fields<<",\"old_booleanity_certificates\":"<<c.booleans
           <<",\"later_controls\":"<<c.later<<",\"omission_controls\":"<<c.omissions
           <<",\"sharp_degree_cases\":"<<c.sharp<<",\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failure");
        std::cout<<c.cases<<" cases; "<<c.companions<<" companion, "<<c.fields<<" field, "
                 <<c.booleans<<" Booleanity certificates; "<<c.later<<" later and "
                 <<c.omissions<<" omission controls; "<<c.sharp<<" sharp degree cases.\n";
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
