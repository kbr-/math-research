// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact exterior-algebra coefficient checks; all arithmetic is over F2.
#include "binary_php.hpp"
#include <filesystem>
#include <set>
using namespace binary_php;
using Poly=std::vector<Word>;
Poly sum(const Poly& a,const Poly& b){
    Poly result;
    std::set_symmetric_difference(a.begin(),a.end(),b.begin(),b.end(),
                                 std::back_inserter(result));
    return result;
}
Poly wedge_variable(const Poly& p,int variable){
    Poly result;
    for(Word m:p)if(!(m&(Word(1)<<variable)))result.push_back(m|(Word(1)<<variable));
    return result;
}
Poly volume(int ell,int a,int b,int degree){
    Poly result{0};
    for(int t=0;t<degree;++t)
        result=sum(wedge_variable(result,a*ell+t),wedge_variable(result,b*ell+t));
    return result;
}
template<class T>void array(std::ostream& out,const std::vector<T>& values){
    out<<'[';
    for(std::size_t i=0;i<values.size();++i){
        if(i)out<<',';
        out<<values[i];
    }
    out<<']';
}
void xor_bits(Bits& a,const Bits& b){
    need(a.size()==b.size(),"tag width");
    for(std::size_t i=0;i<a.size();++i)a[i]^=b[i];
}
Bits linear_bits(Word value,int width){
    Bits result=blank(width);
    for(int i=0;i<width;++i)if((value>>i)&1)flip(result,i);
    return result;
}
void kernel_case(const std::string& name,int ell,const Poly& multiplier,
                 const std::vector<Poly>& allowed,const std::vector<Word>& expected,
                 std::ostream& out){
    int variables=4*ell;
    std::vector<Poly> columns;
    std::set<Word> coordinates;
    for(const Poly& p:allowed)coordinates.insert(p.begin(),p.end());
    for(int v=0;v<variables;++v){
        columns.push_back(wedge_variable(multiplier,v));
        coordinates.insert(columns.back().begin(),columns.back().end());
    }
    std::vector<Word> monomials(coordinates.begin(),coordinates.end());
    need(!monomials.empty(),"empty output space");
    int width=int(monomials.size());
    std::unordered_map<Word,int> index;
    for(int i=0;i<width;++i)index.emplace(monomials[i],i);
    auto encode=[&](const Poly& p){
        Bits b=blank(width);
        for(Word monomial:p)flip(b,index.at(monomial));
        return b;
    };
    out<<"{\"type\":\"case\",\"name\":\""<<name<<"\",\"ell\":"<<ell
       <<",\"variables\":"<<variables<<",\"multiplier\":";
    array(out,multiplier);out<<",\"output_monomials\":";array(out,monomials);
    out<<",\"expected_linear_kernel\":";array(out,expected);out<<"}\n";
    Space base(width),expected_space(variables);
    for(Word row:expected)expected_space.add(linear_bits(row,variables));
    for(std::size_t i=0;i<allowed.size();++i){
        Bits raw=encode(allowed[i]);std::vector<int> trace;
        Bits reduced=base.reduce(raw,&trace);int pivot=highest(reduced);
        if(pivot>=0)base.insert_reduced(reduced,pivot);
        out<<"{\"type\":\"allowed\",\"generator\":"<<i<<",\"raw\":";
        sparse_json(out,raw);out<<",\"trace\":";array(out,trace);
        out<<",\"pivot\":"<<pivot<<",\"reduced\":";sparse_json(out,reduced);out<<"}\n";
    }
    Space image(width),kernel(variables);
    std::vector<Bits> tags(width);
    for(int v=0;v<variables;++v){
        Bits raw=encode(columns[v]),tag=blank(variables);flip(tag,v);
        std::vector<int> base_trace,image_trace;
        Bits reduced=base.reduce(raw,&base_trace);
        reduced=image.reduce(reduced,&image_trace);
        for(int p:image_trace)xor_bits(tag,tags[p]);
        int pivot=highest(reduced);
        if(pivot>=0){
            image.insert_reduced(reduced,pivot);tags[pivot]=tag;
        }else{
            need(zero(expected_space.reduce(tag)),"unexpected linear kernel vector");
            kernel.add(tag);
        }
        out<<"{\"type\":\"column\",\"variable\":"<<v<<",\"raw\":";
        sparse_json(out,raw);out<<",\"allowed_trace\":";array(out,base_trace);
        out<<",\"image_trace\":";array(out,image_trace);
        out<<",\"pivot\":"<<pivot<<",\"reduced\":";sparse_json(out,reduced);
        out<<",\"source_combination\":";sparse_json(out,tag);out<<"}\n";
    }
    need(kernel.rank==expected_space.rank,"wrong linear kernel dimension");
    need(image.rank+kernel.rank==variables,"rank-nullity");
    out<<"{\"type\":\"case_summary\",\"name\":\""<<name
       <<"\",\"ell\":"<<ell<<",\"allowed_rank\":"<<base.rank
       <<",\"image_rank\":"<<image.rank<<",\"kernel_dimension\":"<<kernel.rank<<"}\n";
}
int main(int argc,char** argv){
    try{
        need(argc==3&&std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];
        need(!std::filesystem::exists(path),"refusing existing output");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot create output");
        out<<"{\"type\":\"schema\",\"version\":1,\"field\":2,\"rows\":4,"
               "\"algebra\":\"commuting square-zero variables, the associated graded Boolean algebra\","
               "\"variable_order\":\"row*ell+bit\",\"scope\":\"leading coefficients, not PHP NS matrices\"}\n";
        std::vector<std::pair<int,int>> edges;
        for(int a=0;a<4;++a)for(int b=a+1;b<4;++b)edges.emplace_back(a,b);
        int cases=0;
        for(int ell=3;ell<=5;++ell){
            std::vector<Poly> equalities;
            for(auto [a,b]:edges)equalities.push_back(volume(ell,a,b,ell));
            for(int graph=1;graph<64;++graph){
                Poly multiplier;std::vector<Word> expected;
                for(int e=0;e<6;++e)if((graph>>e)&1)multiplier=sum(multiplier,equalities[e]);
                if(__builtin_popcount(unsigned(graph))==1){
                    auto [a,b]=edges[__builtin_ctz(unsigned(graph))];
                    for(int t=0;t<ell;++t)
                        expected.push_back((Word(1)<<(a*ell+t))|(Word(1)<<(b*ell+t)));
                }
                kernel_case("graph-"+std::to_string(ell)+"-"+std::to_string(graph),
                            ell,multiplier,{},expected,out);++cases;
            }
            std::vector<Word> expected;
            for(int t=0;t<ell;++t)expected.push_back((Word(1)<<t)|(Word(1)<<(ell+t)));
            kernel_case("tight-rank-"+std::to_string(ell),ell,
                        volume(ell,0,1,ell-1),equalities,expected,out);++cases;
        }
        Poly exceptional;
        for(auto [a,b]:edges)exceptional=sum(exceptional,volume(2,a,b,2));
        std::vector<Word> expected;
        for(int t=0;t<2;++t){
            Word row=0;
            for(int a=0;a<4;++a)row|=Word(1)<<(a*2+t);
            expected.push_back(row);
        }
        kernel_case("width-two-complete-graph-control",2,exceptional,{},expected,out);++cases;
        need(cases==193,"case count");
        out<<"{\"type\":\"summary\",\"graph_cases\":189,\"tight_rank_cases\":3,"
               "\"excluded_width_controls\":1,\"cases\":193,\"passed\":true}\n";
        out.close();need(bool(out),"write failed");
        std::cout<<"Passed 189 complete four-row graph kernels, three tight-rank cases, "
                    "and the excluded width-two complete-graph control.\n";
    }catch(const std::exception& error){std::cerr<<"ERROR: "<<error.what()<<'\n';return 1;}
}
