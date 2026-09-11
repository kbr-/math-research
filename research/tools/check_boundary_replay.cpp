// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact PC traces for old-consequence elimination and implication-boundary replay.
// Fixed synthetic cases, not PHP proofs. Run through compute.sh with --out PATH.
#include "pc_boundary.hpp"
using namespace boundary_pc;
void old_case(std::ostream& out,int p,int h,const std::string& kind) {
    Poly x=variable(p,0),y=variable(p,1);
    Poly g=kind=="nonlinear_input"?x*y:x;
    std::vector<int> sizes{p,2};auto old=domains(p,sizes);old.push_back(g*g);
    int next=2;Block U=block({g},h,next);
    Proof src(p,augmented(old,U,p));
    int final=src.lc(src.ax(int(old.size())),src.mul(src.ax(2),U.coef[0]));
    if(kind=="larger_boundary")final=src.mul(final,y*y);
    Poly target=src.val(final);int d=src.degree,k=target.deg(),delta=g.deg();
    need(target==(kind=="larger_boundary"?g*y*y:g),"source consequence");
    need(src.verify(),"invalid source proof");
    Proof dst(p,old);int result=eliminate(src,final,dst,U,sizes);
    int bound=std::max({d+(p-1)*delta,d+k,p*k});
    check_proof(dst,result,target,bound,U.first);
    out<<"{\"record\":\"case\",\"family\":\"old_consequence\",\"kind\":\""<<kind
       <<"\",\"p\":"<<p<<",\"h\":"<<h<<",\"old_variables\":2,\"variables\":"<<next
       <<",\"domain_sizes\":["<<p<<",2],\"delta\":"<<delta<<",\"target_degree\":"<<k
       <<",\"source_degree\":"<<d<<",\"bound\":"<<bound<<",\"actual_degree\":"<<dst.degree<<"}\n";
    src.write(out,"source",final);dst.write(out,"eliminated",result);
    out<<"{\"record\":\"case_passed\",\"corrupted_trace_rejected\":true}\n";
}
void mp_case(std::ostream& out,int p,int h,bool disjunction) {
    Poly one(p,1),x=variable(p,0),y=variable(p,1),b=x;
    int next=2;Block B{Poly(p),{},{},{},2,2};
    if(disjunction){B=block({one-x,y},h,next);b=B.product;}
    int first=next;
    Block U=block(disjunction?std::vector<Poly>{x,one-x,y}:std::vector<Poly>{x,one-x},h,next);
    std::vector<int> sizes(first,p);sizes[0]=sizes[1]=2;
    auto old=domains(p,sizes);int a_index=int(old.size());old.push_back(x);
    int B_index=int(old.size());if(disjunction)old.insert(old.end(),B.axioms.begin(),B.axioms.end());
    auto ax=augmented(old,U,p);int E_index=int(old.size());
    Proof antecedent(p,ax);
    int a_final=antecedent.lc(antecedent.ax(E_index),antecedent.mul(antecedent.ax(a_index),one-U.product));
    need(antecedent.val(a_final)==x && antecedent.verify(),"antecedent source");
    Proof implication(p,ax);
    int c_final=implication.lc(implication.ax(E_index),implication.ax(E_index+1));
    need(implication.val(c_final)==U.product && implication.verify(),"implication source");
    Proof dst(p,old);int learned_a=eliminate(antecedent,a_final,dst,U,sizes);
    std::vector<int> annihilators{dst.mul(learned_a,b)};
    if(disjunction)for(size_t i=0;i<B.axioms.size();i++)annihilators.push_back(dst.ax(B_index+int(i)));
    else annihilators.push_back(field_proof(dst,b*(one-b),sizes));
    std::array<int,NV> zero{};
    int result=replay(implication,c_final,dst,int(old.size()),U,b,zero,[&](int i){return annihilators.at(i);});
    int H=disjunction?0:2;
    int bound=std::max({antecedent.degree+(p-1),implication.degree+b.deg(),H});
    check_proof(dst,result,b,bound,first);
    out<<"{\"record\":\"case\",\"family\":\"implication_boundary\",\"kind\":\""
       <<(disjunction?"disjunction":"atom")<<"\",\"p\":"<<p<<",\"h\":"<<h
       <<",\"old_variables\":"<<first<<",\"variables\":"<<next
       <<",\"antecedent_degree\":"<<antecedent.degree<<",\"implication_degree\":"<<implication.degree
       <<",\"boundary_degree\":"<<b.deg()<<",\"bound\":"<<bound<<",\"actual_degree\":"<<dst.degree
       <<",\"antecedent_uses_removed_block\":true,\"boundary_preserved\":true}\n";
    antecedent.write(out,"antecedent",a_final);implication.write(out,"implication",c_final);
    dst.write(out,"eliminated",result);
    out<<"{\"record\":\"case_passed\",\"corrupted_trace_rejected\":true}\n";
}
void controls(std::ostream& out,int p) {
    Poly one(p,1),x=variable(p,0);int next=1;
    Block U=block({x,one-x},1,next);
    // With only Boolean/domain axioms and U, c is derivable but x need not vanish.
    // x=1,r0=1,r1=0 satisfies the domains and companions, and c=0 while x=1.
    std::array<int,NV> point{};point[0]=1;point[1]=1;
    need(specialize(x*x-x,0,point).terms.empty(),"control domain");
    for(const auto& e:U.axioms)need(specialize(e,0,point).terms.empty(),"control companion");
    need(specialize(U.product,0,point).terms.empty() && specialize(x,0,point)==one,"missing antecedent witness");
    out<<"{\"record\":\"control\",\"kind\":\"missing_annihilator\",\"p\":"<<p
       <<",\"x\":1,\"r0\":1,\"r1\":0,\"c_value\":0,\"b_value\":1}\n";
    Block V=block({U.product},1,next);
    need(!V.axioms[0].old(U.first),"freshness control vacuous");
    // Keep the later block coefficient s while zeroing only r0,r1.
    Poly changed(p);
    for(const auto& term:V.axioms[0].terms) if(!term.first[1] && !term.first[2])changed.add(term.first,term.second);
    need(!(changed==V.axioms[0]),"later input dependency went undetected");
    out<<"{\"record\":\"control\",\"kind\":\"later_block_not_old\",\"p\":"<<p<<",\"before\":";
    jsonpoly(out,V.axioms[0]);out<<",\"after_zeroing_U\":";jsonpoly(out,changed);out<<"}\n";
}
int main(int argc,char** argv) {
    try {
        if(argc==2 && std::string(argv[1])=="--help") {
            std::cout<<"Usage: check_boundary_replay --out NEW_PATH\n";return 0;
        }
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists; choose a new path");
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"boundary_replay\",\"seed\":null,\"arithmetic\":\"exact sparse ordinary polynomials\",\"scope\":\"synthetic PC traces; not PHP or global elimination\"}\n";
        int cases=0;
        for(int p:{2,3,5,7}) {
            for(int h:{1,2}) {
                for(const std::string kind:{"affine_input","nonlinear_input","larger_boundary"}){old_case(out,p,h,kind);++cases;}
                for(bool disj:{false,true}){mp_case(out,p,h,disj);++cases;}
            }
            controls(out,p);
        }
        out<<"{\"record\":\"summary\",\"proof_cases\":"<<cases<<",\"corrupted_trace_controls\":"<<cases
           <<",\"hypothesis_controls\":8,\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failed");
        std::cout<<cases<<" exact PC transformations and corrupted-trace controls passed; 8 hypothesis controls checked.\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
