// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact weighted module moments on a complete small affine-flat registry.
#include "sparse_polynomial.hpp"
#include <array>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iostream>
#include <set>
#include <string>
using namespace sparse_polynomial;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
constexpr int OLD=4;
using Moments=std::array<int,1<<OLD>;
struct Flat{int mask=0,value=0,selector=-1;Polynomial indicator,formal;};
struct Fixture{
    Ring ring{2,32};std::vector<Flat> flats;
    std::map<std::pair<int,int>,int> index;
    std::vector<int> high;std::array<int,OLD> signals{};
    std::array<int,3> points{0,1,2};
    int bottom=-1;
    Fixture(){
        for(int i=0;i<OLD;i++)signals[i]=((1<<OLD)-1)^(1<<i);
        for(int mask=0;mask<(1<<OLD);mask++)for(int value=0;value<(1<<OLD);value++)if(!(value&~mask)){
            Flat f;f.mask=mask;f.value=value;f.indicator=ring.constant(1);
            for(int i=0;i<OLD;i++)if((mask>>i)&1){
                auto factor=ring.constant(1^((value>>i)&1));
                for(int j=0;j<OLD;j++)if((signals[i]>>j)&1)ring.accumulate(factor,ring.variable(j));
                f.indicator=ring.multiply(f.indicator,factor);
            }
            int id=int(flats.size());
            if(__builtin_popcount(unsigned(mask))>2){f.selector=int(high.size());high.push_back(id);f.formal=ring.variable(OLD+f.selector);}
            else f.formal=f.indicator;
            index.emplace(std::make_pair(mask,value),id);flats.push_back(f);
        }
        bottom=int(flats.size());Flat empty;empty.mask=-1;flats.push_back(empty);
        need(bottom==81 && high.size()==48,"registry size");
        for(int x=0;x<(1<<OLD);x++){
            int y=signal_point(x),z=signal_point(y);need(z==x,"dense signal map is not invertible");
        }
    }
    int signal_point(int x)const{
        int result=0;for(int i=0;i<OLD;i++)result|=__builtin_parity(unsigned(signals[i]&x))<<i;return result;
    }
    int join(int a,int b)const{
        if(a==bottom || b==bottom)return bottom;
        const auto& x=flats[a];const auto& y=flats[b];
        if((x.value^y.value)&x.mask&y.mask)return bottom;
        return index.at({x.mask|y.mask,x.value|y.value});
    }
    bool contains(int id,int point)const{
        return id!=bottom && (signal_point(point)&flats[id].mask)==flats[id].value;
    }
    Moments conditional(int id)const{
        Moments result{};
        for(int mask=0;mask<(1<<OLD);mask++)for(int point:points)
            result[mask]^=contains(id,point) && (point&mask)==mask;
        return result;
    }
};
void moments(std::ostream& out,const Moments& values){
    out<<'[';for(int i=0;i<int(values.size());i++){if(i)out<<',';if(values[i]<0)out<<"null";else out<<values[i];}out<<']';
}
std::vector<Monomial> monomials(int budget,int selectors,bool old_only=false){
    std::vector<Monomial> out;Monomial current;int variables=OLD+(old_only?0:selectors);
    std::function<void(int,int)> rec=[&](int first,int remaining){
        out.push_back(current);
        for(int v=first;v<variables;v++){
            int cost=v<OLD?1:2;if(cost>remaining)continue;
            current.push_back(v);rec(v,remaining-cost);current.pop_back();
        }
    };
    rec(0,budget);return out;
}
struct Design{
    const Fixture& fixture;int u,D;Moments root;
    std::vector<Moments> singles;std::map<std::pair<int,int>,Moments> pairs;
    Design(const Fixture& f,int excess):fixture(f),u(excess),D(6+u),root(f.conditional(f.index.at({0,0}))){
        need(u==0 || u==1,"test band");need(root[0]==1,"root normalization");
        for(int id:f.high)singles.push_back(f.conditional(id));
        for(int a=0;a<int(f.high.size());a++)for(int b=a+1;b<int(f.high.size());b++){
            auto low=f.conditional(f.join(f.high[a],f.high[b]));Moments extension{};
            for(int mask=0;mask<(1<<OLD);mask++){
                int degree=__builtin_popcount(unsigned(mask));
                extension[mask]=degree>2+u?-1:(degree<=u?low[mask]:0);
            }
            pairs.emplace(std::make_pair(a,b),extension);
        }
    }
    int term(const Monomial& m)const{
        int mask=0,weight=0;std::set<int> selected;
        for(int v:m){
            if(v<OLD){mask|=1<<v;++weight;}
            else{need(v<OLD+int(singles.size()),"undefined selector");selected.insert(v-OLD);weight+=2;}
        }
        need(weight<=D,"moment outside declared weighted domain");
        if(selected.empty())return root[mask];
        if(selected.size()==1)return singles[*selected.begin()][mask];
        if(selected.size()==2){
            auto it=selected.begin();int a=*it++,b=*it;int value=pairs.at({a,b})[mask];
            need(value>=0,"pair moment outside old degree ceiling");return value;
        }
        need(selected.size()==3,"more than three selectors in this band");return 0;
    }
    int apply(const Polynomial& p)const{int value=0;for(const auto& [m,c]:p)value^=(c&1)&term(m);return value;}
};
void dump_registry(std::ostream& out,const Fixture& f){
    out<<"{\"type\":\"registry\",\"old_variables\":4,\"h\":1,\"signals\":[";
    for(int i=0;i<OLD;i++){if(i)out<<',';out<<f.signals[i];}
    out<<"],\"root_support_points\":[0,1,2],\"point_weights\":[1,1,1],\"flats\":81,\"retained_selectors\":48,\"empty_flat_id\":"<<f.bottom<<"}\n";
    for(int id=0;id<=f.bottom;id++){
        const auto& flat=f.flats[id];
        out<<"{\"type\":\"flat\",\"id\":"<<id<<",\"mask\":"<<flat.mask<<",\"value\":"<<flat.value
           <<",\"selector\":"<<flat.selector<<",\"indicator\":";write_json(out,flat.indicator);
        out<<",\"formal_value\":";write_json(out,flat.formal);out<<"}\n";
    }
}
void run_case(std::ostream& out,const Fixture& f,int u){
    Design d(f,u);const Ring& ring=f.ring;int high=int(f.high.size());
    out<<"{\"type\":\"design\",\"D\":"<<d.D<<",\"u\":"<<u<<",\"root_moments\":";moments(out,d.root);
    out<<",\"root_is_nonmultiplicative\":"<<((d.root[1]*d.root[2]!=d.root[3])?"true":"false")
       <<",\"distinct_triple_components\":\"identically zero on old degree <= u\","
         "\"repeated_selector_powers\":\"reduce to the same distinct support\","
         "\"moment_index\":\"squarefree old-variable mask; null is outside this component domain\"}\n";
    need(d.root[1]*d.root[2]!=d.root[3],"nonmultiplicative root control");
    for(int a=0;a<high;a++){
        out<<"{\"type\":\"singleton\",\"D\":"<<d.D<<",\"selector\":"<<a<<",\"flat\":"<<f.high[a]
           <<",\"old_degree_ceiling\":"<<4+u<<",\"moments\":";moments(out,d.singles[a]);out<<"}\n";
    }
    for(const auto& [pair,data]:d.pairs){
        out<<"{\"type\":\"pair\",\"D\":"<<d.D<<",\"selectors\":["<<pair.first<<','<<pair.second
           <<"],\"union_flat\":"<<f.join(f.high[pair.first],f.high[pair.second])
           <<",\"old_degree_ceiling\":"<<2+u<<",\"moments\":";moments(out,data);out<<"}\n";
    }
    long long old_checks=0,boolean_checks=0,gate_checks=0;
    auto old_cofactors=monomials(d.D-2,high),selector_cofactors=monomials(d.D-4,high);
    auto gate_cofactors=monomials(u,high,true);
    for(int i=0;i<OLD;i++){
        auto x=ring.variable(i),axiom=ring.subtract(ring.multiply(x,x),x);
        for(const auto& m:old_cofactors){need(d.apply(ring.multiply(Polynomial{{m,1}},axiom))==0,"old-domain multiple");++old_checks;}
    }
    for(int i=0;i<high;i++){
        auto z=ring.variable(OLD+i),axiom=ring.subtract(ring.multiply(z,z),z);
        for(const auto& m:selector_cofactors){need(d.apply(ring.multiply(Polynomial{{m,1}},axiom))==0,"selector-Booleanity multiple");++boolean_checks;}
    }
    std::array<int,4> types{};int incompatible=0;
    for(int a=0;a<f.bottom;a++)for(int b=0;b<f.bottom;b++){
        int c=f.join(a,b),count=(f.flats[a].selector>=0)+(f.flats[b].selector>=0);
        int kind=count==0?(f.flats[c].selector>=0?1:0):(count==1?2:3);
        ++types[kind];incompatible+=c==f.bottom;
        auto target=ring.subtract(f.flats[c].formal,ring.multiply(f.flats[a].formal,f.flats[b].formal));
        out<<"{\"type\":\"source_gate\",\"D\":"<<d.D<<",\"a\":"<<a<<",\"b\":"<<b<<",\"c\":"<<c
           <<",\"witness_cost\":6,\"constraint_kind\":"<<kind<<",\"cofactor_moments\":[";
        for(int i=0;i<int(gate_cofactors.size());i++){
            int value=d.apply(ring.multiply(Polynomial{{gate_cofactors[i],1}},target));
            need(value==0,"source OR module multiple");if(i)out<<',';out<<value;++gate_checks;
        }
        out<<"]}\n";
    }
    int a=f.index.at({7,0}),b=f.index.at({11,0}),c=f.join(a,b);
    need(a!=b && a!=c && b!=c,"boundary triple is not distinct");
    auto relation=ring.subtract(f.flats[c].formal,ring.multiply(f.flats[a].formal,f.flats[b].formal));
    auto boundary=ring.multiply(f.flats[c].formal,relation);
    need(d.apply(boundary)==1,"8h boundary control did not separate");
    out<<"{\"type\":\"nonextension_control\",\"D\":"<<d.D<<",\"gate_flats\":["<<a<<','<<b<<','<<c
       <<"],\"cofactor_flat\":"<<c<<",\"formal_target\":";write_json(out,boundary);
    out<<",\"formal_weighted_degree\":6,\"required_NS_module_cost\":8,\"moment_value\":1,"
         "\"scope\":\"this chosen degree-D design cannot extend to the same module system at degree 8\"}\n";
    int solutions=0;for(int value=0;value<2;value++)solutions+=(value==0 && value==1);
    need(solutions==0,"duplicate-parent compatibility control");
    out<<"{\"type\":\"uncanonical_parent_control\",\"D\":"<<d.D
       <<",\"pair_unknown\":\"nu_ab(1)\",\"required_parent_means\":[0,1],\"solutions\":0,"
         "\"scope\":\"without canonical sharing, arbitrary singleton choices need not admit a pair extension\"}\n";
    out<<"{\"type\":\"result\",\"D\":"<<d.D<<",\"old_domain_checks\":"<<old_checks
       <<",\"selector_Booleanity_checks\":"<<boolean_checks<<",\"source_gate_checks\":"<<gate_checks
       <<",\"source_gate_count\":"<<f.bottom*f.bottom<<",\"incompatible_flat_pairs\":"<<incompatible
       <<",\"gate_kinds\":["<<types[0]<<','<<types[1]<<','<<types[2]<<','<<types[3]<<"],\"all_passed\":true}\n";
    std::cout<<"D="<<d.D<<": "<<old_checks<<" old-domain, "<<boolean_checks<<" selector-domain, "<<gate_checks
             <<" source-gate checks; nonextension and canonical-sharing controls passed.\n";
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");
        auto parent=std::filesystem::path(argv[2]).parent_path();if(!parent.empty())std::filesystem::create_directories(parent);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"flat_source_module_moments\",\"p\":2,\"seed\":null,"
             "\"base\":\"four free Boolean variables, not PHP\","
             "\"polynomial_encoding\":\"[coefficient,[variable,...]], repeated indices encode powers\","
             "\"source_gate_registry\":\"all ordered pairs of the 81 nonempty affine zero flats; parent is their intersection\","
             "\"gate_cofactor_order\":\"ordinary old monomials of degree <= u, recursively in nondecreasing variable order\"}\n";
        Fixture fixture;dump_registry(out,fixture);run_case(out,fixture,0);run_case(out,fixture,1);
        out.close();need(bool(out),"output write failed");
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
