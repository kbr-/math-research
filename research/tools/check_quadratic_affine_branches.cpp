// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Complete binary coefficient maps after conditioning linear coordinates.
#include "domain_polynomial.hpp"
#include "ns_witness.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace domain_polynomial;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
struct Cert {Polynomial target;std::map<int,Polynomial> cof;};
struct Context {
    Ring r{2,100};
    int old=5,count=0;
    std::vector<Polynomial> axioms;
    int add(const Polynomial& f){axioms.push_back(f);return int(axioms.size())-1;}
    Cert ax(int id)const{return {axioms.at(id),{{id,r.constant(1)}}};}
    Cert scale(Cert c,const Polynomial& f)const{
        c.target=r.multiply(c.target,f);
        for(auto& [id,a]:c.cof){(void)id;a=r.multiply(a,f);}return c;
    }
    void plus(Cert& a,const Cert& b)const{
        r.accumulate(a.target,b.target);
        for(const auto& [id,f]:b.cof)r.accumulate(a.cof[id],f);
    }
    Cert Boolean(const Polynomial& f)const{
        std::vector<int> powers(old,2);
        auto red=domain_reduce(r,f,powers);verify_reduction(r,f,powers,red);
        need(red.remainder.empty(),"nonzero old-Boolean remainder");
        Cert result;result.target=f;
        for(int i=0;i<old;++i)if(!red.coefficients[i].empty())result.cof[i]=red.coefficients[i];
        return result;
    }
    void write(std::ostream& out,int h,const std::string& name,const Cert& c,int budget,
               const Polynomial* source=nullptr){
        out<<"{\"record\":\"NS_certificate\",\"accuracy\":"<<h<<",\"name\":\""<<name
           <<"\",\"target\":";write_json(out,c.target);out<<",\"budget\":"<<budget;
        if(source){
            need(budget<=3*degree(*source),"threefold original-degree budget");
            out<<",\"source_axiom\":";write_json(out,*source);
            out<<",\"original_degree\":"<<degree(*source)<<",\"transfer_ceiling\":"<<3*degree(*source);
        }
        ns_witness::write_terms(out,r,axioms,c.target,c.cof,budget,name);
        out<<"}\n";++count;
    }
};
int rank(std::vector<unsigned> rows){
    unsigned basis[32]={};int result=0;
    for(unsigned x:rows)for(int bit=31;bit>=0;--bit)if(x&(1u<<bit)){
        if(basis[bit])x^=basis[bit];else{basis[bit]=x;++result;break;}
    }
    return result;
}
void assignment(std::ostream& out,const std::map<int,int>& point,int end){
    out<<'[';for(int id=0;id<end;++id){if(id)out<<',';out<<point.at(id);}out<<']';
}
int run(std::ostream& out,int h){
    Context c;auto& r=c.r;auto one=r.constant(1);
    auto x=[&](int id){return r.variable(id);};
    const int t=2,T=3;
    std::vector<std::vector<unsigned>> masks={{1,2},{5,6},{9,10},{17,18}};
    std::vector<std::vector<int>> lists={{0,1,2},{1,2,3}};
    std::vector<std::vector<Polynomial>> factors={
        {x(0),x(1)},{r.add(x(0),x(2)),r.add(x(1),x(2))},
        {r.add(x(0),x(3)),r.add(x(1),x(3))},
        {r.add(x(0),x(4)),r.add(x(1),x(4))}};
    std::vector<Polynomial> q;
    for(const auto& pair:factors)q.push_back(r.multiply(pair[0],pair[1]));
    for(int a=0;a<2;++a){
        std::vector<unsigned> selected=masks[lists[a][0]];
        need(rank(selected)==2,"selected pair is independent");
        for(int i:lists[a]){
            auto extended=selected;extended.insert(extended.end(),masks[i].begin(),masks[i].end());
            need(rank(extended)<=3,"maximal selected pair has rank-at-most-one quotients");
        }
        auto all=selected;
        for(int i:lists[a])all.insert(all.end(),masks[i].begin(),masks[i].end());
        need(rank(all)==4,"large joint span despite one selected pair");
        for(const auto& f:factors[lists[a][0]]){
            bool common=true;
            for(int i:lists[a])common=common && (f==factors[i][0] || f==factors[i][1]);
            need(!common,"fixture has no common affine polynomial factor");
        }
    }
    std::vector<std::vector<Polynomial>> probes={factors[0],factors[1]};
    std::vector<std::vector<Polynomial>> tails={{Polynomial{},x(2),x(3)},
        {Polynomial{},r.add(x(2),x(3)),r.add(x(2),x(4))}};
    int fresh=c.old;
    std::vector<std::vector<Block>> cores(2);
    std::vector<std::vector<Polynomial>> selectors(2);
    for(int a=0;a<2;++a){
        Polynomial partition;
        for(int s=0;s<4;++s){
            auto chi=one;
            for(int j=0;j<2;++j)chi=r.multiply(chi,(s&(1<<j))?probes[a][j]:r.subtract(one,probes[a][j]));
            selectors[a].push_back(chi);r.accumulate(partition,chi);
            int u=s&1,v=(s>>1)&1;
            std::vector<Polynomial> g;
            for(const auto& tail:tails[a])g.push_back(r.add(r.constant(u*v),
                r.multiply(r.constant(1+u+v),tail)));
            for(const auto& f:g)need(degree(f)<=1,"affine branch input");
            cores[a].push_back(make_block(r,g,h,fresh));
        }
        need(partition==one,"literal selector partition");
    }
    const int retained_end=fresh;
    for(int id=0;id<retained_end;++id)c.add(r.subtract(r.power(x(id),2),x(id)));
    std::vector<std::vector<std::vector<int>>> companion_ids(2);
    for(int a=0;a<2;++a)for(int s=0;s<4;++s){
        std::vector<int> ids;
        for(const auto& f:cores[a][s].companions)ids.push_back(c.add(f));
        companion_ids[a].push_back(ids);
    }
    std::vector<Block> bottoms,parents;
    std::map<int,Polynomial> phi;
    if(h==1)for(const auto& pair:factors){
        auto B=make_block(r,{r.subtract(one,pair[0]),r.subtract(one,pair[1])},1,fresh);
        phi[B.variables[0][0]]=one;phi[B.variables[0][1]]=pair[0];
        need(r.substitute(B.product,phi)==r.multiply(pair[0],pair[1]),"literal quadratic bottom image");
        bottoms.push_back(B);
    }
    for(int a=0;a<2;++a){
        std::vector<Polynomial> inputs;
        for(int i:lists[a])inputs.push_back(h==1?bottoms[i].product:q[i]);
        parents.push_back(make_block(r,inputs,h,fresh));
        for(int u=0;u<h;++u)for(int i=0;i<3;++i){
            Polynomial beta;
            for(int s=0;s<4;++s)r.accumulate(beta,
                r.multiply(selectors[a][s],x(cores[a][s].variables[u][i])));
            need(degree(beta)<=T,"coefficient-image degree");
            phi[parents[a].variables[u][i]]=beta;
        }
    }
    out<<"{\"record\":\"case\",\"field\":2,\"accuracy\":"<<h<<",\"old_variables\":5"
       <<",\"retained_variables\":"<<retained_end<<",\"source_variables_end\":"<<fresh
       <<",\"source_scope\":\""<<(h==1?"actual two-level family":"quadratic intermediate family")
       <<"\",\"coordinate_dimension\":2,\"transfer_factor\":3,\"selected_pair_indices\":[0,1]"
       <<",\"factor_masks\":[[1,2],[5,6],[9,10],[17,18]],\"parent_lists\":[[0,1,2],[1,2,3]],"
         "\"quadratic_inputs\":";write_polynomials(out,q);
    out<<",\"bottom_blocks\":[";
    for(std::size_t i=0;i<bottoms.size();++i){if(i)out<<',';write_block(out,bottoms[i]);}
    out<<"],\"parents\":[";write_block(out,parents[0]);out<<',';write_block(out,parents[1]);
    out<<"],\"affine_cores\":[";
    for(int a=0;a<2;++a)for(int s=0;s<4;++s){if(a || s)out<<',';write_block(out,cores[a][s]);}
    out<<"],\"selectors\":[";
    write_polynomials(out,selectors[0]);out<<',';write_polynomials(out,selectors[1]);
    out<<"],\"retained_axioms\":";write_polynomials(out,c.axioms);
    out<<",\"coefficient_map\":[";bool comma=false;
    for(const auto& [id,f]:phi){if(comma)out<<',';comma=true;out<<'['<<id<<',';write_json(out,f);out<<']';}
    out<<"]}\n";
    std::vector<Polynomial> source_images;
    auto source_cert=[&](const std::string& name,const Polynomial& source,const Cert& cert,int budget){
        auto image=r.substitute(source,phi);need(image==cert.target,"complete source image");
        c.write(out,h,name,cert,budget,&source);source_images.push_back(image);
    };
    for(int i=0;i<c.old;++i)source_cert("old_Boolean_"+std::to_string(i),c.axioms[i],c.ax(i),2);
    for(std::size_t b=0;b<bottoms.size();++b){
        for(int i=0;i<2;++i){
            const auto& source=bottoms[b].companions[i];
            source_cert("bottom_companion_"+std::to_string(b)+"_"+std::to_string(i),
                        source,c.Boolean(r.substitute(source,phi)),3);
        }
        for(int id:bottoms[b].variables[0]){
            auto source=r.subtract(r.power(x(id),2),x(id));
            source_cert("bottom_field_"+std::to_string(id),source,c.Boolean(r.substitute(source,phi)),2);
        }
    }
    for(int a=0;a<2;++a){
        Polynomial V;
        std::vector<std::vector<Cert>> input_errors(4);
        for(int s=0;s<4;++s){
            r.accumulate(V,r.multiply(selectors[a][s],cores[a][s].product));
            for(int i=0;i<3;++i){
                auto error=c.Boolean(r.multiply(selectors[a][s],
                    r.subtract(q[lists[a][i]],cores[a][s].inputs[i])));
                c.write(out,h,"branch_input_"+std::to_string(a)+"_"+std::to_string(s)+"_"+std::to_string(i),
                        error,t+2);input_errors[s].push_back(error);
            }
        }
        auto product_image=r.substitute(parents[a].product,phi);
        auto delta=c.Boolean(r.subtract(product_image,V));
        c.write(out,h,"parent_product_"+std::to_string(a),delta,h*(t+3));
        for(int i=0;i<3;++i){
            Cert cert=c.scale(delta,q[lists[a][i]]);
            for(int s=0;s<4;++s){
                c.plus(cert,c.scale(c.ax(companion_ids[a][s][i]),selectors[a][s]));
                c.plus(cert,c.scale(input_errors[s][i],cores[a][s].product));
            }
            source_cert("parent_companion_"+std::to_string(a)+"_"+std::to_string(i),
                        parents[a].companions[i],cert,h*(t+3)+2);
        }
        for(int u=0;u<h;++u)for(int i=0;i<3;++i){
            Cert cert;
            for(int s=0;s<4;++s){
                int id=cores[a][s].variables[u][i];const auto& chi=selectors[a][s];
                c.plus(cert,c.scale(c.ax(id),r.power(chi,2)));
                c.plus(cert,c.scale(c.Boolean(r.subtract(r.power(chi,2),chi)),x(id)));
            }
            int id=parents[a].variables[u][i];auto source=r.subtract(r.power(x(id),2),x(id));
            source_cert("parent_field_"+std::to_string(id),source,cert,2*T);
        }
    }
    need(source_images.size()==std::size_t(h==1?33:23),"source axiom inventory");
    auto canonical=[&](int bits){
        std::map<int,int> point;
        for(int id=0;id<retained_end;++id)point[id]=id<c.old?int((bits>>id)&1):0;
        for(const auto& family:cores)for(const auto& A:family)
            for(std::size_t i=0;i<A.inputs.size();++i)if(r.evaluate(A.inputs[i],point)){
                point[A.variables[0][i]]=1;break;
            }
        return point;
    };
    auto model=[&](const std::string& name,int bits,const std::map<int,int>& point,int omit,bool valid){
        out<<"{\"record\":\"model\",\"accuracy\":"<<h<<",\"name\":\""<<name<<"\",\"old_point\":"
           <<bits<<",\"assignment\":";assignment(out,point,retained_end);
        out<<",\"omitted_retained_axiom\":"<<omit<<",\"retained_values\":[";
        for(std::size_t i=0;i<c.axioms.size();++i){
            int v=r.evaluate(c.axioms[i],point);need(int(i)==omit || v==0,"retained model");
            if(i)out<<',';
            out<<v;
        }
        out<<"],\"source_image_values\":[";
        for(std::size_t i=0;i<source_images.size();++i){
            int v=r.evaluate(source_images[i],point);need(!valid || !v,"source model");
            if(i)out<<',';
            out<<v;
        }
        out<<"]}\n";
    };
    for(int bits=0;bits<32;++bits)model("canonical",bits,canonical(bits),-1,true);
    auto missing=canonical(4);
    for(const auto& row:cores[0][0].variables)for(int id:row)missing[id]=0;
    int omitted=companion_ids[0][0][1];
    need(r.evaluate(c.axioms[omitted],missing)==1,"missing companion is nonzero");
    auto missing_image=r.substitute(parents[0].companions[1],phi);
    need(r.evaluate(missing_image,missing)==1,"missing branch companion control");
    model("missing_branch_companion",4,missing,omitted,false);
    auto wrong=phi;auto point=canonical(3);
    for(int u=0;u<h;++u)for(int i=0;i<3;++i)
        wrong[parents[0].variables[u][i]]=x(cores[0][0].variables[u][i]);
    auto bad=r.substitute(parents[0].companions[0],wrong);
    need(r.evaluate(bad,point)==1,"wrong fixed-branch map must fail");
    need(r.evaluate(r.substitute(parents[0].companions[0],phi),point)==0,"correct branch map");
    out<<"{\"record\":\"wrong_branch_control\",\"accuracy\":"<<h<<",\"old_point\":3,"
         "\"assignment\":";assignment(out,point,retained_end);
    out<<",\"incorrect_companion_image\":";write_json(out,bad);out<<",\"value\":1}\n";
    need(rank({1,2,4,8})==4,"independent-pair coordinate control");
    auto extra=r.multiply(x(2),x(3));
    auto obstruction=domain_reduce(r,r.multiply(selectors[0][0],extra),std::vector<int>(c.old,2));
    need(!obstruction.remainder.empty(),"missing-coordinate error remains nonzero");
    auto obstruction_point=canonical(12);
    need(r.evaluate(obstruction.remainder,obstruction_point)==1,"missing-coordinate witness");
    out<<"{\"record\":\"insufficient_coordinates_control\",\"accuracy\":"<<h
       <<",\"extra_pair_masks\":[4,8],\"quotient_rank\":2,\"old_point\":12,"
         "\"selected_branch_input\":";write_json(out,extra);
    out<<",\"nonzero_selector_error\":";write_json(out,obstruction.remainder);
    out<<",\"scope\":\"the selected two coordinates do not make this added product affine\"}\n";
    need(c.count==(h==1?59:49),"certificate inventory");
    out<<"{\"record\":\"case_summary\",\"accuracy\":"<<h<<",\"source_images\":"<<source_images.size()
       <<",\"NS_certificates\":"<<c.count<<",\"canonical_models\":32,\"negative_models\":1,"
         "\"affine_cores\":8,\"passed\":true}\n";
    return c.count;
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");
        out<<"{\"record\":\"schema\",\"version\":1,\"polynomials\":\"[coefficient,[variable IDs with repetitions]]\","
             "\"scope\":\"binary complete affine-branch interfaces; local Boolean base, not PHP\"}\n";
        int count=run(out,1);count+=run(out,2);
        out<<"{\"record\":\"summary\",\"NS_certificates\":"<<count<<",\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<count<<" exact NS certificates, 64 canonical models, and branch controls passed.\n";
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
