// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Stable-ideal affine feasibility, non-common-factor covers, and row controls.
#define ENS_INPUT_REDUCTION_NO_MAIN
#include "check_ens_input_reduction.cpp"

using Dense=std::vector<int>;
using EquationKey=std::pair<int,Mon>;
int mod(int x,int p){x%=p;return x<0?x+p:x;}
void dense_json(std::ostream& out,const Dense& row) {
    out<<'[';bool comma=false;
    for(size_t i=0;i<row.size();i++)if(row[i]) {
        if(comma)out<<',';
        comma=true;out<<'['<<i<<','<<row[i]<<']';
    }
    out<<']';
}
int dot_dense(const Dense& a,const Dense& b,int p) {
    need(a.size()==b.size(),"dot dimension");int s=0;
    for(size_t i=0;i<a.size();i++)s=(s+a[i]*b[i])%p;
    return s;
}
struct SolveResult {bool feasible;Dense coefficients,dual;int dual_value;};
SolveResult solve_columns(const std::vector<Dense>& columns,const Dense& rhs,int p) {
    int m=int(rhs.size()),n=int(columns.size());
    need(m<=5000 && n<=512,"linear-system guard");
    std::vector<Dense> rows(m),witness(m);
    for(int j=0;j<n;j++) {
        Dense a=columns[j],w(n);w[j]=1;
        for(int pivot=0;pivot<m;pivot++)if(a[pivot]) {
            if(rows[pivot].empty()) {
                int inv=modpow(a[pivot],p-2,p);
                for(auto& x:a)x=x*inv%p;
                for(auto& x:w)x=x*inv%p;
                rows[pivot]=a;witness[pivot]=w;break;
            }
            int c=a[pivot];
            for(int k=0;k<m;k++)a[k]=mod(a[k]-c*rows[pivot][k],p);
            for(int k=0;k<n;k++)w[k]=mod(w[k]-c*witness[pivot][k],p);
        }
    }
    auto reduce=[&](Dense a,Dense* coefficients) {
        for(int pivot=0;pivot<m;pivot++)if(a[pivot] && !rows[pivot].empty()) {
            int c=a[pivot];
            for(int k=0;k<m;k++)a[k]=mod(a[k]-c*rows[pivot][k],p);
            if(coefficients)for(int k=0;k<n;k++)
                (*coefficients)[k]=mod((*coefficients)[k]+c*witness[pivot][k],p);
        }
        return a;
    };
    Dense coefficients(n),rem=reduce(rhs,&coefficients);
    int free=-1;for(int i=0;i<m;i++)if(rem[i]){free=i;break;}
    if(free<0) {
        Dense reconstructed(m);
        for(int j=0;j<n;j++)for(int i=0;i<m;i++)
            reconstructed[i]=(reconstructed[i]+coefficients[j]*columns[j][i])%p;
        need(reconstructed==rhs,"primal reconstruction");
        return {true,coefficients,{},0};
    }
    Dense dual(m);
    for(int i=0;i<m;i++){Dense unit(m);unit[i]=1;dual[i]=reduce(unit,nullptr)[free];}
    for(const auto& column:columns)need(dot_dense(dual,column,p)==0,"dual fails a column");
    int value=dot_dense(dual,rhs,p);need(value==rem[free] && value!=0,"dual target value");
    return {false,{},dual,value};
}
struct StableCounts {
    int systems=0,feasible=0,infeasible=0,normalizations=0,ns=0,states=0,source_models=0,row_certificates=0;
};
int stable_ns(std::ostream& out,StableCounts& count,const std::string& name,
              const std::vector<Poly>& ax,const std::vector<Poly>& cof,
              const Poly& target,int degree) {
    int d=ns(out,name,ax,cof,target,degree);count.ns++;return d;
}
struct Normalized {
    Block block;std::vector<Poly> source,beta;Poly H;int variables;
};
Normalized certify(std::ostream& out,StableCounts& count,const std::string& name,
                   const std::vector<Poly>& input,const std::vector<NFRule>& rules,
                   int old_count,int h,const std::vector<Poly>& beta) {
    int p=input[0].p,next=old_count;Poly one(p,1);
    auto J=rule_axioms(rules);Block U=block(input,h,next);
    need(next<=NV && int(beta.size())==next-old_count,"normalizer variable budget");
    for(const auto& b:beta)need(b.old(old_count) && b.deg()<=1,"coefficient image scope");
    auto phi=[&](const Poly& f){return affine_image(f,U,beta);};
    Poly H=phi(U.product);auto source=J;
    for(int v=old_count;v<next;v++)source.push_back(powp(variable(p,v),p)-variable(p,v));
    source.insert(source.end(),U.axioms.begin(),U.axioms.end());
    for(size_t i=0;i<input.size();i++) {
        Poly target=input[i]*H;auto nf=normal_form(target,rules);
        need(nf.value.terms.empty(),"nonzero companion remainder");
        int image_bound=std::max(0,target.deg());
        need(image_bound<=U.axioms[i].deg(),"original companion image budget");
        stable_ns(out,count,name+"_companion_"+std::to_string(i),
                  J,nf.cofactors,target,image_bound);
    }
    for(size_t i=0;i<beta.size();i++) {
        Poly target=powp(beta[i],p)-beta[i];auto nf=normal_form(target,rules);
        need(nf.value.terms.empty(),"nonzero field-image remainder");
        stable_ns(out,count,name+"_field_"+std::to_string(i),J,nf.cofactors,target,p);
    }
    Poly target=H*H-H;auto nf=normal_form(target,rules);
    need(nf.value.terms.empty(),"non-Boolean normalizer");
    stable_ns(out,count,name+"_sharp_H_Booleanity",J,nf.cofactors,target,std::max(0,2*H.deg()));
    out<<"{\"record\":\"normalization\",\"case\":\""<<name<<"\",\"accuracy\":"<<h
       <<",\"coefficient_range\":["<<old_count<<','<<next<<"],\"inputs\":";
    poly_vector(out,input);out<<",\"beta\":";poly_vector(out,beta);out<<",\"H\":";
    jsonpoly(out,H);out<<",\"NF_H\":";jsonpoly(out,normal_form(H,rules).value);out<<"}\n";
    count.normalizations++;return {U,source,beta,H,next};
}
void state(std::ostream& out,StableCounts& count,const std::string& name,
           const std::vector<NFRule>& rules,const std::vector<Poly>& input,
           int old_count,std::array<int,NV> point,const Poly& selector,
           const Normalized* normalizer) {
    models(rule_axioms(rules),point);int expected=1;
    for(const auto& g:input)if(evaluate(g,point))expected=0;
    need(evaluate(selector,point)==expected,"zero-set selector value");
    int variables=old_count;
    if(normalizer) {
        variables=normalizer->variables;
        for(int v=old_count;v<variables;v++)point[v]=evaluate(normalizer->beta[v-old_count],point);
        models(normalizer->source,point);
        need(evaluate(normalizer->H,point)==expected,"normalizer at common model");
        count.source_models++;
    }
    out<<"{\"record\":\"state\",\"case\":\""<<name<<"\",\"source_lift\":"
       <<(normalizer?"true":"false")<<",\"selector\":"<<expected<<",\"point\":";
    point_json(out,point,variables);out<<"}\n";count.states++;
}
std::vector<Poly> affine_system(std::ostream& out,StableCounts& count,const std::string& name,
                               const std::vector<Poly>& input,const std::vector<NFRule>& rules,
                               int old_count,bool expected_feasible) {
    int p=input[0].p,k=int(input.size()),unknowns=k*(old_count+1);
    std::vector<std::vector<Poly>> columns(unknowns);
    std::vector<Poly> rhs;
    std::map<EquationKey,int> keys;
    for(int i=0;i<k;i++) {
        rhs.push_back(normal_form(input[i],rules).value);
        for(const auto& term:rhs.back().terms)keys[{i,term.first}]=0;
    }
    for(int j=0;j<k;j++)for(int v=0;v<=old_count;v++) {
        int u=j*(old_count+1)+v;Poly multiplier=v?variable(p,v-1):Poly(p,1);
        for(int i=0;i<k;i++) {
            columns[u].push_back(normal_form(input[i]*input[j]*multiplier,rules).value);
            for(const auto& term:columns[u].back().terms)keys[{i,term.first}]=0;
        }
    }
    int dimension=0;for(auto& key:keys)key.second=dimension++;
    auto vectorize=[&](const std::vector<Poly>& tuple) {
        Dense value(dimension);
        for(int i=0;i<k;i++)for(const auto& term:tuple[i].terms)
            value[keys.at({i,term.first})]=term.second;
        return value;
    };
    Dense b=vectorize(rhs);std::vector<Dense> A;
    for(const auto& column:columns)A.push_back(vectorize(column));
    SolveResult solution=solve_columns(A,b,p);
    need(solution.feasible==expected_feasible,"unexpected affine feasibility");
    out<<"{\"record\":\"affine_system\",\"case\":\""<<name<<"\",\"p\":"<<p
       <<",\"old_variables\":"<<old_count<<",\"inputs\":";poly_vector(out,input);
    out<<",\"base_axioms\":";poly_vector(out,rule_axioms(rules));
    out<<",\"unknown_order\":\"input index, then constant and old variables\","
          "\"equation_coordinates\":[";
    bool comma=false;
    for(const auto& key:keys) {
        if(comma)out<<',';
        comma=true;Poly mon(p);mon.add(key.first.second,1);
        out<<"{\"input\":"<<key.first.first<<",\"monomial\":";jsonpoly(out,mon);out<<'}';
    }
    out<<"],\"rhs\":";dense_json(out,b);out<<",\"columns\":[";
    for(size_t i=0;i<A.size();i++){if(i)out<<',';dense_json(out,A[i]);}
    out<<"],\"feasible\":"<<(solution.feasible?"true":"false");
    if(solution.feasible) {out<<",\"solution\":";dense_json(out,solution.coefficients);count.feasible++;}
    else {
        out<<",\"dual\":";dense_json(out,solution.dual);
        out<<",\"dual_rhs_value\":"<<solution.dual_value;count.infeasible++;
    }
    out<<"}\n";count.systems++;
    std::vector<Poly> beta;
    if(solution.feasible)for(int j=0;j<k;j++) {
        Poly bpoly(p,solution.coefficients[j*(old_count+1)]);
        for(int v=1;v<=old_count;v++)
            bpoly=bpoly+Poly(p,solution.coefficients[j*(old_count+1)+v])*variable(p,v-1);
        beta.push_back(bpoly);
    }
    return beta;
}
void row_difference_case(std::ostream& out,StableCounts& count,int p,int n) {
    int old_count=2*n;Poly one(p,1),selector=one;
    std::vector<Poly> input;std::vector<NFRule> rules;
    for(int v=0;v<old_count;v++)rules.push_back(domain_rule(p,v,2));
    for(int j=0;j<n;j++) {
        Poly x=variable(p,2*j),y=variable(p,2*j+1);
        Mon pair{};pair[2*j]=pair[2*j+1]=1;rules.push_back({x*y,pair});
        input.push_back(x-y);selector=selector*(one-x-y);
    }
    need(normal_form(selector,rules).value==selector && selector.deg()==n,"selector degree");
    std::string name="row_difference_n"+std::to_string(n)+"_F"+std::to_string(p);
    auto beta=affine_system(out,count,name,input,rules,old_count,n==1 || (p==2 && n==2));
    bool feasible=!beta.empty();
    Normalized norm{Block{Poly(p),{},{},{},0,0},{},{},Poly(p),0};
    if(feasible)norm=certify(out,count,name,input,rules,old_count,1,beta);
    int states=1;for(int j=0;j<n;j++)states*=3;
    for(int code=0;code<states;code++) {
        std::array<int,NV> point{};int q=code;
        for(int j=0;j<n;j++){int s=q%3;q/=3;if(s)point[2*j+s-1]=1;}
        state(out,count,name,rules,input,old_count,point,selector,feasible?&norm:nullptr);
    }
    auto row_base=rule_axioms(rules);Poly row(p,-1),H=one;
    for(int j=0;j<n;j++) {
        Poly x=variable(p,2*j);row=row+x;H=H-x*input[j];
    }
    row_base.push_back(row);
    std::vector<Poly> cof(row_base.size(),Poly(p));cof.back()=Poly(p,-1);
    for(int j=0;j<n;j++){cof[2*j]=Poly(p,-1);cof[old_count+j]=one;}
    stable_ns(out,count,name+"_row_restores_H",row_base,cof,H,2);count.row_certificates++;
    for(int i=0;i<n;i++) {
        auto weighted=cof;for(auto& q:weighted)q=q*input[i];
        stable_ns(out,count,name+"_row_restores_companion_"+std::to_string(i),
                  row_base,weighted,input[i]*H,3);count.row_certificates++;
    }
    if(p==2 && n==4) {
        std::string paired=name+"_two_rows";std::vector<Poly> packed(2*n,Poly(p));
        packed[0]=one;packed[1]=one-input[0];packed[n+2]=one;packed[n+3]=one-input[2];
        auto pair_norm=certify(out,count,paired,input,rules,old_count,2,packed);
        need(normal_form(pair_norm.H,rules).value==selector,"binary sharp row-count control");
        for(int code=0;code<states;code++) {
            std::array<int,NV> point{};int q=code;
            for(int j=0;j<n;j++){int s=q%3;q/=3;if(s)point[2*j+s-1]=1;}
            state(out,count,paired,rules,input,old_count,point,selector,&pair_norm);
        }
    }
}
void field_case(std::ostream& out,StableCounts& count,int p) {
    Poly a=variable(p,0),selector=Poly(p,1)-powp(a,p-1);
    std::vector<Poly> input={a};std::vector<NFRule> rules={domain_rule(p,0,p)};
    std::string name="field_input_F"+std::to_string(p);
    auto beta=affine_system(out,count,name,input,rules,1,p<=3);bool feasible=!beta.empty();
    Normalized norm{Block{Poly(p),{},{},{},0,0},{},{},Poly(p),0};
    if(feasible)norm=certify(out,count,name,input,rules,1,1,beta);
    for(int value=0;value<p;value++) {
        std::array<int,NV> point{};point[0]=value;
        state(out,count,name,rules,input,1,point,selector,feasible?&norm:nullptr);
    }
}
void high_rank_cover(std::ostream& out,StableCounts& count,int p,int m) {
    int old_count=2+2*m;Poly one(p,1),x=variable(p,0),y=variable(p,1);
    Poly b=x+y-x*y;std::vector<Poly> input={b};
    for(int j=0;j<m;j++)input.push_back(x*variable(p,2+j));
    for(int j=0;j<m;j++)input.push_back(y*variable(p,2+m+j));
    std::vector<NFRule> rules;
    for(int v=0;v<old_count;v++)rules.push_back(domain_rule(p,v,2));
    std::vector<Poly> beta(input.size(),Poly(p));beta[0]=one;
    std::string name="noncommon_factor_cover_m"+std::to_string(m)+"_F"+std::to_string(p);
    auto norm=certify(out,count,name,input,rules,old_count,1,beta);
    need(norm.H==(one-x)*(one-y),"non-common-factor selector");
    out<<"{\"record\":\"high_rank_cover\",\"case\":\""<<name
       <<"\",\"literal_rank\":"<<input.size()
       <<",\"gcd_control\":\"x*z_0 and y*w_0 use disjoint variable sets\","
         "\"original_companion_degree\":5,\"image_certificate_ceiling\":4}\n";
    for(int mask=0;mask<(1<<old_count);mask++) {
        std::array<int,NV> point{};for(int v=0;v<old_count;v++)point[v]=(mask>>v)&1;
        state(out,count,name,rules,input,old_count,point,norm.H,&norm);
    }
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","usage: check_stable_ideal_normalizers --out PATH");
        std::string path=argv[2];need(!std::ifstream(path).good(),"refusing to overwrite output");
        std::ofstream out(path);need(out.good(),"cannot open output");StableCounts count;
        out<<"{\"record\":\"schema\",\"version\":1,\"arithmetic\":\"exact prime fields\","
              "\"scope\":\"proper stable ideals; row restoration certificates explicitly labeled\"}\n";
        for(int p:{2,3,5}) {
            for(int n:{1,2,3,4})row_difference_case(out,count,p,n);
            field_case(out,count,p);
            for(int m:{2,3})high_rank_cover(out,count,p,m);
        }
        out<<"{\"record\":\"summary\",\"affine_systems\":"<<count.systems
           <<",\"feasible\":"<<count.feasible<<",\"infeasible\":"<<count.infeasible
           <<",\"normalizations\":"<<count.normalizations<<",\"NS_certificates\":"<<count.ns
           <<",\"row_restoration_certificates\":"<<count.row_certificates
           <<",\"domain_states\":"<<count.states<<",\"source_lifts\":"<<count.source_models<<"}\n";
        out.flush();need(out.good(),"output failure");
        std::cout<<"Passed "<<count.systems<<" affine systems ("<<count.feasible<<" feasible), "
                 <<count.normalizations<<" normalizations, "<<count.ns<<" NS certificates, "
                 <<count.states<<" domain states; output "<<path<<"\n";return 0;
    }catch(const std::exception& e){std::cerr<<"ERROR: "<<e.what()<<"\n";return 1;}
}
