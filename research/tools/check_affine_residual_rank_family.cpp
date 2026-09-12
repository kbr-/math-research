// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact F2 witness: eight rank-three spaces, every 6-by-5 residual subboard.
#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

constexpr int ROWS=9, COLS=8, KEEP_ROWS=6, KEEP_COLS=5, BLOCKS=8, RANK=3;
using Word=std::uint32_t;
using Input=std::array<unsigned char,ROWS>;
using Family=std::array<std::array<Input,RANK>,BLOCKS>;
using Residual=std::array<std::array<Word,RANK>,BLOCKS>;

void require(bool condition,const std::string& message) {
    if(!condition) throw std::runtime_error(message);
}
int rank_of(const std::vector<Word>& rows) {
    std::array<Word,32> pivots{};
    int rank=0;
    for(Word x:rows) {
        while(x) {
            const int bit=31-__builtin_clz(x);
            if(pivots[bit]) x^=pivots[bit];
            else {pivots[bit]=x; ++rank; break;}
        }
    }
    return rank;
}
std::vector<Word> row_axioms() {
    std::vector<Word> rows;
    for(int i=0;i<KEEP_ROWS;++i)
        rows.push_back(((Word(1)<<KEEP_COLS)-1)<<(i*KEEP_COLS));
    return rows;
}
Residual restrict_linear_parts(const Family& family,int row_mask,int col_mask) {
    Residual result{};
    int ii=0;
    for(int i=0;i<ROWS;++i) if((row_mask>>i)&1) {
        int jj=0;
        for(int j=0;j<COLS;++j) if((col_mask>>j)&1) {
            for(int a=0;a<BLOCKS;++a) for(int k=0;k<RANK;++k)
                if((family[a][k][i]>>j)&1)
                    result[a][k] |= Word(1)<<(ii*KEEP_COLS+jj);
            ++jj;
        }
        ++ii;
    }
    return result;
}
template<class Rows> void words(std::ostream& out,const Rows& rows) {
    out<<'[';
    bool first=true;
    for(auto x:rows) {if(!first) out<<','; first=false; out<<std::uint64_t(x);}
    out<<']';
}
void family_record(std::ostream& out,const Family& family,int draw) {
    out<<"{\"record\":\"matrix_draw\",\"draw\":"<<draw<<",\"input_row_masks\":[";
    for(int a=0;a<BLOCKS;++a) {
        if(a) out<<',';
        out<<'[';
        for(int k=0;k<RANK;++k) {if(k) out<<','; words(out,family[a][k]);}
        out<<']';
    }
    out<<"]}\n";
}
bool verify_draw(std::ostream& out,const Family& family,int draw) {
    const auto base=row_axioms();
    int boards=0,pairs=0;
    for(int rm=0;rm<(1<<ROWS);++rm) if(__builtin_popcount(unsigned(rm))==KEEP_ROWS)
      for(int cm=0;cm<(1<<COLS);++cm) if(__builtin_popcount(unsigned(cm))==KEEP_COLS) {
        const auto image=restrict_linear_parts(family,rm,cm);
        std::vector<int> single_ranks,pair_ranks;
        for(int a=0;a<BLOCKS;++a) {
            auto rows=base;
            rows.insert(rows.end(),image[a].begin(),image[a].end());
            single_ranks.push_back(rank_of(rows)-KEEP_ROWS);
        }
        for(int a=0;a<BLOCKS;++a) for(int b=a+1;b<BLOCKS;++b) {
            auto rows=base;
            rows.insert(rows.end(),image[a].begin(),image[a].end());
            rows.insert(rows.end(),image[b].begin(),image[b].end());
            const int rank=rank_of(rows)-KEEP_ROWS;
            ++pairs; pair_ranks.push_back(rank);
            if(rank!=2*RANK) {
                out<<"{\"record\":\"rejected_draw\",\"draw\":"<<draw
                   <<",\"row_mask\":"<<rm<<",\"column_mask\":"<<cm
                   <<",\"pair\":["<<a<<','<<b<<"],\"quotient_rank\":"<<rank<<"}\n";
                return false;
            }
        }
        for(int rank:single_ranks) require(rank==RANK,"Pair test failed to imply single rank");
        if(boards==0) {
            auto duplicate=base;
            duplicate.insert(duplicate.end(),image[0].begin(),image[0].end());
            duplicate.insert(duplicate.end(),image[0].begin(),image[0].end());
            require(rank_of(duplicate)-KEEP_ROWS==RANK,"Duplicated-block negative control");
            out<<"{\"record\":\"duplicate_block_control\",\"draw\":"<<draw
               <<",\"observed_quotient_rank\":"<<RANK
               <<",\"required_pair_rank\":"<<2*RANK<<",\"rejected\":true}\n";
        }
        ++boards;
        out<<"{\"record\":\"residual_board\",\"draw\":"<<draw
           <<",\"row_mask\":"<<rm<<",\"column_mask\":"<<cm
           <<",\"input_linear_parts\":[";
        for(int a=0;a<BLOCKS;++a) {if(a) out<<','; words(out,image[a]);}
        out<<"],\"block_quotient_ranks\":"; words(out,single_ranks);
        out<<",\"pair_quotient_ranks\":"; words(out,pair_ranks);
        out<<"}\n";
    }
    require(boards==4704 && pairs==131712,"Exhaustive fixture counts");
    out<<"{\"record\":\"accepted_draw\",\"draw\":"<<draw
       <<",\"residual_boards\":"<<boards<<",\"block_checks\":"<<boards*BLOCKS
       <<",\"pair_checks\":"<<pairs
       <<",\"covered_partial_matchings\":28224,\"checks_passed\":true}\n";
    return true;
}
int main(int argc,char** argv) {
    try {
        require(argc==3 || argc==5,"Usage: checker --out NEW.jsonl [--seed INTEGER]");
        require(std::string(argv[1])=="--out","Expected --out");
        std::uint64_t seed=20260912;
        if(argc==5) {
            require(std::string(argv[3])=="--seed","Expected --seed");
            seed=std::stoull(argv[4]);
        }
        const std::filesystem::path path(argv[2]);
        require(!std::filesystem::exists(path),"Refusing to overwrite output");
        if(!path.parent_path().empty()) std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);
        require(bool(out),"Cannot open output");
        out<<"{\"record\":\"metadata\",\"schema\":1,\"field\":2,\"n\":8,\"N\":5,"
              "\"blocks\":8,\"rank\":3,\"q\":3,\"seed\":"<<seed
           <<",\"generator\":\"std::mt19937_64\","
              "\"source_encoding\":\"nine row masks per input; bit j is x_ij coefficient\","
              "\"residual_encoding\":\"bit 5*i+j in increasing retained row/column order\","
              "\"pair_order\":\"lexicographic (a,b) with a<b\","
              "\"existence_union_numerator\":8297856,"
              "\"existence_union_denominator\":16777216,\"base_row_linear_parts\":";
        words(out,row_axioms()); out<<"}\n";
        std::mt19937_64 rng(seed);
        for(int draw=1;draw<=32;++draw) {
            Family family{};
            for(auto& block:family) for(auto& input:block) for(auto& row:input)
                row=static_cast<unsigned char>(rng()&255);
            family_record(out,family,draw);
            if(!verify_draw(out,family,draw)) continue;
            out.close(); require(bool(out),"Output write failed");
            std::cout<<"Draw "<<draw<<": all 4704 residual boards, 37632 block ranks, "
                       "and 131712 pair ranks verified; duplicate control rejected.\n";
            return 0;
        }
        throw std::runtime_error("No witness found in 32 draws; all attempted evidence retained");
    } catch(const std::exception& error) {
        std::cerr<<error.what()<<'\n';
        return 1;
    }
}
