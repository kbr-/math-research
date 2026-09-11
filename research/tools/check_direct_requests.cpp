// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Four-vertex path: PC degree two, NS degree three, and normalizer tradeoffs.
#include "pc_boundary.hpp"
using namespace boundary_pc;
int ns(const Poly& target,const std::vector<Poly>& axioms,const std::vector<Poly>& cofactors){
    need(axioms.size()==cofactors.size(),"NS arity");Poly sum(target.p);int d=0;
    for(size_t i=0;i<axioms.size();i++){
        auto term=axioms[i]*cofactors[i];sum=sum+term;d=std::max(d,term.deg());
    }
    need(sum==target,"NS identity");return d;
}
void polynomials(std::ostream& out,const std::vector<Poly>& values){
    out<<'[';for(size_t i=0;i<values.size();i++){if(i)out<<',';jsonpoly(out,values[i]);}out<<']';
}
int functional(const Poly& q){
    int value=0;
    for(const auto& term:q.terms){
        int mask=0;
        for(int v=0;v<NV;v++)if(term.first[v]){
            need(v<4,"dual variable");mask|=1<<v;
        }
        if(mask==0 || mask==1 || mask==2 || mask==3 || mask==6)value=(value+term.second)%q.p;
    }
    return value;
}
void field_case(std::ostream& out,int p){
    Poly one(p,1),zero(p);std::vector<Poly> x;
    for(int i=0;i<4;i++)x.push_back(variable(p,i));
    std::vector<Poly> inputs{one-x[0],x[0]*(one-x[1]),x[1]*(one-x[2]),x[2]*(one-x[3]),x[3]};
    auto base=domains(p,{2,2,2,2}),axioms=base;axioms.insert(axioms.end(),inputs.begin(),inputs.end());
    Proof proof(p,axioms);int current=proof.ax(4);
    for(int i=1;i<4;i++)current=proof.lc(proof.mul(current,one-x[i]),proof.ax(4+i));
    current=proof.lc(current,proof.ax(8));
    need(proof.val(current)==one && proof.degree==2 && proof.verify(),"path PC proof");
    need(!proof.verify(current),"PC corruption control");
    out<<"{\"record\":\"case\",\"p\":"<<p<<",\"variables\":[\"x0\",\"x1\",\"x2\",\"x3\"],\"inputs\":";
    polynomials(out,inputs);out<<"}\n";proof.write(out,"path_PC_degree_two",current);
    std::vector<Poly> beta{one-x[2],one-x[2],x[0],one,x[2]};
    int d=ns(one,inputs,beta);need(d==3,"NS degree-three witness");
    out<<"{\"record\":\"NS_certificate\",\"degree\":"<<d<<",\"cofactors\":";polynomials(out,beta);out<<"}\n";
    need(functional(one)==1,"dual normalization");
    int rows=0;
    for(size_t i=0;i<inputs.size();i++){
        std::vector<Poly> multipliers{one};
        if(inputs[i].deg()==1)multipliers.insert(multipliers.end(),x.begin(),x.end());
        for(const auto& q:multipliers){
            need(functional(q*inputs[i])==0,"NS degree-two dual");++rows;
            out<<"{\"record\":\"dual_check\",\"axiom\":"<<i<<",\"multiplier\":";
            jsonpoly(out,q);out<<",\"value\":0}\n";
        }
    }
    for(const auto& f:base)need(functional(f)==0,"Boolean-domain dual");
    need(rows==13,"all degree-two nondomain rows");
    out<<"{\"record\":\"dual\",\"degree\":2,\"squarefree_support_masks\":[0,1,2,3,6],"
           "\"all_other_masks_zero\":true,\"nondomain_rows\":13}\n";
    // A single factor using affine coefficients vanishes identically.
    Poly error=one;for(size_t i=0;i<inputs.size();i++)error=error-beta[i]*inputs[i];
    need(error.terms.empty(),"affine one-factor normalizer");
    Proof coefficient_fields(p,base);
    for(const auto& b:beta){
        int id=field_proof(coefficient_fields,powp(b,p)-b,{2,2,2,2});
        need(coefficient_fields.val(id)==powp(b,p)-b,"affine field image");
    }
    need(coefficient_fields.verify() && coefficient_fields.degree<=p,"coefficient-field degree");
    coefficient_fields.write(out,"affine_coefficient_fields",
                             coefficient_fields.lines.empty()?-1:int(coefficient_fields.lines.size())-1);
    // Three constant vectors: (g0+g1), (g2+g3), and g4.
    Poly product=(one-inputs[0]-inputs[1])*(one-inputs[2]-inputs[3])*(one-inputs[4]);
    std::vector<Poly> domain_cofactors(4,zero);
    domain_cofactors[1]=Poly(p,-1)*x[0]*(one-x[2])*(one-x[3]);
    domain_cofactors[3]=Poly(p,-1)*x[0]*x[1]*x[2];
    int product_degree=ns(product,base,domain_cofactors);need(product_degree==5,"three-factor domain witness");
    out<<"{\"record\":\"constant_normalizer\",\"accuracy\":3,\"vectors\":[[1,1,0,0,0],[0,0,1,1,0],[0,0,0,0,1]],"
           "\"product\":";jsonpoly(out,product);out<<",\"domain_cofactors\":";
    polynomials(out,domain_cofactors);out<<",\"certificate_degree\":5}\n";
    // Weighted positive-antecedent conversion, keeping all block companions.
    int next=4;Block argument=block(inputs,1,next);Proof positive(p,augmented(base,argument,p));
    std::vector<int> mapped;
    for(const auto& line:proof.lines){
        int id=-1;
        if(line.rule=='a'){
            id=line.a<4?positive.mul(positive.ax(line.a),argument.product):positive.ax(line.a);
        }else if(line.rule=='l'){
            id=positive.lc(line.a<0?-1:mapped.at(line.a),line.b<0?-1:mapped.at(line.b),line.ca,line.cb);
        }else id=positive.mv(line.a<0?-1:mapped.at(line.a),line.v);
        need(positive.val(id)==line.value*argument.product,"positive weighted replay");
        mapped.push_back(id);
    }
    int final=mapped.at(current);need(positive.verify() && positive.degree<=5,"positive degree ceiling");
    positive.write(out,"positive_antecedent_PC",final);
    // All old variables and coefficient variables zero: Booleanity holds but a=1.
    std::array<int,NV> model{};Poly a=argument.product;
    need(specialize(a,0,model)==one && specialize(a*a-a,0,model).terms.empty(),"Booleanity-only model");
    for(const auto& f:base)need(specialize(f,0,model).terms.empty(),"model base");
    for(int v=argument.first;v<argument.end;v++){
        auto r=variable(p,v);need(specialize(powp(r,p)-r,0,model).terms.empty(),"model coefficient domain");
    }
    need(specialize(argument.axioms[0],0,model)==one,"direct companion excludes model");
    out<<"{\"record\":\"Booleanity_only_countermodel\",\"all_variables\":0,\"a_value\":1,"
           "\"Booleanity_value\":0,\"first_companion_value\":1}\n";
}
unsigned input_mask(unsigned assignment){
    unsigned x0=assignment&1,x1=(assignment>>1)&1,x2=(assignment>>2)&1,x3=(assignment>>3)&1;
    return (1-x0) | ((x0*(1-x1))<<1) | ((x1*(1-x2))<<2) | ((x2*(1-x3))<<3) | (x3<<4);
}
void binary_constant_audit(std::ostream& out){
    out<<"{\"record\":\"binary_constant_audit\",\"input_order\":[\"g0\",\"g1\",\"g2\",\"g3\",\"g4\"]}\n";
    for(unsigned assignment=0;assignment<16;assignment++)
        out<<"{\"record\":\"input_values\",\"assignment_mask\":"<<assignment<<",\"input_mask\":"<<input_mask(assignment)<<"}\n";
    for(unsigned first=0;first<32;first++)for(unsigned second=0;second<32;second++){
        int witness=-1;
        for(unsigned point=0;point<16;point++){
            unsigned values=input_mask(point);
            if((__builtin_popcount(first&values)%2)==0 && (__builtin_popcount(second&values)%2)==0){
                witness=int(point);break;
            }
        }
        need(witness>=0,"unexpected two-factor constant normalizer");
        out<<"{\"record\":\"two_factor_countermodel\",\"vectors\":["<<first<<','<<second
           <<"],\"assignment_mask\":"<<witness<<"}\n";
    }
    for(unsigned point=0;point<16;point++){
        unsigned values=input_mask(point);
        need((__builtin_popcount(3&values)%2) || (__builtin_popcount(12&values)%2) ||
             (__builtin_popcount(16&values)%2),"three-factor cover");
    }
    for(unsigned value:{1U,4U,16U,5U,17U,20U,21U}){
        bool found=false;for(unsigned point=0;point<16;point++)found|=input_mask(point)==value;
        need(found,"missing nonzero three-cube input pattern");
    }
    out<<"{\"record\":\"constant_audit_passed\",\"rejected_ordered_pairs\":1024,"
           "\"three_factor_vectors\":[3,12,16],\"minimum_constant_accuracy\":3}\n";
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");std::ofstream out(argv[2]);need(bool(out),"open output");
        out<<"{\"schema\":1,\"suite\":\"direct_companion_requests\",\"seed\":null,"
               "\"scope\":\"four-vertex pebbling path, not PHP\"}\n";
        for(int p:{2,3,5,7})field_case(out,p);
        binary_constant_audit(out);
        out<<"{\"record\":\"summary\",\"fields\":4,\"all_passed\":true}\n";
        out.close();need(bool(out),"write output");
        std::cout<<"Four exact NS/PC path controls and all 1024 binary two-factor rejections passed.\n";
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
