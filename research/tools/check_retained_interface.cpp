// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact retained-interface NS tests with additional old-affine blocks.
#include "ns_witness.hpp"
#include "binary_php.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
using namespace ens_symbolic;
using binary_php::Word;
using binary_php::Bits;
void need(bool value,const char* message){if(!value)throw std::runtime_error(message);}
void xor_into(Bits& a,const Bits& b){need(a.size()==b.size(),"XOR size");for(unsigned i=0;i<a.size();++i)a[i]^=b[i];}
Monomial monomial(Word mask){Monomial m;while(mask){int v=__builtin_ctzll(mask);mask&=mask-1;m.push_back(v);}return m;}
void integers(std::ostream& out,const std::vector<int>& values){
    out<<'[';for(unsigned i=0;i<values.size();++i){if(i)out<<',';out<<values[i];}out<<']';
}
struct InterfaceBaseline {
    int rank=0,width=0;
    std::vector<Bits> residuals;
    std::vector<int> values;
};

bool one_case(std::ostream& out,int helpers,InterfaceBaseline& baseline){
    Ring ring(2,32);const int D=5;int fresh=6;
    std::vector<Polynomial> xs,ys,all;
    for(int i=0;i<3;++i){xs.push_back(ring.variable(i));ys.push_back(ring.variable(i+3));}
    all=xs;all.insert(all.end(),ys.begin(),ys.end());
    std::vector<Block> blocks;
    blocks.push_back(make_block(ring,xs,1,fresh));
    blocks.push_back(make_block(ring,ys,1,fresh));
    blocks.push_back(make_block(ring,all,1,fresh));
    for(int a=0;a<helpers;++a){
        std::vector<Polynomial> input;
        for(int i=0;i<3;++i){
            auto g=ring.add(xs[i],ys[i]);
            if(a==1 && i==0)ring.accumulate(g,ring.constant(1));
            input.push_back(g);
        }
        blocks.push_back(make_block(ring,input,1,fresh));
    }
    const int variables=fresh;
    need(variables==18+3*helpers,"source variable count");
    std::vector<Polynomial> axioms;
    for(const auto& b:blocks)for(const auto& e:b.companions){need(degree(e)==3,"original companion degree");axioms.push_back(e);}
    const int companion_count=int(axioms.size());
    for(int v=0;v<variables;++v){auto x=ring.variable(v);axioms.push_back(ring.subtract(ring.multiply(x,x),x));}
    auto target_poly=ring.subtract(blocks[2].product,ring.multiply(blocks[0].product,blocks[1].product));
    std::vector<Word> monomials{0};Word limit=Word(1)<<variables;
    for(int d=1;d<=D;++d)for(Word mask=(Word(1)<<d)-1;mask<limit;){
        monomials.push_back(mask);Word low=mask&(-mask),raised=mask+low;
        mask=raised+(((raised^mask)/low)>>2);
    }
    const int width=int(monomials.size());std::unordered_map<Word,int> position;
    for(int i=0;i<width;++i)position.emplace(monomials[i],i);
    std::vector<Word> cofactors;
    for(Word mask:monomials){if(__builtin_popcountll(mask)>D-3)break;cofactors.push_back(mask);}
    auto vector=[&](const Polynomial& p,Word q){
        Bits value=binary_php::blank(width);
        for(const auto& [m,c]:p){Word mask=q;for(int v:m){need(v<variables,"unexpected variable");mask|=Word(1)<<v;}
            need(c==1 && position.count(mask),"Boolean degree range");binary_php::flip(value,position.at(mask));}
        return value;
    };
    out<<"{\"record\":\"case\",\"helpers\":"<<helpers<<",\"degree\":5,\"variables\":"<<variables
       <<",\"companion_count\":"<<companion_count<<",\"columns\":"<<width<<",\"blocks\":[";
    for(unsigned i=0;i<blocks.size();++i){if(i)out<<',';write_block(out,blocks[i]);}
    out<<"],\"axioms\":";write_polynomials(out,axioms);
    out<<",\"monomial_masks\":[";
    for(int i=0;i<width;++i){if(i)out<<',';out<<monomials[i];}out<<"]}\n";
    const int rows_expected=companion_count*int(cofactors.size());
    binary_php::Space span(width);std::vector<Bits> combinations(width);
    std::vector<std::pair<int,Word>> original_rows;original_rows.reserve(rows_expected);
    for(int f=0;f<companion_count;++f)for(Word q:cofactors){
        const int row=int(original_rows.size());original_rows.emplace_back(f,q);
        Bits raw=vector(axioms[f],q);std::vector<int> trace;
        int pivot=span.add(raw,&trace);
        if(pivot>=0){
            auto combination=binary_php::blank(rows_expected);binary_php::flip(combination,row);
            for(int p:trace)xor_into(combination,combinations[p]);
            combinations[pivot]=std::move(combination);
        }
        out<<"{\"record\":\"row\",\"helpers\":"<<helpers<<",\"row\":"<<row<<",\"axiom\":"<<f
           <<",\"cofactor_mask\":"<<q<<",\"image\":";binary_php::sparse_json(out,raw);
        out<<",\"trace\":[";for(unsigned i=0;i<trace.size();++i){if(i)out<<',';out<<trace[i];}
        out<<"],\"pivot\":"<<pivot<<"}\n";
    }
    need(int(original_rows.size())==rows_expected,"complete row inventory");
    auto emit_proof=[&](const Polynomial& statement,const std::vector<int>& trace){
        Bits combination=binary_php::blank(rows_expected);
        for(int p:trace)xor_into(combination,combinations[p]);
        std::map<int,Polynomial> proof;
        for(int row:binary_php::support(combination)){
            auto [f,q]=original_rows[row];ring.accumulate(proof[f],Polynomial{{monomial(q),1}});
        }
        Polynomial difference=statement;
        for(const auto& [f,q]:proof)ring.accumulate(difference,ring.multiply(q,axioms[f]));
        Polynomial normal;
        for(const auto& [original,c]:difference){
            Monomial m=original;
            while(true){
                auto repeated=std::adjacent_find(m.begin(),m.end());if(repeated==m.end())break;
                int v=*repeated;Monomial q=m;
                q.erase(std::find(q.begin(),q.end(),v));q.erase(std::find(q.begin(),q.end(),v));
                ring.accumulate(proof[companion_count+v],Polynomial{{q,c}});
                m.erase(std::find(m.begin(),m.end(),v));
            }
            ring.accumulate(normal,Polynomial{{m,c}});
        }
        need(normal.empty(),"ordinary Boolean lift remainder");
        out<<",\"NS_row_combination\":";binary_php::sparse_json(out,combination);
        ns_witness::write_terms(out,ring,axioms,statement,proof,D,"retained_interface_lower_degree");
    };
    Bits target=vector(target_poly,0);std::vector<int> target_trace;
    Bits remainder=span.reduce(target,&target_trace);const bool member=binary_php::zero(remainder);
    Bits target_dual;
    out<<"{\"record\":\"target\",\"helpers\":"<<helpers<<",\"polynomial\":";write_json(out,target_poly);
    out<<",\"vector\":";binary_php::sparse_json(out,target);
    out<<",\"trace\":";integers(out,target_trace);
    out<<",\"remainder\":";binary_php::sparse_json(out,remainder);
    if(member){
        emit_proof(target_poly,target_trace);
    }else{
        Bits dual=span.separating_dual(target);std::map<int,int> model;
        for(int v=0;v<variables;++v)model[v]=0;
        if(helpers==2)model[blocks[4].variables[0][0]]=1;
        for(const auto& f:axioms)need(ring.evaluate(f,model)==0,"normalizing model");
        need(ring.evaluate(target_poly,model)==0,"model preserves target value zero");
        Word model_mask=0;for(auto [v,value]:model)if(value)model_mask|=Word(1)<<v;
        if(!binary_php::bit(dual,position.at(0)))for(int i=0;i<width;++i)
            if((monomials[i]&~model_mask)==0)binary_php::flip(dual,i);
        need(binary_php::bit(dual,position.at(0)) && binary_php::dot(target,dual),"normalized target separator");
        for(auto [f,q]:original_rows)need(binary_php::dot(vector(axioms[f],q),dual)==0,"dual generator multiple");
        out<<",\"normalized_separating_dual\":";binary_php::sparse_json(out,dual);
        out<<",\"normalizing_model_mask\":"<<model_mask;
        target_dual=std::move(dual);
    }
    out<<"}\n";
    // The formal old/whole-product interface has weights one and two.
    // Compare its entire relation kernel, rather than only the OR target.
    std::vector<Polynomial> features;
    std::vector<std::pair<Word,Word>> feature_masks;
    for(Word products=0;products<8;++products)for(Word old=0;old<64;++old){
        if(__builtin_popcountll(old)+2*__builtin_popcountll(products)>D)continue;
        Polynomial f{{monomial(old),1}};
        for(int b=0;b<3;++b)if(products&(Word(1)<<b))f=ring.multiply(f,blocks[b].product);
        need(degree(f)<=D,"interface original degree");
        features.push_back(std::move(f));feature_masks.emplace_back(old,products);
    }
    const int feature_count=int(features.size());need(feature_count==210,"interface inventory");
    if(helpers==0){need(!target_dual.empty(),"baseline target separator");baseline.width=width;}
    else need(int(baseline.residuals.size())==feature_count,"baseline interface inventory");
    binary_php::Space interface_span(width);
    std::vector<Bits> feature_combinations(width),feature_images;
    std::vector<int> pivot_values(width,0);
    Bits new_relation;bool baseline_dual_extends=true;
    for(int f=0;f<feature_count;++f){
        Bits image=vector(features[f],0);feature_images.push_back(image);
        std::vector<int> source_trace,feature_trace;
        Bits source_remainder=span.reduce(image,&source_trace);
        if(helpers==0){baseline.residuals.push_back(source_remainder);baseline.values.push_back(binary_php::dot(image,target_dual));}
        Bits feature_remainder=interface_span.reduce(source_remainder,&feature_trace);
        Bits combination=binary_php::blank(feature_count);binary_php::flip(combination,f);
        int rhs=baseline.values[f];
        for(int p:feature_trace){xor_into(combination,feature_combinations[p]);rhs^=pivot_values[p];}
        int pivot=binary_php::highest(feature_remainder);
        if(pivot>=0){
            interface_span.insert_reduced(feature_remainder,pivot);
            feature_combinations[pivot]=combination;pivot_values[pivot]=rhs;
        }else{
            if(rhs)baseline_dual_extends=false;
            Bits old_remainder=binary_php::blank(baseline.width);
            for(int index:binary_php::support(combination))xor_into(old_remainder,baseline.residuals[index]);
            if(!binary_php::zero(old_remainder) && new_relation.empty())new_relation=combination;
        }
        out<<"{\"record\":\"interface_feature\",\"helpers\":"<<helpers<<",\"feature\":"<<f
           <<",\"old_mask\":"<<feature_masks[f].first<<",\"product_mask\":"<<feature_masks[f].second
           <<",\"image\":";binary_php::sparse_json(out,image);
        out<<",\"source_trace\":";integers(out,source_trace);
        out<<",\"source_remainder\":";binary_php::sparse_json(out,source_remainder);
        out<<",\"interface_trace\":";integers(out,feature_trace);
        out<<",\"interface_remainder\":";binary_php::sparse_json(out,feature_remainder);
        out<<",\"feature_combination\":";binary_php::sparse_json(out,combination);
        out<<",\"pivot\":"<<pivot<<",\"baseline_value\":"<<baseline.values[f]<<",\"reduced_value\":"<<rhs<<"}\n";
    }
    if(helpers==0)baseline.rank=interface_span.rank;
    need(interface_span.rank<=baseline.rank,"source extension cannot enlarge interface quotient");
    const bool preserves_interface=interface_span.rank==baseline.rank;
    need(preserves_interface==new_relation.empty(),"interface rank/kernel agreement");
    if(!new_relation.empty()){
        Polynomial statement;Bits old_remainder=binary_php::blank(baseline.width);
        for(int f:binary_php::support(new_relation)){
            ring.accumulate(statement,features[f]);xor_into(old_remainder,baseline.residuals[f]);
        }
        std::vector<int> trace;need(binary_php::zero(span.reduce(vector(statement,0),&trace)),"new interface relation");
        out<<"{\"record\":\"new_interface_relation\",\"helpers\":"<<helpers<<",\"features\":";
        binary_php::sparse_json(out,new_relation);out<<",\"polynomial\":";write_json(out,statement);
        out<<",\"baseline_remainder\":";binary_php::sparse_json(out,old_remainder);
        emit_proof(statement,trace);out<<"}\n";
    }
    if(baseline_dual_extends){
        Bits seed=binary_php::blank(width);
        for(int p=0;p<width;++p)if(!interface_span.rows[p].empty()){
            need(!binary_php::bit(span.pivots,p),"interface pivot must be source-free");
            if(binary_php::dot(interface_span.rows[p],seed)!=pivot_values[p])binary_php::flip(seed,p);
        }
        Bits dual=span.complete_dual(seed);
        for(int f=0;f<feature_count;++f)need(binary_php::dot(feature_images[f],dual)==baseline.values[f],"complete interface dual values");
        for(auto [f,q]:original_rows)need(binary_php::dot(vector(axioms[f],q),dual)==0,"extended dual generator multiple");
        need(binary_php::bit(dual,position.at(0)) && binary_php::dot(target,dual),"extended normalized OR separator");
        out<<"{\"record\":\"interface_dual_extension\",\"helpers\":"<<helpers<<",\"dual\":";
        binary_php::sparse_json(out,dual);out<<",\"all_210_values_verified\":true,\"passed\":true}\n";
    }
    out<<"{\"record\":\"interface_result\",\"helpers\":"<<helpers<<",\"features\":"<<feature_count
       <<",\"quotient_rank\":"<<interface_span.rank<<",\"baseline_rank\":"<<baseline.rank
       <<",\"preserves_entire_interface\":"<<(preserves_interface?"true":"false")
       <<",\"baseline_dual_extends\":"<<(baseline_dual_extends?"true":"false")<<",\"passed\":true}\n";
    std::map<int,Polynomial> upper;
    for(int i=0;i<3;++i){
        ring.accumulate(upper[6+i],blocks[0].prefix[i]);
        ring.accumulate(upper[9+i],ring.multiply(blocks[0].product,blocks[1].prefix[i]));
        ring.accumulate(upper[i],ring.multiply(blocks[1].product,blocks[2].prefix[i]),-1);
        ring.accumulate(upper[3+i],ring.multiply(blocks[0].product,blocks[2].prefix[3+i]),-1);
    }
    out<<"{\"record\":\"degree_six_upper\",\"helpers\":"<<helpers<<",\"target\":";write_json(out,target_poly);
    ns_witness::write_terms(out,ring,axioms,target_poly,upper,6,"retained_original_OR_upper");out<<"}\n";
    if(helpers==0)need(!member && span.rank==1450 && width==12616 && rows_expected==2064,"archived baseline control");
    out<<"{\"record\":\"result\",\"helpers\":"<<helpers<<",\"variables\":"<<variables<<",\"columns\":"<<width
       <<",\"generator_multiples\":"<<rows_expected<<",\"rank\":"<<span.rank<<",\"degree_five_member\":"
       <<(member?"true":"false")<<",\"complete_domains\":true,\"passed\":true}\n";
    std::cout<<"Helpers "<<helpers<<": "<<rows_expected<<" rows, rank "<<span.rank<<'/'<<width
             <<", retained target at degree five: "<<(member?"yes":"no")
             <<"; interface quotient rank "<<interface_span.rank<<'/'<<feature_count
             <<", full interface preserved: "<<(preserves_interface?"yes":"no")<<".\n";
    return member;
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"open output");
        out<<"{\"record\":\"schema\",\"prime\":2,\"old_variables\":6,\"accuracy\":1,\"retained_products\":[\"A(x_1,x_2,x_3)\",\"B(y_1,y_2,y_3)\",\"C(x,y)\"],"
              "\"helpers\":[\"G_0=(x_i+y_i)_i\",\"G_1=(x_1+y_1+1,x_2+y_2,x_3+y_3)\"],"
              "\"scope\":\"complete Boolean-base source extensions; not a PHP refutation\",\"degrees\":\"ordinary original companion degree three, before Boolean reduction\"}\n";
        InterfaceBaseline baseline;
        int members=0;for(int count:{0,1,2})members+=one_case(out,count,baseline);
        out<<"{\"record\":\"summary\",\"cases\":3,\"degree_five_members\":"<<members<<",\"passed\":true}\n";
        need(bool(out),"write output");
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
