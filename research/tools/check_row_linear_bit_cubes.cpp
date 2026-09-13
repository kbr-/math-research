// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exhaust coordinate-direction multisets for row-linear coefficient duals.
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using Word=std::uint64_t;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
template<class T>void array(std::ostream& out,const std::vector<T>& values){
    out<<'[';
    for(std::size_t i=0;i<values.size();++i){
        if(i)out<<',';
        out<<values[i];
    }
    out<<']';
}
int main(int argc,char** argv){
    try{
        need(argc==3&&std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];
        need(!std::filesystem::exists(path),"refusing existing output");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot create output");
        constexpr int ell=5,n=32;
        out<<"{\"type\":\"schema\",\"version\":1,\"field\":2,\"ell\":5,\"labels\":32,"
               "\"scope\":\"all direction multisets, representing ordered cases up to row permutation\","
               "\"cube_points\":\"representative and representative XOR (1<<axis)\"}\n";
        int total=0,tuples=0;
        for(int rows:{6,7,8}){
            need(4*(rows-1)<n,"row-linear cube range");
            int cases=0;
            std::vector<int> axes;
            std::function<void(int)> enumerate=[&](int first){
                if(int(axes.size())<rows){
                    for(int axis=first;axis<ell;++axis){
                        axes.push_back(axis);enumerate(axis);axes.pop_back();
                    }
                    return;
                }
                Word occupied=0;
                std::vector<int> representatives;
                for(int axis:axes){
                    int found=-1,direction=1<<axis;
                    for(int a=0;a<n;++a)if(!(a&direction)){
                        Word points=(Word(1)<<a)|(Word(1)<<(a^direction));
                        if(!(points&occupied)){found=a;occupied|=points;break;}
                    }
                    need(found>=0,"greedy line placement failed");
                    representatives.push_back(found);
                }
                std::vector<std::vector<int>> parities(rows,std::vector<int>(1<<(rows-1)));
                int coefficient=0;
                for(int state=0;state<(1<<rows);++state){
                    Word used=0;
                    int value=1;
                    for(int i=0;i<rows;++i){
                        int point=representatives[i]^(((state>>i)&1)<<axes[i]);
                        need(!(used&(Word(1)<<point)),"repeated label");
                        used|=Word(1)<<point;
                        value&=(point>>axes[i])&1;
                        int context=(state&((1<<i)-1))|((state>>(i+1))<<i);
                        parities[i][context]^=1;
                    }
                    coefficient^=value;++tuples;
                }
                need(coefficient==1,"leading coefficient");
                for(const auto& row:parities)
                    for(int value:row)need(value==0,"missing-row potential");
                out<<"{\"type\":\"family\",\"rows\":"<<rows<<",\"id\":"<<cases++
                   <<",\"axes\":";array(out,axes);
                out<<",\"representatives\":";array(out,representatives);
                out<<",\"leading_coefficient\":1,\"missing_row_parities\":[";
                for(int i=0;i<rows;++i){
                    if(i)out<<',';
                    array(out,parities[i]);
                }
                out<<"]}\n";
            };
            enumerate(0);
            need(cases==(rows==6?210:rows==7?330:495),"multiset count");
            total+=cases;
            out<<"{\"type\":\"row_summary\",\"rows\":"<<rows<<",\"families\":"<<cases<<"}\n";
        }
        need(total==1035&&tuples==182400,"total counts");
        out<<"{\"type\":\"summary\",\"families\":"<<total<<",\"tuples\":"<<tuples
           <<",\"passed\":true}\n";
        out.close();need(bool(out),"write failed");
        std::cout<<"Passed all 1035 direction multisets and 182400 product tuples "
                    "with six to eight rows at bit width five.\n";
    }catch(const std::exception& error){std::cerr<<"ERROR: "<<error.what()<<'\n';return 1;}
}
