// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Source-shaped row-local selectors, canonical remaining inputs, and NS budgets.
#include "ens_symbolic.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace ens_symbolic;
void need(bool value,const std::string& why){if(!value)throw std::runtime_error(why);}
using Proof=std::vector<Polynomial>;
struct Axiom {std::string name;Polynomial value;};
struct LocalBase {
    const Ring& ring;
    std::vector<Axiom> axioms;
    std::map<std::pair<int,int>,int> exclusions;
    explicit LocalBase(const Ring& r):ring(r) {
        auto one=ring.constant(1);
        for(int v=100;v<108;++v) {
            auto x=ring.variable(v);
            axioms.push_back({"Boolean_"+std::to_string(v),ring.subtract(ring.multiply(x,x),x)});
        }
        for(int row=0;row<2;++row)for(int j=0;j<4;++j)for(int k=j+1;k<4;++k) {
            int a=100+4*row+j,b=100+4*row+k;
            exclusions[{a,b}]=int(axioms.size());
            axioms.push_back({"same_row_"+std::to_string(a)+"_"+std::to_string(b),
                ring.multiply(ring.variable(a),ring.variable(b))});
        }
        for(int row=0;row<2;++row) {
            Polynomial rho;
            for(int j=0;j<4;++j)ring.accumulate(rho,ring.variable(100+4*row+j));
            axioms.push_back({"row_"+std::to_string(row),ring.subtract(rho,one)});
        }
        for(int j=0;j<4;++j)
            axioms.push_back({"column_"+std::to_string(j),
                ring.multiply(ring.variable(100+j),ring.variable(104+j))});
        need(axioms.size()==26,"base indexing");
    }
    Proof zero() const{return Proof(axioms.size());}
    Proof row_proof(const Polynomial& target) const {
        Proof proof=zero();Polynomial normal;
        for(const auto& [source,c]:target) {
            Monomial m=source;bool vanished=false;
            for(int v:m)need(v>=100 && v<108,"row proof has a nonold variable");
            while(true) {
                auto repeated=std::adjacent_find(m.begin(),m.end());
                if(repeated!=m.end()) {
                    int v=*repeated;Monomial q=m;
                    for(int k=0;k<2;++k)q.erase(std::find(q.begin(),q.end(),v));
                    ring.accumulate(proof[v-100],Polynomial{{q,c}});
                    m.erase(std::find(m.begin(),m.end(),v));continue;
                }
                int a=-1,b=-1;
                for(std::size_t j=1;j<m.size();++j)
                    if((m[j-1]-100)/4==(m[j]-100)/4){a=m[j-1];b=m[j];break;}
                if(a>=0) {
                    Monomial q=m;q.erase(std::find(q.begin(),q.end(),a));
                    q.erase(std::find(q.begin(),q.end(),b));
                    ring.accumulate(proof[exclusions.at({a,b})],Polynomial{{q,c}});
                    vanished=true;
                }
                break;
            }
            if(!vanished)ring.accumulate(normal,Polynomial{{m,c}});
        }
        for(int row=0;row<2;++row) {
            Polynomial projected;int pivot=100+4*row;
            for(const auto& [m,c]:normal) {
                if(std::find(m.begin(),m.end(),pivot)==m.end()) {
                    ring.accumulate(projected,Polynomial{{m,c}});continue;
                }
                Monomial q=m;q.erase(std::find(q.begin(),q.end(),pivot));
                ring.accumulate(proof[20+row],Polynomial{{q,c}});
                ring.accumulate(projected,Polynomial{{q,c}});
                for(int j=1;j<4;++j)
                    ring.accumulate(projected,ring.multiply(Polynomial{{q,1}},ring.variable(pivot+j)),-c);
            }
            normal=std::move(projected);
        }
        need(normal.empty(),"nonzero row-state normal form");return proof;
    }
    void add(Proof& target,const Proof& source,const Polynomial& multiplier,int scalar=1) const {
        need(target.size()==source.size(),"proof length");
        for(std::size_t i=0;i<source.size();++i)
            if(!source[i].empty())
                ring.accumulate(target[i],ring.multiply(source[i],multiplier),scalar);
    }
};
int certificates=0;
void emit(std::ostream& out,const Ring& ring,const LocalBase& base,const std::string& name,
          const Polynomial& target,const Proof& proof,int bound) {
    Polynomial sum;int used=0,count=0;
    for(std::size_t i=0;i<proof.size();++i)if(!proof[i].empty()) {
        auto term=ring.multiply(proof[i],base.axioms[i].value);
        ring.accumulate(sum,term);used=std::max(used,degree(term));++count;
    }
    need(sum==target && used<=bound,"certificate "+name);
    out<<"{\"type\":\"NS_certificate\",\"name\":\""<<name<<"\",\"target\":";write_json(out,target);
    out<<",\"image_degree\":"<<degree(target)<<",\"witness_degree\":"<<used
       <<",\"original_budget\":"<<bound<<",\"terms\":[";
    bool comma=false;
    for(std::size_t i=0;i<proof.size();++i)if(!proof[i].empty()) {
        if(comma)out<<',';
        comma=true;out<<"{\"name\":\""<<base.axioms[i].name<<"\",\"cofactor\":";
        write_json(out,proof[i]);out<<",\"axiom\":";write_json(out,base.axioms[i].value);out<<'}';
    }
    out<<"]}\n";++certificates;
    std::cout<<name<<": "<<count<<" terms, witness "<<used<<", original budget "<<bound<<'\n';
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"refusing existing output");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot create output");
        Ring ring(2,64);auto one=ring.constant(1);int fresh=4;
        std::vector<Block> blocks;
        blocks.push_back(make_block(ring,{ring.variable(0),ring.variable(1)},1,fresh));
        blocks.push_back(make_block(ring,{ring.variable(2),ring.variable(3)},1,fresh));
        blocks.push_back(make_block(ring,{ring.add(blocks[0].product,ring.variable(0)),
            ring.subtract(one,ring.variable(1))},1,fresh));
        blocks.push_back(make_block(ring,{ring.add(blocks[1].product,ring.variable(2)),
            ring.subtract(one,ring.variable(3))},1,fresh));
        auto equality=ring.multiply(ring.add(one,ring.add(ring.variable(0),ring.variable(2))),
                                   ring.add(one,ring.add(ring.variable(1),ring.variable(3))));
        blocks.push_back(make_block(ring,{
            ring.add(ring.add(blocks[2].product,blocks[1].product),equality),
            ring.add(blocks[3].product,ring.variable(0))},1,fresh));
        std::map<int,std::vector<int>> profiles;
        for(int a=0;a<4;++a)for(int v:blocks[a].variables[0])
            profiles[v]=std::vector<int>(16);
        std::vector<std::vector<int>> product_values(4,std::vector<int>(16));
        out<<"{\"type\":\"schema\",\"version\":1,\"p\":2,\"scope\":\"selector-linear source fixture on two functional four-label rows; not a full PHP refutation\","
               "\"original_bit_ids\":[0,1,2,3],\"target_incidence_ids\":[100,101,102,103,104,105,106,107],"
               "\"randomness\":\"none\"}\n";
        for(int state=0;state<16;++state) {
            std::map<int,int> point;
            for(int bit=0;bit<4;++bit)point[bit]=(state>>bit)&1;
            out<<"{\"type\":\"state\",\"labels\":["<<(state&3)<<','<<(state>>2)<<"],\"local_products\":[";
            for(int a=0;a<4;++a) {
                bool found=false;
                for(int j=0;j<2;++j) {
                    int g=ring.evaluate(blocks[a].inputs[j],point);
                    int w=g && !found;found=found || g;
                    int v=blocks[a].variables[0][j];profiles[v][state]=w;point[v]=w;
                }
                int P=ring.evaluate(blocks[a].product,point);need(P==int(!found),"product state");
                product_values[a][state]=P;
                for(const auto& E:blocks[a].companions)need(ring.evaluate(E,point)==0,"companion state");
                if(a)out<<',';
                out<<P;
            }
            out<<"]}\n";
        }
        std::map<int,Polynomial> sigma;
        for(int row=0;row<2;++row)for(int bit=0;bit<2;++bit) {
            Polynomial image;
            for(int z=0;z<4;++z)if((z>>bit)&1)ring.accumulate(image,ring.variable(100+4*row+z));
            sigma[2*row+bit]=image;
        }
        std::vector<Polynomial> values;
        for(int a=0;a<4;++a) {
            int row=a%2;
            Polynomial value;
            for(int z=0;z<4;++z) {
                int state=z<<(2*row);
                ring.accumulate(value,ring.variable(100+4*row+z),product_values[a][state]);
            }
            values.push_back(value);
            for(int v:blocks[a].variables[0]) {
                Polynomial image;
                for(int z=0;z<4;++z)
                    ring.accumulate(image,ring.variable(100+4*row+z),profiles[v][z<<(2*row)]);
                sigma[v]=image;need(degree(image)<=1,"nonaffine coefficient");
                for(int state=0;state<16;++state) {
                    int local=((state>>(2*row))&3)<<(2*row);
                    need(profiles[v][state]==profiles[v][local],"nonlocal coefficient profile");
                }
            }
        }
        need(values[0]==ring.variable(100) && values[1]==ring.variable(104) &&
             values[2]==ring.variable(102) && values[3]==ring.variable(106),"canonical labels");
        std::vector<Polynomial> G={ring.add(values[2],values[1]),
                                  ring.add(values[3],sigma[0])};
        Block canonical=blocks[4];canonical.inputs=G;canonical.product=one;canonical.companions.clear();
        for(int j=0;j<2;++j) {
            int v=canonical.variables[0][j];
            canonical.prefix[j]=ring.variable(v);
            ring.accumulate(canonical.product,ring.multiply(ring.variable(v),G[j]),-1);
        }
        for(const auto& g:G)canonical.companions.push_back(ring.multiply(g,canonical.product));
        LocalBase base(ring);
        for(int j=0;j<2;++j)base.axioms.push_back({"remaining_companion_"+std::to_string(j),canonical.companions[j]});
        for(int j=0;j<2;++j) {
            auto r=ring.variable(canonical.variables[0][j]);
            base.axioms.push_back({"remaining_field_"+std::to_string(j),ring.subtract(ring.multiply(r,r),r)});
        }
        out<<"{\"type\":\"fixture\",\"accuracy\":1,\"local_rows\":[0,1,0,1],\"blocks\":[";
        for(std::size_t a=0;a<blocks.size();++a){if(a)out<<',';write_block(out,blocks[a]);}
        out<<"],\"global_affine_map\":[";
        bool comma=false;for(const auto& [v,image]:sigma) {
            if(comma)out<<',';
            comma=true;
            out<<'['<<v<<',';write_json(out,image);out<<']';
        }
        out<<"],\"canonical_local_values\":";write_polynomials(out,values);
        out<<",\"canonical_remaining_block\":";write_block(out,canonical);out<<"}\n";
        std::vector<Proof> comparison;
        for(int a=0;a<4;++a) {
            auto target=ring.subtract(ring.substitute(blocks[a].product,sigma),values[a]);
            comparison.push_back(base.row_proof(target));
            emit(out,ring,base,"selector"+std::to_string(a),target,comparison.back(),degree(blocks[a].product));
            for(int j=0;j<2;++j) {
                auto image=ring.substitute(blocks[a].companions[j],sigma);
                emit(out,ring,base,"local_companion"+std::to_string(a)+"_"+std::to_string(j),
                     image,base.row_proof(image),degree(blocks[a].companions[j]));
            }
            for(int v:blocks[a].variables[0]) {
                auto image=sigma[v],field=ring.subtract(ring.multiply(image,image),image);
                emit(out,ring,base,"local_field"+std::to_string(v),field,base.row_proof(field),2);
            }
        }
        for(int bit=0;bit<4;++bit) {
            auto b=sigma[bit],image=ring.subtract(ring.multiply(b,b),b);
            emit(out,ring,base,"bit_field"+std::to_string(bit),image,base.row_proof(image),2);
        }
        auto equality_image=ring.substitute(equality,sigma);Polynomial diagonal;
        for(int j=22;j<26;++j)ring.accumulate(diagonal,base.axioms[j].value);
        auto equality_proof=base.row_proof(ring.subtract(equality_image,diagonal));
        for(int j=22;j<26;++j)ring.accumulate(equality_proof[j],one);
        emit(out,ring,base,"old_equality",equality_image,equality_proof,2);
        auto delta0=base.zero();base.add(delta0,comparison[2],one);
        base.add(delta0,comparison[1],one);base.add(delta0,equality_proof,one);
        std::vector<Proof> delta={delta0,comparison[3]};
        auto actual_product=ring.substitute(blocks[4].product,sigma);
        std::vector<Proof> parent_proofs;
        for(int i=0;i<2;++i) {
            auto proof=base.zero();proof[26+i]=one;
            base.add(proof,delta[i],actual_product);
            for(int j=0;j<2;++j)
                base.add(proof,delta[j],ring.multiply(G[i],ring.variable(canonical.variables[0][j])),-1);
            auto target=ring.substitute(blocks[4].companions[i],sigma);
            emit(out,ring,base,"remaining_companion"+std::to_string(i),target,proof,degree(blocks[4].companions[i]));
            parent_proofs.push_back(proof);
            auto fieldproof=base.zero();fieldproof[28+i]=one;
            emit(out,ring,base,"remaining_field"+std::to_string(i),base.axioms[28+i].value,fieldproof,2);
        }
        int raw=blocks[0].variables[0][0];
        auto multiplier=ring.multiply(sigma[raw],sigma[raw]);
        auto weighted=base.zero();base.add(weighted,parent_proofs[0],multiplier);
        auto target=ring.multiply(multiplier,ring.substitute(blocks[4].companions[0],sigma));
        emit(out,ring,base,"raw_old_cofactor",target,weighted,degree(blocks[4].companions[0])+2);
        std::map<int,int> point;
        for(int row=0;row<2;++row)for(int z=0;z<4;++z)
            point[100+4*row+z]=z==(row==0?2:1);
        for(int j=0;j<26;++j)need(ring.evaluate(base.axioms[j].value,point)==0,"local old control state");
        auto actual_B0=ring.substitute(blocks[2].product,sigma);
        need(ring.evaluate(actual_B0,point)==1 && ring.evaluate(values[0],point)==0,"wrong selector control");
        out<<"{\"type\":\"wrong_selector_control\",\"labels\":[2,1],\"actual_local_product\":1,"
               "\"incorrect_replacement\":0,\"satisfies_local_functional_and_column_axioms\":true}\n";
        need(product_values[3][0]==0 && product_values[3][8]==1,"dependency support control");
        out<<"{\"type\":\"dependency_support_control\",\"input\":";
        write_json(out,blocks[4].inputs[1]);
        out<<",\"literal_old_rows\":[0],\"propagated_rows\":[0,1],"
               "\"label_pairs\":[[0,0],[0,2]],\"semantic_values\":[0,1]}\n";
        need(certificates==30,"certificate count");
        out<<"{\"type\":\"summary\",\"NS_certificates\":30,\"row_states\":16,\"removed_blocks\":4,"
               "\"retained_blocks\":1,\"global_map_degree\":1,\"raw_cofactor_bound\":9,"
               "\"controls\":2,\"passed\":true}\n";
        out.close();need(bool(out),"write failed");
        std::cout<<"Passed 30 complete certificates for four local blocks, one retained parent, and two controls.\n";
    }catch(const std::exception& error){std::cerr<<"ERROR: "<<error.what()<<'\n';return 1;}
}
