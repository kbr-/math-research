// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Accuracy-two MOD schema pruning, with explicit NS and Booleanity witnesses.
#include "domain_polynomial.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace domain_polynomial;
using Cofactors=std::vector<Polynomial>;
void need(bool ok,const std::string& message) {if(!ok)throw std::runtime_error(message);}
Cofactors scale(const Ring& ring,Cofactors a,const Polynomial& q) {
    for(auto& f:a)f=ring.multiply(f,q);
    return a;
}
Cofactors add(const Ring& ring,Cofactors a,const Cofactors& b) {
    need(a.size()==b.size(),"cofactor arity");
    for(size_t i=0;i<a.size();i++)ring.accumulate(a[i],b[i]);
    return a;
}
struct Value {Polynomial f;Cofactors boolean;int original_degree;std::string name;};
struct Context {
    Ring ring;std::ostream& out;std::vector<int> powers;
    std::vector<Polynomial> axioms;int next=0;int certificates=0;
    Context(int p,std::ostream& stream):ring(p,128),out(stream) {}
    Polynomial one()const{return ring.constant(1);}
    Polynomial boolean(const Polynomial& f)const{return ring.subtract(ring.multiply(f,f),f);}
    Cofactors certificate(const std::string& name,const Polynomial& target,
                          Cofactors cof,int bound) {
        need(cof.size()==axioms.size(),"certificate size");
        Polynomial sum;int used=0;
        for(size_t i=0;i<cof.size();i++) {
            auto term=ring.multiply(cof[i],axioms[i]);ring.accumulate(sum,term);
            used=std::max(used,degree(term));
        }
        need(sum==target,"identity: "+name);
        // Once the identity is checked, a zero target needs no nonzero summands.
        if(target.empty()) {cof.assign(axioms.size(),{});used=0;}
        need(used<=bound,"degree: "+name);
        need(ring.add(sum,one())!=target,"corrupted certificate accepted");
        out<<"{\"record\":\"certificate\",\"name\":\""<<name<<"\",\"target\":";
        write_json(out,target);out<<",\"cofactors\":";write_polynomials(out,cof);
        out<<",\"degree\":"<<used<<",\"bound\":"<<bound
           <<",\"corruption_rejected\":true}\n";
        certificates++;return cof;
    }
    Cofactors domain_certificate(const std::string& name,const Polynomial& target,int bound) {
        auto proof=domain_reduce(ring,target,powers);verify_reduction(ring,target,powers,proof);
        need(proof.remainder.empty(),"domain remainder: "+name);
        proof.coefficients.resize(axioms.size());
        return certificate(name,target,proof.coefficients,bound);
    }
    Value domain_value(const std::string& name,const Polynomial& f,int original) {
        out<<"{\"record\":\"scalar\",\"name\":\""<<name<<"\",\"image\":";write_json(out,f);
        out<<",\"original_degree\":"<<original<<"}\n";
        return {f,domain_certificate(name+"_booleanity",boolean(f),2*degree(f)),original,name};
    }
    Value negate(const Value& a) {
        auto f=ring.subtract(one(),a.f);auto name="one_minus_"+a.name;
        need(boolean(f)==boolean(a.f),"negation Booleanity");
        out<<"{\"record\":\"expression\",\"name\":\""<<name
           <<"\",\"op\":\"one_minus\",\"argument\":\""<<a.name<<"\",\"image\":";
        write_json(out,f);out<<"}\n";
        return {f,a.boolean,a.original_degree,name};
    }
    int gate(const std::string& name,const std::vector<Value>& inputs,bool forward) {
        int delta=0;for(const auto& v:inputs)delta=std::max(delta,v.original_degree);
        int original=2*(delta+1);
        out<<"{\"record\":\"source_gate\",\"name\":\""<<name
           <<"\",\"accuracy\":2,\"mode\":\""<<(forward?"earlier_zero":"pack")
           <<"\",\"input_names\":[";
        for(size_t i=0;i<inputs.size();i++) {if(i)out<<',';out<<'"'<<inputs[i].name<<'"';}
        out<<"],\"original_input_degrees\":[";
        for(size_t i=0;i<inputs.size();i++) {if(i)out<<',';out<<inputs[i].original_degree;}
        out<<"],\"original_product_degree\":"<<original<<",\"coefficient_assignments\":[";
        bool comma=false;
        for(int u=0;u<2;u++)for(size_t i=0;i<inputs.size();i++) {
            int value=forward?(u==0):(u==int(i));
            auto c=ring.constant(value);need(ring.subtract(ring.power(c,ring.p),c).empty(),"field image");
            if(comma)out<<',';
            comma=true;
            out<<"{\"variable\":"<<next++<<",\"factor\":"<<u<<",\"coordinate\":"<<i
               <<",\"value\":"<<value<<'}';
        }
        out<<"],\"selected_field_images_zero\":true}\n";return original;
    }
    Value pack(const std::string& name,const Value& a,const Value& b) {
        int original=gate(name,{a,b},false);
        auto na=ring.subtract(one(),a.f),nb=ring.subtract(one(),b.f);
        auto f=ring.multiply(na,nb);
        out<<"{\"record\":\"gate_image\",\"name\":\""<<name<<"\",\"image\":";
        write_json(out,f);out<<"}\n";
        auto h=add(ring,scale(ring,a.boolean,ring.multiply(nb,nb)),scale(ring,b.boolean,na));
        h=certificate(name+"_booleanity",boolean(f),h,2*degree(f));
        certificate(name+"_companion_0",ring.multiply(a.f,f),
                    scale(ring,a.boolean,ring.subtract({},nb)),a.original_degree+original);
        certificate(name+"_companion_1",ring.multiply(b.f,f),
                    scale(ring,b.boolean,ring.subtract({},na)),b.original_degree+original);
        return {f,h,original,name};
    }
};
Polynomial quotient(Context& c) {
    auto& ring=c.ring;auto t=ring.variable(0),a=ring.variable(1),one=c.one();
    auto b=ring.power(t,ring.p-1),v=ring.power(ring.subtract(t,one),ring.p-1);
    auto m=ring.power(ring.subtract(ring.add(t,a),one),ring.p-1);
    auto numerator=ring.subtract(m,ring.add(ring.multiply(a,b),ring.multiply(ring.subtract(one,a),v)));
    auto proof=domain_reduce(ring,numerator,{ring.p,2});verify_reduction(ring,numerator,{ring.p,2},proof);
    need(proof.remainder.empty() && proof.coefficients[0].empty(),"interpolation needs only a^2-a");
    auto R=proof.coefficients[1];
    need(R.empty() || degree(R)<=ring.p-3,"interpolation quotient degree");
    if(ring.p==2)need(R.empty(),"binary interpolation must be an identity");
    c.out<<"{\"record\":\"interpolation_quotient\",\"formal_variables\":[\"t\",\"a\"],\"R\":";
    write_json(c.out,R);c.out<<",\"numerator\":";write_json(c.out,numerator);c.out<<"}\n";
    return R;
}
void run_case(std::ostream& out,int id,int p,int mode,int width=0) {
    // mode 0: t,a; 1: t=x^2+y, a=1-z; 2/3: constant a=0/1;
    // mode 4: t is field-valued, a is a retained accuracy-two ENS product.
    Context c(p,out);auto& ring=c.ring;auto one=c.one();
    out<<"{\"record\":\"case\",\"id\":"<<id<<",\"p\":"<<p<<",\"mode\":"<<mode
       <<",\"retained_width\":"<<width<<"}\n";
    Polynomial t,a;Block argument;bool retained=mode==4;
    if(retained) {
        c.powers.assign(width+1,2);c.powers[0]=p;c.next=width+1;
        std::vector<Polynomial> inputs;for(int i=1;i<=width;i++)inputs.push_back(ring.variable(i));
        argument=make_block(ring,inputs,2,c.next);c.powers.resize(c.next,p);
        t=ring.variable(0);a=argument.product;
    } else if(mode==1) {
        c.powers={p,p,2};c.next=3;
        t=ring.add(ring.power(ring.variable(0),2),ring.variable(1));
        a=ring.subtract(one,ring.variable(2));
    } else {
        c.powers={p,2};c.next=2;t=ring.variable(0);
        a=mode==2?Polynomial{}:mode==3?one:ring.variable(1);
    }
    for(size_t i=0;i<c.powers.size();i++) {
        auto x=ring.variable(int(i));c.axioms.push_back(ring.subtract(ring.power(x,c.powers[i]),x));
    }
    int companion_start=int(c.axioms.size());
    if(retained)c.axioms.insert(c.axioms.end(),argument.companions.begin(),argument.companions.end());
    out<<"{\"record\":\"retained_system\",\"domain_powers\":[";
    for(size_t i=0;i<c.powers.size();i++) {if(i)out<<',';out<<c.powers[i];}
    out<<"],\"axioms\":";write_polynomials(out,c.axioms);
    if(retained) {out<<",\"argument_block\":";write_block(out,argument);}
    out<<",\"t\":";write_json(out,t);out<<",\"a\":";write_json(out,a);out<<"}\n";
    Value av;
    if(retained) {
        Cofactors ha(c.axioms.size());
        for(int i=0;i<width;i++)ha[companion_start+i]=ring.subtract({},argument.prefix[i]);
        ha=c.certificate("a_booleanity",c.boolean(a),ha,2*degree(a));
        av={a,ha,degree(a),"a"};
    } else av=c.domain_value("a",a,degree(a));
    auto b=c.domain_value("b",ring.power(t,p-1),(p-1)*degree(t));
    auto cv=c.domain_value("c",ring.power(ring.subtract(t,one),p-1),(p-1)*degree(t));
    auto m=c.domain_value("m",ring.power(ring.subtract(ring.add(t,a),one),p-1),
                          (p-1)*std::max(degree(t),av.original_degree));
    auto l=c.pack("l",b,c.negate(av)),r=c.pack("r",cv,av);
    auto R=ring.substitute(quotient(c),{{0,t},{1,a}});
    auto error=normalizer_error(ring,{m.f,l.f,r.f},{one,one,one});
    need(error==ring.subtract({},ring.multiply(c.boolean(a),R)),"forward error identity");
    int forward_original=c.gate("forward",{m,l,r},true);
    auto zero=c.certificate("forward_zero",error,scale(ring,av.boolean,ring.subtract({},R)),degree(error));
    std::vector<Value> forward_inputs{m,l,r};
    for(size_t i=0;i<forward_inputs.size();i++)
        c.certificate("forward_companion_"+std::to_string(i),ring.multiply(forward_inputs[i].f,error),
                      scale(ring,zero,forward_inputs[i].f),forward_inputs[i].original_degree+forward_original);
    auto he=c.certificate("forward_booleanity",c.boolean(error),
                          scale(ring,zero,ring.subtract(error,one)),2*degree(error));
    Value forward{error,he,forward_original,"forward"};
    out<<"{\"record\":\"gate_image\",\"name\":\"forward\",\"image\":";write_json(out,error);
    out<<",\"specialized_R\":";write_json(out,R);out<<"}\n";
    if(!retained) {
        auto q=c.pack("q",l,r),reverse=c.pack("reverse",q,c.negate(m));
        auto z=c.pack("z",forward,reverse);auto F=ring.subtract(one,z.f);
        auto S=ring.add(R,ring.multiply(ring.subtract(one,b.f),ring.subtract(one,cv.f)));
        auto coef_a=ring.subtract(ring.multiply(ring.multiply(ring.subtract(one,error),m.f),S),R);
        auto cof=add(ring,scale(ring,av.boolean,coef_a),scale(ring,m.boolean,ring.subtract(error,one)));
        int bound=(4*p-2)*std::max({1,degree(t),degree(a)});
        c.certificate("full_axiom",F,cof,bound);
        out<<"{\"record\":\"full_schema_summary\",\"gates\":6,\"axiom_degree\":"<<degree(F)
           <<",\"axiom_bound\":"<<bound<<",\"original_outer_product_degree\":"<<z.original_degree<<"}\n";
    } else {
        auto consumer=c.pack("consumer",forward,cv);
        (void)consumer;
        for(int value:{0,1}) {
            std::map<int,int> point;for(int i=0;i<c.next;i++)point[i]=0;
            if(value==0) {point[1]=1;point[argument.variables[0][0]]=1;}
            for(const auto& f:c.axioms)need(ring.evaluate(f,point)==0,"retained system model");
            need(ring.evaluate(a,point)==value && ring.evaluate(error,point)==0,"retained value model");
            if(value==0)need(ring.evaluate(m.f,point)==1,"unit forward must fail direct m companion");
            out<<"{\"record\":\"retained_model\",\"argument_value\":"<<value
               <<",\"forward_value\":0,\"unit_forward_m_companion_value\":"<<ring.evaluate(m.f,point)
               <<",\"assignment\":[";
            for(int i=0;i<c.next;i++) {if(i)out<<',';out<<point[i];}
            out<<"]}\n";
        }
    }
    out<<"{\"record\":\"case_passed\",\"id\":"<<id<<",\"certificates\":"<<c.certificates<<"}\n";
}
void controls(std::ostream& out) {
    for(int p:{3,5,7}) {
        int count=0;
        for(int t=0;t<p && count==0;t++)for(int a=2;a<p && count==0;a++) {
            auto pow=[p](int x,int n){int v=1;x=(x%p+p)%p;for(int i=0;i<n;i++)v=v*x%p;return v;};
            int b=pow(t,p-1),c=pow(t-1,p-1),m=pow(t+a-1,p-1);
            int l=(a*(1-b))%p,r=((1-a)*(1-c)%p+p)%p;
            int error=((1-m-l-r)%p+p)%p;
            if(!error)continue;
            need(m*error%p || l*error%p || r*error%p,"nonzero error needs companion control");
            out<<"{\"record\":\"missing_argument_booleanity\",\"p\":"<<p<<",\"t\":"<<t
               <<",\"a\":"<<a<<",\"inputs\":["<<m<<','<<l<<','<<r<<"],\"error\":"<<error<<"}\n";
            count++;
        }
        need(count==1,"no missing-Booleanity control");
    }
    // t=0,a=0 gives m=1,r=0. A free Boolean l=1, instead of its packed
    // value zero, leaves a nonzero m*(1-m-l-r) in every prime field.
    for(int p:{2,3,5,7})out<<"{\"record\":\"missing_inner_packing\",\"p\":"<<p
        <<",\"t\":0,\"a\":0,\"free_l\":1,\"m\":1,\"r\":0,\"bad_companion\":"<<p-1<<"}\n";
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");
        auto parent=std::filesystem::path(argv[2]).parent_path();
        if(!parent.empty())std::filesystem::create_directories(parent);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"mod_accuracy_two\",\"seed\":null}\n";
        int id=0;for(int p:{2,3,5,7})run_case(out,id++,p,0);
        run_case(out,id++,3,1);run_case(out,id++,3,2);run_case(out,id++,3,3);
        for(int p:{2,3})for(int width:{1,2})run_case(out,id++,p,4,width);
        controls(out);
        out<<"{\"record\":\"summary\",\"full_schema_cases\":7,\"retained_argument_cases\":4,"
               "\"missing_hypothesis_controls\":7,\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failed");
        std::cout<<"Seven full MOD schemas, four retained arguments, and seven missing-hypothesis controls passed.\n";
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
