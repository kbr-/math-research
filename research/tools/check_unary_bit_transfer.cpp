// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Ordinary-polynomial unary-to-bit image certificates and query-scope controls.
#include "ens_symbolic.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <numeric>
#include <string>
using namespace ens_symbolic;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
Polynomial indicator(const Ring& ring,int row,int bits,int label){
    auto value=ring.constant(1);
    for(int t=0;t<bits;t++){
        auto x=ring.variable(row*bits+t);
        value=ring.multiply(value,(label>>t)&1?x:ring.subtract(ring.constant(1),x));
    }
    return value;
}
void domain_certificate(std::ostream& out,const Ring& ring,const std::string& name,
                        const Polynomial& target,int variables,int ceiling){
    Polynomial pending=target;std::vector<Polynomial> cofactors(variables);int steps=0;
    while(true){
        auto found=pending.end();int variable=-1;
        for(auto it=pending.begin();it!=pending.end();++it){
            auto repeat=std::adjacent_find(it->first.begin(),it->first.end());
            if(repeat!=it->first.end()){found=it;variable=*repeat;break;}
        }
        if(found==pending.end())break;
        auto mon=found->first;int coefficient=found->second;
        need(variable>=0 && variable<variables,"domain variable");
        for(int k=0;k<2;k++)mon.erase(std::find(mon.begin(),mon.end(),variable));
        Polynomial q{{mon,coefficient}};ring.accumulate(cofactors[variable],q);
        auto x=ring.variable(variable),axiom=ring.subtract(ring.multiply(x,x),x);
        ring.accumulate(pending,ring.multiply(q,axiom),-1);++steps;
    }
    need(pending.empty(),"nonzero Boolean normal form: "+name);
    Polynomial sum;int actual=0,used=0;
    for(int i=0;i<variables;i++)if(!cofactors[i].empty()){
        auto x=ring.variable(i),axiom=ring.subtract(ring.multiply(x,x),x);
        auto term=ring.multiply(cofactors[i],axiom);ring.accumulate(sum,term);
        actual=std::max(actual,degree(term));++used;
    }
    need(sum==target && actual<=ceiling,"domain certificate identity or degree: "+name);
    out<<"{\"type\":\"domain_certificate\",\"name\":\""<<name<<"\",\"target\":";
    write_json(out,target);out<<",\"cofactors\":";write_polynomials(out,cofactors);
    out<<",\"degree\":"<<actual<<",\"bound\":"<<ceiling<<",\"used_domains\":"<<used
       <<",\"reduction_steps\":"<<steps<<"}\n";
}
void run_case(std::ostream& out,int bits){
    Ring ring(2,64);int holes=1<<bits;auto one=ring.constant(1);
    std::string name="unary_bit_l"+std::to_string(bits);
    std::vector<Polynomial> a,b;
    for(int j=0;j<holes;j++){a.push_back(indicator(ring,0,bits,j));b.push_back(indicator(ring,1,bits,j));}
    out<<"{\"type\":\"case\",\"name\":\""<<name<<"\",\"bits\":"<<bits<<",\"holes\":"<<holes
       <<",\"old_unary_slots\":[100,101],\"bit_variables\":"<<2*bits<<",\"row0_images\":";
    write_polynomials(out,a);out<<",\"row1_images\":";write_polynomials(out,b);out<<"}\n";
    Polynomial partition;
    for(const auto& image:a)ring.accumulate(partition,image);
    need(partition==one,"literal partition identity");
    int boolean_count=0,exclusion_count=0;
    for(int j=0;j<holes;j++){
        need(degree(a[j])==bits,"indicator ordinary degree");
        domain_certificate(out,ring,name+"/Boolean_"+std::to_string(j),
                           ring.subtract(ring.multiply(a[j],a[j]),a[j]),2*bits,2*bits);++boolean_count;
        auto collision=ring.multiply(a[j],b[j]);need(degree(collision)==2*bits,"bit collision degree");
        out<<"{\"type\":\"collision_image\",\"case\":\""<<name<<"\",\"label\":"<<j
           <<",\"bit_BPHP_axiom\":";write_json(out,collision);out<<"}\n";
        for(int k=j+1;k<holes;k++){
            domain_certificate(out,ring,name+"/row_exclusion_"+std::to_string(j)+"_"+std::to_string(k),
                               ring.multiply(a[j],a[k]),2*bits,2*bits);++exclusion_count;
        }
    }
    Monomial top(bits);std::iota(top.begin(),top.end(),0);
    need(a[0].at(top)==1,"missing top multilinear coefficient");
    int parity=0;
    for(int assignment=0;assignment<holes;assignment++){
        std::map<int,int> point;for(int t=0;t<bits;t++)point[t]=(assignment>>t)&1;
        parity^=ring.evaluate(a[0],point);
    }
    need(parity==1,"indicator full-cube derivative");
    out<<"{\"type\":\"query_control\",\"case\":\""<<name<<"\",\"top_degree\":"<<bits
       <<",\"top_coefficient\":1,\"full_cube_parity\":1,\"affine_bit_query\":"
       <<(bits==1?"true":"false")<<"}\n";
    for(int h:{1,2}){
        int original_fresh=2*bits,new_fresh=2*bits;
        Block original=make_block(ring,{ring.variable(100),ring.variable(101)},h,original_fresh);
        Block mapped=make_block(ring,{a[0],b.back()},h,new_fresh);
        std::map<int,Polynomial> images{{100,a[0]},{101,b.back()}};
        need(ring.substitute(original.product,images)==mapped.product,"genuine product image");
        for(int j=0;j<2;j++)need(ring.substitute(original.companions[j],images)==mapped.companions[j],"complete companion image");
        int e=(h+1)*bits+h;need(degree(mapped.companions[0])==e && e<=bits*(2*h+1),"original activity ceiling");
        out<<"{\"type\":\"ENS_image\",\"case\":\""<<name<<"\",\"h\":"<<h<<",\"original\":";
        write_block(out,original);out<<",\"mapped\":";write_block(out,mapped);
        out<<",\"original_companion_degree\":"<<2*h+1<<",\"actual_image_degree\":"<<e
           <<",\"carried_upper_bound\":"<<bits*(2*h+1)<<"}\n";
    }
    if(bits==2){
        std::vector<int> unary{1,1,1,0};int label=0;
        for(int j=0;j<holes;j++)if(unary[j])label^=j;
        need(label==3 && unary[label]==0,"weak-row inverse control");
        out<<"{\"type\":\"weak_row_control\",\"unary_values\":[1,1,1,0],\"row_parity\":1,"
             "\"reconstructed_label\":3,\"reconstructed_unary_values\":[0,0,0,1],"
             "\"functionality_is_violated\":true}\n";
    }
    out<<"{\"type\":\"result\",\"case\":\""<<name<<"\",\"Boolean_certificates\":"<<boolean_count
       <<",\"row_exclusion_certificates\":"<<exclusion_count<<",\"collision_images\":"<<holes
       <<",\"ENS_images\":2,\"partition_exact\":true,\"all_passed\":true}\n";
    std::cout<<name<<": "<<boolean_count<<" Boolean and "<<exclusion_count
             <<" row-exclusion certificates, "<<holes<<" collision images, two ENS images; query control passed.\n";
}
void equality_filtration(std::ostream& out,int bits){
    Ring ring(2,64);int holes=1<<bits;auto one=ring.constant(1);Polynomial sum;
    std::vector<Polynomial> axioms;
    for(int j=0;j<holes;j++){
        auto f=ring.multiply(indicator(ring,0,bits,j),indicator(ring,1,bits,j));
        need(degree(f)==2*bits,"collision original degree");
        ring.accumulate(sum,f);axioms.push_back(f);
    }
    auto equality=one;
    for(int t=0;t<bits;t++)
        equality=ring.multiply(equality,ring.subtract(ring.subtract(one,ring.variable(t)),ring.variable(bits+t)));
    need(sum==equality && degree(equality)==bits,"ordinary collision-sum equality");
    std::map<int,int> point;for(int t=0;t<2*bits;t++)point[t]=0;
    need(ring.evaluate(equality,point)==1,"low-degree separation point");
    out<<"{\"type\":\"equality_filtration\",\"bits\":"<<bits<<",\"holes\":"<<holes
       <<",\"collision_axioms\":";write_polynomials(out,axioms);
    out<<",\"all_axiom_coefficients\":1,\"literal_sum_target\":";write_json(out,equality);
    out<<",\"target_degree\":"<<bits<<",\"NS_membership_ceiling\":"<<2*bits
       <<",\"NS_nonmembership_ceiling\":"<<bits<<",\"separating_bit_assignment\":\"all zero\","
         "\"target_value_at_separator\":1,\"low_ceiling_has_only_domain_axioms\":true}\n";
    std::cout<<"bits="<<bits<<": collision sum has degree "<<bits<<", belongs to I_"<<2*bits
             <<" and is separated from I_"<<bits<<" by the all-zero bit point.\n";
}
int main(int argc,char** argv){
    try{
        bool filtration=argc==4 && std::string(argv[3])=="--equality-filtration";
        need((argc==3 || filtration) && std::string(argv[1])=="--out","--out NEW_PATH [--equality-filtration] required");
        need(!std::filesystem::exists(argv[2]),"output exists");
        auto parent=std::filesystem::path(argv[2]).parent_path();if(!parent.empty())std::filesystem::create_directories(parent);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        if(filtration){
            out<<"{\"schema\":1,\"suite\":\"bit_equality_NS_filtration\",\"p\":2,\"seed\":null,"
                 "\"scope\":\"two-pigeon collision subfamily; the same degree separation holds in the full standard bit-PHP base\"}\n";
            for(int bits:{1,2,3,4})equality_filtration(out,bits);
            out.close();need(bool(out),"output write failed");return 0;
        }
        out<<"{\"schema\":1,\"suite\":\"unary_bit_polynomial_transfer\",\"p\":2,\"seed\":null,"
             "\"encoding\":\"[coefficient,[variable,...]] with repeated indices for powers\","
             "\"scope\":\"complete local base/ENS image certificates; not a Res(parity) proof translation\"}\n";
        for(int bits:{1,2,3,4})run_case(out,bits);
        int mass=0,left=0,right=0,linear=0;
        for(int point:{0,1,2}){
            bool on_flat=(point&14)==0;
            if(on_flat){mass^=1;left^=(point&1)==0;right^=(point&1)!=0;linear^=point&1;}
        }
        need(mass==0 && left==1 && right==1 && linear==1,"zero-mean singleton control");
        out<<"{\"type\":\"zero_mean_singleton_control\",\"old_variables\":4,\"root_points\":[0,1,2],"
             "\"root_point_weights\":[1,1,1],\"flat_equations\":\"x_1=x_2=x_3=0\","
             "\"singleton_mass\":0,\"singleton_x0_moment\":1,\"split_child_masses\":[1,1],"
             "\"scope\":\"zero mean does not make a finite-field singleton functional vanish\"}\n";
        out.close();need(bool(out),"output write failed");
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
