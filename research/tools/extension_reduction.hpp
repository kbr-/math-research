// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Degree-controlled monic division with binary-extension coefficients.
#pragma once
#include "binary_extension_polynomial.hpp"
#include "graded_reduction.hpp"
namespace extension_reduction {
using namespace domain_polynomial;
using namespace binary_extension;
inline int coefficient(const EP& p,const Monomial& m){
    int value=0;for(unsigned i=0;i<p.size();++i)if(p[i].count(m))value|=1u<<i;return value;
}
inline Monomial leading(const Arithmetic& a,const EP& p,const graded_reduction::MonomialOrder& less){
    extension_need(!a.empty(p),"nonzero extension divisor");Monomial best;bool found=false;
    for(const auto& component:p)for(const auto& [m,c]:component){
        extension_need(c==1,"binary coefficient component");
        if(!found || less(best,m)){best=m;found=true;}
    }
    extension_need(coefficient(p,best)==1,"monic extension divisor");return best;
}
struct ExtensionNormal {EP remainder;std::map<int,EP> coefficients;};
struct ExtensionReduction {
    const Arithmetic& a;std::vector<EP> divisors;graded_reduction::MonomialOrder less;
    std::vector<Monomial> heads;std::map<Monomial,ExtensionNormal> memo;
    ExtensionReduction(const Arithmetic& arithmetic,std::vector<EP> source,
                       graded_reduction::MonomialOrder order=graded_reduction::monomial_less)
        :a(arithmetic),divisors(std::move(source)),less(std::move(order)){
        for(const auto& p:divisors)heads.push_back(leading(a,p,less));
    }
    const ExtensionNormal& monomial(const Monomial& m){
        auto old=memo.find(m);if(old!=memo.end())return old->second;
        ExtensionNormal result{a.zero(),{}};int divisor=-1;Monomial quotient;
        for(unsigned i=0;i<heads.size();++i)if(graded_reduction::quotient(m,heads[i],quotient)){divisor=i;break;}
        if(divisor<0)result.remainder=a.binary(Polynomial{{m,1}});
        else{
            auto factor=a.binary(Polynomial{{quotient,1}}),tail=a.binary(Polynomial{{m,1}});
            a.add(tail,a.multiply(factor,divisors[divisor]));result.coefficients[divisor]=factor;
            for(int component=0;component<a.f.d;++component)for(const auto& [term,c]:tail[component]){
                extension_need(c==1 && less(term,m),"extension reduction order must decrease");
                const auto& child=monomial(term);a.add(result.remainder,child.remainder,1<<component);
                for(const auto& [id,p]:child.coefficients)a.add(result.coefficients[id],p,1<<component);
            }
        }
        return memo.emplace(m,std::move(result)).first->second;
    }
    ExtensionNormal polynomial(const EP& p){
        ExtensionNormal result{a.zero(),{}};
        for(int component=0;component<a.f.d;++component)for(const auto& [m,c]:p[component]){
            extension_need(c==1,"binary extension input component");const auto& child=monomial(m);
            a.add(result.remainder,child.remainder,1<<component);
            for(const auto& [id,q]:child.coefficients)a.add(result.coefficients[id],q,1<<component);
        }
        return result;
    }
};
} // namespace extension_reduction
