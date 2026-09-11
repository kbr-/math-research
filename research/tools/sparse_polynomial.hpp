// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Small exact ordinary-polynomial kernel for bounded symbolic research checks.
#pragma once
#include <algorithm>
#include <map>
#include <ostream>
#include <stdexcept>
#include <vector>
namespace sparse_polynomial {
using Monomial=std::vector<int>;
using Polynomial=std::map<Monomial,int>;
struct Ring {
    int p,degree_limit;
    explicit Ring(int prime,int maximum_degree=32):p(prime),degree_limit(maximum_degree){
        if(p!=2 && p!=3 && p!=5 && p!=7)throw std::runtime_error("tested prime guard");
        if(degree_limit<1 || degree_limit>128)throw std::runtime_error("symbolic degree limit guard");
    }
    int residue(int value) const{value%=p;return value<0?value+p:value;}
    Polynomial constant(int value) const{
        value=residue(value);return value?Polynomial{{{},value}}:Polynomial{};
    }
    Polynomial variable(int id) const{return {{{id},1}};}
    void accumulate(Polynomial& a,const Polynomial& b,int scalar=1) const{
        for(const auto& [monomial,c]:b){
            int value=residue(a[monomial]+scalar*c);
            if(value)a[monomial]=value;else a.erase(monomial);
        }
    }
    Polynomial add(Polynomial a,const Polynomial& b) const{accumulate(a,b);return a;}
    Polynomial subtract(Polynomial a,const Polynomial& b) const{accumulate(a,b,-1);return a;}
    Polynomial multiply(const Polynomial& a,const Polynomial& b) const{
        Polynomial result;
        for(const auto& [u,c]:a)for(const auto& [v,d]:b){
            Monomial monomial;
            std::merge(u.begin(),u.end(),v.begin(),v.end(),std::back_inserter(monomial));
            if(monomial.size()>size_t(degree_limit))throw std::runtime_error("symbolic degree guard");
            int value=residue(result[monomial]+c*d);
            if(value)result[monomial]=value;else result.erase(monomial);
        }
        if(result.size()>500000)throw std::runtime_error("symbolic term guard");
        return result;
    }
    Polynomial power(Polynomial base,int exponent) const{
        if(exponent<0)throw std::runtime_error("negative polynomial exponent");
        Polynomial result=constant(1);
        while(exponent){
            if(exponent&1)result=multiply(result,base);
            exponent>>=1;
            if(exponent)base=multiply(base,base);
        }
        return result;
    }
    Polynomial substitute(const Polynomial& polynomial,const std::map<int,Polynomial>& images) const{
        Polynomial result;
        for(const auto& [monomial,c]:polynomial){
            Polynomial term=constant(c);
            for(int v:monomial){
                auto found=images.find(v);
                term=multiply(term,found==images.end()?variable(v):found->second);
                if(term.empty())break;
            }
            accumulate(result,term);
        }
        return result;
    }
    int evaluate(const Polynomial& polynomial,const std::map<int,int>& values) const{
        int result=0;
        for(const auto& [monomial,c]:polynomial){
            int term=c;
            for(int v:monomial){
                auto found=values.find(v);
                if(found==values.end())throw std::runtime_error("missing evaluation variable");
                term=residue(term*found->second);
            }
            result=residue(result+term);
        }
        return result;
    }
};
inline int degree(const Polynomial& polynomial){
    int result=0;
    for(const auto& term:polynomial)result=std::max(result,int(term.first.size()));
    return result;
}
inline void write_json(std::ostream& out,const Polynomial& polynomial){
    out<<'[';bool comma=false;
    for(const auto& [monomial,c]:polynomial){
        if(comma)out<<',';
        comma=true;out<<'['<<c<<",[";
        for(size_t j=0;j<monomial.size();j++){
            if(j)out<<',';
            out<<monomial[j];
        }
        out<<"]]";
    }
    out<<']';
}
} // namespace sparse_polynomial
