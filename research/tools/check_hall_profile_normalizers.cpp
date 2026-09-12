// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Constructive row/telescoping/collision certificates; no full-ideal solver.
#define ENS_INPUT_REDUCTION_NO_MAIN
#include "check_ens_input_reduction.cpp"

struct HallCounts {int cases=0,certificates=0,companions=0,fields=0,controls=0;};
void hall_ns(std::ostream& out,HallCounts& count,const std::string& name,
             const std::vector<Poly>& ax,const std::vector<Poly>& cof,
             const Poly& target,int ceiling) {
    ns(out,name,ax,cof,target,ceiling);count.certificates++;
}
void hall_case(std::ostream& out,HallCounts& count,int p,int r,int h,int witness_power) {
    constexpr int n=3,m=4,base_variables=12;
    const int u=r-1;const Poly zero(p),one(p,1);
    need(1<=r && r<=n && h>=r && witness_power>=1,"Hall fixture parameters");
    const std::string name="F"+std::to_string(p)+"_r"+std::to_string(r)
                           +"_h"+std::to_string(h)+"_power"+std::to_string(witness_power);
    std::vector<Poly> rows;
    for(int i=0;i<m;i++) {
        Poly row(p,-1);for(int j=0;j<n;j++)row=row+variable(p,i*n+j);rows.push_back(row);
    }
    std::vector<NFRule> rules;
    for(int v=0;v<base_variables;v++)rules.push_back(domain_rule(p,v,2));
    for(int j=0;j<n;j++)for(int i=0;i<m;i++)for(int k=i+1;k<m;k++) {
        Mon mon{};mon[i*n+j]=mon[k*n+j]=1;
        rules.push_back({variable(p,i*n+j)*variable(p,k*n+j),mon});
    }
    auto domain=rule_axioms(rules),base=rows;base.insert(base.end(),domain.begin(),domain.end());
    std::vector<Poly> inputs;
    for(int j=u;j<n;j++) {
        Poly g(p);
        for(int i=0;i<m;i++)
            g=g+Poly(p,1+i%(p-1))*powp(variable(p,i*n+j),witness_power);
        if(witness_power>1)g=g+variable(p,j)*variable(p,n+j);
        inputs.push_back(g);
    }
    Poly extra=variable(p,base_variables);
    if(witness_power>1)extra=extra*(one-variable(p,3*n));
    inputs.push_back(extra);
    const int arity=int(inputs.size());int delta=0;
    for(const auto& g:inputs)delta=std::max(delta,g.deg());
    std::vector<std::vector<Poly>> beta(h,std::vector<Poly>(arity,zero));
    std::vector<Poly> factors,allowed;
    std::vector<std::vector<Poly>> differences;
    const int tau=witness_power+1,W=r*tau;
    for(int a=0;a<r;a++) {
        Poly F=one,R(p);for(int j=0;j<u;j++)R=R+variable(p,a*n+j);
        std::vector<Poly> cof(base.size(),zero);cof[a]=Poly(p,-1);
        for(int j=u;j<n;j++) {
            int index=j-u,lambda=1+a%(p-1),inverse=modpow(lambda,p-2,p);
            Poly cell=variable(p,a*n+j);beta[a][index]=Poly(p,inverse)*cell;
            F=F-beta[a][index]*inputs[index];
            Poly identity=cell*inputs[index]-Poly(p,lambda)*cell;
            auto nf=normal_form(identity,rules);need(nf.value==zero,"occupied-state identity");
            hall_ns(out,count,name+"_cell_"+std::to_string(a)+"_"+std::to_string(j),
                    domain,nf.cofactors,identity,tau);
            for(size_t t=0;t<domain.size();t++)cof[m+t]=cof[m+t]-Poly(p,inverse)*nf.cofactors[t];
        }
        hall_ns(out,count,name+"_row_"+std::to_string(a),base,cof,F-R,tau);
        factors.push_back(F);allowed.push_back(R);differences.push_back(cof);
    }
    Poly H=one,Q=one;for(int a=0;a<r;a++){H=H*factors[a];Q=Q*allowed[a];}
    auto collision=normal_form(Q,rules);need(collision.value==zero,"Hall product survives");
    // This proof must use collision axioms alone, not Booleanity or full PHP.
    for(int v=0;v<base_variables;v++)need(collision.cofactors[v]==zero,"unexpected Boolean cofactor");
    hall_ns(out,count,name+"_collision_finish",domain,collision.cofactors,Q,r);
    std::vector<Poly> Hcof(base.size(),zero);
    for(size_t t=0;t<domain.size();t++)Hcof[m+t]=collision.cofactors[t];
    for(int a=0;a<r;a++) {
        Poly multiplier=one;
        for(int b=0;b<a;b++)multiplier=multiplier*factors[b];
        for(int b=a+1;b<r;b++)multiplier=multiplier*allowed[b];
        for(size_t t=0;t<base.size();t++)Hcof[t]=Hcof[t]+multiplier*differences[a][t];
    }
    hall_ns(out,count,name+"_product_zero",base,Hcof,H,W);
    std::vector<int> companion_degrees;
    for(int i=0;i<arity;i++) {
        auto cof=Hcof;for(auto& term:cof)term=term*inputs[i];
        int original=inputs[i].deg()+h*(delta+1);
        need(inputs[i].deg()+W<=original,"original companion budget");
        hall_ns(out,count,name+"_companion_"+std::to_string(i),base,cof,inputs[i]*H,
                inputs[i].deg()+W);companion_degrees.push_back(original);count.companions++;
    }
    for(int a=0;a<h;a++)for(int i=0;i<arity;i++) {
        Poly field=powp(beta[a][i],p)-beta[a][i];auto nf=normal_form(field,rules);
        need(nf.value==zero,"coefficient field image");
        if(field.deg()>=0)hall_ns(out,count,name+"_field_"+std::to_string(a)+"_"+std::to_string(i),
                                domain,nf.cofactors,field,p);
        out<<"{\"record\":\"field_image\",\"case\":\""<<name<<"\",\"row\":"<<a
           <<",\"input\":"<<i<<",\"original_degree\":"<<p<<",\"image\":";
        jsonpoly(out,field);out<<",\"verified\":true}\n";count.fields++;
    }
    out<<"{\"record\":\"normalizer\",\"case\":\""<<name<<"\",\"holes\":3,\"rows\":4,"
         "\"selected_rows\":\"0 through r-1\",\"common_zero_columns\":\"0 through r-2\","
         "\"r\":"<<r<<",\"accuracy\":"<<h<<",\"witness_degree\":"<<witness_power
       <<",\"product_certificate_ceiling\":"<<W<<",\"extra_variable\":12,\"inputs\":";
    poly_vector(out,inputs);out<<",\"coefficient_rows\":[";
    for(int a=0;a<h;a++){if(a)out<<',';poly_vector(out,beta[a]);}
    out<<"],\"factors\":";poly_vector(out,factors);out<<",\"allowed_row_sums\":";
    poly_vector(out,allowed);out<<",\"product_image\":";jsonpoly(out,H);
    out<<",\"original_companion_degrees\":[";
    for(size_t i=0;i<companion_degrees.size();i++){if(i)out<<',';out<<companion_degrees[i];}
    out<<"],\"source_product\":\"product_a(1-sum_i r_a_i*g_i)\",\"verified\":true}\n";

    // Delete the final selected row equation: all remaining selected rows fit U.
    std::array<int,NV> point{};point[base_variables]=1;
    for(int a=0;a<r-1;a++)point[a*n+a]=1;
    models(domain,point);
    for(int a=0;a<r-1;a++)need(evaluate(rows[a],point)==0,"row-omission control");
    need(evaluate(rows[r-1],point)==p-1 && evaluate(H,point)==1
         && evaluate(extra*H,point)==1,"missing-row witness does not separate");
    out<<"{\"record\":\"row_omission_control\",\"case\":\""<<name
       <<"\",\"omitted_selected_row\":"<<r-1<<",\"point\":";
    point_json(out,point,base_variables+1);
    out<<",\"model_scope\":\"column domains and selected rows except the omitted one\","
         "\"product_value\":1,\"extra_companion_value\":1}\n";count.controls++;

    // Enlarge U by one column: the collision-only finish now has a matching monomial.
    Poly enlarged=one;std::array<int,NV> matching{};
    for(int a=0;a<r;a++) {
        Poly sum(p);for(int j=0;j<r;j++)sum=sum+variable(p,a*n+j);
        enlarged=enlarged*sum;matching[a*n+a]=1;
    }
    auto survives=normal_form(enlarged,rules);
    need(survives.value.deg()==r && evaluate(enlarged,matching)==1,"matching product control");
    models(domain,matching);for(int a=0;a<r;a++)need(evaluate(rows[a],matching)==0,"selected row model");
    out<<"{\"record\":\"matching_control\",\"case\":\""<<name<<"\",\"enlarged_zero_columns\":"<<r
       <<",\"product\":";jsonpoly(out,enlarged);out<<",\"proper_normal_form\":";
    jsonpoly(out,survives.value);out<<",\"point\":";point_json(out,matching,base_variables);
    out<<",\"model_scope\":\"column domains and selected rows only\",\"product_value\":1}\n";
    count.controls++;count.cases++;
}

int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","usage: check_hall_profile_normalizers --out NEW-PATH.jsonl");
        std::filesystem::path path(argv[2]);need(!std::filesystem::exists(path),"output already exists");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot open output");HallCounts count;
        hall_case(out,count,2,3,3,1);
        hall_case(out,count,3,2,2,2);
        hall_case(out,count,5,1,2,1);
        out<<"{\"record\":\"summary\",\"cases\":"<<count.cases<<",\"NS_certificates\":"<<count.certificates
           <<",\"companions\":"<<count.companions<<",\"fields\":"<<count.fields
           <<",\"controls\":"<<count.controls<<",\"verified\":true}\n";
        out.close();need(bool(out),"failed writing output");
        std::cout<<"Verified "<<count.certificates<<" NS certificates, "<<count.companions
                 <<" companion images, "<<count.fields<<" field images, and "<<count.controls<<" controls.\n";
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
