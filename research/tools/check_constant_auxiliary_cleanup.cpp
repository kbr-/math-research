// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact constant-mode cascades after one goal-relative unit substitution.
#include "ens_symbolic.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace ens_symbolic;
void require(bool condition,const std::string& message) {if(!condition)throw std::runtime_error(message);}
using Term=std::pair<Polynomial,Polynomial>; // axiom, cofactor
int ns_certificate(std::ostream& out,const Ring& ring,const std::string& name,
                   const Polynomial& target,const std::vector<Term>& terms,int bound) {
    Polynomial sum;int maximum=0;
    for(const auto& [axiom,cofactor]:terms) {
        auto term=ring.multiply(axiom,cofactor);ring.accumulate(sum,term);maximum=std::max(maximum,degree(term));
    }
    require(sum==target && maximum<=bound,"NS certificate "+name);
    out<<"{\"record\":\"certificate\",\"name\":\""<<name<<"\",\"target\":";write_json(out,target);
    out<<",\"degree\":"<<maximum<<",\"bound\":"<<bound<<",\"terms\":[";
    for(size_t i=0;i<terms.size();i++) {
        if(i)out<<',';
        out<<"{\"axiom\":";write_json(out,terms[i].first);out<<",\"cofactor\":";write_json(out,terms[i].second);out<<'}';
    }
    out<<"]}\n";return maximum;
}
void write_images(std::ostream& out,const std::map<int,Polynomial>& images) {
    out<<'[';bool comma=false;
    for(const auto& [id,value]:images) {if(comma)out<<',';comma=true;out<<'['<<id<<',';write_json(out,value);out<<']';}
    out<<']';
}
void field_images(std::ostream& out,const Ring& ring,const Block& block,
                  const std::map<int,Polynomial>& images) {
    out<<'[';bool comma=false;
    for(const auto& row:block.variables)for(int id:row) {
        auto r=ring.variable(id),f=ring.subtract(ring.power(r,ring.p),r),image=ring.substitute(f,images);
        require(image.empty(),"nonzero coefficient field image");
        if(comma)out<<',';
        comma=true;out<<"{\"variable\":"<<id<<",\"original\":";write_json(out,f);out<<",\"image\":[]}";
    }
    out<<']';
}
void chain(std::ostream& out,int p,int h,int depth) {
    Ring ring(p,64);auto one=ring.constant(1),x=ring.variable(0),y=ring.variable(1),z=ring.variable(2);
    int next=3;std::vector<Block> blocks;
    blocks.push_back(make_block(ring,{x,y},h,next));
    for(int j=1;j<=depth;j++) {
        auto previous=blocks.back().product;
        blocks.push_back(make_block(ring,j%2?std::vector<Polynomial>{previous,z}:std::vector<Polynomial>{previous,previous},h,next));
    }
    out<<"{\"record\":\"chain\",\"p\":"<<p<<",\"accuracy\":"<<h<<",\"parents\":"<<depth
       <<",\"goal_inputs\":";write_polynomials(out,{x,y});out<<",\"blocks\":[";
    for(size_t i=0;i<blocks.size();i++) {if(i)out<<',';write_block(out,blocks[i]);}
    out<<"],\"old_boolean_axioms\":[";
    for(int i=0;i<3;i++) {if(i)out<<',';auto v=ring.variable(i);write_json(out,ring.subtract(ring.multiply(v,v),v));}
    out<<"]}\n";

    const auto& initial=blocks.front();const auto& last=blocks.back();
    auto target=ring.add(x,last.companions[0]);
    std::vector<Term> source{{initial.companions[0],one},{x,ring.multiply(x,initial.prefix[0])},
                             {y,ring.multiply(x,initial.prefix[1])},{last.companions[0],one}};
    int source_bound=std::max(2*h+1,degree(last.companions[0]));
    int source_degree=ns_certificate(out,ring,"source_target",target,source,source_bound);
    std::map<int,Polynomial> images;
    for(size_t i=0;i<blocks.size();i++) {
        const auto& b=blocks[i];std::vector<Polynomial> current_inputs,beta(2);
        for(const auto& g:b.inputs)current_inputs.push_back(ring.substitute(g,images));
        std::string mode=i==0?"goal_unit":i%2?"nonzero_constant":"all_zero_inputs";
        int result=i%2?0:1;
        if(i==0)require(current_inputs==std::vector<Polynomial>({x,y}),"initial goals changed");
        else if(i%2) {require(current_inputs[0]==one,"missing nonzero constant input");beta[0]=one;}
        else require(current_inputs[0].empty() && current_inputs[1].empty(),"inputs are not both zero");
        auto local=coefficient_images(ring,b,beta);images.insert(local.begin(),local.end());
        auto product=ring.substitute(b.product,images);
        require(product==ring.constant(result),"wrong propagated product value");
        std::vector<Polynomial> companion_images;
        for(size_t j=0;j<b.companions.size();j++) {
            auto image=ring.substitute(b.companions[j],images);
            require(image==(i==0?current_inputs[j]:Polynomial{}),"wrong companion image");
            require(degree(image)<=degree(b.companions[j]),"image degree increased");
            companion_images.push_back(image);
        }
        out<<"{\"record\":\"step\",\"block\":"<<i<<",\"mode\":\""<<mode<<"\",\"current_inputs\":";
        write_polynomials(out,current_inputs);out<<",\"coefficient_images\":";write_images(out,local);
        out<<",\"product_image\":";write_json(out,product);out<<",\"companion_images\":";
        write_polynomials(out,companion_images);out<<",\"field_images\":";field_images(out,ring,b,images);out<<"}\n";
    }
    require(ring.substitute(x,images)==x && ring.substitute(y,images)==y,"protected goal changed");
    auto final_target=ring.substitute(target,images);require(final_target==x,"target image");
    Polynomial mapped_sum;
    for(const auto& [axiom,cofactor]:source)
        ring.accumulate(mapped_sum,ring.multiply(ring.substitute(axiom,images),ring.substitute(cofactor,images)));
    require(mapped_sum==x,"whole certificate did not specialize");
    int replay_degree=ns_certificate(out,ring,"replayed_target_from_goal",x,{{x,one}},1);

    std::map<int,int> model{{0,0},{1,0},{2,1}};
    for(const auto& [id,value]:images)model[id]=ring.evaluate(value,model);
    for(const auto& b:blocks)for(const auto& axiom:b.companions)require(ring.evaluate(axiom,model)==0,"common model companion");
    require(ring.evaluate(target,model)==0,"common model target");
    out<<"{\"record\":\"common_model\",\"assignment\":[";bool comma=false;
    for(const auto& [id,value]:model) {if(comma)out<<',';comma=true;out<<'['<<id<<','<<value<<']';}
    out<<"]}\n";
    // After complete removal, Boolean x=1,y=0,z=0 satisfies the retained
    // domain and the other goal, but violates the selected xP image x.
    std::map<int,int> missing{{0,1},{1,0},{2,0}};
    require(ring.evaluate(x,missing)==1 && ring.evaluate(y,missing)==0,"missing goal control");
    out<<"{\"record\":\"missing_goal_control\",\"assignment\":[[0,1],[1,0],[2,0]],\"selected_image_value\":1}\n";
    out<<"{\"record\":\"chain_verified\",\"source_degree\":"<<source_degree<<",\"replayed_degree\":"<<replay_degree
       <<",\"zero_modes\":"<<(depth+1)/2<<",\"unit_modes\":"<<depth/2<<",\"all_passed\":true}\n";
}
void inverse_control(std::ostream& out,int p,int h) {
    Ring ring(p,32);int next=1;auto c=ring.constant(2),z=ring.variable(0);
    auto b=make_block(ring,{c,z},h,next);
    int inverse=1;for(int j=0;j<p-2;j++)inverse=inverse*2%p;
    auto correct=coefficient_images(ring,b,{ring.constant(inverse),{}});
    auto wrong=coefficient_images(ring,b,{{},{}});
    require(ring.substitute(b.product,correct).empty(),"inverse did not kill product");
    require(ring.substitute(b.companions[0],wrong)==c,"wrong assignment control");
    for(const auto& e:b.companions)require(ring.substitute(e,correct).empty(),"correct companion image");
    out<<"{\"record\":\"inverse_control\",\"p\":"<<p<<",\"accuracy\":"<<h<<",\"input_constant\":2,\"inverse\":"<<inverse<<",\"block\":";
    write_block(out,b);out<<",\"correct_images\":";write_images(out,correct);
    out<<",\"wrong_images\":";write_images(out,wrong);
    out<<",\"wrong_first_companion\":";write_json(out,c);
    out<<",\"correct_field_images\":";field_images(out,ring,b,correct);
    out<<",\"wrong_field_images\":";field_images(out,ring,b,wrong);out<<"}\n";
}
int main(int argc,char** argv) {
    try {
        require(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        require(!std::filesystem::exists(argv[2]),"output exists");
        auto dir=std::filesystem::path(argv[2]).parent_path();if(!dir.empty())std::filesystem::create_directories(dir);
        std::ofstream out(argv[2]);require(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"constant_auxiliary_cleanup\",\"seed\":null,\"scope\":\"exact local image cascades and satisfiable target certificates, not PHP refutations\"}\n";
        for(int p:{2,3,5}) {for(int depth:{1,2,5})chain(out,p,1,depth);chain(out,p,2,1);}
        for(int p:{3,5})for(int h:{1,2})inverse_control(out,p,h);
        out<<"{\"record\":\"summary\",\"chains\":12,\"source_and_image_certificates\":24,\"goal_unit_cuts\":12,\"constant_zero_cuts\":18,\"all_zero_input_cuts\":9,\"common_models\":12,\"missing_goal_controls\":12,\"inverse_controls\":4,\"all_passed\":true}\n";
        out.close();require(bool(out),"output write failed");
        std::cout<<"Twelve exact constant cascades, 24 certificates, and four inverse controls passed.\n";
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
