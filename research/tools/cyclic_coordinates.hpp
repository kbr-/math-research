// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Small exact cyclic local-coordinate fixtures, shared by projected-source checks.
#pragma once
#include "binary_extension_polynomial.hpp"
#include "graded_reduction.hpp"
namespace cyclic_coordinates {
using namespace domain_polynomial;
using namespace binary_extension;
inline void coordinate_need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
inline bool binomial_odd(unsigned n,unsigned k){return (n&k)==k;}
inline int odd_part(int t){coordinate_need(t>0,"positive cyclic length");while(t%2==0)t/=2;return t;}
inline int modulus_for_length(int t){
    int u=odd_part(t),d=1;
    if(u>1){int residue=2%u;while(residue!=1){residue=2*residue%u;++d;coordinate_need(d<=u,"finite order bound");}}
    const int moduli[5]={0,3,7,11,19};coordinate_need(d<=4,"small exact cyclic extension");return moduli[d];
}
struct Coordinates {
    Arithmetic a;int t,u,e,v;bool affine;static constexpr int Y=1024;
    std::vector<int> roots,frobenius,weights;
    Matrix left,right,left_inverse,right_inverse;
    std::vector<Polynomial> probes_a,probes_b,inputs,boolean,local_products,domain_divisors;
    std::map<int,EP> to_old,to_y;
    std::vector<std::map<int,int>> domain_pullback;
    explicit Coordinates(int length,bool shifted=false):a(modulus_for_length(length)),t(length),u(odd_part(t)),e(t/u),v(2*t+1),affine(shifted){
        coordinate_need(t>=2 && t<=12,"bounded local-coordinate fixture");
        for(int x=1;x<a.f.q;++x)if(a.f.power(x,u)==1)roots.push_back(x);
        coordinate_need(int(roots.size())==u,"all cyclic roots");
        for(int root:roots){auto it=std::find(roots.begin(),roots.end(),a.f.mul(root,root));coordinate_need(it!=roots.end(),"root Frobenius permutation");frobenius.push_back(it-roots.begin());}
        for(int i=0;i<t;++i){
            auto A=a.r.variable(i),B=a.r.variable(t+i);
            if(affine && i==0){a.r.accumulate(A,a.r.variable(1));a.r.accumulate(B,a.r.variable(t+1));}
            if(affine && i<(u==1?2:3)){a.r.accumulate(A,a.r.constant(1));a.r.accumulate(B,a.r.constant(1));}
            probes_a.push_back(A);probes_b.push_back(B);
        }
        left.resize(t,std::vector<int>(t));right=left;
        for(int j=0;j<u;++j)for(int r=0;r<e;++r)for(int i=0;i<t;++i){
            int exponent=(t-i)%t;
            if(exponent>=r && (exponent&r)==r)left[j*e+r][i]=a.f.power(roots[j],exponent-r);
            if(i>=r && (i&r)==r)right[j*e+r][i]=a.f.power(roots[j],i-r);
        }
        left_inverse=invert(a.f,left);right_inverse=invert(a.f,right);
        std::vector<EP> A_inverse(t,a.zero()),B_inverse(t,a.zero());
        for(int row=0;row<t;++row){
            auto A=a.zero(),B=a.zero();
            for(int i=0;i<t;++i){
                a.add(A,a.binary(probes_a[i]),left[row][i]);a.add(B,a.binary(probes_b[i]),right[row][i]);
                a.add(A_inverse[row],a.variable(Y+i),left_inverse[row][i]);a.add(B_inverse[row],a.variable(Y+t+i),right_inverse[row][i]);
            }
            to_old[Y+row]=A;to_old[Y+t+row]=B;
        }
        for(int i=0;i<t;++i){
            auto A=A_inverse[i],B=B_inverse[i];
            if(affine && i==0){a.add(A,A_inverse[1]);a.add(B,B_inverse[1]);}
            if(affine && i>0 && i<(u==1?2:3)){a.add(A,a.constant(1));a.add(B,a.constant(1));}
            to_y[i]=A;to_y[t+i]=B;
        }
        to_old[Y+v-1]=a.variable(v-1);to_y[v-1]=a.variable(Y+v-1);
        weights.resize(v);
        for(int i=0;i<v;++i){
            coordinate_need(a.substitute(to_y[i],to_old)==a.variable(i),"old cyclic-coordinate round trip");
            coordinate_need(a.substitute(to_old[Y+i],to_y)==a.variable(Y+i),"local cyclic-coordinate round trip");
            auto x=a.r.variable(i);boolean.push_back(a.r.subtract(a.r.power(x,2),x));
            int next=i;
            if(i<2*t){int local=i%t,side=i<t?0:t;next=side+frobenius[local/e]*e+local%e;weights[i]=-(local%e)*(local%e);}
            auto y=a.r.variable(Y+i);domain_divisors.push_back(a.r.subtract(a.r.power(y,2),a.r.variable(Y+next)));
            std::map<int,int> image;
            for(int j=0;j<v;++j){int scalar=0;for(int c=0;c<a.f.d;++c)if(to_old[Y+next][c].count(Monomial{j}))scalar|=1<<c;if(scalar)image[j]=scalar;}
            domain_pullback.push_back(image);
        }
        for(int i=0;i<t;++i){
            Polynomial g;for(int j=0;j<t;++j)a.r.accumulate(g,a.r.multiply(probes_a[j],probes_b[(j+i)%t]));inputs.push_back(g);
        }
        for(int j=0;j<u;++j)for(int k=0;k<e;++k){
            Polynomial C;for(int r=0;r<=k;++r)a.r.accumulate(C,a.r.multiply(a.r.variable(Y+j*e+r),a.r.variable(Y+t+j*e+k-r)));local_products.push_back(C);
        }
    }
    graded_reduction::MonomialOrder order() const{
        return [w=weights](const Monomial& m,const Monomial& n){
            if(m.size()!=n.size())return m.size()<n.size();
            int wm=0,wn=0;for(int id:m)wm+=w.at(id-Y);for(int id:n)wn+=w.at(id-Y);
            return wm!=wn?wm<wn:graded_reduction::monomial_less(m,n);
        };
    }
};
} // namespace cyclic_coordinates
