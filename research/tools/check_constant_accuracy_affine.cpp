// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact two-bit-row dimension counts and complete constant-accuracy image checks.
#include "domain_polynomial.hpp"
#include "ns_witness.hpp"
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <string>
using namespace domain_polynomial;

void need(bool yes,const std::string& why){if(!yes)throw std::runtime_error(why);}
std::uint64_t small(__uint128_t x){
    need(x<=std::numeric_limits<std::uint64_t>::max(),"integer count overflow");
    return static_cast<std::uint64_t>(x);
}
std::uint64_t choose(int n,int k){
    if(k<0 || n<k)return 0;
    k=std::min(k,n-k);std::uint64_t a=1;
    for(int j=1;j<=k;++j)a=small((__uint128_t)a*(n-k+j)/j);
    return a;
}
std::uint64_t capped(int m,int ell,int k){
    std::vector<std::uint64_t> a(k+1);a[0]=1;
    for(int row=0;row<m;++row){
        std::vector<std::uint64_t> next(k+1);
        for(int d=0;d<=k;++d){
            __uint128_t value=a[d];
            if(d>=1)value+=(__uint128_t)ell*a[d-1];
            if(d>=2)value+=(__uint128_t)choose(ell,2)*a[d-2];
            next[d]=small(value);
        }
        a=std::move(next);
    }
    return a[k];
}
void dimensions(std::ostream& out){
    struct Case{int m,ell,k,high;};
    for(const Case c:std::vector<Case>{{5,2,2,2},{9,3,7,1},{17,4,7,1},
                                      {33,5,9,1},{16,16,3,1}}){
        const int v=c.m*c.ell,r=2*c.k+3;
        need(r<=v,"nonvacuous high rank");
        auto total=choose(v,c.k),actual=capped(c.m,c.ell,c.k);
        auto excluded=small((__uint128_t)c.m*choose(c.ell,3)*choose(v-3,c.k-3));
        auto image=choose(v-r+c.k,c.k);
        need(excluded<=total && actual>=total-excluded,"triple union bound");
        need((__uint128_t)2*excluded<=total,"epsilon at most one half");
        need((__uint128_t)c.high*image<actual,"strict joint dimension inequality");
        std::uint64_t row_linear=0,power=1;
        for(int d=0;d<=c.k;++d){
            row_linear=small((__uint128_t)row_linear+(__uint128_t)choose(c.m,d)*power);
            power=small((__uint128_t)power*c.ell);
        }
        const bool old_bound_fails=image>=row_linear;
        if(c.m==16)need(old_bound_fails,"old row-linear dimension control");
        out<<"{\"record\":\"dimension\",\"rows\":"<<c.m<<",\"bits_per_row\":"<<c.ell
           <<",\"degree\":"<<c.k<<",\"rank\":"<<r<<",\"high_blocks\":"<<c.high
           <<",\"all_squarefree_top\":\""<<total<<"\",\"row_cap_two_top\":\""<<actual
           <<"\",\"triple_union_bound_excluded\":\""<<excluded
           <<"\",\"one_flat_ordinary_image_bound\":\""<<image
           <<"\",\"old_row_linear_through_k\":\""<<row_linear
           <<"\",\"old_row_linear_bound_fails\":"<<(old_bound_fails?"true":"false")
           <<",\"scope\":\"exact dimension components; not a complete asymptotic PHP instance\"}\n";
    }
}
int affine_rank(const Ring& ring,const std::vector<Polynomial>& inputs,int old){
    std::vector<std::vector<int>> a;
    for(const auto& g:inputs){
        std::vector<int> row(old);
        for(const auto& [mon,c]:g){
            need(mon.size()==1,"homogeneous linear rank fixture");
            row.at(mon[0])=c;
        }
        a.push_back(std::move(row));
    }
    auto mod=[&](int x){x%=ring.p;return x<0?x+ring.p:x;};
    int answer=0;
    for(int col=0;col<old && answer<int(a.size());++col){
        int pivot=answer;
        while(pivot<int(a.size()) && a[pivot][col]==0)++pivot;
        if(pivot==int(a.size()))continue;
        std::swap(a[pivot],a[answer]);
        int inverse=1;while(mod(inverse*a[answer][col])!=1)++inverse;
        for(int j=col;j<old;++j)a[answer][j]=mod(a[answer][j]*inverse);
        for(int i=0;i<int(a.size());++i)if(i!=answer){
            int scale=a[i][col];
            for(int j=col;j<old;++j)a[i][j]=mod(a[i][j]-scale*a[answer][j]);
        }
        ++answer;
    }
    return answer;
}
void point_json(std::ostream& out,const std::map<int,int>& point,int variables){
    out<<'[';
    for(int i=0;i<variables;++i){if(i)out<<',';out<<point.at(i);}
    out<<']';
}
int certificate(std::ostream& out,const Ring& ring,const std::vector<Polynomial>& axioms,
                const Polynomial& target,int budget,int original_degree,
                const std::string& label){
    const std::vector<int> powers(10,2);
    auto reduced=domain_reduce(ring,target,powers);
    verify_reduction(ring,target,powers,reduced);
    need(reduced.remainder.empty(),"nonzero Boolean remainder: "+label);
    need(budget<=2*(original_degree+1),"weighted original-degree ledger");
    std::map<int,Polynomial> cof;
    for(int i=0;i<10;++i)if(!reduced.coefficients[i].empty())cof[i]=reduced.coefficients[i];
    out<<"{\"record\":\"NS_certificate\",\"field\":"<<ring.p<<",\"name\":\""<<label
       <<"\",\"original_axiom_degree\":"<<original_degree
       <<",\"weighted_original_ceiling\":"<<2*(original_degree+1)
       <<",\"certificate_ceiling\":"<<budget<<",\"target\":";
    write_json(out,target);
    ns_witness::write_terms(out,ring,axioms,target,cof,budget,label);
    out<<"}\n";return 1;
}
int field_case(std::ostream& out,int p){
    Ring ring(p,100);auto x=[&](int i){return ring.variable(i);};
    auto one=ring.constant(1);
    const int h=2*(p-1),k=2,old=10;
    auto d0=ring.subtract(x(0),x(3)),d1=ring.subtract(x(1),x(2));
    auto f=ring.multiply(d0,d1);
    need(degree(f)==k && f.at(Monomial{0,1})==1,"within-row quadratic target term");
    for(const auto& [mon,c]:f){
        (void)c;std::map<int,int> row_degrees;
        need(std::adjacent_find(mon.begin(),mon.end())==mon.end(),"squarefree multiplier");
        for(int id:mon)need(++row_degrees[id/2]<=2,"row degree at most two");
    }
    int fresh=old;
    std::vector<Block> blocks;
    blocks.push_back(make_block(ring,{d0,x(2),x(4),x(5),x(6),x(7),x(8)},h,fresh));
    blocks.push_back(make_block(ring,{d1,x(0),x(4),x(5),x(6),x(7),x(9)},h,fresh));
    blocks.push_back(make_block(ring,{x(4),x(5),x(6),x(7),x(8),x(9)},h,fresh));
    need(affine_rank(ring,blocks[0].inputs,old)==7,"first high rank");
    need(affine_rank(ring,blocks[1].inputs,old)==7,"second high rank");
    need(affine_rank(ring,blocks[2].inputs,old)==6,"low rank");
    need(7==2*k+3 && (p-1)*6==h*(k+1),"rank partition boundary");
    std::vector<Polynomial> axioms,fields;
    for(int i=0;i<old;++i)axioms.push_back(ring.subtract(ring.power(x(i),2),x(i)));
    for(int i=old;i<fresh;++i)fields.push_back(ring.subtract(ring.power(x(i),p),x(i)));
    out<<"{\"record\":\"system\",\"field\":"<<p<<",\"old_variables\":10,\"accuracy\":"<<h
       <<",\"multiplier_degree\":2,\"ranks\":[7,7,6],\"old_Boolean_axioms\":";
    write_polynomials(out,axioms);out<<",\"multiplier\":";write_json(out,f);
    out<<",\"source_blocks\":[";
    for(int b=0;b<3;++b){if(b)out<<',';write_block(out,blocks[b]);}
    out<<"],\"source_coefficient_field_axioms\":";write_polynomials(out,fields);
    out<<",\"scope\":\"complete local affine-family maps over Booleanity; no PHP or old-board hypothesis in this fixture\"}\n";

    std::map<int,Polynomial> images;
    for(int b=0;b<2;++b)for(int u=0;u<h;++u)for(int j=0;j<7;++j)
        images[blocks[b].variables[u][j]]
          =(u<p-1 && j==0)?ring.multiply(ring.constant(u+1),b?d0:d1):Polynomial{};
    std::vector<std::pair<int,int>> factors;
    for(int j=0;j<6;++j)for(int alpha=1;alpha<p;++alpha)factors.emplace_back(j,alpha);
    need(int(factors.size())==3*h,"fully occupied packing bins");
    for(int u=0;u<h;++u){
        std::vector<Polynomial> beta(6);auto prefix=one;
        for(int t=3*u;t<3*u+3;++t){
            auto [j,alpha]=factors[t];
            ring.accumulate(beta[j],ring.multiply(ring.constant(alpha),prefix));
            prefix=ring.multiply(prefix,ring.subtract(one,ring.multiply(ring.constant(alpha),blocks[2].inputs[j])));
        }
        for(int j=0;j<6;++j)images[blocks[2].variables[u][j]]=beta[j];
    }
    need(int(images.size())==fresh-old,"all coefficient images assigned once");
    out<<"{\"record\":\"simultaneous_map\",\"field\":"<<p<<",\"images\":[";
    bool comma=false;
    for(const auto& [id,beta]:images){
        need(degree(beta)<=k,"coefficient degree");
        if(comma)out<<',';
        comma=true;out<<'['<<id<<',';write_json(out,beta);out<<']';
    }
    out<<"]}\n";
    auto high=ring.subtract(one,ring.power(f,p-1)),low=one;
    for(const auto& g:blocks[2].inputs)low=ring.multiply(low,ring.subtract(one,ring.power(g,p-1)));
    std::vector<Polynomial> products;
    for(int b=0;b<3;++b){
        auto mapped=ring.substitute(blocks[b].product,images);
        need(mapped==(b<2?high:low),"literal product image");
        products.push_back(mapped);
    }
    out<<"{\"record\":\"product_images\",\"field\":"<<p<<",\"products\":";
    write_polynomials(out,products);out<<"}\n";
    int count=0;
    for(int b=0;b<3;++b){
        for(int j=0;j<int(blocks[b].inputs.size());++j){
            const auto& axiom=blocks[b].companions[j];
            need(degree(axiom)==2*h+1,"original companion degree");
            auto mapped=ring.substitute(axiom,images);
            need(mapped==ring.multiply(blocks[b].inputs[j],products[b]),"complete companion image");
            count+=certificate(out,ring,axioms,ring.multiply(f,mapped),
                               b<2?p*k+1:(p-1)*6+1+k,2*h+1,
                               "companion_"+std::to_string(b)+"_"+std::to_string(j));
        }
    }
    for(int id=old;id<fresh;++id){
        auto mapped=ring.substitute(fields[id-old],images);
        count+=certificate(out,ring,axioms,ring.multiply(f,mapped),(p+1)*k,p,
                           "coefficient_field_"+std::to_string(id));
    }
    for(int i=0;i<old;++i)
        count+=certificate(out,ring,axioms,ring.multiply(f,axioms[i]),k+2,2,
                           "old_Boolean_"+std::to_string(i));

    int models=0;std::vector<int> values(p);
    for(int bits=0;bits<(1<<old);++bits){
        std::map<int,int> point;
        for(int i=0;i<old;++i)point[i]=(bits>>i)&1;
        int value=ring.evaluate(f,point);if(value==0)continue;
        for(const auto& [id,beta]:images)point[id]=ring.evaluate(beta,point);
        for(const auto& equation:fields)need(ring.evaluate(equation,point)==0,"source field model");
        for(const auto& block:blocks){
            int product=ring.evaluate(block.product,point);
            for(const auto& g:block.inputs)
                need(ring.evaluate(g,point)*product%p==0,"complete source companion model");
        }
        out<<"{\"record\":\"conditional_model\",\"field\":"<<p<<",\"multiplier_value\":"<<value
           <<",\"assignment\":";point_json(out,point,fresh);out<<"}\n";
        ++models;++values[value];
    }
    need(models==256,"all nonzero-multiplier Boolean models");
    std::map<int,int> point;
    for(int i=0;i<old;++i)point[i]=int(i==4);
    need(ring.evaluate(f,point)==0,"unweighted control multiplier");
    for(int b=0;b<2;++b)
        need(ring.evaluate(ring.multiply(blocks[b].inputs[2],products[b]),point)==1,
             "unweighted high companion counterexample");
    out<<"{\"record\":\"unweighted_high_counter\",\"field\":"<<p<<",\"old_assignment\":";
    point_json(out,point,old);out<<",\"multiplier_value\":0,\"unweighted_companion_values\":[1,1]}\n";
    if(p==3){
        for(int i=0;i<old;++i)point[i]=int(i==0 || i==1);
        const int id=blocks[0].variables[1][0];
        int value=ring.evaluate(images.at(id),point);
        need(value==2 && (value*value-value)%p!=0,"non-Boolean coefficient control");
        out<<"{\"record\":\"field_domain_control\",\"field\":3,\"coefficient_id\":"<<id
           <<",\"old_assignment\":";point_json(out,point,old);
        out<<",\"coefficient_value\":2,\"Boolean_equation_value\":2,\"field_equation_value\":0}\n";
        need(values[1]==128 && values[2]==128,"both nonzero F3 multiplier values");
    }
    out<<"{\"record\":\"field_summary\",\"field\":"<<p<<",\"NS_certificates\":"<<count
       <<",\"conditional_models\":"<<models<<",\"passed\":true}\n";
    return count;
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];
        need(!std::filesystem::exists(path),"output path already exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"open output");
        out<<"{\"record\":\"schema\",\"version\":1,\"polynomials\":\"[coefficient,[variable IDs with repetitions]]\","
             "\"dimension_counts\":\"exact decimal strings\",\"scope\":\"local complete image and dimension controls\"}\n";
        dimensions(out);
        int count=field_case(out,2)+field_case(out,3);
        need(count==180,"complete certificate count");
        out<<"{\"record\":\"summary\",\"NS_certificates\":"<<count
           <<",\"conditional_models\":512,\"dimension_fixtures\":5,\"passed\":true}\n";
        need(bool(out),"write output");
        std::cout<<count<<" exact NS certificates, 512 conditional models, and 5 dimension fixtures passed.\n";
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
