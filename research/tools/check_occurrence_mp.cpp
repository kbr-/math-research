// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// A -> (A AND TRUE): separate the antecedent occurrence from the conclusion copy.
#include "pc_boundary.hpp"
using namespace boundary_pc;
bool uses(const Poly& value,int first,int end){
    for(const auto& term:value.terms)for(int i=first;i<end;i++)if(term.first[i])return true;
    return false;
}
template<class AxiomImage>
int weighted(const Proof& source,int final,Proof& target,const Poly& weight,AxiomImage axiom){
    std::vector<int> ids;
    for(const auto& line:source.lines){
        int id=-1;
        if(line.rule=='a')id=axiom(line.a);
        else if(line.rule=='l')id=target.lc(line.a<0?-1:ids.at(line.a),
                                          line.b<0?-1:ids.at(line.b),line.ca,line.cb);
        else id=target.mv(line.a<0?-1:ids.at(line.a),line.v);
        need(target.val(id)==weight*line.value,"weighted line mismatch");ids.push_back(id);
    }
    return final<0?-1:ids.at(final);
}
void check(std::ostream& out,const std::string& name,Proof& proof,int final,const Poly& target,int bound){
    need(proof.val(final)==target && proof.degree<=bound && proof.verify(),"invalid "+name);
    need(final>=0 && !proof.verify(final),"corruption control "+name);
    proof.write(out,name,final);
    out<<"{\"record\":\"verified\",\"name\":\""<<name<<"\",\"actual_degree\":"<<proof.degree
       <<",\"bound\":"<<bound<<",\"corrupted_final_rejected\":true}\n";
}
Proof reorder(const Proof& source,const std::vector<Poly>& axioms){
    Proof result=source;result.axioms=axioms;
    for(auto& line:result.lines)if(line.rule=='a'){
        auto found=std::find(axioms.begin(),axioms.end(),source.axioms.at(line.a));
        need(found!=axioms.end(),"missing axiom during permutation");
        line.a=int(found-axioms.begin());
    }
    need(result.verify(),"axiom permutation changed proof");return result;
}
void run_case(std::ostream& out,int p){
    Poly one(p,1),zero(p),x=variable(p,0);int next=1;
    Block right=block({x,one-x},1,next),left=block({x,one-x},1,next);
    Block conclusion=block({right.product,zero},1,next);
    auto old=domains(p,{2,p,p});old.insert(old.end(),right.axioms.begin(),right.axioms.end());
    auto before_left=domains(p,{2,p,p,p,p});
    before_left.insert(before_left.end(),right.axioms.begin(),right.axioms.end());
    before_left.insert(before_left.end(),left.axioms.begin(),left.axioms.end());
    auto full=augmented(before_left,conclusion,p);int count=int(full.size());
    int rf=5,lf=7,df=int(before_left.size());
    auto premise_axioms=full;premise_axioms.push_back(left.product);premise_axioms.push_back(conclusion.product);
    Proof implication(p,premise_axioms);int difference=-1;
    for(int i=0;i<2;i++){
        difference=implication.lc(difference,implication.mul(implication.ax(rf+i),left.coef[i]));
        difference=implication.lc(difference,implication.mul(implication.ax(lf+i),right.coef[i]),1,-1);
    }
    need(implication.val(difference)==right.product-left.product,"copy agreement");
    int derived_right=implication.lc(implication.ax(count),difference);
    int unit=implication.lc(implication.ax(count+1),implication.mul(derived_right,conclusion.coef[0]));
    out<<"{\"record\":\"case\",\"p\":"<<p<<",\"h\":1,"
           "\"variables\":[\"x\",\"right_r0\",\"right_r1\",\"left_r0\",\"left_r1\",\"B_r0\",\"B_r1\"],"
           "\"left_product\":";jsonpoly(out,left.product);out<<",\"right_product\":";jsonpoly(out,right.product);
    out<<",\"B_inner_product\":";jsonpoly(out,conclusion.product);out<<"}\n";
    check(out,"implication_input_refutation",implication,unit,one,4);
    auto joined_axioms=full;joined_axioms.push_back(conclusion.product);Proof joined(p,joined_axioms);
    int learned_left=joined.lc(joined.ax(lf),joined.ax(lf+1));
    need(joined.val(learned_left)==left.product,"antecedent conversion");
    int joined_unit=weighted(implication,unit,joined,one,[&](int a){
        if(a<count)return joined.ax(a);
        return a==count?learned_left:joined.ax(count);
    });
    check(out,"joined_premise_refutation",joined,joined_unit,one,4);
    Proof raw(p,full);
    int target=weighted(joined,joined_unit,raw,right.product,[&](int a){
        return a<count?raw.mul(raw.ax(a),right.product):raw.ax(df);
    });
    check(out,"negative_conclusion_input",raw,target,right.product,6);
    // Remove the last variable family first, then permute the remaining axioms
    // into the old-engine layout for removing the left family.
    Proof without_B(p,before_left);
    int first=eliminate(raw,target,without_B,conclusion,{2,p,p,p,p});
    int first_bound=std::max({raw.degree+(p-1)*2,raw.degree+2,p*2});
    check(out,"B_interface_removed",without_B,first,right.product,first_bound);
    for(const auto& line:without_B.lines)need(!uses(line.value,conclusion.first,conclusion.end),"B coefficient survived");
    Proof permuted=reorder(without_B,augmented(old,left,p));Proof clean(p,old);
    int last=eliminate(permuted,first,clean,left,{2,p,p});
    int last_bound=std::max({without_B.degree+(p-1),without_B.degree+2,p*2});
    check(out,"both_interfaces_removed",clean,last,right.product,last_bound);
    for(const auto& line:clean.lines)need(line.value.old(left.first),"removed interface variable survived");
    // A shared root would occur in the conclusion block's input and target.
    int repeat=conclusion.first;Block shared=block({left.product,zero},1,repeat);
    need(uses(shared.axioms[0],left.first,left.end),"shared-copy freshness control");
    need(uses(left.product,left.first,left.end),"shared target control");
    need(!uses(conclusion.axioms[0],left.first,left.end) &&
         !uses(right.product,left.first,left.end),"separate-copy freshness");
    out<<"{\"record\":\"freshness_control\",\"shared_B_companion\":";jsonpoly(out,shared.axioms[0]);
    out<<",\"separated_B_companion\":";jsonpoly(out,conclusion.axioms[0]);
    out<<",\"shared_copy_fails_axiom_and_target_freshness\":true,\"separated_copy_passes\":true,"
           "\"surviving_right_copy_retained\":true}\n";
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");std::ofstream out(argv[2]);need(bool(out),"open output");
        out<<"{\"schema\":1,\"suite\":\"occurrence_mp\",\"seed\":null,"
               "\"scope\":\"one source-shaped MP pattern with supplied input proofs; not a full Frege compiler\"}\n";
        for(int p:{2,3})run_case(out,p);
        out<<"{\"record\":\"summary\",\"cases\":2,\"all_passed\":true}\n";
        out.close();need(bool(out),"write output");
        std::cout<<"Two exact occurrence-separated MP replays and shared-copy freshness controls passed.\n";
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
