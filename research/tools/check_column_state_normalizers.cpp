// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact affine column-state normalizers, NS replay, and omitted-collision controls.
#define AFFINE_BASIS_PACKING_NO_MAIN
#include "check_affine_basis_packing.cpp"

struct ColumnCounts {
    int cases=0,certificates=0,models=0,controls=0,nonzero_fields=0,nonboolean_states=0;
};

Reduction reduce_column(const Poly& input,int column_size,int old_count,
                        const std::vector<Poly>& base) {
    need(input.old(old_count),"column reduction contains fresh variables");
    Poly rem=input;std::vector<Poly> cof(base.size(),Poly(input.p));
    while(true) {
        bool found=false;Mon mon{};int coefficient=0,index=-1;
        for(const auto& term:rem.terms) {
            int pair_index=old_count;
            for(int i=0;i<column_size && !found;i++)
                for(int j=i+1;j<column_size;j++,pair_index++)
                    if(term.first[i] && term.first[j]) {
                        mon=term.first;mon[i]--;mon[j]--;
                        index=pair_index;coefficient=term.second;found=true;break;
                    }
            if(!found)for(int i=0;i<old_count;i++)if(term.first[i]>=2) {
                mon=term.first;mon[i]-=2;index=i;
                coefficient=term.second;found=true;break;
            }
            if(found)break;
        }
        if(!found)break;
        Poly q(input.p);q.add(mon,coefficient);
        cof[index]=cof[index]+q;rem=rem-q*base[index];
    }
    return {cof,rem};
}

int column_ns(std::ostream& out,ColumnCounts& counts,const std::string& label,
              const std::vector<Poly>& ax,const std::vector<Poly>& cof,
              const Poly& target,int bound) {
    int degree=ns(out,label,ax,cof,target,bound);counts.certificates++;return degree;
}

void column_case(std::ostream& out,ColumnCounts& counts,int p,int m,char kind) {
    const int old_count=m+(kind=='C');Poly one(p,1);
    std::vector<Poly> y;for(int i=0;i<m;i++)y.push_back(variable(p,i));
    std::vector<Poly> input;
    if(kind=='A')input={y[0]+Poly(p,2)*y[1],y[1]+y[2]};
    if(kind=='B')input={y[0]*y[0]+y[1]*y[2],(one-y[0])*y[2],
                       powp(y[1],3)-y[1]};
    if(kind=='C')input={one-y[0],one-y[1],variable(p,m)};
    if(kind=='D')input={y[0]*y[0]-y[0],y[0]*y[1],powp(y[1],3)-y[1]};
    const int k=int(input.size()),eligible=kind=='C'?2:k;
    int delta=0;for(const auto& g:input)delta=std::max(delta,g.deg());
    std::string name=std::string(1,kind)+"_m"+std::to_string(m)+"_F"+std::to_string(p);
    auto base=domains(p,std::vector<int>(old_count,2));
    for(int i=0;i<m;i++)for(int j=i+1;j<m;j++)base.push_back(y[i]*y[j]);
    std::vector<Poly> indicators;Poly empty=one;
    for(const auto& yi:y)empty=empty-yi;
    indicators.push_back(empty);indicators.insert(indicators.end(),y.begin(),y.end());
    std::vector<Poly> beta(k,Poly(p));
    out<<"{\"record\":\"case_start\",\"name\":\""<<name<<"\",\"p\":"<<p
       <<",\"column_size\":"<<m<<",\"old_variables\":"<<old_count
       <<",\"accuracy\":1,\"delta\":"<<delta<<",\"eligible_inputs\":"<<eligible
       <<",\"inputs\":";poly_vector(out,input);
    out<<",\"base_axioms\":";poly_vector(out,base);out<<"}\n";
    bool inconsistent=true;
    for(int s=0;s<=m;s++) {
        std::array<int,NV> point{};if(s)point[s-1]=1;
        int chosen=-1,inverse=0;std::vector<int> values;
        for(int i=0;i<eligible;i++) {
            int value=evaluate(input[i],point);values.push_back(value);
            if(value!=0 && value!=1)counts.nonboolean_states++;
            if(chosen<0 && value) {chosen=i;inverse=modpow(value,p-2,p);}
        }
        if(chosen<0)inconsistent=false;
        else beta[chosen]=beta[chosen]+Poly(p,inverse)*indicators[s];
        out<<"{\"record\":\"state_choice\",\"case\":\""<<name<<"\",\"state\":"<<s
           <<",\"input_values\":[";
        for(size_t i=0;i<values.size();i++){if(i)out<<',';out<<values[i];}
        out<<"],\"chosen_input\":"<<chosen<<",\"inverse\":"<<inverse<<"}\n";
    }
    need(kind!='C' || inconsistent,"inconsistent-subtuple control");
    for(const auto& b:beta)need(b.deg()<=1 && b.old(m),"nonaffine or noncolumn coefficient");
    int next=old_count;Block U=block(input,1,next);
    auto phi=[&](const Poly& f){return affine_image(f,U,beta);};
    Poly H=one;for(int i=0;i<k;i++)H=H-beta[i]*input[i];
    need(phi(U.product)==H && H.deg()<=delta+1,"ordinary product image");
    auto certificate=[&](const Poly& target) {
        Reduction reduced=reduce_column(target,m,old_count,base);
        need(reduced.remainder.terms.empty(),"nonzero column-state remainder");
        return reduced.cofactors;
    };
    column_ns(out,counts,name+"_sharp_H_Booleanity",base,certificate(H*H-H),
              H*H-H,std::max(0,2*H.deg()));
    if(inconsistent)
        column_ns(out,counts,name+"_inconsistent_subset",base,certificate(H),H,
                  std::max(0,H.deg()));
    auto source_ax=base;
    int field_start=int(source_ax.size());
    for(int v=U.first;v<U.end;v++)
        source_ax.push_back(powp(variable(p,v),p)-variable(p,v));
    int companion_start=int(source_ax.size());
    source_ax.insert(source_ax.end(),U.axioms.begin(),U.axioms.end());
    std::vector<std::vector<Poly>> image(source_ax.size(),
                                       std::vector<Poly>(base.size(),Poly(p)));
    for(size_t a=0;a<base.size();a++)image[a][a]=one;
    for(int i=0;i<k;i++) {
        int a=field_start+i;Poly target=phi(source_ax[a]);image[a]=certificate(target);
        column_ns(out,counts,name+"_field_image_"+std::to_string(i),
                  base,image[a],target,p);
        if(!target.terms.empty())counts.nonzero_fields++;
    }
    for(int i=0;i<k;i++) {
        int a=companion_start+i;Poly target=phi(source_ax[a]);
        need(target==input[i]*H,"companion image mismatch");
        image[a]=certificate(target);
        int bound=input[i].deg()+std::max(0,H.deg());
        need(bound<=source_ax[a].deg(),"original companion activity budget");
        column_ns(out,counts,name+"_companion_image_"+std::to_string(i),
                  base,image[a],target,bound);
    }
    int selected=0;for(int i=0;i<k;i++)if(beta[i].deg()==1)selected=i;
    std::vector<Poly> cof(source_ax.size(),Poly(p));
    cof[2]=one;cof[field_start+selected]=one;
    for(int i=0;i<k;i++)cof[companion_start+i]=Poly(p,-1)*U.coef[i];
    Poly source_target=U.product*U.product-U.product+base[2]+source_ax[field_start+selected];
    int ceiling=std::max(p,2*U.product.deg());
    int source_degree=column_ns(out,counts,name+"_source_consequence",source_ax,
                                cof,source_target,ceiling);
    std::vector<Poly> mapped_cof(base.size(),Poly(p));
    for(size_t a=0;a<source_ax.size();a++)if(!cof[a].terms.empty()) {
        Poly multiplier=phi(cof[a]);
        for(size_t b=0;b<base.size();b++)
            mapped_cof[b]=mapped_cof[b]+multiplier*image[a][b];
    }
    Poly mapped_target=phi(source_target);
    need(!mapped_target.terms.empty(),"vacuous mapped consequence");
    int mapped_degree=column_ns(out,counts,name+"_mapped_consequence",base,
                                mapped_cof,mapped_target,ceiling);
    out<<"{\"record\":\"normalization\",\"case\":\""<<name
       <<"\",\"coefficient_range\":["<<U.first<<','<<U.end<<"],\"beta\":";
    poly_vector(out,beta);out<<",\"H\":";jsonpoly(out,H);
    out<<",\"original_product_degree\":"<<U.product.deg()
       <<",\"image_product_degree\":"<<H.deg()
       <<",\"source_certificate_degree\":"<<source_degree
       <<",\"mapped_certificate_degree\":"<<mapped_degree<<"}\n";
    for(int s=0;s<=m;s++)for(int z=0;z<(kind=='C'?2:1);z++) {
        std::array<int,NV> point{};if(s)point[s-1]=1;if(kind=='C')point[m]=z;
        for(int i=0;i<k;i++)point[U.first+i]=evaluate(beta[i],point);
        models(base,point);models(source_ax,point);
        need(evaluate(source_target,point)==0 && evaluate(mapped_target,point)==0,
             "nonzero consequence on a common model");
        int expected=1;
        for(int i=0;i<eligible;i++)if(evaluate(input[i],point))expected=0;
        need(evaluate(H,point)==expected,"incorrect selector state");
        out<<"{\"record\":\"common_model\",\"case\":\""<<name<<"\",\"point\":";
        point_json(out,point,next);out<<",\"H\":"<<expected<<"}\n";counts.models++;
    }
    if(kind=='C') {
        std::array<int,NV> point{};point[0]=point[1]=point[m]=1;
        for(int i=0;i<k;i++)point[U.first+i]=evaluate(beta[i],point);
        std::vector<Poly> reduced_base=base;
        reduced_base.erase(reduced_base.begin()+old_count);
        models(reduced_base,point);
        need(evaluate(base[old_count],point)==1 && evaluate(input[2]*H,point)==1,
             "missing-collision control does not separate the target");
        out<<"{\"record\":\"omitted_collision_control\",\"case\":\""<<name
           <<"\",\"omitted_base_index\":"<<old_count<<",\"target_value\":1,\"point\":";
        point_json(out,point,next);out<<"}\n";counts.controls++;
    }
    counts.cases++;
}

int main(int argc,char** argv) {
    std::string path;
    for(int i=1;i<argc;i++) {
        std::string arg=argv[i];
        if(arg=="--out" && i+1<argc)path=argv[++i];
        else throw std::runtime_error("usage: check_column_state_normalizers --out PATH");
    }
    try {
        need(!path.empty(),"--out is required");
        need(!std::ifstream(path).good(),"refusing to replace an existing output");
        std::ofstream out(path);need(out.good(),"cannot open output");
        out<<"{\"record\":\"schema\",\"version\":1,\"arithmetic\":\"exact prime fields\","
              "\"polynomials\":\"sparse coefficient/exponent arrays from pc_boundary.hpp\","
              "\"scope\":\"consistent column domains; no PHP row equations\"}\n";
        ColumnCounts count;
        for(int p:{2,3,5})for(int m:{3,5})for(char kind:{'A','B','C','D'})
            column_case(out,count,p,m,kind);
        out<<"{\"record\":\"summary\",\"cases\":"<<count.cases
           <<",\"ns_certificates\":"<<count.certificates<<",\"common_models\":"<<count.models
           <<",\"omitted_collision_controls\":"<<count.controls
           <<",\"nonzero_field_images\":"<<count.nonzero_fields
           <<",\"nonboolean_input_state_values\":"<<count.nonboolean_states<<"}\n";
        out.flush();need(out.good(),"output failure");
        std::cout<<"Passed "<<count.cases<<" cases, "<<count.certificates
                 <<" NS certificates, "<<count.models<<" common models, "
                 <<count.controls<<" omitted-collision controls; output "<<path<<"\n";
        return 0;
    } catch(const std::exception& e) {std::cerr<<"ERROR: "<<e.what()<<"\n";return 1;}
}
