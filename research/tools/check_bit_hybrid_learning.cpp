// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact ordinary-polynomial certificates for simultaneous packing and learning.
#include "ens_symbolic.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace ens_symbolic;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
int certificates=0;
int certify(std::ostream& out,const Ring& ring,const std::string& name,
            const Polynomial& target,int old,int bound){
    Polynomial pending=target,total;
    std::vector<Polynomial> cofactors(old);
    while(true){
        auto found=pending.end();
        int variable=-1;
        for(auto it=pending.begin();it!=pending.end();++it){
            auto repeat=std::adjacent_find(it->first.begin(),it->first.end());
            if(repeat!=it->first.end()){found=it;variable=*repeat;break;}
        }
        if(found==pending.end())break;
        need(variable>=0&&variable<old,"non-old variable in image");
        auto monomial=found->first;
        int scalar=found->second;
        for(int i=0;i<2;++i)
            monomial.erase(std::find(monomial.begin(),monomial.end(),variable));
        Polynomial q{{monomial,scalar}};
        ring.accumulate(cofactors[variable],q);
        auto x=ring.variable(variable);
        ring.accumulate(pending,ring.multiply(q,ring.subtract(ring.multiply(x,x),x)),-1);
    }
    need(pending.empty(),"nonzero Boolean remainder: "+name);
    int used=0;
    for(int i=0;i<old;++i){
        auto x=ring.variable(i);
        auto term=ring.multiply(cofactors[i],ring.subtract(ring.multiply(x,x),x));
        ring.accumulate(total,term);used=std::max(used,degree(term));
    }
    need(total==target&&used<=bound,"certificate identity or bound: "+name);
    out<<"{\"type\":\"Boolean_certificate\",\"name\":\""<<name<<"\",\"target\":";
    write_json(out,target);out<<",\"cofactors\":";write_polynomials(out,cofactors);
    out<<",\"degree\":"<<used<<",\"bound\":"<<bound<<"}\n";
    ++certificates;return used;
}
void point(std::ostream& out,const Ring& ring,const std::string& name,
           const Polynomial& target,int old,const std::vector<int>& ones){
    std::map<int,int> values;
    for(int i=0;i<old;++i)values[i]=0;
    for(int i:ones)values[i]=1;
    need(ring.evaluate(target,values)==1,"negative control failed: "+name);
    out<<"{\"type\":\"control\",\"name\":\""<<name<<"\",\"target\":";
    write_json(out,target);out<<",\"ones\":[";
    for(std::size_t i=0;i<ones.size();++i){if(i)out<<',';out<<ones[i];}
    out<<"],\"value\":1}\n";
}
void fixture(int h,std::ostream& out){
    constexpr int k=3;
    int D=2*h+3,B=k*(D+1),low_rank=h*(k+1),high_rank=low_rank+1;
    int second=high_rank+2,low_start=2*high_rank+1,u=low_start+low_rank,old=u+1;
    Ring ring(2,64);
    auto one=ring.constant(1),zero=ring.constant(0);
    auto f=ring.multiply(ring.multiply(ring.variable(0),ring.variable(1)),ring.variable(2));
    std::vector<Polynomial> low,ga,gb;
    for(int j=0;j<low_rank;++j)low.push_back(ring.variable(low_start+j));
    ga={ring.add(ring.variable(0),ring.variable(3)),ring.variable(3)};
    gb={ring.add(ring.variable(1),ring.variable(second)),ring.variable(second)};
    for(int j=2;j<high_rank;++j){
        ga.push_back(ring.variable(j+2));
        gb.push_back(ring.variable(second+j-1));
    }
    int fresh=old;
    std::vector<Block> blocks;
    blocks.push_back(make_block(ring,low,h,fresh));
    blocks.push_back(make_block(ring,{ring.variable(u)},h,fresh));
    blocks.push_back(make_block(ring,{ring.subtract(one,ring.variable(u))},h,fresh));
    blocks.push_back(make_block(ring,ga,h,fresh));
    blocks.push_back(make_block(ring,gb,h,fresh));
    std::map<int,Polynomial> images;
    for(int id=old;id<fresh;++id)images[id]=zero;
    for(int row=0;row<h;++row){
        Polynomial prefix=one;
        for(int j=row*(k+1);j<(row+1)*(k+1);++j){
            images[blocks[0].variables[row][j]]=prefix;
            prefix=ring.multiply(prefix,ring.subtract(one,low[j]));
        }
    }
    images[blocks[1].variables[0][0]]=one;
    images[blocks[2].variables[0][0]]=one;
    auto aa=ring.multiply(ring.variable(1),ring.variable(2));
    auto ab=ring.multiply(ring.variable(0),ring.variable(2));
    auto x3=ring.variable(3);
    auto error=ring.subtract(ring.multiply(x3,x3),x3);
    images[blocks[3].variables[0][0]]=ring.add(aa,error);
    images[blocks[3].variables[0][1]]=aa;
    images[blocks[4].variables[0][0]]=ab;
    images[blocks[4].variables[0][1]]=ab;
    int substitution_degree=0;
    for(const auto& item:images)substitution_degree=std::max(substitution_degree,degree(item.second));
    need(substitution_degree==k,"joint substitution degree");
    std::string tag="h"+std::to_string(h);
    out<<"{\"type\":\"fixture\",\"name\":\""<<tag<<"\",\"h\":"<<h
       <<",\"k\":"<<k<<",\"D\":"<<D<<",\"B\":"<<B<<",\"old_variables\":"<<old
       <<",\"joint_variables\":"<<fresh<<",\"low_rank\":"<<low_rank
       <<",\"high_rank\":"<<high_rank<<",\"weight\":";
    write_json(out,f);out<<",\"blocks\":[";
    for(std::size_t b=0;b<blocks.size();++b){if(b)out<<',';write_block(out,blocks[b]);}
    out<<"],\"coefficient_images\":[";
    bool comma=false;
    for(const auto& [id,image]:images){
        if(comma)out<<',';
        comma=true;out<<'['<<id<<',';write_json(out,image);out<<']';
    }
    out<<"]}\n";
    for(int b=3;b<5;++b){
        Polynomial membership;
        for(std::size_t j=0;j<blocks[b].inputs.size();++j)
            ring.accumulate(membership,ring.multiply(images.at(blocks[b].variables[0][j]),
                                                    blocks[b].inputs[j]));
        certify(out,ring,tag+"/membership-"+std::to_string(b),
                ring.subtract(f,membership),old,k);
    }
    for(std::size_t b=0;b<blocks.size();++b)
        for(std::size_t j=0;j<blocks[b].companions.size();++j){
            need(degree(blocks[b].companions[j])==2*h+1,"original companion degree");
            auto target=ring.multiply(f,ring.substitute(blocks[b].companions[j],images));
            certify(out,ring,tag+"/companion-"+std::to_string(b)+"-"+std::to_string(j),
                    target,old,k*(2*h+1)+k);
        }
    for(int id=old;id<fresh;++id){
        auto image=images.at(id);
        certify(out,ring,tag+"/field-"+std::to_string(id),
                ring.multiply(f,ring.subtract(ring.multiply(image,image),image)),old,3*k);
    }
    for(int id=0;id<old;++id){
        auto x=ring.variable(id);
        certify(out,ring,tag+"/old-field-"+std::to_string(id),
                ring.multiply(f,ring.subtract(ring.multiply(x,x),x)),old,k+2);
    }
    int saturating=blocks[0].variables[0][k];
    auto image=images.at(saturating);
    auto weighted_field=ring.multiply(f,ring.subtract(ring.multiply(image,image),image));
    auto saturated=ring.multiply(ring.power(image,D-2),weighted_field);
    need(certify(out,ring,tag+"/saturating-field-cofactor",saturated,old,B)==B,
         "the final image-degree control did not reach B");
    point(out,ring,tag+"/weight-omitted",
          ring.substitute(blocks[3].companions[0],images),old,{0});
    point(out,ring,tag+"/low-packing-omitted",
          ring.multiply(f,blocks[0].inputs[0]),old,{0,1,2,low_start});
    point(out,ring,tag+"/f-nonzero-on-low-cover-zero",f,old,{0,1,2});
    out<<"{\"type\":\"fixture_summary\",\"name\":\""<<tag
       <<"\",\"substitution_degree\":"<<substitution_degree
       <<",\"sequential_degree_product\":6,\"opposing_low_zero_spaces_cover_cube\":true,"
         "\"passed\":true}\n";
}
void row_boundary(std::ostream& out){
    Ring ring(2,16);
    auto one=ring.constant(1);
    std::vector<Polynomial> equalities;
    Polynomial f;
    for(int a=0;a<3;++a)for(int b=a+1;b<3;++b){
        Polynomial e=one;
        for(int t=0;t<2;++t)
            e=ring.multiply(e,ring.add(one,ring.add(ring.variable(2*a+t),ring.variable(2*b+t))));
        equalities.push_back(e);ring.accumulate(f,e);
    }
    need(!f.empty()&&degree(f)==2,"row-linear boundary polynomial");
    for(const auto& [monomial,coefficient]:f){
        (void)coefficient;
        std::vector<int> rows;
        for(int variable:monomial)rows.push_back(variable/2);
        std::sort(rows.begin(),rows.end());
        need(std::adjacent_find(rows.begin(),rows.end())==rows.end(),"not row-linear");
    }
    need(f.at({})==1,"nonzero boundary evaluation");
    out<<"{\"type\":\"row_linear_boundary\",\"n\":4,\"ell\":2,\"k\":2,"
         "\"cube_hypothesis_holds\":false,\"equality_axioms\":";
    write_polynomials(out,equalities);out<<",\"unit_cofactor_sum\":";
    write_json(out,f);out<<",\"ordinary_NS_degree\":2,\"zero_point_value\":1}\n";
}
int main(int argc,char** argv){
    try{
        need(argc==3&&std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];
        need(!std::filesystem::exists(path),"refusing existing output");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot create output");
        out<<"{\"type\":\"schema\",\"version\":1,\"field\":2,"
               "\"scope\":\"mixed generator-image NS certificates over Booleanity, not a PHP refutation\","
               "\"polynomials\":\"[coefficient, sorted variable list with repetitions]\"}\n";
        fixture(1,out);fixture(2,out);row_boundary(out);
        out<<"{\"type\":\"summary\",\"fixtures\":2,\"Boolean_certificates\":"<<certificates
           <<",\"controls\":7,\"passed\":true}\n";
        out.close();need(bool(out),"write failed");
        std::cout<<"Passed "<<certificates<<" complete Boolean NS image certificates, "
                    "two mixed-rank fixtures, and seven controls.\n";
    }catch(const std::exception& error){std::cerr<<"ERROR: "<<error.what()<<'\n';return 1;}
}
