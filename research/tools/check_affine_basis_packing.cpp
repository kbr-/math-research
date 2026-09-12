// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact affine-bin images, degree-adapted bases, and Boolean-degree controls.
#define main small_probe_unused_main
#include "check_small_probe_normalizers.cpp"
#undef main

using Matrix=std::vector<std::vector<int>>;
struct PackingCounts {int cases=0,certificates=0,models=0,degree_cases=0,cube_points=0,nonboolean=0;};
struct Reduction {std::vector<Poly> cofactors;Poly remainder;};
Reduction reduce_boolean(const Poly& input,const std::vector<Poly>& boolean) {
    need(input.old(int(boolean.size())),"domain target uses fresh variables");
    Poly remainder=input;std::vector<Poly> cof(boolean.size(),Poly(input.p));
    while(true) {
        bool found=false;Mon mon{};int coefficient=0,variable_id=-1;
        for(const auto& term:remainder.terms) {
            for(size_t i=0;i<boolean.size();i++)if(term.first[i]>=2) {
                mon=term.first;coefficient=term.second;variable_id=int(i);found=true;break;
            }
            if(found)break;
        }
        if(!found)break;
        mon[variable_id]-=2;Poly q(input.p);q.add(mon,coefficient);
        cof[variable_id]=cof[variable_id]+q;
        remainder=remainder-q*boolean[variable_id];
    }
    return {cof,remainder};
}
std::vector<Poly> boolean_certificate(const Poly& target,const std::vector<Poly>& boolean) {
    auto result=reduce_boolean(target,boolean);
    need(result.remainder.terms.empty(),"nonzero Boolean remainder");
    return result.cofactors;
}
int record_ns(std::ostream& out,PackingCounts& count,const std::string& name,
              const std::vector<Poly>& ax,const std::vector<Poly>& cof,
              const Poly& target,int bound) {
    int degree=ns(out,name,ax,cof,target,bound);count.certificates++;return degree;
}
int polynomial_rank(const std::vector<Poly>& input,int p) {
    std::map<Mon,Poly> rows;
    for(Poly q:input)while(!q.terms.empty()) {
        auto first=*q.terms.begin();auto found=rows.find(first.first);
        if(found==rows.end()) {
            rows.emplace(first.first,Poly(p,modpow(first.second,p-2,p))*q);break;
        }
        q=q-Poly(p,first.second)*found->second;
    }
    return int(rows.size());
}
Matrix identity(int n) {Matrix out(n,std::vector<int>(n));for(int i=0;i<n;i++)out[i][i]=1;return out;}
void matrix_json(std::ostream& out,const Matrix& matrix,int p) {
    out<<'[';
    for(size_t i=0;i<matrix.size();i++) {
        if(i)out<<',';
        out<<'[';
        for(size_t j=0;j<matrix[i].size();j++){if(j)out<<',';out<<(matrix[i][j]%p+p)%p;}
        out<<']';
    }
    out<<']';
}
std::vector<std::vector<int>> factor_groups(const std::vector<Poly>& basis) {
    std::vector<int> affine,nonlinear;
    for(size_t i=0;i<basis.size();i++) {
        need(basis[i].deg()>=1,"basis contains a constant");
        (basis[i].deg()==1?affine:nonlinear).push_back(int(i));
    }
    std::vector<std::vector<int>> groups;size_t a=0,n=0;
    while(a<affine.size() && n<nonlinear.size())groups.push_back({affine[a++],nonlinear[n++]});
    while(a+1<affine.size()){groups.push_back({affine[a],affine[a+1]});a+=2;}
    if(a<affine.size())groups.push_back({affine[a]});
    while(n<nonlinear.size())groups.push_back({nonlinear[n++]});
    return groups;
}
struct Tuple {std::vector<Poly> input;Matrix from_basis,basis_from_input;};
void packing_case(std::ostream& out,PackingCounts& count,const std::string& kind,
                  int p,int old_count,int h,const std::vector<Poly>& basis,
                  const std::vector<Tuple>& tuples) {
    Poly one(p,1);const int r=int(basis.size());
    auto boolean=domains(p,std::vector<int>(old_count,2));
    auto groups=factor_groups(basis);
    int affine=0,delta=0,W=0;
    for(const auto& b:basis){affine+=int(b.deg()==1);delta=std::max(delta,b.deg());W+=b.deg();}
    need(polynomial_rank(basis,p)==r,"basis rank");
    auto with_one=basis;with_one.push_back(one);
    need(polynomial_rank(with_one,p)==r+1,"one belongs to the input span");
    int required=std::max(r-affine,(r+1)/2);
    need(int(groups.size())==required && required<=h,"affine-bin count");
    need(W<=h*(delta+1),"product degree budget");
    int total_variables=old_count;
    for(const auto& tuple:tuples)total_variables+=h*int(tuple.input.size());
    need(total_variables<=NV,"fixture variable capacity");
    const std::string name=kind+"_r"+std::to_string(r)+"_h"+std::to_string(h)+"_F"+std::to_string(p);
    out<<"{\"record\":\"case_start\",\"name\":\""<<name<<"\",\"p\":"<<p
       <<",\"old_variables\":"<<old_count<<",\"accuracy\":"<<h<<",\"rank\":"<<r
       <<",\"affine_basis_count\":"<<affine<<",\"required_rows\":"<<required
       <<",\"W\":"<<W<<",\"delta\":"<<delta<<",\"basis\":";
    poly_vector(out,basis);out<<",\"groups\":[";
    for(size_t j=0;j<groups.size();j++) {
        if(j)out<<',';
        out<<'[';
        for(size_t k=0;k<groups[j].size();k++){if(k)out<<',';out<<groups[j][k];}out<<']';
    }
    out<<"]}\n";
    std::vector<Poly> factors;
    Poly H=one;for(const auto& b:basis){factors.push_back(one-b);H=H*factors.back();}
    need(H.deg()==W,"ordinary product degree");
    std::vector<std::vector<Poly>> bool_basis;
    for(int j=0;j<r;j++) {
        auto cof=boolean_certificate(basis[j]*basis[j]-basis[j],boolean);
        record_ns(out,count,name+"_basis_Booleanity_"+std::to_string(j),
                  boolean,cof,basis[j]*basis[j]-basis[j],2*basis[j].deg());
        bool_basis.push_back(cof);
    }
    std::vector<Poly> Hbool(old_count,Poly(p));
    for(int j=0;j<r;j++) {
        Poly weight=one;
        for(int k=0;k<j;k++)weight=weight*factors[k];
        for(int k=j+1;k<r;k++)weight=weight*factors[k]*factors[k];
        for(int v=0;v<old_count;v++)Hbool[v]=Hbool[v]+weight*bool_basis[j][v];
    }
    record_ns(out,count,name+"_sharp_product_Booleanity",boolean,Hbool,H*H-H,2*W);

    std::vector<Poly> canonical(h*r,Poly(p));
    for(size_t row=0;row<groups.size();row++) {
        int first=groups[row][0];canonical[row*r+first]=one;
        if(groups[row].size()==2)canonical[row*r+groups[row][1]]=one-basis[first];
    }
    std::vector<Block> blocks;std::vector<Poly> beta;
    int next=old_count;
    for(size_t t=0;t<tuples.size();t++) {
        const auto& tuple=tuples[t];int m=int(tuple.input.size());
        need(polynomial_rank(tuple.input,p)==r,"tuple rank");
        std::vector<Poly> listed_affine;
        for(int i=0;i<m;i++) {
            Poly reconstructed(p);
            for(int j=0;j<r;j++) {
                int coefficient=(tuple.from_basis[i][j]%p+p)%p;
                if(coefficient)need(basis[j].deg()<=tuple.input[i].deg(),"unadapted listed-input representation");
                reconstructed=reconstructed+Poly(p,coefficient)*basis[j];
            }
            need(reconstructed==tuple.input[i],"input reconstruction");
            if(tuple.input[i].deg()<=1)listed_affine.push_back(tuple.input[i]);
            bool is_basis=false;for(const auto& b:basis)if(tuple.input[i]==b)is_basis=true;
            if(!is_basis) {
                Poly target=tuple.input[i]*tuple.input[i]-tuple.input[i];
                record_ns(out,count,name+"_input_Booleanity_"+std::to_string(t)+"_"+std::to_string(i),
                          boolean,boolean_certificate(target,boolean),target,2*tuple.input[i].deg());
            }
        }
        for(int j=0;j<r;j++) {
            Poly reconstructed(p);
            for(int i=0;i<m;i++)reconstructed=reconstructed+Poly(p,tuple.basis_from_input[i][j])*tuple.input[i];
            need(reconstructed==basis[j],"basis reconstruction");
        }
        Block U=block(tuple.input,h,next);blocks.push_back(U);
        need(U.product.deg()==h*(delta+1),"original product ledger");
        for(int row=0;row<h;row++)for(int i=0;i<m;i++) {
            Poly image(p);
            for(int j=0;j<r;j++)image=image+Poly(p,tuple.basis_from_input[i][j])*canonical[row*r+j];
            need(image.deg()<=1 && image.old(old_count),"coefficient image is not earlier affine");
            beta.push_back(image);
        }
        out<<"{\"record\":\"tuple\",\"case\":\""<<name<<"\",\"index\":"<<t
           <<",\"listed_affine_rank\":"<<polynomial_rank(listed_affine,p)<<",\"input\":";
        poly_vector(out,tuple.input);out<<",\"from_basis\":";matrix_json(out,tuple.from_basis,p);
        out<<",\"basis_from_input\":";matrix_json(out,tuple.basis_from_input,p);out<<"}\n";
    }
    Block range{Poly(p),{},{},{},old_count,next};
    auto phi=[&](const Poly& q){return affine_image(q,range,beta);};
    for(const auto& U:blocks)need(phi(U.product)==H,"exact affine product realization");
    std::vector<int> sizes(next,p);for(int v=0;v<old_count;v++)sizes[v]=2;
    auto source_axioms=domains(p,sizes);
    std::vector<int> companion_start;
    for(const auto& U:blocks) {
        companion_start.push_back(int(source_axioms.size()));
        source_axioms.insert(source_axioms.end(),U.axioms.begin(),U.axioms.end());
    }
    std::vector<std::vector<Poly>> images(source_axioms.size(),std::vector<Poly>(old_count,Poly(p)));
    for(int v=0;v<old_count;v++)images[v][v]=one;
    for(int v=old_count;v<next;v++) {
        Poly target=phi(source_axioms[v]);images[v]=boolean_certificate(target,boolean);
        record_ns(out,count,name+"_field_image_"+std::to_string(v),
                  boolean,images[v],target,p);
    }
    for(size_t t=0;t<tuples.size();t++)for(size_t i=0;i<tuples[t].input.size();i++) {
        int index=companion_start[t]+int(i);
        for(int j=0;j<r;j++) {
            int coefficient=(tuples[t].from_basis[i][j]%p+p)%p;
            if(!coefficient)continue;
            Poly weight(p,-coefficient);
            for(int k=0;k<r;k++)if(k!=j)weight=weight*factors[k];
            for(int v=0;v<old_count;v++)images[index][v]=images[index][v]+weight*bool_basis[j][v];
        }
        Poly target=phi(source_axioms[index]);
        need(target==tuples[t].input[i]*H,"companion image identity");
        int bound=tuples[t].input[i].deg()+W;
        need(bound<=source_axioms[index].deg(),"original companion budget");
        record_ns(out,count,name+"_companion_image_"+std::to_string(t)+"_"+std::to_string(i),
                  boolean,images[index],target,bound);
    }
    int selected_field=old_count;
    for(int v=old_count;v<next;v++)if(beta[v-old_count].deg()==1)selected_field=v;
    std::vector<Poly> source_cof(source_axioms.size(),Poly(p));source_cof[selected_field]=one;
    Poly source_target=source_axioms[selected_field];int source_bound=p;
    for(size_t t=0;t<blocks.size();t++) {
        source_target=source_target+blocks[t].product*blocks[t].product-blocks[t].product;
        source_bound=std::max(source_bound,2*blocks[t].product.deg());
        for(size_t i=0;i<blocks[t].inputs.size();i++)
            source_cof[companion_start[t]+int(i)]=Poly(p,-1)*blocks[t].coef[i];
    }
    int source_degree=record_ns(out,count,name+"_source_consequence",source_axioms,
                                source_cof,source_target,source_bound);
    std::vector<Poly> mapped_cof(old_count,Poly(p));
    for(size_t i=0;i<source_cof.size();i++)if(!source_cof[i].terms.empty()) {
        Poly cofactor=phi(source_cof[i]);
        for(int v=0;v<old_count;v++)mapped_cof[v]=mapped_cof[v]+cofactor*images[i][v];
    }
    Poly mapped_target=phi(source_target);
    need(!mapped_target.terms.empty(),"mapped consequence is vacuous");
    int mapped_degree=record_ns(out,count,name+"_mapped_consequence",boolean,
                                mapped_cof,mapped_target,source_bound);
    out<<"{\"record\":\"normalization\",\"case\":\""<<name<<"\",\"coefficient_range\":["
       <<old_count<<','<<next<<"],\"coefficient_images\":";
    poly_vector(out,beta);out<<",\"product_image\":";jsonpoly(out,H);
    out<<",\"source_degree\":"<<source_degree<<",\"mapped_certificate_degree\":"<<mapped_degree
       <<",\"mapped_target_degree\":"<<mapped_target.deg()<<",\"selected_field\":"<<selected_field<<"}\n";
    for(int mask=0;mask<(1<<old_count);mask++) {
        std::array<int,NV> point{};for(int v=0;v<old_count;v++)point[v]=(mask>>v)&1;
        for(int v=old_count;v<next;v++)point[v]=evaluate(beta[v-old_count],point);
        models(source_axioms,point);models(boolean,point);
        need(evaluate(source_target,point)==0 && evaluate(mapped_target,point)==0,"consequence at common model");
        out<<"{\"record\":\"common_model\",\"case\":\""<<name<<"\",\"point\":";
        point_json(out,point,next);out<<",\"H\":"<<evaluate(H,point)<<"}\n";count.models++;
    }
    count.cases++;
}
void degree_obstruction(std::ostream& out,PackingCounts& count,int p) {
    Poly one(p,1);std::vector<Poly> b={variable(p,0),
        variable(p,1)*variable(p,2),variable(p,3)*variable(p,4),variable(p,5)*variable(p,6)};
    auto boolean=domains(p,std::vector<int>(7,2));Poly H=one;
    for(int j=0;j<4;j++) {
        H=H*(one-b[j]);Poly target=b[j]*b[j]-b[j];
        record_ns(out,count,"obstruction_Booleanity_F"+std::to_string(p)+"_"+std::to_string(j),
                  boolean,boolean_certificate(target,boolean),target,2*b[j].deg());
    }
    need(polynomial_rank(b,p)==4 && factor_groups(b).size()==3,"mixed obstruction rank/bin count");
    int next=7;Block original=block(b,2,next);
    need(original.product.deg()==6 && H.deg()==7,"mixed degree obstruction");
    for(const auto& term:H.terms)for(int v=0;v<NV;v++)need(term.first[v]<=1,"normalizer function not multilinear");
    out<<"{\"record\":\"degree_obstruction\",\"p\":"<<p<<",\"accuracy\":2,\"rank\":4,"
          "\"listed_affine_rank\":1,\"required_rows\":3,\"affine_product_degree_ceiling\":6,"
          "\"Boolean_normalizer_degree\":7,\"coefficient_maps_enumerated\":0,\"input_tuple\":";
    poly_vector(out,b);out<<",\"normalizer_function\":";jsonpoly(out,H);out<<"}\n";
    for(int mask=0;mask<128;mask++) {
        std::array<int,NV> point{};for(int v=0;v<7;v++)point[v]=(mask>>v)&1;
        int expected=1;for(const auto& g:b)if(evaluate(g,point))expected=0;
        models(boolean,point);need(evaluate(H,point)==expected,"obstruction function on Boolean cube");
        out<<"{\"record\":\"degree_control_point\",\"p\":"<<p<<",\"point\":";
        point_json(out,point,7);out<<",\"inputs\":[";
        for(int j=0;j<4;j++){if(j)out<<',';out<<evaluate(b[j],point);}out<<"],\"H\":"<<expected<<"}\n";
        count.cube_points++;
    }
    count.degree_cases++;
}
void nonboolean_control(std::ostream& out,PackingCounts& count,int p) {
    need(p>2,"nonboolean control requires odd characteristic");
    Poly one(p,1),x=variable(p,0),y=variable(p,1),z=variable(p,2),g=x+y;
    auto boolean=domains(p,std::vector<int>(3,2));int next=3;
    Block U=block({g,z},1,next);std::vector<Poly> beta={one,one-g};
    Poly H=affine_image(U.product,U,beta),image=g*H;
    auto failed_bool=reduce_boolean(g*g-g,boolean);
    need(!failed_bool.remainder.terms.empty(),"missing Booleanity unexpectedly holds");
    Poly field_image=powp(beta[1],p)-beta[1];
    record_ns(out,count,"nonBoolean_control_field_image_F"+std::to_string(p),
              boolean,boolean_certificate(field_image,boolean),field_image,p);
    std::array<int,NV> point{};point[0]=point[1]=1;
    point[3]=1;point[4]=evaluate(beta[1],point);models(boolean,point);
    need(evaluate(image,point)!=0 && evaluate(g*g-g,point)!=0,"missing Booleanity countermodel");
    for(int v=3;v<next;v++)need(evaluate(powp(variable(p,v),p)-variable(p,v),point)==0,"field control");
    out<<"{\"record\":\"nonBoolean_input_control\",\"p\":"<<p<<",\"point\":";
    point_json(out,point,next);out<<",\"input_Booleanity_remainder\":";
    jsonpoly(out,failed_bool.remainder);out<<",\"product_image\":";jsonpoly(out,H);
    out<<",\"companion_image\":";jsonpoly(out,image);
    out<<",\"companion_value\":"<<evaluate(image,point)<<"}\n";count.nonboolean++;
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","usage: check_affine_basis_packing --out PATH");
        std::filesystem::path path(argv[2]);need(!std::filesystem::exists(path),"refuse to overwrite output");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot open output");
        out<<"{\"record\":\"metadata\",\"schema\":1,\"arithmetic\":\"exact Fp ordinary polynomials\","
             "\"monomial_encoding\":\"[coefficient,[[variable,exponent],...]]\","
             "\"zero_polynomial\":[],\"retained_base\":\"old Boolean domains only\","
             "\"randomness\":\"none\",\"scope\":\"existing affine-bin criterion and mixed normal form\"}\n";
        PackingCounts count;
        for(int p:{2,3,5}) {
            for(auto [r,h]:std::vector<std::pair<int,int>>{{1,1},{2,1},{3,2},{4,2},{3,3}}) {
                std::vector<Poly> basis;for(int i=0;i<r;i++)basis.push_back(variable(p,i));
                Matrix I=identity(r);
                packing_case(out,count,"free",p,r,h,basis,{{basis,I,I}});
            }
            std::vector<Poly> mixed={variable(p,0),variable(p,1),
                variable(p,2)*variable(p,3),variable(p,4)*variable(p,5)};
            packing_case(out,count,"mixed",p,6,2,mixed,{{mixed,identity(4),identity(4)}});
            Poly x=variable(p,0),y=variable(p,1);
            std::vector<Poly> basis={x,y,x*y};
            Tuple A{basis,identity(3),identity(3)};
            Tuple B{{x*y,x-x*y,y-x*y},{{0,0,1},{1,0,-1},{0,1,-1}},
                    {{1,1,1},{1,0,0},{0,1,0}}};
            packing_case(out,count,"shared_span",p,2,2,basis,{A,B});
            degree_obstruction(out,count,p);
            if(p>2)nonboolean_control(out,count,p);
        }
        need(count.cases==21 && count.certificates==350 && count.models==318
             && count.degree_cases==3 && count.cube_points==384 && count.nonboolean==2,"summary counts");
        out<<"{\"record\":\"summary\",\"status\":\"passed\",\"normalizations\":"<<count.cases
           <<",\"NS_certificates\":"<<count.certificates<<",\"common_models\":"<<count.models
           <<",\"degree_obstruction_cases\":"<<count.degree_cases
           <<",\"degree_control_points\":"<<count.cube_points
           <<",\"nonBoolean_input_controls\":"<<count.nonboolean<<"}\n";
        out.close();need(bool(out),"output write failed");
        std::cout<<"PASS: 21 normalizations, 350 NS certificates, 318 common models, "
                   "384 degree-control points, 2 non-Boolean input controls.\n";
        return 0;
    } catch(const std::exception& error) {std::cerr<<"FAIL: "<<error.what()<<'\n';return 1;}
}
