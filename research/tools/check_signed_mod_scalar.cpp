// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact conversions between signed MOD values and scalar proof invariants.
#include "pc_boundary.hpp"
using namespace boundary_pc;

template<class AxiomImage>
int weighted_copy(const Proof& source,int final,Proof& target,const Poly& weight,AxiomImage axiom) {
    std::vector<int> ids;
    for(const auto& line:source.lines) {
        int id=-1;
        if(line.rule=='a') id=axiom(line.a);
        else if(line.rule=='l')
            id=target.lc(line.a<0?-1:ids.at(line.a),line.b<0?-1:ids.at(line.b),line.ca,line.cb);
        else id=target.mv(line.a<0?-1:ids.at(line.a),line.v);
        need(target.val(id)==weight*line.value,"weighted conversion mismatch");
        ids.push_back(id);
    }
    return final<0?-1:ids.at(final);
}
void trace(std::ostream& out,const std::string& name,Proof& proof,int final,
           const Poly& target,int bound) {
    need(proof.val(final)==target && proof.degree<=bound && proof.verify(),name);
    need(final>=0 && !proof.verify(final),"corruption control "+name);
    proof.write(out,name,final);
    out<<"{\"record\":\"verified\",\"name\":\""<<name<<"\",\"degree\":"<<proof.degree
       <<",\"bound\":"<<bound<<",\"corruption_rejected\":true}\n";
}
int planted_scalar(Proof& proof,const Poly& y) {
    return proof.lc(proof.mul(proof.ax(3),y),proof.ax(4));
}
void run_case(std::ostream& out,int p) {
    Poly one(p,1),x=variable(p,0),y=variable(p,1),z=variable(p,2);
    Poly u=x*y+z-one,power=powp(u,p-1),nonzero_value=one-power;
    std::vector<int> sizes={2,p,p};
    auto domain=domains(p,sizes);
    auto zero_axioms=domain;zero_axioms.push_back(x-one);zero_axioms.push_back(z+y-one);
    auto nonzero_axioms=domain;nonzero_axioms.push_back(x-one);nonzero_axioms.push_back(z+y-Poly(p,2));
    out<<"{\"record\":\"case\",\"p\":"<<p
       <<",\"variables\":[\"Boolean_x\",\"field_y\",\"field_z\"],\"scalar\":";jsonpoly(out,u);
    out<<",\"zero_base_model\":[1,0,1],\"nonzero_base_model\":[1,0,"<<2%p<<"]}\n";
    Proof scalar(p,zero_axioms);int s=planted_scalar(scalar,y);
    trace(out,"zero_scalar_from_old_equations",scalar,s,u,2);
    Proof value=scalar;int a=value.mul(s,powp(u,p-2));
    trace(out,"zero_scalar_to_mod_value",value,a,power,2*(p-1));
    Proof recovered=value;int recovered_scalar=a;
    if(p>2) {
        int frobenius=field_proof(recovered,powp(u,p)-u,sizes);
        recovered_scalar=recovered.lc(recovered.mul(a,u),frobenius,1,-1);
    }
    trace(out,"mod_value_to_zero_scalar",recovered,recovered_scalar,u,p==2?2:2*p);

    Proof negative(p,nonzero_axioms);int shift=planted_scalar(negative,y);
    need(negative.val(shift)==u-one,"nonzero planted scalar");
    Poly geometric(p);
    for(int j=0;j<p-1;j++) geometric=geometric+powp(u,j);
    int negative_value=negative.mul(shift,Poly(p,-1)*geometric);
    trace(out,"nonzero_mod_value_from_old_equations",negative,negative_value,nonzero_value,2*(p-1));
    auto augmented=nonzero_axioms;augmented.push_back(u);
    Proof forward(p,augmented);
    int copied=weighted_copy(negative,negative_value,forward,one,[&](int i){return forward.ax(i);});
    int contradiction=forward.lc(copied,forward.mul(forward.ax(5),powp(u,p-2)));
    trace(out,"nonzero_value_to_scalar_refutation",forward,contradiction,one,2*(p-1));

    Proof short_refutation(p,augmented);int shifted=planted_scalar(short_refutation,y);
    int refuted=short_refutation.lc(short_refutation.ax(5),shifted,1,-1);
    trace(out,"direct_scalar_refutation",short_refutation,refuted,one,2);
    Proof back(p,nonzero_axioms);
    int back_value=weighted_copy(short_refutation,refuted,back,nonzero_value,[&](int i) {
        if(i<5) return back.mul(back.ax(i),nonzero_value);
        return field_proof(back,nonzero_value*u,sizes);
    });
    trace(out,"scalar_refutation_to_nonzero_value",back,back_value,nonzero_value,2*p);

    // A positive MOD conclusion can be extracted directly from a refutation
    // under 1-u^(p-1), by weighting with u rather than u^(p-1).
    auto premise_axioms=zero_axioms;premise_axioms.push_back(one-power);
    Proof premise(p,premise_axioms);
    int scalar_proof=planted_scalar(premise,y);
    int premise_unit=premise.lc(premise.ax(5),premise.mul(scalar_proof,powp(u,p-2)));
    trace(out,"positive_mod_remaining_input_refutation",premise,premise_unit,one,2*(p-1));
    Proof extracted(p,zero_axioms);
    int extracted_scalar=weighted_copy(premise,premise_unit,extracted,u,[&](int i) {
        if(i<5) return extracted.mul(extracted.ax(i),u);
        return field_proof(extracted,u*(one-power),sizes);
    });
    trace(out,"positive_mod_scalar_weighted_extraction",extracted,extracted_scalar,u,2*p);
}
struct F9 {int a,b;};
F9 product(F9 x,F9 y) {
    return {(x.a*y.a+2*x.b*y.b)%3,(x.a*y.b+x.b*y.a)%3};
}
void domain_control(std::ostream& out) {
    // F9 = F3[i]/(i^2-2); no element of F3 squares to 2.
    for(int t=0;t<3;t++) need(t*t%3!=2,"quadratic control reducible");
    F9 u{0,1},v{0,2},uv=product(u,v),u2=product(u,u);
    need(uv.a==1 && uv.b==0,"inverse control");
    need(u2.a==2 && u2.b==0,"nonzero MOD value control");
    out<<"{\"record\":\"missing_domain_control\",\"p\":3,\"extension\":\"i^2=2\","
           "\"u\":[0,1],\"v\":[0,2],\"uv_minus_one\":[0,0],"
           "\"one_minus_u_squared\":[2,0],"
           "\"scalar_refutation_identity\":\"1=-(uv-1)+v*u\","
           "\"domain_free_value_implication_fails\":true}\n";
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");
        auto parent=std::filesystem::path(argv[2]).parent_path();
        if(!parent.empty()) std::filesystem::create_directories(parent);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"signed_mod_scalar\",\"seed\":null}\n";
        for(int p:{2,3,5}) run_case(out,p);
        domain_control(out);
        out<<"{\"record\":\"summary\",\"cases\":3,\"pc_traces\":27,"
               "\"missing_domain_controls\":1,\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failed");
        std::cout<<"27 signed MOD scalar traces and the missing-domain control passed.\n";
    } catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}
}
