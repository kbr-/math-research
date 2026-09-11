// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Complete small NS spans and an ordinary degree-four PC trace for copy matching.
#include "domain_polynomial.hpp"
#include "binary_php.hpp"
#include <filesystem>
using namespace ens_symbolic;
using namespace domain_polynomial;
using binary_php::Bits;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
void xor_into(Bits& a,const Bits& b){for(size_t j=0;j<a.size();j++)a[j]^=b[j];}
Bits normal(const Polynomial& polynomial){
    Bits result=binary_php::blank(512);
    for(const auto& [monomial,c]:polynomial){
        int mask=0;for(int v:monomial){need(v>=0 && v<9,"old-variable range");mask|=1<<v;}
        if(c&1)binary_php::flip(result,mask);
    }
    return result;
}
Polynomial monomial(const Ring& ring,int mask){
    Polynomial p=ring.constant(1);
    for(int v=0;v<9;v++)if(mask&(1<<v))p=ring.multiply(p,ring.variable(v));
    return p;
}
struct Row{int axiom,mask;Bits value;};

int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","Usage: check_copy_pc_ns --out NEW_PATH");
        std::string path=argv[2];need(!std::filesystem::exists(path),"output must be new");
        std::ofstream out(path);need(bool(out),"cannot open output");
        Ring ring(2,64);Polynomial one=ring.constant(1);
        Polynomial x=ring.variable(0),y=ring.variable(1),z=ring.variable(2);
        int fresh=3;
        Block lower_g=make_block(ring,{x,y},1,fresh);
        Block lower_f=make_block(ring,{x,y},1,fresh);
        Block root=make_block(ring,{lower_f.product,z},1,fresh);
        need(fresh==9,"coordinate layout");
        Polynomial g=lower_g.product,f=lower_f.product,u=ring.variable(7),v=ring.variable(8);
        Polynomial pg=ring.subtract(ring.subtract(one,ring.multiply(u,g)),ring.multiply(v,z));
        Polynomial target=ring.multiply(z,pg),difference=ring.subtract(g,f);
        std::vector<Polynomial> axioms=lower_g.companions;
        axioms.insert(axioms.end(),lower_f.companions.begin(),lower_f.companions.end());
        axioms.insert(axioms.end(),root.companions.begin(),root.companions.end());
        out<<"{\"schema\":1,\"suite\":\"copy_pc_ns\",\"p\":2,\"old_variables\":9,"
              "\"domain\":\"all Boolean\",\"scope\":\"satisfiable ENS data, not PHP\","
              "\"axioms\":";write_polynomials(out,axioms);
        out<<",\"lower_g\":";write_block(out,lower_g);
        out<<",\"lower_f\":";write_block(out,lower_f);
        out<<",\"retained_root\":";write_block(out,root);
        out<<",\"target\":";write_json(out,target);out<<",\"input_difference\":";write_json(out,difference);
        out<<"}\n";

        std::vector<Polynomial> lines;
        out<<"{\"record\":\"pc_trace\",\"degree_ceiling\":4,\"lines\":[";bool comma=false;
        auto emit=[&](Polynomial poly,const std::string& action){
            need(degree(poly)<=4,"PC degree exceeded");
            if(comma)out<<',';
            comma=true;int id=int(lines.size());lines.push_back(std::move(poly));
            out<<"{\"id\":"<<id<<','<<action<<",\"polynomial\":";write_json(out,lines.back());out<<'}';
            return id;
        };
        for(int i=0;i<4;i++)emit(axioms[i],"\"axiom\":"+std::to_string(i));
        int multipliers[]={5,6,3,4};
        for(int i=0;i<4;i++)emit(ring.multiply(axioms[i],ring.variable(multipliers[i])),
            "\"multiply\":"+std::to_string(i)+",\"variable\":"+std::to_string(multipliers[i]));
        int current=emit(ring.add(lines[4],lines[5]),"\"add\":[4,5]");
        for(int i:{6,7})current=emit(ring.add(lines[current],lines[i]),
            "\"add\":["+std::to_string(current)+","+std::to_string(i)+"]");
        need(lines[current]==difference,"PC difference trace");
        for(int variable:{7,2})current=emit(ring.multiply(lines[current],ring.variable(variable)),
            "\"multiply\":"+std::to_string(current)+",\"variable\":"+std::to_string(variable));
        int root_line=emit(axioms[5],"\"axiom\":5");
        current=emit(ring.add(lines[current],lines[root_line]),
            "\"add\":["+std::to_string(current)+","+std::to_string(root_line)+"]");
        need(lines[current]==target && degree(target)==4,"PC final target");
        out<<"],\"all_steps_checked\":true}\n";

        int minimum_ns=-1;
        for(int D=4;D<=6;D++){
            std::vector<Row> rows;
            for(size_t a=0;a<axioms.size();a++){
                int allowance=D-degree(axioms[a]);
                for(int mask=0;mask<512;mask++)if(__builtin_popcount(unsigned(mask))<=allowance)
                    rows.push_back({int(a),mask,normal(ring.multiply(monomial(ring,mask),axioms[a]))});
            }
            binary_php::Space span(512);
            std::vector<Bits> combinations(512);
            for(size_t j=0;j<rows.size();j++){
                std::vector<int> trace;Bits reduced=span.reduce(rows[j].value,&trace);
                Bits combination=binary_php::blank(int(rows.size()));binary_php::flip(combination,int(j));
                for(int pivot:trace)xor_into(combination,combinations[pivot]);
                int pivot=binary_php::highest(reduced);
                if(pivot>=0){
                    span.insert_reduced(std::move(reduced),pivot);
                    combinations[pivot]=std::move(combination);
                }
            }
            need(binary_php::zero(span.reduce(normal(difference))),"nontrivial NS positive control");
            std::vector<int> trace;Bits remainder=span.reduce(normal(target),&trace);
            bool member=binary_php::zero(remainder);
            out<<"{\"record\":\"ns_span\",\"degree\":"<<D<<",\"row_count\":"<<rows.size()
               <<",\"rank\":"<<span.rank<<",\"target_is_member\":"<<(member?"true":"false")
               <<",\"input_difference_is_member\":true,\"rows\":[";
            for(size_t j=0;j<rows.size();j++){
                if(j)out<<',';
                out<<"{\"axiom\":"<<rows[j].axiom<<",\"multiplier_mask\":"<<rows[j].mask
                   <<",\"normal_form_support\":";binary_php::sparse_json(out,rows[j].value);out<<'}';
            }
            out<<']';
            if(!member){
                Bits dual=span.separating_dual(normal(target));
                for(const auto& row:rows)need(binary_php::dot(dual,row.value)==0,"NS dual row");
                need(binary_php::dot(dual,normal(target))==1,"NS target separation");
                Bits corrupted=dual;binary_php::flip(corrupted,binary_php::support(normal(target)).front());
                need(binary_php::dot(corrupted,normal(target))==0,"corrupted dual control");
                out<<",\"dual_support\":";binary_php::sparse_json(out,dual);
                out<<",\"dual_corruption_rejected\":true";
            }else{
                Bits solution=binary_php::blank(int(rows.size()));
                for(int pivot:trace)xor_into(solution,combinations[pivot]);
                std::vector<Polynomial> q(axioms.size());
                for(int j:binary_php::support(solution))
                    ring.accumulate(q[rows[j].axiom],monomial(ring,rows[j].mask));
                Polynomial error=target;int budget=0;
                for(size_t j=0;j<axioms.size();j++){
                    Polynomial term=ring.multiply(q[j],axioms[j]);
                    budget=std::max(budget,degree(term));ring.accumulate(error,term,-1);
                }
                Reduction domains=domain_reduce(ring,error,std::vector<int>(9,2));
                verify_reduction(ring,error,std::vector<int>(9,2),domains);
                need(domains.remainder.empty() && std::max(budget,domains.degree)<=D,"ordinary NS lift");
                out<<",\"equation_cofactors\":";write_polynomials(out,q);
                out<<",\"domain_certificate\":";write_reduction(out,domains);
                minimum_ns=D;
            }
            out<<"}\n";
            std::cout<<"NS degree "<<D<<": "<<rows.size()<<" rows, rank "<<span.rank
                     <<", target member "<<(member?"yes":"no")<<".\n";
            if(member)break;
        }
        need(minimum_ns>=4,"NS search did not reach the explicit degree-six upper bound");
        out<<"{\"record\":\"summary\",\"minimum_pc_degree\":4,\"minimum_ns_degree\":"
           <<minimum_ns<<",\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failure");return 0;
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
