// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Literal affine quotients of intact surviving occurrence families.
#include "ens_symbolic.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace ens_symbolic;
void need(bool condition,const std::string& message) {
    if(!condition) throw std::runtime_error(message);
}
struct Family {
    std::string key;
    Block block;
    std::vector<int> dependencies;
    bool live=true;
    int level=0;
};
bool closed(const std::vector<Family>& families) {
    for(const auto& family:families) if(family.live)
        for(int child:family.dependencies)
            if(child<0 || size_t(child)>=families.size() || !families[child].live) return false;
    return true;
}
void add_images(const Ring& ring,const Block& from,const Block& to,
                std::map<int,Polynomial>& images) {
    need(from.variables.size()==to.variables.size(),"accuracy mismatch");
    for(size_t u=0;u<from.variables.size();u++) {
        need(from.variables[u].size()==to.variables[u].size(),"arity mismatch");
        for(size_t j=0;j<from.variables[u].size();j++)
            images[from.variables[u][j]]=ring.variable(to.variables[u][j]);
    }
}
void run_case(std::ostream& out,int p,int h) {
    Ring ring(p,96);auto one=ring.constant(1);
    auto x=ring.variable(0),y=ring.variable(1),z=ring.variable(2),w=ring.variable(3);
    int fresh=4,width=p+1;std::vector<Family> families;std::vector<int> roots;
    const std::string inner_key="NOT_X_OR_NOT_Y";
    const std::string root_key="(X_AND_Y)_OR_Z",other_key="(X_AND_Y)_OR_W";
    for(int j=0;j<width;j++) {
        int inner=int(families.size());Block a=make_block(ring,{x,y},h,fresh);
        families.push_back({inner_key,a,{},true,1});
        Block b=make_block(ring,{a.product,ring.subtract(one,z)},h,fresh);
        roots.push_back(int(families.size()));families.push_back({root_key,b,{inner},true,2});
    }
    int other_inner=int(families.size());Block ai=make_block(ring,{x,y},h,fresh);
    families.push_back({inner_key,ai,{},true,1});
    int other_root=int(families.size());Block bi=make_block(ring,{ai.product,ring.subtract(one,w)},h,fresh);
    families.push_back({other_key,bi,{other_inner},true,2});
    // A removed ancestor has no block or coefficient family in this already-pruned system.
    int removed=int(families.size());
    families.push_back({"REMOVED_ANCESTOR",Block{}, {roots[0],other_root},false,3});
    need(closed(families),"initial survivor set is not closed");
    std::map<std::string,int> representative;
    for(size_t i=0;i<families.size();i++) if(families[i].live)
        representative.emplace(families[i].key,int(i));
    need(representative.size()==3 && !representative.count("REMOVED_ANCESTOR"),"revived absent class");
    std::map<int,Polynomial> images,upper_only;
    for(const auto& f:families) if(f.live) {
        const auto& chosen=families.at(representative.at(f.key));
        need(chosen.live && chosen.level==f.level,"invalid canonical witness");
        add_images(ring,f.block,chosen.block,images);
        if(f.key==root_key) add_images(ring,f.block,chosen.block,upper_only);
    }
    std::map<std::string,Block> canonical;
    for(const auto& [key,id]:representative) {
        const auto& original=families[id].block;
        std::vector<Polynomial> inputs;
        for(const auto& input:original.inputs) inputs.push_back(ring.substitute(input,images));
        int start=original.variables.front().front();
        Block b=make_block(ring,inputs,h,start);
        need(b.variables==original.variables,"canonical coefficient coordinates changed");
        canonical.emplace(key,b);
    }
    out<<"{\"record\":\"case\",\"p\":"<<p<<",\"accuracy\":"<<h
       <<",\"base_variables\":[\"x\",\"y\",\"z\",\"w\"],\"width\":"<<width
       <<",\"variables\":"<<fresh<<",\"families\":[";
    for(size_t id=0;id<families.size();id++) {
        if(id) out<<',';
        const auto& f=families[id];
        out<<"{\"id\":"<<id<<",\"key\":\""<<f.key<<"\",\"live\":"<<(f.live?"true":"false")
           <<",\"level\":"<<f.level<<",\"dependencies\":[";
        for(size_t j=0;j<f.dependencies.size();j++) {if(j) out<<',';out<<f.dependencies[j];}
        out<<']';
        if(f.live) {out<<",\"block\":";write_block(out,f.block);}
        out<<'}';
    }
    out<<"],\"coefficient_images\":[";
    bool comma=false;
    for(const auto& [variable,image]:images) {
        if(comma) out<<',';
        comma=true;out<<"{\"variable\":"<<variable<<",\"image\":";write_json(out,image);out<<'}';
    }
    out<<"],\"canonical_blocks\":[";
    comma=false;
    for(const auto& [key,b]:canonical) {
        if(comma) out<<',';
        comma=true;out<<"{\"key\":\""<<key<<"\",\"surviving_witness\":"
                       <<representative.at(key)<<",\"block\":";write_block(out,b);out<<'}';
    }
    out<<"]}\n";
    for(size_t id=0;id<families.size();id++) if(families[id].live) {
        const auto& f=families[id];const auto& b=canonical.at(f.key);
        need(ring.substitute(f.block.product,images)==b.product,"canonical product image");
        for(size_t j=0;j<f.block.inputs.size();j++)
            need(ring.substitute(f.block.inputs[j],images)==b.inputs[j],"canonical input image");
        out<<"{\"record\":\"axiom_images\",\"family\":"<<id<<",\"companions\":[";
        for(size_t j=0;j<f.block.companions.size();j++) {
            auto image=ring.substitute(f.block.companions[j],images);
            need(image==b.companions[j] && degree(image)<=degree(f.block.companions[j]),"companion image");
            if(j) out<<',';
            write_json(out,image);
        }
        out<<"],\"fields\":[";
        comma=false;
        for(const auto& row:f.block.variables) for(int variable:row) {
            auto r=ring.variable(variable),mapped=images.at(variable);
            auto image=ring.substitute(ring.subtract(ring.power(r,p),r),images);
            need(image==ring.subtract(ring.power(mapped,p),mapped),"field image");
            if(comma) out<<',';
            comma=true;write_json(out,image);
        }
        out<<"],\"all_passed\":true}\n";
    }
    Polynomial sum;
    for(int j=0;j<p;j++) ring.accumulate(sum,families[roots[j]].block.product);
    auto pair=ring.subtract(families[roots[0]].block.product,families[roots[1]].block.product);
    auto remainder=ring.add(sum,families[roots[p]].block.product);
    const auto& common=canonical.at(root_key).product;
    need(!sum.empty() && !pair.empty(),"original targets unexpectedly cancelled");
    need(ring.substitute(sum,images).empty(),"p-fold MOD cancellation");
    need(ring.substitute(pair,images).empty(),"signed pair cancellation");
    need(ring.substitute(ring.add(sum,one),images)==one,"nonzero constant scalar");
    need(ring.substitute(remainder,images)==common,"noncancelling multiplicity remainder");
    auto upper_error=ring.substitute(sum,upper_only);
    need(!upper_error.empty(),"upper-only sharing control is vacuous");
    auto wrong=images;
    add_images(ring,families[other_root].block,families[roots[0]].block,wrong);
    auto wrong_error=ring.subtract(ring.substitute(families[other_root].block.product,wrong),common);
    need(!wrong_error.empty(),"different-syntax merge control is vacuous");
    auto gapped=families;gapped[0].live=false;
    need(!closed(gapped),"missing-descendant hypothesis was not detected");
    out<<"{\"record\":\"scalar_images\",\"p_fold_scalar\":";write_json(out,sum);
    out<<",\"signed_pair_scalar\":";write_json(out,pair);
    out<<",\"remainder_scalar\":";write_json(out,remainder);
    out<<",\"images\":[[],[[1,[]]],[],";
    write_json(out,common);
    out<<"],\"image_order\":[\"p_fold\",\"p_fold_plus_one\",\"signed_pair\",\"p_plus_one\"],"
           "\"upper_only_error\":";write_json(out,upper_error);
    out<<",\"different_syntax_error\":";write_json(out,wrong_error);
    out<<",\"missing_descendant_rejected\":true,\"removed_class_absent\":true,"
           "\"removed_ancestor_id\":"<<removed<<"}\n";
    for(int qvalue=0;qvalue<2;qvalue++) {
        std::map<int,int> point;
        for(int i=0;i<fresh;i++) point[i]=0;
        point[0]=qvalue;point[1]=0;point[2]=1;point[3]=1;
        point[canonical.at(inner_key).variables[0][0]]=qvalue;
        point[canonical.at(root_key).variables[0][0]]=1-qvalue;
        point[canonical.at(other_key).variables[0][0]]=1-qvalue;
        for(const auto& [key,b]:canonical)
            for(const auto& e:b.companions) need(ring.evaluate(e,point)==0,"canonical model");
        need(ring.evaluate(common,point)==qvalue,"argument failed to attain both values");
        for(const auto& [variable,image]:images) point[variable]=ring.evaluate(image,point);
        for(const auto& f:families) if(f.live)
            for(const auto& e:f.block.companions) need(ring.evaluate(e,point)==0,"lifted model");
        out<<"{\"record\":\"argument_model\",\"common_value\":"<<qvalue<<",\"assignment\":[";
        for(int i=0;i<fresh;i++) {if(i) out<<',';out<<point.at(i);}
        out<<"],\"all_original_and_canonical_companions_zero\":true}\n";
    }
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");
        auto parent=std::filesystem::path(argv[2]).parent_path();
        if(!parent.empty()) std::filesystem::create_directories(parent);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"survivor_resharing\",\"seed\":null,"
               "\"scope\":\"literal axiom images and MOD scalar cancellation; no full proof compiler\"}\n";
        for(int p:{2,3,5,7}) for(int h:{1,2}) run_case(out,p,h);
        out<<"{\"record\":\"summary\",\"cases\":8,\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failed");
        std::cout<<"Eight recursive sharing cases, scalar cancellations, and negative controls passed.\n";
    } catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}
}
