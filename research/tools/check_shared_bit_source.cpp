// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Complete degree-preserving images of a two-level shared-bit ENS family.
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
    Ring r;
    std::vector<Polynomial> axioms;
    int count=0;
    explicit Context(int p):r(p,80){}
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
        std::vector<int> powers(4,2);auto red=domain_reduce(r,f,powers);
        verify_reduction(r,f,powers,red);need(red.remainder.empty(),"old Boolean remainder");
        Cert result;result.target=f;
        for(int i=0;i<4;++i)if(!red.coefficients[i].empty())result.cof[i]=red.coefficients[i];
        return result;
    }
    void write(std::ostream& out,const std::string& name,const Cert& cert,int budget,
               const Polynomial* source=nullptr){
        out<<"{\"record\":\"NS_certificate\",\"field\":"<<r.p<<",\"name\":\""<<name
           <<"\",\"target\":";write_json(out,cert.target);out<<",\"budget\":"<<budget;
        if(source){out<<",\"source_axiom\":";write_json(out,*source);out<<",\"original_degree\":"<<degree(*source);}
        int used=ns_witness::write_terms(out,r,axioms,cert.target,cert.cof,budget,name);
        if(source)need(used<=degree(*source),"original degree exceeded");
        out<<"}\n";++count;
    }
};
void assign(const Ring& r,const Block& A,std::map<int,int>& point){
    for(const auto& row:A.variables)for(int id:row)point[id]=0;
    for(std::size_t i=0;i<A.inputs.size();++i)
        if(r.evaluate(A.inputs[i],point)){point[A.variables[0][i]]=1;break;}
}
int run(std::ostream& out,int p,bool unit=false){
    Context c(p);auto& r=c.r;auto one=r.constant(1);
    auto x=[&](int id){return r.variable(id);};
    auto probe=x(0),chi=r.subtract(one,probe);int old=4,h=unit?1:2;
    std::vector<std::vector<int>> lists={{0,1,2},{1,2}};
    int target_end=old+h*(3+2),bottom_next=target_end;
    std::vector<Block> bottom;
    for(int i=0;i<3;++i)bottom.push_back(make_block(r,{probe,x(i+1)},h,bottom_next));
    std::vector<Block> parent,core;int parent_next=old,core_next=old;
    for(const auto& list:lists){
        std::vector<Polynomial> inputs,literals;
        for(int i:list){inputs.push_back(bottom[i].product);literals.push_back(r.subtract(one,x(i+1)));}
        parent.push_back(make_block(r,inputs,h,parent_next));
        core.push_back(make_block(r,literals,h,core_next));
    }
    need(parent_next==target_end && core_next==target_end,"parent/core coefficient alignment");
    for(int i=0;i<target_end;++i)c.add(r.subtract(r.power(x(i),i<old?2:p),x(i)));
    std::vector<std::vector<int>> companions;
    for(const auto& A:core){
        std::vector<int> ids;for(const auto& f:A.companions)ids.push_back(c.add(f));companions.push_back(ids);
    }
    std::map<int,Polynomial> phi;
    for(const auto& B:bottom)for(int u=0;u<h;++u)for(int i=0;i<2;++i)
        phi[B.variables[u][i]]=unit?(i==0?one:chi):r.constant(int(u==i));
    for(int i=0;i<3;++i)
        need(r.substitute(bottom[i].product,phi)==r.multiply(chi,r.subtract(one,x(i+1))),"bottom image");
    out<<"{\"record\":\"case\",\"field\":"<<p<<",\"accuracy\":"<<h<<",\"old_variables\":4"
         ",\"retained_variables\":"<<target_end<<",\"source_variables\":"<<bottom_next
       <<",\"retained_axioms\":";write_polynomials(out,c.axioms);
    out<<",\"bottom_blocks\":[";
    for(int i=0;i<3;++i){if(i)out<<',';write_block(out,bottom[i]);}
    out<<"],\"parent_blocks\":[";
    for(int i=0;i<2;++i){if(i)out<<',';write_block(out,parent[i]);}
    out<<"],\"affine_cores\":[";
    for(int i=0;i<2;++i){if(i)out<<',';write_block(out,core[i]);}
    out<<"],\"bottom_coefficient_images\":[";bool comma=false;
    for(const auto& [id,f]:phi){
        if(comma)out<<',';
        comma=true;out<<'['<<id<<',';write_json(out,f);out<<']';
    }
    out<<"],\"other_variables\":\"fixed; each affine core reuses its parent's coefficient IDs\","
         "\"scope\":\"two overlapping parents share actual bottom blocks; local old Boolean base, not PHP\"}\n";
    std::vector<Polynomial> source_images;
    auto source_cert=[&](const std::string& name,const Polynomial& source,const Cert& cert){
        auto image=r.substitute(source,phi);need(image==cert.target,"source image mismatch");
        c.write(out,name,cert,degree(source),&source);source_images.push_back(image);
    };
    for(int i=0;i<old;++i)source_cert("old_Boolean_"+std::to_string(i),c.axioms[i],c.ax(i));
    for(int b=0;b<3;++b){
        for(int i=0;i<2;++i){
            const auto& source=bottom[b].companions[i];
            source_cert("bottom_companion_"+std::to_string(b)+"_"+std::to_string(i),
                        source,c.Boolean(r.substitute(source,phi)));
        }
        for(const auto& row:bottom[b].variables)for(int id:row){
            auto source=r.subtract(r.power(x(id),p),x(id));
            source_cert("bottom_field_"+std::to_string(id),source,c.Boolean(r.substitute(source,phi)));
        }
    }
    std::vector<Polynomial> mapped_products,values;
    for(int a=0;a<2;++a){
        const auto& A=core[a];const auto& P=parent[a];
        auto mapped=r.substitute(P.product,phi);
        auto value=r.add(probe,r.multiply(chi,A.product));
        if(unit)need(mapped==value,"literal unit-accuracy parent value");
        mapped_products.push_back(mapped);values.push_back(value);
        auto delta=c.Boolean(r.subtract(mapped,value));
        c.write(out,"parent_product_difference_"+std::to_string(a),delta,3*h);
        auto prefix_error=r.subtract(one,value);
        for(std::size_t i=0;i<A.inputs.size();++i){
            auto g=r.multiply(chi,A.inputs[i]);
            need(r.substitute(P.inputs[i],phi)==g,"parent input image");
            need(degree(A.prefix[i])+2*h<=h*(2*h+1),"original-input prefix bound");
            r.accumulate(prefix_error,r.multiply(A.prefix[i],g),-1);
            Cert image=c.scale(delta,g);
            c.plus(image,c.scale(c.ax(companions[a][i]),chi));
            c.plus(image,c.scale(c.ax(0),r.multiply(A.inputs[i],r.subtract(A.product,one))));
            source_cert("parent_companion_"+std::to_string(a)+"_"+std::to_string(i),P.companions[i],image);
        }
        need(prefix_error.empty(),"exact source profile prefix");
        Cert abool;
        for(std::size_t i=0;i<A.inputs.size();++i)
            c.plus(abool,c.scale(c.ax(companions[a][i]),r.multiply(r.constant(-1),A.prefix[i])));
        need(abool.target==r.subtract(r.power(A.product,2),A.product),"affine product Booleanity");
        auto vbool=c.scale(abool,chi);
        c.plus(vbool,c.scale(c.ax(0),r.power(r.subtract(A.product,one),2)));
        need(vbool.target==r.subtract(r.power(value,2),value),"source value Booleanity");
        c.write(out,"source_value_Booleanity_"+std::to_string(a),vbool,2*h*(2*h+1));
        out<<"{\"record\":\"value_profile\",\"field\":"<<p<<",\"parent\":"<<a
           <<",\"value\":";write_json(out,value);
        out<<",\"prefix_coefficients\":";write_polynomials(out,A.prefix);
        out<<",\"input_degrees\":[";
        for(std::size_t i=0;i<A.inputs.size();++i){if(i)out<<',';out<<2*h;}
        out<<"],\"original_cost\":"<<h*(2*h+1)<<",\"prefix_residual\":[],\"selector_rank\":"
           <<A.inputs.size()<<"}\n";
        for(const auto& row:P.variables)for(int id:row){
            auto source=r.subtract(r.power(x(id),p),x(id));
            source_cert("parent_field_"+std::to_string(id),source,c.ax(id));
        }
    }
    need(source_images.size()==std::size_t(15+11*h),"complete source axiom inventory");
    auto model=[&](const std::string& name,const std::map<int,int>& point,int omit,bool source_ok){
        out<<"{\"record\":\"model\",\"field\":"<<p<<",\"name\":\""<<name<<"\",\"assignment\":[";
        for(int i=0;i<target_end;++i){if(i)out<<',';out<<point.at(i);}
        out<<"],\"omitted_retained_axiom\":"<<omit<<",\"retained_axiom_values\":[";
        for(std::size_t i=0;i<c.axioms.size();++i){
            int v=r.evaluate(c.axioms[i],point);need(int(i)==omit || v==0,"retained model");
            if(i)out<<',';
            out<<v;
        }
        out<<"],\"source_axiom_image_values\":[";
        for(std::size_t i=0;i<source_images.size();++i){
            int v=r.evaluate(source_images[i],point);need(!source_ok || !v,"mapped source model");
            if(i)out<<',';
            out<<v;
        }
        out<<"],\"mapped_parent_values\":[";
        for(int i=0;i<2;++i){if(i)out<<',';out<<r.evaluate(mapped_products[i],point);}
        out<<"],\"affine_core_values\":[";
        for(int i=0;i<2;++i){if(i)out<<',';out<<r.evaluate(core[i].product,point);}
        out<<"]}\n";
    };
    for(int bits=0;bits<16;++bits){
        std::map<int,int> point;for(int i=0;i<old;++i)point[i]=(bits>>i)&1;
        for(const auto& A:core)assign(r,A,point);
        model("old_Boolean_point_"+std::to_string(bits),point,-1,true);
        if(bits==1){
            for(int a=0;a<2;++a)
                need(r.evaluate(mapped_products[a],point)==1 && r.evaluate(core[a].product,point)==0,
                     "missing shared-bit branch control");
            out<<"{\"record\":\"wrong_branch_control\",\"field\":"<<p
               <<",\"old_point\":1,\"mapped_parent_values\":[1,1],\"incorrect_ungated_values\":[0,0]}\n";
        }
        if(unit && bits==3){
            auto incorrect=r.subtract(r.subtract(one,probe),x(1));
            need(r.evaluate(incorrect,point)==p-1,"incorrect scalar bottom map control");
            out<<"{\"record\":\"incorrect_unit_scalar_map\",\"field\":"<<p
               <<",\"old_point\":3,\"incorrect_product\":";write_json(out,incorrect);
            out<<",\"incorrect_companion_value\":"<<p-1<<",\"correct_product_value\":0}\n";
        }
    }
    if(p==3){
        std::map<int,int> point;for(int i=0;i<target_end;++i)point[i]=0;
        for(int i=1;i<old;++i)point[i]=1;
        point[old]=2;
        model("non_Boolean_parent_coefficient",point,-1,true);
    }
    std::map<int,int> missing;for(int i=0;i<target_end;++i)missing[i]=0;
    missing[2]=missing[3]=1;
    model("missing_affine_companion",missing,companions[0][0],false);
    need(r.evaluate(r.substitute(parent[0].companions[0],phi),missing)==1,"missing companion control");
    out<<"{\"record\":\"case_summary\",\"field\":"<<p<<",\"source_axiom_images\":"<<source_images.size()
       <<",\"NS_certificates\":"
       <<c.count<<",\"old_Boolean_models\":16,\"missing_companion_models\":1,\"passed\":true}\n";
    return c.count;
}
int main(int argc,char** argv){
    try{
        const bool unit=argc==4 && std::string(argv[1])=="--unit-accuracy";
        const int argument=unit?2:1;
        need(argc==argument+2 && std::string(argv[argument])=="--out",
             "usage: [--unit-accuracy] --out NEW_PATH");
        std::filesystem::path path=argv[argument+1];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");
        out<<"{\"record\":\"schema\",\"version\":1,\"polynomials\":\"[coefficient,[variable IDs with repetitions]]\","
             "\"scope\":\"complete original-degree images of two overlapping shared-bit parents\"}\n";
        int certificates=run(out,2,unit);certificates+=run(out,3,unit);
        out<<"{\"record\":\"summary\",\"NS_certificates\":"<<certificates<<",\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<certificates<<" exact NS certificates passed, covering every source axiom image and shared-parent controls.\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
