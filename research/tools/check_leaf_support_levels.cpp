// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Source OR depth collapses brackets; certificate support must be checked separately.
#include "ens_symbolic.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
using namespace ens_symbolic;
void need(bool condition,const std::string& why){if(!condition)throw std::runtime_error(why);}
struct Node{
    char kind='?';std::vector<int> children;Polynomial value;
    int source_depth=0,ens_level=0,binary_depth=0;Block extension{};
};
struct Builder{
    Ring ring;int fresh;std::vector<Node> nodes;
    Builder(int p,int atoms):ring(p),fresh(atoms){}
    int append(Node node){nodes.push_back(std::move(node));return int(nodes.size())-1;}
    int atom(int v){Node n;n.kind='x';n.value=ring.variable(v);return append(std::move(n));}
    int truth(){Node n;n.kind='t';return append(std::move(n));}
    int neg(int child){
        Node n;n.kind='n';n.children={child};n.value=ring.subtract(ring.constant(1),nodes.at(child).value);
        n.source_depth=nodes[child].source_depth+1;n.ens_level=nodes[child].ens_level;
        n.binary_depth=nodes[child].binary_depth+1;return append(std::move(n));
    }
    void frontier(int id,std::vector<int>& result)const{
        if(nodes.at(id).kind!='o'){result.push_back(id);return;}
        for(int child:nodes[id].children)frontier(child,result);
    }
    int disjunction(int a,int b){
        Node n;n.kind='o';n.children={a,b};std::vector<int> leaves;frontier(a,leaves);frontier(b,leaves);
        std::vector<Polynomial> inputs;
        for(int id:leaves){
            n.source_depth=std::max(n.source_depth,nodes[id].source_depth);
            n.ens_level=std::max(n.ens_level,nodes[id].ens_level);
            inputs.push_back(ring.subtract(ring.constant(1),nodes[id].value));
        }
        ++n.source_depth;++n.ens_level;
        n.binary_depth=std::max(nodes[a].binary_depth,nodes[b].binary_depth)+1;
        n.extension=make_block(ring,std::move(inputs),1,fresh);n.value=n.extension.product;
        return append(std::move(n));
    }
    void write(std::ostream& out)const{
        for(size_t i=0;i<nodes.size();i++){
            const auto& n=nodes[i];out<<"{\"record\":\"node\",\"id\":"<<i<<",\"kind\":\""<<n.kind
                <<"\",\"source_depth\":"<<n.source_depth<<",\"ens_level\":"<<n.ens_level
                <<",\"binary_depth\":"<<n.binary_depth<<",\"children\":[";
            for(size_t j=0;j<n.children.size();j++){if(j)out<<',';out<<n.children[j];}
            out<<"],\"value\":";write_json(out,n.value);
            if(n.kind=='o'){out<<",\"block\":";write_block(out,n.extension);}
            out<<"}\n";
        }
    }
};
void positive(std::ostream& out,int p,int arity){
    Builder b(p,arity);std::vector<int> negated;
    for(int j=0;j<arity;j++)negated.push_back(b.neg(b.atom(j)));
    int argument=b.disjunction(negated[0],negated[1]);
    for(int j=2;j<arity;j++)argument=b.disjunction(negated[j],argument);
    int root=b.disjunction(b.truth(),argument);
    const auto& n=b.nodes[root];
    need(n.source_depth==2 && n.ens_level==1,"flattened root depth");
    need(b.nodes[argument].ens_level==n.ens_level,"proper argument must be same level in control");
    int same=0;
    for(int i=0;i<root;i++)if(b.nodes[i].kind=='o' && b.nodes[i].ens_level==n.ens_level)++same;
    need(same==arity-1 && n.binary_depth==arity+1,"raw chain counterexample");
    auto one=b.ring.constant(1);need(n.extension.inputs[0]==one,"TRUE input is one");
    need(n.extension.companions[0]==n.value,"one-companion source certificate");
    std::vector<Polynomial> beta(n.extension.inputs.size());beta[0]=one;
    need(normalizer_error(b.ring,n.extension.inputs,beta).empty(),"strict older unit witness");
    out<<"{\"record\":\"case\",\"kind\":\"positive_TRUE_or_X\",\"p\":"<<p<<",\"arity\":"<<arity
       <<",\"argument_node\":"<<argument<<",\"root_node\":"<<root<<",\"same_level_proper_blocks\":"<<same<<"}\n";
    b.write(out);
    out<<"{\"record\":\"positive_unit\",\"target\":";write_json(out,one);
    out<<",\"root_inputs\":";write_polynomials(out,n.extension.inputs);
    out<<",\"cofactors\":";write_polynomials(out,beta);
    out<<",\"degree\":0,\"older_companion_support\":[],\"pure_root_argument_ignored\":true,"
           "\"proper_implies_strictly_earlier_rejected\":true}\n";
}
void negative(std::ostream& out,int p){
    Builder b(p,1);int x=b.atom(0),notx=b.neg(x),core=b.disjunction(notx,x),contradiction=b.neg(core);
    int intermediate=b.disjunction(contradiction,contradiction);
    int root=b.disjunction(contradiction,intermediate),leaf=b.neg(root);
    const auto& c=b.nodes[core];const auto& r=b.nodes[root];
    need(b.nodes[intermediate].ens_level==r.ens_level && r.ens_level==2,"negative same-level grouping");
    need(c.ens_level==1 && c.ens_level<r.ens_level,"negative input proof support");
    auto sum=b.ring.add(c.extension.companions[0],c.extension.companions[1]);
    need(sum==c.value,"negative input certificate");
    for(const auto& g:r.extension.inputs)need(g==c.value,"flattened negative inputs");
    Polynomial cofactor;
    for(const auto& q:r.extension.prefix)b.ring.accumulate(cofactor,q);
    auto source=b.ring.multiply(cofactor,sum);
    need(source==b.nodes[leaf].value,"negative source certificate");
    out<<"{\"record\":\"case\",\"kind\":\"negative_grouped_contradictions\",\"p\":"<<p
       <<",\"core_node\":"<<core<<",\"intermediate_node\":"<<intermediate<<",\"root_node\":"<<root
       <<",\"leaf_node\":"<<leaf<<"}\n";b.write(out);
    out<<"{\"record\":\"negative_input_certificate\",\"target\":";write_json(out,c.value);
    out<<",\"axioms\":";write_polynomials(out,c.extension.companions);
    out<<",\"cofactors\":[[[1,[]]],[[1,[]]]],\"degree\":3,\"support_level\":1,\"root_level\":2,"
           "\"same_level_intermediate_unused\":true}\n";
    out<<"{\"record\":\"negative_source_certificate\",\"target\":";write_json(out,source);
    out<<",\"cofactor_for_each_core_companion\":";write_json(out,cofactor);
    out<<",\"degree\":"<<degree(cofactor)+degree(c.extension.companions[0])<<"}\n";
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");std::ofstream out(argv[2]);need(bool(out),"open output");
        out<<"{\"schema\":1,\"suite\":\"leaf_support_levels\",\"seed\":null,"
               "\"scope\":\"source depth and witness-support controls, not a full axiom compiler\"}\n";
        for(int p:{2,3}){for(int arity:{3,8,24})positive(out,p,arity);negative(out,p);}
        out<<"{\"record\":\"summary\",\"positive_cases\":6,\"negative_cases\":2,\"all_passed\":true}\n";
        out.close();need(bool(out),"write output");
        std::cout<<"Eight flattened-depth and strictly-earlier leaf-support controls passed.\n";
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
