// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Three-level direct row-profile maps and complete original-degree NS witnesses.
#include "ens_symbolic.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace ens_symbolic;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
struct Term { std::string name; Polynomial cofactor,axiom; };
struct RowIdeal {
    const Ring& ring;
    std::vector<Term> templates;
    RowIdeal(const Ring& r):ring(r) {
        auto one=ring.constant(1);
        for(int v=0;v<6;++v) {
            auto x=ring.variable(v);
            templates.push_back({"Boolean_"+std::to_string(v),{},ring.subtract(ring.multiply(x,x),x)});
        }
        for(int i=0;i<3;++i)
            templates.push_back({"same_row_"+std::to_string(i),{},
                ring.multiply(ring.variable(2*i),ring.variable(2*i+1))});
        for(int i=0;i<3;++i)
            templates.push_back({"row_"+std::to_string(i),{},
                ring.subtract(ring.add(ring.variable(2*i),ring.variable(2*i+1)),one)});
    }
    std::vector<Term> prove(const Polynomial& target) const {
        auto proof=templates;
        Polynomial normal;
        for(const auto& [source,c]:target) {
            Monomial m=source; bool vanished=false;
            for(int v:m)need(v>=0 && v<6,"unremoved coefficient");
            while(true) {
                auto repeated=std::adjacent_find(m.begin(),m.end());
                if(repeated!=m.end()) {
                    int v=*repeated; Monomial q=m;
                    for(int k=0;k<2;++k)q.erase(std::find(q.begin(),q.end(),v));
                    ring.accumulate(proof[v].cofactor,Polynomial{{q,c}});
                    m.erase(std::find(m.begin(),m.end(),v));
                    continue;
                }
                int a=-1,b=-1;
                for(std::size_t j=1;j<m.size();++j)
                    if(m[j-1]/2==m[j]/2){a=m[j-1];b=m[j];break;}
                if(a>=0) {
                    Monomial q=m;
                    q.erase(std::find(q.begin(),q.end(),a));
                    q.erase(std::find(q.begin(),q.end(),b));
                    ring.accumulate(proof[6+a/2].cofactor,Polynomial{{q,c}});
                    vanished=true;
                }
                break;
            }
            if(!vanished)ring.accumulate(normal,Polynomial{{m,c}});
        }
        for(int row=0;row<3;++row) {
            Polynomial projected;
            for(const auto& [m,c]:normal) {
                auto pivot=std::find(m.begin(),m.end(),2*row);
                if(pivot==m.end()) {ring.accumulate(projected,Polynomial{{m,c}});continue;}
                Monomial q=m; q.erase(std::find(q.begin(),q.end(),2*row));
                ring.accumulate(proof[9+row].cofactor,Polynomial{{q,c}});
                ring.accumulate(projected,Polynomial{{q,c}});
                auto image=ring.multiply(Polynomial{{q,1}},ring.variable(2*row+1));
                ring.accumulate(projected,image,-c);
            }
            normal=std::move(projected);
        }
        need(normal.empty(),"nonzero row-state normal form");
        return proof;
    }
};
int certificates=0;
void certificate(std::ostream& out,const Ring& ring,const RowIdeal& ideal,
                 const std::string& name,const Polynomial& target,int original_degree,int T) {
    auto proof=ideal.prove(target); Polynomial sum; int used=0,terms=0;
    for(const auto& term:proof)if(!term.cofactor.empty()) {
        auto product=ring.multiply(term.cofactor,term.axiom);
        ring.accumulate(sum,product);used=std::max(used,degree(product));++terms;
    }
    need(sum==target && used<=degree(target) && degree(target)<=T*original_degree,
         "ordinary NS witness "+name);
    out<<"{\"type\":\"NS_certificate\",\"name\":\""<<name<<"\",\"p\":"<<ring.p
       <<",\"original_degree\":"<<original_degree<<",\"map_degree\":"<<T
       <<",\"image_degree\":"<<degree(target)<<",\"witness_degree\":"<<used
       <<",\"target\":";write_json(out,target);out<<",\"terms\":[";
    bool comma=false;
    for(const auto& term:proof)if(!term.cofactor.empty()) {
        if(comma)out<<',';
        comma=true;
        out<<"{\"name\":\""<<term.name<<"\",\"cofactor\":";write_json(out,term.cofactor);
        out<<",\"axiom\":";write_json(out,term.axiom);out<<'}';
    }
    out<<"]}\n";++certificates;
    std::cout<<name<<": "<<terms<<" terms, image/witness "<<degree(target)<<'/'<<used
             <<", original "<<original_degree<<", bound "<<T*original_degree<<'\n';
}
void suite(std::ostream& out,int p) {
    Ring ring(p,64); RowIdeal ideal(ring); auto one=ring.constant(1);
    int fresh=6,amplitude=p==2?1:2;
    auto scaled=ring.variable(1);for(auto& term:scaled)term.second=amplitude;
    std::vector<Block> blocks;
    blocks.push_back(make_block(ring,{scaled,ring.variable(3)},1,fresh));
    auto PA=blocks[0].product;
    blocks.push_back(make_block(ring,{
        ring.multiply(PA,ring.variable(5)),
        ring.multiply(ring.subtract(one,PA),ring.variable(1))},1,fresh));
    auto PB=blocks[1].product;
    blocks.push_back(make_block(ring,{
        ring.multiply(PB,ring.variable(3)),
        ring.multiply(PA,ring.variable(5))},1,fresh));
    std::vector<std::vector<std::vector<int>>> gamma(3,std::vector<std::vector<int>>(8));
    std::map<int,std::vector<int>> profiles;
    for(const auto& block:blocks)for(const auto& row:block.variables)
        for(int v:row)profiles[v]=std::vector<int>(8);
    for(int state=0;state<8;++state) {
        std::map<int,int> point;
        for(int row=0;row<3;++row)for(int j=0;j<2;++j)
            point[2*row+j]=j==((state>>row)&1);
        std::vector<int> products;
        for(int a=0;a<3;++a) {
            bool found=false;
            for(const auto& g:blocks[a].inputs)gamma[a][state].push_back(ring.evaluate(g,point));
            for(std::size_t j=0;j<blocks[a].inputs.size();++j) {
                int value=gamma[a][state][j],coefficient=0;
                if(value && !found) {
                    for(int c=1;c<p;++c)if(ring.residue(c*value)==1){coefficient=c;break;}
                    need(coefficient!=0,"inverse unavailable");found=true;
                }
                int v=blocks[a].variables[0][j];
                profiles[v][state]=coefficient;point[v]=coefficient;
            }
            int product=ring.evaluate(blocks[a].product,point);
            need(product==int(!found),"first-success product");
            for(const auto& E:blocks[a].companions)
                need(ring.evaluate(E,point)==0,"semantic companion");
            products.push_back(product);
        }
        out<<"{\"type\":\"state\",\"p\":"<<p<<",\"labels_mask\":"<<state<<",\"input_values\":[";
        for(int a=0;a<3;++a) {
            if(a)out<<',';
            out<<'['<<gamma[a][state][0]<<','<<gamma[a][state][1]<<']';
        }
        out<<"],\"products\":["<<products[0]<<','<<products[1]<<','<<products[2]<<"]}\n";
    }
    std::map<int,Polynomial> images;std::vector<int> supports;int T=1;
    for(int a=0;a<3;++a) {
        int support=0;
        for(int row=0;row<3;++row)
            for(int state=0;state<8;++state)
                if(gamma[a][state]!=gamma[a][state^(1<<row)])support|=1<<row;
        supports.push_back(support);int width=__builtin_popcount(unsigned(support));
        T=std::max(T,width);
        bool zero_tuple=false;
        for(int state=0;state<8;++state)
            if(gamma[a][state][0]==0 && gamma[a][state][1]==0)zero_tuple=true;
        need(zero_tuple,"constant nonzero tuple control");
        for(int j=0;j<2;++j) {
            bool nonzero=false;
            for(int state=0;state<8;++state)nonzero|=gamma[a][state][j]!=0;
            need(nonzero,"vacuous input");
            int v=blocks[a].variables[0][j];
            for(int state=0;state<8;++state) {
                need(profiles[v][state]==profiles[v][state&support],"profile support");
                if(state&~support)continue;
                Monomial monomial;
                for(int row=0;row<3;++row)if((support>>row)&1)
                    monomial.push_back(2*row+((state>>row)&1));
                ring.accumulate(images[v],Polynomial{{monomial,profiles[v][state]}});
            }
            need(degree(images[v])<=width,"interpolation degree");
        }
    }
    need(supports==std::vector<int>({3,7,7}) && T==3,"fixture support");
    out<<"{\"type\":\"fixture\",\"p\":"<<p<<",\"row_count\":3,\"labels_per_row\":2,"
           "\"tuple_support_masks\":[3,7,7],\"global_map_degree\":3,"
           "\"product_of_level_support_bounds\":18,\"blocks\":[";
    for(int a=0;a<3;++a){if(a)out<<',';write_block(out,blocks[a]);}
    out<<"],\"coefficient_images\":[";
    bool comma=false;
    for(const auto& [v,image]:images) {
        if(comma)out<<',';
        comma=true;
        out<<'['<<v<<',';write_json(out,image);out<<']';
        for(int state=0;state<8;++state) {
            std::map<int,int> point;
            for(int row=0;row<3;++row)for(int j=0;j<2;++j)
                point[2*row+j]=j==((state>>row)&1);
            need(ring.evaluate(image,point)==profiles[v][state],"interpolated value");
        }
    }
    out<<"]}\n";
    for(int a=0;a<3;++a)for(int j=0;j<2;++j) {
        auto E=blocks[a].companions[j];
        certificate(out,ring,ideal,"p"+std::to_string(p)+"/block"+std::to_string(a)+"/companion"+std::to_string(j),
                    ring.substitute(E,images),degree(E),T);
    }
    for(const auto& [v,image]:images)
        certificate(out,ring,ideal,"p"+std::to_string(p)+"/field"+std::to_string(v),
                    ring.subtract(ring.power(image,p),image),p,T);
    for(int row=0;row<3;++row)
        certificate(out,ring,ideal,"p"+std::to_string(p)+"/affine_row"+std::to_string(row),
                    ideal.templates[9+row].axiom,1,1);
    std::map<int,int> omitted={{0,0},{1,1},{2,0},{3,0},{4,1},{5,0}};
    for(int j=0;j<9;++j)need(ring.evaluate(ideal.templates[j].axiom,omitted)==0,"control domain");
    auto witness=ring.substitute(blocks[0].companions[0],images);
    need(ring.evaluate(witness,omitted)==amplitude,"omitted-row control");
    out<<"{\"type\":\"missing_row_control\",\"p\":"<<p
       <<",\"old_values\":[0,1,0,0,1,0],\"satisfies_Booleanity_and_row_exclusions\":true,"
         "\"violated_row\":1,\"first_companion_image_value\":"<<amplitude<<"}\n";
    if(p==3) {
        int variable=blocks[0].variables[0][0];
        std::map<int,int> point={{0,0},{1,1},{2,1},{3,0},{4,1},{5,0}};
        int value=ring.evaluate(images[variable],point);
        need(value==2 && ring.residue(value*value-value)==2,"odd coefficient control");
        out<<"{\"type\":\"nonBoolean_coefficient_control\",\"p\":3,\"coefficient\":"
           <<variable<<",\"old_values\":[0,1,1,0,1,0],\"value\":2,"
             "\"Boolean_equation_value\":2,\"field_equation_value\":0}\n";
    }
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"refusing existing output");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot create output");
        out<<"{\"type\":\"schema\",\"version\":1,\"scope\":\"satisfiable three-row functional domain, not full PHP\","
               "\"polynomials\":\"coefficient and sorted ordinary variable-list pairs\","
               "\"randomness\":\"none\"}\n";
        suite(out,2);suite(out,3);need(certificates==30,"certificate count");
        out<<"{\"type\":\"summary\",\"fixtures\":2,\"NS_certificates\":30,\"semantic_states\":16,"
               "\"missing_row_controls\":2,\"nonBoolean_coefficient_controls\":1,\"passed\":true}\n";
        out.close();need(bool(out),"write failed");
        std::cout<<"Passed 30 complete NS certificates, 16 semantic states, and three controls.\n";
    }catch(const std::exception& error){std::cerr<<"ERROR: "<<error.what()<<'\n';return 1;}
}
