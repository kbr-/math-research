// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Find and certify an F_2 spread embedding resisting every single-cell matching.
// Fixed n=7, m=8, ambient W dimension 48, seven graph spaces of dimension 24.
// Run through compute.sh; outputs include all draws and complete dual witnesses.
#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

using Word=std::uint64_t;
constexpr int N=7,M=8,W=48,R=24,RES=36;
constexpr Word MASK=(Word(1)<<W)-1;
void need(bool ok,const std::string& message){
    if(!ok)throw std::runtime_error(message);
}
struct Basis{
    int width,rank=0;
    std::array<Word,64> rows{};
    explicit Basis(int size):width(size){need(size>0 && size<=64,"bit-width guard");}
    Word reduce(Word value) const{
        for(int i=width-1;i>=0;i--){
            if(((value>>i)&1) && rows[i])value^=rows[i];
        }
        return value;
    }
    bool add(Word value){
        value=reduce(value);
        if(!value)return false;
        int pivot=63-__builtin_clzll(value);
        rows[pivot]=value;rank++;return true;
    }
};
void hexword(std::ostream& out,Word value){
    auto flags=out.flags();out<<'"'<<std::hex<<value<<'"';out.flags(flags);
}
void words_json(std::ostream& out,const std::vector<Word>& values){
    out<<'[';
    for(size_t i=0;i<values.size();i++){
        if(i)out<<',';
        hexword(out,values[i]);
    }
    out<<']';
}
int gf8_multiply(int a,int b){
    int result=0;
    while(b){
        if(b&1)result^=a;
        b>>=1;a<<=1;
        if(a&8)a^=11; // X^3+X+1, irreducible because it has no root in F_2.
    }
    return result;
}
Word graph_input(int alpha,int j){
    int product=gf8_multiply(alpha,1<<(j%3));
    Word v=Word(1)<<j;
    for(int i=0;i<3;i++){
        if((product>>i)&1)v^=Word(1)<<(R+(j/3)*3+i);
    }
    return v;
}
Word transform(Word value,const std::vector<Word>& matrix){
    Word result=0;
    while(value){
        int i=__builtin_ctzll(value);value&=value-1;result^=matrix.at(i);
    }
    return result;
}
// Restrict the full PHP variable x_(i,j), then reduce residual row equations.
// Bit 0 is one; remaining bits are rows with the matched row omitted, each
// using increasing free columns with the largest free column omitted.
Word restricted_variable(int i,int j,int matched_row,int matched_column){
    if(i==matched_row)return j==matched_column?Word(1):Word(0);
    if(j==matched_column)return 0;
    int spare=matched_column==N-1?N-2:N-1;
    int row=i-(i>matched_row);
    if(j==spare){
        Word value=1;
        for(int c=0;c<N-2;c++)value^=Word(1)<<(1+row*(N-2)+c);
        return value;
    }
    int column=0;
    for(int c=0;c<j;c++){
        if(c!=matched_column && c!=spare)column++;
    }
    return Word(1)<<(1+row*(N-2)+column);
}
Word restrict_input(Word input,int matched_row,int matched_column){
    Word result=0;
    while(input){
        int v=__builtin_ctzll(input);input&=input-1;
        result^=restricted_variable(v/(N-1),v%(N-1),matched_row,matched_column);
    }
    return result;
}
struct Witness{
    int row,column,alpha,rank;
    Word dual;
    std::vector<Word> inputs;
};
bool certify(const std::vector<Word>& inputs,Word dual){
    if(!(dual&1))return false;
    for(Word input:inputs){
        if(__builtin_parityll(input&dual))return false;
    }
    return true;
}
int main(int argc,char** argv){
    try{
        std::string path;Word seed=20260911;
        for(int i=1;i<argc;i++){
            std::string arg=argv[i];
            if(arg=="--out" && i+1<argc)path=argv[++i];
            else if(arg=="--seed" && i+1<argc)seed=std::stoull(argv[++i]);
            else if(arg=="--help"){
                std::cout<<"Usage: find_restriction_resistant_spread --out NEW_PATH [--seed INTEGER]\n";
                return 0;
            }else throw std::runtime_error("unknown or incomplete argument");
        }
        need(!path.empty() && !std::filesystem::exists(path),"new --out path required");
        std::ofstream out(path);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"restriction_resistant_spread\",\"p\":2,\"n\":7,\"m\":8,"
              "\"ambient_dimension\":48,\"input_rank\":24,\"residual_affine_dimension\":36,"
              "\"rng\":\"std::mt19937_64\",\"seed\":"<<seed
           <<",\"gf8_modulus\":11,\"union_bound_numerator\":1605632,\"union_bound_denominator\":16777217}\n";
        for(int a=0;a<M;a++)for(int b=0;b<N;b++)for(int i=0;i<M;i++){
            Word row_equation=1;
            for(int j=0;j<N;j++)row_equation^=restricted_variable(i,j,a,b);
            need(row_equation==0,"residual row-equation projection");
        }
        std::mt19937_64 rng(seed);
        int invertible=0;
        for(int draw=1;draw<=1000;draw++){
            std::vector<Word> matrix(W);Basis linear(W);
            for(auto& row:matrix){row=rng()&MASK;linear.add(row);}
            out<<"{\"record\":\"matrix_draw\",\"draw\":"<<draw<<",\"rank\":"<<linear.rank<<",\"images\":";
            words_json(out,matrix);out<<"}\n";
            if(linear.rank<W)continue;
            invertible++;
            std::array<std::vector<Word>,N> spaces;
            for(int alpha=0;alpha<N;alpha++){
                Basis span(W);
                for(int j=0;j<R;j++){
                    Word v=transform(graph_input(alpha,j),matrix);spaces[alpha].push_back(v);span.add(v);
                }
                need(span.rank==R,"graph rank");
            }
            for(int a=0;a<N;a++)for(int b=a+1;b<N;b++){
                Basis joint(W);
                for(Word v:spaces[a])joint.add(v);
                for(Word v:spaces[b])joint.add(v);
                need(joint.rank==2*R,"spread disjointness");
            }
            std::vector<Witness> witnesses;bool good=true;
            for(int a=0;a<M && good;a++)for(int b=0;b<N && good;b++)for(int alpha=0;alpha<N;alpha++){
                std::vector<Word> inputs;Basis image(RES);
                for(Word v:spaces[alpha]){
                    Word projected=restrict_input(v,a,b);inputs.push_back(projected);image.add(projected);
                }
                Word remainder=image.reduce(1);
                if(!remainder){
                    out<<"{\"record\":\"candidate_rejected\",\"draw\":"<<draw
                       <<",\"row\":"<<a<<",\"column\":"<<b<<",\"alpha\":"<<alpha<<"}\n";
                    good=false;break;
                }
                int free_coordinate=__builtin_ctzll(remainder);Word dual=0;
                for(int j=0;j<RES;j++){
                    if((image.reduce(Word(1)<<j)>>free_coordinate)&1)dual^=Word(1)<<j;
                }
                need(certify(inputs,dual),"dual certificate failed");
                need(!certify(inputs,dual^1),"corrupted certificate not rejected");
                witnesses.push_back({a,b,alpha,image.rank,dual,std::move(inputs)});
            }
            if(!good)continue;
            need(witnesses.size()==size_t(M*N*N),"missing restriction witnesses");
            for(int alpha=0;alpha<N;alpha++){
                out<<"{\"record\":\"accepted_space\",\"draw\":"<<draw<<",\"alpha\":"<<alpha<<",\"inputs\":";
                words_json(out,spaces[alpha]);out<<"}\n";
            }
            for(const auto& witness:witnesses){
                out<<"{\"record\":\"dual_witness\",\"row\":"<<witness.row<<",\"column\":"<<witness.column
                   <<",\"alpha\":"<<witness.alpha<<",\"image_rank\":"<<witness.rank<<",\"dual\":";
                hexword(out,witness.dual);out<<",\"restricted_inputs\":";
                words_json(out,witness.inputs);out<<"}\n";
            }
            out<<"{\"record\":\"summary\",\"accepted_draw\":"<<draw<<",\"invertible_candidates\":"<<invertible
               <<",\"spaces\":7,\"pair_checks\":21,\"matchings\":56,\"dual_witnesses\":392,"
                 "\"corrupted_witness_controls\":392,\"all_passed\":true}\n";
            out.close();need(bool(out),"output write failed");
            std::cout<<"Accepted matrix draw "<<draw<<" ("<<invertible<<" invertible candidates): "
                       "7 rank-24 spread spaces, 56 matchings, and 392 checked dual witnesses.\n";
            return 0;
        }
        throw std::runtime_error("search exhausted 1000 matrix draws");
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
