// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Structural proof-spine controls plus exact positive-boundary zero replay.
#include "pc_boundary.hpp"
using namespace boundary_pc;

struct Node {
    char kind;
    int a=-1,b=-1,variable=-1,origin=0;
};
struct Forest {
    std::vector<Node> nodes;
    int add(char kind,int a=-1,int b=-1,int variable=-1,int origin=0) {
        nodes.push_back({kind,a,b,variable,origin});
        return int(nodes.size())-1;
    }
    int atom(int variable) {return add('x',-1,-1,variable);}
    int taut(int variable) {
        int left=atom(variable),right=add('n',atom(variable));
        return add('o',left,right);
    }
    int formula(int kind,int variable) {
        if(kind==0) return taut(variable);
        if(kind==1) {
            int a=add('n',taut(variable)),b=add('n',taut(variable+1));
            return add('n',add('o',a,b));
        }
        if(kind==2) return add('n',add('n',taut(variable)));
        if(kind==3) return add('m',add('n',taut(variable)));
        if(kind==4) {
            int a=taut(variable),b=taut(variable+1),c=taut(variable+2);
            return add('o',a,add('o',b,c));
        }
        return add('t');
    }
    int copy(int id,int origin) {
        Node n=nodes.at(id);
        int a=n.a<0?-1:copy(n.a,origin),b=n.b<0?-1:copy(n.b,origin);
        return add(n.kind,a,b,n.variable,origin);
    }
    int boundary(int id) const {
        while(nodes.at(id).kind=='n') id=nodes[id].a;
        return nodes[id].kind=='o'?id:-1;
    }
    std::string mode(int id) const {
        int parity=0;
        while(nodes.at(id).kind=='n') {id=nodes[id].a;parity^=1;}
        if(nodes[id].kind!='o') return "value";
        return parity?"negative":"positive";
    }
    void descendants(int id,std::vector<int>& result) const {
        result.push_back(id);
        if(nodes[id].a>=0) descendants(nodes[id].a,result);
        if(nodes[id].b>=0) descendants(nodes[id].b,result);
    }
    int or_count(int id) const {
        int total=nodes[id].kind=='o';
        if(nodes[id].a>=0) total+=or_count(nodes[id].a);
        if(nodes[id].b>=0) total+=or_count(nodes[id].b);
        return total;
    }
    void frontier(int id,std::vector<int>& result) const {
        if(nodes[id].kind!='o') {result.push_back(id);return;}
        frontier(nodes[id].a,result);frontier(nodes[id].b,result);
    }
    int depth(int id,bool level) const {
        const auto& n=nodes[id];
        if(n.kind=='x' || n.kind=='t') return 0;
        if(n.kind=='o') {
            std::vector<int> children;frontier(id,children);int maximum=0;
            for(int child:children) maximum=std::max(maximum,depth(child,level));
            return 1+maximum;
        }
        return depth(n.a,level)+(level?0:1);
    }
    bool intact(int root,const std::vector<bool>& live) const {
        std::vector<int> sub;descendants(root,sub);int excluded=boundary(root);
        for(int id:sub) if(nodes[id].kind=='o' && id!=excluded && !live[id]) return false;
        return true;
    }
};
void structural(std::ostream& out,int length,int terminal,bool mixed) {
    Forest f;
    int current=f.formula(terminal,0);
    std::vector<int> antecedents(length),representatives(length+1),leaves;
    representatives[length]=current;
    for(int i=length-1;i>=0;--i) {
        int a=f.formula(mixed?i%4:0,i%2);
        antecedents[i]=a;current=f.add('o',f.add('n',a),current);
        representatives[i]=current;
    }
    leaves.push_back(current);
    for(int i=0;i<length;i++) leaves.push_back(f.copy(antecedents[i],i+1));
    std::vector<int> parent(f.nodes.size(),-1);
    std::vector<bool> live(f.nodes.size(),false);
    int initial=0,fresh=0;
    for(size_t i=0;i<f.nodes.size();i++) {
        const auto& n=f.nodes[i];
        if(n.kind=='o') {live[i]=true;++initial;}
        for(int child:{n.a,n.b}) if(child>=0) {
            need(parent[child]<0,"occurrence unexpectedly shared");
            parent[child]=int(i);
        }
    }
    fresh=initial;
    for(int i=1;i<=length;i++) fresh+=f.or_count(representatives[i]);
    for(int leaf:leaves) {
        int boundary=f.boundary(leaf);
        if(boundary>=0) live[boundary]=false;
        need(f.intact(leaf,live),"leaf proper family damaged");
    }
    auto fresh_root=[&](int selected) {
        if(selected<0) return true;
        for(int a=parent[selected];a>=0;a=parent[a])
            if(f.nodes[a].kind=='o' && live[a]) return false;
        return true;
    };
    out<<"{\"record\":\"structural_case\",\"length\":"<<length<<",\"terminal\":"<<terminal
       <<",\"mixed_antecedents\":"<<(mixed?"true":"false")<<",\"source_depth\":"
       <<f.depth(current,false)<<",\"ens_level\":"<<f.depth(current,true)
       <<",\"leaf_only_blocks\":"<<initial<<",\"fresh_line_blocks\":"<<fresh<<",\"nodes\":[";
    for(size_t i=0;i<f.nodes.size();i++) {
        if(i) out<<',';
        const auto& n=f.nodes[i];
        out<<"{\"id\":"<<i<<",\"kind\":\""<<n.kind<<"\",\"a\":"<<n.a<<",\"b\":"<<n.b
           <<",\"variable\":"<<n.variable<<",\"origin_leaf\":"<<n.origin<<"}";
    }
    out<<"],\"leaf_roots\":[";
    for(size_t i=0;i<leaves.size();i++) {if(i) out<<',';out<<leaves[i];}
    out<<"],\"steps\":[";
    int removed=0;
    for(int i=0;i<length;i++) {
        int rep=representatives[i],next=representatives[i+1];
        need(f.intact(rep,live),"live implication lost proper descendants");
        int left=f.boundary(antecedents[i]),right=f.boundary(next);
        need(fresh_root(left) && fresh_root(right),"selected interface has a live OR ancestor");
        for(int selected:{left,right}) if(selected>=0) {
            need(live[selected],"interface removed twice");
            live[selected]=false;++removed;
        }
        need(f.intact(next,live),"inherited consequent lost a proper block");
        // Restoring the original implication root would break the invariant.
        live[current]=true;
        bool bad=(left>=0 && !fresh_root(left)) || (right>=0 && !fresh_root(right));
        live[current]=false;
        if(left>=0 || right>=0) need(bad,"ancestor-restoration control missed");
        if(i) out<<',';
        out<<"{\"implication\":"<<rep<<",\"antecedent_leaf\":"<<leaves[i+1]
           <<",\"inherited_consequent\":"<<next<<",\"left_interface\":"<<left
           <<",\"right_interface\":"<<right<<",\"mode\":\""<<f.mode(next)
           <<"\",\"proper_family_intact\":true,\"freshness\":true"
             ",\"ancestor_control_applicable\":"<<((left>=0 || right>=0)?"true":"false")<<"}";
    }
    int surviving=0;
    for(bool value:live) surviving+=value;
    out<<"],\"removed_mp_interfaces\":"<<removed<<",\"surviving_blocks\":"<<surviving
       <<",\"surviving_ids\":[";
    bool comma=false;
    for(size_t i=0;i<live.size();i++) if(live[i]) {
        if(comma) out<<',';
        comma=true;out<<i;
        need(f.intact(int(i),live),"remaining OR subtree contains a removed proper block");
    }
    out<<"],\"all_passed\":true}\n";
    if(!mixed && length==2 && terminal==0)
        need(initial==7 && fresh==11 && surviving==0,"two-step projection control");
}
void positive_zero(std::ostream& out,int p,bool wrapped) {
    Poly one(p,1),x=variable(p,0),y=variable(p,1);int next=2;
    Block b=block({x,y},1,next);
    auto old=domains(p,{2,2});old.push_back(one-x);
    auto raw_axioms=old;
    raw_axioms.insert(raw_axioms.end(),b.axioms.begin(),b.axioms.end());
    for(int r=b.first;r<b.end;r++) raw_axioms.push_back(powp(variable(p,r),p)-variable(p,r));
    int extra=int(raw_axioms.size());
    if(wrapped) raw_axioms.push_back(one-b.product);
    else {raw_axioms.push_back(x);raw_axioms.push_back(y);}
    Proof raw(p,raw_axioms);
    int value=raw.lc(raw.ax(3),raw.mul(raw.ax(2),b.product));
    need(raw.val(value)==b.product,"positive value from one live companion");
    int unit=value;
    if(wrapped) unit=raw.lc(unit,raw.ax(extra));
    else for(int i=0;i<2;i++) unit=raw.lc(unit,raw.mul(raw.ax(extra+i),b.coef[i]));
    need(raw.val(unit)==one && raw.verify() && raw.degree==3,"raw positive proof");
    need(!raw.verify(unit),"raw corruption missed");
    auto target_axioms=old;target_axioms.push_back(x);target_axioms.push_back(y);
    Proof clean(p,target_axioms);std::vector<int> mapped;std::array<int,NV> zero{};
    for(const auto& line:raw.lines) {
        int id=-1;
        if(line.rule=='a') {
            Poly image=specialize(raw.axioms[line.a],b.first,zero);
            if(!image.terms.empty()) {
                auto found=std::find(clean.axioms.begin(),clean.axioms.end(),image);
                need(found!=clean.axioms.end(),"zeroed axiom lacks input or old justification");
                id=clean.ax(int(found-clean.axioms.begin()));
            }
        } else if(line.rule=='l') {
            id=clean.lc(line.a<0?-1:mapped[line.a],line.b<0?-1:mapped[line.b],line.ca,line.cb);
        } else if(line.v<b.first) id=clean.mv(line.a<0?-1:mapped[line.a],line.v);
        need(clean.val(id)==specialize(line.value,b.first,zero),"zeroed inference mismatch");
        mapped.push_back(id);
    }
    int final=mapped.at(unit);
    need(clean.val(final)==one && clean.verify() && clean.degree<=raw.degree,"positive zero replay");
    need(!clean.verify(final),"clean corruption missed");
    for(const auto& line:clean.lines) need(line.value.old(b.first),"removed coefficient survived");
    // Companions do not become zero: their input assumptions are essential.
    need(specialize(b.axioms[0],b.first,zero)==x,"zero companion must become input");
    out<<"{\"record\":\"positive_zero_case\",\"p\":"<<p<<",\"wrapped\":"
       <<(wrapped?"true":"false")<<",\"raw_degree\":"<<raw.degree
       <<",\"zeroed_degree\":"<<clean.degree<<",\"old_base_satisfiable_at\":[1,0]"
         ",\"live_companion_used\":true,\"input_image_is_nonzero\":true"
         ",\"all_passed\":true}\n";
    raw.write(out,wrapped?"wrapped_positive_raw":"direct_positive_raw",unit);
    clean.write(out,wrapped?"wrapped_positive_zeroed":"direct_positive_zeroed",final);
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output already exists");
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"inherited_consequent\",\"seed\":null,"
               "\"structural_scope\":\"conditional MP spines; not a source-leaf compiler\","
               "\"node_kinds\":{\"x\":\"atom\",\"t\":\"TRUE\",\"n\":\"NOT\","
               "\"o\":\"binary OR\",\"m\":\"one-input MOD_0\"}}\n";
        structural(out,2,0,false);
        for(int length:{1,2,7,31}) for(int terminal=0;terminal<6;terminal++)
            structural(out,length,terminal,true);
        for(int p:{2,3}) for(bool wrapped:{false,true}) positive_zero(out,p,wrapped);
        out<<"{\"record\":\"summary\",\"structural_cases\":25,\"positive_zero_cases\":4,"
               "\"pc_traces\":8,\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failed");
        std::cout<<"25 structural inheritance cases and four exact positive zero replays passed.\n";
    } catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}
}
