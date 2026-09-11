// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
#include "domain_polynomial.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace domain_polynomial;
void need(bool ok,const std::string& reason) {if(!ok)throw std::runtime_error(reason);}
struct Item {int group,variable,weight;Polynomial factor;};
struct Example {std::vector<int> degrees,accuracies;int parent_accuracy;};
void run_case(std::ostream& out,int p,const Example& example,int case_id) {
    Ring ring(p,96);auto one=ring.constant(1);int next=0;
    std::vector<Polynomial> inputs;
    for(int degree_value:example.degrees) {
        Polynomial g=one;for(int j=0;j<degree_value;j++)g=ring.multiply(g,ring.variable(next++));
        inputs.push_back(g);
    }
    int Boolean_variables=next;std::vector<Block> children;std::vector<Item> items;
    Polynomial target=one;
    for(size_t j=0;j<inputs.size();j++) {
        Block child=make_block(ring,{inputs[j]},example.accuracies[j],next);
        for(const auto& row:child.variables) {
            auto factor=ring.subtract(one,ring.multiply(ring.variable(row[0]),inputs[j]));
            items.push_back({int(j),row[0],example.degrees[j]+1,factor});
        }
        target=ring.multiply(target,child.product);children.push_back(child);
    }
    int old_variables=next,h=example.parent_accuracy;
    Block parent=make_block(ring,inputs,h,next);
    int count=int(items.size()),partitions=1;
    for(int i=0;i<count;i++)partitions*=h;
    need(partitions<=100000,"enumeration guard");
    int best=100000;std::vector<int> best_bins;
    out<<"{\"record\":\"case\",\"p\":"<<p<<",\"case_id\":"<<case_id
       <<",\"parent_accuracy\":"<<h<<",\"Boolean_variables\":"<<Boolean_variables
       <<",\"old_variables\":"<<old_variables<<",\"children\":[";
    for(size_t i=0;i<children.size();i++) {if(i)out<<',';write_block(out,children[i]);}
    out<<"],\"parent\":";write_block(out,parent);
    out<<",\"target_product\":";write_json(out,target);
    out<<",\"factor_partitions\":[";
    for(int code=0;code<partitions;code++) {
        int remaining=code,T=0;std::vector<int> bins(count),weight(h,0),maximum(h,-1);
        for(int j=0;j<count;j++) {
            int bin=remaining%h;remaining/=h;bins[j]=bin;
            weight[bin]+=items[j].weight;
            maximum[bin]=std::max(maximum[bin],example.degrees[items[j].group]);
        }
        for(int bin=0;bin<h;bin++) if(maximum[bin]>=0)T=std::max(T,weight[bin]-maximum[bin]);
        if(T<best) {best=T;best_bins=bins;}
        if(code)out<<',';
        out<<"{\"bins\":[";
        for(int j=0;j<count;j++) {if(j)out<<',';out<<bins[j];}
        out<<"],\"coefficient_degree\":"<<T<<'}';
    }
    std::vector<int> sorted_weights;
    for(const auto& item:items)sorted_weights.push_back(item.weight);
    std::sort(sorted_weights.begin(),sorted_weights.end(),std::greater<int>());
    sorted_weights.erase(sorted_weights.begin(),sorted_weights.begin()+std::min(h,count));
    int remaining_partitions=1;for(size_t i=0;i<sorted_weights.size();i++)remaining_partitions*=h;
    int makespan=100000;
    for(int code=0;code<remaining_partitions;code++) {
        int remaining=code;std::vector<int> load(h,0);
        for(int weight:sorted_weights) {load[remaining%h]+=weight;remaining/=h;}
        makespan=std::min(makespan,*std::max_element(load.begin(),load.end()));
    }
    need(best==1+makespan,"anchor formula disagrees with exhaustive factor partition");
    int Delta=*std::max_element(example.degrees.begin(),example.degrees.end());
    int degree_bound=std::max(1,(degree(target)+h-1)/h-Delta);
    out<<"],\"partition_optimum\":"<<best<<",\"anchor_formula\":"<<1+makespan
       <<",\"total_degree_lower_bound\":"<<degree_bound<<"}\n";
    std::map<int,Polynomial> images;
    for(int bin=0;bin<h;bin++) {
        std::vector<int> indices;
        for(int j=0;j<count;j++)if(best_bins[j]==bin)indices.push_back(j);
        std::sort(indices.begin(),indices.end(),[&](int a,int b) {
            if(items[a].weight!=items[b].weight)return items[a].weight>items[b].weight;
            return a<b;
        });
        std::vector<Polynomial> coefficients(inputs.size());Polynomial suffix=one;
        for(auto it=indices.rbegin();it!=indices.rend();++it) {
            const auto& item=items[*it];
            ring.accumulate(coefficients[item.group],ring.multiply(ring.variable(item.variable),suffix));
            suffix=ring.multiply(item.factor,suffix);
        }
        Polynomial factor=one;
        for(size_t j=0;j<inputs.size();j++) {
            images[parent.variables[bin][j]]=coefficients[j];
            need(degree(coefficients[j])<=best,"coefficient exceeds partition optimum");
            ring.accumulate(factor,ring.multiply(coefficients[j],inputs[j]),-1);
        }
        need(factor==suffix,"factor telescope");
    }
    need(ring.substitute(parent.product,images)==target,"prescribed product realization");
    out<<"{\"record\":\"realization\",\"coefficient_degree\":"<<best<<",\"images\":[";
    bool comma=false;
    for(const auto& [variable,image]:images) {
        if(comma)out<<',';
        comma=true;out<<"{\"variable\":"<<variable<<",\"image\":";write_json(out,image);out<<'}';
    }
    out<<"]}\n";
    for(size_t j=0;j<inputs.size();j++) {
        Polynomial multiplier=one;
        for(size_t k=0;k<children.size();k++)if(k!=j)multiplier=ring.multiply(multiplier,children[k].product);
        auto image=ring.substitute(parent.companions[j],images);
        auto reconstructed=ring.multiply(multiplier,children[j].companions[0]);
        need(image==reconstructed,"companion image certificate");
        int d=degree(reconstructed),original=degree(parent.companions[j]);
        need(d<=best*original,"T-scaled image budget");
        out<<"{\"record\":\"companion_image\",\"coordinate\":"<<j<<",\"target\":";write_json(out,image);
        out<<",\"old_companion\":";write_json(out,children[j].companions[0]);
        out<<",\"cofactor\":";write_json(out,multiplier);
        out<<",\"degree\":"<<d<<",\"original_degree\":"<<original
           <<",\"scaled_budget\":"<<best*original<<"}\n";
    }
    std::vector<int> powers(old_variables,p);
    for(int i=0;i<Boolean_variables;i++)powers[i]=2;
    for(const auto& [variable,image]:images) {
        auto field_image=ring.subtract(ring.power(image,p),image);
        auto proof=domain_reduce(ring,field_image,powers);verify_reduction(ring,field_image,powers,proof);
        need(proof.remainder.empty() && proof.degree<=p*best,"field-image budget");
        if(field_image.empty())continue;
        out<<"{\"record\":\"field_image\",\"variable\":"<<variable<<",\"target\":";
        write_json(out,field_image);out<<",\"domain_powers\":[";
        for(size_t i=0;i<powers.size();i++) {if(i)out<<',';out<<powers[i];}
        out<<"],\"proof\":";write_reduction(out,proof);out<<"}\n";
    }
    std::map<int,int> point;
    for(int i=0;i<old_variables;i++)point[i]=0;
    for(int i=0;i<example.degrees[0];i++)point[i]=1;
    for(const auto& child:children) {
        int value=ring.evaluate(child.product,point);need(value==1,"Booleanity-only model");
    }
    need(ring.evaluate(ring.multiply(inputs[0],target),point)==1,"direct companion request disappeared");
    out<<"{\"record\":\"Booleanity_only_control\",\"assignment\":[";
    for(int i=0;i<old_variables;i++) {if(i)out<<',';out<<point[i];}
    out<<"],\"all_child_products\":1,\"all_child_Booleanity_zero\":true,"
           "\"first_parent_companion_image\":1,\"not_a_model_of_all_child_companions\":true}\n";
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");
        auto directory=std::filesystem::path(argv[2]).parent_path();
        if(!directory.empty())std::filesystem::create_directories(directory);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        std::vector<Example> examples={
            {{1,1,1},{1,1,1},2},{{4,3,3},{1,1,1},2},
            {{1,2},{2,2},2},{{1,3,4},{1,1,1},3},
            {{1,1,1},{2,2,2},2},{{1,1,1,1,1},{1,1,1,1,1},2}};
        out<<"{\"schema\":1,\"suite\":\"weighted_core_product\",\"seed\":null,"
               "\"scope\":\"disjoint monomial inputs and prescribed old products\"}\n";
        for(int p:{2,3,5,7})for(size_t i=0;i<examples.size();i++)run_case(out,p,examples[i],int(i));
        out<<"{\"record\":\"summary\",\"cases\":24,\"all_passed\":true}\n";
        out.close();need(bool(out),"write output failed");
        std::cout<<"Twenty-four weighted product realizations, exhaustive partitions, and image checks passed.\n";
    } catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}
}
