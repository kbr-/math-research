// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Complete factored collision-pruned bit assignment trees over F2.
#include "binary_php.hpp"
#include <filesystem>
using namespace binary_php;
using Poly=std::vector<Word>;
Poly sum(const Poly& a,const Poly& b){
    Poly result;
    std::set_symmetric_difference(a.begin(),a.end(),b.begin(),b.end(),
                                 std::back_inserter(result));
    return result;
}
Poly product(const Poly& a,const Poly& b){
    std::vector<Word> terms,result;
    for(Word x:a)for(Word y:b)terms.push_back(x|y);
    std::sort(terms.begin(),terms.end());
    for(std::size_t i=0;i<terms.size();){
        std::size_t j=i+1;
        while(j<terms.size()&&terms[j]==terms[i])++j;
        if((j-i)&1)result.push_back(terms[i]);
        i=j;
    }
    return result;
}
template<class T>void array(std::ostream& out,const std::vector<T>& values){
    out<<'[';
    for(std::size_t i=0;i<values.size();++i){
        if(i)out<<',';
        out<<values[i];
    }
    out<<']';
}
struct Node{
    int depth,left=-1,right=-1,collision=-1;
    Word prefix;
};
struct Tree{
    int n=4,ell=2,pigeons;
    std::vector<Node> nodes;
    explicit Tree(int m):pigeons(m){build(0,0);}
    int build(int depth,Word prefix){
        int id=int(nodes.size());
        nodes.push_back({depth,-1,-1,-1,prefix});
        if(depth>0&&depth%ell==0){
            int row=depth/ell-1,label=int((prefix>>(row*ell))&(n-1));
            for(int i=0;i<row;++i)if(int((prefix>>(i*ell))&(n-1))==label){
                nodes[id].collision=i;
                return id;
            }
        }
        if(depth==pigeons*ell)return id;
        int left=build(depth+1,prefix);
        int right=build(depth+1,prefix|(Word(1)<<depth));
        nodes[id].left=left;nodes[id].right=right;
        return id;
    }
};
void check(int pigeons,std::ostream& out){
    Tree tree(pigeons);
    int count=int(tree.nodes.size()),internal=0,bad=0,good=0,companions=0;
    std::vector<int> ledger(count),frontier;
    Word model=0;
    if(pigeons==tree.n)
        for(int i=0;i<pigeons;++i)model|=Word(i)<<(tree.ell*i);
    out<<"{\"type\":\"case\",\"holes\":4,\"ell\":2,\"pigeons\":"<<pigeons
       <<",\"old_variables\":"<<pigeons*tree.ell<<",\"accuracies\":[1,2],"
         "\"root_node\":0,\"root_product\":1}\n";
    for(int id=0;id<count;++id){
        const Node& node=tree.nodes[id];
        int offset=companions;
        if(id)companions+=node.depth;
        if(node.left>=0){
            ++internal;++ledger[id];--ledger[node.left];--ledger[node.right];
        }else if(node.collision>=0){++bad;++ledger[id];}
        else{++good;frontier.push_back(id);}
        int selected=-1;
        if(pigeons==tree.n){
            for(int i=0;i<node.depth;++i)if(((model^node.prefix)>>i)&1){
                selected=i;break;
            }
        }
        out<<"{\"type\":\"node\",\"id\":"<<id<<",\"depth\":"<<node.depth
           <<",\"prefix_mask\":"<<node.prefix<<",\"children\":["<<node.left<<','
           <<node.right<<"],\"coefficient_offset_per_h\":"<<offset
           <<",\"collision_earlier_row\":"<<node.collision;
        if(pigeons==tree.n)out<<",\"model_first_success_input\":"<<selected
                              <<",\"model_product\":"<<(selected<0?1:0);
        out<<"}\n";
        if(node.collision>=0){
            int a=node.collision,b=node.depth/tree.ell-1;
            int label=int((node.prefix>>(a*tree.ell))&(tree.n-1));
            need(label==int((node.prefix>>(b*tree.ell))&(tree.n-1)),"leaf collision");
            Poly equality{0},difference;
            std::vector<Poly> prefixes;
            for(int t=0;t<tree.ell;++t){
                prefixes.push_back(equality);
                Poly ga{Word(1)<<(a*tree.ell+t)},gb{Word(1)<<(b*tree.ell+t)};
                if((label>>t)&1){ga=sum(ga,Poly{0});gb=sum(gb,Poly{0});}
                Poly delta=sum(ga,gb);
                difference=sum(difference,product(equality,delta));
                equality=product(equality,sum(Poly{0},delta));
            }
            need(sum(sum(equality,Poly{0}),difference).empty(),"leaf telescoping identity");
            out<<"{\"type\":\"leaf_certificate\",\"node\":"<<id
               <<",\"collision_rows\":["<<a<<','<<b<<"],\"common_label\":"<<label
               <<",\"equality\":";array(out,equality);
            out<<",\"prefix_cofactors\":[";
            for(std::size_t t=0;t<prefixes.size();++t){
                if(t)out<<',';
                array(out,prefixes[t]);
            }
            out<<"],\"companion_inputs\":[";
            for(int t=0;t<tree.ell;++t){
                if(t)out<<',';
                out<<'['<<a*tree.ell+t<<','<<b*tree.ell+t<<']';
            }
            out<<"],\"NS_costs\":[4,6]}\n";
        }
    }
    for(int id=0;id<count;++id){
        int expected=id==0?1:0;
        if(std::find(frontier.begin(),frontier.end(),id)!=frontier.end())--expected;
        need(ledger[id]==expected,"global formal tree certificate");
    }
    int falling=1,A=0,B=0;
    for(int k=0;k<pigeons;++k){A+=falling;B+=k*falling;falling*=tree.n-k;}
    need(internal==(tree.n-1)*A,"internal-node formula");
    need(count-1==2*internal,"block formula");
    need(companions==2*(tree.ell*(tree.n-1)*B+((tree.ell-1)*tree.n+1)*A),
         "companion formula");
    if(pigeons==tree.n+1)need(good==0&&bad==196,"unsatisfiable frontier count");
    else{
        need(good==24&&bad==100,"satisfiable frontier count");
        int value=1;
        for(int id:frontier){
            const Node& node=tree.nodes[id];
            value-=((model&((Word(1)<<node.depth)-1))==node.prefix);
        }
        need(value==0,"permutation model does not satisfy the frontier target");
        out<<"{\"type\":\"satisfiable_control\",\"old_point\":"<<model
           <<",\"frontier_target_value\":0,\"frontier_omission_value\":1}\n";
    }
    out<<"{\"type\":\"target\",\"constant\":1,\"negative_frontier_nodes\":";
    array(out,frontier);out<<"}\n";
    out<<"{\"type\":\"case_summary\",\"pigeons\":"<<pigeons
       <<",\"internal_nodes\":"<<internal<<",\"blocks\":"<<count-1
       <<",\"companions\":"<<companions<<",\"bad_leaves\":"<<bad
       <<",\"open_frontier_leaves\":"<<good<<",\"NS_costs\":[5,9]}\n";
    std::cout<<"pigeons="<<pigeons<<": "<<count-1<<" blocks, "<<companions
             <<" companions, "<<bad<<" collision leaves, "<<good<<" open leaves.\n";
}
int main(int argc,char** argv){
    try{
        need(argc==3&&std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];
        need(!std::filesystem::exists(path),"refusing existing output");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot create output");
        out<<"{\"type\":\"schema\",\"version\":1,\"field\":2,"
               "\"representation\":\"complete factored tree and leaf witnesses; generic split witness referenced\","
               "\"mismatch_input\":\"x_i plus prefix bit i\","
               "\"coefficient_id\":\"old_variables+h*offset+factor_row*depth+input\"}\n";
        check(5,out);check(4,out);
        out<<"{\"type\":\"summary\",\"cases\":2,\"passed\":true}\n";
        out.close();need(bool(out),"write failed");
    }catch(const std::exception& error){std::cerr<<"ERROR: "<<error.what()<<'\n';return 1;}
}
