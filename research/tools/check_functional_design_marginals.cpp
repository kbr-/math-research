// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact NS moment spaces for functional PHP; no PC closure is performed.
#include "binary_php.hpp"
#include <filesystem>
#include <random>
using namespace binary_php;

struct MomentBoard {
    int n,m,variables,degree,width,low;
    std::vector<Word> monomials;
    std::unordered_map<Word,int> index;
    explicit MomentBoard(int holes,int d):n(holes),m(n+1),variables(n*m),degree(d) {
        need(n>=3 && n<=7 && (d==2 || d==3),"Fixed degree-two/three fixture range");
        monomials.push_back(0);
        for(int a=0;a<variables;++a) monomials.push_back(Word(1)<<a);
        for(int a=0;a<variables;++a) for(int b=a+1;b<variables;++b)
            if(a/n!=b/n && a%n!=b%n)
                monomials.push_back((Word(1)<<a)|(Word(1)<<b));
        low=int(monomials.size());
        if(d==3)
            for(int a=0;a<variables;++a) for(int b=a+1;b<variables;++b) {
                if(a/n==b/n || a%n==b%n) continue;
                for(int c=b+1;c<variables;++c)
                    if(c/n!=a/n && c/n!=b/n && c%n!=a%n && c%n!=b%n)
                        monomials.push_back((Word(1)<<a)|(Word(1)<<b)|(Word(1)<<c));
            }
        width=int(monomials.size()); index.reserve(width*2);
        for(int j=0;j<width;++j)
            need(index.emplace(monomials[j],j).second,"Duplicate matching monomial");
    }
    std::pair<unsigned,unsigned> used(Word monomial) const {
        unsigned rows=0,cols=0;
        while(monomial) {
            int v=__builtin_ctzll(monomial); monomial&=monomial-1;
            rows|=1u<<(v/n); cols|=1u<<(v%n);
        }
        return {rows,cols};
    }
    Bits row_relation(int monomial,int row) const {
        auto [rows,cols]=used(monomials[monomial]);
        need(!(rows&(1u<<row)),"Assigned row gives the zero relation");
        Bits result=blank(width); flip(result,monomial);
        for(int j=0;j<n;++j) if(!(cols&(1u<<j)))
            flip(result,index.at(monomials[monomial]|(Word(1)<<(row*n+j))));
        return result;
    }
};
void integers(std::ostream& out,const std::vector<int>& values) {
    out<<'[';
    for(size_t i=0;i<values.size();++i) {if(i)out<<',';out<<values[i];}
    out<<']';
}
void hexword(std::ostream& out,Word value) {
    auto flags=out.flags();out<<'"'<<std::hex<<value<<'"';out.flags(flags);
}
void packed(std::ostream& out,const Bits& values) {
    out<<'[';
    for(size_t i=0;i<values.size();++i) {if(i)out<<',';hexword(out,values[i]);}
    out<<']';
}
int covariance_rank(const MomentBoard& board,const Bits& values) {
    std::vector<int> means(board.variables);
    for(int a=0;a<board.variables;++a)
        means[a]=bit(values,board.index.at(Word(1)<<a));
    std::vector<Word> covariance(board.variables,0);
    for(int a=0;a<board.variables;++a) for(int b=0;b<board.variables;++b) {
        Word mask=(Word(1)<<a)|(Word(1)<<b);
        auto found=board.index.find(mask);
        int moment=found==board.index.end()?0:int(bit(values,found->second));
        if(moment^(means[a]&means[b])) covariance[a]|=Word(1)<<b;
    }
    Space rank_space(board.variables);
    for(int a=0;a<board.variables;++a) {
        need(!(covariance[a]&(Word(1)<<a)),"Covariance diagonal");
        for(int b=0;b<board.variables;++b)
            need(((covariance[a]>>b)&1)==((covariance[b]>>a)&1),"Covariance symmetry");
        for(int i=0;i<board.m;++i) {
            Word row_mask=((Word(1)<<board.n)-1)<<(i*board.n);
            need(!__builtin_parityll(covariance[a]&row_mask),"Row sums in covariance kernel");
        }
        Bits row=blank(board.variables); row[0]=covariance[a];rank_space.add(std::move(row));
    }
    need(rank_space.rank%2==0,"Alternating binary rank must be even");
    return rank_space.rank;
}
struct Summary {bool consistent;int dimension,quadratic_dimension;};
Summary run_case(std::ostream& out,int n,int degree,std::mt19937_64& rng) {
    MomentBoard board(n,degree);Space equations(board.width);
    out<<"{\"record\":\"case\",\"n\":"<<n<<",\"degree\":"<<degree
       <<",\"variables\":"<<board.variables<<",\"moments\":"<<board.width
       <<",\"quadratic_moments\":"<<board.low<<",\"monomial_masks\":[";
    for(int i=0;i<board.width;++i) {if(i)out<<',';hexword(out,board.monomials[i]);}
    out<<"]}\n";
    std::vector<std::pair<int,int>> originals;
    for(int mon=0;mon<board.width;++mon) {
        if(__builtin_popcountll(board.monomials[mon])>=degree) continue;
        const auto masks=board.used(board.monomials[mon]);
        for(int row=0;row<board.m;++row) if(!(masks.first&(1u<<row))) {
            std::vector<int> trace;
            const int pivot=equations.add(board.row_relation(mon,row),&trace);
            originals.push_back({mon,row});
            out<<"{\"record\":\"elimination\",\"n\":"<<n<<",\"degree\":"<<degree
               <<",\"monomial\":"<<mon<<",\"row\":"<<row<<",\"pivot\":"<<pivot
               <<",\"xor_previous_pivots\":";integers(out,trace);
            out<<",\"reduced_row\":";
            if(pivot<0) out<<"[]";else sparse_json(out,equations.rows[pivot]);
            out<<"}\n";
        }
    }
    for(auto [mon,row]:originals)
        need(zero(equations.reduce(board.row_relation(mon,row))),"Original relation not spanned");
    int low_rank=0;
    for(int p=0;p<board.low;++p) if(!equations.rows[p].empty()) ++low_rank;
    const bool consistent=equations.rows[0].empty();
    const int dimension=board.width-equations.rank-1;
    const int projected=board.low-low_rank-1;
    out<<"{\"record\":\"space_summary\",\"n\":"<<n<<",\"degree\":"<<degree
       <<",\"original_equations\":"<<originals.size()<<",\"NS_row_rank\":"<<equations.rank
       <<",\"quadratic_equation_rank\":"<<low_rank<<",\"consistent\":"<<(consistent?"true":"false");
    if(consistent) out<<",\"design_dimension\":"<<dimension
                      <<",\"quadratic_projection_dimension\":"<<projected;
    out<<"}\n";
    std::cout<<"n="<<n<<", degree="<<degree<<": moments="<<board.width
             <<", NS rank="<<equations.rank<<", consistent="<<consistent;
    if(consistent)std::cout<<", design dimension="<<dimension<<", quadratic image="<<projected;
    std::cout<<".\n";
    if(degree==2) {
        int expected=n*n-1+(n+1)*n/2*(n*n-3*n+1);
        need(consistent && dimension==expected,"Analytic degree-two dimension");
    }
    if(!consistent) {
        need(highest(equations.rows[0])==0 && bit(equations.rows[0],0),
             "Inconsistency requires the constant-moment equation");
        return {false,-1,-1};
    }
    constexpr int samples=32;
    std::vector<int> histogram(board.variables+1,0);
    Word kernel_sum=0;
    for(int s=0;s<samples;++s) {
        Bits seed=blank(board.width);
        for(int j=1;j<board.width;++j)
            if(equations.rows[j].empty() && (rng()&1)) flip(seed,j);
        flip(seed,0); // Normalize omega(1)=1; this is a free coordinate.
        Bits values=equations.complete_dual(std::move(seed));
        need(bit(values,0),"Lost normalization");
        for(auto [mon,row]:originals)
            need(dot(values,board.row_relation(mon,row))==0,"Sample violates an original row moment");
        int rank=covariance_rank(board,values);
        ++histogram[rank];kernel_sum+=Word(1)<<(board.variables-rank);
        out<<"{\"record\":\"sample\",\"n\":"<<n<<",\"degree\":"<<degree
           <<",\"sample\":"<<s<<",\"covariance_rank\":"<<rank
           <<",\"moment_words\":";packed(out,values);out<<"}\n";
    }
    out<<"{\"record\":\"sample_summary\",\"n\":"<<n<<",\"degree\":"<<degree
       <<",\"samples\":"<<samples<<",\"rank_histogram\":";integers(out,histogram);
    out<<",\"empirical_kernel_weight_numerator\":"<<kernel_sum
       <<",\"empirical_kernel_weight_denominator\":"<<(Word(samples)<<board.variables)
       <<",\"scope\":\"exact values on saved samples; not the exact uniform-space expectation\"}\n";
    return {true,dimension,projected};
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","Usage: checker --out NEW.jsonl");
        std::filesystem::path path(argv[2]);
        need(!std::filesystem::exists(path),"Refusing to overwrite output");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"Cannot open output");
        constexpr Word seed=20260912;
        out<<"{\"record\":\"metadata\",\"schema\":1,\"field\":2,\"base\":\"functional PHP\","
              "\"calculus\":\"NS constraints only; no PC closure\","
              "\"generator\":\"std::mt19937_64\",\"seed\":"<<seed
           <<",\"sample_law\":\"independent free moment coordinates, omega(1)=1\","
              "\"moment_word_order\":\"little-endian 64-bit hexadecimal words\","
              "\"cell_bit\":\"i*n+j with zero-based row i and column j\"}\n";
        std::mt19937_64 rng(seed);
        for(int n:{4,6}) {
            Summary two=run_case(out,n,2,rng),three=run_case(out,n,3,rng);
            if(three.consistent)
                need(three.quadratic_dimension<=two.dimension,"Higher-degree image escaped degree two");
            out<<"{\"record\":\"projection_comparison\",\"n\":"<<n
               <<",\"degree_three_consistent\":"<<(three.consistent?"true":"false")
               <<",\"onto_all_degree_two_designs\":"
               <<(three.consistent && three.quadratic_dimension==two.dimension?"true":"false")<<"}\n";
        }
        out<<"{\"record\":\"summary\",\"checks_passed\":true}\n";
        out.close();need(bool(out),"Output write failed");return 0;
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
