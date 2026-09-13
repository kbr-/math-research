// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact local witnesses and complete factored matching-tree module certificates.
#include "ens_symbolic.hpp"
#include <filesystem>
#include <fstream>
#include <functional>
#include <iostream>
#include <set>
#include <string>
using namespace ens_symbolic;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
void integers(std::ostream& out,const std::vector<int>& a){
    out<<'[';for(size_t i=0;i<a.size();i++){if(i)out<<',';out<<a[i];}out<<']';
}
struct Term{std::string name;Polynomial q,f;bool field=false;};
struct Template{
    std::string name;int old=0,variables=0,ceiling=0;
    Block A,C;std::vector<int> a_slots,c_slots;
};
Block rest_block(const Ring& ring,const std::vector<Polynomial>& inputs,int h,int& fresh){
    if(inputs.size()>1)return make_block(ring,inputs,h,fresh);
    Block a;a.accuracy=h;a.inputs=inputs;a.product=ring.constant(1);
    a.prefix.resize(1);a.companions.resize(1);return a;
}
Template local_template(std::ostream& out,int h,int k,bool collision){
    Ring ring(2,32);auto one=ring.constant(1);Template t;
    t.name=(collision?"collision":"edge")+std::string("_h")+std::to_string(h)+"_k"+std::to_string(k);
    t.old=k+(collision?2:1);int fresh=t.old;
    std::vector<Polynomial> g{ring.constant(0)};t.a_slots={-1};
    for(int i=0;i<k;i++){
        int v=i+(collision?2:0);g.push_back(ring.subtract(one,ring.variable(v)));t.a_slots.push_back(v);
    }
    t.A=rest_block(ring,g,h,fresh);
    auto x=ring.variable(collision?0:k),bx=ring.subtract(ring.multiply(x,x),x);
    std::vector<Polynomial> c_inputs;std::vector<Term> proof;Polynomial target;
    if(!collision){
        c_inputs=g;c_inputs.push_back(ring.subtract(one,x));t.c_slots=t.a_slots;t.c_slots.push_back(k);
        t.C=make_block(ring,c_inputs,h,fresh);
        target=ring.subtract(t.C.product,ring.multiply(x,t.A.product));
        proof.push_back({"child_last",one,t.C.companions.back()});
        for(int i=0;i<=k;i++){
            proof.push_back({"child_"+std::to_string(i),ring.multiply(x,t.A.prefix[i]),t.C.companions[i]});
            proof.push_back({"parent_"+std::to_string(i),ring.multiply(ring.constant(-1),ring.multiply(x,t.C.prefix[i])),t.A.companions[i]});
        }
        proof.push_back({"Boolean_x",ring.multiply(t.A.product,t.C.prefix.back()),bx,true});
        t.ceiling=k?4*h+1:2*h+1;
    }else{
        auto y=ring.variable(1),xy=ring.multiply(x,y),by=ring.subtract(ring.multiply(y,y),y);
        c_inputs={ring.subtract(one,x),ring.subtract(one,y)};
        c_inputs.insert(c_inputs.end(),g.begin(),g.end());t.c_slots={0,1};
        t.c_slots.insert(t.c_slots.end(),t.a_slots.begin(),t.a_slots.end());
        t.C=make_block(ring,c_inputs,h,fresh);
        target=ring.subtract(t.C.product,ring.multiply(xy,t.A.product));
        proof.push_back({"child_x",one,t.C.companions[0]});
        proof.push_back({"child_y",x,t.C.companions[1]});
        for(int i=0;i<=k;i++){
            proof.push_back({"child_rest_"+std::to_string(i),ring.multiply(xy,t.A.prefix[i]),t.C.companions[i+2]});
            proof.push_back({"rest_"+std::to_string(i),ring.multiply(ring.constant(-1),ring.multiply(xy,t.C.prefix[i+2])),t.A.companions[i]});
        }
        proof.push_back({"Boolean_x",ring.multiply(y,ring.multiply(t.A.product,t.C.prefix[0])),bx,true});
        proof.push_back({"Boolean_y",ring.multiply(x,ring.multiply(t.A.product,t.C.prefix[1])),by,true});
        t.ceiling=k?4*h+2:2*h+2;
    }
    t.variables=fresh;Polynomial sum,without_fields;int used=0,terms=0;
    for(const auto& term:proof)if(!term.q.empty() && !term.f.empty()){
        auto product=ring.multiply(term.q,term.f);ring.accumulate(sum,product);
        if(!term.field)ring.accumulate(without_fields,product);
        used=std::max(used,degree(product));++terms;
    }
    need(sum==target && used==t.ceiling,"local witness identity/degree "+t.name);
    need(without_fields!=target,"field omission control "+t.name);
    out<<"{\"type\":\"local_template\",\"name\":\""<<t.name<<"\",\"p\":2,\"h\":"<<h
       <<",\"k\":"<<k<<",\"old_variables\":"<<t.old<<",\"actual_variables\":"<<fresh
       <<",\"A_virtual_constant\":"<<(k?"false":"true")<<",\"A_input_old_slots\":";
    integers(out,t.a_slots);out<<",\"C_input_old_slots\":";integers(out,t.c_slots);
    out<<",\"A\":";write_block(out,t.A);out<<",\"C\":";write_block(out,t.C);
    out<<",\"target\":";write_json(out,target);out<<",\"NS_witness_degree\":"<<used
       <<",\"field_omission_changes_identity\":true,\"terms\":[";
    bool comma=false;
    for(const auto& term:proof)if(!term.q.empty() && !term.f.empty()){
        if(comma)out<<',';
        comma=true;out<<"{\"name\":\""<<term.name<<"\",\"field\":"
          <<(term.field?"true":"false")<<",\"cofactor\":";write_json(out,term.q);
        out<<",\"axiom\":";write_json(out,term.f);out<<'}';
    }
    out<<"]}\n";
    std::cout<<t.name<<": "<<terms<<" exact NS terms, witness degree "<<used<<", field control passed.\n";
    return t;
}
struct GlobalBlock{std::vector<int> cells;int start=-1;};
struct Edge{int parent=-1,child=-1,cell=-1,k=0;};
struct Leaf{int bad=-1,rest=-1,x=-1,y=-1;};
int weighted_degree(const Polynomial& f,int old,int weight){
    int result=0;for(const auto& [m,c]:f){int d=0;for(int v:m)d+=v<old?1:weight;result=std::max(result,d);}return result;
}
std::vector<int> module_map(const Template& t,const std::vector<int>& old_map,
                            const GlobalBlock* A,const GlobalBlock& C){
    need(int(old_map.size())==t.old,"old-coordinate mapping");
    std::vector<int> map(t.variables,-1);std::copy(old_map.begin(),old_map.end(),map.begin());
    auto assign=[&](const Block& local,const std::vector<int>& slots,const GlobalBlock* global){
        if(!global){need(local.variables.empty(),"virtual block has coefficient variables");return;}
        for(int u=0;u<int(local.variables.size());u++)for(int i=0;i<int(slots.size());i++){
            int position=0;
            if(slots[i]>=0){
                int cell=old_map[slots[i]];
                auto found=std::lower_bound(global->cells.begin(),global->cells.end(),cell);
                need(found!=global->cells.end() && *found==cell,"local input missing from global block");
                position=1+int(found-global->cells.begin());
            }
            map[local.variables[u][i]]=global->start+u*int(global->cells.size()+1)+position;
        }
    };
    assign(t.A,t.a_slots,A);assign(t.C,t.c_slots,&C);
    need(std::find(map.begin(),map.end(),-1)==map.end(),"incomplete actual-variable mapping");
    std::set<int> unique(map.begin(),map.end());need(unique.size()==map.size(),"noninjective local renaming");
    return map;
}
void global_case(std::ostream& out,int n,int h,bool satisfiable,const std::map<std::string,Template>& templates){
    Ring ring(2,32);auto one=ring.constant(1);int pigeons=n+(satisfiable?0:1),old=n*pigeons;
    std::string name="matching_tree_n"+std::to_string(n)+"_h"+std::to_string(h)+(satisfiable?"_satisfiable":"");
    std::map<std::vector<int>,int> registry;std::vector<GlobalBlock> blocks;
    auto intern=[&](const std::vector<int>& cells){
        if(cells.empty())return -1;
        auto found=registry.find(cells);if(found!=registry.end())return found->second;
        int id=int(blocks.size());blocks.push_back({cells,-1});registry.emplace(cells,id);return id;
    };
    std::vector<Edge> edges;std::vector<Leaf> leaves;std::vector<int> good;
    std::vector<std::pair<int,int>> internal;
    std::function<void(std::vector<int>)> walk=[&](std::vector<int> cells){
        int k=int(cells.size()),parent=intern(cells);internal.emplace_back(parent,k);
        for(int j=0;j<n;j++){
            int y=k*n+j;auto child_cells=cells;child_cells.push_back(y);int child=intern(child_cells);
            edges.push_back({parent,child,y,k});
            auto collision=std::find_if(cells.begin(),cells.end(),[&](int x){return x%n==j;});
            if(collision!=cells.end()){
                std::vector<int> rest;for(int x:cells)if(x!=*collision)rest.push_back(x);
                leaves.push_back({child,intern(rest),*collision,y});
            }else if(k+1==pigeons)good.push_back(child);
            else walk(child_cells);
        }
    };
    walk({});
    int next=old;for(auto& block:blocks){block.start=next;next+=h*int(block.cells.size()+1);}
    auto selector=[&](int id){return id<0?one:ring.variable(old+id);};
    out<<"{\"type\":\"global_case\",\"name\":\""<<name<<"\",\"p\":2,\"n\":"<<n<<",\"pigeons\":"<<pigeons
       <<",\"h\":"<<h<<",\"old_variables\":"<<old<<",\"actual_variables\":"<<next
       <<",\"blocks\":"<<blocks.size()<<",\"internal_matching_nodes\":"<<internal.size()
       <<",\"edge_modules\":"<<edges.size()<<",\"collision_modules\":"<<leaves.size()
       <<",\"satisfiable_control\":"<<(satisfiable?"true":"false")<<"}\n";
    for(int id=0;id<int(blocks.size());id++){
        out<<"{\"type\":\"global_block\",\"case\":\""<<name<<"\",\"id\":"<<id
           <<",\"formal_slot\":"<<old+id<<",\"weight\":"<<2*h<<",\"coefficient_start\":"<<blocks[id].start
           <<",\"cells\":";integers(out,blocks[id].cells);out<<"}\n";
    }
    Polynomial sum;int cost=0,modules=0;std::vector<Polynomial> rows(pigeons);
    std::map<std::pair<int,int>,Polynomial> columns;
    for(const auto& [parent,k]:internal)ring.accumulate(rows[k],selector(parent));
    auto module=[&](const Template& t,const std::vector<int>& old_map,int a,int c,const Polynomial& target){
        auto map=module_map(t,old_map,a<0?nullptr:&blocks[a],blocks[c]);
        need(weighted_degree(target,old,2*h)<=t.ceiling,"formal target exceeds witness ceiling");
        ring.accumulate(sum,target);cost=std::max(cost,t.ceiling);
        out<<"{\"type\":\"global_module\",\"case\":\""<<name<<"\",\"id\":"<<modules++
           <<",\"template\":\""<<t.name<<"\",\"variable_map\":";integers(out,map);
        out<<",\"formal_target\":";write_json(out,target);
        out<<",\"outer_cofactor\":1,\"witness_cost\":"<<t.ceiling<<"}\n";
    };
    for(const auto& edge:edges){
        std::vector<int> map;if(edge.parent>=0)map=blocks[edge.parent].cells;map.push_back(edge.cell);
        std::string key="edge_h"+std::to_string(h)+"_k"+std::to_string(edge.k);
        auto target=ring.subtract(selector(edge.child),ring.multiply(ring.variable(edge.cell),selector(edge.parent)));
        module(templates.at(key),map,edge.parent,edge.child,target);
    }
    Polynomial first_leaf;
    for(const auto& leaf:leaves){
        auto xy=ring.multiply(ring.variable(leaf.x),ring.variable(leaf.y));
        auto target=ring.subtract(selector(leaf.bad),ring.multiply(xy,selector(leaf.rest)));
        if(first_leaf.empty())first_leaf=target;
        std::vector<int> map{leaf.x,leaf.y};
        if(leaf.rest>=0)map.insert(map.end(),blocks[leaf.rest].cells.begin(),blocks[leaf.rest].cells.end());
        int k=int(map.size())-2;std::string key="collision_h"+std::to_string(h)+"_k"+std::to_string(k);
        module(templates.at(key),map,leaf.rest,leaf.bad,target);
        ring.accumulate(columns[{leaf.x,leaf.y}],selector(leaf.rest));
    }
    auto base_term=[&](const std::string& label,const Polynomial& q,const Polynomial& f){
        if(q.empty())return;
        ring.accumulate(sum,ring.multiply(q,f));
        int charge=weighted_degree(q,old,2*h)+degree(f);cost=std::max(cost,charge);
        out<<"{\"type\":\"base_term\",\"case\":\""<<name<<"\",\"name\":\""<<label<<"\",\"cofactor\":";
        write_json(out,q);out<<",\"axiom\":";write_json(out,f);out<<",\"weighted_cost\":"<<charge<<"}\n";
    };
    for(int i=0;i<pigeons;i++){
        auto row=ring.constant(-1);for(int j=0;j<n;j++)ring.accumulate(row,ring.variable(i*n+j));
        base_term("row_"+std::to_string(i),rows[i],row);
    }
    for(const auto& [pair,q]:columns){
        need(pair.first/n!=pair.second/n && pair.first%n==pair.second%n,"wrong collision generator");
        base_term("collision_"+std::to_string(pair.first)+"_"+std::to_string(pair.second),q,
                  ring.multiply(ring.variable(pair.first),ring.variable(pair.second)));
    }
    auto target=one;for(int id:good)ring.accumulate(target,selector(id),-1);
    need(sum==target && cost<=4*h+2,"complete formal module identity/degree");
    need(!first_leaf.empty() && ring.subtract(sum,first_leaf)!=target,"missing collision module control");
    if(!satisfiable)need(good.empty() && target==one,"refutation target");
    else{
        need(!good.empty() && target!=one,"satisfiable frontier remains");
        std::vector<int> old_ones,coefficient_ones,products;
        for(int i=0;i<n;i++)old_ones.push_back(i*n+i);
        std::map<int,int> point;for(int v=0;v<old;v++)point[v]=(v/n==v%n);
        for(int i=0;i<n;i++){
            int total=0;for(int j=0;j<n;j++)total+=point.at(i*n+j);
            need(total==1,"satisfiable row equation");
            for(int a=i+1;a<n;a++)for(int j=0;j<n;j++)
                need(point.at(i*n+j)*point.at(a*n+j)==0,"satisfiable column collision");
        }
        int companions=0;
        for(int id=0;id<int(blocks.size());id++){
            const auto& block=blocks[id];int selected=-1;
            for(int i=0;i<int(block.cells.size());i++)if(!point.at(block.cells[i])){selected=i+1;break;}
            if(selected>=0)coefficient_ones.push_back(block.start+selected);
            int product=1;
            for(int u=0;u<h;u++){
                int factor=1;
                for(int i=0;i<int(block.cells.size());i++)
                    factor^=(u==0 && selected==i+1) && !point.at(block.cells[i]);
                product&=factor;
            }
            products.push_back(product);point[old+id]=product;
            for(int cell:block.cells){need((1-point.at(cell))*product==0,"retained companion in model");++companions;}
            ++companions; // The FALSE leaf gives the identically zero input.
        }
        need(ring.evaluate(target,point)==0,"satisfiable model target");
        out<<"{\"type\":\"satisfiable_model\",\"case\":\""<<name<<"\",\"old_x_ones\":";
        integers(out,old_ones);out<<",\"actual_coefficient_ones\":";integers(out,coefficient_ones);
        out<<",\"products\":";integers(out,products);
        out<<",\"companion_checks\":"<<companions<<",\"target_value\":0,\"one_value\":1}\n";
    }
    out<<"{\"type\":\"global_result\",\"case\":\""<<name<<"\",\"modules\":"<<modules
       <<",\"NS_witness_bound\":"<<cost<<",\"formal_target\":";write_json(out,target);
    out<<",\"good_frontier\":";integers(out,good);
    out<<",\"omitting_one_collision_module_changes_identity\":true,\"all_passed\":true}\n";
    std::cout<<name<<": "<<blocks.size()<<" blocks, "<<modules<<" modules, degree "<<cost
             <<", target "<<(satisfiable?"1 minus surviving frontier":"1")<<".\n";
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");
        auto parent=std::filesystem::path(argv[2]).parent_path();if(!parent.empty())std::filesystem::create_directories(parent);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"weighted_source_matching_tree\",\"p\":2,\"seed\":null,"
             "\"polynomial_encoding\":\"[coefficient,[variable,...]] with repeated indices for powers\","
             "\"global_block_inputs\":\"0 followed by 1-x_cell in listed cell order\","
             "\"coefficient_layout\":\"h consecutive rows of arity cells+1\","
             "\"scope\":\"local NS certificates and complete factored PHP module identities; exponential family control\"}\n";
        std::map<std::string,Template> templates;
        for(int h:{1,2}){
            for(int k=0;k<=6;k++){auto t=local_template(out,h,k,false);templates.emplace(t.name,std::move(t));}
            for(int k=0;k<=5;k++){auto t=local_template(out,h,k,true);templates.emplace(t.name,std::move(t));}
        }
        for(int h:{1,2}){
            for(int n:{2,3,4,6})global_case(out,n,h,false,templates);
            global_case(out,4,h,true,templates);
        }
        out.close();need(bool(out),"output write failed");
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
