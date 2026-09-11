// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact local certificates for removing the theorem boundary and ordinary clauses.
#include "ens_symbolic.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace ens_symbolic;
void need(bool condition,const std::string& why){
    if(!condition)throw std::runtime_error(why);
}
struct Counts{int cases=0,boundary=0,companions=0,fields=0,omissions=0,later=0;};

void certificate(std::ostream& out,const Ring& ring,const std::string& name,
                 const Polynomial& original,const Polynomial& image,
                 const std::vector<Polynomial>& axioms,const std::vector<Polynomial>& cofactors){
    need(axioms.size()==cofactors.size(),"certificate arity");
    Polynomial sum;int budget=0;
    for(size_t j=0;j<axioms.size();j++){
        Polynomial term=ring.multiply(axioms[j],cofactors[j]);
        ring.accumulate(sum,term);budget=std::max(budget,degree(term));
    }
    need(sum==image,"certificate reconstruction: "+name);
    need(budget<=degree(original),"original degree exceeded: "+name);
    out<<"{\"name\":\""<<name<<"\",\"original\":";write_json(out,original);
    out<<",\"image\":";write_json(out,image);
    out<<",\"original_degree\":"<<degree(original)<<",\"certificate_degree\":"<<budget;
    out<<",\"cofactors\":";write_polynomials(out,cofactors);out<<'}';
}

void check_case(std::ostream& out,int p,int h,int n,Counts& count){
    Ring ring(p,64);Polynomial one=ring.constant(1),zero;
    std::vector<Polynomial> row_inputs;
    Polynomial rho;
    for(int j=0;j<n;j++){row_inputs.push_back(ring.variable(j));ring.accumulate(rho,row_inputs.back());}
    Polynomial x=ring.variable(0),y=ring.variable(n);
    Polynomial row_axiom=ring.subtract(rho,one),collision=ring.multiply(x,y);
    Polynomial boolean=ring.subtract(ring.multiply(x,x),x);
    std::vector<Polynomial> base={row_axiom,collision,boolean};
    int fresh=n+1;
    Block row=make_block(ring,row_inputs,h,fresh);
    Block column=make_block(ring,{ring.subtract(one,x),ring.subtract(one,y)},h,fresh);
    Block boundary=make_block(ring,{row.product,column.product},h,fresh);
    for(const auto& e:boundary.companions)need(degree(e)==2*h*h+3*h,"boundary degree formula");

    std::map<int,Polynomial> top_images=coefficient_images(ring,boundary,{zero,zero});
    auto images=top_images;
    auto row_images=coefficient_images(ring,row,std::vector<Polynomial>(n,one));
    auto column_images=coefficient_images(ring,column,{one,x});
    images.insert(row_images.begin(),row_images.end());
    images.insert(column_images.begin(),column_images.end());
    need(ring.substitute(boundary.product,images)==one,"theorem target must become one");
    need(boundary.product!=one,"unchanged target control");

    out<<"{\"record\":\"boundary_case\",\"p\":"<<p<<",\"h\":"<<h<<",\"row_width\":"<<n;
    out<<",\"base_axioms\":";write_polynomials(out,base);
    out<<",\"row\":";write_block(out,row);out<<",\"column\":";write_block(out,column);
    out<<",\"boundary\":";write_block(out,boundary);
    out<<",\"coefficient_images\":[";bool comma=false;
    for(const auto& [v,poly]:images){
        if(comma)out<<',';
        comma=true;out<<'['<<v<<',';write_json(out,poly);out<<']';
    }
    std::vector<Polynomial> earlier=row.companions;
    earlier.insert(earlier.end(),column.companions.begin(),column.companions.end());
    earlier.push_back(row_axiom);earlier.push_back(collision);
    out<<"],\"boundary_only_axioms\":";write_polynomials(out,earlier);
    out<<",\"boundary_only_certificates\":[";
    for(int j=0;j<2;j++){
        if(j)out<<',';
        std::vector<Polynomial> q(earlier.size());
        if(j==0){
            for(int k=0;k<n;k++)q[k]=one;
            q[n+2]=ring.subtract(zero,row.product);
        }else{q[n]=one;q[n+1]=x;q[n+3]=column.product;}
        Polynomial image=ring.substitute(boundary.companions[j],top_images);
        certificate(out,ring,j==0?"row_input":"collision_input",boundary.companions[j],image,earlier,q);
        Polynomial omitted=ring.multiply(q[n+2+j],earlier[n+2+j]);
        need(!omitted.empty(),"essential base summand omission control");
        count.boundary++;count.omissions++;
    }
    out<<"],\"combined_companion_certificates\":[";comma=false;
    for(size_t j=0;j<row.companions.size();j++){
        if(comma)out<<',';
        comma=true;
        certificate(out,ring,"row_"+std::to_string(j),row.companions[j],
                    ring.substitute(row.companions[j],images),base,
                    {ring.subtract(zero,row.inputs[j]),zero,zero});count.companions++;
    }
    for(int j=0;j<2;j++){
        out<<',';
        certificate(out,ring,"collision_"+std::to_string(j),column.companions[j],
                    ring.substitute(column.companions[j],images),base,
                    {zero,column.inputs[j],zero});count.companions++;
        out<<',';
        certificate(out,ring,"boundary_"+std::to_string(j),boundary.companions[j],
                    ring.substitute(boundary.companions[j],images),base,
                    j==0?std::vector<Polynomial>{ring.constant(-1),zero,zero}
                        :std::vector<Polynomial>{zero,one,zero});count.companions++;
    }
    out<<"],\"field_image_certificates\":[";comma=false;
    for(const auto& [v,poly]:images){
        if(comma)out<<',';
        comma=true;
        Polynomial original=ring.subtract(ring.power(ring.variable(v),p),ring.variable(v));
        Polynomial image=ring.substitute(original,images),q;
        if(poly==x){
            for(int k=0;k<=p-2;k++)ring.accumulate(q,ring.power(x,k));
            need(!image.empty(),"nonconstant field image needs Boolean equation");
        }
        certificate(out,ring,"field_"+std::to_string(v),original,image,base,{zero,zero,q});
        count.fields++;
    }
    out<<"],\"boundary_target_image\":";write_json(out,ring.substitute(boundary.product,images));
    out<<",\"target_changed_control\":true,\"essential_base_omissions_rejected\":2";
    if(h==1){
        int later_first=fresh;
        Block later=make_block(ring,{ring.subtract(boundary.product,row.product),
                      ring.subtract(one,ring.multiply(boundary.product,column.product))},1,fresh);
        std::vector<Polynomial> mapped_inputs;
        for(const auto& g:later.inputs)mapped_inputs.push_back(ring.substitute(g,images));
        Block rebuilt=make_block(ring,mapped_inputs,1,later_first);
        out<<",\"later_original\":";write_block(out,later);
        out<<",\"later_specialized\":";write_block(out,rebuilt);
        out<<",\"later_original_image_degrees\":[";
        for(size_t j=0;j<later.companions.size();j++){
            Polynomial image=ring.substitute(later.companions[j],images);
            need(image==rebuilt.companions[j],"later ENS must use specialized inputs");
            need(image!=later.companions[j],"unchanged later companion control");
            need(degree(image)<=degree(later.companions[j]),"later degree increase");
            if(j)out<<',';
            out<<'['<<degree(later.companions[j])<<','<<degree(image)<<']';count.later++;
        }
        out<<"],\"unchanged_later_controls_rejected\":2";
    }
    out<<"}\n";count.cases++;
}

int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","Usage: check_direct_php_boundary --out NEW_PATH");
        std::string path=argv[2];need(!std::filesystem::exists(path),"output must be new");
        std::ofstream out(path);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"direct_php_boundary\",\"arithmetic\":\"exact\","
              "\"scope\":\"local clause and boundary certificates, not a Frege proof\"}\n";
        Counts c;
        for(int p:{2,3,5,7})for(int h:{1,2})for(int n:{2,3})check_case(out,p,h,n,c);
        out<<"{\"record\":\"summary\",\"cases\":"<<c.cases<<",\"boundary_certificates\":"<<c.boundary
           <<",\"companion_certificates\":"<<c.companions<<",\"field_certificates\":"<<c.fields
           <<",\"base_omission_controls\":"<<c.omissions<<",\"later_companions\":"<<c.later
           <<",\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failure");
        std::cout<<c.cases<<" cases: "<<c.boundary<<" boundary, "<<c.companions<<" companion, "
                 <<c.fields<<" field certificates; "<<c.omissions<<" base omissions and "
                 <<c.later<<" later-companion controls.\n";
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
