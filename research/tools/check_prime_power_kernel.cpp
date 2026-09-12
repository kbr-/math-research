// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Compare the prime-power fast path with independent repeated multiplication.
#include "pc_boundary.hpp"
using namespace boundary_pc;

Poly reference_power(const Poly& a,int e) {
    need(e>=0,"negative reference exponent");Poly value(a.p,1);
    for(int k=0;k<e;k++)value=value*a;
    return value;
}
bool exponent_failure(const Poly& a,bool reference) {
    try {
        if(reference)reference_power(a,a.p);
        else powp(a,a.p);
    }catch(const std::runtime_error& e){return std::string(e.what())=="exponent guard";}
    return false;
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","usage: check_prime_power_kernel --out PATH");
        std::string path=argv[2];need(!std::ifstream(path).good(),"refusing to overwrite output");
        std::ofstream out(path);need(out.good(),"cannot open output");
        int comparisons=0,guards=0;
        out<<"{\"record\":\"schema\",\"version\":1,\"scope\":\"ordinary prime-field polynomials; no variable-domain reductions\"}\n";
        auto compare=[&](const std::string& name,const Poly& input,int exponent) {
            Poly got=powp(input,exponent),expected=reference_power(input,exponent);
            need(got==expected,"prime-power/reference mismatch");
            if(exponent==input.p && input.deg()>0)
                need(got.deg()==input.p*input.deg(),"ordinary prime-power degree changed");
            out<<"{\"record\":\"comparison\",\"name\":\""<<name<<"\",\"p\":"<<input.p
               <<",\"exponent\":"<<exponent<<",\"input\":";jsonpoly(out,input);
            out<<",\"result\":";jsonpoly(out,got);
            out<<",\"reference_equal\":true,\"ordinary_degree\":"<<got.deg()<<"}\n";comparisons++;
        };
        for(int p:{2,3,5,7}) {
            Poly one(p,1),x=variable(p,0),y=variable(p,1),z=variable(p,2);
            std::vector<Poly> fixtures={Poly(p),Poly(p,-1),one+x+y,
                x*y+Poly(p,2)*x-y+one,x*x*y+y*z-z+one};
            for(size_t i=0;i<fixtures.size();i++)
                compare("prime_fixture_"+std::to_string(i),fixtures[i],p);
            std::vector<int> other={0,1,p-1,p+1};
            std::sort(other.begin(),other.end());other.erase(std::unique(other.begin(),other.end()),other.end());
            for(int e:other)compare("unchanged_generic_power",fixtures.back(),e);
            Mon mon{};mon[0]=255/p;Poly boundary(p);boundary.add(mon,1);
            compare("largest_accepted_univariate_exponent",boundary,p);
            mon[0]=255/p+1;Poly overflow(p);overflow.add(mon,1);
            need(exponent_failure(overflow,false) && exponent_failure(overflow,true),"exponent guard changed");
            out<<"{\"record\":\"guard\",\"p\":"<<p
               <<",\"input_exponent\":"<<int(mon[0])
               <<",\"optimized_rejected\":true,\"reference_rejected\":true}\n";guards++;
        }
        bool negative=false;
        try{powp(variable(3,0),-1);}
        catch(const std::runtime_error& e){negative=std::string(e.what())=="negative exponent";}
        need(negative,"negative exponent was not rejected");guards++;
        out<<"{\"record\":\"guard\",\"negative_exponent_rejected\":true}\n";
        out<<"{\"record\":\"summary\",\"comparisons\":"<<comparisons<<",\"guard_cases\":"<<guards
           <<",\"all_passed\":true}\n";
        out.flush();need(out.good(),"output failure");
        std::cout<<"Passed "<<comparisons<<" polynomial comparisons and "<<guards
                 <<" guard cases; output "<<path<<"\n";return 0;
    }catch(const std::exception& e){std::cerr<<"ERROR: "<<e.what()<<"\n";return 1;}
}
