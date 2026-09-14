// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact complete NS images for a positive-MOD tuple with a shared affine probe.
#include "domain_polynomial.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace domain_polynomial;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
struct Cert {Polynomial target;std::map<int,Polynomial> cof;};
struct Context {
    Ring r;
    int old_count;
    std::vector<int> sizes;
    std::vector<Polynomial> axioms;
    std::vector<std::string> names;
    int certificates=0,models=0;
    Context(int p,int old):r(p,64),old_count(old){}
    int add(const std::string& name,const Polynomial& f){
        int id=int(axioms.size());axioms.push_back(f);names.push_back(name);return id;
    }
    void domains(int total){
        for(int i=0;i<total;++i){
            int size=i<old_count?2:r.p;sizes.push_back(size);
            auto x=r.variable(i);
            need(add("domain/"+std::to_string(i),r.subtract(r.power(x,size),x))==i,"domain index");
        }
    }
    Cert ax(int id)const{return {axioms.at(id),{{id,r.constant(1)}}};}
    Cert scale(Cert c,const Polynomial& q)const{
        c.target=r.multiply(c.target,q);
        for(auto& [id,f]:c.cof){(void)id;f=r.multiply(f,q);}
        return c;
    }
    void plus(Cert& a,const Cert& b)const{
        r.accumulate(a.target,b.target);
        for(const auto& [id,f]:b.cof)r.accumulate(a.cof[id],f);
    }
    Cert domain(const Polynomial& f,bool old_only)const{
        auto powers=old_only?std::vector<int>(old_count,2):sizes;
        auto reduced=domain_reduce(r,f,powers);
        verify_reduction(r,f,powers,reduced);
        need(reduced.remainder.empty(),"nonzero typed-domain remainder");
        Cert result;result.target=f;
        for(std::size_t i=0;i<reduced.coefficients.size();++i)
            if(!reduced.coefficients[i].empty())result.cof[int(i)]=reduced.coefficients[i];
        return result;
    }
    void write(std::ostream& out,const std::string& name,const Cert& c,int budget,
               int original_degree=-1){
        Polynomial reconstructed;int used=0;bool comma=false;
        out<<"{\"record\":\"NS_certificate\",\"name\":\""<<name<<"\",\"target\":";
        write_json(out,c.target);
        out<<",\"budget\":"<<budget<<",\"original_axiom_degree\":"<<original_degree<<",\"terms\":[";
        for(const auto& [id,q]:c.cof)if(!q.empty() && !axioms.at(id).empty()){
            r.accumulate(reconstructed,r.multiply(q,axioms[id]));
            used=std::max(used,degree(q)+degree(axioms[id]));
            if(comma)out<<',';
            comma=true;out<<"{\"axiom_id\":"<<id<<",\"cofactor\":";write_json(out,q);out<<'}';
        }
        need(reconstructed==c.target && used<=budget,"NS certificate "+name);
        if(original_degree>=0)need(used<=r.p*original_degree,"original-degree transfer ceiling");
        out<<"],\"witness_degree\":"<<used<<"}\n";++certificates;
    }
    void header(std::ostream& out,const std::string& name,int h)const{
        out<<"{\"record\":\"case\",\"name\":\""<<name<<"\",\"field\":"<<r.p
           <<",\"accuracy\":"<<h<<",\"old_Boolean_variables\":"<<old_count
           <<",\"domain_exponents\":[";
        for(std::size_t i=0;i<sizes.size();++i){if(i)out<<',';out<<sizes[i];}
        out<<"],\"axioms\":[";
        for(std::size_t i=0;i<axioms.size();++i){
            if(i)out<<',';
            out<<"{\"id\":"<<i<<",\"name\":\""<<names[i]<<"\",\"polynomial\":";
            write_json(out,axioms[i]);out<<'}';
        }
        out<<"]}\n";
    }
    void model(std::ostream& out,const std::string& name,const std::map<int,int>& point,
               const std::map<int,Polynomial>& images,const Polynomial& probe,int expected){
        out<<"{\"record\":\"typed_model\",\"name\":\""<<name<<"\",\"assignment\":[";
        for(std::size_t i=0;i<sizes.size();++i){if(i)out<<',';out<<point.at(int(i));}
        out<<"],\"axiom_values\":[";
        for(std::size_t i=0;i<axioms.size();++i){
            int value=r.evaluate(axioms[i],point);need(value==0,"invalid retained-system model");
            if(i)out<<',';
            out<<value;
        }
        out<<"],\"mapped_coefficient_values\":[";bool comma=false;
        for(const auto& [id,beta]:images){
            if(comma)out<<',';
            comma=true;out<<'['<<id<<','<<r.evaluate(beta,point)<<']';
        }
        int value=r.evaluate(probe,point);need(value==expected,"model probe");
        out<<"],\"probe\":";write_json(out,probe);out<<",\"probe_value\":"<<value<<"}\n";++models;
    }
};
void assign_core(const Ring& r,const Block& b,std::map<int,int>& point){
    for(const auto& row:b.variables)for(int id:row)point[id]=0;
    for(std::size_t i=0;i<b.inputs.size();++i){
        int value=r.evaluate(b.inputs[i],point);
        need(value==0 || value==1,"specialized affine input is not a Boolean literal or constant");
        if(value){point[b.variables[0][i]]=1;break;}
    }
}
void run_case(std::ostream& out,int prime,int h,bool varied){
    int old=prime==3?3:4,m=3,fresh=old;
    Context c(prime,old);const auto& r=c.r;auto one=r.constant(1);
    std::vector<Polynomial> literals={r.variable(0),r.subtract(one,r.variable(1)),r.variable(2)};
    std::vector<int> slopes={1,varied?2:1,varied?0:1};
    std::vector<int> offsets={0,1,varied?1:2};
    Polynomial t;for(int i=0;i<old;++i)r.accumulate(t,r.variable(i));
    std::vector<Polynomial> inputs,chi;
    for(int i=0;i<m;++i){
        auto L=r.add(r.add(r.multiply(r.constant(slopes[i]),t),literals[i]),r.constant(offsets[i]));
        inputs.push_back(r.subtract(one,r.power(L,prime-1)));
        need(degree(inputs.back())==prime-1,"original input degree");
    }
    std::vector<Block> cores;
    for(int alpha=0;alpha<prime;++alpha){
        chi.push_back(r.subtract(one,r.power(r.subtract(t,r.constant(alpha)),prime-1)));
        std::vector<Polynomial> list;
        for(int i=0;i<m;++i){
            int a=r.residue(slopes[i]*alpha+offsets[i]),b=r.residue(a+1);
            int g0=r.residue(1-r.evaluate(r.power(r.constant(a),prime-1),{}));
            int g1=r.residue(1-r.evaluate(r.power(r.constant(b),prime-1),{}));
            auto G=r.add(r.constant(g0),r.multiply(r.constant(g1-g0),literals[i]));
            need(degree(G)<=1,"specialized input not affine");
            list.push_back(G);
        }
        cores.push_back(make_block(r,list,h,fresh));
    }
    int total=fresh;auto source=make_block(r,inputs,h,fresh);
    need(degree(source.product)==h*prime,"original product weight");
    c.domains(total);std::vector<std::vector<int>> comp(prime);
    for(int alpha=0;alpha<prime;++alpha)for(int i=0;i<m;++i)
        comp[alpha].push_back(c.add("affine/"+std::to_string(alpha)+"/"+std::to_string(i),
                                  cores[alpha].companions[i]));
    std::map<int,Polynomial> images,wrong,missing;
    for(int u=0;u<h;++u)for(int i=0;i<m;++i){
        Polynomial beta,short_beta;
        for(int alpha=0;alpha<prime;++alpha){
            auto piece=r.multiply(chi[alpha],r.variable(cores[alpha].variables[u][i]));
            r.accumulate(beta,piece);
            if(alpha!=prime-1)r.accumulate(short_beta,piece);
        }
        need(degree(beta)<=prime,"coefficient image degree");
        int id=source.variables[u][i];
        images[id]=beta;wrong[id]=r.variable(cores[0].variables[u][i]);missing[id]=short_beta;
    }
    Polynomial V;
    for(int alpha=0;alpha<prime;++alpha)r.accumulate(V,r.multiply(chi[alpha],cores[alpha].product));
    auto mapped=r.substitute(source.product,images);
    std::vector<Polynomial> mapped_companions;
    for(const auto& companion:source.companions)
        mapped_companions.push_back(r.substitute(companion,images));
    auto difference=c.domain(r.subtract(mapped,V),true);
    std::string name="shared_probe_F"+std::to_string(prime)+"_h"+std::to_string(h)+(varied?"_varied":"_uniform");
    c.header(out,name,h);
    out<<"{\"record\":\"construction\",\"probe\":";write_json(out,t);
    out<<",\"literals\":";write_polynomials(out,literals);
    out<<",\"slopes\":[";for(int i=0;i<m;++i){if(i)out<<',';out<<slopes[i];}
    out<<"],\"offsets\":[";for(int i=0;i<m;++i){if(i)out<<',';out<<offsets[i];}
    out<<"],\"source_block\":";write_block(out,source);
    out<<",\"affine_blocks\":[";
    for(int alpha=0;alpha<prime;++alpha){if(alpha)out<<',';write_block(out,cores[alpha]);}
    out<<"],\"selectors\":";write_polynomials(out,chi);
    out<<",\"canonical_value\":";write_json(out,V);
    out<<",\"mapped_product\":";write_json(out,mapped);
    out<<",\"coefficient_images\":[";bool comma=false;
    for(const auto& [id,beta]:images){
        if(comma)out<<',';
        comma=true;out<<"{\"variable\":"<<id<<",\"image\":";write_json(out,beta);out<<'}';
    }
    out<<"],\"map_degree_bound\":"<<prime<<",\"new_block_count\":"<<prime
       <<",\"original_product_weight\":"<<h*prime<<"}\n";
    c.write(out,"product_difference_old_Boolean_only",difference,h*(2*prime-1));
    for(int alpha=0;alpha<prime;++alpha)for(int i=0;i<m;++i){
        auto target=r.multiply(chi[alpha],r.subtract(inputs[i],cores[alpha].inputs[i]));
        c.write(out,"conditional_input/"+std::to_string(alpha)+"/"+std::to_string(i),
                c.domain(target,true),2*(prime-1));
    }
    for(int i=0;i<m;++i){
        auto witness=c.scale(difference,inputs[i]);
        for(int alpha=0;alpha<prime;++alpha){
            c.plus(witness,c.scale(c.ax(comp[alpha][i]),chi[alpha]));
            auto local=c.domain(r.multiply(chi[alpha],r.subtract(inputs[i],cores[alpha].inputs[i])),true);
            c.plus(witness,c.scale(local,cores[alpha].product));
        }
        need(witness.target==mapped_companions[i],"complete companion image");
        c.write(out,"source_companion/"+std::to_string(i),witness,
                h*(2*prime-1)+prime-1,h*prime+prime-1);
    }
    for(const auto& [id,beta]:images)
        c.write(out,"source_field/"+std::to_string(id),
                c.domain(r.subtract(r.power(beta,prime),beta),false),prime*prime,prime);
    auto wrong_product=r.substitute(source.product,wrong);
    auto missing_product=r.substitute(source.product,missing);
    bool wrong_found=false,missing_found=false,nonBoolean_found=false;
    std::vector<int> residues(prime),source_zero_states;
    for(int bits=0;bits<(1<<old);++bits){
        std::map<int,int> point;
        for(int i=0;i<total;++i)point[i]=i<old?(bits>>i)&1:0;
        int alpha=r.evaluate(t,point);++residues[alpha];
        for(const auto& A:cores)assign_core(r,A,point);
        int value=r.evaluate(mapped,point);
        need(value==r.evaluate(V,point),"typed product equality");
        bool common_zero=true;
        out<<"{\"record\":\"old_Boolean_state\",\"bits\":"<<bits<<",\"probe_value\":"<<alpha<<",\"inputs\":[";
        for(int i=0;i<m;++i){
            int g=r.evaluate(inputs[i],point);common_zero&=g==0;
            need(g==r.evaluate(cores[alpha].inputs[i],point),"conditional literal equality");
            need(r.evaluate(mapped_companions[i],point)==0,"mapped companion model");
            if(i)out<<',';
            out<<g;
        }
        if(common_zero)source_zero_states.push_back(bits);
        out<<"],\"product_value\":"<<value<<"}\n";
        c.model(out,name+"/state_"+std::to_string(bits),point,images,r.subtract(mapped,V),0);
        for(int i=0;i<m && (!wrong_found || !missing_found);++i){
            auto bad=r.multiply(inputs[i],wrong_product);int v=r.evaluate(bad,point);
            if(!wrong_found && v){
                c.model(out,name+"/unconditional_branch_fails",point,wrong,bad,v);wrong_found=true;
            }
            bad=r.multiply(inputs[i],missing_product);v=r.evaluate(bad,point);
            if(!missing_found && v){
                need(alpha==prime-1,"missing-residue countermodel at wrong residue");
                c.model(out,name+"/omitted_residue_fails",point,missing,bad,v);missing_found=true;
            }
        }
        if(!nonBoolean_found){
            std::vector<int> active;
            for(int i=0;i<m;++i)if(r.evaluate(cores[alpha].inputs[i],point)==1)active.push_back(i);
            if(active.size()>=2){
                for(const auto& row:cores[alpha].variables)for(int id:row)point[id]=0;
                point[cores[alpha].variables[0][active[0]]]=2;
                point[cores[alpha].variables[0][active[1]]]=prime-1;
                need(r.evaluate(images.at(source.variables[0][active[0]]),point)==2,"nonBoolean source coefficient");
                for(const auto& companion:mapped_companions)
                    need(r.evaluate(companion,point)==0,"nonBoolean mapped companion");
                c.model(out,name+"/nonBoolean_coefficient",point,images,r.subtract(mapped,V),0);
                nonBoolean_found=true;
            }
        }
    }
    need(wrong_found && missing_found && nonBoolean_found,"missing control");
    for(int count:residues)need(count>0,"probe did not attain every residue");
    out<<"{\"record\":\"case_summary\",\"name\":\""<<name<<"\",\"certificates\":"<<c.certificates
       <<",\"models\":"<<c.models<<",\"old_states\":"<<(1<<old)<<",\"probe_residue_counts\":[";
    for(int alpha=0;alpha<prime;++alpha){if(alpha)out<<',';out<<residues[alpha];}
    out<<"],\"common_zero_states\":[";
    for(std::size_t i=0;i<source_zero_states.size();++i){if(i)out<<',';out<<source_zero_states[i];}
    out<<"],\"wrong_branch_rejected\":true,\"missing_residue_rejected\":true,"
         "\"nonBoolean_coefficients_exercised\":true,\"passed\":true}\n";
    std::cout<<name<<": "<<c.certificates<<" complete NS certificates, "<<c.models
             <<" retained-system models; all residues and controls passed.\n";
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");
        out<<"{\"record\":\"schema\",\"version\":1,\"polynomials\":\"[coefficient,[variable IDs with repetitions]]\","
             "\"scope\":\"complete raw one-level shared-probe source maps over a satisfiable typed domain, not a PHP refutation\","
             "\"NS\":\"ordinary target=sum(cofactor*axiom), retaining original image budgets\"}\n";
        run_case(out,3,1,false);run_case(out,3,2,true);run_case(out,5,1,false);
        out<<"{\"record\":\"summary\",\"cases\":3,\"passed\":true}\n";
        need(bool(out),"output write");
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
