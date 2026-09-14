// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Degree-preserving linear monomial reduction, with ordinary ideal witnesses.
#pragma once
#include "domain_polynomial.hpp"
#include <functional>
namespace graded_reduction {
using namespace domain_polynomial;
inline void require(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
struct Normal {Polynomial remainder;std::map<int,Polynomial> coefficients;};
inline bool monomial_less(const Monomial& a,const Monomial& b){
    return a.size()!=b.size()?a.size()<b.size():b<a;
}
using MonomialOrder=std::function<bool(const Monomial&,const Monomial&)>;
inline Monomial leading(const Polynomial& p,const MonomialOrder& less=monomial_less){
    require(!p.empty(),"nonzero divisor");auto it=p.begin(),best=it++;
    for(;it!=p.end();++it)if(less(best->first,it->first))best=it;
    require(best->second==1,"monic divisor");return best->first;
}
inline bool quotient(const Monomial& m,const Monomial& divisor,Monomial& q){
    q=m;
    for(int id:divisor){
        auto it=std::lower_bound(q.begin(),q.end(),id);
        if(it==q.end() || *it!=id)return false;
        q.erase(it);
    }
    return true;
}
struct ReductionMap {
    const Ring& r;
    MonomialOrder less;
    std::vector<Polynomial> divisors;
    std::vector<Monomial> heads;
    std::map<Monomial,Normal> memo;
    ReductionMap(const Ring& ring,std::vector<Polynomial> ds,MonomialOrder order=monomial_less)
        :r(ring),less(std::move(order)),divisors(std::move(ds)){
        for(const auto& g:divisors)heads.push_back(leading(g,less));
    }
    const Normal& monomial(const Monomial& m){
        auto cached=memo.find(m);if(cached!=memo.end())return cached->second;
        Normal result;int divisor=-1;Monomial q;
        for(unsigned i=0;i<heads.size();++i)if(quotient(m,heads[i],q)){divisor=i;break;}
        if(divisor<0)result.remainder=Polynomial{{m,1}};
        else{
            Polynomial factor{{q,1}};
            auto tail=r.subtract(Polynomial{{m,1}},r.multiply(factor,divisors[divisor]));
            result.coefficients[divisor]=factor;
            for(const auto& [term,coefficient]:tail){
                require(less(term,m),"graded reduction order must decrease");
                const auto& child=monomial(term);
                r.accumulate(result.remainder,child.remainder,coefficient);
                for(const auto& [id,f]:child.coefficients)r.accumulate(result.coefficients[id],f,coefficient);
            }
        }
        return memo.emplace(m,std::move(result)).first->second;
    }
    Normal polynomial(const Polynomial& p){
        Normal result;
        for(const auto& [m,coefficient]:p){
            const auto& child=monomial(m);
            r.accumulate(result.remainder,child.remainder,coefficient);
            for(const auto& [id,f]:child.coefficients)r.accumulate(result.coefficients[id],f,coefficient);
        }
        return result;
    }
};
inline std::vector<Monomial> monomials(int variables,int maximum){
    std::vector<Monomial> result;Monomial m;
    std::function<void(int,int)> add=[&](int first,int left){
        if(!left){result.push_back(m);return;}
        for(int i=first;i<variables;++i){m.push_back(i);add(i,left-1);m.pop_back();}
    };
    for(int d=0;d<=maximum;++d)add(0,d);
    return result;
}
} // namespace graded_reduction
