// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact binary linear algebra and ordinary-PHP normal forms through degree three.
#pragma once
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

namespace binary_php {
using Word=std::uint64_t;
using Bits=std::vector<Word>;
inline void need(bool ok,const std::string& why){
    if(!ok)throw std::runtime_error(why);
}
inline Bits blank(int width){return Bits((width+63)/64);}
inline bool bit(const Bits& b,int i){return (b[i/64]>>(i%64))&1;}
inline void flip(Bits& b,int i){b[i/64]^=Word(1)<<(i%64);}
inline bool zero(const Bits& b){
    return std::all_of(b.begin(),b.end(),[](Word w){return w==0;});
}
inline int highest(const Bits& b){
    for(int j=int(b.size())-1;j>=0;j--){
        if(b[j])return 64*j+63-__builtin_clzll(b[j]);
    }
    return -1;
}
inline int dot(const Bits& a,const Bits& b){
    need(a.size()==b.size(),"dot width mismatch");int value=0;
    for(size_t j=0;j<a.size();j++)value^=__builtin_parityll(a[j]&b[j]);
    return value;
}
inline std::vector<int> support(const Bits& b){
    std::vector<int> result;
    for(size_t j=0;j<b.size();j++){
        Word w=b[j];
        while(w){
            int k=__builtin_ctzll(w);w&=w-1;result.push_back(int(64*j)+k);
        }
    }
    return result;
}
inline void sparse_text(std::ostream& out,const Bits& b){
    auto cells=support(b);out<<cells.size();
    for(int cell:cells)out<<' '<<cell;
}
inline Bits read_sparse(std::istream& in,int width){
    int count=-1;in>>count;need(count>=0 && count<=width,"sparse count guard");
    Bits result=blank(width);int last=-1;
    for(int j=0;j<count;j++){
        int cell=-1;in>>cell;
        need(cell>last && cell<width,"sparse coordinate order/range");
        flip(result,cell);last=cell;
    }
    need(bool(in),"sparse read failure");return result;
}
inline void sparse_json(std::ostream& out,const Bits& b){
    auto cells=support(b);out<<'[';
    for(size_t j=0;j<cells.size();j++){
        if(j)out<<',';
        out<<cells[j];
    }
    out<<']';
}
inline Bits low_part(const Bits& b,int width){
    need(highest(b)<width,"nonzero high-degree component");
    Bits result=b;result.resize((width+63)/64);return result;
}

struct Space {
    int width,rank=0;
    std::vector<Bits> rows;
    std::vector<std::vector<int>> sparse_rows;
    Bits pivots;
    explicit Space(int w):width(w),rows(w),sparse_rows(w),pivots(blank(w)){
        need(w>0 && w<=500000,"matrix width guard");
    }
    Bits reduce(Bits value,std::vector<int>* trace=nullptr) const{
        need(value.size()==pivots.size(),"row width mismatch");
        for(int word=int(value.size())-1;word>=0;word--){
            Word candidates=value[word]&pivots[word];
            while(candidates){
                int p=64*word+63-__builtin_clzll(candidates);
                if(trace)trace->push_back(p);
                if(!sparse_rows[p].empty()){
                    for(int cell:sparse_rows[p])flip(value,cell);
                }else{
                    for(int j=0;j<=word;j++)value[j]^=rows[p][j];
                }
                candidates=value[word]&pivots[word];
            }
        }
        return value;
    }
    void insert_reduced(Bits value,int pivot){
        need(pivot>=0 && pivot<width && rows[pivot].empty(),"invalid new pivot");
        need(highest(value)==pivot,"pivot does not lead row");
        auto cells=support(value);
        if(cells.size()<size_t(pivot/64+1))sparse_rows[pivot]=std::move(cells);
        rows[pivot]=std::move(value);flip(pivots,pivot);rank++;
        need(std::uint64_t(rank)*pivots.size()*sizeof(Word)<1500000000ULL,
             "matrix storage guard");
    }
    int add(Bits value,std::vector<int>* trace=nullptr){
        value=reduce(std::move(value),trace);int p=highest(value);
        if(p>=0)insert_reduced(std::move(value),p);
        return p;
    }
    Bits complete_dual(Bits free_values) const{
        need(free_values.size()==pivots.size(),"dual width mismatch");
        for(size_t j=0;j<pivots.size();j++){
            need((free_values[j]&pivots[j])==0,"dual seed uses a pivot");
        }
        for(int p=0;p<width;p++){
            if(!rows[p].empty() && dot(rows[p],free_values))flip(free_values,p);
        }
        for(const Bits& row:rows){
            if(!row.empty())need(dot(row,free_values)==0,"dual completion failed");
        }
        return free_values;
    }
    Bits separating_dual(const Bits& target) const{
        Bits remainder=reduce(target);int free_coordinate=highest(remainder);
        need(free_coordinate>=0,"target is in the span");
        Bits seed=blank(width);flip(seed,free_coordinate);
        Bits dual=complete_dual(std::move(seed));
        need(dot(dual,target)==1,"target separation failed");return dual;
    }
};

struct Board {
    int n,m,variables,low,width;
    std::vector<Word> monomials;
    std::vector<std::vector<int>> products;
    explicit Board(int holes):n(holes),m(n+1),variables(m*n){
        need(n>=1 && n<=7,"degree-three board-size guard");
        monomials.push_back(0);
        for(int a=0;a<variables;a++)monomials.push_back(Word(1)<<a);
        for(int a=0;a<variables;a++)for(int b=a+1;b<variables;b++){
            if(a%n!=b%n)monomials.push_back((Word(1)<<a)|(Word(1)<<b));
        }
        low=int(monomials.size());
        for(int a=0;a<variables;a++)for(int b=a+1;b<variables;b++){
            if(a%n==b%n)continue;
            for(int c=b+1;c<variables;c++){
                if(a%n!=c%n && b%n!=c%n){
                    monomials.push_back((Word(1)<<a)|(Word(1)<<b)|(Word(1)<<c));
                }
            }
        }
        width=int(monomials.size());
        std::unordered_map<Word,int> ids;ids.reserve(monomials.size()*2);
        for(int j=0;j<width;j++)need(ids.emplace(monomials[j],j).second,"duplicate monomial");
        products.assign(variables,std::vector<int>(low,-1));
        for(int v=0;v<variables;v++)for(int j=0;j<low;j++){
            Word mask=monomials[j],others=mask&~(Word(1)<<v);bool collision=false;
            while(others){
                int cell=__builtin_ctzll(others);others&=others-1;
                if(cell%n==v%n){collision=true;break;}
            }
            if(!collision)products[v][j]=ids.at(mask|(Word(1)<<v));
        }
    }
    Bits unit(int j) const{
        need(j>=0 && j<width,"monomial index");Bits result=blank(width);flip(result,j);return result;
    }
    Bits affine(Word value) const{
        need((value>>(variables+1))==0,"affine input width");Bits result=blank(width);
        result[0]=value;return result;
    }
    Bits variable_product(const Bits& polynomial,int variable) const{
        need(variable>=0 && variable<variables && highest(polynomial)<low,"multiplication degree/range");
        Bits result=blank(width);
        for(int j:support(polynomial)){
            int image=products[variable][j];if(image>=0)flip(result,image);
        }
        return result;
    }
    Bits affine_product(Word value,const Bits& polynomial) const{
        need(highest(polynomial)<low,"affine multiplication degree");
        Bits result=(value&1)?polynomial:blank(width);
        auto cells=support(polynomial);value>>=1;
        while(value){
            int v=__builtin_ctzll(value);value&=value-1;
            need(v<variables,"affine product variable");
            for(int j:cells){
                int image=products[v][j];if(image>=0)flip(result,image);
            }
        }
        return result;
    }
    Bits row_multiple(int row,int monomial) const{
        need(row>=0 && row<m && monomial>=0 && monomial<low,"row multiple parameters");
        Bits result=unit(monomial);
        for(int j=0;j<n;j++){
            int image=products[row*n+j][monomial];if(image>=0)flip(result,image);
        }
        return result;
    }
};

// Fixed producer schema used by the previously saved seven-space certificate.
inline std::vector<std::vector<Word>> read_spread(const std::string& path){
    std::ifstream input(path);need(bool(input),"cannot read input spread");
    std::vector<std::vector<Word>> result(7);std::string line;int found=0;
    while(std::getline(input,line)){
        if(line.find("\"record\":\"accepted_space\"")==std::string::npos)continue;
        auto a=line.find("\"alpha\":");auto start=line.find("\"inputs\":[");
        need(a!=std::string::npos && start!=std::string::npos && line.size()<10000,"spread record schema");
        int alpha=std::stoi(line.substr(a+8));
        need(alpha>=0 && alpha<7 && result[alpha].empty(),"spread index");
        start+=10;auto end=line.find(']',start);need(end!=std::string::npos,"spread array");
        while(start<end){
            auto quote=line.find('"',start);if(quote==std::string::npos || quote>=end)break;
            auto close=line.find('"',quote+1);need(close<end,"spread word terminator");
            auto token=line.substr(quote+1,close-quote-1);size_t used=0;
            Word v=std::stoull(token,&used,16);
            need(used==token.size() && (v>>48)==0,"spread word range");
            result[alpha].push_back(v);start=close+1;
        }
        need(result[alpha].size()==24,"spread input count");found++;
    }
    need(found==7 && input.eof(),"incomplete spread input");return result;
}
inline Word old_input(Word source){
    need((source>>48)==0,"source coordinate range");Word result=0;
    for(int j=0;j<48;j++){
        if((source>>j)&1)result^=Word(1)<<(1+(j/6)*7+j%6);
    }
    return result;
}

// Replay every saved row derivation, then independently verify axiom coverage
// and PC closure. The returned space is certified C_3, not merely a row span.
inline Space load_pc3(const Board& board,const std::string& path,std::ostream& report){
    std::ifstream in(path);need(bool(in),"cannot read PC basis proof");
    std::string tag;int schema=0,n=0,d=0,v=0,low=0,width=0;
    in>>tag>>schema>>n>>d>>v>>low>>width;
    need(tag=="BINARY_PHP_PC" && schema==1 && n==board.n && d==3
         && v==board.variables && low==board.low && width==board.width,"PC proof header");
    for(int j=0;j<board.width;j++){
        int id=-1;Word monomial=0;in>>tag>>id>>monomial;
        need(tag=="MONOMIAL" && id==j && monomial==board.monomials[j],"PC monomial map");
    }
    Space base(board.width);bool initial=false,final=false,ended=false;int derivations=0;
    std::uint64_t claimed_products=0;
    while(in>>tag){
        if(tag=="BASIS"){
            int pivot=-1,a=-1,b=-1,count=-1;char kind=0;
            in>>pivot>>kind>>a>>b>>count;
            need(!final && count>=0 && count<=board.width,"PC derivation header");
            Bits value;
            if(kind=='A'){
                need(!initial,"late original generator");value=board.row_multiple(a,b);
            }else{
                need(kind=='P' && initial && a>=0 && a<board.low
                     && !base.rows[a].empty(),"PC reuse origin");
                value=board.variable_product(base.rows[a],b);
            }
            for(int j=0;j<count;j++){
                int old=-1;in>>old;
                need(old>=0 && old<board.width && !base.rows[old].empty()
                     && bit(value,old),"PC elimination reference");
                for(size_t k=0;k<value.size();k++)value[k]^=base.rows[old][k];
            }
            Bits stored=read_sparse(in,board.width);
            need(value==stored && highest(stored)==pivot,"PC derivation polynomial mismatch");
            base.insert_reduced(std::move(stored),pivot);derivations++;
        }else if(tag=="INITIAL"){
            int rank=-1,small=-1;in>>rank>>small;int counted=0;
            for(int j=0;j<board.low;j++){
                if(!base.rows[j].empty())counted++;
            }
            need(!initial && rank==base.rank && small==counted,"initial rank mismatch");initial=true;
        }else if(tag=="FINAL"){
            int rank=-1,small=-1,affine=-1;in>>rank>>small>>affine>>claimed_products;
            int counted=0,linear=0;
            for(int j=0;j<board.low;j++){
                if(!base.rows[j].empty()){
                    counted++;if(j<=board.variables)linear++;
                }
            }
            need(initial && !final && rank==base.rank && small==counted
                 && affine==linear,"final rank mismatch");final=true;
        }else if(tag=="BASE_DUAL"){
            need(final,"premature base dual");Bits dual=read_sparse(in,board.width);
            need(bit(dual,0),"base dual normalization");
            for(const Bits& row:base.rows){
                if(!row.empty())need(dot(row,dual)==0,"saved base dual failed");
            }
        }else if(tag=="REFUTATION"){
            int pivot=-1;in>>pivot;
            need(final && pivot==0 && !base.rows[0].empty(),"invalid refutation record");
        }else if(tag=="END"){
            need(final,"unfinished PC proof");ended=true;break;
        }else{
            throw std::runtime_error("unknown PC proof record");
        }
    }
    need(ended && bool(in),"PC proof read failure");in>>std::ws;need(in.eof(),"trailing PC proof data");
    std::uint64_t axiom_checks=0,closure_checks=0;
    for(int row=0;row<board.m;row++)for(int mon=0;mon<board.low;mon++){
        need(zero(base.reduce(board.row_multiple(row,mon))),"missing original generator");axiom_checks++;
    }
    for(int j=0;j<board.low;j++){
        if(base.rows[j].empty())continue;
        for(int variable=0;variable<board.variables;variable++){
            need(zero(base.reduce(board.variable_product(base.rows[j],variable))),"PC closure failure");
            closure_checks++;
        }
    }
    need(claimed_products==closure_checks,"closure coverage count");
    report<<"{\"record\":\"base_proof_verified\",\"basis_derivations\":"<<derivations
          <<",\"original_generator_checks\":"<<axiom_checks
          <<",\"pc_closure_checks\":"<<closure_checks<<",\"rank\":"<<base.rank<<"}\n";
    return base;
}
} // namespace binary_php
