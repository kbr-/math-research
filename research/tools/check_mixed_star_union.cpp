// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Overlapping source-group prefixes and a complete residual-corrected OR module.
#include "domain_polynomial.hpp"
#include "ns_witness.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
using namespace domain_polynomial;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
struct Cert {Polynomial target;std::map<int,Polynomial> cof;};
struct Context {
    Ring r{2,80};std::vector<Polynomial> axioms;int count=0;
    int add(const Polynomial& f){axioms.push_back(f);return int(axioms.size())-1;}
    Cert ax(int id)const{return {axioms.at(id),{{id,r.constant(1)}}};}
    Cert scale(Cert c,const Polynomial& q)const{
        c.target=r.multiply(c.target,q);
        for(auto& [id,f]:c.cof){(void)id;f=r.multiply(f,q);}return c;
    }
    void plus(Cert& a,const Cert& b)const{
        r.accumulate(a.target,b.target);
        for(const auto& [id,f]:b.cof)r.accumulate(a.cof[id],f);
    }
    Cert Boolean(const Polynomial& f)const{
        std::vector<int> powers(7,2);auto red=domain_reduce(r,f,powers);
        verify_reduction(r,f,powers,red);need(red.remainder.empty(),"old Boolean remainder");
        Cert c;c.target=f;
        for(int i=0;i<7;++i)if(!red.coefficients[i].empty())c.cof[i]=red.coefficients[i];
        return c;
    }
    void write(std::ostream& out,const std::string& name,const Cert& c,int budget){
        out<<"{\"record\":\"NS_certificate\",\"name\":\""<<name<<"\",\"target\":";
        write_json(out,c.target);out<<",\"budget\":"<<budget;
        ns_witness::write_terms(out,r,axioms,c.target,c.cof,budget,name);
        out<<"}\n";++count;
    }
};
struct Profile {
    Polynomial value;
    std::vector<int> inputs;
    std::map<int,Polynomial> prefix;
    std::map<int,Cert> companions;
    Cert residual;
};
void assign(const Ring& r,const Block& A,std::map<int,int>& point){
    for(const auto& row:A.variables)for(int id:row)point[id]=0;
    for(std::size_t i=0;i<A.inputs.size();++i)
        if(r.evaluate(A.inputs[i],point)){point[A.variables[0][i]]=1;break;}
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");
        Context c;auto& r=c.r;auto one=r.constant(1),minus=r.constant(-1);
        auto x=[&](int id){return r.variable(id);};
        int h=2,old=7,fresh=old;
        std::vector<std::vector<int>> member={{0,1},{0,2},{3,4}};
        std::vector<std::vector<int>> other={{1,3},{0,4},{5,6}};
        std::vector<std::pair<int,int>> pairs={{0,1},{0,3},{1,4},{2,5},{2,6}};
        std::vector<Polynomial> chi,G;
        for(int s=0;s<3;++s)chi.push_back(r.subtract(one,x(s)));
        for(const auto& [a,b]:pairs)G.push_back(r.multiply(r.subtract(one,x(a)),r.subtract(one,x(b))));
        std::vector<Block> A,B;
        for(int s=0;s<3;++s)
            A.push_back(make_block(r,{r.subtract(one,x(other[s][0])),r.subtract(one,x(other[s][1]))},h,fresh));
        std::vector<std::vector<int>> groups={{0,1},{0,1,2}},union_inputs={{0,1,2},{0,1,2,3,4}};
        for(const auto& list:groups){
            std::vector<Polynomial> truth;for(int s:list)truth.push_back(chi[s]);
            B.push_back(make_block(r,truth,h,fresh));
        }
        int target_variables=fresh;
        std::vector<Block> raw_bottom,raw_union;std::map<int,Polynomial> phi;
        for(const auto& [a,b]:pairs){
            auto block=make_block(r,{x(a),x(b)},h,fresh);
            for(int u=0;u<h;++u)for(int j=0;j<2;++j)phi[block.variables[u][j]]=r.constant(int(u==j));
            raw_bottom.push_back(block);
        }
        for(int i=0;i<5;++i)need(r.substitute(raw_bottom[i].product,phi)==G[i],"canonical bottom map");
        for(const auto& list:union_inputs){
            std::vector<Polynomial> raw;for(int i:list)raw.push_back(raw_bottom[i].product);
            raw_union.push_back(make_block(r,raw,h,fresh));
            need(degree(raw_union.back().product)==10,"original same-level union weight");
        }
        for(int i=0;i<target_variables;++i)c.add(r.subtract(r.power(x(i),2),x(i)));
        for(const auto& block:A)for(const auto& f:block.companions)c.add(f);
        std::vector<std::vector<int>> bc;
        for(const auto& block:B){
            std::vector<int> ids;for(const auto& f:block.companions)ids.push_back(c.add(f));bc.push_back(ids);
        }
        std::vector<int> clamp;for(const auto& block:A)clamp.push_back(c.add(block.product));
        out<<"{\"record\":\"setup\",\"field\":2,\"accuracy\":2,\"old_variables\":7"
           <<",\"retained_variables\":"<<target_variables<<",\"source_variables\":"<<fresh
           <<",\"canonical_inputs\":";write_polynomials(out,G);
        out<<",\"retained_axioms\":";write_polynomials(out,c.axioms);
        out<<",\"star_cores\":[";
        for(int s=0;s<3;++s){if(s)out<<',';write_block(out,A[s]);}
        out<<"],\"union_cores\":[";write_block(out,B[0]);out<<',';write_block(out,B[1]);
        out<<"],\"original_bottom_blocks\":[";
        for(int i=0;i<5;++i){if(i)out<<',';write_block(out,raw_bottom[i]);}
        out<<"],\"original_union_blocks\":[";write_block(out,raw_union[0]);out<<',';write_block(out,raw_union[1]);
        out<<"],\"star_input_indices\":[[0,1],[0,2],[3,4]],\"union_input_indices\":[[0,1,2],[0,1,2,3,4]]"
             ",\"original_input_degree\":4,\"original_union_weight\":10"
             ",\"scope\":\"conditional profiles over rank-two clamped cores; original union products record degrees, not a raw union coefficient map\"}\n";
        std::vector<Profile> P;
        for(int u=0;u<2;++u){
            Profile p;p.value=B[u].product;p.inputs=union_inputs[u];
            for(std::size_t j=0;j<groups[u].size();++j){
                int s=groups[u][j];
                for(int t=0;t<2;++t)
                    r.accumulate(p.prefix[member[s][t]],r.multiply(B[u].prefix[j],A[s].prefix[t]));
                c.plus(p.residual,c.scale(c.ax(clamp[s]),r.multiply(B[u].prefix[j],chi[s])));
            }
            auto residual=r.subtract(one,p.value);
            std::vector<Polynomial> prefixes;
            for(int i:p.inputs){
                need(degree(p.prefix[i])+4<=10,"composed original-input prefix bound");
                r.accumulate(residual,r.multiply(p.prefix[i],G[i]),-1);prefixes.push_back(p.prefix[i]);
                bool found=false;
                for(std::size_t j=0;j<groups[u].size() && !found;++j){
                    int s=groups[u][j];
                    for(int t=0;t<2;++t)if(member[s][t]==i){
                        need(G[i]==r.multiply(chi[s],A[s].inputs[t]),"input cover factor");
                        p.companions[i]=c.scale(c.ax(bc[u][j]),A[s].inputs[t]);found=true;break;
                    }
                }
                need(found && p.companions[i].target==r.multiply(G[i],p.value),"covered companion");
            }
            need(p.residual.target==residual,"composed prefix residual");
            c.write(out,"union_"+std::to_string(u)+"_prefix",p.residual,10);
            for(int i:p.inputs)c.write(out,"union_"+std::to_string(u)+"_companion_"+std::to_string(i),p.companions[i],14);
            Cert boolean;
            for(std::size_t j=0;j<groups[u].size();++j)
                c.plus(boolean,c.scale(c.ax(bc[u][j]),r.multiply(minus,B[u].prefix[j])));
            need(boolean.target==r.subtract(r.power(p.value,2),p.value),"union Booleanity");
            c.write(out,"union_"+std::to_string(u)+"_Booleanity",boolean,20);
            out<<"{\"record\":\"profile\",\"union\":"<<u<<",\"value\":";write_json(out,p.value);
            out<<",\"input_order\":[";
            for(std::size_t j=0;j<p.inputs.size();++j){if(j)out<<',';out<<p.inputs[j];}
            out<<"],\"prefix_coefficients\":";write_polynomials(out,prefixes);
            out<<",\"constructed_cost\":10,\"original_cost\":10}\n";
            P.push_back(p);
        }
        Profile star;star.value=x(2);star.inputs=member[2];
        star.residual=c.scale(c.ax(clamp[2]),chi[2]);
        for(int t=0;t<2;++t){
            int i=member[2][t];star.prefix[i]=A[2].prefix[t];
            star.companions[i]=c.Boolean(r.multiply(G[i],star.value));
        }
        auto& a=P[0];auto& combined=P[1];auto& b=star;Cert relation;
        for(int i:a.inputs)c.plus(relation,c.scale(combined.companions[i],a.prefix[i]));
        for(int i:b.inputs)c.plus(relation,c.scale(combined.companions[i],r.multiply(a.value,b.prefix[i])));
        for(int i:a.inputs)c.plus(relation,c.scale(a.companions[i],r.multiply(minus,r.multiply(b.value,combined.prefix[i]))));
        for(int i:b.inputs)c.plus(relation,c.scale(b.companions[i],r.multiply(minus,r.multiply(a.value,combined.prefix[i]))));
        auto child_residual=c.scale(a.residual,combined.value);
        c.plus(relation,child_residual);
        c.plus(relation,c.scale(b.residual,r.multiply(combined.value,a.value)));
        c.plus(relation,c.scale(combined.residual,r.multiply(minus,r.multiply(a.value,b.value))));
        auto target=r.subtract(combined.value,r.multiply(a.value,b.value));
        need(relation.target==target,"actual OR relation");
        c.write(out,"actual_mixed_OR_module",relation,30);
        auto omitted=relation;c.plus(omitted,c.scale(child_residual,minus));
        need(omitted.target!=target,"nonvacuous omitted residual control");
        std::ostringstream scratch;bool rejected=false;
        try{ns_witness::write_terms(scratch,r,c.axioms,target,omitted.cof,30,"omitted child residual");}
        catch(const std::runtime_error&){rejected=true;}
        need(rejected && scratch.str().empty(),"incomplete OR witness accepted");
        out<<"{\"record\":\"omitted_OR_residual_control\",\"rejected\":true,\"omitted_prefix_certificate\":\"union_0_prefix\""
             ",\"multiplier\":";write_json(out,combined.value);
        out<<",\"target_difference\":";write_json(out,r.subtract(omitted.target,target));out<<"}\n";
        auto model=[&](const std::string& name,const std::map<int,int>& point,int omit){
            out<<"{\"record\":\"model\",\"name\":\""<<name<<"\",\"assignment\":[";
            for(int i=0;i<target_variables;++i){if(i)out<<',';out<<point.at(i);}
            out<<"],\"omitted_axiom\":"<<omit<<",\"axiom_values\":[";
            for(std::size_t i=0;i<c.axioms.size();++i){
                int value=r.evaluate(c.axioms[i],point);need(int(i)==omit || !value,"retained model");
                if(i)out<<',';
                out<<value;
            }
            out<<"],\"union_values\":["<<r.evaluate(B[0].product,point)<<','<<r.evaluate(B[1].product,point)
               <<"],\"OR_relation_value\":"<<r.evaluate(target,point)<<"}\n";
        };
        int models=0,first_ones=0,all_ones=0;
        for(int bits=0;bits<128;++bits){
            std::map<int,int> point;for(int i=0;i<old;++i)point[i]=(bits>>i)&1;
            for(const auto& block:A)assign(r,block,point);
            for(const auto& block:B)assign(r,block,point);
            bool valid=true;for(const auto& block:A)valid&=!r.evaluate(block.product,point);
            if(!valid)continue;
            model("old_point_"+std::to_string(bits),point,-1);++models;
            first_ones+=r.evaluate(B[0].product,point);all_ones+=r.evaluate(B[1].product,point);
            need(!r.evaluate(target,point),"OR model relation");
        }
        need(models==54 && first_ones==6 && all_ones==3,"complete model counts");
        std::map<int,int> overlap;for(int i=0;i<old;++i)overlap[i]=0;
        for(const auto& block:A)assign(r,block,overlap);
        for(const auto& block:B)assign(r,block,overlap);
        for(const auto& row:B[0].variables)for(int id:row)overlap[id]=0;
        overlap[B[0].variables[0][1]]=1;
        model("overlapping_input_uses_second_group",overlap,-1);
        auto missing_term=r.multiply(B[0].prefix[1],A[1].prefix[0]);
        auto bad=r.add(P[0].residual.target,r.multiply(missing_term,G[0]));
        need(r.evaluate(bad,overlap)==1,"omitted overlap prefix control");
        out<<"{\"record\":\"missing_overlap_prefix_control\",\"model\":\"overlapping_input_uses_second_group\""
             ",\"input_index\":0,\"omitted_prefix_term\":";write_json(out,missing_term);
        out<<",\"wrong_prefix_residual_value\":1}\n";
        std::map<int,int> missing;for(int i=0;i<old;++i)missing[i]=0;
        missing[1]=missing[3]=1;
        for(const auto& block:A)assign(r,block,missing);
        for(const auto& block:B)assign(r,block,missing);
        model("missing_first_star_clamp",missing,clamp[0]);
        need(r.evaluate(P[1].residual.target,missing)==1,"missing star clamp control");
        std::map<int,int> no_comp;for(int i=0;i<old;++i)no_comp[i]=0;
        no_comp[1]=no_comp[2]=1;
        for(const auto& block:A)assign(r,block,no_comp);
        for(const auto& block:B)assign(r,block,no_comp);
        for(const auto& row:B[1].variables)for(int id:row)no_comp[id]=0;
        model("missing_union_truth_companion",no_comp,bc[1][0]);
        need(r.evaluate(r.multiply(G[1],B[1].product),no_comp)==1,"missing union companion control");
        out<<"{\"record\":\"summary\",\"NS_certificates\":"<<c.count<<",\"canonical_models\":"<<models
           <<",\"union_value_one_models\":[6,3],\"additional_control_models\":3,\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<c.count<<" complete NS witnesses passed, including the actual OR module; overlapping-input controls passed.\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
