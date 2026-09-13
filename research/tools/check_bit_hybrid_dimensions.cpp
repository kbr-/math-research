// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact dimension and degree tests for mixed affine packing/learning.
#include <boost/multiprecision/cpp_int.hpp>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using boost::multiprecision::cpp_int;
using U64=std::uint64_t;
struct Case{std::string name;U64 n,M,h,D,k;bool dimension,degree;};
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
void check(const Case& c,std::ostream& out){
    need(c.n>=4 && (c.n&(c.n-1))==0,"power-of-two board");
    U64 ell=__builtin_ctzll(c.n),m=c.n+1,v=m*ell;
    U64 low_rank=c.h*(c.k+1),high_rank=low_rank+1;
    need(high_rank<=v && c.D>=2*c.h+1 && c.k>0,"parameter guard");
    U64 remaining=v-high_rank,B=c.k*(c.D+1);
    cpp_int row_term=1,flat_term=1,ambient_term=1;
    cpp_int row_space=1,flat_space=1,ambient=1;
    for(U64 j=1;j<=c.k;++j){
        row_term=row_term*(m-j+1)*ell/j;
        flat_term=j<=remaining?cpp_int(flat_term*(remaining-j+1)/j):cpp_int(0);
        ambient_term=ambient_term*(v-j+1)/j;
        row_space+=row_term;flat_space+=flat_term;ambient+=ambient_term;
    }
    cpp_int upper=c.M*flat_space;
    bool dimension=upper<row_space;
    bool degree=c.n>=2*B-1;
    bool cubes=4*(c.k-1)<c.n;
    need(dimension==c.dimension && degree==c.degree,"unexpected criterion result: "+c.name);
    out<<"{\"type\":\"case\",\"name\":\""<<c.name<<"\",\"n\":"<<c.n
       <<",\"ell\":"<<ell<<",\"bit_variables\":"<<v<<",\"inventory_upper\":"<<c.M
       <<",\"accuracy\":"<<c.h<<",\"source_degree\":"<<c.D
       <<",\"predicate_degree\":"<<c.k<<",\"normalizer_degree\":"<<c.k
       <<",\"packed_rank_ceiling\":"<<low_rank
       <<",\"high_rank_lower_bound\":"<<high_rank<<",\"old_degree_ceiling\":"<<B
       <<",\"row_linear_dimension\":\""<<row_space
       <<"\",\"one_high_flat_restriction_bound\":\""<<flat_space
       <<"\",\"all_high_flat_restriction_bound\":\""<<upper
       <<"\",\"full_Boolean_dimension\":\""<<ambient
       <<"\",\"dimension_margin\":\""<<row_space-upper
       <<"\",\"dimension_condition\":"<<(dimension?"true":"false")
       <<",\"degree_condition\":"<<(degree?"true":"false")
       <<",\"cube_condition\":"<<(cubes?"true":"false")
       <<",\"exclusion\":"<<(dimension&&degree&&cubes?"true":"false")<<"}\n";
    std::cout<<c.name<<": k="<<c.k<<", B="<<B<<", dimension="<<dimension
             <<", degree="<<degree<<", cube="<<cubes<<'\n';
}
int main(int argc,char** argv){
    try{
        need(argc==3&&std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];
        need(!std::filesystem::exists(path),"refusing existing output");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot create output");
        out<<"{\"type\":\"schema\",\"version\":1,\"field\":2,"
               "\"scope\":\"exact dimension inequalities, not instantiated large PHP matrices\","
               "\"large_integers\":\"decimal strings\",\"randomness\":\"none\"}\n";
        std::vector<Case> cases={
            {"active-companions",U64(1)<<20,U64(1)<<20,40,81,4096,true,true},
            {"beyond-four-h",U64(1)<<22,U64(1)<<22,44,200,9216,true,true},
            {"predicate-too-small",U64(1)<<22,U64(1)<<22,44,200,1024,false,true},
            {"old-degree-too-large",U64(1)<<22,U64(1)<<22,44,227,9216,true,false},
        };
        for(const auto& c:cases)check(c,out);
        out<<"{\"type\":\"summary\",\"cases\":4,\"positive\":2,\"controls\":2,\"passed\":true}\n";
        out.close();need(bool(out),"write failed");
    }catch(const std::exception& error){std::cerr<<"ERROR: "<<error.what()<<'\n';return 1;}
}
