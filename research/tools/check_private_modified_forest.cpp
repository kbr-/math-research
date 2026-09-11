// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Conditional constant-depth MP forests with nonmaximal covered cuts.
#define GOAL_CLEANUP_NO_MAIN
#include "check_goal_input_cleanup.cpp"

bool proper_intact(const Forest& f,int root,const Live& live) {
    for(int id:region(f,root))if(id!=root && f.nodes[id].kind=='o' && !live.count(id))return false;
    return true;
}
bool ancestor_of(const Forest& f,int parent,int child) {
    for(int id=f.nodes[child].parent;id>=0;id=f.nodes[id].parent)if(id==parent)return true;
    return false;
}
std::string image_value(Forest& f,const std::vector<int>& tags,const Live& removed,int id) {
    const auto& node=f.nodes[id];
    if(node.kind=='o' && removed.count(id))return "unit";
    std::vector<int> children=node.children;
    if(node.kind=='o') {children.clear();f.frontier(id,children);}
    std::string value(1,node.kind);
    value+='[';value+=std::to_string(node.kind=='o'?tags[id]:node.variable)+","+std::to_string(node.residue)+":";
    for(int child:children)value+=image_value(f,tags,removed,child)+",";
    return value+"]";
}
Live difference(const Live& a,const Live& b) {
    Live result;std::set_difference(a.begin(),a.end(),b.begin(),b.end(),std::inserter(result,result.end()));return result;
}
struct NewStats {long cuts=0,nonmaximal=0,modified=0,pairs=0;};
NewStats modified_case(std::ostream& out,int p,int length,int width) {
    Forest proto,f;
    int B=proto.atom(0);
    for(int i=1;i<width;i++)B=proto.disj(B,proto.atom(i));
    int C=proto.implication(B,B);
    std::vector<ProofNode> proof;std::vector<int> leaves;
    auto leaf=[&](int formula) {
        int rho=f.copy(proto,formula,int(leaves.size()));leaves.push_back(rho);
        proof.push_back({formula,rho,-1,-1,false});return int(proof.size())-1;
    };
    auto mp=[&](int left,int right,int formula) {
        int rho=f.nodes[proof[right].rho].children[1];
        proof.push_back({formula,rho,left,right,false});return int(proof.size())-1;
    };
    int current=leaf(B);
    for(int j=0;j<length;j++) {
        int U=proto.disj(proto.neg(B),proto.atom(1000+j));
        int A=proto.add('m',{U,proto.atom(2000+j)},-1,j%p);
        int a=leaf(A),imp=leaf(proto.implication(A,C));
        int c=mp(a,imp,C);current=mp(current,c,B);
    }
    f.parents();
    std::vector<Live> states(proof.size()),scopes(proof.size());
    std::vector<std::vector<int>> ordinary(proof.size());
    std::vector<std::vector<std::vector<int>>> batches(proof.size());
    std::vector<bool> cuts(f.nodes.size(),false),private_family(f.nodes.size(),false);
    auto goal_map=[&](int rho) {
        std::map<std::string,int> goal;int boundary=f.boundary(rho);
        if(boundary>=0) {std::vector<int> children;f.frontier(boundary,children);for(int child:children)goal.emplace(f.key(child),child);}
        return goal;
    };
    auto eligible=[&](const Live& live,int rho) {
        Live result,protected_region=region(f,rho);auto goal=goal_map(rho);
        if(f.boundary(rho)<0)return result;
        for(int root:live)if(!protected_region.count(root) && proper_intact(f,root,live) && covered(f,root,goal))result.insert(root);
        return result;
    };
    for(size_t v=0;v<proof.size();v++) {
        const auto& node=proof[v];Live live,scope;
        if(node.left<0) {
            for(int id:region(f,node.rho))if(f.nodes[id].kind=='o')scope.insert(id);
            live=scope;int root=f.boundary(node.rho);if(root>=0)ordinary[v].push_back(root);
        } else {
            scope=scopes[node.left];scope.insert(scopes[node.right].begin(),scopes[node.right].end());
            live=states[node.left];live.insert(states[node.right].begin(),states[node.right].end());
            int c=proof[node.right].rho,left=f.nodes[f.nodes[c].children[0]].children[0];
            need(f.key(left)==f.key(proof[node.left].rho),"MP syntax");
            for(int root:{f.boundary(left),f.boundary(node.rho)})if(root>=0)ordinary[v].push_back(root);
        }
        for(int root:ordinary[v]) {need(live.erase(root)==1,"ordinary cut is not live");cuts[root]=true;}
        while(true) {
            auto candidates=eligible(live,node.rho);if(candidates.empty())break;
            std::vector<int> selected;
            for(int root:candidates) {
                bool has_eligible_ancestor=false;
                for(int a=f.nodes[root].parent;a>=0;a=f.nodes[a].parent)has_eligible_ancestor=has_eligible_ancestor || candidates.count(a);
                if(!has_eligible_ancestor)selected.push_back(root);
            }
            need(!selected.empty(),"eligible batch made no progress");batches[v].push_back(selected);
            for(int root:selected) {cuts[root]=true;live.erase(root);}
        }
        states[v]=std::move(live);scopes[v]=std::move(scope);
    }
    // The private set is the ancestor closure of cuts, not just the cut set.
    for(size_t root=0;root<cuts.size();root++)if(cuts[root]) {
        for(int id=int(root);id>=0;id=f.nodes[id].parent)if(f.nodes[id].kind=='o')private_family[id]=true;
    }
    std::map<std::string,int> canonical;std::vector<int> tags(f.nodes.size(),-1);
    for(size_t id=0;id<f.nodes.size();id++)if(f.nodes[id].kind=='o') {
        if(private_family[id])tags[id]=int(id);
        else {
            for(int child:region(f,int(id)))if(f.nodes[child].kind=='o')need(!private_family[child],"shared region is not descendant closed");
            tags[id]=canonical.emplace(f.key(int(id)),int(id)).first->second;
        }
    }
    Evaluation eval(f,tags,p);for(size_t id=0;id<f.nodes.size();id++)eval.expression(int(id));
    std::function<int(int)> level=[&](int id) {
        auto children=f.nodes[id].children;if(f.nodes[id].kind=='o') {children.clear();f.frontier(id,children);}
        int maximum=0;for(int child:children)maximum=std::max(maximum,level(child));
        return maximum+(f.nodes[id].kind=='o'?1:0);
    };
    int max_level=0;for(int root:leaves)max_level=std::max(max_level,level(root));
    need(max_level==3,"source level should be independent of spine length");
    out<<"{\"record\":\"case\",\"p\":"<<p<<",\"length\":"<<length<<",\"width\":"<<width
       <<",\"accuracy\":2,\"max_ens_level\":"<<max_level<<",\"nodes\":[";
    for(size_t id=0;id<f.nodes.size();id++) {
        if(id)out<<',';
        const auto& n=f.nodes[id];out<<"{\"id\":"<<id<<",\"kind\":\""<<n.kind<<"\",\"variable\":"<<n.variable
          <<",\"residue\":"<<n.residue<<",\"parent\":"<<n.parent<<",\"origin\":"<<n.origin
          <<",\"family\":"<<tags[id]<<",\"private\":"<<(private_family[id]?"true":"false")
          <<",\"cut\":"<<(cuts[id]?"true":"false")<<",\"children\":";write_ints(out,n.children);out<<'}';
    }
    out<<"],\"leaves\":";write_ints(out,leaves);out<<",\"steps\":[";
    NewStats stats;bool comma=false;
    auto full_available=[&](int root,const Live& live) {
        for(int id:region(f,root))if(f.nodes[id].kind=='o')need(live.count(id),"copy uses an unavailable original subtree");
    };
    auto pair=[&](int a,int b,const Live& live) {
        need(f.key(a)==f.key(b),"copy syntax");full_available(a,live);full_available(b,live);stats.pairs++;
        out<<"["<<a<<','<<b<<"]";
    };
    for(size_t v=0;v<proof.size();v++) {
        const auto& node=proof[v];Live live;
        if(node.left<0)live=scopes[v];
        else {live=states[node.left];live.insert(states[node.right].begin(),states[node.right].end());}
        if(comma)out<<',';
        comma=true;out<<"{\"node\":"<<v<<",\"representative\":"<<node.rho<<",\"left\":"<<node.left
                      <<",\"right\":"<<node.right<<",\"ordinary_pairs\":[";
        if(node.left>=0) {
            int c=proof[node.right].rho,a=proof[node.left].rho,b=f.nodes[f.nodes[c].children[0]].children[0];
            if(f.boundary(a)>=0) {
                std::vector<int> aa,bb;f.frontier(f.boundary(a),aa);f.frontier(f.boundary(b),bb);
                need(aa.size()==bb.size(),"ordinary input lengths");
                for(size_t i=0;i<aa.size();i++) {if(i)out<<',';pair(aa[i],bb[i],live);}
            } else pair(a,b,live);
        }
        out<<"],\"ordinary_cuts\":";write_ints(out,ordinary[v]);
        for(int root:ordinary[v]) {
            need(maximal(f,root,live) && tags[root]==root,"ordinary interface lost freshness");
            for(int other:live)if(other!=root)need(!eval.supports[other].count(tags[root]),"ordinary cut changes retained axiom");
            live.erase(root);
        }
        auto goal=goal_map(node.rho);Live protected_region=region(f,node.rho);
        out<<",\"cleanup\":[";
        for(size_t round=0;round<batches[v].size();round++) {
            if(round)out<<',';
            const auto& selected=batches[v][round];Live selected_tags;
            for(int root:selected)selected_tags.insert(tags[root]);
            out<<"{\"roots\":";write_ints(out,selected);out<<",\"pairs\":[";bool sep=false;
            for(int root:selected) {
                need(live.count(root) && proper_intact(f,root,live) && !protected_region.count(root),"ineligible root");
                need(private_family[root] && tags[root]==root,"cut is not private");
                stats.cuts++;if(!maximal(f,root,live))stats.nonmaximal++;
                for(int other:live)if(other!=root && eval.supports[other].count(tags[root]))
                    need(ancestor_of(f,other,root) && private_family[other] && tags[other]==other,"changed ancestor escaped private closure");
                std::vector<int> inputs;f.frontier(root,inputs);
                for(int child:inputs) {
                    int target=goal.at(f.key(child));
                    for(int tag:selected_tags)need(!eval.supports[child].count(tag) && !eval.supports[target].count(tag),"witness uses a current cut");
                    if(sep)out<<',';
                    sep=true;pair(child,target,live);
                }
            }
            out<<"]}";for(int root:selected)live.erase(root);
        }
        need(live==states[v] && eligible(live,node.rho).empty(),"schedule replay or saturation");
        for(int id:protected_region)if(f.nodes[id].kind=='o' && id!=f.boundary(node.rho))need(live.count(id),"representative was modified");
        auto removed=difference(scopes[v],live);
        out<<"],\"retained_images\":[";bool sep=false;
        for(int root:live) {
            if(sep)out<<',';
            sep=true;bool intact=proper_intact(f,root,live);
            auto image=image_value(f,tags,removed,root);
            if(!intact)need(private_family[root],"modified root was shared");
            out<<"{\"root\":"<<root<<",\"intact\":"<<(intact?"true":"false")<<",\"product_expression\":\""<<image<<"\"}";
        }
        out<<"],\"representative_intact\":true}";
    }
    out<<"],\"final_modified_roots\":[";bool sep=false;std::map<std::string,std::vector<int>> modified_classes;
    for(int root:states.back())if(!proper_intact(f,root,states.back())) {
        if(sep)out<<',';
        sep=true;out<<root;stats.modified++;modified_classes[f.key(root)].push_back(root);
    }
    need(stats.nonmaximal>=2*length && stats.modified==2*length,"nonmaximal fixture was vacuous");
    // A naive canonical quotient cannot identify an affected ancestor before
    // its independently private child values agree literally.
    bool control=false;
    for(const auto& [key,roots]:modified_classes) {
        (void)key;if(roots.size()<2)continue;
        int a=roots[0],b=roots[1],inner=f.nodes[f.nodes[a].children[0]].children[0];
        need(f.nodes[inner].kind=='o',"control inner root");
        auto merged=tags;merged[b]=merged[a];Assignment point{{merged[a],{0}},{merged[inner],{0}}};
        int va=assigned_value(f,merged,p,a,point),vb=assigned_value(f,merged,p,b,point);
        need(va==1 && vb==0,"affected ancestor alias control");
        out<<"],\"premature_share_control\":{\"first\":"<<a<<",\"second\":"<<b
           <<",\"shared_family\":"<<merged[a]<<",\"values\":[1,0],\"point\":";write_assignment(out,point);out<<'}';
        control=true;break;
    }
    need(control,"missing premature-sharing control");
    out<<",\"summary\":{\"cleanup_roots\":"<<stats.cuts<<",\"nonmaximal_cuts\":"<<stats.nonmaximal
       <<",\"final_modified_ancestors\":"<<stats.modified<<",\"copy_pairs\":"<<stats.pairs<<"},\"all_passed\":true}\n";
    return stats;
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");need(!std::filesystem::exists(argv[2]),"output exists");
        auto dir=std::filesystem::path(argv[2]).parent_path();if(!dir.empty())std::filesystem::create_directories(dir);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"private_modified_forest\",\"seed\":null,\"scope\":\"conditional constant-depth MP forests, not primitive-Frege leaf proofs\"}\n";
        NewStats total;
        for(int p:{2,3})for(int length:{1,2,7,15})for(int width:{3,7}) {
            auto s=modified_case(out,p,length,width);total.cuts+=s.cuts;total.nonmaximal+=s.nonmaximal;total.modified+=s.modified;total.pairs+=s.pairs;
        }
        out<<"{\"record\":\"summary\",\"cases\":16,\"cleanup_roots\":"<<total.cuts<<",\"nonmaximal_cuts\":"<<total.nonmaximal
           <<",\"final_modified_ancestors\":"<<total.modified<<",\"copy_pairs\":"<<total.pairs<<",\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failed");
        std::cout<<"Sixteen private modified-forest schedules passed; "<<total.nonmaximal<<" nonmaximal cuts and "<<total.modified<<" retained modified ancestors.\n";
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
