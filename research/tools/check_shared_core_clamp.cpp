// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Original-input profiles after clamping the affine cores of shared-bit parents.
#include "domain_polynomial.hpp"
#include "ns_witness.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
using namespace domain_polynomial;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
struct Cert {Polynomial target;std::map<int,Polynomial> cof;};
struct Context {
    Ring r{2,80};std::vector<Polynomial> axioms;int count=0;
    int add(const Polynomial& f){axioms.push_back(f);return int(axioms.size())-1;}
    Cert ax(int id)const{return {axioms.at(id),{{id,r.constant(1)}}};}
    Cert scale(Cert a,const Polynomial& q)const{
        a.target=r.multiply(a.target,q);
        for(auto& [id,f]:a.cof){(void)id;f=r.multiply(f,q);}return a;
    }
    void plus(Cert& a,const Cert& b)const{
        r.accumulate(a.target,b.target);
        for(const auto& [id,f]:b.cof)r.accumulate(a.cof[id],f);
    }
    Cert Boolean(const Polynomial& f)const{
        std::vector<int> powers(9,2);auto red=domain_reduce(r,f,powers);
        verify_reduction(r,f,powers,red);need(red.remainder.empty(),"old Boolean remainder");
        Cert result;result.target=f;
        for(int i=0;i<9;++i)if(!red.coefficients[i].empty())result.cof[i]=red.coefficients[i];
        return result;
    }
    void write(std::ostream& out,const std::string& name,const Cert& c,int budget){
        out<<"{\"record\":\"NS_certificate\",\"name\":\""<<name<<"\",\"target\":";
        write_json(out,c.target);out<<",\"budget\":"<<budget;
        ns_witness::write_terms(out,r,axioms,c.target,c.cof,budget,name);
        out<<"}\n";++count;
    }
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
        Context c;auto& r=c.r;auto one=r.constant(1);
        auto x=[&](int i){return r.variable(i);};
        int h=2,old=9,fresh=old;std::vector<Block> A;
        for(int s=0;s<2;++s)
            A.push_back(make_block(r,{r.subtract(one,x(2+2*s)),r.subtract(one,x(3+2*s))},h,fresh));
        std::vector<int> owner={0,1,0};std::vector<Polynomial> L;
        for(int i=0;i<3;++i)L.push_back(r.add(x(6+i),x(owner[i])));
        auto C=make_block(r,L,h,fresh);int target_variables=fresh;
        std::vector<Block> bottom,source_parent;
        std::map<int,Polynomial> phi;
        for(int s=0;s<2;++s)for(int i=0;i<2;++i){
            auto B=make_block(r,{x(s),x(2+2*s+i)},h,fresh);
            for(int u=0;u<h;++u)for(int j=0;j<2;++j)
                phi[B.variables[u][j]]=r.constant(int(u==j));
            bottom.push_back(B);
        }
        std::vector<Polynomial> T,raw_inputs,inputs;
        for(int s=0;s<2;++s){
            int parent_fresh=A[s].variables[0][0];
            auto P=make_block(r,{bottom[2*s].product,bottom[2*s+1].product},h,parent_fresh);
            need(parent_fresh==A[s].variables.back().back()+1,"source/core coefficient alignment");
            need(degree(P.product)==10,"original star weight");
            source_parent.push_back(P);T.push_back(r.substitute(P.product,phi));
        }
        for(int i=0;i<3;++i){
            raw_inputs.push_back(r.add(x(6+i),source_parent[owner[i]].product));
            inputs.push_back(r.substitute(raw_inputs.back(),phi));
            need(degree(raw_inputs.back())==10 && degree(inputs.back())==6,"original/mapped input ledger");
        }
        int upper_weight=h*(degree(raw_inputs[0])+1);
        need(upper_weight==22,"original third-level weight");
        for(int i=0;i<target_variables;++i)c.add(r.subtract(r.power(x(i),2),x(i)));
        for(const auto& block:A)for(const auto& f:block.companions)c.add(f);
        std::vector<int> cc;for(const auto& f:C.companions)cc.push_back(c.add(f));
        std::vector<int> clamp;for(const auto& block:A)clamp.push_back(c.add(block.product));
        out<<"{\"record\":\"setup\",\"field\":2,\"accuracy\":2,\"old_variables\":9"
           <<",\"retained_variables\":"<<target_variables<<",\"source_variables\":"<<fresh
           <<",\"retained_axioms\":";write_polynomials(out,c.axioms);
        out<<",\"bottom_blocks\":[";
        for(int i=0;i<4;++i){if(i)out<<',';write_block(out,bottom[i]);}
        out<<"],\"source_parents\":[";
        for(int i=0;i<2;++i){if(i)out<<',';write_block(out,source_parent[i]);}
        out<<"],\"affine_star_cores\":[";
        for(int i=0;i<2;++i){if(i)out<<',';write_block(out,A[i]);}
        out<<"],\"third_affine_core\":";write_block(out,C);
        out<<",\"original_third_inputs\":";write_polynomials(out,raw_inputs);
        out<<",\"mapped_third_inputs\":";write_polynomials(out,inputs);
        out<<",\"old_affine_third_inputs\":";write_polynomials(out,L);
        out<<",\"original_star_cost\":10,\"original_third_input_degrees\":[10,10,10]"
             ",\"original_third_cost\":22,\"source_selector_matrix\":[[1,0],[0,1],[1,0]]"
             ",\"after_projection_selector_matrix\":[[],[],[]],"
             "\"scope\":\"conditional profile test; rank-two cores are not instances of the asymptotic high-rank threshold\"}\n";
        std::vector<Cert> errors;
        for(int s=0;s<2;++s){
            auto chi=r.subtract(one,x(s)),value=r.add(x(s),r.multiply(chi,A[s].product));
            auto error=c.Boolean(r.subtract(T[s],value));
            c.plus(error,c.scale(c.ax(clamp[s]),chi));
            need(error.target==r.subtract(T[s],x(s)),"star old-bit comparison");
            c.write(out,"star_to_old_bit_"+std::to_string(s),error,6);errors.push_back(error);
            auto residual=chi;
            for(int i=0;i<2;++i){
                auto g=r.substitute(bottom[2*s+i].product,phi);
                need(g==r.multiply(chi,A[s].inputs[i]),"canonical bottom input");
                need(degree(A[s].prefix[i])+4<=10,"original star prefix budget");
                r.accumulate(residual,r.multiply(A[s].prefix[i],g),-1);
                c.write(out,"star_old_bit_companion_"+std::to_string(s)+"_"+std::to_string(i),
                        c.Boolean(r.multiply(g,x(s))),14);
            }
            auto residual_cert=c.scale(c.ax(clamp[s]),chi);
            need(residual_cert.target==residual,"old-bit prefix residual");
            c.write(out,"star_old_bit_prefix_"+std::to_string(s),residual_cert,10);
            c.write(out,"star_old_bit_Booleanity_"+std::to_string(s),c.ax(s),20);
        }
        auto residual=r.subtract(one,C.product);Cert residual_cert;
        for(int i=0;i<3;++i){
            need(degree(C.prefix[i])+degree(raw_inputs[i])<=upper_weight,"third original prefix bound");
            r.accumulate(residual,r.multiply(C.prefix[i],inputs[i]),-1);
            c.plus(residual_cert,c.scale(errors[owner[i]],r.multiply(r.constant(-1),C.prefix[i])));
        }
        need(residual_cert.target==residual,"third original-input prefix");
        c.write(out,"third_original_input_prefix",residual_cert,upper_weight);
        for(int i=0;i<3;++i){
            auto cert=c.ax(cc[i]);c.plus(cert,c.scale(errors[owner[i]],C.product));
            need(cert.target==r.multiply(inputs[i],C.product),"third original companion");
            c.write(out,"third_original_companion_"+std::to_string(i),cert,upper_weight+degree(raw_inputs[i]));
        }
        Cert cbool;
        for(int i=0;i<3;++i)c.plus(cbool,c.scale(c.ax(cc[i]),r.multiply(r.constant(-1),C.prefix[i])));
        need(cbool.target==r.subtract(r.power(C.product,2),C.product),"third Booleanity");
        c.write(out,"third_Booleanity",cbool,2*upper_weight);
        auto model=[&](const std::string& name,const std::map<int,int>& point,int omit){
            out<<"{\"record\":\"model\",\"name\":\""<<name<<"\",\"assignment\":[";
            for(int i=0;i<target_variables;++i){if(i)out<<',';out<<point.at(i);}
            out<<"],\"omitted_axiom\":"<<omit<<",\"axiom_values\":[";
            for(std::size_t i=0;i<c.axioms.size();++i){
                int v=r.evaluate(c.axioms[i],point);need(int(i)==omit || !v,"retained model");
                if(i)out<<',';
                out<<v;
            }
            int cv=r.evaluate(C.product,point);
            out<<"],\"star_values\":["<<r.evaluate(T[0],point)<<','<<r.evaluate(T[1],point)
               <<"],\"third_value\":"<<cv<<",\"third_input_values\":[";
            for(int i=0;i<3;++i){if(i)out<<',';out<<r.evaluate(inputs[i],point);}
            out<<"],\"third_companion_values\":[";
            for(int i=0;i<3;++i){
                int v=r.evaluate(inputs[i],point)*cv;need(omit>=0 || !v,"third model companion");
                if(i)out<<',';
                out<<v;
            }
            out<<"]}\n";
        };
        int models=0,ones=0;std::vector<int> star_ones(2);
        for(int bits=0;bits<512;++bits){
            std::map<int,int> point;for(int i=0;i<old;++i)point[i]=(bits>>i)&1;
            for(const auto& block:A)assign(r,block,point);
            assign(r,C,point);
            if(r.evaluate(A[0].product,point) || r.evaluate(A[1].product,point))continue;
            for(int s=0;s<2;++s){need(r.evaluate(T[s],point)==point[s],"star profile model");star_ones[s]+=point[s];}
            model("old_point_"+std::to_string(bits),point,-1);++models;ones+=r.evaluate(C.product,point);
            if(bits==1){
                need(r.evaluate(T[0],point)==1 && r.evaluate(inputs[0],point)==1 && point[6]==0,"lost old-offset counter");
                out<<"{\"record\":\"wrong_zero_projection\",\"old_point\":1,\"star_value\":1"
                     ",\"correct_later_input\":1,\"input_after_incorrect_zero_deletion\":0}\n";
            }
        }
        need(models==288 && ones==36 && star_ones==std::vector<int>({144,144}),"complete profile model counts");
        std::map<int,int> missing;for(int i=0;i<old;++i)missing[i]=0;
        missing[2]=missing[3]=1;
        for(const auto& block:A)assign(r,block,missing);
        assign(r,C,missing);
        model("missing_first_core_clamp",missing,clamp[0]);
        need(r.evaluate(inputs[0],missing)*r.evaluate(C.product,missing)==1,"missing clamp fails third companion");
        out<<"{\"record\":\"summary\",\"NS_certificates\":"<<c.count<<",\"clamped_models\":"<<models
           <<",\"third_value_one_models\":"<<ones<<",\"star_value_one_models\":[144,144],"
             "\"missing_clamp_models\":1,\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<c.count<<" exact NS certificates and 288 clamped source models passed; original input costs retained.\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
