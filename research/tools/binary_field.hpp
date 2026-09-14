// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Small exact binary fields for bounded symbolic verification fixtures.
#pragma once
#include <stdexcept>
namespace binary_field {
struct SmallField {
    int d,q,modulus;
    static int dimension(int m){
        if(m<2 || m>=32)throw std::runtime_error("small exact field guard");
        return 31-__builtin_clz(unsigned(m));
    }
    explicit SmallField(int m):d(dimension(m)),q(1<<d),modulus(m){
        for(int a=1;a<q;++a)if(power(a,q-1)!=1)
            throw std::runtime_error("every nonzero residue must be a unit");
    }
    int mul(int a,int b) const{
        int result=0;
        while(b){if(b&1)result^=a;b>>=1;a<<=1;if(a&q)a^=modulus;}
        return result;
    }
    int power(int a,int e) const{
        int result=1;while(e){if(e&1)result=mul(result,a);a=mul(a,a);e>>=1;}return result;
    }
    int trace(int a) const{
        int result=0;
        for(int j=0;j<d;++j){result^=a;a=mul(a,a);}
        if(result!=0 && result!=1)throw std::runtime_error("trace must be binary");
        return result;
    }
};
} // namespace binary_field
