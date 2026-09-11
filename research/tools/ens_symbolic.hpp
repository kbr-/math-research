// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
#pragma once
#include "sparse_polynomial.hpp"
namespace ens_symbolic {
using namespace sparse_polynomial;
struct Block {
    std::vector<Polynomial> inputs,prefix,companions;
    std::vector<std::vector<int>> variables;
    Polynomial product;
    int accuracy;
};
inline Block make_block(const Ring& ring,std::vector<Polynomial> inputs,int accuracy,int& fresh){
    if(inputs.empty() || accuracy<1)throw std::runtime_error("ENS block parameters");
    Block result;result.inputs=std::move(inputs);result.accuracy=accuracy;
    result.product=ring.constant(1);result.prefix.resize(result.inputs.size());
    for(int u=0;u<accuracy;u++){
        Polynomial factor=ring.constant(1);std::vector<int> ids;
        for(size_t j=0;j<result.inputs.size();j++){
            int id=fresh++;ids.push_back(id);Polynomial r=ring.variable(id);
            ring.accumulate(result.prefix[j],ring.multiply(r,result.product));
            ring.accumulate(factor,ring.multiply(r,result.inputs[j]),-1);
        }
        result.product=ring.multiply(result.product,factor);result.variables.push_back(std::move(ids));
    }
    for(const Polynomial& g:result.inputs)result.companions.push_back(ring.multiply(g,result.product));
    return result;
}
inline Polynomial normalizer_error(const Ring& ring,const std::vector<Polynomial>& inputs,
                                   const std::vector<Polynomial>& beta){
    if(inputs.size()!=beta.size())throw std::runtime_error("normalizer arity");
    Polynomial result=ring.constant(1);
    for(size_t j=0;j<inputs.size();j++)ring.accumulate(result,ring.multiply(beta[j],inputs[j]),-1);
    return result;
}
inline void write_polynomials(std::ostream& out,const std::vector<Polynomial>& values){
    out<<'[';
    for(size_t j=0;j<values.size();j++){
        if(j)out<<',';
        write_json(out,values[j]);
    }
    out<<']';
}
inline void write_block(std::ostream& out,const Block& b){
    out<<"{\"accuracy\":"<<b.accuracy<<",\"inputs\":";write_polynomials(out,b.inputs);
    out<<",\"product\":";write_json(out,b.product);
    out<<",\"prefix_coefficients\":";write_polynomials(out,b.prefix);
    out<<",\"companions\":";write_polynomials(out,b.companions);
    out<<",\"coefficient_variables\":[";
    for(size_t u=0;u<b.variables.size();u++){
        if(u)out<<',';
        out<<'[';
        for(size_t j=0;j<b.variables[u].size();j++){
            if(j)out<<',';
            out<<b.variables[u][j];
        }
        out<<']';
    }
    out<<"]}";
}
inline std::map<int,Polynomial> coefficient_images(const Ring& ring,const Block& b,
                                                  const std::vector<Polynomial>& beta){
    if(beta.size()!=b.inputs.size())throw std::runtime_error("coefficient image arity");
    std::map<int,Polynomial> images;
    for(size_t u=0;u<b.variables.size();u++)for(size_t j=0;j<beta.size();j++){
        images[b.variables[u][j]]=u==0?beta[j]:ring.constant(0);
    }
    return images;
}
} // namespace ens_symbolic
