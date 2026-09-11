// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Physical occurrence schedules, survivor sharing, and future-cut comparisons.
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
void need(bool ok,const std::string& message) {if(!ok)throw std::runtime_error(message);}
struct Node {char kind;std::vector<int> children;int variable=-1,residue=0,origin=-1,parent=-1;};
struct Forest {
    std::vector<Node> nodes;std::vector<std::string> keys;
    int add(char kind,std::vector<int> children={},int variable=-1,int residue=0,int origin=-1) {
        need(nodes.size()<50000,"forest size guard");
        nodes.push_back({kind,std::move(children),variable,residue,origin,-1});return int(nodes.size())-1;
    }
    int atom(int variable) {return add('x',{},variable);}
    int neg(int a) {return add('n',{a});}
    int disj(int a,int b) {return add('o',{a,b});}
    int implication(int a,int b) {return disj(neg(a),b);}
    int copy(const Forest& source,int id,int origin) {
        auto n=source.nodes.at(id);std::vector<int> children;
        for(int child:n.children)children.push_back(copy(source,child,origin));
        return add(n.kind,children,n.variable,n.residue,origin);
    }
    std::string key(int id) {
        keys.resize(nodes.size());if(!keys[id].empty())return keys[id];
        const auto n=nodes[id];std::string value(1,n.kind);
        value+='[';value+=std::to_string(n.variable)+","+std::to_string(n.residue)+":";
        for(int child:n.children)value+=key(child)+",";
        value+=']';keys[id]=value;return value;
    }
    int boundary(int id)const {while(nodes[id].kind=='n')id=nodes[id].children[0];return nodes[id].kind=='o'?id:-1;}
    int mod_root(int id)const {while(nodes[id].kind=='n')id=nodes[id].children[0];need(nodes[id].kind=='m',"not MOD");return id;}
    void walk(int id,std::vector<int>& result)const {
        result.push_back(id);for(int child:nodes[id].children)walk(child,result);
    }
    void frontier(int id,std::vector<int>& result)const {
        if(nodes[id].kind!='o') {result.push_back(id);return;}
        for(int child:nodes[id].children)frontier(child,result);
    }
    void parents() {
        for(size_t i=0;i<nodes.size();i++)for(int child:nodes[i].children) {
            need(nodes[child].parent==-1,"physical occurrence was shared");nodes[child].parent=int(i);
        }
    }
    bool intact(int root,const std::vector<bool>& live)const {
        std::vector<int> sub;walk(root,sub);int excluded=boundary(root);
        for(int id:sub)if(nodes[id].kind=='o' && id!=excluded && !live[id])return false;
        return true;
    }
};
struct ProofNode {int formula,rho,left=-1,right=-1;bool matched=false;};
struct Evaluation {
    Forest& f;const std::vector<int>& tags;int p;
    std::vector<std::string> expressions;std::vector<std::set<int>> supports;
    Evaluation(Forest& forest,const std::vector<int>& t,int prime):f(forest),tags(t),p(prime),
        expressions(f.nodes.size()),supports(f.nodes.size()) {}
    std::string expression(int id) {
        if(!expressions[id].empty())return expressions[id];
        const auto& n=f.nodes[id];std::vector<int> children=n.children;
        std::string value(1,n.kind);
        value+='[';value+=std::to_string(n.kind=='o'?tags[id]:n.variable)+","+std::to_string(n.residue)+":";
        if(n.kind=='o') {children.clear();f.frontier(id,children);supports[id].insert(tags[id]);}
        for(int child:children) {
            value+=expression(child)+",";supports[id].insert(supports[child].begin(),supports[child].end());
        }
        value+=']';expressions[id]=value;return value;
    }
    int value(int id,int changed_tag,int auxiliary_tag=-1)const {
        const auto& n=f.nodes[id];
        if(n.kind=='x' || n.kind=='t')return 0;
        if(n.kind=='n')return (1-value(n.children[0],changed_tag,auxiliary_tag)+p)%p;
        if(n.kind=='o') {
            if(tags[id]!=changed_tag && tags[id]!=auxiliary_tag)return 1;
            std::vector<int> children;f.frontier(id,children);
            // Only the first coefficient of the first vector is one; all
            // others, including the complete second vector, are zero.
            return value(children[0],changed_tag,auxiliary_tag);
        }
        int scalar=n.residue-int(n.children.size());
        for(int child:n.children)scalar+=value(child,changed_tag,auxiliary_tag);
        scalar=(scalar%p+p)%p;int result=1;for(int i=0;i<p-1;i++)result=result*scalar%p;return result;
    }
};
void write_ints(std::ostream& out,const std::vector<int>& values) {
    out<<'[';for(size_t i=0;i<values.size();i++) {if(i)out<<',';out<<values[i];}out<<']';
}
void run_case(std::ostream& out,int p,int length,int final_count,int width) {
    Forest proto,f;std::vector<int> A(length),B(length),T(length),arguments;
    for(int j=0;j<final_count;j++) {
        int q=proto.atom(100+j*width);
        for(int i=1;i<width;i++)q=proto.disj(q,proto.atom(100+j*width+i));
        arguments.push_back(q);
    }
    int last=length-1;B[last]=arguments[0];
    for(int j=1;j<final_count;j++)B[last]=proto.disj(B[last],arguments[j]);
    auto modular=[&](std::vector<int> args,int j) {
        int m=proto.add('m',std::move(args),-1,j%2?0:1);return j%2?proto.neg(m):m;
    };
    A[last]=modular(arguments,last);
    for(int j=last-1;j>=0;j--) {
        int q=proto.disj(proto.atom(j),proto.neg(proto.atom(j)));
        T[j]=j%3==0?q:j%3==1?proto.add('m',{q},-1,1):proto.neg(q);
        B[j]=proto.implication(T[j],A[j+1]);A[j]=modular({B[j]},j);
    }
    std::vector<ProofNode> proof;std::vector<int> leaves;
    auto leaf=[&](int formula) {
        int rho=f.copy(proto,formula,int(leaves.size()));leaves.push_back(rho);
        proof.push_back({formula,rho,-1,-1,false});return int(proof.size())-1;
    };
    auto mp=[&](int left,int right,bool matched) {
        int c=proof[right].rho;need(f.nodes[c].kind=='o',"MP right premise not an implication");
        int neg=f.nodes[c].children[0];need(f.nodes[neg].kind=='n',"MP antecedent syntax");
        need(f.key(proof[left].rho)==f.key(f.nodes[neg].children[0]),"MP formulas do not match");
        int result_formula=proto.nodes[proof[right].formula].children[1];
        proof.push_back({result_formula,f.nodes[c].children[1],left,right,matched});return int(proof.size())-1;
    };
    int current=leaf(A[0]);
    for(int j=0;j<length;j++) {
        int c=leaf(proto.implication(A[j],B[j]));current=mp(current,c,true);
        if(j<last) {int t=leaf(T[j]);current=mp(t,current,false);}
    }
    f.parents();std::vector<bool> cuts(f.nodes.size(),false),extra(cuts),live(cuts);
    for(size_t i=0;i<f.nodes.size();i++)live[i]=f.nodes[i].kind=='o';
    auto mark=[&](int id) {if(id>=0)cuts[id]=true;};
    for(int root:leaves) {int b=f.boundary(root);mark(b);if(b>=0)live[b]=false;}
    for(const auto& node:proof)if(node.left>=0) {
        int c=proof[node.right].rho;
        mark(f.boundary(f.nodes[f.nodes[c].children[0]].children[0]));mark(f.boundary(node.rho));
        if(node.matched)for(int root:f.nodes[f.mod_root(proof[node.left].rho)].children) {
            need(f.nodes[root].kind=='o',"frontier argument is not directly OR-headed");cuts[root]=extra[root]=true;
        }
    }
    std::map<std::string,int> canonical;std::vector<int> tags(f.nodes.size(),-1);
    for(size_t i=0;i<f.nodes.size();i++)if(f.nodes[i].kind=='o') {
        if(cuts[i])tags[i]=int(i);
        else {
            std::vector<int> sub;f.walk(int(i),sub);
            for(int d:sub)if(f.nodes[d].kind=='o')need(!cuts[d],"survivor closure violated");
            auto [entry,inserted]=canonical.emplace(f.key(int(i)),int(i));(void)inserted;tags[i]=entry->second;
        }
    }
    Evaluation eval(f,tags,p);for(size_t i=0;i<f.nodes.size();i++)eval.expression(int(i));
    out<<"{\"record\":\"case\",\"p\":"<<p<<",\"matched_nodes\":"<<length
       <<",\"final_arguments\":"<<final_count<<",\"argument_width\":"<<width
       <<",\"accuracy\":2,\"nodes\":[";
    for(size_t i=0;i<f.nodes.size();i++) {
        if(i)out<<',';
        const auto& n=f.nodes[i];
        out<<"{\"id\":"<<i<<",\"kind\":\""<<n.kind<<"\",\"children\":";write_ints(out,n.children);
        out<<",\"variable\":"<<n.variable<<",\"residue\":"<<n.residue<<",\"origin\":"<<n.origin
           <<",\"parent\":"<<n.parent<<",\"coefficient_family\":"<<tags[i]
           <<",\"private_cut\":"<<(cuts[i]?"true":"false")<<",\"new_frontier_cut\":"<<(extra[i]?"true":"false")<<'}';
    }
    out<<"],\"leaf_roots\":";write_ints(out,leaves);out<<",\"steps\":[";
    int nonliteral=0,ordinary=0,removed=0;bool first=true;
    auto fresh=[&](int root) {
        if(root<0)return;
        for(int a=f.nodes[root].parent;a>=0;a=f.nodes[a].parent)
            need(f.nodes[a].kind!='o' || !live[a],"live OR ancestor of a cut");
        for(size_t i=0;i<live.size();i++)if(live[i] && int(i)!=root)
            need(!eval.supports[i].count(tags[root]),"outside axiom uses a private root");
    };
    for(size_t index=0;index<proof.size();index++) {
        const auto& node=proof[index];if(node.left<0)continue;
        int a=proof[node.left].rho,c=proof[node.right].rho,b=node.rho;
        int left=f.nodes[f.nodes[c].children[0]].children[0];
        need(f.intact(a,live) && f.intact(c,live),"current representative lost proper descendants");
        if(!first)out<<',';
        first=false;
        out<<"{\"proof_node\":"<<index<<",\"antecedent\":"<<a<<",\"implication\":"<<c
           <<",\"consequent\":"<<b<<",\"matched\":"<<(node.matched?"true":"false");
        if(node.matched) {
            auto roots=f.nodes[f.mod_root(a)].children;std::vector<int> from,to;
            for(int root:roots)f.frontier(root,from);
            f.frontier(b,to);
            need(from.size()==to.size(),"flattened arities do not match");
            out<<",\"input_pairs\":[";
            for(size_t j=0;j<from.size();j++) {
                if(j)out<<',';
                need(f.key(from[j])==f.key(to[j]),"input syntax mismatch");
                for(int root:roots)need(!eval.supports[from[j]].count(tags[root]) && !eval.supports[to[j]].count(tags[root]),"goal/input contains a current cut");
                bool literal=eval.expressions[from[j]]==eval.expressions[to[j]];
                out<<"{\"source\":"<<from[j]<<",\"target\":"<<to[j]<<",\"literal\":"<<(literal?"true":"false");
                if(!literal) {
                    nonliteral++;bool found=false;
                    std::vector<int> auxiliaries{-1};
                    std::set<int> joint=eval.supports[from[j]];
                    joint.insert(eval.supports[to[j]].begin(),eval.supports[to[j]].end());
                    auxiliaries.insert(auxiliaries.end(),joint.begin(),joint.end());
                    for(int tag:eval.supports[to[j]])if(cuts[tag] && live[tag] && !eval.supports[from[j]].count(tag)) {
                        for(int aux:auxiliaries) {
                            if(aux==tag)continue;
                            int x=eval.value(from[j],tag,aux),y=eval.value(to[j],tag,aux);
                            if(x==y)continue;
                            out<<",\"changed_future_family\":"<<tag<<",\"auxiliary_family\":"<<aux
                               <<",\"source_input_value\":"<<(1-x+p)%p<<",\"target_input_value\":"<<(1-y+p)%p;
                            found=true;break;
                        }
                        if(found)break;
                    }
                    need(found,"no coefficient-domain witness for a nonliteral comparison");
                }
                out<<'}';
            }
            out<<"],\"new_cuts\":";write_ints(out,roots);
            out<<",\"bad_merge_witnesses\":[";
            for(size_t j=0;j<roots.size();j++) {
                int root=roots[j];fresh(root);
                auto witness=canonical.find(f.key(root));need(witness!=canonical.end(),"no surviving same-syntax copy");
                need(live[witness->second] && eval.supports[witness->second].count(witness->second),"bad merge did not expose an outside axiom");
                if(j)out<<',';
                out<<"{\"private\":"<<root<<",\"surviving\":"<<witness->second<<'}';
                live[root]=false;removed++;
            }
            out<<']';
        } else {
            ordinary++;int ra=f.boundary(a),rl=f.boundary(left);
            if(ra>=0) {
                std::vector<int> x,y;f.frontier(ra,x);f.frontier(rl,y);need(x.size()==y.size(),"ordinary input arity");
                for(size_t j=0;j<x.size();j++)need(eval.expressions[x[j]]==eval.expressions[y[j]],"ordinary comparison lost literal agreement");
            } else need(eval.expressions[a]==eval.expressions[left],"ordinary value comparison lost literal agreement");
            out<<",\"ordinary_comparison_literal\":true";
        }
        for(int root:{f.boundary(left),f.boundary(b)})if(root>=0) {fresh(root);need(live[root],"interface cut repeated");live[root]=false;}
        need(f.intact(b,live),"consequent proper family damaged");
        for(size_t i=0;i<live.size();i++)if(live[i]) {
            std::vector<int> sub;f.walk(int(i),sub);
            for(int d:sub)if(f.nodes[d].kind=='o')need(live[d],"retained OR subtree is not intact");
        }
        out<<",\"freshness\":true,\"consequent_intact\":true}";
    }
    int expected=length-1;
    for(int j=0;j<length-1;j++)if(j%3!=1)expected++;
    need(nonliteral==expected && ordinary==length-1,"future-comparison count");
    out<<"],\"nonliteral_input_pairs\":"<<nonliteral<<",\"ordinary_comparisons\":"<<ordinary
       <<",\"removed_frontier_roots\":"<<removed<<",\"all_passed\":true}\n";
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");
        auto parent=std::filesystem::path(argv[2]).parent_path();if(!parent.empty())std::filesystem::create_directories(parent);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"private_mod_frontiers\",\"seed\":null,"
               "\"scope\":\"conditional MP trees and exact support checks; no Frege leaf or PC compiler\","
               "\"nonidentity_model\":\"all proposition values and coefficients zero except the first coefficient of the named future family and, when not -1, the auxiliary family; these are one, and companion equations are not imposed\"}\n";
        for(int p:{2,3})for(int length:{1,2,7,15})for(int count:{1,3})run_case(out,p,length,count,5);
        out<<"{\"record\":\"summary\",\"cases\":16,\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failed");
        std::cout<<"Sixteen expanded-cut schedules and future-private-root controls passed.\n";
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
