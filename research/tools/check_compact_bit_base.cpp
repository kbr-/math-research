// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Complete compact-bit decoder and source-clause NS image certificates.
#include "ens_symbolic.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace ens_symbolic;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
struct Term{std::string label;Polynomial q,f;};
void certificate(std::ostream& out,const Ring& ring,const std::string& name,
                 const Polynomial& target,const std::vector<Term>& terms,int bound){
    Polynomial sum;int degree_used=0,used=0;
    for(const auto& t:terms)if(!t.q.empty() && !t.f.empty()){
        auto term=ring.multiply(t.q,t.f);ring.accumulate(sum,term);
        degree_used=std::max(degree_used,degree(term));++used;
    }
    need(sum==target && degree_used<=bound,"NS certificate "+name);
    out<<"{\"type\":\"NS_certificate\",\"name\":\""<<name<<"\",\"target\":";write_json(out,target);
    out<<",\"degree\":"<<degree_used<<",\"bound\":"<<bound<<",\"terms\":[";
    bool comma=false;
    for(const auto& t:terms)if(!t.q.empty() && !t.f.empty()){
        if(comma)out<<',';
        comma=true;out<<"{\"label\":\""<<t.label<<"\",\"cofactor\":";write_json(out,t.q);
        out<<",\"axiom\":";write_json(out,t.f);out<<'}';
    }
    out<<"]}\n";
    std::cout<<name<<": "<<used<<" exact axiom multiples, degree "<<degree_used<<".\n";
}
void decoder_case(std::ostream& out,int ell){
    Ring ring(2,64);int n=1<<ell,variables=2*n;auto one=ring.constant(1);
    std::string name="decoder_l"+std::to_string(ell);
    std::vector<Polynomial> bits;
    for(int row=0;row<2;row++)for(int t=0;t<ell;t++){
        Polynomial b;for(int j=0;j<n;j++)if((j>>t)&1)ring.accumulate(b,ring.variable(row*n+j));
        bits.push_back(b);
    }
    auto P=one;
    for(int t=0;t<ell;t++)P=ring.multiply(P,ring.add(one,ring.add(bits[t],bits[ell+t])));
    need(degree(P)==ell,"decoded equality ordinary degree");
    std::vector<Term> terms;std::vector<int> boolean(variables);
    std::map<std::pair<int,int>,int> row_pair;
    for(int v=0;v<variables;v++){
        auto x=ring.variable(v);boolean[v]=int(terms.size());
        terms.push_back({"Boolean_"+std::to_string(v),{},ring.subtract(ring.multiply(x,x),x)});
    }
    for(int row=0;row<2;row++)for(int j=0;j<n;j++)for(int k=j+1;k<n;k++){
        int a=row*n+j,b=row*n+k;row_pair[{a,b}]=int(terms.size());
        terms.push_back({"row_exclusion_"+std::to_string(a)+"_"+std::to_string(b),{},
                         ring.multiply(ring.variable(a),ring.variable(b))});
    }
    std::vector<Polynomial> rho(2);
    for(int row=0;row<2;row++)for(int j=0;j<n;j++)ring.accumulate(rho[row],ring.variable(row*n+j));
    int row0=int(terms.size());terms.push_back({"row_0",{},ring.subtract(rho[0],one)});
    int row1=int(terms.size());terms.push_back({"row_1",{},ring.subtract(rho[1],one)});
    Polynomial normal;int monomial_steps=0;
    for(const auto& [source,c]:P){
        Monomial m=source;bool vanished=false;
        while(true){
            auto repeat=std::adjacent_find(m.begin(),m.end());
            if(repeat!=m.end()){
                int v=*repeat;Monomial q=m;
                for(int k=0;k<2;k++)q.erase(std::find(q.begin(),q.end(),v));
                ring.accumulate(terms[boolean[v]].q,Polynomial{{q,c}});
                m.erase(std::find(m.begin(),m.end(),v));++monomial_steps;continue;
            }
            int a=-1,b=-1;
            for(size_t i=1;i<m.size();i++)if(m[i-1]/n==m[i]/n){a=m[i-1];b=m[i];break;}
            if(a>=0){
                Monomial q=m;q.erase(std::find(q.begin(),q.end(),a));q.erase(std::find(q.begin(),q.end(),b));
                ring.accumulate(terms[row_pair.at({a,b})].q,Polynomial{{q,c}});
                vanished=true;++monomial_steps;
            }
            break;
        }
        if(!vanished)ring.accumulate(normal,Polynomial{{m,c}});
    }
    Polynomial interpolated;
    for(const auto& [m,c]:normal){
        if(m.empty()){
            ring.accumulate(interpolated,ring.multiply(rho[0],rho[1]),c);
            ring.accumulate(terms[row0].q,ring.constant(-c));
            ring.accumulate(terms[row1].q,rho[0],-c);
        }else if(m.size()==1){
            auto x=ring.variable(m[0]);int row=m[0]/n;
            ring.accumulate(interpolated,ring.multiply(x,rho[1-row]),c);
            ring.accumulate(terms[row?row0:row1].q,x,-c);
        }else{
            need(m.size()==2 && m[0]/n!=m[1]/n,"not a two-row normal form");
            ring.accumulate(interpolated,Polynomial{{m,c}});
        }
    }
    Polynomial diagonal;
    for(int j=0;j<n;j++){
        auto f=ring.multiply(ring.variable(j),ring.variable(n+j));
        ring.accumulate(diagonal,f);terms.push_back({"column_collision_"+std::to_string(j),one,f});
    }
    need(interpolated==diagonal,"two-row interpolation coefficients are not the equality table");
    out<<"{\"type\":\"decoder_case\",\"name\":\""<<name<<"\",\"ell\":"<<ell<<",\"holes\":"<<n
       <<",\"unary_variables\":"<<variables<<",\"bit_images\":";write_polynomials(out,bits);
    out<<",\"decoded_equality\":";write_json(out,P);out<<",\"two_row_normal_form\":";
    write_json(out,normal);out<<",\"interpolated_diagonal\":";write_json(out,diagonal);
    out<<",\"monomial_reduction_steps\":"<<monomial_steps<<"}\n";
    certificate(out,ring,name+"/equality_image",P,terms,std::max(ell,2));
    for(int row=0;row<2;row++)for(int t=0;t<ell;t++){
        std::vector<Term> proof;
        for(int j=0;j<n;j++)if((j>>t)&1)proof.push_back({terms[boolean[row*n+j]].label,one,terms[boolean[row*n+j]].f});
        auto b=bits[row*ell+t];
        certificate(out,ring,name+"/bit_Boolean_"+std::to_string(row)+"_"+std::to_string(t),
                    ring.subtract(ring.multiply(b,b),b),proof,2);
    }
    if(ell==2){
        std::map<int,int> point;for(int v=0;v<variables;v++)point[v]=0;
        for(int v:{0,1,2,n+3})point[v]=1;
        for(int v=0;v<variables;v++)need(ring.evaluate(terms[boolean[v]].f,point)==0,"weak model Booleanity");
        need(ring.evaluate(terms[row0].f,point)==0 && ring.evaluate(terms[row1].f,point)==0,"weak model rows");
        for(int j=0;j<n;j++)need(point[j]*point[n+j]==0,"weak model column collision");
        need(ring.evaluate(P,point)==1,"weak-row decoder failure");
        out<<"{\"type\":\"missing_functionality_control\",\"ell\":2,\"one_coordinates\":[0,1,2,7],"
             "\"all_other_coordinates\":0,\"decoded_equality_value\":1,"
             "\"scope\":\"satisfies the local two-row weak base, not the full n+1-pigeon system\"}\n";
    }
}
void packing_case(std::ostream& out,int ell){
    Ring ring(2,64);auto one=ring.constant(1);int h=(ell+1)/2,fresh=2*ell;
    std::vector<Polynomial> g;
    for(int t=0;t<ell;t++)g.push_back(ring.add(ring.variable(t),ring.variable(ell+t)));
    Block block=make_block(ring,g,h,fresh);std::map<int,Polynomial> images;
    for(const auto& row:block.variables)for(int v:row)images[v]=ring.constant(0);
    for(int u=0;u<h;u++){
        int first=2*u;images[block.variables[u][first]]=one;
        if(first+1<ell)images[block.variables[u][first+1]]=ring.subtract(one,g[first]);
    }
    auto E=one;for(const auto& f:g)E=ring.multiply(E,ring.subtract(one,f));
    need(ring.substitute(block.product,images)==E && degree(E)==ell,"source clause product image");
    std::string name="packing_l"+std::to_string(ell);
    out<<"{\"type\":\"packing_case\",\"name\":\""<<name<<"\",\"ell\":"<<ell<<",\"h\":"<<h
       <<",\"original_companion_degree\":"<<2*h+1<<",\"final_boundary_original_degree\":"<<2*h*h+3*h
       <<",\"final_boundary_image_degree\":"<<ell<<",\"block\":";write_block(out,block);
    out<<",\"coefficient_images\":[";
    bool comma=false;for(const auto& [v,p]:images){if(comma)out<<',';comma=true;out<<"["<<v<<',';write_json(out,p);out<<']';}
    out<<"],\"product_image\":";write_json(out,E);out<<"}\n";
    for(int t=0;t<ell;t++){
        auto q=ring.constant(-1);for(int s=0;s<ell;s++)if(s!=t)q=ring.multiply(q,ring.subtract(one,g[s]));
        std::vector<Term> proof;
        for(int v:{t,ell+t}){auto b=ring.variable(v);proof.push_back({"bit_Boolean_"+std::to_string(v),q,ring.subtract(ring.multiply(b,b),b)});}
        auto target=ring.substitute(block.companions[t],images);
        need(target==ring.multiply(g[t],E),"companion substitution");
        certificate(out,ring,name+"/companion_"+std::to_string(t),target,proof,2*h+1);
    }
    for(const auto& [v,p]:images){
        auto target=ring.subtract(ring.multiply(p,p),p);if(target.empty())continue;
        std::vector<Term> proof;
        for(int u=0;u<h;u++){
            int t=2*u;
            if(t+1<ell && v==block.variables[u][t+1])
                for(int b:{t,ell+t}){auto x=ring.variable(b);proof.push_back({"bit_Boolean_"+std::to_string(b),one,ring.subtract(ring.multiply(x,x),x)});}
        }
        certificate(out,ring,name+"/coefficient_field_"+std::to_string(v),target,proof,2);
    }
    need(ell<=2*h*h+3*h,"final boundary image ceiling");
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");
        auto parent=std::filesystem::path(argv[2]).parent_path();if(!parent.empty())std::filesystem::create_directories(parent);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"compact_bit_base\",\"p\":2,\"seed\":null,"
             "\"encoding\":\"[coefficient,[variable,...]], repeated indices for powers\","
             "\"scope\":\"complete local decoder and source-clause image certificates; lower bound and Frege bridge are proved analytically\"}\n";
        for(int ell:{1,2,3,4}){decoder_case(out,ell);packing_case(out,ell);}
        out.close();need(bool(out),"output write failed");
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
