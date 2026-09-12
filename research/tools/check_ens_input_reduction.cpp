// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact stable-ideal input replacement and reduced-product Booleanity gaps.
#define main small_probe_unused_main
#include "check_small_probe_normalizers.cpp"
#undef main

struct NFRule {Poly axiom;Mon leading;};
struct NFResult {Poly value;std::vector<Poly> cofactors;};
NFResult normal_form(const Poly& f,const std::vector<NFRule>& rules) {
    Poly rem=f;std::vector<Poly> cof(rules.size(),Poly(f.p));
    while(true) {
        bool found=false;Mon quotient{};int coefficient=0,index=-1;
        for(const auto& term:rem.terms) {
            for(size_t i=0;i<rules.size();i++) {
                bool divides=true;Mon q=term.first;
                for(int v=0;v<NV;v++)
                    if(q[v]<rules[i].leading[v]){divides=false;break;}
                if(!divides)continue;
                for(int v=0;v<NV;v++)q[v]-=rules[i].leading[v];
                quotient=q;coefficient=term.second;index=int(i);found=true;break;
            }
            if(found)break;
        }
        if(!found)break;
        Poly q(f.p);q.add(quotient,coefficient);
        cof[index]=cof[index]+q;rem=rem-q*rules[index].axiom;
    }
    return {rem,cof};
}
NFRule domain_rule(int p,int v,int exponent) {
    Mon lead{};lead[v]=exponent;
    return {powp(variable(p,v),exponent)-variable(p,v),lead};
}
std::vector<Poly> rule_axioms(const std::vector<NFRule>& rules) {
    std::vector<Poly> out;for(const auto& r:rules)out.push_back(r.axiom);return out;
}
struct ReductionCounts {int replacements=0,gaps=0,ns=0,traces=0,lower_checks=0,models=0,controls=0;};
int reduction_ns(std::ostream& out,ReductionCounts& count,const std::string& name,
                 const std::vector<Poly>& ax,const std::vector<Poly>& cof,
                 const Poly& target,int ceiling) {
    int d=ns(out,name,ax,cof,target,ceiling);count.ns++;return d;
}
Poly old_ones(const Poly& f,int t) {
    Poly out(f.p);
    for(const auto& term:f.terms) {
        Mon mon=term.first;for(int v=0;v<t;v++)mon[v]=0;
        out.add(mon,term.second);
    }
    return out;
}
void gap_case(std::ostream& out,ReductionCounts& count,int p,int t,int h) {
    Poly one(p,1),g=one;std::vector<NFRule> bool_rules;
    for(int v=0;v<t;v++){g=g*variable(p,v);bool_rules.push_back(domain_rule(p,v,2));}
    int next=t;Block U=block({g},h,next);
    auto boolean=rule_axioms(bool_rules);
    auto source=boolean;std::vector<NFRule> field_rules;
    Poly scalar=one;
    for(int v=t;v<next;v++) {
        field_rules.push_back(domain_rule(p,v,p));
        source.push_back(field_rules.back().axiom);scalar=scalar*(one-variable(p,v));
    }
    const int companion=int(source.size());source.push_back(U.axioms[0]);
    Poly K=one-scalar,V=one-K*g,target=V*V-V;
    auto reduced=normal_form(U.product,bool_rules);
    need(reduced.value==V,"reduced-product formula");
    const int e=(h+1)*t+h,ns_min=e+h,pc_min=std::max(e,2*(h+t));
    need(U.axioms[0].deg()==e && V.deg()==h+t,"gap ordinary-degree accounting");
    std::string name="gap_t"+std::to_string(t)+"_h"+std::to_string(h)+"_F"+std::to_string(p);
    reduction_ns(out,count,name+"_product_reduction",boolean,reduced.cofactors,
                 U.product-V,U.product.deg());
    std::vector<Poly> gv_cof(source.size(),Poly(p));gv_cof[companion]=one;
    for(int v=0;v<t;v++)gv_cof[v]=Poly(p,-1)*g*reduced.cofactors[v];
    reduction_ns(out,count,name+"_gV",source,gv_cof,g*V,e);
    auto Hcof=gv_cof;for(auto& q:Hcof)q=Poly(p,-1)*K*q;
    need(reduction_ns(out,count,name+"_Booleanity_NS",source,Hcof,target,ns_min)==ns_min,
         "NS upper bound is not tight in the explicit certificate");
    Proof pc(p,source);int gv=pc.ax(companion);
    for(int v=0;v<t;v++)if(!gv_cof[v].terms.empty())
        gv=pc.lc(gv,pc.mul(pc.ax(v),gv_cof[v]));
    need(pc.val(gv)==g*V,"completed gV proof");
    int final=pc.mul(gv,Poly(p,-1)*K);
    trace(out,pc,name+"_Booleanity_PC",final,target,pc_min);
    need(pc.degree==pc_min,"PC upper degree");count.traces++;
    Poly specialized=old_ones(target,t);
    Poly target_nf=normal_form(specialized,field_rules).value;
    Mon top{};for(int v=t;v<next;v++)top[v]=2;
    need(target_nf.terms.count(top) && target_nf.terms.at(top)==1,"lower functional target");
    int local_checks=0;
    auto enumerate=[&](auto&& self,int v,int remaining,Mon mon)->void {
        if(v==next) {
            Poly q(p);q.add(mon,1);Poly value=normal_form(q*scalar,field_rules).value;
            need(!value.terms.count(top),"lower functional fails an eligible companion multiple");
            out<<"{\"record\":\"NS_lower_companion_check\",\"case\":\""<<name
               <<"\",\"cofactor\":";jsonpoly(out,q);out<<",\"functional_value\":0}\n";
            local_checks++;count.lower_checks++;return;
        }
        for(int a=0;a<=remaining;a++){mon[v]=a;self(self,v+1,remaining-a,mon);}
    };
    enumerate(enumerate,t,h-1,Mon{});
    out<<"{\"record\":\"gap\",\"case\":\""<<name<<"\",\"p\":"<<p<<",\"monomial_degree\":"<<t
       <<",\"accuracy\":"<<h<<",\"original_companion_degree\":"<<e
       <<",\"reduced_value_degree\":"<<V.deg()<<",\"NS_minimum\":"<<ns_min
       <<",\"PC_minimum\":"<<pc_min<<",\"V\":";jsonpoly(out,V);
    out<<",\"lower_functional\":\"set old variables to one, reduce coefficient fields, extract product r_u^2\","
          "\"lower_ceiling\":"<<ns_min-1<<",\"target_value\":1,\"eligible_R_monomials\":"
       <<local_checks<<"}\n";
    std::array<int,NV> missing{};for(int v=0;v<t;v++)missing[v]=1;missing[t]=p-1;
    std::vector<Poly> domain_only=source;domain_only.pop_back();models(domain_only,missing);
    need(evaluate(target,missing)==2%p,"missing-companion control");
    out<<"{\"record\":\"missing_companion_control\",\"case\":\""<<name
       <<"\",\"target_value\":"<<evaluate(target,missing)<<",\"point\":";
    point_json(out,missing,next);out<<"}\n";count.controls++;
    for(bool occupied:{false,true}) {
        std::array<int,NV> point{};
        if(occupied){for(int v=0;v<t;v++)point[v]=1;point[t]=1;}
        models(source,point);need(evaluate(target,point)==0,"gap source model");
        out<<"{\"record\":\"source_model\",\"case\":\""<<name<<"\",\"point\":";
        point_json(out,point,next);out<<"}\n";count.models++;
    }
    count.gaps++;
}

void replacement_case(std::ostream& out,ReductionCounts& count,int p,int h) {
    Poly one(p,1),x=variable(p,0),y=variable(p,1),z=variable(p,2),a=variable(p,3);
    std::vector<NFRule> rules;
    for(int v=0;v<3;v++)rules.push_back(domain_rule(p,v,2));
    rules.push_back(domain_rule(p,3,p));
    Mon pair{};pair[0]=pair[1]=1;rules.push_back({x*y,pair});
    auto J=rule_axioms(rules);
    std::vector<Poly> input={x*x+x*y,(powp(a,p)-a)*z+y*y,z*z*z+x*y};
    std::vector<Poly> normal={x,y,z};
    std::string name="replacement_h"+std::to_string(h)+"_F"+std::to_string(p);
    for(size_t i=0;i<input.size();i++) {
        auto nf=normal_form(input[i],rules);need(nf.value==normal[i],"input normal form");
        reduction_ns(out,count,name+"_input_"+std::to_string(i),J,nf.cofactors,
                     input[i]-normal[i],input[i].deg());
    }
    int next=4,next_new=4;Block old=block(input,h,next),fresh=block(normal,h,next_new);
    need(next==next_new,"coefficient variables must be unchanged");
    auto difference=normal_form(old.product-fresh.product,rules);
    need(difference.value.terms.empty(),"product difference remainder");
    reduction_ns(out,count,name+"_product_difference",J,difference.cofactors,
                 old.product-fresh.product,old.product.deg());
    auto source=J,destination=J;int selected_field=int(J.size());
    for(int v=4;v<next;v++) {
        Poly field=powp(variable(p,v),p)-variable(p,v);
        source.push_back(field);destination.push_back(field);
    }
    int start=int(source.size());
    source.insert(source.end(),old.axioms.begin(),old.axioms.end());
    destination.insert(destination.end(),fresh.axioms.begin(),fresh.axioms.end());
    std::vector<std::vector<Poly>> image(source.size(),std::vector<Poly>(destination.size(),Poly(p)));
    for(size_t i=0;i<source.size();i++)image[i][i]=one;
    for(size_t i=0;i<input.size();i++) {
        auto nf=normal_form(old.axioms[i]-fresh.axioms[i],rules);
        need(nf.value.terms.empty(),"companion difference remainder");
        for(size_t j=0;j<J.size();j++)image[start+i][j]=nf.cofactors[j];
        reduction_ns(out,count,name+"_old_companion_from_new_"+std::to_string(i),
                     destination,image[start+i],old.axioms[i],old.axioms[i].deg());
    }
    Poly target=old.product*old.product-old.product+source[selected_field];
    std::vector<Poly> cof(source.size(),Poly(p));cof[selected_field]=one;
    for(size_t i=0;i<input.size();i++)cof[start+i]=Poly(p,-1)*old.coef[i];
    int ceiling=std::max(p,2*old.product.deg());
    int old_degree=reduction_ns(out,count,name+"_original_consequence",source,cof,target,ceiling);
    std::vector<Poly> replay(destination.size(),Poly(p));
    for(size_t i=0;i<source.size();i++)if(!cof[i].terms.empty())
        for(size_t j=0;j<destination.size();j++)replay[j]=replay[j]+cof[i]*image[i][j];
    int new_degree=reduction_ns(out,count,name+"_unchanged_target_replay",
                                destination,replay,target,ceiling);
    need(!target.terms.empty(),"replacement target is vacuous");
    out<<"{\"record\":\"replacement\",\"case\":\""<<name<<"\",\"p\":"<<p
       <<",\"accuracy\":"<<h<<",\"old_inputs\":";poly_vector(out,input);
    out<<",\"new_inputs\":";poly_vector(out,normal);
    out<<",\"old_product_degree\":"<<old.product.deg()
       <<",\"new_product_degree\":"<<fresh.product.deg()
       <<",\"original_certificate_degree\":"<<old_degree
       <<",\"replayed_certificate_degree\":"<<new_degree<<"}\n";
    for(int state=0;state<3;state++)for(int zvalue=0;zvalue<2;zvalue++)
        for(int avalue=0;avalue<p;avalue++) {
            std::array<int,NV> point{};
            if(state)point[state-1]=1;
            point[2]=zvalue;point[3]=avalue;
            for(int i=0;i<3;i++)if(evaluate(normal[i],point)){point[4+i]=1;break;}
            models(source,point);models(destination,point);need(evaluate(target,point)==0,"replacement model");
            out<<"{\"record\":\"common_model\",\"case\":\""<<name<<"\",\"point\":";
            point_json(out,point,next);out<<"}\n";count.models++;
        }
    count.replacements++;
}
#ifndef ENS_INPUT_REDUCTION_NO_MAIN
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","usage: check_ens_input_reduction --out PATH");
        std::string path=argv[2];need(!std::ifstream(path).good(),"refusing to overwrite output");
        std::ofstream out(path);need(out.good(),"cannot open output");ReductionCounts count;
        out<<"{\"record\":\"schema\",\"version\":1,\"arithmetic\":\"exact prime fields\","
              "\"scope\":\"consistent domain and column subsystems, not full PHP\"}\n";
        for(int p:{2,3,5})for(int h:{1,2})replacement_case(out,count,p,h);
        for(int p:{3,5})for(int t:{1,2})for(int h:{1,2,3})gap_case(out,count,p,t,h);
        out<<"{\"record\":\"summary\",\"replacement_cases\":"<<count.replacements
           <<",\"gap_cases\":"<<count.gaps<<",\"NS_certificates\":"<<count.ns
           <<",\"PC_traces\":"<<count.traces<<",\"lower_companion_checks\":"<<count.lower_checks
           <<",\"model_controls\":"<<count.models<<",\"missing_companion_controls\":"<<count.controls<<"}\n";
        out.flush();need(out.good(),"output failure");
        std::cout<<"Passed "<<count.replacements<<" replacements, "<<count.gaps<<" exact gap cases, "
                 <<count.ns<<" NS certificates, "<<count.traces<<" PC traces, "
                 <<count.lower_checks<<" lower-bound checks; output "<<path<<"\n";return 0;
    }catch(const std::exception& e){std::cerr<<"ERROR: "<<e.what()<<"\n";return 1;}
}
#endif
