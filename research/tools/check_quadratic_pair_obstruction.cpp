// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Full Boolean degree-two evaluation kernels and cubic ideal controls.
#include "domain_polynomial.hpp"
#include "ns_witness.hpp"
#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <set>
using namespace domain_polynomial;
using Row=std::array<std::uint64_t,2>;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
bool bit(const Row& row,unsigned j){return (row[j/64]>>(j%64))&1;}
void set_bit(Row& row,unsigned j){row[j/64]|=std::uint64_t(1)<<(j%64);}
void bits_json(std::ostream& out,const Row& row,unsigned width){
    out<<'"';for(unsigned j=0;j<width;++j)out<<bit(row,j);out<<'"';
}
void rows_json(std::ostream& out,const std::vector<Row>& rows,unsigned width){
    out<<'[';for(unsigned i=0;i<rows.size();++i){if(i)out<<',';bits_json(out,rows[i],width);}out<<']';
}
void numbers(std::ostream& out,const std::vector<unsigned>& v){
    out<<'[';for(unsigned i=0;i<v.size();++i){if(i)out<<',';out<<v[i];}out<<']';
}
unsigned scalar_rank(std::vector<unsigned> rows,unsigned width){
    unsigned rank=0;
    for(unsigned j=0;j<width && rank<rows.size();++j){
        unsigned i=rank;while(i<rows.size() && !((rows[i]>>j)&1))++i;
        if(i==rows.size())continue;
        std::swap(rows[i],rows[rank]);
        for(unsigned k=0;k<rows.size();++k)if(k!=rank && ((rows[k]>>j)&1))rows[k]^=rows[rank];
        ++rank;
    }
    return rank;
}
int check(std::ostream& out,unsigned groups,unsigned pairs){
    unsigned variables=2*pairs*groups;need(variables<=12 && (pairs==1 || pairs==2),"small complete fixture");
    std::vector<unsigned> features{0};
    for(unsigned i=0;i<variables;++i)features.push_back(1u<<i);
    for(unsigned i=0;i<variables;++i)for(unsigned j=i+1;j<variables;++j)features.push_back((1u<<i)|(1u<<j));
    need(features.size()<=128,"two-word feature rows");
    std::vector<unsigned> points;
    for(unsigned point=0;point<(1u<<variables);++point){
        bool zero=true;
        for(unsigned g=0;g<groups;++g){
            bool q=false;
            for(unsigned j=0;j<pairs;++j){unsigned start=2*pairs*g+2*j;q^=((point>>start)&3)==3;}
            zero=zero && !q;
        }
        if(zero)points.push_back(point);
    }
    unsigned expected_points=1;for(unsigned g=0;g<groups;++g)expected_points*=pairs==1?3:10;
    need(points.size()==expected_points,"complete common zero set");
    std::vector<Row> matrix(points.size(),Row{0,0});
    for(unsigned i=0;i<points.size();++i)for(unsigned j=0;j<features.size();++j)
        if((points[i]&features[j])==features[j])set_bit(matrix[i],j);
    auto reduced=matrix;std::vector<unsigned> pivots;
    for(unsigned j=0;j<features.size() && pivots.size()<reduced.size();++j){
        unsigned rank=pivots.size(),i=rank;while(i<reduced.size() && !bit(reduced[i],j))++i;
        if(i==reduced.size())continue;
        std::swap(reduced[i],reduced[rank]);
        for(unsigned k=0;k<reduced.size();++k)if(k!=rank && bit(reduced[k],j)){
            reduced[k][0]^=reduced[rank][0];reduced[k][1]^=reduced[rank][1];
        }
        pivots.push_back(j);
    }
    need(pivots.size()+groups==features.size(),"degree-two vanishing kernel has precisely the input rank");
    std::vector<Row> kernel;
    for(unsigned j=0;j<features.size();++j)if(std::find(pivots.begin(),pivots.end(),j)==pivots.end()){
        Row vector{0,0};set_bit(vector,j);
        for(unsigned i=0;i<pivots.size();++i)if(bit(reduced[i],j))set_bit(vector,pivots[i]);
        for(const auto& row:matrix)need((__builtin_parityll(row[0]&vector[0])^__builtin_parityll(row[1]&vector[1]))==0,"kernel reconstruction");
        kernel.push_back(vector);
    }
    std::vector<Row> canonical;Ring r(2,20);std::vector<Polynomial> inputs,axioms;
    for(unsigned i=0;i<variables;++i){auto x=r.variable(i);axioms.push_back(r.subtract(r.power(x,2),x));}
    for(unsigned g=0;g<groups;++g){
        Row vector{0,0};Polynomial q;
        for(unsigned j=0;j<pairs;++j){
            unsigned start=2*pairs*g+2*j,mask=(1u<<start)|(1u<<(start+1));
            auto it=std::find(features.begin(),features.end(),mask);need(it!=features.end(),"input feature column");
            set_bit(vector,it-features.begin());r.accumulate(q,r.multiply(r.variable(start),r.variable(start+1)));
        }
        canonical.push_back(vector);inputs.push_back(q);
    }
    need(std::set<Row>(kernel.begin(),kernel.end())==std::set<Row>(canonical.begin(),canonical.end()),"canonical full vanishing-ideal basis");
    axioms.insert(axioms.end(),inputs.begin(),inputs.end());
    out<<"{\"record\":\"quadratic_vanishing_matrix\",\"groups\":"<<groups<<",\"pairs_per_input\":"<<pairs
       <<",\"old_variables\":"<<variables<<",\"features\":";numbers(out,features);
    out<<",\"common_zeroes\":";numbers(out,points);out<<",\"inputs\":";write_polynomials(out,inputs);
    out<<",\"ordinary_generators\":";write_polynomials(out,axioms);out<<",\"pivots\":";numbers(out,pivots);
    out<<",\"matrix\":";rows_json(out,matrix,features.size());out<<",\"rref\":";rows_json(out,reduced,features.size());
    out<<",\"kernel_basis\":";rows_json(out,kernel,features.size());out<<",\"evaluation_rank\":"<<pivots.size()
       <<",\"kernel_dimension\":"<<kernel.size()<<",\"independent_affine_pair_obstruction\":"<<(pairs==2?"true":"false")
       <<",\"scope\":\"complete degree-two Boolean function space on the specified zero set\",\"passed\":true}\n";
    for(unsigned choice=1;choice<(1u<<groups);++choice){
        std::vector<unsigned> polar(variables);
        for(unsigned g=0;g<groups;++g)if((choice>>g)&1)for(unsigned j=0;j<pairs;++j){
            unsigned start=2*pairs*g+2*j;polar[start]=1u<<(start+1);polar[start+1]=1u<<start;
        }
        unsigned rank=scalar_rank(polar,variables),expected=2*pairs*__builtin_popcount(choice);
        need(rank==expected && (pairs==1 || rank>=4),"nonzero kernel polar ranks");
        out<<"{\"record\":\"kernel_polar_rank\",\"groups\":"<<groups<<",\"pairs_per_input\":"<<pairs
           <<",\"input_combination\":"<<choice<<",\"rank\":"<<rank<<",\"polar_rows\":";numbers(out,polar);out<<"}\n";
    }
    int certificates=0;
    if(pairs==2)for(unsigned g=0;g<groups;++g){
        unsigned start=4*g;auto selector=r.subtract(r.constant(1),r.variable(start+2));
        auto target=r.multiply(r.multiply(r.variable(start),r.variable(start+1)),selector);
        std::map<int,Polynomial> cof{{int(variables+g),selector},{int(start+2),r.variable(start+3)}};
        out<<"{\"record\":\"NS_certificate\",\"groups\":"<<groups<<",\"name\":\"cubic_product_"<<g
           <<"\",\"target\":";write_json(out,target);out<<",\"budget\":3";
        ns_witness::write_terms(out,r,axioms,target,cof,3,"cubic product");out<<"}\n";++certificates;
    }
    return certificates;
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");
        out<<"{\"record\":\"schema\",\"version\":1,\"field\":2,\"feature_encoding\":\"squarefree monomial bitmasks\","
             "\"matrix_encoding\":\"binary strings in feature order\","
             "\"polynomial_encoding\":\"[coefficient,[variable IDs with repetitions]]\"}\n";
        int certificates=check(out,1,1);for(unsigned groups:{1u,2u,3u})certificates+=check(out,groups,2);
        need(certificates==6,"complete cubic certificate count");
        out<<"{\"record\":\"summary\",\"complete_evaluation_matrices\":4,\"ordinary_NS_certificates\":6,\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<"Four full degree-two vanishing kernels and six ordinary cubic certificates passed.\n";
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
