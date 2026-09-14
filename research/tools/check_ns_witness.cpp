// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Corrupted and over-budget witnesses must not pass the shared NS writer.
#include "ns_witness.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
using namespace ns_witness;
void need(bool ok,const char* why){if(!ok)throw std::runtime_error(why);}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");
        for(int p:{2,3}){
            Ring ring(p,20);auto x=ring.variable(0),one=ring.constant(1);
            auto F=ring.subtract(ring.power(x,2),x),xF=ring.multiply(x,F);
            std::vector<Polynomial> axioms={F,F};
            auto accept=[&](const std::string& name,const Polynomial& target,
                            const std::map<int,Polynomial>& cof,int budget,int expected){
                out<<"{\"record\":\"accepted\",\"field\":"<<p<<",\"name\":\""<<name<<"\"";
                need(write_terms(out,ring,axioms,target,cof,budget,name)==expected,"accepted degree");
                out<<"}\n";
            };
            auto reject=[&](const std::string& name,const Polynomial& target,
                            const std::map<int,Polynomial>& cof,int budget){
                std::ostringstream scratch;bool rejected=false;
                try{write_terms(scratch,ring,axioms,target,cof,budget,name);}
                catch(const std::runtime_error&){rejected=true;}
                need(rejected && scratch.str().empty(),"invalid witness accepted or emitted");
                out<<"{\"record\":\"rejected\",\"field\":"<<p<<",\"name\":\""<<name
                   <<"\",\"no_suffix_emitted\":true}\n";
            };
            std::map<int,Polynomial> cancel={{0,x},{1,ring.multiply(ring.constant(-1),x)}};
            accept("ordinary_multiple",xF,{{0,x}},3,3);
            accept("zero_target_with_cancelling_multiples",{},cancel,3,3);
            accept("empty_zero_certificate",{},{},0,0);
            reject("corrupted_cofactor",xF,{{0,ring.add(x,one)}},3);
            reject("ordinary_multiple_over_budget",xF,{{0,x}},2);
            reject("cancellation_does_not_erase_original_cost",{},cancel,2);
        }
        out<<"{\"record\":\"summary\",\"accepted\":6,\"rejected\":6,\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<"Six legal witnesses accepted; six corrupt or over-budget witnesses rejected.\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
