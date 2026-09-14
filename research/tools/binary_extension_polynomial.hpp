// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Ordinary polynomials over small binary extensions, in binary coefficient coordinates.
#pragma once
#include "binary_field.hpp"
#include "domain_polynomial.hpp"
namespace binary_extension {
using namespace domain_polynomial;
using binary_field::SmallField;
using EP=std::vector<Polynomial>;
inline void extension_need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
struct Arithmetic {
    Ring r{2,80};SmallField f;
    explicit Arithmetic(int modulus):f(modulus){}
    EP zero() const{return EP(f.d);}
    bool empty(const EP& p) const{return std::all_of(p.begin(),p.end(),[](const auto& q){return q.empty();});}
    EP binary(const Polynomial& p) const{auto result=zero();result[0]=p;return result;}
    EP constant(int a) const{
        auto result=zero();for(int i=0;i<f.d;++i)if((a>>i)&1)result[i]=r.constant(1);return result;
    }
    EP variable(int id) const{return binary(r.variable(id));}
    void add(EP& a,const EP& b,int scalar=1) const{
        a.resize(f.d);extension_need(b.size()==unsigned(f.d),"extension coordinate count");
        for(int i=0;i<f.d;++i){
            int value=f.mul(1<<i,scalar);
            for(int j=0;j<f.d;++j)if((value>>j)&1)r.accumulate(a[j],b[i]);
        }
    }
    EP multiply(const EP& a,const EP& b) const{
        auto result=zero();
        for(int i=0;i<f.d;++i)for(int j=0;j<f.d;++j){
            auto term=r.multiply(a[i],b[j]);int value=f.mul(1<<i,1<<j);
            for(int k=0;k<f.d;++k)if((value>>k)&1)r.accumulate(result[k],term);
        }
        return result;
    }
    EP square(const EP& p) const{
        auto result=zero();
        for(int i=0;i<f.d;++i){
            auto term=r.power(p[i],2);int value=f.mul(1<<i,1<<i);
            for(int j=0;j<f.d;++j)if((value>>j)&1)r.accumulate(result[j],term);
        }
        return result;
    }
    EP substitute(const EP& p,const std::map<int,EP>& images) const{
        auto result=zero();
        for(int i=0;i<f.d;++i)for(const auto& [m,c]:p[i]){
            extension_need(c==1,"binary component coefficient");auto term=constant(1<<i);
            for(int id:m){auto found=images.find(id);term=multiply(term,found==images.end()?variable(id):found->second);}
            add(result,term);
        }
        return result;
    }
    int degree_of(const EP& p) const{int d=0;for(const auto& q:p)d=std::max(d,degree(q));return d;}
    int evaluate(const EP& p,const std::map<int,int>& point) const{
        int value=0;for(int i=0;i<f.d;++i)value|=r.evaluate(p[i],point)<<i;return value;
    }
    void write(std::ostream& out,const EP& p) const{
        Polynomial wire;
        for(int i=0;i<f.d;++i)for(const auto& [m,c]:p[i]){extension_need(c==1,"wire coefficient");wire[m]^=1<<i;}
        write_json(out,wire);
    }
};
using Matrix=std::vector<std::vector<int>>;
inline Matrix invert(const SmallField& f,Matrix matrix){
    int n=matrix.size();for(int i=0;i<n;++i){matrix[i].resize(2*n);matrix[i][n+i]=1;}
    for(int col=0;col<n;++col){
        int pivot=col;while(pivot<n && !matrix[pivot][col])++pivot;extension_need(pivot<n,"Moore matrix invertibility");
        std::swap(matrix[pivot],matrix[col]);int inverse=f.power(matrix[col][col],f.q-2);
        for(auto& value:matrix[col])value=f.mul(value,inverse);
        for(int row=0;row<n;++row)if(row!=col && matrix[row][col]){
            int scale=matrix[row][col];for(int j=0;j<2*n;++j)matrix[row][j]^=f.mul(scale,matrix[col][j]);
        }
    }
    Matrix result(n,std::vector<int>(n));
    for(int i=0;i<n;++i)for(int j=0;j<n;++j){extension_need(matrix[i][j]==int(i==j),"matrix left identity");result[i][j]=matrix[i][n+j];}
    return result;
}
inline void matrix_json(std::ostream& out,const Matrix& m){
    out<<'[';for(unsigned i=0;i<m.size();++i){
        if(i)out<<',';
        out<<'[';for(unsigned j=0;j<m[i].size();++j){if(j)out<<',';out<<m[i][j];}out<<']';
    }out<<']';
}
} // namespace binary_extension
