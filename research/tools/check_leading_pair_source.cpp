// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact all-prime shared-tail reductions and complete actual-source maps.
#include "graded_reduction.hpp"
#include "ns_witness.hpp"
#include <boost/multiprecision/cpp_int.hpp>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <set>
using namespace domain_polynomial;
using namespace graded_reduction;
using boost::multiprecision::cpp_int;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
void point_json(std::ostream& out,const std::map<int,int>& point,int end){
    out<<'[';
    for(int i=0;i<end;++i){if(i)out<<',';out<<point.at(i);}
    out<<']';
}
struct Fixture {
    Ring r;int count=0,delta,T;
    std::vector<Polynomial> boolean,inputs;
    Fixture(int p):r(p,100),delta(3*(p-1)),T(delta-2){
        for(int i=0;i<12;++i){auto x=r.variable(i);boolean.push_back(r.subtract(r.power(x,2),x));}
        for(int i=0;i<3;++i){
            auto g=r.multiply(r.variable(i),r.variable(3+i));
            for(int j=0;j<3;++j)r.accumulate(g,r.multiply(r.variable(6+j),r.variable(9+(j+i)%3)));
            inputs.push_back(g);
        }
    }
    void certificate(std::ostream& out,const std::vector<Polynomial>& axioms,
                     const std::string& system,const std::string& name,const Polynomial& target,
                     const std::map<int,Polynomial>& cof,int budget,const Polynomial* source=nullptr){
        out<<"{\"record\":\"NS_certificate\",\"field\":"<<r.p<<",\"system\":\""<<system
           <<"\",\"name\":\""<<name<<"\",\"target\":";write_json(out,target);
        out<<",\"budget\":"<<budget;
        if(source){
            int ceiling=T*degree(*source)+delta;
            need(budget<=ceiling,"complete original-degree ledger");
            out<<",\"source_axiom\":";write_json(out,*source);
            out<<",\"original_degree\":"<<degree(*source)<<",\"weighted_transfer_ceiling\":"<<ceiling;
        }
        ns_witness::write_terms(out,r,axioms,target,cof,budget,name);out<<"}\n";++count;
    }
    void bool_certificate(std::ostream& out,const std::string& name,const Polynomial& target,
                          int budget,const Polynomial* source=nullptr){
        std::vector<int> powers(12,2);auto red=domain_reduce(r,target,powers);
        verify_reduction(r,target,powers,red);need(red.remainder.empty(),"old Boolean certificate");
        std::map<int,Polynomial> cof;
        for(int i=0;i<12;++i)if(!red.coefficients[i].empty())cof[i]=red.coefficients[i];
        certificate(out,boolean,"old_Boolean",name,target,cof,budget,source);
    }
};
int row_degree(const Polynomial& f){
    const int rows[12]={0,0,2,1,2,2,0,0,0,1,1,1};int result=0;
    for(const auto& [m,c]:f){
        (void)c;int counts[3]={};for(int id:m)++counts[rows[id]];
        result=std::max(result,*std::max_element(counts,counts+3));
    }
    return result;
}
int field_checks(std::ostream& out,int p){
    Fixture c(p);auto& r=c.r;auto one=r.constant(1);auto x=[&](int i){return r.variable(i);};
    auto divisors=c.boolean;divisors.insert(divisors.end(),c.inputs.begin(),c.inputs.end());
    ReductionMap reducer(r,divisors);
    for(int i=0;i<3;++i)need(reducer.heads[12+i]==Monomial({i,3+i}),"private leading pair");
    out<<"{\"record\":\"normal_map_system\",\"field\":"<<p<<",\"old_variables\":12,\"divisors\":";
    write_polynomials(out,divisors);
    out<<",\"order\":\"graded lexicographic; lower variable ID has higher priority\","
         "\"division_priority\":\"Boolean divisors then actual quadratic inputs, in listed order\","
         "\"scope\":\"kernel construction only; quadratic inputs are not old PHP axioms\"}\n";
    auto basis=monomials(12,3);need(basis.size()==455,"ordinary filtered basis count");
    std::set<Monomial> normal_monomials;
    for(unsigned i=0;i<basis.size();++i){
        Polynomial original{{basis[i],1}};auto normal=reducer.polynomial(original);
        for(const auto& [m,coefficient]:normal.remainder){
            (void)coefficient;Monomial q;
            for(const auto& head:reducer.heads)need(!quotient(m,head,q),"irreducible remainder monomial");
            normal_monomials.insert(m);
        }
        out<<"{\"record\":\"basis_reduction\",\"field\":"<<p<<",\"index\":"<<i<<",\"original\":";
        write_json(out,original);out<<",\"normal_remainder\":";write_json(out,normal.remainder);out<<"}\n";
        c.certificate(out,divisors,"normal_map","basis_"+std::to_string(i),
                      r.subtract(original,normal.remainder),normal.coefficients,basis[i].size());
    }
    need(normal_monomials.size()==266,"normal-space count through three");
    out<<"{\"record\":\"normal_space\",\"field\":"<<p<<",\"dimension\":266,\"monomials\":[";
    bool comma=false;
    for(const auto& m:normal_monomials){
        if(comma)out<<',';
        comma=true;write_json(out,Polynomial{{m,1}});
    }
    out<<"],\"scope\":\"reduction-image space; no exact functional quotient assertion\"}\n";
    auto f=r.multiply(x(1),c.inputs[0]);auto normal=reducer.polynomial(f);
    need(normal.remainder.empty() && degree(f)==3 && row_degree(f)==2,"row-cap-two kernel");
    c.certificate(out,divisors,"normal_map","shared_tail_kernel",f,normal.coefficients,3);
    std::vector<Polynomial> cofs(3);
    for(const auto& [id,a]:normal.coefficients){
        if(id<12)need(a.empty(),"fixture has literal kernel membership");
        else cofs[id-12]=a;
    }
    need(cofs[0]==x(1) && cofs[1].empty() && cofs[2].empty(),"extracted actual-input coefficients");
    auto F=r.power(f,p-1);auto red=domain_reduce(r,F,std::vector<int>(12,2));
    verify_reduction(r,F,std::vector<int>(12,2),red);auto H=red.remainder;
    need(!H.empty() && row_degree(H)<=2*(p-1),"nonzero Booleanized power and row cap");
    need(degree(H)==(p==2?3:p==3?5:9) && row_degree(H)==(p==2?2:p==3?3:5),"odd-prime row-growth control");
    c.bool_certificate(out,"power_Booleanization",r.subtract(F,H),c.delta);
    out<<"{\"record\":\"power_control\",\"field\":"<<p<<",\"kernel\":";write_json(out,f);
    out<<",\"weight\":";write_json(out,F);out<<",\"Boolean_weight\":";write_json(out,H);
    out<<",\"row_by_variable\":[0,0,2,1,2,2,0,0,0,1,1,1],\"kernel_row_degree\":2,\"power_degree\":"
       <<degree(H)<<",\"power_row_degree\":"<<row_degree(H)<<",\"allowed_row_degree\":"<<2*(p-1)<<"}\n";
    int fresh=12;std::vector<Block> bottoms;std::map<std::pair<int,int>,unsigned> by_pair;
    std::map<int,Polynomial> phi;
    auto bottom=[&](int left,int right){
        std::pair<int,int> key{left,right};auto found=by_pair.find(key);
        if(found!=by_pair.end())return found->second;
        auto b=make_block(r,{r.subtract(one,x(left)),r.subtract(one,x(right))},1,fresh);
        phi[b.variables[0][0]]=one;phi[b.variables[0][1]]=x(left);
        need(r.substitute(b.product,phi)==r.multiply(x(left),x(right)),"literal bottom product");
        unsigned id=bottoms.size();bottoms.push_back(b);by_pair[key]=id;return id;
    };
    std::vector<Polynomial> source_inputs;
    for(int i=0;i<3;++i){
        auto input=bottoms[bottom(i,3+i)].product;
        for(int j=0;j<3;++j){unsigned id=bottom(6+j,9+(j+i)%3);r.accumulate(input,bottoms[id].product);}
        source_inputs.push_back(input);
    }
    need(bottoms.size()==12,"reused complete bottom registry");
    auto parent=make_block(r,source_inputs,1,fresh);
    for(int i=0;i<3;++i){
        phi[parent.variables[0][i]]=r.multiply(cofs[i],r.power(f,p-2));
        need(degree(phi[parent.variables[0][i]])<=c.T,"kernel coefficient degree");
        need(r.substitute(parent.inputs[i],phi)==c.inputs[i],"actual parent sum preserved");
    }
    need(fresh==39 && r.substitute(parent.product,phi)==r.subtract(one,F),"complete parent product");
    out<<"{\"record\":\"shared_tail_source_system\",\"field\":"<<p<<",\"old_variables\":12,"
         "\"source_variables\":"<<fresh<<",\"old_Boolean_axioms\":";write_polynomials(out,c.boolean);
    out<<",\"bottoms\":[";
    for(unsigned i=0;i<bottoms.size();++i){if(i)out<<',';write_block(out,bottoms[i]);}
    out<<"],\"parent\":";write_block(out,parent);out<<",\"summed_images\":";write_polynomials(out,c.inputs);
    out<<",\"simultaneous_map\":[";comma=false;
    for(const auto& [id,a]:phi){
        if(comma)out<<',';
        comma=true;out<<'['<<id<<',';write_json(out,a);out<<']';
    }
    out<<"],\"weight_degree\":"<<c.delta<<",\"coefficient_degree\":"<<c.T
       <<",\"scope\":\"complete local two-level source over old Booleanity; not a PHP instance\"}\n";
    int before=c.count;
    for(int i=0;i<12;++i)c.bool_certificate(out,"weighted_old_"+std::to_string(i),
        r.multiply(F,c.boolean[i]),c.delta+2,&c.boolean[i]);
    auto blocks=bottoms;blocks.push_back(parent);
    for(unsigned b=0;b<blocks.size();++b){
        bool is_parent=b==bottoms.size();
        for(unsigned i=0;i<blocks[b].companions.size();++i){
            const auto& source=blocks[b].companions[i];
            c.bool_certificate(out,"weighted_companion_"+std::to_string(b)+"_"+std::to_string(i),
                r.multiply(F,r.substitute(source,phi)),c.delta+(is_parent?c.T+4:3),&source);
        }
        for(int id:blocks[b].variables[0]){
            auto source=r.subtract(r.power(x(id),p),x(id));
            // Frobenius expansion preserves ordinary exponents, including non-Boolean coefficients.
            auto image=r.subtract(r.power(phi.at(id),p),phi.at(id));
            c.bool_certificate(out,"weighted_field_"+std::to_string(id),r.multiply(F,image),
                               c.delta+p*(is_parent?c.T:1),&source);
        }
    }
    need(c.count-before==66,"all weighted source images");
    int models=0;
    for(unsigned bits=0;bits<(1u<<12);++bits){
        std::map<int,int> point;for(int i=0;i<12;++i)point[i]=(bits>>i)&1;
        if(!r.evaluate(f,point))continue;
        need(r.evaluate(F,point)==1,"Fermat nonzero support");
        for(const auto& [id,a]:phi)point[id]=r.evaluate(a,point);
        for(const auto& b:blocks){
            for(const auto& g:b.companions)need(!r.evaluate(g,point),"complete conditional source model");
            for(int id:b.variables[0]){
                int value=1;for(int j=0;j<p;++j)value=r.residue(value*point[id]);
                need(value==point[id],"genuine coefficient field equation");
            }
        }
        out<<"{\"record\":\"conditional_source_model\",\"field\":"<<p<<",\"old_point\":"<<bits
           <<",\"assignment\":";point_json(out,point,fresh);out<<"}\n";++models;
    }
    need(models==(p==2?960:p==3?1304:1400),"complete support enumeration");
    std::map<int,int> counter;
    for(int i=0;i<12;++i)counter[i]=(9>>i)&1;
    auto unweighted=r.substitute(parent.companions[0],phi);
    need(!r.evaluate(F,counter) && r.evaluate(unweighted,counter)==1,"unweighted map must fail");
    out<<"{\"record\":\"unweighted_control\",\"field\":"<<p<<",\"old_point\":9,\"weight_value\":0,"
         "\"companion_value\":1,\"companion_image\":";write_json(out,unweighted);out<<"}\n";
    if(p!=2){
        for(int i=0;i<12;++i)counter[i]=(587>>i)&1;
        auto beta=phi.at(parent.variables[0][0]);int value=r.evaluate(beta,counter);
        auto bad=r.subtract(r.power(beta,2),beta),good=r.subtract(r.power(beta,p),beta);
        need(r.evaluate(F,counter)==1 && r.evaluate(bad,counter)!=0 && !r.evaluate(good,counter),
             "Boolean coefficient equation would be wrong");
        out<<"{\"record\":\"nonBoolean_coefficient_control\",\"field\":"<<p<<",\"old_point\":587,"
             "\"coefficient_id\":"<<parent.variables[0][0]<<",\"value\":"<<value
           <<",\"Boolean_equation_value\":"<<r.evaluate(bad,counter)<<",\"field_equation_value\":0}\n";
    }
    need(c.count==523,"per-field ordinary certificate count");
    out<<"{\"record\":\"field_summary\",\"field\":"<<p<<",\"NS_certificates\":"<<c.count
       <<",\"weighted_source_images\":66,\"conditional_models\":"<<models<<",\"passed\":true}\n";
    return c.count;
}
cpp_int power(cpp_int a,unsigned e){cpp_int r=1;while(e){if(e&1)r*=a;a*=a;e>>=1;}return r;}
cpp_int ceil_sqrt(const cpp_int& a){
    cpp_int lo=0,hi=1;while(hi*hi<a)hi<<=1;
    while(lo+1<hi){cpp_int mid=(lo+hi)/2;if(mid*mid>=a)hi=mid;else lo=mid;}
    need(hi*hi>=a && (hi-1)*(hi-1)<a,"exact ceiling square root");return hi;
}
void parameters(std::ostream& out){
    for(unsigned ell:{40u,64u,128u})for(int p:{2,3,5}){
        unsigned logell=0;while((1u<<logell)<ell)++logell;
        cpp_int n=cpp_int(1)<<ell,m=n+1,v=m*ell,M=n*n,D=power(cpp_int(ell),3);
        cpp_int H=3*ell+logell+4,R=v/4;
        cpp_int k=ceil_sqrt((v*v*H+R-1)/R),delta=(p-1)*k,T=2*(p-1)*(k+1)-1,B=T*D+delta;
        cpp_int eps_num=m*(cpp_int(ell)*(ell-1)*(ell-2)/6)*k*(k-1)*(k-2);
        cpp_int eps_den=v*(v-1)*(v-2),packing=power(cpp_int(4),2*(p-1))*(delta-1);
        cpp_int room=2*B+(power(cpp_int(2),2*(p-1))-2)*delta-1;
        bool range=R>=1 && 2*R<=v && k>=3 && 2*k<=v && D>=(p-1)*ell && D>=p && D>=5;
        bool image=R*k*k>=v*v*H,space=2*eps_num<=eps_den,cubes=packing<n,board=room<=n;
        need(range && image && space,"leading-pair range/image/domain premises");
        need(board==(ell>=64) && cubes==(ell>=64 || p!=5),"positive and negative finite room cases");
        out<<"{\"record\":\"leading_pair_parameters\",\"field\":"<<p<<",\"ell\":"<<ell
           <<",\"n\":\""<<n<<"\",\"v\":\""<<v<<"\",\"M\":\""<<M<<"\",\"D\":\""<<D
           <<"\",\"H\":\""<<H<<"\",\"R\":\""<<R<<"\",\"k\":\""<<k<<"\",\"delta\":\""<<delta
           <<"\",\"A\":"<<2*(p-1)<<",\"T\":\""<<T<<"\",\"B\":\""<<B<<"\",\"epsilon_numerator\":\""
           <<eps_num<<"\",\"epsilon_denominator\":\""<<eps_den<<"\",\"packing_left\":\""<<packing
           <<"\",\"room_required\":\""<<room<<"\",\"range\":true,\"image_bound\":true,\"domain_bound\":true,"
             "\"packing_bound\":"<<(cubes?"true":"false")<<",\"old_degree_bound\":"<<(board?"true":"false")
           <<",\"scope\":\"exact integer sufficient conditions; local algebra fixture is separate\",\"passed\":true}\n";
    }
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");
        out<<"{\"record\":\"schema\",\"version\":1,\"polynomials\":\"[coefficient,[variable IDs with repetitions]]\","
             "\"large_integers\":\"exact decimal strings\"}\n";
        int total=0;for(int p:{2,3,5})total+=field_checks(out,p);parameters(out);
        need(total==1569,"total certificate count");
        out<<"{\"record\":\"summary\",\"NS_certificates\":"<<total<<",\"conditional_models\":3664,\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<total<<" exact NS certificates, 3664 source models, and nine finite parameter cases passed.\n";
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
