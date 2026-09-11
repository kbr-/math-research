// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// MOD comparisons have bounded PC degree but can require every frontier family.
#include "pc_boundary.hpp"
using namespace boundary_pc;

int evaluate(const Poly& value,const std::vector<int>& assignment) {
    int result=0;
    for(const auto& term:value.terms) {
        int c=term.second;
        for(size_t i=0;i<assignment.size();i++)
            c=c*modpow(assignment[i],term.first[i],value.p)%value.p;
        for(size_t i=assignment.size();i<NV;i++) need(!term.first[i],"missing assignment");
        result=(result+c)%value.p;
    }
    return result;
}
Poly replace_one(const Poly& value,int variable_id,const Poly& image) {
    Poly result(value.p);
    for(const auto& term:value.terms) {
        Mon mon=term.first;int e=mon[variable_id];mon[variable_id]=0;
        Poly coefficient(value.p);coefficient.add(mon,term.second);
        result=result+coefficient*powp(image,e);
    }
    return result;
}
void trace(std::ostream& out,const std::string& name,Proof& proof,int final,
           const Poly& target,int ceiling) {
    need(proof.val(final)==target && proof.verify() && proof.degree<=ceiling,name);
    need(final>=0 && !proof.verify(final),"corruption control "+name);
    proof.write(out,name,final);
    out<<"{\"record\":\"verified\",\"name\":\""<<name<<"\",\"actual_degree\":"
       <<proof.degree<<",\"ceiling\":"<<ceiling<<",\"corruption_rejected\":true}\n";
}
void polynomial_case(std::ostream& out,int p,int width) {
    int next=width;Poly one(p,1),u(p),v(p);
    std::vector<Block> left,right;
    for(int side=0;side<2;side++) for(int j=0;j<width;j++) {
        Poly x=variable(p,j);
        Block b=block({x,one-x},1,next);
        if(side==0) {u=u+b.product;left.push_back(b);}
        else {v=v+b.product;right.push_back(b);}
    }
    std::vector<int> sizes(next,p);
    for(int j=0;j<width;j++) sizes[j]=2;
    auto domain=domains(p,sizes),axioms=domain;
    for(const auto& b:left) axioms.insert(axioms.end(),b.axioms.begin(),b.axioms.end());
    for(const auto& b:right) axioms.insert(axioms.end(),b.axioms.begin(),b.axioms.end());
    Proof copy(p,axioms),unit(p,axioms);int copy_sum=-1,unit_sum=-1;
    int base=int(domain.size());
    for(int j=0;j<width;j++) {
        int difference=-1;
        for(int i=0;i<2;i++) {
            difference=copy.lc(difference,copy.mul(copy.ax(base+2*j+i),right[j].coef[i]));
            difference=copy.lc(difference,copy.mul(copy.ax(base+2*width+2*j+i),left[j].coef[i]),1,-1);
        }
        need(copy.val(difference)==left[j].product-right[j].product,"block copy identity");
        copy_sum=copy.lc(copy_sum,difference);
        int lp=unit.lc(unit.ax(base+2*j),unit.ax(base+2*j+1));
        int rp=unit.lc(unit.ax(base+2*width+2*j),unit.ax(base+2*width+2*j+1));
        unit_sum=unit.lc(unit_sum,unit.lc(lp,rp,1,-1));
    }
    need(copy.val(copy_sum)==u-v && unit.val(unit_sum)==u-v,"aggregate difference");
    Poly multiplier(p);
    for(int j=0;j<p-1;j++) multiplier=multiplier+powp(u,p-2-j)*powp(v,j);
    Poly beta=powp(u,p-1),other=powp(v,p-1),target=beta-other;
    int c=copy.mul(copy_sum,multiplier),d=unit.mul(unit_sum,multiplier);
    out<<"{\"record\":\"polynomial_case\",\"p\":"<<p<<",\"width\":"<<width
       <<",\"h\":1,\"variables\":"<<next<<",\"formal_value_degree\":"<<beta.deg()
       <<",\"left_value\":";jsonpoly(out,beta);out<<",\"right_value\":";jsonpoly(out,other);out<<"}\n";
    trace(out,"generic_copy_reuse",copy,c,target,std::max(4,2*(p-1)));
    trace(out,"input_unit_aggregate",unit,d,target,std::max(3,2*(p-1)));
    Proof booleanity(p,domain);Poly hb=beta*beta-beta;
    int b=field_proof(booleanity,hb,sizes);
    trace(out,"domain_only_booleanity",booleanity,b,hb,2*beta.deg());
    if(width==1) {
        int changed=left[0].first;
        Poly image=variable(p,0)*variable(p,changed+1);
        Poly specialized=replace_one(beta,changed,image),hs=specialized*specialized-specialized;
        Proof after(p,domain);int q=field_proof(after,hs,sizes);
        trace(out,"polynomial_substitution_booleanity",after,q,hs,2*specialized.deg());
        for(const auto& line:after.lines)
            need(line.rule!='a' || line.a!=changed,"unused replaced-variable domain was needed");
    }
    for(int side=0;side<2;side++) for(int omitted=0;omitted<width;omitted++) {
        std::vector<int> point(next,0);
        for(int j=0;j<width;j++) point[j]=1;
        for(const auto& b:left) point[b.first]=1;
        for(const auto& b:right) point[b.first]=1;
        point[(side==0?left[omitted]:right[omitted]).first]=0;
        int omitted_start=base+2*(side*width+omitted);
        for(size_t i=0;i<axioms.size();i++)
            if(int(i)!=omitted_start && int(i)!=omitted_start+1)
                need(evaluate(axioms[i],point)==0,"omission model violates retained axiom");
        int value=evaluate(target,point);
        need(value!=0 && evaluate(hb,point)==0,"omission does not separate equality from Booleanity");
        out<<"{\"record\":\"omission_model\",\"side\":"<<side<<",\"block\":"<<omitted
           <<",\"copy_difference\":"<<value<<",\"all_retained_axioms_zero\":true,"
             "\"booleanity_zero\":true,\"assignment\":[";
        for(size_t i=0;i<point.size();i++) {if(i) out<<',';out<<point[i];}
        out<<"]}\n";
    }
}
void wide_controls(std::ostream& out,int p,int width) {
    out<<"{\"record\":\"wide_support\",\"p\":"<<p<<",\"width\":"<<width
       <<",\"model_encoding\":\"all x_j=1; all r_j0=1,r_j1=0 except omitted r_j0=0\","
         "\"omissions\":[";
    for(int omitted=0;omitted<2*width;omitted++) {
        int left_sum=0,right_sum=0;
        for(int j=0;j<2*width;j++) {
            int r0=j==omitted?0:1,product=(1-r0+p)%p;
            if(j!=omitted) need(product==0,"retained companion is nonzero");
            if(j<width) left_sum=(left_sum+product)%p;
            else right_sum=(right_sum+product)%p;
        }
        int a=modpow(left_sum,p-1,p),b=modpow(right_sum,p-1,p);
        need(a!=b && (a*a-a)%p==0 && (b*b-b)%p==0,"wide omission model");
        if(omitted) out<<',';
        out<<"{\"family\":"<<omitted<<",\"left_value\":"<<a<<",\"right_value\":"<<b<<"}";
    }
    out<<"],\"required_original_families\":"<<2*width<<",\"all_passed\":true}\n";
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");
        auto parent=std::filesystem::path(argv[2]).parent_path();
        if(!parent.empty()) std::filesystem::create_directories(parent);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"mod_frontier\",\"seed\":null,"
               "\"scope\":\"exact local PC proofs and original-family support controls\"}\n";
        for(int p:{2,3}) for(int width:{1,2,3}) polynomial_case(out,p,width);
        polynomial_case(out,5,1);
        for(int p:{2,3,5,7}) for(int width:{8,64}) wide_controls(out,p,width);
        out<<"{\"record\":\"summary\",\"polynomial_cases\":7,\"pc_traces\":24,"
               "\"wide_cases\":8,\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failed");
        std::cout<<"Seven polynomial cases, 24 PC traces, and eight wide support controls passed.\n";
    } catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}
}
