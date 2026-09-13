// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Affected source comparison after virtual OR folding, including prefix errors.
#include "sparse_polynomial.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace sparse_polynomial;
void need(bool b,const std::string& s){if(!b)throw std::runtime_error(s);}
Ring ring(2,64);
std::vector<Polynomial> axioms;
std::vector<std::string> axiom_names;
int add_axiom(const std::string& name,const Polynomial& p){
    int id=int(axioms.size());axioms.push_back(p);axiom_names.push_back(name);return id;
}
struct Cert{Polynomial target;std::map<int,Polynomial> cof;};
Cert ax(int id){return {axioms.at(id),{{id,ring.constant(1)}}};}
Cert scale(Cert c,const Polynomial& q){
    c.target=ring.multiply(c.target,q);
    for(auto& [id,p]:c.cof){(void)id;p=ring.multiply(p,q);}
    return c;
}
void accumulate(Cert& a,const Cert& b,int scalar=1){
    ring.accumulate(a.target,b.target,scalar);
    for(const auto& [id,p]:b.cof)ring.accumulate(a.cof[id],p,scalar);
}
void write_cert(std::ostream& out,const std::string& name,const Cert& c,int budget){
    Polynomial actual;int used=0;
    out<<"{\"type\":\"certificate\",\"name\":\""<<name<<"\",\"target\":";
    write_json(out,c.target);out<<",\"budget\":"<<budget<<",\"terms\":[";
    bool comma=false;
    for(const auto& [id,p]:c.cof)if(!p.empty()){
        auto term=ring.multiply(p,axioms[id]);ring.accumulate(actual,term);
        used=std::max(used,degree(term));
        if(comma)out<<',';
        comma=true;out<<"{\"axiom_id\":"<<id<<",\"cofactor\":";write_json(out,p);out<<'}';
    }
    need(actual==c.target && used<=budget,"certificate "+name);
    out<<"],\"witness_degree\":"<<used<<"}\n";
}
struct Block{
    std::string name;std::vector<int> inputs,coefficient_ids;
    std::vector<Polynomial> prefixes,factors;Polynomial value;
    std::map<int,int> companion_ids;
};
Block block(const std::string& name,const std::vector<int>& inputs,
            const std::vector<Polynomial>& g,int& next){
    Block b{name,inputs,{},std::vector<Polynomial>(inputs.size()),{},ring.constant(1),{}};
    for(int u=0;u<2;++u){
        auto factor=ring.constant(1);
        for(std::size_t i=0;i<inputs.size();++i){
            auto r=ring.variable(next);b.coefficient_ids.push_back(next++);
            ring.accumulate(b.prefixes[i],ring.multiply(b.value,r));
            ring.accumulate(factor,ring.multiply(r,g[inputs[i]]),-1);
        }
        b.factors.push_back(factor);b.value=ring.multiply(b.value,factor);
    }
    Polynomial sum;
    for(std::size_t i=0;i<inputs.size();++i)
        ring.accumulate(sum,ring.multiply(b.prefixes[i],g[inputs[i]]));
    need(sum==ring.subtract(ring.constant(1),b.value),"ordinary prefix");
    return b;
}
void write_block(std::ostream& out,const Block& b){
    out<<"{\"type\":\"block\",\"name\":\""<<b.name<<"\",\"inputs\":[";
    for(std::size_t i=0;i<b.inputs.size();++i){if(i)out<<',';out<<b.inputs[i];}
    out<<"],\"coefficient_ids_row_major\":[";
    for(std::size_t i=0;i<b.coefficient_ids.size();++i){if(i)out<<',';out<<b.coefficient_ids[i];}
    out<<"],\"value\":";write_json(out,b.value);out<<",\"prefixes\":[";
    for(std::size_t i=0;i<b.prefixes.size();++i){if(i)out<<',';write_json(out,b.prefixes[i]);}
    out<<"]}\n";
}
Cert boolean_cert(const Polynomial& p){
    Cert c; c.target=ring.subtract(ring.multiply(p,p),p);
    auto pending=c.target;
    while(true){
        bool changed=false;
        for(const auto& [m,coefficient]:pending){
            auto duplicate=std::adjacent_find(m.begin(),m.end());
            if(duplicate==m.end())continue;
            int variable=*duplicate;auto reduced=m;
            auto pos=std::size_t(duplicate-m.begin());reduced.erase(reduced.begin()+pos,reduced.begin()+pos+2);
            Polynomial q{{reduced,coefficient}};
            ring.accumulate(c.cof[variable],q);
            ring.accumulate(pending,ring.multiply(q,axioms.at(variable)),-1);
            changed=true;break;
        }
        if(!changed)break;
    }
    need(pending.empty(),"Boolean remainder must vanish");return c;
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");
        auto one=ring.constant(1),z=ring.variable(9);
        std::vector<Polynomial> g;
        for(int i=0;i<5;++i)g.push_back(ring.variable(i));
        std::vector<Polynomial> chi={
            ring.multiply(ring.variable(5),ring.variable(6)),
            ring.multiply(ring.variable(7),ring.variable(8))};
        for(const auto& c:chi)g.push_back(ring.add(ring.add(one,c),z));
        auto q=ring.multiply(ring.add(chi[0],z),ring.add(chi[1],z));
        int next=10;
        auto A=block("A",{0,1,2,3,4},g,next);
        auto D=block("D",{0,5},g,next);
        auto E=block("E",{1,2,3,4,6},g,next);
        for(int i=0;i<next;++i){
            auto x=ring.variable(i);
            need(add_axiom("Boolean/"+std::to_string(i),ring.subtract(ring.multiply(x,x),x))==i,"field ids");
        }
        for(auto* b:{&A,&D,&E})for(int i:b->inputs)
            b->companion_ids[i]=add_axiom(b->name+"/"+std::to_string(i),ring.multiply(g[i],b->value));
        auto value=ring.multiply(A.value,q);
        std::vector<Cert> companions(7);
        for(int i=0;i<5;++i)companions[i]=scale(ax(A.companion_ids[i]),q);
        for(int b=0;b<2;++b){
            auto c=boolean_cert(g[5+b]);
            companions[5+b]=scale(scale(c,ring.add(chi[1-b],z)),A.value);
        }
        std::vector<Polynomial> prefixes=A.prefixes;
        ring.accumulate(prefixes[0],axioms[1]); // Deliberately create a nonzero, certified prefix error.
        prefixes.push_back(A.value);
        prefixes.push_back(ring.multiply(A.value,ring.add(chi[0],z)));
        auto residual=scale(ax(1),g[0]);
        Polynomial unit=ring.subtract(one,value);
        for(int i=0;i<7;++i)ring.accumulate(unit,ring.multiply(prefixes[i],g[i]),-1);
        need(unit==residual.target,"costed virtual prefix error");
        Cert witness;
        for(std::size_t i=0;i<D.inputs.size();++i)
            accumulate(witness,scale(companions[D.inputs[i]],D.prefixes[i]));
        for(std::size_t i=0;i<E.inputs.size();++i)
            accumulate(witness,scale(companions[E.inputs[i]],ring.multiply(D.value,E.prefixes[i])));
        for(int i:D.inputs)
            accumulate(witness,scale(ax(D.companion_ids[i]),ring.multiply(E.value,prefixes[i])),-1);
        for(int i:E.inputs)
            accumulate(witness,scale(ax(E.companion_ids[i]),ring.multiply(D.value,prefixes[i])),-1);
        auto target=ring.subtract(value,ring.multiply(D.value,E.value));
        auto correction=scale(residual,ring.multiply(D.value,E.value));
        need(witness.target!=target && witness.target==ring.add(target,correction.target),"missing-error control");
        accumulate(witness,correction,-1);
        need(witness.target==target && !target.empty(),"affected comparison target");

        std::vector<Polynomial> coefficient_images;
        auto product=one;
        for(int u=0;u<2;++u){
            auto factor=one,multiplier=ring.add(chi[u],z);
            for(int i=0;i<7;++i){
                auto beta=i<5?ring.multiply(multiplier,ring.variable(A.coefficient_ids[u*5+i])):
                             ring.constant(i==5+u);
                coefficient_images.push_back(beta);
                ring.accumulate(factor,ring.multiply(beta,g[i]),-1);
            }
            product=ring.multiply(product,factor);
        }
        need(product==value,"paired-factor realization");
        auto field_control=boolean_cert(coefficient_images[0]);
        need(degree(field_control.target)==6,"raw coefficient field image exceeds original degree two");

        out<<"{\"type\":\"schema\",\"version\":1,\"field\":2,\"accuracy\":2,"
              "\"old_variables\":\"t_0..t_4=0..4, L_0..L_3=5..8, modifier=9\","
              "\"polynomials\":\"explicit coefficients and sorted variable lists retaining repetitions\","
              "\"scope\":\"local source-shaped retained system, not a complete PHP proof\"}\n";
        out<<"{\"type\":\"inputs\",\"polynomials\":[";
        for(std::size_t i=0;i<g.size();++i){if(i)out<<',';write_json(out,g[i]);}
        out<<"],\"normalized_child\":";write_json(out,q);out<<"}\n";
        for(const auto* b:{&A,&D,&E})write_block(out,*b);
        out<<"{\"type\":\"axioms\",\"entries\":[";
        for(std::size_t i=0;i<axioms.size();++i){
            if(i)out<<',';
            out<<"{\"id\":"<<i<<",\"name\":\""<<axiom_names[i]<<"\",\"polynomial\":";
            write_json(out,axioms[i]);out<<'}';
        }
        out<<"]}\n{\"type\":\"virtual_profile\",\"weight\":8,\"original_union_weight\":10,"
              "\"intermediate_genuine_union_degree\":6,\"value\":";
        write_json(out,value);out<<",\"prefixes\":[";
        for(std::size_t i=0;i<prefixes.size();++i){if(i)out<<',';write_json(out,prefixes[i]);}
        out<<"]}\n";
        for(int i=0;i<7;++i){
            need(companions[i].target==ring.multiply(g[i],value),"virtual companion target");
            need(degree(prefixes[i])+degree(g[i])<=8,"weighted prefix");
            write_cert(out,"virtual_companion/"+std::to_string(i),companions[i],8+degree(g[i]));
        }
        write_cert(out,"virtual_prefix_residual",residual,8);
        write_cert(out,"virtual_Booleanity",boolean_cert(value),16);
        write_cert(out,"affected_OR_comparison",witness,20);
        write_cert(out,"raw_field_image_control",field_control,6);
        out<<"{\"type\":\"paired_map\",\"original_union_coefficients_row_major\":[";
        for(std::size_t i=0;i<coefficient_images.size();++i){if(i)out<<',';write_json(out,coefficient_images[i]);}
        out<<"],\"maximum_coefficient_degree\":3,\"original_field_budget\":2,"
              "\"field_image_degree\":6,\"ordinary_union_product_identity\":true}\n";
        out<<"{\"type\":\"controls\",\"omitted_prefix_error_nonzero\":";
        write_json(out,correction.target);
        out<<",\"folded_weight\":8,\"original_parent_weight\":10,"
              "\"two_fresh_affine_children_weight_sum\":8,\"fresh_affine_parent_weight\":4}\n";
        out<<"{\"type\":\"summary\",\"complete_NS_certificates\":11,"
              "\"rebuilt_comparison_budget\":20,\"original_comparison_ceiling\":30,\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<"Passed 11 full NS certificates. The nonzero affected comparison fits degree 20 (original 30).\n"
                 <<"The prefix-error correction is necessary; the raw field image has degree six, not two.\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
