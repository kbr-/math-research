// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Reuse the existing occurrence/evaluation kernel without running its CLI.
#define main private_mod_frontier_reference_main
#include "check_private_mod_frontiers.cpp"
#undef main
#include <functional>
#include <iterator>

using Live=std::set<int>;
using Assignment=std::map<int,std::vector<int>>;
struct CleanupStats {long roots=0,rounds=0,ordinary_repairs=0,input_repairs=0;int gap_classes=0;};
int assigned_value(const Forest& f,const std::vector<int>& tags,int p,int id,const Assignment& assignment) {
    const auto& n=f.nodes[id];
    if(n.kind=='x' || n.kind=='t')return 0;
    if(n.kind=='n')return (1-assigned_value(f,tags,p,n.children[0],assignment)+p)%p;
    if(n.kind=='o') {
        auto found=assignment.find(tags[id]);if(found==assignment.end())return 1;
        std::vector<int> children;f.frontier(id,children);int value=1;
        for(int coordinate:found->second)value-=1-assigned_value(f,tags,p,children.at(coordinate),assignment);
        return (value%p+p)%p;
    }
    int value=n.residue-int(n.children.size());
    for(int child:n.children)value+=assigned_value(f,tags,p,child,assignment);
    value=(value%p+p)%p;int result=1;for(int j=0;j<p-1;j++)result=result*value%p;return result;
}
void write_assignment(std::ostream& out,const Assignment& assignment) {
    out<<'[';bool comma=false;
    for(const auto& [family,coordinates]:assignment) {
        if(comma)out<<',';
        comma=true;out<<"{\"family\":"<<family<<",\"vector_zero_coordinates\":";write_ints(out,coordinates);out<<'}';
    }
    out<<']';
}
bool maximal(const Forest& f,int root,const Live& live) {
    for(int a=f.nodes[root].parent;a>=0;a=f.nodes[a].parent)if(live.count(a))return false;
    return true;
}
Live region(const Forest& f,int root) {
    std::vector<int> sub;f.walk(root,sub);return Live(sub.begin(),sub.end());
}
bool covered(Forest& f,int root,const std::map<std::string,int>& goal) {
    std::vector<int> inputs;f.frontier(root,inputs);
    for(int child:inputs)if(!goal.count(f.key(child)))return false;
    return true;
}
CleanupStats cleanup_case(std::ostream& out,int p,int length,int width,bool gap) {
    Forest proto,f;
    auto argument=[&](int j) {
        int r=proto.atom(100*j);
        for(int i=1;i<width;i++)r=proto.disj(r,proto.atom(100*j+i));
        if(gap)r=proto.disj(proto.add('m',{r,proto.atom(20000+j)},-1,1),proto.atom(10000+j));
        return r;
    };
    int r0=argument(0),formula=proto.disj(proto.neg(r0),r0);
    std::vector<ProofNode> proof;std::vector<int> leaves;
    auto leaf=[&](int t) {
        int rho=f.copy(proto,t,int(leaves.size()));leaves.push_back(rho);
        proof.push_back({t,rho,-1,-1,false});return int(proof.size())-1;
    };
    int current=leaf(formula);
    for(int j=1;j<=length;j++) {
        int next=proto.disj(formula,argument(j));int c=leaf(proto.implication(formula,next));
        int rho=f.nodes[proof[c].rho].children[1];
        proof.push_back({next,rho,current,c,false});current=int(proof.size())-1;formula=next;
    }
    f.parents();
    std::vector<Live> states(proof.size());std::vector<std::vector<int>> standard(proof.size());
    std::vector<std::vector<std::vector<int>>> rounds(proof.size());
    std::vector<bool> cuts(f.nodes.size(),false);
    for(size_t v=0;v<proof.size();v++) {
        const auto& node=proof[v];Live live;
        if(node.left<0) {
            for(int id:region(f,node.rho))if(f.nodes[id].kind=='o')live.insert(id);
            int boundary=f.boundary(node.rho);if(boundary>=0)standard[v].push_back(boundary);
        } else {
            live=states[node.left];live.insert(states[node.right].begin(),states[node.right].end());
            int c=proof[node.right].rho,left=f.nodes[f.nodes[c].children[0]].children[0];
            need(f.key(proof[node.left].rho)==f.key(left),"MP antecedent syntax");
            for(int root:{f.boundary(left),f.boundary(node.rho)})if(root>=0)standard[v].push_back(root);
        }
        for(int root:standard[v]) {need(live.erase(root)==1,"standard boundary not live");cuts[root]=true;}
        Live protected_region=region(f,node.rho);std::vector<int> target;f.frontier(f.boundary(node.rho),target);
        std::map<std::string,int> goal;for(int child:target)goal.emplace(f.key(child),child);
        while(true) {
            std::vector<int> selected;
            for(int root:live)if(!protected_region.count(root) && maximal(f,root,live) && covered(f,root,goal))selected.push_back(root);
            if(selected.empty())break;
            rounds[v].push_back(selected);
            for(int root:selected) {cuts[root]=true;need(live.erase(root)==1,"cleanup failed to progress");}
        }
        states[v]=std::move(live);
    }
    std::map<std::string,int> canonical;std::vector<int> tags(f.nodes.size(),-1);
    for(size_t i=0;i<f.nodes.size();i++)if(f.nodes[i].kind=='o') {
        if(cuts[i])tags[i]=int(i);
        else {
            for(int d:region(f,int(i)))if(f.nodes[d].kind=='o')need(!cuts[d],"survivor closure");
            tags[i]=canonical.emplace(f.key(int(i)),int(i)).first->second;
        }
    }
    Evaluation eval(f,tags,p);for(size_t i=0;i<f.nodes.size();i++)eval.expression(int(i));
    std::function<int(int,bool)> depth=[&](int id,bool levels) {
        const auto& n=f.nodes[id];if(n.kind=='x' || n.kind=='t')return 0;
        std::vector<int> children=n.children;if(n.kind=='o') {children.clear();f.frontier(id,children);}
        int maximum=0;for(int child:children)maximum=std::max(maximum,depth(child,levels));
        return maximum+(n.kind=='o' || !levels?1:0);
    };
    int max_level=0,max_depth=0;for(int root:leaves) {max_level=std::max(max_level,depth(root,true));max_depth=std::max(max_depth,depth(root,false));}
    need(max_level==(gap?4:3) && max_depth==(gap?7:5),"depth depends on the proof-spine length");
    out<<"{\"record\":\"case\",\"p\":"<<p<<",\"length\":"<<length<<",\"width\":"<<width
       <<",\"gap\":"<<(gap?"true":"false")<<",\"accuracy\":2,\"ens_level\":"<<max_level
       <<",\"flat_gate_depth\":"<<max_depth<<",\"nodes\":[";
    for(size_t i=0;i<f.nodes.size();i++) {
        if(i)out<<',';
        const auto& n=f.nodes[i];out<<"{\"id\":"<<i<<",\"kind\":\""<<n.kind<<"\",\"children\":";write_ints(out,n.children);
        out<<",\"variable\":"<<n.variable<<",\"residue\":"<<n.residue<<",\"origin\":"<<n.origin
           <<",\"parent\":"<<n.parent<<",\"family\":"<<tags[i]<<",\"cut\":"<<(cuts[i]?"true":"false")<<'}';
    }
    out<<"],\"leaf_roots\":";write_ints(out,leaves);
    // At the initial leaf, the negative R occurrence is already maximal and
    // its raw inputs are covered, but its value is itself a protected input.
    int initial=proof[0].rho,negative=f.nodes[initial].children[0],protected_r=f.nodes[negative].children[0];
    Assignment protected_point{{tags[protected_r],{0}}};
    int before=(1-assigned_value(f,tags,p,negative,protected_point)+p)%p;
    Assignment after=protected_point;after.erase(tags[protected_r]);
    int after_value=(1-assigned_value(f,tags,p,negative,after)+p)%p;
    need(before==0 && after_value==1,"representative protection control");
    out<<",\"protected_input_control\":{\"root\":"<<protected_r<<",\"input_before\":0,\"input_after\":1,\"point\":";
    write_assignment(out,protected_point);out<<"},\"steps\":[";
    CleanupStats stats;bool comma=false,max_control=false;
    auto full_available=[&](int root,const Live& live) {
        for(int d:region(f,root))if(f.nodes[d].kind=='o')need(live.count(d),"a value-copy subtree is missing a block");
    };
    auto fresh=[&](int root,const Live& live) {
        need(cuts[root] && tags[root]==root && maximal(f,root,live),"cut was shared or has a live ancestor");
        for(int other:live)if(other!=root)need(!eval.supports[other].count(tags[root]),"retained axiom uses a removed family");
    };
    auto pair=[&](int a,int b,const Live& live,bool ordinary) {
        need(f.key(a)==f.key(b),"copy syntax mismatch");full_available(a,live);full_available(b,live);
        bool literal=eval.expressions[a]==eval.expressions[b];
        out<<"{\"source\":"<<a<<",\"target\":"<<b<<",\"literal\":"<<(literal?"true":"false");
        if(!literal) {
            if(ordinary)stats.ordinary_repairs++;else stats.input_repairs++;
            Live candidates,joint=eval.supports[a];joint.insert(eval.supports[b].begin(),eval.supports[b].end());
            std::set_symmetric_difference(eval.supports[a].begin(),eval.supports[a].end(),eval.supports[b].begin(),eval.supports[b].end(),std::inserter(candidates,candidates.end()));
            std::vector<int> auxiliaries{-1};auxiliaries.insert(auxiliaries.end(),joint.begin(),joint.end());bool found=false;
            for(int probe:candidates) {
                for(int aux:auxiliaries) {
                    if(aux==probe)continue;
                    Assignment point{{probe,{0}}};if(aux>=0)point[aux]={0};
                    int x=assigned_value(f,tags,p,a,point),y=assigned_value(f,tags,p,b,point);
                    if(x==y)continue;
                    out<<",\"point\":";write_assignment(out,point);
                    out<<",\"source_input_value\":"<<(1-x+p)%p<<",\"target_input_value\":"<<(1-y+p)%p;
                    found=true;break;
                }
                if(found)break;
            }
            need(found,"nonliteral comparison has no saved field witness");
        }
        out<<'}';
    };
    for(size_t v=0;v<proof.size();v++) {
        const auto& node=proof[v];Live live;
        if(node.left<0) {for(int id:region(f,node.rho))if(f.nodes[id].kind=='o')live.insert(id);}
        else {live=states[node.left];live.insert(states[node.right].begin(),states[node.right].end());}
        if(comma)out<<',';
        comma=true;out<<"{\"proof_node\":"<<v<<",\"representative\":"<<node.rho
                      <<",\"left\":"<<node.left<<",\"right\":"<<node.right;
        if(node.left>=0) {
            int c=proof[node.right].rho,left=f.nodes[f.nodes[c].children[0]].children[0];
            std::vector<int> a,b;f.frontier(f.boundary(proof[node.left].rho),a);f.frontier(f.boundary(left),b);
            need(a.size()==b.size(),"ordinary input arities");out<<",\"ordinary_input_pairs\":[";
            for(size_t j=0;j<a.size();j++) {if(j)out<<',';pair(a[j],b[j],live,true);}
            out<<']';
        }
        out<<",\"standard_cuts\":";write_ints(out,standard[v]);
        for(int root:standard[v]) {fresh(root,live);live.erase(root);}
        Live protected_region=region(f,node.rho);std::vector<int> target;f.frontier(f.boundary(node.rho),target);
        std::map<std::string,int> goal;for(int child:target)goal.emplace(f.key(child),child);
        // A nonmaximal root can have covered inputs but an unchanged parent
        // axiom is no longer available after its coefficients are zeroed.
        if(!max_control)for(int parent:live)if(!protected_region.count(parent)) {
            std::vector<int> children;f.frontier(parent,children);
            if(children.empty() || f.nodes[children[0]].kind!='n')continue;
            int inner=f.nodes[children[0]].children[0];
            if(f.nodes[inner].kind!='o' || !live.count(inner) || maximal(f,inner,live) || !covered(f,inner,goal))continue;
            int atom=-1;for(size_t j=1;j<children.size();j++)if(f.nodes[children[j]].kind=='x') {atom=int(j);break;}
            if(atom<0)continue;
            Assignment point{{tags[parent],{0,atom}},{tags[inner],{0}}};
            Assignment removed=point;removed.erase(tags[inner]);
            int old_value=assigned_value(f,tags,p,parent,point),new_value=assigned_value(f,tags,p,parent,removed);
            need(old_value==0 && new_value==p-1,"nonmaximal retained-parent control");
            out<<",\"nonmaximal_control\":{\"inner\":"<<inner<<",\"retained_parent\":"<<parent
               <<",\"companion_coordinate\":"<<atom<<",\"before\":0,\"after\":"<<p-1<<",\"point\":";
            write_assignment(out,point);out<<'}';max_control=true;break;
        }
        out<<",\"cleanup_rounds\":[";
        for(size_t round=0;round<rounds[v].size();round++) {
            if(round)out<<',';
            const auto& selected=rounds[v][round];Live selected_tags;for(int r:selected)selected_tags.insert(tags[r]);
            out<<"{\"roots\":";write_ints(out,selected);out<<",\"input_witnesses\":[";bool sep=false;
            for(int root:selected) {
                fresh(root,live);need(!protected_region.count(root),"protected root selected");
                std::vector<int> inputs;f.frontier(root,inputs);
                for(int child:inputs) {
                    int goal_child=goal.at(f.key(child));
                    for(int tag:selected_tags)need(!eval.supports[child].count(tag) && !eval.supports[goal_child].count(tag),"input witness uses this cleanup batch");
                    if(sep)out<<',';
                    sep=true;pair(child,goal_child,live,false);
                }
            }
            out<<"],\"freshness\":true}";
            for(int root:selected)live.erase(root);
            stats.roots+=long(selected.size());stats.rounds++;
            for(int root:live)for(int d:region(f,root))if(f.nodes[d].kind=='o')need(live.count(d),"cleanup damaged a retained subtree");
        }
        out<<"],\"surviving_or_nodes\":";write_ints(out,std::vector<int>(live.begin(),live.end()));
        need(live==states[v],"replayed schedule differs from plan");
        for(int id:protected_region)if(f.nodes[id].kind=='o' && id!=f.boundary(node.rho))need(live.count(id),"representative proper family was damaged");
        for(int root:live)if(!protected_region.count(root) && maximal(f,root,live))need(!covered(f,root,goal),"cleanup did not saturate");
        out<<",\"representative_intact\":true,\"saturated\":true}";
    }
    Live protected_final=region(f,proof.back().rho),classes;
    for(int root:states.back())if(!protected_final.count(root) && maximal(f,root,states.back()))classes.insert(tags[root]);
    stats.gap_classes=int(classes.size());
    need(stats.ordinary_repairs==length,"ordinary comparisons unexpectedly stayed literal");
    need(stats.gap_classes==(gap?length:0),"unexpected uncovered class count");
    need(length<2 || max_control,"missing nonmaximality control");
    out<<"],\"summary\":{\"cleanup_roots\":"<<stats.roots<<",\"rounds\":"<<stats.rounds
       <<",\"ordinary_nonliteral_pairs\":"<<stats.ordinary_repairs<<",\"cleanup_nonliteral_pairs\":"<<stats.input_repairs
       <<",\"uncovered_off_representative_classes\":"<<stats.gap_classes
       <<",\"nonmaximal_control\":"<<(max_control?"true":"false")<<"},\"all_passed\":true}\n";
    return stats;
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");
        auto parent=std::filesystem::path(argv[2]).parent_path();if(!parent.empty())std::filesystem::create_directories(parent);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"goal_input_cleanup\",\"seed\":null,\"scope\":\"occurrence schedules for excluded-middle and weakening schemas; not a primitive Frege or PC compiler\","
               "\"point_encoding\":\"all proposition values zero; listed first-vector coordinates one; every other coefficient in both vectors zero; companion equations are not imposed\"}\n";
        CleanupStats total;
        for(int p:{2,3})for(int length:{1,2,7})for(int width:{3,7})for(bool gap:{false,true}) {
            auto s=cleanup_case(out,p,length,width,gap);total.roots+=s.roots;total.rounds+=s.rounds;
            total.ordinary_repairs+=s.ordinary_repairs;total.input_repairs+=s.input_repairs;
        }
        out<<"{\"record\":\"summary\",\"cases\":24,\"cleanup_roots\":"<<total.roots<<",\"rounds\":"<<total.rounds
           <<",\"ordinary_nonliteral_pairs\":"<<total.ordinary_repairs<<",\"cleanup_nonliteral_pairs\":"<<total.input_repairs
           <<",\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failed");
        std::cout<<"Twenty-four saturated cleanup schedules passed; "<<total.roots<<" roots removed with "
                 <<total.ordinary_repairs<<" ordinary and "<<total.input_repairs<<" cleanup copy witnesses.\n";
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
