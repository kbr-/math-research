// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
#include "ens_symbolic.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
using namespace ens_symbolic;
void need(bool b,const char* message) {if(!b) throw std::runtime_error(message);}
std::vector<int> variables(const Block& block) {
    std::vector<int> result;
    for(const auto& row:block.variables) result.insert(result.end(),row.begin(),row.end());
    return result;
}
bool uses(const Polynomial& value,const std::vector<int>& ids) {
    for(const auto& [monomial,coefficient]:value) {
        (void)coefficient;
        for(int id:ids) if(std::find(monomial.begin(),monomial.end(),id)!=monomial.end()) return true;
    }
    return false;
}
void run(std::ostream& out,int p,int h) {
    Ring ring(p,64);auto one=ring.constant(1);
    auto x=ring.variable(0),y=ring.variable(1),z=ring.variable(2);int next=3;
    Block inner=make_block(ring,{x,y},h,next);
    Block retained=make_block(ring,{inner.product,ring.subtract(one,z)},h,next);
    Block other_inner=make_block(ring,{x,y},h,next);
    Block selected=make_block(ring,{other_inner.product,ring.subtract(one,z)},h,next);
    std::map<int,Polynomial> images;
    for(size_t u=0;u<inner.variables.size();u++) for(size_t j=0;j<inner.variables[u].size();j++)
        images[other_inner.variables[u][j]]=ring.variable(inner.variables[u][j]);
    int private_first=selected.variables.front().front();
    Block private_image=make_block(ring,retained.inputs,h,private_first);
    need(private_image.variables==selected.variables,"private variables changed");
    need(ring.substitute(selected.product,images)==private_image.product,"private product image");
    for(size_t i=0;i<selected.companions.size();i++) {
        need(ring.substitute(selected.companions[i],images)==private_image.companions[i],"private companion image");
        need(ring.substitute(other_inner.companions[i],images)==inner.companions[i],"descendant image");
    }
    auto private_ids=variables(selected),retained_ids=variables(retained);
    for(const auto& axiom:retained.companions) need(!uses(axiom,private_ids),"retained axiom uses private root");
    need(!uses(retained.product,private_ids),"old target uses private root");
    for(int id:private_ids) {
        auto r=ring.variable(id);
        need(ring.substitute(r,images)==r,"selected root must remain private");
        need(ring.substitute(ring.subtract(ring.power(r,p),r),images)==ring.subtract(ring.power(r,p),r),
             "private field image");
    }
    auto wrong=images;
    for(size_t u=0;u<selected.variables.size();u++) for(size_t j=0;j<selected.variables[u].size();j++)
        wrong[selected.variables[u][j]]=ring.variable(retained.variables[u][j]);
    need(ring.substitute(selected.product,wrong)==retained.product,"wrong merge control");
    need(uses(retained.product,retained_ids) && uses(retained.companions[0],retained_ids),
         "merging selected root did not break freshness");
    out<<"{\"record\":\"case\",\"p\":"<<p<<",\"accuracy\":"<<h<<",\"inner\":";
    write_block(out,inner);out<<",\"retained_root\":";write_block(out,retained);
    out<<",\"other_inner\":";write_block(out,other_inner);
    out<<",\"selected_root\":";write_block(out,selected);
    out<<",\"private_image\":";write_block(out,private_image);
    out<<",\"surviving_inputs_agree_literally\":true,\"selected_root_remains_private\":true,"
           "\"old_target_fresh\":true,\"retained_axioms_fresh\":true,"
           "\"merging_selected_root_breaks_freshness\":true}\n";
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");
        auto parent=std::filesystem::path(argv[2]).parent_path();
        if(!parent.empty()) std::filesystem::create_directories(parent);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"private_survivor_sharing\",\"seed\":null}\n";
        for(int p:{2,3,5,7}) for(int h:{1,2}) run(out,p,h);
        out<<"{\"record\":\"summary\",\"cases\":8,\"all_passed\":true}\n";
        out.close();need(bool(out),"write output failed");
        std::cout<<"Eight shared-descendant/private-root cases and bad-merge controls passed.\n";
    } catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}
}
