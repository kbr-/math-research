// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Complete ordinary-NS witnesses for odd-prime affine maps and MOD source profiles.
#include "domain_polynomial.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace domain_polynomial;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
struct Cert {Polynomial target;std::map<int,Polynomial> cof;};
struct Context {
    Ring ring;
    std::vector<Polynomial> axioms;
    std::vector<std::string> names;
    std::vector<int> powers;
    int certificates=0;
    explicit Context(int p):ring(p,64){}
    int add(const std::string& name,const Polynomial& polynomial){
        int id=int(axioms.size());axioms.push_back(polynomial);names.push_back(name);return id;
    }
    void domains(int old,int total){
        for(int i=0;i<total;++i){
            int exponent=i<old?2:ring.p;powers.push_back(exponent);
            auto x=ring.variable(i);
            need(add("domain/"+std::to_string(i),ring.subtract(ring.power(x,exponent),x))==i,
                 "domain index");
        }
    }
    Cert ax(int id)const{return {axioms.at(id),{{id,ring.constant(1)}}};}
    Cert scale(Cert c,const Polynomial& q)const{
        c.target=ring.multiply(c.target,q);
        for(auto& [id,p]:c.cof){(void)id;p=ring.multiply(p,q);}
        return c;
    }
    void plus(Cert& a,const Cert& b,int scalar=1)const{
        ring.accumulate(a.target,b.target,scalar);
        for(const auto& [id,q]:b.cof)ring.accumulate(a.cof[id],q,scalar);
    }
    Cert domain(const Polynomial& target)const{
        auto reduced=domain_reduce(ring,target,powers);
        verify_reduction(ring,target,powers,reduced);
        need(reduced.remainder.empty(),"nonzero domain remainder");
        Cert result;result.target=target;
        for(std::size_t i=0;i<reduced.coefficients.size();++i)
            if(!reduced.coefficients[i].empty())result.cof[int(i)]=reduced.coefficients[i];
        return result;
    }
    void write(std::ostream& out,const std::string& name,const Cert& c,int budget){
        Polynomial actual;int used=0;
        out<<"{\"record\":\"NS_certificate\",\"name\":\""<<name
           <<"\",\"budget\":"<<budget<<",\"target\":";write_json(out,c.target);
        out<<",\"terms\":[";bool comma=false;
        for(const auto& [id,q]:c.cof)if(!q.empty()){
            auto term=ring.multiply(q,axioms.at(id));ring.accumulate(actual,term);
            used=std::max(used,degree(q)+degree(axioms.at(id)));
            if(comma)out<<',';
            comma=true;
            out<<"{\"axiom_id\":"<<id<<",\"cofactor\":";write_json(out,q);out<<'}';
        }
        need(actual==c.target && used<=budget,"certificate "+name);
        out<<"],\"witness_degree\":"<<used<<"}\n";++certificates;
    }
    void header(std::ostream& out,const std::string& name)const{
        out<<"{\"record\":\"case\",\"name\":\""<<name<<"\",\"field\":"<<ring.p
           <<",\"domain_exponents\":[";
        for(std::size_t i=0;i<powers.size();++i){if(i)out<<',';out<<powers[i];}
        out<<"],\"axioms\":[";
        for(std::size_t i=0;i<axioms.size();++i){
            if(i)out<<',';
            out<<"{\"id\":"<<i<<",\"name\":\""<<names[i]<<"\",\"polynomial\":";
            write_json(out,axioms[i]);out<<'}';
        }
        out<<"]}\n";
    }
    void model(std::ostream& out,const std::string& name,std::map<int,int> values,
               bool valid,const Polynomial& probe,int expected)const{
        for(std::size_t i=0;i<powers.size();++i)values.emplace(int(i),0);
        bool all=true;out<<"{\"record\":\"model\",\"name\":\""<<name<<"\",\"values\":[";
        for(std::size_t i=0;i<powers.size();++i){if(i)out<<',';out<<values.at(int(i));}
        out<<"],\"axiom_values\":[";
        for(std::size_t i=0;i<axioms.size();++i){
            int value=ring.evaluate(axioms[i],values);all&=value==0;
            if(i)out<<',';
            out<<value;
        }
        int value=ring.evaluate(probe,values);
        need(all==valid && value==expected,"model "+name);
        out<<"],\"satisfies_all_axioms\":"<<(all?"true":"false")<<",\"probe\":";
        write_json(out,probe);out<<",\"probe_value\":"<<value<<"}\n";
    }
};
void map_record(std::ostream& out,const Block& original,const std::map<int,Polynomial>& images){
    out<<"{\"record\":\"substitution\",\"original_block\":";write_block(out,original);
    out<<",\"coefficient_images\":[";bool comma=false;
    for(const auto& [id,p]:images){
        if(comma)out<<',';
        comma=true;
        out<<"{\"variable\":"<<id<<",\"image\":";write_json(out,p);out<<'}';
    }
    out<<"]}\n";
}
Cert product_boolean(const Context& c,const Block& block,const std::vector<int>& companions){
    Cert result;
    for(std::size_t i=0;i<companions.size();++i)
        c.plus(result,c.scale(c.ax(companions[i]),block.prefix[i]),-1);
    need(result.target==c.ring.subtract(c.ring.power(block.product,2),block.product),
         "companion Booleanity identity");
    return result;
}
int negative_mod_profile(std::ostream& out,int prime,bool raw_transfer){
    Context c(prime);const auto& r=c.ring;int h=2,fresh=3,s=2*h+prime-1;
    auto one=r.constant(1),x=r.variable(0),y=r.variable(1),z=r.variable(2);
    auto L0=r.subtract(r.add(x,r.multiply(r.constant(2),y)),z);
    auto L1=r.subtract(y,z);
    auto core=make_block(r,{L0,L1},h,fresh);c.domains(3,fresh);
    std::vector<int> comp;
    for(int i=0;i<2;++i)comp.push_back(c.add("affine_core/"+std::to_string(i),core.companions[i]));
    c.header(out,"negative_MOD_"+std::to_string(prime));
    std::vector<Polynomial> inputs,prefix;
    Cert residual;
    for(int i=0;i<2;++i){
        inputs.push_back(r.power(core.inputs[i],prime-1));
        prefix.push_back(r.multiply(core.prefix[i],core.inputs[i]));
        auto error=c.domain(r.subtract(core.inputs[i],r.power(core.inputs[i],prime)));
        c.plus(residual,c.scale(error,core.prefix[i]));
    }
    auto target=r.subtract(one,core.product);
    for(int i=0;i<2;++i)r.accumulate(target,r.multiply(prefix[i],inputs[i]),-1);
    need(target==residual.target && s<=h*prime,"source prefix and original weight");
    out<<"{\"record\":\"source_profile\",\"original_weight\":"<<h*prime<<",\"cost\":"<<s
       <<",\"input_weight\":"<<prime-1<<",\"affine_core\":";write_block(out,core);
    out<<",\"actual_MOD_inputs\":";write_polynomials(out,inputs);
    out<<",\"prefixes\":";write_polynomials(out,prefix);out<<"}\n";
    c.write(out,"prefix_residual",residual,s);
    for(int i=0;i<2;++i){
        auto companion=c.scale(c.ax(comp[i]),r.power(core.inputs[i],prime-2));
        need(companion.target==r.multiply(inputs[i],core.product),"power companion");
        c.write(out,"power_companion/"+std::to_string(i),companion,s);
        c.write(out,"input_Booleanity/"+std::to_string(i),
                c.domain(r.subtract(r.power(inputs[i],2),inputs[i])),2*(prime-1));
    }
    c.write(out,"value_Booleanity_from_companions",product_boolean(c,core,comp),4*h);
    if(raw_transfer){
        int original_fresh=fresh;
        auto original=make_block(r,inputs,h,original_fresh);
        std::map<int,Polynomial> images;
        for(int u=0;u<h;++u)for(int i=0;i<2;++i)
            images[original.variables[u][i]]=r.multiply(r.variable(core.variables[u][i]),core.inputs[i]);
        map_record(out,original,images);
        auto mapped=r.substitute(original.product,images);
        auto difference=c.domain(r.subtract(mapped,core.product));
        for(const auto& [id,q]:difference.cof)need(id<3 || q.empty(),"product error needs only old Booleanity");
        c.write(out,"raw_product_difference",difference,h*(prime+1));
        for(int i=0;i<2;++i){
            auto image=c.scale(difference,inputs[i]);
            c.plus(image,c.scale(c.ax(comp[i]),r.power(core.inputs[i],prime-2)));
            need(image.target==r.substitute(original.companions[i],images),"raw companion image");
            c.write(out,"raw_source_companion/"+std::to_string(i),image,2*(h*prime+prime-1));
        }
        for(const auto& [id,beta]:images)
            c.write(out,"raw_source_field/"+std::to_string(id),
                    c.domain(r.subtract(r.power(beta,prime),beta)),2*prime);
    }
    c.model(out,"zero_affine_inputs",{},true,core.product,1);
    c.model(out,"nonzero_input_forced_zero",{{0,1},{3,1}},true,core.product,0);
    auto boolP=r.subtract(r.power(core.product,2),core.product);
    int nonbool=r.residue((prime-1)*(prime-1)-(prime-1));
    c.model(out,"domains_alone_do_not_make_product_Boolean",{{0,1},{3,2}},false,boolP,nonbool);
    c.model(out,"same_core_fails_complement_input",{},true,
            r.multiply(r.subtract(one,inputs[0]),core.product),1);
    return c.certificates;
}
int high_map(std::ostream& out,int prime){
    Context c(prime);const auto& r=c.ring;int h=prime-1,k=2,fresh=3;
    auto one=r.constant(1),x=r.variable(0),y=r.variable(1),z=r.variable(2);
    std::vector<Polynomial> a={r.add(one,y),r.multiply(r.constant(2),z),r.constant(0)};
    auto f=r.add(r.multiply(x,a[0]),r.multiply(y,a[1]));
    auto original=make_block(r,{x,y,z},h,fresh);
    std::map<int,Polynomial> images;
    for(int u=0;u<h;++u)for(int i=0;i<3;++i)
        images[original.variables[u][i]]=r.multiply(r.constant(u+1),a[i]);
    auto value=r.substitute(original.product,images);
    need(value==r.subtract(one,r.power(f,prime-1)),"all nonzero factor rows");
    c.domains(3,3);c.header(out,"high_rank_identity_F"+std::to_string(prime));
    map_record(out,original,images);
    out<<"{\"record\":\"weight\",\"polynomial\":";write_json(out,f);
    out<<",\"degree\":"<<k<<",\"scope\":\"local algebraic identity; not the asymptotic rank threshold\"}\n";
    for(int i=0;i<3;++i){
        auto target=r.multiply(f,r.substitute(original.companions[i],images));
        c.write(out,"weighted_high_companion/"+std::to_string(i),c.domain(target),prime*k+1);
    }
    for(const auto& [id,beta]:images){
        auto target=r.multiply(f,r.subtract(r.power(beta,prime),beta));
        c.write(out,"weighted_coefficient_field/"+std::to_string(id),c.domain(target),(prime+1)*k);
    }
    auto single=r.multiply(r.multiply(f,x),r.subtract(one,f));
    c.model(out,"single_factor_binary_copy_fails",{{0,1},{1,1},{2,0}},true,single,r.residue(-2));
    return c.certificates;
}
int low_map(std::ostream& out){
    Context c(3);const auto& r=c.ring;int h=2,k=2,fresh=3;
    auto one=r.constant(1),x=r.variable(0),y=r.variable(1),z=r.variable(2);
    auto original=make_block(r,{x,y,r.multiply(r.constant(2),z)},h,fresh);
    std::map<int,Polynomial> images;
    std::vector<Polynomial> factors;
    for(int u=0;u<h;++u){
        auto partial=one;
        std::vector<Polynomial> beta(3);
        for(int t=0;t<3;++t){
            int index=u*3+t,j=index/2,alpha=index%2+1;
            r.accumulate(beta[j],r.multiply(r.constant(alpha),partial));
            auto factor=r.subtract(one,r.multiply(r.constant(alpha),original.inputs[j]));
            factors.push_back(factor);partial=r.multiply(partial,factor);
        }
        for(int j=0;j<3;++j){
            need(degree(beta[j])<=k,"packed coefficient degree");
            images[original.variables[u][j]]=beta[j];
        }
    }
    auto value=r.substitute(original.product,images),expected=one;
    for(const auto& g:original.inputs)expected=r.multiply(expected,r.subtract(one,r.power(g,2)));
    need(value==expected,"packed affine zero indicator");
    auto f=r.add(one,r.multiply(x,y));
    c.domains(3,3);c.header(out,"low_rank_packing_F3");map_record(out,original,images);
    out<<"{\"record\":\"weight\",\"polynomial\":";write_json(out,f);out<<",\"degree\":2}\n";
    for(int i=0;i<3;++i)
        c.write(out,"weighted_low_companion/"+std::to_string(i),
                c.domain(r.multiply(f,r.substitute(original.companions[i],images))),9);
    for(const auto& [id,beta]:images)
        c.write(out,"weighted_coefficient_field/"+std::to_string(id),
                c.domain(r.multiply(f,r.subtract(r.power(beta,3),beta))),8);
    auto incomplete=one;
    for(std::size_t i=0;i+1<factors.size();++i)incomplete=r.multiply(incomplete,factors[i]);
    c.model(out,"missing_nonzero_residue_factor",{{0,0},{1,0},{2,1}},true,
            r.multiply(f,r.multiply(original.inputs[2],incomplete)),1);
    return c.certificates;
}
int positive_common_bit(std::ostream& out,bool raw_transfer){
    Context c(3);const auto& r=c.ring;int h=2,s=2*h+1,fresh=3;
    auto one=r.constant(1),x=r.variable(0),y=r.variable(1),z=r.variable(2);
    auto core=make_block(r,{y,z},h,fresh);c.domains(3,fresh);
    std::vector<int> comp;
    for(int i=0;i<2;++i)comp.push_back(c.add("affine_core/"+std::to_string(i),core.companions[i]));
    std::vector<Polynomial> inputs;
    for(const auto& b:core.inputs)inputs.push_back(r.subtract(one,r.power(r.add(r.add(one,x),b),2)));
    auto V=r.add(r.subtract(one,x),r.multiply(x,core.product));
    c.header(out,"positive_MOD3_common_bit");
    out<<"{\"record\":\"source_profile\",\"original_weight\":6,\"cost\":"<<s
       <<",\"input_weight\":2,\"affine_core\":";write_block(out,core);
    out<<",\"value\":";write_json(out,V);out<<",\"actual_MOD_inputs\":";write_polynomials(out,inputs);
    out<<",\"prefixes\":";write_polynomials(out,core.prefix);out<<"}\n";
    Cert residual;
    std::vector<Cert> source_companions;
    for(int i=0;i<2;++i){
        auto e=c.ax(0);c.plus(e,c.ax(i+1));
        c.plus(residual,c.scale(e,core.prefix[i]));
    }
    auto target=r.subtract(one,V);
    for(int i=0;i<2;++i)r.accumulate(target,r.multiply(core.prefix[i],inputs[i]),-1);
    need(target==residual.target,"positive source prefix");
    c.write(out,"prefix_residual",residual,s);
    for(int i=0;i<2;++i){
        auto witness=c.scale(c.ax(comp[i]),x);
        auto coefficient=r.subtract(r.multiply(core.inputs[i],r.subtract(core.product,one)),V);
        c.plus(witness,c.scale(c.ax(0),coefficient));
        c.plus(witness,c.scale(c.ax(i+1),V),-1);
        need(witness.target==r.multiply(inputs[i],V),"positive source companion");
        source_companions.push_back(witness);
        c.write(out,"positive_companion/"+std::to_string(i),witness,s+2);
        c.write(out,"input_Booleanity/"+std::to_string(i),
                c.domain(r.subtract(r.power(inputs[i],2),inputs[i])),4);
    }
    auto boolV=c.scale(c.ax(0),r.power(r.subtract(core.product,one),2));
    c.plus(boolV,c.scale(product_boolean(c,core,comp),x));
    need(boolV.target==r.subtract(r.power(V,2),V),"positive source Booleanity");
    c.write(out,"value_Booleanity",boolV,2*s);
    if(raw_transfer){
        int original_fresh=fresh;
        auto original=make_block(r,inputs,h,original_fresh);
        std::map<int,Polynomial> images;
        for(int u=0;u<h;++u)for(int i=0;i<2;++i)
            images[original.variables[u][i]]=r.variable(core.variables[u][i]);
        map_record(out,original,images);
        auto difference=c.domain(r.subtract(r.substitute(original.product,images),V));
        for(const auto& [id,q]:difference.cof)need(id<3 || q.empty(),"common-bit error needs only old Booleanity");
        c.write(out,"raw_product_difference",difference,3*h);
        for(int i=0;i<2;++i){
            auto image=c.scale(difference,inputs[i]);c.plus(image,source_companions[i]);
            need(image.target==r.substitute(original.companions[i],images),"positive raw companion");
            c.write(out,"raw_source_companion/"+std::to_string(i),image,3*h+2);
        }
        for(const auto& [id,beta]:images)
            c.write(out,"raw_source_field/"+std::to_string(id),
                    c.domain(r.subtract(r.power(beta,3),beta)),3);
    }
    c.model(out,"common_bit_zero",{{0,0},{1,1},{3,1}},true,V,1);
    c.model(out,"common_bit_one_and_detected_child",{{0,1},{1,1},{3,1}},true,V,0);
    int m=5,zeros=0;
    for(int bits=0;bits<(1<<(m+1));++bits){
        int b0=bits&1;bool all=true;
        out<<"{\"record\":\"high_rank_positive_zero_set\",\"assignment\":[";
        for(int i=0;i<=m;++i){if(i)out<<',';out<<((bits>>i)&1);}
        out<<"],\"affine_values\":[";
        for(int i=1;i<=m;++i){if(i>1)out<<',';out<<r.residue(1+b0+((bits>>i)&1));}
        out<<"],\"MOD_inputs\":[";
        for(int i=1;i<=m;++i){
            int bi=(bits>>i)&1,L=r.residue(1+b0+bi),g=r.residue(1-L*L);
            need(g==b0*bi,"positive MOD3 Boolean identity");
            all&=g==0;if(i>1)out<<',';out<<g;
        }
        zeros+=int(all);out<<"],\"common_zero\":"<<(all?"true":"false")<<"}\n";
    }
    need(zeros==(1<<m)+1,"large common zero set");
    out<<"{\"record\":\"positive_rank_control\",\"independent_affine_forms\":"<<m
       <<",\"identity_minor_columns\":\"b1,...,b5\",\"Boolean_assignments\":64,"
         "\"common_zero_assignments\":"<<zeros<<",\"covered_by_common_bit_profile\":true}\n";
    return c.certificates;
}
int main(int argc,char** argv){
    try{
        need((argc==3 || argc==4) && std::string(argv[1])=="--out",
             "usage: --out NEW_PATH [--raw-transfer]");
        bool raw_transfer=argc==4;
        if(raw_transfer)need(std::string(argv[3])=="--raw-transfer","raw transfer flag");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");
        out<<"{\"record\":\"schema\",\"version\":1,\"polynomials\":\"[coefficient,[variable ids with repetitions]]\","
             "\"certificates\":\"ordinary target=sum(cofactor*axiom), field arithmetic in current case\","
             "\"scope\":\"local affine-map and actual MOD-profile identities, not a finite PHP lower bound\"}\n";
        int count=0;
        for(int p:{3,5}){count+=negative_mod_profile(out,p,raw_transfer);count+=high_map(out,p);}
        count+=low_map(out);count+=positive_common_bit(out,raw_transfer);
        out<<"{\"record\":\"summary\",\"cases\":6,\"NS_certificates\":"<<count<<",\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<count<<" complete NS certificates in six cases; all profiles and negative controls passed.\n";
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
