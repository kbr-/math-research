// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact cut matrices, balanced binary codes, and composed selector certificates.
#include "sparse_polynomial.hpp"
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
using namespace sparse_polynomial;
using Word=std::uint64_t;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
template<class T>void array(std::ostream& out,const std::vector<T>& a){
    out<<'[';for(std::size_t i=0;i<a.size();++i){if(i)out<<',';out<<a[i];}out<<']';
}
int rank(std::vector<Word> a){
    std::vector<Word> basis(64);int answer=0;
    for(auto x:a)while(x){
        int j=63-__builtin_clzll(x);
        if(basis[j])x^=basis[j];else{basis[j]=x;++answer;break;}
    }
    return answer;
}
std::vector<Word> subset_sums(const std::vector<Word>& columns){
    std::vector<Word> result(Word(1)<<columns.size());
    for(std::size_t S=1;S<result.size();++S){
        unsigned j=__builtin_ctzll(S);
        result[S]=result[S^(Word(1)<<j)]^columns[j];
    }
    return result;
}
void matrix_case(std::ostream& out,const std::string& id,
                 const std::vector<Word>& columns,int rows,Word side,Word target,
                 bool require_balance){
    std::vector<int> left_ids,right_ids;
    std::vector<Word> left,right;
    for(std::size_t i=0;i<columns.size();++i){
        if((side>>i)&1){left_ids.push_back(int(i));left.push_back(columns[i]);}
        else{right_ids.push_back(int(i));right.push_back(columns[i]);}
    }
    need(left.size()==4 && right.size()==4,"small cut size");
    int rl=rank(left),rr=rank(right),all=rank(columns);
    need(all==rows,"full rank fixture");
    if(require_balance)need(rl>=rows-1 && rr>=rows-1,"half-rank consequence");
    auto l=subset_sums(left),r=subset_sums(right);
    std::vector<Word> values(l.size());
    for(std::size_t i=0;i<l.size();++i)for(std::size_t j=0;j<r.size();++j)
        if((l[i]^r[j])==target)values[i]|=Word(1)<<j;
    auto coefficients=values;
    for(unsigned b=0;b<left.size();++b)
        for(std::size_t i=0;i<coefficients.size();++i)
            if((i>>b)&1)coefficients[i]^=coefficients[i^(Word(1)<<b)];
    for(unsigned b=0;b<right.size();++b)
        for(auto& row:coefficients)for(std::size_t j=0;j<r.size();++j)
            if(((j>>b)&1) && ((row>>(j^(Word(1)<<b)))&1))row^=Word(1)<<j;
    int actual=rank(values),expected=1<<(rl+rr-all);
    need(actual==expected && rank(coefficients)==expected,"cut-rank identity");
    out<<"{\"type\":\"cut_matrix\",\"fixture\":\""<<id<<"\",\"left\":";
    array(out,left_ids);out<<",\"right\":";array(out,right_ids);
    out<<",\"target\":"<<target<<",\"left_rank\":"<<rl<<",\"right_rank\":"<<rr
       <<",\"rank\":"<<actual<<",\"evaluation_rows\":";array(out,values);
    out<<",\"multilinear_coefficient_rows\":";array(out,coefficients);out<<"}\n";
}
void small_matrices(std::ostream& out){
    std::vector<Word> columns(8);std::iota(columns.begin(),columns.end(),0);
    out<<"{\"type\":\"cut_fixture\",\"id\":\"cube3\",\"rank\":3,\"columns\":";
    array(out,columns);out<<",\"all_nonzero_codeword_weights\":4}\n";
    for(Word side=0;side<256;++side)if(__builtin_popcountll(side)==4)
        for(Word target=0;target<8;++target)matrix_case(out,"cube3",columns,3,side,target,true);
    columns={1,1,2,2,4,4,8,8};
    need(rank(columns)==4,"control full rank");
    out<<"{\"type\":\"cut_fixture\",\"id\":\"unbalanced_pairs\",\"rank\":4,\"columns\":";
    array(out,columns);out<<",\"violating_codeword\":1,\"weight\":2,"
       "\"half_rank_required\":3,\"selected_half_rank\":2,\"cut_rank\":1}\n";
    matrix_case(out,"unbalanced_pairs",columns,4,15,15,false);
}
int source_template(std::ostream& out,int h){
    Ring ring(2,64);int r=h*h;auto one=ring.constant(1),z=ring.variable(r);
    std::vector<Polynomial> t,chi;
    for(int j=0;j<r;++j)t.push_back(ring.variable(j));
    for(int b=0;b<h;++b){
        auto value=one;
        for(int j=0;j<h;++j)value=ring.multiply(value,t[b*h+j]);
        chi.push_back(value);
    }
    auto parent=one;
    for(const auto& c:chi)parent=ring.multiply(parent,ring.add(c,z));
    out<<"{\"type\":\"source_template\",\"accuracy\":"<<h<<",\"linear_form_count\":"<<r
       <<",\"modifier_variable\":"<<r<<",\"old_product_image\":";
    write_json(out,parent);
    out<<",\"original_child_product_degree\":"<<2*h
       <<",\"original_parent_product_degree\":"<<h*(2*h+1)
       <<",\"scalar_map\":\"identity coefficient matrices; modifier remains free\","
       "\"linear_substitution\":\"t_j=sum_i A[j,i]*x_i; t_j^2-t_j maps to sum_i A[j,i]*(x_i^2-x_i)\","
       "\"certificates\":[";
    int count=0;
    auto cert=[&](const std::string& name,const Polynomial& target,
                  const std::vector<std::pair<Polynomial,int>>& terms,int budget){
        Polynomial sum;int degree_used=0;
        if(count)out<<',';
        out<<"{\"name\":\""<<name<<"\",\"target\":";write_json(out,target);
        out<<",\"original_budget\":"<<budget<<",\"terms\":[";
        for(std::size_t k=0;k<terms.size();++k){
            const auto& [q,v]=terms[k];auto x=ring.variable(v);
            auto axiom=ring.subtract(ring.multiply(x,x),x),product=ring.multiply(q,axiom);
            ring.accumulate(sum,product);degree_used=std::max(degree_used,degree(product));
            if(k)out<<',';
            out<<"{\"cofactor\":";write_json(out,q);out<<",\"axiom\":";
            write_json(out,axiom);out<<'}';
        }
        need(sum==target && degree_used<=budget,"template NS identity");
        out<<"],\"witness_degree\":"<<degree_used<<'}';++count;
    };
    for(int b=0;b<h;++b)for(int j=0;j<h;++j){
        auto q=one;
        for(int k=0;k<h;++k)if(k!=j)q=ring.multiply(q,t[b*h+k]);
        cert("child"+std::to_string(b)+"/"+std::to_string(j),
             ring.multiply(ring.add(one,t[b*h+j]),chi[b]),{{q,b*h+j}},2*h+1);
    }
    for(int b=0;b<h;++b){
        auto other=one;
        for(int c=0;c<h;++c)if(c!=b)other=ring.multiply(other,ring.add(chi[c],z));
        std::vector<std::pair<Polynomial,int>> terms;
        for(int j=0;j<h;++j){
            auto q=other;
            for(int k=0;k<h;++k)if(k!=j)
                q=ring.multiply(q,ring.power(t[b*h+k],k<j?2:1));
            terms.push_back({q,b*h+j});
        }
        terms.push_back({other,r});
        cert("parent/"+std::to_string(b),
             ring.multiply(ring.add(ring.add(one,chi[b]),z),parent),terms,2*h*h+3*h);
    }
    out<<"],\"certificate_count\":"<<count<<"}\n";
    return count;
}
void balanced_code(std::ostream& out,int h){
    int r=h*h,v=64*(r+1);
    Word seed=202609140115ULL+Word(h),mask=(Word(1)<<r)-1;
    std::mt19937_64 engine(seed);
    for(int trial=1;trial<=256;++trial){
        std::vector<Word> columns(v);for(auto& c:columns)c=engine()&mask;
        std::vector<int> weights;int minimum=v,maximum=0;
        for(Word a=1;a<=mask;++a){
            int weight=0;
            for(auto c:columns)weight+=__builtin_parityll(a&c);
            weights.push_back(weight);minimum=std::min(minimum,weight);maximum=std::max(maximum,weight);
        }
        bool accepted=8*minimum>=3*v && 8*maximum<=5*v;
        out<<"{\"type\":\"code_attempt\",\"accuracy\":"<<h<<",\"rank\":"<<r
           <<",\"variables\":"<<v<<",\"seed\":"<<seed<<",\"trial\":"<<trial
           <<",\"accepted\":"<<(accepted?"true":"false")<<",\"columns\":";
        array(out,columns);out<<",\"nonzero_codeword_weights_in_mask_order\":";
        array(out,weights);
        out<<",\"minimum_weight\":"<<minimum<<",\"maximum_weight\":"<<maximum
           <<",\"required_half_rank\":"<<r-1<<",\"log2_width_lower_bound\":"<<r-2<<"}\n";
        if(accepted){
            need(rank(columns)==r,"accepted code full rank");
            std::cout<<"h="<<h<<", r="<<r<<", v="<<v<<": all "<<mask
                     <<" nonzero codeword weights in ["<<minimum<<','<<maximum
                     <<"]; every-order width >= 2^"<<r-2<<".\n";
            return;
        }
    }
    throw std::runtime_error("No accepted code in 256 trials; complete attempts retained");
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");
        out<<"{\"type\":\"schema\",\"version\":1,\"field\":2,"
              "\"matrix_rows\":\"integers encoding bits in increasing column index\","
              "\"code_columns\":\"r-bit column vectors, least-significant row first\","
              "\"polynomials\":\"sorted variable lists retain repetitions; templates compose with saved linear forms\"}\n";
        small_matrices(out);int certificates=0;
        for(int h:{2,3,4}){balanced_code(out,h);certificates+=source_template(out,h);}
        need(certificates==38,"certificate count");
        out<<"{\"type\":\"summary\",\"complete_cut_matrices\":561,\"balanced_code_witnesses\":3,"
              "\"source_template_certificates\":38,\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<"Passed 561 full cut matrices, three complete code witnesses, and 38 NS templates.\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
