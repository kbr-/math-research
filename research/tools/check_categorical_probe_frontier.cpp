// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Higher-alphabet column sharing and encoding-sensitive degree controls.
#define STABLE_IDEAL_NORMALIZERS_NO_MAIN
#include "check_stable_ideal_normalizers.cpp"

struct CategoricalCounts {int encoded=0,native=0,ns=0,states=0;};
int categorical_ns(std::ostream& out,CategoricalCounts& count,const std::string& name,
                   const std::vector<Poly>& ax,const std::vector<Poly>& cof,
                   const Poly& target,int bound) {
    int d=ns(out,name,ax,cof,target,bound);count.ns++;return d;
}
void image_case(std::ostream& out,CategoricalCounts& count,const std::string& name,
                int p,int old_count,int h,int T,const std::vector<Poly>& input,
                const std::vector<NFRule>& rules,const std::vector<Poly>& beta,
                const Poly& selector,const std::vector<std::array<int,NV>>& points) {
    const int n=int(input.size()),original_e=2*h+1;Poly one(p,1),H=one;
    need(int(beta.size())==h*n && old_count<=NV,"image case dimensions");
    for(const auto& g:input)need(g.old(old_count) && g.deg()==1,"probe must be nonconstant affine");
    for(const auto& b:beta)need(b.old(old_count) && b.deg()<=T,"coefficient degree or scope");
    for(int row=0;row<h;row++) {
        Poly factor=one;
        for(int i=0;i<n;i++)factor=factor-beta[row*n+i]*input[i];
        H=H*factor;
    }
    auto J=rule_axioms(rules);
    auto difference=normal_form(H-selector,rules);
    need(difference.value.terms.empty(),"wrong selector remainder");
    categorical_ns(out,count,name+"_selector_identity",J,difference.cofactors,
                   H-selector,std::max(H.deg(),selector.deg()));
    for(int i=0;i<n;i++) {
        Poly target=input[i]*H;auto nf=normal_form(target,rules);
        need(nf.value.terms.empty(),"nonzero companion remainder");
        int bound=std::max(0,target.deg());
        need(bound<=1+h*(T+1) && bound<=std::max(1,T)*original_e,"original companion image budget");
        categorical_ns(out,count,name+"_companion_"+std::to_string(i),
                       J,nf.cofactors,target,bound);
    }
    for(size_t i=0;i<beta.size();i++) {
        Poly target=powp(beta[i],p)-beta[i];auto nf=normal_form(target,rules);
        need(nf.value.terms.empty(),"coefficient field remainder");
        categorical_ns(out,count,name+"_field_"+std::to_string(i),
                       J,nf.cofactors,target,p*std::max(1,T));
    }
    out<<"{\"record\":\"case\",\"name\":\""<<name<<"\",\"p\":"<<p
       <<",\"old_variables\":"<<old_count<<",\"source_coefficient_count\":"<<beta.size()
       <<",\"accuracy\":"<<h<<",\"coefficient_degree_bound\":"<<T
       <<",\"original_companion_degree\":"<<original_e<<",\"inputs\":";
    poly_vector(out,input);out<<",\"coefficient_images\":";poly_vector(out,beta);
    out<<",\"H\":";jsonpoly(out,H);out<<",\"selector\":";jsonpoly(out,selector);
    out<<",\"H_degree\":"<<H.deg()<<",\"selector_degree\":"<<selector.deg()
       <<",\"Booleanity_scope\":\"follows from the proved proper-ideal theorem; no expanded H^2-H certificate emitted\"}\n";
    for(const auto& point:points) {
        models(J,point);int expected=1;
        std::vector<int> g(n),coefficient(beta.size());
        for(int i=0;i<n;i++){g[i]=evaluate(input[i],point);if(g[i])expected=0;}
        for(size_t i=0;i<beta.size();i++) {
            coefficient[i]=evaluate(beta[i],point);
            need(modpow(coefficient[i],p,p)==coefficient[i],"source coefficient field model");
        }
        int product=1;
        for(int row=0;row<h;row++) {
            int factor=1;
            for(int i=0;i<n;i++)factor=mod(factor-coefficient[row*n+i]*g[i],p);
            product=product*factor%p;
        }
        for(int value:g)need(value*product%p==0,"source companion model");
        need(product==expected && evaluate(H,point)==expected && evaluate(selector,point)==expected,
             "selector/source model mismatch");
        out<<"{\"record\":\"source_model\",\"case\":\""<<name<<"\",\"old_point\":";
        point_json(out,point,old_count);out<<",\"coefficient_values\":[";
        for(size_t i=0;i<coefficient.size();i++){if(i)out<<',';out<<coefficient[i];}
        out<<"],\"H\":"<<expected<<"}\n";count.states++;
    }
}
void encoded_case(std::ostream& out,CategoricalCounts& count,int p,
                  const std::vector<int>& labels,int n,int T) {
    int k=int(labels.size()),old_count=k*n,h=(k*n+k*T)/(k*T+1);
    need(k>0 && old_count<=NV,"encoded case size");
    std::vector<NFRule> rules;
    for(int v=0;v<old_count;v++)rules.push_back(domain_rule(p,v,2));
    std::vector<Poly> g,q,inverse;
    Poly one(p,1),selector=one;
    for(int j=0;j<n;j++) {
        Poly value(p),empty=one,inv(p);
        for(int a=0;a<k;a++) {
            need(labels[a]>0 && labels[a]<p,"nonzero field label");
            for(int b=0;b<a;b++)need(labels[b]!=labels[a],"duplicate label");
            Poly x=variable(p,j*k+a);
            value=value+Poly(p,labels[a])*x;empty=empty-x;
            inv=inv+Poly(p,modpow(labels[a],p-2,p))*x;
            for(int b=0;b<a;b++) {
                Mon pair{};pair[j*k+a]=pair[j*k+b]=1;
                rules.push_back({x*variable(p,j*k+b),pair});
            }
        }
        g.push_back(value);q.push_back(empty);inverse.push_back(inv);selector=selector*empty;
    }
    std::vector<Poly> beta(h*n,Poly(p));int next_column=0,row=0;
    auto fill_side=[&](int current_row) {
        Poly prefix=one;
        for(int used=0;used<T && next_column<n;used++) {
            int j=next_column++;
            beta[current_row*n+j]=inverse[j]*prefix;prefix=prefix*q[j];
        }
        return prefix;
    };
    for(int group=0;group<h/k;group++) {
        if(next_column>=n){row+=k;continue;}
        int central=next_column++;
        for(int a=0;a<k;a++,row++) {
            Poly mask=fill_side(row);
            beta[row*n+central]=Poly(p,modpow(labels[a],p-2,p))*mask;
        }
    }
    while(row<h){fill_side(row);row++;}
    need(next_column==n,"capacity allocation failed");
    int number=1;for(int j=0;j<n;j++)number*=k+1;
    std::vector<std::array<int,NV>> points;
    for(int code=0;code<number;code++) {
        std::array<int,NV> point{};int c=code;
        for(int j=0;j<n;j++){int state=c%(k+1);c/=k+1;if(state)point[j*k+state-1]=1;}
        points.push_back(point);
    }
    std::string name="encoded_k"+std::to_string(k)+"_n"+std::to_string(n)
                     +"_T"+std::to_string(T)+"_F"+std::to_string(p);
    image_case(out,count,name,p,old_count,h,T,g,rules,beta,selector,points);count.encoded++;
}
void native_field_case(std::ostream& out,CategoricalCounts& count) {
    const int p=5;Poly one(p,1),s=variable(p,0);
    std::vector<Poly> input={s},beta={s,Poly(p,4)*s};
    std::vector<NFRule> rules={domain_rule(p,0,p)};
    std::vector<std::array<int,NV>> points;
    for(int a=0;a<p;a++){std::array<int,NV> point{};point[0]=a;points.push_back(point);}
    image_case(out,count,"native_field_F5",p,1,2,1,input,rules,beta,one-powp(s,4),points);
    count.native++;
}
void mixed_alphabet_case(std::ostream& out,CategoricalCounts& count) {
    const int p=5,old_count=10,n=4,h=2;Poly one(p,1),selector=one;
    std::vector<std::vector<int>> groups={{0},{1},{2,3,4,5},{6,7,8,9}};
    std::vector<NFRule> rules;
    for(int v=0;v<old_count;v++)rules.push_back(domain_rule(p,v,2));
    std::vector<Poly> g,q,inverse;
    for(const auto& group:groups) {
        Poly value(p),empty=one,inv(p);
        for(size_t a=0;a<group.size();a++) {
            int label=int(a)+1;Poly x=variable(p,group[a]);
            value=value+Poly(p,label)*x;empty=empty-x;
            inv=inv+Poly(p,modpow(label,p-2,p))*x;
            for(size_t b=0;b<a;b++) {
                Mon pair{};pair[group[a]]=pair[group[b]]=1;
                rules.push_back({x*variable(p,group[b]),pair});
            }
        }
        g.push_back(value);q.push_back(empty);inverse.push_back(inv);selector=selector*empty;
    }
    std::vector<Poly> beta(h*n,Poly(p));
    beta[0]=q[2];beta[2]=inverse[2];
    beta[n+1]=q[3];beta[n+3]=inverse[3];
    std::vector<std::array<int,NV>> points;
    for(int code=0;code<100;code++) {
        std::array<int,NV> point{};int c=code;
        for(const auto& group:groups) {
            int radix=int(group.size())+1,s=c%radix;c/=radix;
            if(s)point[group[s-1]]=1;
        }
        points.push_back(point);
    }
    out<<"{\"record\":\"heterogeneous_budget\",\"alphabet_sizes\":[1,1,4,4],"
          "\"coefficient_degree\":1,\"accuracy\":2,\"required_centers\":2,"
          "\"selected_center_cost\":2,\"excluded_accuracy_one_center_cost\":6}\n";
    image_case(out,count,"mixed_alphabets_1_1_4_4_F5",p,old_count,h,1,g,rules,beta,selector,points);
    count.encoded++;
}
int main(int argc,char** argv) {
    try {
        bool mixed_only=argc==4 && std::string(argv[3])=="--mixed-only";
        need((argc==3 || mixed_only) && std::string(argv[1])=="--out",
             "usage: check_categorical_probe_frontier --out PATH [--mixed-only]");
        std::string path=argv[2];need(!std::ifstream(path).good(),"refusing to overwrite output");
        std::ofstream out(path);need(out.good(),"cannot open output");CategoricalCounts count;
        out<<"{\"record\":\"schema\",\"version\":1,\"arithmetic\":\"exact prime fields\","
              "\"scope\":\"proper categorical column ideals and an explicit native field control\","
              "\"models\":\"old point followed by separately stored source coefficient values\"}\n";
        if(mixed_only)mixed_alphabet_case(out,count);
        else {
            encoded_case(out,count,5,{1,2,3},4,1);
            encoded_case(out,count,5,{1,2,3,4},1,1);
            native_field_case(out,count);
        }
        out<<"{\"record\":\"summary\",\"encoded_cases\":"<<count.encoded
           <<",\"native_cases\":"<<count.native<<",\"NS_certificates\":"<<count.ns
           <<",\"complete_source_models\":"<<count.states
           <<",\"expanded_product_Booleanity_tests\":0}\n";
        out.flush();need(out.good(),"output failure");
        std::cout<<"Passed "<<count.encoded<<" encoded cases, "<<count.native<<" native-field case, "
                 <<count.ns<<" NS certificates, "<<count.states<<" complete source models; output "
                 <<path<<"\n";return 0;
    }catch(const std::exception& e){std::cerr<<"ERROR: "<<e.what()<<"\n";return 1;}
}
