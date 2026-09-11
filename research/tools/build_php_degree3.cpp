// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Build and record the exact ordinary-PHP PC consequence space through degree 3.
#include "binary_php.hpp"
#include <filesystem>
using namespace binary_php;
int main(int argc,char** argv){
    try{
        int n=7;std::string path;
        for(int j=1;j<argc;j++){
            std::string arg=argv[j];
            if(arg=="--out" && j+1<argc)path=argv[++j];
            else if(arg=="--holes" && j+1<argc)n=std::stoi(argv[++j]);
            else throw std::runtime_error("Usage: build_php_degree3 --out NEW_PATH [--holes N]");
        }
        need(!path.empty() && !std::filesystem::exists(path),"new --out required");
        std::ofstream out(path);need(bool(out),"cannot open output");
        Board board(n);Space base(board.width);std::vector<int> queue;
        out<<"BINARY_PHP_PC 1 "<<n<<" 3 "<<board.variables<<' '<<board.low<<' '<<board.width<<'\n';
        for(int j=0;j<board.width;j++)out<<"MONOMIAL "<<j<<' '<<board.monomials[j]<<'\n';
        auto derive=[&](Bits polynomial,char kind,int a,int b){
            std::vector<int> trace;int pivot=base.add(std::move(polynomial),&trace);
            if(pivot<0)return;
            out<<"BASIS "<<pivot<<' '<<kind<<' '<<a<<' '<<b<<' '<<trace.size();
            for(int old:trace)out<<' '<<old;
            out<<' ';sparse_text(out,base.rows[pivot]);out<<'\n';
            if(pivot<board.low)queue.push_back(pivot);
        };
        for(int row=0;row<board.m;row++){
            for(int mon=0;mon<board.low;mon++)derive(board.row_multiple(row,mon),'A',row,mon);
        }
        int original_rank=base.rank,original_low=int(queue.size());
        out<<"INITIAL "<<original_rank<<' '<<original_low<<'\n';
        std::cout<<"Initial normalized I3 rank "<<original_rank<<'/'<<board.width
                 <<", degree-at-most-two part "<<original_low<<".\n"<<std::flush;
        std::uint64_t products=0;
        for(size_t cursor=0;cursor<queue.size();cursor++){
            int pivot=queue[cursor];Bits polynomial=base.rows[pivot];
            for(int v=0;v<board.variables;v++){
                derive(board.variable_product(polynomial,v),'P',pivot,v);products++;
            }
            if((cursor+1)%200==0){
                std::cout<<"Closed "<<cursor+1<<'/'<<queue.size()<<" low-degree rows; rank "
                         <<base.rank<<".\n"<<std::flush;
            }
        }
        int affine_rank=0;
        for(int j=0;j<=board.variables;j++){
            if(!base.rows[j].empty())affine_rank++;
        }
        out<<"FINAL "<<base.rank<<' '<<queue.size()<<' '<<affine_rank<<' '<<products<<'\n';
        if(base.rows[0].empty()){
            Bits dual=base.separating_dual(board.unit(0));
            out<<"BASE_DUAL ";sparse_text(out,dual);out<<'\n';
        }else{
            out<<"REFUTATION 0\n";
        }
        out<<"END\n";out.close();need(bool(out),"output write failure");
        std::cout<<"Final C3 rank "<<base.rank<<", low-degree part "<<queue.size()
                 <<", affine part "<<affine_rank<<", checked products "<<products
                 <<", refutation "<<(!base.rows[0].empty()?"YES":"NO")<<".\n";
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
