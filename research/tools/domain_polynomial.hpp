// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact mixed Boolean/field domain certificates, shared by symbolic checkers.
#pragma once
#include "ens_symbolic.hpp"
#include <string>
namespace domain_polynomial {
using namespace ens_symbolic;
inline void reduction_need(bool condition,const std::string& why){
    if(!condition)throw std::runtime_error(why);
}
struct Reduction {Polynomial remainder;std::vector<Polynomial> coefficients;int degree=0;};
inline Reduction domain_reduce(const Ring& ring,Polynomial polynomial,const std::vector<int>& powers){
    Reduction result;result.coefficients.resize(powers.size());const int start_degree=degree(polynomial);
    for(size_t variable=0;variable<powers.size();variable++){
        int exponent=powers[variable];reduction_need(exponent==2 || exponent==ring.p,"domain exponent");
        while(true){
            auto found=polynomial.end();
            for(auto term=polynomial.begin();term!=polynomial.end();++term){
                auto range=std::equal_range(term->first.begin(),term->first.end(),int(variable));
                if(range.second-range.first>=exponent){found=term;break;}
            }
            if(found==polynomial.end())break;
            Monomial monomial=found->first;int coefficient=found->second;polynomial.erase(found);
            auto first=std::lower_bound(monomial.begin(),monomial.end(),int(variable));
            int position=int(first-monomial.begin());
            Monomial quotient=monomial;quotient.erase(quotient.begin()+position,quotient.begin()+position+exponent);
            ring.accumulate(result.coefficients[variable],Polynomial{{quotient,coefficient}});
            monomial.erase(monomial.begin()+position,monomial.begin()+position+exponent-1);
            ring.accumulate(polynomial,Polynomial{{monomial,coefficient}});
        }
    }
    result.remainder=std::move(polynomial);
    for(size_t variable=0;variable<powers.size();variable++){
        if(!result.coefficients[variable].empty()){
            result.degree=std::max(result.degree,degree(result.coefficients[variable])+powers[variable]);
        }
    }
    reduction_need(result.degree<=start_degree,"domain reduction increased certificate degree");
    return result;
}
inline void verify_reduction(const Ring& ring,const Polynomial& original,const std::vector<int>& powers,
                      const Reduction& reduction){
    Polynomial reconstructed=reduction.remainder;
    for(size_t variable=0;variable<powers.size();variable++){
        Polynomial x=ring.variable(int(variable));
        Polynomial equation=ring.subtract(ring.power(x,powers[variable]),x);
        ring.accumulate(reconstructed,ring.multiply(reduction.coefficients[variable],equation));
    }
    reduction_need(reconstructed==original,"domain certificate reconstruction");
}
inline void write_reduction(std::ostream& out,const Reduction& result){
    out<<"{\"degree\":"<<result.degree<<",\"remainder\":";write_json(out,result.remainder);
    out<<",\"cofactors\":";write_polynomials(out,result.coefficients);out<<'}';
}
} // namespace domain_polynomial
