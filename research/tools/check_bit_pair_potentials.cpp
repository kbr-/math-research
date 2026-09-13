// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact two-row bit polynomial quotients by off-diagonal row/column potentials.
#include "binary_php.hpp"
#include <filesystem>
using namespace binary_php;
void integers(std::ostream& out,const std::vector<int>& values){
    out<<'[';for(std::size_t i=0;i<values.size();++i){if(i)out<<',';out<<values[i];}out<<']';
}
void xor_bits(Bits& a,const Bits& b){
    need(a.size()==b.size(),"tag width");for(std::size_t i=0;i<a.size();++i)a[i]^=b[i];
}
void check(int ell,bool both,std::ostream& out){
    int n=1<<ell,width=n*(n-1);
    std::vector<std::pair<int,int>> pairs;
    for(int z=0;z<n;++z)for(int w=0;w<n;++w)if(z!=w)pairs.emplace_back(z,w);
    std::vector<int> monomials;
    for(int mask=1;mask<(1<<(2*ell));++mask)
        if((mask&(n-1))&&(mask>>ell)&&__builtin_popcount(unsigned(mask))<=ell)
            monomials.push_back(mask);
    int source_width=int(monomials.size());
    out<<"{\"type\":\"case\",\"ell\":"<<ell<<",\"both_potentials\":"
       <<(both?"true":"false")<<",\"pairs\":[";
    for(std::size_t i=0;i<pairs.size();++i){
        if(i)out<<',';
        out<<'['<<pairs[i].first<<','<<pairs[i].second<<']';
    }
    out<<"],\"source_monomials\":";integers(out,monomials);out<<"}\n";
    Space base(width);
    for(int side=0;side<(both?2:1);++side)for(int label=0;label<n;++label){
        Bits raw=blank(width);
        for(int i=0;i<width;++i)
            if((side==0?pairs[i].first:pairs[i].second)==label)flip(raw,i);
        std::vector<int> trace;Bits reduced=base.reduce(raw,&trace);int pivot=highest(reduced);
        if(pivot>=0)base.insert_reduced(reduced,pivot);
        out<<"{\"type\":\"potential\",\"side\":"<<side<<",\"label\":"<<label
           <<",\"raw\":";sparse_json(out,raw);out<<",\"trace\":";integers(out,trace);
        out<<",\"pivot\":"<<pivot<<",\"reduced\":";sparse_json(out,reduced);out<<"}\n";
    }
    need(base.rank==(both?2*n-1:n),"potential rank");
    Space image(width);
    std::vector<Bits> tags(width);
    Bits equality=blank(source_width);
    for(int i=0;i<source_width;++i){
        int left=monomials[i]&(n-1),right=monomials[i]>>ell;
        if(!(left&right))flip(equality,i);
    }
    int kernels=0;
    for(int s=0;s<source_width;++s){
        int left=monomials[s]&(n-1),right=monomials[s]>>ell;
        Bits raw=blank(width),tag=blank(source_width);flip(tag,s);
        for(int i=0;i<width;++i){
            auto [z,w]=pairs[i];
            if((z&left)==left&&(w&right)==right)flip(raw,i);
        }
        std::vector<int> base_trace,image_trace;
        Bits remainder=base.reduce(raw,&base_trace);
        remainder=image.reduce(remainder,&image_trace);
        for(int pivot:image_trace)xor_bits(tag,tags[pivot]);
        int pivot=highest(remainder);
        if(pivot>=0){
            image.insert_reduced(remainder,pivot);tags[pivot]=tag;
        }else{
            ++kernels;
            need(both&&tag==equality,"unexpected mixed-polynomial kernel");
        }
        out<<"{\"type\":\"source\",\"source\":"<<s<<",\"monomial\":"<<monomials[s]
           <<",\"raw\":";sparse_json(out,raw);
        out<<",\"potential_trace\":";integers(out,base_trace);
        out<<",\"image_trace\":";integers(out,image_trace);
        out<<",\"pivot\":"<<pivot<<",\"reduced\":";sparse_json(out,remainder);
        out<<",\"source_combination\":";sparse_json(out,tag);out<<"}\n";
    }
    need(kernels==(both?1:0),"kernel dimension");
    need(image.rank==source_width-kernels,"image rank");
    out<<"{\"type\":\"case_summary\",\"ell\":"<<ell
       <<",\"both_potentials\":"<<(both?"true":"false")
       <<",\"potential_rank\":"<<base.rank<<",\"source_dimension\":"<<source_width
       <<",\"image_rank\":"<<image.rank<<",\"kernel_dimension\":"<<kernels
       <<",\"equality_cross_part\":";sparse_json(out,equality);out<<"}\n";
    std::cout<<"ell="<<ell<<", row+column="<<both<<": rank "
             <<image.rank<<'/'<<source_width<<", kernel "<<kernels<<'\n';
}
int main(int argc,char** argv){
    try{
        need(argc==3&&std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];
        need(!std::filesystem::exists(path),"refusing existing output");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot create output");
        out<<"{\"type\":\"schema\",\"version\":1,\"field\":2,"
               "\"scope\":\"two-row coefficient space, not the whole PHP NS quotient\","
               "\"monomial_bits\":\"low ell bits are row z; next ell bits are row w\"}\n";
        for(int ell=2;ell<=6;++ell)check(ell,true,out);
        check(3,false,out);
        out<<"{\"type\":\"summary\",\"cases\":6,\"passed\":true}\n";
        out.close();need(bool(out),"write failed");
    }catch(const std::exception& error){std::cerr<<"ERROR: "<<error.what()<<'\n';return 1;}
}
