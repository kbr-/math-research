// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Explicit signed-boundary and MOD-value PC derivations, with final-cone support.
#include "pc_boundary.hpp"
#include <set>
using namespace boundary_pc;

struct Support {
    std::set<int> lines,axioms,variables;
    int degree=0;
};
Support support(const Proof& proof,int final) {
    Support result;std::vector<int> pending{final};
    while(!pending.empty()) {
        int id=pending.back();pending.pop_back();
        if(id<0 || !result.lines.insert(id).second)continue;
        const auto& line=proof.lines.at(id);result.degree=std::max(result.degree,line.value.deg());
        for(const auto& term:line.value.terms)for(int v=0;v<NV;v++)
            if(term.first[v])result.variables.insert(v);
        if(line.rule=='a')result.axioms.insert(line.a);
        else {pending.push_back(line.a);if(line.rule=='l')pending.push_back(line.b);}
    }
    return result;
}
void ints(std::ostream& out,const std::set<int>& values) {
    out<<'[';bool comma=false;
    for(int value:values){if(comma)out<<',';comma=true;out<<value;}out<<']';
}
void record(std::ostream& out,const std::string& name,Proof& proof,int final,
            const Poly& target,int ceiling,int variables) {
    need(proof.val(final)==target,"record target: "+name);
    need(proof.degree<=ceiling,"record ceiling: "+name+" actual="+std::to_string(proof.degree)+
         " ceiling="+std::to_string(ceiling));
    need(proof.verify(),"trace verification: "+name);
    if(final>=0)need(!proof.verify(final),"corruption control: "+name);
    for(const auto& line:proof.lines)need(line.value.old(variables),"private variable in "+name);
    proof.write(out,name,final);Support used=support(proof,final);
    out<<"{\"record\":\"support\",\"name\":\""<<name<<"\",\"ceiling\":"<<ceiling
       <<",\"reachable_lines\":"<<used.lines.size()<<",\"reachable_degree\":"<<used.degree
       <<",\"axioms\":";ints(out,used.axioms);out<<",\"variables\":";ints(out,used.variables);
    out<<",\"corrupted_final_rejected\":"<<(final>=0?"true":"null")<<"}\n";
}
Poly substitute(const Poly& input,const std::map<int,Poly>& images) {
    Poly result(input.p);
    for(const auto& term:input.terms) {
        Poly value(input.p,term.second);
        for(int v=0;v<NV;v++)if(term.first[v]) {
            auto found=images.find(v);
            value=value*powp(found==images.end()?variable(input.p,v):found->second,term.first[v]);
        }
        result=result+value;
    }
    return result;
}
// Replay only the dependency cone of the requested conclusion. Each axiom
// callback supplies a checked proof of weight * image(original axiom).
template<class AxiomImage>
int transform(const Proof& source,int final,Proof& destination,const Poly& weight,
              const std::map<int,Poly>& images,AxiomImage axiom) {
    auto used=support(source,final);std::vector<int> ids(source.lines.size(),-1);
    for(size_t i=0;i<source.lines.size();i++)if(used.lines.count(int(i))) {
        const auto& line=source.lines[i];int id=-1;
        if(line.rule=='a')id=axiom(line.a);
        else if(line.rule=='l')id=destination.lc(line.a<0?-1:ids.at(line.a),
                                               line.b<0?-1:ids.at(line.b),line.ca,line.cb);
        else {
            auto found=images.find(line.v);int previous=line.a<0?-1:ids.at(line.a);
            id=found==images.end()?destination.mv(previous,line.v):destination.mul(previous,found->second);
        }
        need(destination.val(id)==weight*substitute(line.value,images),"transformed PC line mismatch");
        ids[i]=id;
    }
    return final<0?-1:ids.at(final);
}
std::map<int,Poly> zero_images(const Block& block) {
    std::map<int,Poly> result;
    for(int v=block.first;v<block.end;v++)result.emplace(v,Poly(block.product.p));
    return result;
}
int introduce_unit_boundary(const Proof& source,int final,Proof& destination,
                            const Block& boundary,int old_count) {
    return transform(source,final,destination,Poly(source.p,1),zero_images(boundary),[&](int a) {
        if(a<old_count+int(boundary.inputs.size()))return destination.ax(a);
        return -1;
    });
}
void describe_block(std::ostream& out,const std::string& role,const Block& block,int first_axiom) {
    out<<"{\"record\":\"block\",\"role\":\""<<role<<"\",\"first_variable\":"<<block.first
       <<",\"end_variable\":"<<block.end<<",\"first_companion\":"<<first_axiom<<",\"product\":";
    jsonpoly(out,block.product);out<<",\"inputs\":[";
    for(size_t j=0;j<block.inputs.size();j++){if(j)out<<',';jsonpoly(out,block.inputs[j]);}
    out<<"]}\n";
}
int append_block(std::vector<Poly>& axioms,const Block& block) {
    int first=int(axioms.size());axioms.insert(axioms.end(),block.axioms.begin(),block.axioms.end());return first;
}
void value_step(std::ostream& out,const std::string& family,int p,const std::vector<Poly>& old,
                const std::vector<int>& sizes,const Poly& alpha,Proof& antecedent,int alpha_final,
                int& next,int expected_degree) {
    Poly one(p,1),beta=powp(alpha,p-1),q=one-beta;
    Block implication=block({alpha,q},1,next);
    int count=int(old.size());Proof leaf(p,augmented(old,implication,p));
    int c=leaf.lc(leaf.ax(count+1),leaf.mul(leaf.ax(count),powp(alpha,p-2)));
    record(out,"implication_leaf",leaf,c,implication.product,2*std::max(alpha.deg(),q.deg())+1,next);
    auto extra=old;extra.push_back(alpha);extra.push_back(q);Proof unit(p,extra);
    int unit_final=introduce_unit_boundary(leaf,c,unit,implication,count);
    record(out,"implication_unit",unit,unit_final,one,std::max(alpha.deg(),q.deg()),int(sizes.size()));

    auto with_q=old;with_q.push_back(q);Proof replaced(p,with_q);
    int learned=transform(antecedent,alpha_final,replaced,one,{},[&](int a){return replaced.ax(a);});
    int refutation=transform(unit,unit_final,replaced,one,{},[&](int a) {
        if(a<count)return replaced.ax(a);
        return a==count?learned:replaced.ax(count);
    });
    record(out,"one_input_refutation",replaced,refutation,one,
           std::max(antecedent.degree,q.deg()),int(sizes.size()));

    Proof result(p,old);int boolean=field_proof(result,beta*(one-beta),sizes);
    int value=transform(replaced,refutation,result,beta,{},[&](int a) {
        return a<count?result.mul(result.ax(a),beta):boolean;
    });
    record(out,"mod_value_weighted",result,value,beta,expected_degree,int(sizes.size()));

    Proof direct=antecedent;int shorter=direct.mul(alpha_final,powp(alpha,p-2));
    record(out,"mod_value_final_reuse",direct,shorter,beta,
           std::max(antecedent.degree,beta.deg()),int(sizes.size()));
    need(!beta.terms.empty(),"vacuous MOD target");
    out<<"{\"record\":\"value_summary\",\"family\":\""<<family<<"\",\"p\":"<<p
       <<",\"target_degree\":"<<beta.deg()<<",\"weighted_degree\":"<<result.degree
       <<",\"reuse_degree\":"<<direct.degree<<",\"wrong_zero_target_rejected\":true}\n";
}
void positive(std::ostream& out,int p) {
    Poly one(p,1),x=variable(p,0),y=variable(p,1);int next=2;
    Block inner=block({x,y},1,next);
    Block proper=block({one-inner.product,one-x},1,next);
    int old_variables=next;std::vector<int> sizes(old_variables,p);sizes[0]=sizes[1]=2;
    auto old=domains(p,sizes);int inner_first=append_block(old,inner),proper_first=append_block(old,proper);
    int count=int(old.size());Block boundary=block(proper.inputs,1,next);
    out<<"{\"record\":\"case\",\"family\":\"positive_antecedent_MOD_value\",\"p\":"<<p
       <<",\"h\":1,\"old_variables\":"<<old_variables<<",\"old_domain_powers\":[2,2,"<<p<<','<<p<<','<<p<<','<<p<<"]}\n";
    describe_block(out,"inner_OR",inner,inner_first);describe_block(out,"proper_A",proper,proper_first);
    describe_block(out,"private_A",boundary,count);
    Proof leaf(p,augmented(old,boundary,p));
    int a=leaf.lc(leaf.ax(count+1),leaf.mul(leaf.ax(count),x));
    a=leaf.lc(a,leaf.mul(leaf.ax(inner_first),boundary.product));
    record(out,"positive_leaf",leaf,a,boundary.product,6,next);
    auto with_inputs=old;with_inputs.insert(with_inputs.end(),boundary.inputs.begin(),boundary.inputs.end());
    Proof unit(p,with_inputs);int unit_final=introduce_unit_boundary(leaf,a,unit,boundary,count);
    record(out,"positive_unit",unit,unit_final,one,6,old_variables);
    need(support(unit,unit_final).degree==3,"positive unit final-cone degree");
    Proof antecedent(p,old);
    int alpha=transform(unit,unit_final,antecedent,proper.product,{},[&](int i) {
        return i<count?antecedent.mul(antecedent.ax(i),proper.product):antecedent.ax(proper_first+i-count);
    });
    record(out,"positive_antecedent",antecedent,alpha,proper.product,6,old_variables);
    auto used=support(antecedent,alpha);
    need(used.axioms.count(proper_first) && used.axioms.count(proper_first+1),"proper-copy support control");
    need(used.axioms.count(inner_first) && !used.axioms.count(inner_first+1),"inner support control");
    value_step(out,"positive",p,old,sizes,proper.product,antecedent,alpha,next,p==2?9:12);

    // Concrete removal of the still-used proper A: r0=x, r1=1, so A maps to xP.
    std::map<int,Poly> images{{proper.first,x},{proper.first+1,one}};
    need(substitute(proper.product,images)==x*inner.product,"positive normalizer");
    auto reduced=domains(p,{2,2,p,p});int inner_new=append_block(reduced,inner);
    Proof pruned(p,reduced);std::vector<int> image_proofs(old.size(),-1);
    for(int i=0;i<count;i++) {
        Poly target=substitute(old[i],images);
        if(target.terms.empty())continue;
        if(i<old_variables)image_proofs[i]=field_proof(pruned,target,{2,2,p,p});
        else if(i<proper_first)image_proofs[i]=pruned.ax(inner_new+i-inner_first);
        else image_proofs[i]=pruned.mul(pruned.ax(inner_new),proper.inputs[i-proper_first]);
        need(pruned.val(image_proofs[i])==target,"positive axiom image");
        need(target.deg()<=old[i].deg(),"positive original degree ledger");
    }
    int pruned_value=transform(antecedent,alpha,pruned,one,images,[&](int i){return image_proofs.at(i);});
    record(out,"positive_proper_A_removed",pruned,pruned_value,x*inner.product,6,inner.end);
    // Keeping later inputs unchanged would fail even for this affine substitution.
    Block later=block({proper.product,y},1,next);
    need(!(substitute(later.axioms[0],images)==later.axioms[0]),"later-input control");
    out<<"{\"record\":\"later_image\",\"family\":\"positive\",\"before\":";
    jsonpoly(out,later.axioms[0]);out<<",\"after\":";jsonpoly(out,substitute(later.axioms[0],images));
    out<<",\"stale_input_rejected\":true}\n";
}
void negative(std::ostream& out,int p) {
    Poly one(p,1),x=variable(p,0),y=variable(p,1);int next=2;
    Block left=block({x,one-x},1,next),right=block({y,one-y},1,next);
    Block proper=block({left.product,right.product},1,next);
    int old_variables=next;std::vector<int> sizes(old_variables,p);sizes[0]=sizes[1]=2;
    auto old=domains(p,sizes);int lf=append_block(old,left),rf=append_block(old,right),wf=append_block(old,proper);
    int count=int(old.size());Block boundary=block(proper.inputs,1,next);
    out<<"{\"record\":\"case\",\"family\":\"negative_antecedent_MOD_value\",\"p\":"<<p
       <<",\"h\":1,\"old_variables\":"<<old_variables<<",\"old_domain_powers\":[2,2,"<<p<<','<<p<<','<<p<<','<<p<<','<<p<<','<<p<<"]}\n";
    describe_block(out,"complementary_X",left,lf);describe_block(out,"complementary_Y",right,rf);
    describe_block(out,"proper_W",proper,wf);describe_block(out,"private_W",boundary,count);
    Proof leaf(p,augmented(old,boundary,p));int a=-1;
    for(int j=0;j<2;j++)for(int k=0;k<2;k++)
        a=leaf.lc(a,leaf.mul(leaf.ax((j==0?lf:rf)+k),boundary.coef[j]));
    record(out,"negative_leaf",leaf,a,one-boundary.product,4,next);
    Proof antecedent(p,old);std::vector<int> learned;
    for(int j=0;j<2;j++) {
        Proof source=leaf;
        int input=source.lc(source.mul(a,boundary.inputs[j]),source.ax(count+j));
        record(out,"augmented_negative_input_"+std::to_string(j),source,input,boundary.inputs[j],5,next);
        int result=eliminate(source,input,antecedent,boundary,sizes);learned.push_back(result);
        record(out,"eliminated_negative_input_"+std::to_string(j),antecedent,result,boundary.inputs[j],5+2*(p-1),old_variables);
        auto used=support(antecedent,result);
        need(!used.axioms.count(wf) && !used.axioms.count(wf+1),"negative core circularity");
        for(int v:used.variables)need(v<proper.first,"negative input proof is not strictly earlier");
    }
    int alpha=-1;
    for(int j=0;j<2;j++)alpha=antecedent.lc(alpha,antecedent.mul(learned[j],proper.coef[j]));
    record(out,"negative_antecedent",antecedent,alpha,one-proper.product,5+2*(p-1),old_variables);
    auto used=support(antecedent,alpha);
    need(!used.axioms.count(wf) && !used.axioms.count(wf+1),"unused negative companions control");
    value_step(out,"negative",p,old,sizes,one-proper.product,antecedent,alpha,next,p==2?10:15);

    // Zero the canonical negative core; its companion images are the learned inputs.
    auto images=zero_images(proper);auto reduced=domains(p,{2,2,p,p,p,p});
    int new_lf=append_block(reduced,left),new_rf=append_block(reduced,right);
    Proof pruned(p,reduced);std::vector<int> input_proofs;
    for(int j=0;j<2;j++) {
        int first=j==0?new_lf:new_rf;
        input_proofs.push_back(pruned.lc(pruned.ax(first),pruned.ax(first+1)));
        need(pruned.val(input_proofs.back())==proper.inputs[j],"negative input certificate");
    }
    // Retain a later block and an actual companion target: this image is nonzero.
    Block later=block({proper.product,y},1,next);
    Poly later_image=substitute(later.axioms[0],images);
    need(!later_image.terms.empty() && !(later_image==later.axioms[0]),"nontrivial later image control");
    Proof old_companions(p,old);int companion=old_companions.ax(wf);
    int mapped=transform(old_companions,companion,pruned,one,images,[&](int i) {
        need(i==wf,"unexpected single-companion support");return input_proofs[0];
    });
    record(out,"negative_proper_companion_image",pruned,mapped,left.product,3,proper.first);
    out<<"{\"record\":\"later_image\",\"family\":\"negative\",\"before\":";
    jsonpoly(out,later.axioms[0]);out<<",\"after\":";jsonpoly(out,later_image);
    out<<",\"stale_input_rejected\":true,\"negative_value_image_is_zero\":"
       <<(substitute(one-proper.product,images).terms.empty()?"true":"false")<<"}\n";
}
int main(int argc,char** argv) {
    try {
        if(argc==2 && std::string(argv[1])=="--help") {
            std::cout<<"Usage: check_signed_boundaries --out NEW_PATH\n";return 0;
        }
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");std::ofstream out(argv[2]);need(bool(out),"open output");
        out<<"{\"schema\":1,\"suite\":\"signed_boundaries\",\"arithmetic\":\"exact ordinary PC\",\"seed\":null,\"scope\":\"fixed derived tautological schemas, h=1, not a PHP proof or arbitrary Frege compiler\"}\n";
        for(int p:{2,3}){positive(out,p);negative(out,p);}
        out<<"{\"record\":\"summary\",\"cases\":4,\"all_passed\":true}\n";
        out.close();need(bool(out),"write output");
        std::cout<<"4 signed-boundary/MOD fixtures, exact PC traces, support and corruption controls passed.\n";
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
