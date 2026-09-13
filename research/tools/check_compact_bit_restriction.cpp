// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact literal restriction witness and dense affine survival control.
#include <algorithm>
#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>
using Word=std::uint64_t;
constexpr int N=1024, ELL=10, KEEP=32, S=5, M=N+1, H=6, R=13, BLOCKS=64;
constexpr Word SEED=202609130107ULL;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
template<class T>void array(std::ostream& out,const std::vector<T>& values){
    out<<'[';
    for(std::size_t i=0;i<values.size();++i){
        if(i)out<<',';
        out<<values[i];
    }
    out<<']';
}
struct Literal{int variable,constant;};
int main(int argc,char** argv){
    try{
        need(argc==3&&std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];
        need(!std::filesystem::exists(path),"refusing existing output");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot create output");
        std::mt19937_64 rng(SEED);
        auto choose=[&](int limit){return std::uniform_int_distribution<int>(0,limit-1)(rng);};
        out<<"{\"type\":\"parameters\",\"version\":1,\"field\":2,\"holes\":"<<N
           <<",\"ell\":"<<ELL<<",\"kept_holes\":"<<KEEP<<",\"kept_bits\":"<<S
           <<",\"pigeons\":"<<M<<",\"accuracy\":"<<H<<",\"rank\":"<<R
           <<",\"literal_blocks\":"<<BLOCKS<<",\"seed\":"<<SEED<<"}\n";
        std::vector<unsigned> code(M);
        for(unsigned& row:code)row=unsigned(rng())&((1U<<R)-1);
        std::vector<int> weights(1<<R);
        int minimum=M;
        for(unsigned v=1;v<(1U<<R);++v){
            int weight=0;
            for(unsigned row:code)weight+=__builtin_parity(row&v);
            weights[v]=weight;
            minimum=std::min(minimum,weight);
        }
        need(minimum*5>=2*M,"dense code did not attain the planned 0.4 distance");
        out<<"{\"type\":\"dense_code\",\"rows\":";
        array(out,code);out<<",\"codeword_weights\":";array(out,weights);
        out<<",\"minimum_nonzero_weight\":"<<minimum<<"}\n";
        std::vector<std::vector<Literal>> blocks(BLOCKS);
        std::vector<int> order(M);
        std::iota(order.begin(),order.end(),0);
        for(int b=0;b<BLOCKS;++b){
            if(b<BLOCKS/2){
                int first=choose(M),second=choose(M-1);
                if(second>=first)++second;
                for(int t=0;t<ELL;++t)blocks[b].push_back({first*ELL+t,choose(2)});
                int start=choose(ELL);
                for(int t=0;t<R-ELL;++t)
                    blocks[b].push_back({second*ELL+(start+t)%ELL,choose(2)});
            }else{
                std::shuffle(order.begin(),order.end(),rng);
                for(int t=0;t<R;++t)blocks[b].push_back({order[t]*ELL+choose(ELL),choose(2)});
            }
            std::vector<int> support;
            out<<"{\"type\":\"literal_block\",\"id\":"<<b<<",\"inputs\":[";
            for(int j=0;j<R;++j){
                if(j)out<<',';
                out<<'['<<blocks[b][j].variable<<','<<blocks[b][j].constant<<']';
                support.push_back(blocks[b][j].variable);
            }
            out<<"]}\n";
            std::sort(support.begin(),support.end());
            need(std::adjacent_find(support.begin(),support.end())==support.end(),
                 "repeated literal variable");
        }
        bool accepted=false;
        int trials=0;
        for(int trial=0;trial<1000&&!accepted;++trial){
            ++trials;
            std::shuffle(order.begin(),order.end(),rng);
            std::vector<int> live(order.begin(),order.begin()+KEEP+1);
            std::sort(live.begin(),live.end());
            std::vector<int> residual_row(M,-1),fixed(M,-1),outside(N-KEEP);
            for(int i=0;i<=KEEP;++i)residual_row[live[i]]=i;
            std::iota(outside.begin(),outside.end(),KEEP);
            std::shuffle(outside.begin(),outside.end(),rng);
            for(int i=0;i<N-KEEP;++i)fixed[order[KEEP+1+i]]=outside[i];
            std::vector<int> killers(BLOCKS,-1);
            int killed=0;
            for(int b=0;b<BLOCKS;++b){
                for(int j=0;j<R;++j){
                    auto literal=blocks[b][j];
                    int row=literal.variable/ELL,t=literal.variable%ELL;
                    int value=fixed[row]>=0?((fixed[row]>>t)&1):(t>=S?0:-1);
                    if(value>=0&&(value^literal.constant)){
                        killers[b]=j;++killed;break;
                    }
                }
            }
            std::array<unsigned,R> basis{};
            std::array<Word,R> tags{};
            int rank=0;
            for(int i=0;i<=KEEP;++i){
                unsigned value=code[live[i]];
                Word tag=Word(1)<<i;
                for(int p=R-1;p>=0;--p)if((value>>p)&1){
                    if(basis[p]){value^=basis[p];tag^=tags[p];}
                    else{basis[p]=value;tags[p]=tag;++rank;break;}
                }
            }
            accepted=killed==BLOCKS&&rank==R;
            out<<"{\"type\":\"trial\",\"id\":"<<trial<<",\"live_pigeons\":";
            array(out,live);out<<",\"fixed_labels\":";array(out,fixed);
            out<<",\"first_constant_one_inputs\":";array(out,killers);
            out<<",\"dense_residual_rank\":"<<rank<<",\"accepted\":"
               <<(accepted?"true":"false")<<"}\n";
            if(!accepted)continue;
            unsigned constant=0;
            for(int i=0;i<M;++i)if(fixed[i]>=0&&(fixed[i]&1))constant^=code[i];
            unsigned remainder=constant;
            Word solution=0;
            for(int p=R-1;p>=0;--p)if((remainder>>p)&1){
                need(basis[p]!=0,"missing residual pivot");
                remainder^=basis[p];solution^=tags[p];
            }
            need(remainder==0,"affine zero-space witness failed");
            unsigned check=constant;
            for(int i=0;i<=KEEP;++i)if((solution>>i)&1)check^=code[live[i]];
            need(check==0,"dense affine zero-space substitution");
            int live_pairs=0,fixed_pairs=0,mixed_pairs=0;
            for(int i=0;i<M;++i)for(int j=i+1;j<M;++j){
                if(fixed[i]<0&&fixed[j]<0){
                    need(residual_row[i]!=residual_row[j],"live row identification");
                    ++live_pairs;
                }else if(fixed[i]>=0&&fixed[j]>=0){
                    need(fixed[i]!=fixed[j],"fixed labels collide");
                    ++fixed_pairs;
                }else{
                    int label=fixed[i]>=0?fixed[i]:fixed[j];
                    need((label>>S)!=0,"fixed label lies inside retained cube");
                    ++mixed_pairs;
                }
            }
            out<<"{\"type\":\"accepted_witness\",\"trial\":"<<trial
               <<",\"dense_constant_mask\":"<<constant
               <<",\"dense_pivot_rows\":[";
            for(int p=0;p<R;++p){
                if(p)out<<',';
                out<<'['<<basis[p]<<','<<tags[p]<<']';
            }
            out<<"],\"dense_zero_solution_live_bit_zero_mask\":"<<solution
               <<",\"live_equality_images\":"<<live_pairs
               <<",\"zero_fixed_equality_images\":"<<fixed_pairs
               <<",\"zero_mixed_equality_images\":"<<mixed_pairs
               <<",\"surviving_old_Booleanity_images\":"<<(KEEP+1)*S<<"}\n";
        }
        need(accepted,"no joint literal-killing/dense-surviving restriction found");
        out<<"{\"type\":\"summary\",\"trials\":"<<trials
           <<",\"literal_blocks_killed\":"<<BLOCKS
           <<",\"dense_residual_rank\":"<<R
           <<",\"minimum_code_weight\":"<<minimum<<",\"passed\":true}\n";
        out.close();need(bool(out),"write failed");
        std::cout<<"Passed after "<<trials<<" restriction trials: all "<<BLOCKS
                 <<" literal blocks killed, dense rank "<<R<<" retained; complete code minimum "
                 <<minimum<<'/'<<M<<".\n";
    }catch(const std::exception& error){std::cerr<<"ERROR: "<<error.what()<<'\n';return 1;}
}
