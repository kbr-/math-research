// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact boundary interpolation, complete NS witnesses, and later-input controls.
#include "ns_witness.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace ens_symbolic;

void need(bool ok,const char* message) {
    if(!ok)throw std::runtime_error(message);
}
struct Node {
    std::vector<Polynomial> inputs;
    std::vector<std::vector<int>> variables;
    int value[2]={0,0};
    Polynomial image;
};
struct Checks {
    std::ostream& out;
    int certificates=0,models=0,cases=0,odd_controls=0;
    void certificate(const Ring& ring,const std::string& key,const std::string& scope,
                     const std::vector<Polynomial>& axioms,const Polynomial& target,
                     const std::map<int,Polynomial>& cofactors,int budget,
                     const std::string& label) {
        out<<"{\"record\":\"ns_certificate\",\"case\":\""<<key
           <<"\",\"axiom_table\":\""<<scope<<"\",\"label\":\""<<label
           <<"\",\"budget\":"<<budget<<",\"target\":";
        write_json(out,target);
        ns_witness::write_terms(out,ring,axioms,target,cofactors,budget,label);
        out<<",\"passed\":true}\n";++certificates;
    }
};
void field_axioms(const Ring& ring,const Block& b,std::vector<Polynomial>& axioms) {
    for(const auto& row:b.variables)for(int id:row)
        axioms.push_back(ring.subtract(ring.power(ring.variable(id),ring.p),ring.variable(id)));
}
std::vector<int> add_block_axioms(const Ring& ring,const Block& b,
                                std::vector<Polynomial>& axioms) {
    std::vector<int> ids;
    for(const auto& e:b.companions) {
        ids.push_back(axioms.size());axioms.push_back(e);
    }
    field_axioms(ring,b,axioms);return ids;
}
void write_axioms(std::ostream& out,const std::string& key,const char* scope,
                  const std::vector<Polynomial>& axioms) {
    out<<"{\"record\":\"axiom_table\",\"case\":\""<<key
       <<"\",\"name\":\""<<scope<<"\",\"axioms\":";
    write_polynomials(out,axioms);out<<"}\n";
}
Polynomial affine_value(const Ring& ring,int a,int b,const Polynomial& z) {
    auto value=ring.constant(a);ring.accumulate(value,z,b-a);return value;
}
void prefix_check(const Ring& ring,const Block& b) {
    Polynomial sum=b.product;
    for(unsigned i=0;i<b.inputs.size();++i)
        ring.accumulate(sum,ring.multiply(b.prefix[i],b.inputs[i]));
    need(sum==ring.constant(1),"literal ENS prefix identity");
}
void write_source_node(std::ostream& out,const Node& n,int index,int h) {
    out<<"{\"id\":"<<index<<",\"accuracy\":"<<h<<",\"inputs\":";
    write_polynomials(out,n.inputs);
    out<<",\"coefficient_variables\":[";
    for(unsigned u=0;u<n.variables.size();++u) {
        if(u)out<<',';
        out<<'[';
        for(unsigned j=0;j<n.variables[u].size();++j) {
            if(j)out<<',';
            out<<n.variables[u][j];
        }
        out<<']';
    }
    out<<"],\"character_values\":["<<n.value[0]<<','<<n.value[1]<<"],\"image\":";
    write_json(out,n.image);out<<'}';
}
void one_case(Checks& check,int p,int h) {
    Ring ring(p,32);const int r=2*h+1,old=r+1,w=2*h;
    int fresh=old;
    const auto one=ring.constant(1);
    std::vector<Polynomial> boundary_inputs;
    for(int i=0;i<r;++i)boundary_inputs.push_back(ring.variable(i));
    auto boundary=make_block(ring,boundary_inputs,h,fresh);
    prefix_check(ring,boundary);
    need(degree(boundary.product)==w,"original affine product degree");
    std::vector<Node> nodes(20);
    for(int type=0;type<4;++type) {
        if(type==1 || type==2) {
            for(int i=0;i<r;++i)nodes[type].inputs.push_back(
                i==0&&type==2 ? ring.subtract(ring.variable(i),one):ring.variable(i));
        }else{
            for(int i=1;i<=r;++i)nodes[type].inputs.push_back(
                i==1&&type==0 ? ring.subtract(ring.variable(i),one):ring.variable(i));
        }
    }
    for(int a=0;a<4;++a)for(int b=0;b<4;++b) {
        auto& n=nodes[4+4*a+b];
        n.inputs=nodes[a].inputs;
        n.inputs.insert(n.inputs.end(),nodes[b].inputs.begin(),nodes[b].inputs.end());
    }
    std::map<int,int> point[2];
    for(int i=0;i<old;++i)point[0][i]=point[1][i]=0;
    point[0][0]=1; // Outside the boundary flat; point[1] is inside it.
    for(unsigned a=0;a<nodes.size();++a) {
        auto& n=nodes[a];
        if(a==1)n.variables=boundary.variables;
        else for(int u=0;u<h;++u) {
            std::vector<int> row;
            for(unsigned j=0;j<n.inputs.size();++j)row.push_back(fresh++);
            n.variables.push_back(row);
        }
        for(int e=0;e<2;++e) {
            n.value[e]=1;
            for(const auto& g:n.inputs)
                if(ring.evaluate(g,point[e]))n.value[e]=0;
        }
        n.image=affine_value(ring,n.value[0],n.value[1],boundary.product);
    }
    need(nodes[0].value[0]==0&&nodes[0].value[1]==0,"constant-zero type");
    need(nodes[1].value[0]==0&&nodes[1].value[1]==1,"boundary fixed");
    need(nodes[2].value[0]==1&&nodes[2].value[1]==0,"complement type");
    need(nodes[3].value[0]==1&&nodes[3].value[1]==1,"constant-one type");

    // Original formal inputs are Z_1 and 1-Z_2; both images are P_boundary.
    auto parent=make_block(ring,{nodes[1].image,ring.subtract(one,nodes[2].image)},h,fresh);
    prefix_check(ring,parent);
    const int parent_weight=h*(w+1),parent_budget=parent_weight+2*w;
    need(parent.inputs[0]==boundary.product&&parent.inputs[1]==boundary.product,
         "later inputs collapse to one retained selector");
    need(degree(parent.product)==parent_weight,"retained original product ceiling");
    for(const auto& e:parent.companions)
        need(degree(e)==parent_weight+w,"retained original companion ceiling");
    std::vector<Polynomial> retained;
    for(int i=0;i<old;++i)
        retained.push_back(ring.subtract(ring.power(ring.variable(i),2),ring.variable(i)));
    auto boundary_ids=add_block_axioms(ring,boundary,retained);
    auto parent_ids=add_block_axioms(ring,parent,retained);
    std::string key="p"+std::to_string(p)+"_h"+std::to_string(h);
    auto& out=check.out;
    out<<"{\"record\":\"case\",\"key\":\""<<key<<"\",\"prime\":"<<p
       <<",\"old_variables\":"<<old<<",\"boundary_rank\":"<<r
       <<",\"weight\":"<<w<<",\"parent_weight\":"<<parent_weight
       <<",\"parent_port_budget\":"<<parent_budget
       <<",\"base\":\"Boolean-only local source\",\"source_coefficient_domains\":\"r^p-r for every listed coefficient variable\","
         "\"source_product_recipe\":\"ordered product over coefficient rows of (1-sum_j r_uj*g_j)\","
         "\"component_nodes\":[";
    for(unsigned a=0;a<nodes.size();++a) {
        if(a)out<<',';
        write_source_node(out,nodes[a],a,h);
    }
    out<<"],\"retained_boundary_node\":1,\"original_later_inputs\":\"Z_1, 1-Z_2\","
         "\"original_selector_coefficient_matrix\":[[1,0],[0,"<<p-1
       <<"]],\"new_selector_coefficient_matrix\":[[1],[1]],\"rebuilt_parent\":";
    write_block(out,parent);
    out<<",\"prefixes_checked\":true}\n";
    write_axioms(out,key,"retained",retained);
    auto boundary_bool=ring.subtract(ring.power(boundary.product,2),boundary.product);
    auto bool_cofactors=[&](int scalar) {
        std::map<int,Polynomial> result;
        for(int i=0;i<r;++i) {
            Polynomial q;ring.accumulate(q,boundary.prefix[i],-scalar);
            result[boundary_ids[i]]=q;
        }
        return result;
    };
    int before=check.certificates;
    for(int a=0;a<4;++a)for(int b=0;b<4;++b) {
        int c=4+4*a+b;
        for(int e=0;e<2;++e)
            need(nodes[c].value[e]==nodes[a].value[e]*nodes[b].value[e],"union characters");
        auto target=ring.subtract(nodes[c].image,ring.multiply(nodes[a].image,nodes[b].image));
        int scalar=ring.residue(-(nodes[a].value[1]-nodes[a].value[0])*
                               (nodes[b].value[1]-nodes[b].value[0]));
        need(target==ring.multiply(ring.constant(scalar),boundary_bool),"literal one-boundary union identity");
        check.certificate(ring,key,"retained",retained,target,bool_cofactors(scalar),2*w,
                          "union_"+std::to_string(a)+"_"+std::to_string(b));
    }
    for(int a=0;a<4;++a) {
        auto target=ring.subtract(nodes[4+4*a+a].image,nodes[a].image);
        check.certificate(ring,key,"retained",retained,target,{},2*w,"copy_"+std::to_string(a));
    }
    for(unsigned a=0;a<nodes.size();++a) {
        int difference=nodes[a].value[1]-nodes[a].value[0];
        auto target=ring.subtract(ring.power(nodes[a].image,2),nodes[a].image);
        check.certificate(ring,key,"retained",retained,target,
                          bool_cofactors(difference*difference),2*w,
                          "Booleanity_"+std::to_string(a));
    }
    auto a=ring.subtract(one,boundary.product),b=nodes[2].image;
    auto target=ring.subtract(parent.product,ring.multiply(a,b));
    std::map<int,Polynomial> cofs;
    cofs[parent_ids[0]]=one;cofs[parent_ids[1]]=a;
    auto multiplier=ring.add(ring.multiply(parent.prefix[0],b),
                             ring.multiply(parent.prefix[1],a));
    for(int i=0;i<r;++i) {
        Polynomial q;ring.accumulate(q,ring.multiply(multiplier,boundary.prefix[i]),-1);
        cofs[boundary_ids[i]]=q;
    }
    check.certificate(ring,key,"retained",retained,target,cofs,parent_budget,"rebuilt_later_port");

    // Separate systems for the general boundary-type witness bounds.
    auto patterns=retained;
    int duplicate_fresh=nodes[2].variables[0][0];
    auto opposite=make_block(ring,nodes[2].inputs,h,duplicate_fresh);
    need(opposite.variables==nodes[2].variables,"original opposite block definition");
    auto opposite_ids=add_block_axioms(ring,opposite,patterns);
    auto containing=make_block(ring,{ring.variable(0)},h,fresh);
    add_block_axioms(ring,containing,patterns);
    std::vector<Block> field_cover;
    for(int c=0;c<p;++c) {
        field_cover.push_back(make_block(ring,{ring.subtract(ring.variable(0),ring.constant(c))},h,fresh));
        add_block_axioms(ring,field_cover.back(),patterns);
    }
    out<<"{\"record\":\"pattern_blocks\",\"case\":\""<<key<<"\",\"opposite\":";
    write_block(out,opposite);out<<",\"containing\":";
    write_block(out,containing);out<<",\"field_cover\":[";
    for(unsigned i=0;i<field_cover.size();++i) {
        if(i)out<<',';
        write_block(out,field_cover[i]);
    }
    out<<"]}\n";write_axioms(out,key,"patterns",patterns);
    cofs.clear();cofs[boundary_ids[0]]=opposite.product;
    ring.accumulate(cofs[opposite_ids[0]],boundary.product,-1);
    check.certificate(ring,key,"patterns",patterns,ring.multiply(boundary.product,opposite.product),
                      cofs,2*w+1,"inconsistent_positive_type");
    cofs.clear();cofs[boundary_ids[0]]=containing.prefix[0];
    check.certificate(ring,key,"patterns",patterns,
                      ring.multiply(boundary.product,ring.subtract(one,containing.product)),
                      cofs,2*w,"positive_flat_inside_negative_flat");
    auto cover_product=one,cover_prefix=one;
    for(const auto& block:field_cover) {
        prefix_check(ring,block);
        cover_product=ring.multiply(cover_product,ring.subtract(one,block.product));
        cover_prefix=ring.multiply(cover_prefix,block.prefix[0]);
    }
    Polynomial power_sum;
    for(int exponent=0;exponent<=p-2;++exponent)
        ring.accumulate(power_sum,ring.power(ring.variable(0),exponent));
    cofs.clear();cofs[0]=ring.multiply(cover_prefix,power_sum);
    check.certificate(ring,key,"patterns",patterns,cover_product,cofs,p*w,"all_field_hyperplanes_cover");
    need(check.certificates-before==44,"complete certificate count per case");

    for(int model=0;model<3;++model) {
        std::map<int,int> values;
        for(int i=0;i<old;++i)values[i]=0;
        if(model)values[model-1]=1;
        for(const auto& row:boundary.variables)for(int id:row)values[id]=p>2?2:0;
        if(model)values[boundary.variables[0][model-1]]=1;
        int z=ring.evaluate(boundary.product,values);
        need(z==(model?0:1),"retained boundary point value");
        for(const auto& row:parent.variables)for(int id:row)values[id]=0;
        if(z) {
            values[parent.variables[0][0]]=p>2?p-1:1;
            values[parent.variables[0][1]]=p>2?2:0;
        }else for(const auto& row:parent.variables)for(int id:row)values[id]=p>2?2:0;
        for(const auto& e:retained)need(ring.evaluate(e,values)==0,"complete retained model");
        bool nonboolean=false;
        for(const auto& row:boundary.variables)for(int id:row)
            nonboolean|=ring.residue(values[id]*values[id]-values[id])!=0;
        need(nonboolean==(p>2),"non-Boolean coefficient-field control");
        int wrong_boundary=model==1?ring.residue(values[0]*(1-z)):0;
        bool hidden_prefix=model==2,hidden_companion=model==2;
        if(hidden_prefix)for(const auto& g:nodes[0].inputs)
            need(ring.evaluate(g,values)==0,"discarded zero-flat value is genuinely forced at this point");
        if(hidden_companion)
            need(ring.evaluate(nodes[3].inputs[0],values)*ring.evaluate(nodes[3].image,values)==1,
                 "exposed discarded companion would fail");
        need(model!=1||wrong_boundary==1,"changing the retained boundary breaks its outside companion");
        out<<"{\"record\":\"retained_model\",\"case\":\""<<key<<"\",\"model\":"<<model
           <<",\"values\":[";
        bool comma=false;
        for(auto [id,value]:values) {
            if(comma)out<<',';
            comma=true;out<<'['<<id<<','<<value<<']';
        }
        out<<"],\"all_retained_axioms_zero\":true,\"coefficient_nonBoolean\":"<<(nonboolean?"true":"false")
           <<",\"wrong_boundary_companion\":"<<wrong_boundary
           <<",\"hidden_prefix_use_fails\":"<<(hidden_prefix?"true":"false")
           <<",\"hidden_companion_use_fails\":"<<(hidden_companion?"true":"false")<<"}\n";
        ++check.models;
    }
    if(p>2) {
        std::map<int,int> values;
        for(int i=0;i<old;++i)values[i]=0;
        values[0]=1;
        for(const auto& row:boundary.variables)for(int id:row)values[id]=0;
        values[boundary.variables[0][0]]=2;
        for(const auto& row:parent.variables)for(int id:row)values[id]=0;
        values[parent.variables[0][0]]=p-1;
        for(unsigned id=0;id<retained.size();++id) {
            bool boundary_comp=false;
            for(int i:boundary_ids)boundary_comp|=int(id)==i;
            if(!boundary_comp)need(ring.evaluate(retained[id],values)==0,"omitted-boundary-companion control");
        }
        int failure=ring.evaluate(boundary_bool,values);
        need(failure!=0,"boundary companions are needed outside the binary domain-only case");
        out<<"{\"record\":\"omitted_boundary_control\",\"case\":\""<<key<<"\",\"values\":[";
        bool comma=false;
        for(auto [id,value]:values) {
            if(comma)out<<',';
            comma=true;out<<'['<<id<<','<<value<<']';
        }
        out<<"],\"all_other_axioms_zero\":true,\"boundary_Booleanity_value\":"<<failure<<"}\n";
        ++check.odd_controls;
    }
    ++check.cases;
}
int main(int argc,char** argv) {
    try {
        need(argc==3&&std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];
        need(!std::filesystem::exists(path),"output already exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");
        out<<"{\"record\":\"schema\",\"version\":1,\"polynomials\":\"[coefficient,[sorted repeated variable IDs]]\","
             "\"degrees\":\"ordinary joint-variable degrees, with original source ceilings retained\","
             "\"original_component\":\"factored definitions plus complete companions g_i*P and all own r^p-r equations\"}\n";
        Checks check{out};
        for(int h:{1,2})for(int p:{2,3,5})one_case(check,p,h);
        need(check.cases==6&&check.certificates==264&&check.models==18&&check.odd_controls==4,
             "complete boundary-compression check counts");
        out<<"{\"record\":\"summary\",\"cases\":6,\"ns_certificates\":264,\"retained_models\":18,"
             "\"odd_field_omission_controls\":4,\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<"Boundary compression: 264 NS certificates, 18 complete retained models, "
                    "and four odd-field omission controls passed.\n";
    }catch(const std::exception& e) {
        std::cerr<<e.what()<<'\n';return 1;
    }
}
