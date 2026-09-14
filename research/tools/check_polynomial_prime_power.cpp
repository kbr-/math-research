// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Small independent repeated-multiplication checks for the shared power routine.
#include "sparse_polynomial.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace sparse_polynomial;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");int cases=0;
        for(int p:{2,3,5,7}){
            Ring r(p,64);auto x=r.variable(0),y=r.variable(1),z=r.variable(2);
            auto f=r.add(r.add(r.power(x,2),r.multiply(r.constant(p-1),r.multiply(y,z))),
                         r.add(z,r.constant(2)));
            for(int e:{p-1,p,p+1}){
                auto actual=r.power(f,e),reference=r.constant(1);
                for(int j=0;j<e;++j)reference=r.multiply(reference,f);
                need(actual==reference,"independent repeated multiplication");
                out<<"{\"record\":\"power_case\",\"field\":"<<p<<",\"exponent\":"<<e
                   <<",\"input\":";write_json(out,f);out<<",\"output\":";write_json(out,actual);
                out<<",\"degree\":"<<degree(actual)<<",\"reference_agrees\":true}\n";++cases;
            }
            for(int value:{0,2}){
                auto f0=r.constant(value),actual=r.power(f0,p),reference=r.constant(1);
                for(int j=0;j<p;++j)reference=r.multiply(reference,f0);
                need(actual==reference,"zero/constant power");
                out<<"{\"record\":\"constant_case\",\"field\":"<<p<<",\"input\":";write_json(out,f0);
                out<<",\"output\":";write_json(out,actual);out<<"}\n";++cases;
            }
            auto ordinary=r.power(x,p);
            need(ordinary!=x && degree(ordinary)==p,"ordinary power was Boolean/field reduced");
            bool degree_rejected=false,negative_rejected=false;
            try{Ring small(p,p-1);(void)small.power(small.variable(0),p);}
            catch(const std::runtime_error&){degree_rejected=true;}
            try{(void)r.power(f,-1);}
            catch(const std::runtime_error&){negative_rejected=true;}
            need(degree_rejected && negative_rejected,"power guards");
            out<<"{\"record\":\"guard_controls\",\"field\":"<<p<<",\"ordinary_power\":";
            write_json(out,ordinary);
            out<<",\"degree_limit_rejected\":true,\"negative_exponent_rejected\":true}\n";
        }
        need(cases==20,"case count");
        out<<"{\"record\":\"summary\",\"power_cases\":"<<cases<<",\"guard_groups\":4,\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<"20 exact power comparisons and four ordinary-degree/guard controls passed.\n";
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
