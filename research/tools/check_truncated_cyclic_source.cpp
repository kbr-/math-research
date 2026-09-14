// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Arbitrary cyclic lengths: local Taylor maps, weighted reduction, complete sources.
#include "binary_extension_polynomial.hpp"
#include "graded_reduction.hpp"
#include "ns_witness.hpp"
#include <boost/multiprecision/cpp_int.hpp>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <set>
using namespace domain_polynomial;
using namespace graded_reduction;
using namespace binary_extension;
using boost::multiprecision::cpp_int;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
bool binomial_odd(unsigned n,unsigned k){return (n&k)==k;}
int odd_part(int t){while(t%2==0)t/=2;return t;}
int field_modulus(int t){
    int u=odd_part(t),d=1;
    if(u>1){int residue=2%u;while(residue!=1){residue=2*residue%u;++d;need(d<=u,"finite order bound");}}
    const int moduli[5]={0,3,7,11,19};need(d<=4,"small exact local-field fixture");return moduli[d];
}
struct OldWitness {EP remainder;std::vector<EP> cofs;};
struct CyclicCase {
    Arithmetic a;int t,u,e,v;bool affine;static constexpr int Y=1024;
    std::vector<int> roots,frobenius,weights,selected_rows;
    Matrix left,right,left_inverse,right_inverse;
    std::vector<Polynomial> probes_a,probes_b,inputs,old_generators,local_products,divisors;
    std::map<int,EP> to_old,to_y;
    std::vector<std::map<int,int>> divisor_map;
    std::unique_ptr<ReductionMap> reduction;
    int extension_certificates=0,coordinate_certificates=0,binary_kernel_certificates=0,source_certificates=0,models=0;
    CyclicCase(int length,bool shifted):a(field_modulus(length)),t(length),u(odd_part(t)),e(t/u),v(2*t+1),affine(shifted){
        need(t>=2 && t<=12,"bounded cyclic fixture");
        for(int x=1;x<a.f.q;++x)if(a.f.power(x,u)==1)roots.push_back(x);
        need(int(roots.size())==u,"all distinct cyclic roots");
        for(int root:roots){auto it=std::find(roots.begin(),roots.end(),a.f.mul(root,root));need(it!=roots.end(),"Frobenius root permutation");frobenius.push_back(it-roots.begin());}
        for(int i=0;i<t;++i){
            auto A=a.r.variable(i),B=a.r.variable(t+i);
            if(affine && i==0){a.r.accumulate(A,a.r.variable(1));a.r.accumulate(B,a.r.variable(t+1));}
            if(affine && i<(u==1?2:3)){a.r.accumulate(A,a.r.constant(1));a.r.accumulate(B,a.r.constant(1));}
            probes_a.push_back(A);probes_b.push_back(B);
        }
        left.resize(t,std::vector<int>(t));right=left;
        for(int j=0;j<u;++j)for(int r=0;r<e;++r)for(int i=0;i<t;++i){
            int exponent=(t-i)%t;
            if(exponent>=r && binomial_odd(exponent,r))left[j*e+r][i]=a.f.power(roots[j],exponent-r);
            if(i>=r && binomial_odd(i,r))right[j*e+r][i]=a.f.power(roots[j],i-r);
        }
        left_inverse=invert(a.f,left);right_inverse=invert(a.f,right);
        std::vector<EP> A_inverse(t,a.zero()),B_inverse(t,a.zero());
        for(int row=0;row<t;++row){
            auto A=a.zero(),B=a.zero();
            for(int i=0;i<t;++i){
                a.add(A,a.binary(probes_a[i]),left[row][i]);a.add(B,a.binary(probes_b[i]),right[row][i]);
                a.add(A_inverse[row],a.variable(Y+i),left_inverse[row][i]);
                a.add(B_inverse[row],a.variable(Y+t+i),right_inverse[row][i]);
            }
            to_old[Y+row]=A;to_old[Y+t+row]=B;
        }
        for(int i=0;i<t;++i){
            auto A=A_inverse[i],B=B_inverse[i];
            if(affine && i==0){a.add(A,A_inverse[1]);a.add(B,B_inverse[1]);}
            if(affine && i>0 && i<(u==1?2:3)){a.add(A,a.constant(1));a.add(B,a.constant(1));}
            to_y[i]=A;to_y[t+i]=B;
        }
        to_old[Y+v-1]=a.variable(v-1);to_y[v-1]=a.variable(Y+v-1);
        for(int i=0;i<v;++i){
            need(a.substitute(to_y[i],to_old)==a.variable(i),"old affine-coordinate round trip");
            need(a.substitute(to_old[Y+i],to_y)==a.variable(Y+i),"local affine-coordinate round trip");
            auto x=a.r.variable(i);old_generators.push_back(a.r.subtract(a.r.power(x,2),x));
        }
        for(int i=0;i<t;++i){
            Polynomial g;for(int j=0;j<t;++j)a.r.accumulate(g,a.r.multiply(probes_a[j],probes_b[(j+i)%t]));
            inputs.push_back(g);
        }
        old_generators.insert(old_generators.end(),inputs.begin(),inputs.end());weights.resize(v);
        for(int i=0;i<v;++i){
            int next=i;
            if(i<2*t){int local=i%t,side=i<t?0:t;next=side+frobenius[local/e]*e+local%e;weights[i]=-(local%e)*(local%e);}
            auto x=a.r.variable(Y+i);divisors.push_back(a.r.subtract(a.r.power(x,2),a.r.variable(Y+next)));
            std::map<int,int> image;
            for(int r=0;r<v;++r){
                int scalar=0;
                for(int component=0;component<a.f.d;++component)if(to_old[Y+next][component].count(Monomial{r}))scalar|=1<<component;
                if(scalar)image[r]=scalar;
            }
            divisor_map.push_back(image);
        }
        for(int j=0;j<u;++j)for(int k=0;k<e;++k){
            Polynomial C;
            for(int r=0;r<=k;++r)a.r.accumulate(C,a.r.multiply(a.r.variable(Y+j*e+r),a.r.variable(Y+t+j*e+k-r)));
            local_products.push_back(C);
            if(k%2==0){
                selected_rows.push_back(j*e+k);divisors.push_back(C);std::map<int,int> image;
                for(int i=0;i<t;++i)if(right[j*e+k][i])image[v+i]=right[j*e+k][i];
                divisor_map.push_back(image);
            }
        }
        auto order=[w=weights](const Monomial& m,const Monomial& n){
            if(m.size()!=n.size())return m.size()<n.size();
            int wm=0,wn=0;for(int id:m)wm+=w.at(id-Y);for(int id:n)wn+=w.at(id-Y);
            return wm!=wn?wm<wn:monomial_less(m,n);
        };
        reduction=std::make_unique<ReductionMap>(a.r,divisors,order);
        std::set<int> used;
        for(unsigned j=0;j<selected_rows.size();++j){
            int row=selected_rows[j],local=(row/e)*e+(row%e)/2;
            need(reduction->heads[v+j]==Monomial({Y+local,Y+t+local}),"central weighted leading pair");
            need(used.insert(Y+local).second && used.insert(Y+t+local).second,"all weighted pairs disjoint");
        }
        need(selected_rows.size()==unsigned(u*((e+1)/2)),"full selected-pair count");
    }
    void extension_certificate(std::ostream& out,const std::string& name,const EP& target,
                               const std::vector<EP>& cofs,int budget){
        auto reconstructed=a.zero();int used=0;
        for(unsigned i=0;i<cofs.size();++i)if(!a.empty(cofs[i])){
            used=std::max(used,a.degree_of(cofs[i])+degree(old_generators[i]));
            a.add(reconstructed,a.multiply(cofs[i],a.binary(old_generators[i])));
        }
        need(reconstructed==target && used<=budget,"local-coordinate original-generator certificate");
        out<<"{\"record\":\"extension_NS_certificate\",\"t\":"<<t<<",\"name\":\""<<name<<"\",\"target\":";
        a.write(out,target);out<<",\"budget\":"<<budget<<",\"terms\":[";bool comma=false;
        for(unsigned i=0;i<cofs.size();++i)if(!a.empty(cofs[i])){
            if(comma)out<<',';
            comma=true;out<<"{\"axiom_id\":"<<i<<",\"cofactor\":";a.write(out,cofs[i]);out<<'}';
        }
        out<<"],\"witness_degree\":"<<used<<"}\n";++extension_certificates;
    }
    void setup_checks(std::ostream& out){
        out<<"{\"record\":\"local_cyclic_system\",\"t\":"<<t<<",\"odd_part\":"<<u<<",\"multiplicity\":"<<e
           <<",\"field_dimension\":"<<a.f.d<<",\"modulus_bits\":"<<a.f.modulus<<",\"affine_probes\":"<<(affine?"true":"false")
           <<",\"old_variables\":"<<v<<",\"coordinate_base_id\":"<<Y<<",\"roots\":[";
        for(int j=0;j<u;++j){if(j)out<<',';out<<roots[j];}out<<"],\"Frobenius_permutation\":[";
        for(int j=0;j<u;++j){if(j)out<<',';out<<frobenius[j];}out<<"],\"operand_A_probes\":";write_polynomials(out,probes_a);
        out<<",\"operand_B_probes\":";write_polynomials(out,probes_b);out<<",\"left_Taylor_matrix\":";matrix_json(out,left);
        out<<",\"right_and_output_Taylor_matrix\":";matrix_json(out,right);out<<",\"left_inverse\":";matrix_json(out,left_inverse);
        out<<",\"right_inverse\":";matrix_json(out,right_inverse);out<<",\"old_generators\":";write_polynomials(out,old_generators);
        out<<",\"coordinate_divisors\":";write_polynomials(out,divisors);out<<",\"all_local_products\":";write_polynomials(out,local_products);
        out<<",\"variable_weights\":[";for(int i=0;i<v;++i){if(i)out<<',';out<<weights[i];}
        out<<"],\"order\":\"ordinary degree, then sum of variable weights, then graded-lex tie break\","
             "\"division_priority\":\"domain relations, then selected even local products\","
             "\"scope\":\"kernel-construction generators, not additional old PHP axioms\"}\n";
        for(int i=0;i<v;++i){
            std::vector<EP> cofs(old_generators.size(),a.zero());
            for(const auto& [id,scalar]:divisor_map[i])cofs[id]=a.constant(scalar);
            extension_certificate(out,"domain_"+std::to_string(i),a.substitute(a.binary(divisors[i]),to_old),cofs,2);
        }
        for(int row=0;row<t;++row){
            std::vector<EP> cofs(old_generators.size(),a.zero());for(int i=0;i<t;++i)cofs[v+i]=a.constant(right[row][i]);
            extension_certificate(out,"local_product_"+std::to_string(row),a.substitute(a.binary(local_products[row]),to_old),cofs,2);
        }
        std::set<int> default_used;int default_matching=0;
        out<<"{\"record\":\"leading_pair_order_control\",\"t\":"<<t<<",\"weighted_heads\":[";
        for(unsigned j=0;j<selected_rows.size();++j){if(j)out<<',';write_json(out,Polynomial{{reduction->heads[v+j],1}});}
        out<<"],\"default_graded_lex_heads\":[";
        for(unsigned j=0;j<selected_rows.size();++j){
            auto head=leading(divisors[v+j]);
            if(j)out<<',';
            write_json(out,Polynomial{{head,1}});
            if(!default_used.count(head[0]) && !default_used.count(head[1])){
                ++default_matching;default_used.insert(head[0]);default_used.insert(head[1]);
            }
        }
        need(default_matching==u,"default heads form one star per root");
        out<<"],\"weighted_disjoint_pairs\":"<<selected_rows.size()<<",\"default_star_matching\":"<<default_matching
           <<",\"strict_improvement_over_default_order\":"<<(e>=4?"true":"false")<<",\"passed\":true}\n";
        if(e>=4){
            need(binomial_odd(2,2) && a.r.residue(2)==0,"Hasse coefficient versus ordinary derivative");
            out<<"{\"record\":\"Taylor_coefficient_control\",\"t\":"<<t<<",\"polynomial\":\"X^2\","
                 "\"epsilon_squared_coefficient\":1,\"ordinary_second_derivative\":0}\n";
        }
        if(a.f.d>1){
            bool found=false;
            for(int coordinate=0;coordinate<2*t && !found;++coordinate)for(int selected=-1;selected<v && !found;++selected){
                std::map<int,int> point;for(int i=0;i<v;++i)point[i]=int(i==selected);
                auto bad=a.square(to_old[Y+coordinate]);a.add(bad,to_old[Y+coordinate]);
                int value=a.evaluate(bad,point);
                if(value){
                    auto good=a.substitute(a.binary(divisors[coordinate]),to_old);need(!a.evaluate(good,point),"correct affine-domain control");
                    out<<"{\"record\":\"local_domain_control\",\"t\":"<<t<<",\"coordinate_index\":"<<coordinate
                       <<",\"old_point\":"<<(selected<0?0u:1u<<selected)<<",\"naive_Boolean_value\":"<<value
                       <<",\"correct_domain_value\":0}\n";found=true;
                }
            }
            need(found,"nonbinary local-coordinate control");
        }
    }
    void reduction_checks(std::ostream& out){
        bool full=t==4 || t==6 || t==8;std::set<Monomial> tests;
        if(full){for(auto m:monomials(v,3)){for(auto& id:m)id+=Y;tests.insert(m);}}
        else{
            tests.insert(Monomial{});
            for(int i=0;i<v;++i){
                tests.insert(Monomial{Y+i});tests.insert(Monomial{Y+i,Y+i,Y+i});
                for(unsigned j=0;j<selected_rows.size();++j){auto m=reduction->heads[v+j];m.push_back(Y+i);std::sort(m.begin(),m.end());tests.insert(m);}
            }
        }
        int index=0;
        for(const auto& m:tests){
            Polynomial original{{m,1}};auto normal=reduction->polynomial(original);auto target=a.r.subtract(original,normal.remainder);
            for(const auto& [term,c]:normal.remainder){
                need(c==1,"binary normal coefficient");Monomial quotient_m;
                for(const auto& head:reduction->heads)need(!quotient(term,head,quotient_m),"irreducible weighted normal monomial");
            }
            out<<"{\"record\":\"coordinate_NS_certificate\",\"t\":"<<t<<",\"index\":"<<index++<<",\"original\":";
            write_json(out,original);out<<",\"normal_remainder\":";write_json(out,normal.remainder);
            out<<",\"target\":";write_json(out,target);out<<",\"budget\":"<<m.size();
            ns_witness::write_terms(out,a.r,divisors,target,normal.coefficients,m.size(),"weighted coordinate reduction");out<<"}\n";++coordinate_certificates;
        }
        out<<"{\"record\":\"coordinate_reduction_scope\",\"t\":"<<t<<",\"complete_ordinary_basis_through_three\":"
           <<(full?"true":"false")<<",\"certificates\":"<<coordinate_certificates
           <<",\"other_cases\":\"constant, linear variables, cubes, and every selected-head times each variable\"}\n";
    }
    OldWitness reduce_old(const Polynomial& p){
        auto transformed=a.substitute(a.binary(p),to_y);EP rem=a.zero();std::vector<EP> cofs(divisors.size(),a.zero());
        for(int component=0;component<a.f.d;++component){
            auto normal=reduction->polynomial(transformed[component]);rem[component]=normal.remainder;
            for(const auto& [id,q]:normal.coefficients)cofs[id][component]=q;
        }
        OldWitness result{a.substitute(rem,to_old),std::vector<EP>(old_generators.size(),a.zero())};
        for(unsigned i=0;i<cofs.size();++i)if(!a.empty(cofs[i])){
            auto pulled=a.substitute(cofs[i],to_old);for(const auto& [id,scalar]:divisor_map[i])a.add(result.cofs[id],pulled,scalar);
        }
        return result;
    }
};
void complete_source(std::ostream& out,CyclicCase& c){
    need(c.affine && (c.t==4 || c.t==6),"complete affine source cases");auto& r=c.a.r;auto one=r.constant(1);
    int root_row=(c.u>1?1:0)*c.e;Polynomial selected;auto extra=r.variable(c.v-1);
    for(int i=0;i<c.t;++i)if(c.right[root_row][i]&1)r.accumulate(selected,c.inputs[i]);
    auto weight=r.multiply(extra,selected);need(!weight.empty() && degree(weight)==3,"nonzero old cubic source weight");
    for(const auto& [m,scalar]:weight){need(scalar==1 && m.size()==3,"homogeneous old multiplier");need(std::adjacent_find(m.begin(),m.end())==m.end(),"squarefree old multiplier");}
    auto witness=c.reduce_old(weight);need(c.a.empty(witness.remainder),"source multiplier in strict local kernel");
    c.extension_certificate(out,"selected_old_kernel",c.a.binary(weight),witness.cofs,3);
    std::map<int,Polynomial> binary_cofs;
    for(unsigned id=0;id<witness.cofs.size();++id)if(!witness.cofs[id][0].empty())binary_cofs[id]=witness.cofs[id][0];
    out<<"{\"record\":\"binary_kernel_NS_certificate\",\"t\":"<<c.t<<",\"target\":";write_json(out,weight);out<<",\"budget\":3";
    ns_witness::write_terms(out,r,c.old_generators,weight,binary_cofs,3,"strict cyclic kernel");out<<"}\n";++c.binary_kernel_certificates;
    int fresh=c.v;std::vector<Block> bottoms;std::map<int,Polynomial> phi;
    for(int i=0;i<c.t;++i)for(int j=0;j<c.t;++j){
        auto b=make_block(r,{r.subtract(one,c.probes_a[i]),r.subtract(one,c.probes_b[j])},1,fresh);
        phi[b.variables[0][0]]=one;phi[b.variables[0][1]]=c.probes_a[i];
        need(r.substitute(b.product,phi)==r.multiply(c.probes_a[i],c.probes_b[j]),"literal affine-probe bottom");bottoms.push_back(b);
    }
    std::vector<Polynomial> actual_inputs;
    for(int i=0;i<c.t;++i){Polynomial g;for(int j=0;j<c.t;++j)r.accumulate(g,bottoms[c.t*j+(j+i)%c.t].product);actual_inputs.push_back(g);}
    auto parent=make_block(r,actual_inputs,1,fresh);Polynomial error=weight;
    for(int i=0;i<c.t;++i){
        auto beta=binary_cofs[c.v+i];need(degree(beta)<=1,"descended parent coefficient degree");
        phi[parent.variables[0][i]]=beta;r.accumulate(error,r.multiply(beta,c.inputs[i]));
        need(r.substitute(parent.inputs[i],phi)==c.inputs[i],"actual cyclic sums preserved");
    }
    need(r.substitute(parent.product,phi)==r.add(r.subtract(one,weight),error),"complete original parent product");
    auto bools=std::vector<Polynomial>(c.old_generators.begin(),c.old_generators.begin()+c.v);
    out<<"{\"record\":\"complete_cyclic_source\",\"t\":"<<c.t<<",\"base_field\":2,\"old_variables\":"<<c.v
       <<",\"source_variables\":"<<fresh<<",\"old_Boolean_axioms\":";write_polynomials(out,bools);out<<",\"bottoms\":[";
    for(unsigned j=0;j<bottoms.size();++j){if(j)out<<',';write_block(out,bottoms[j]);}out<<"],\"parent\":";write_block(out,parent);
    out<<",\"simultaneous_map\":[";bool comma=false;
    for(const auto& [id,p]:phi){if(comma)out<<',';comma=true;out<<'['<<id<<',';write_json(out,p);out<<']';}
    out<<"],\"weight\":";write_json(out,weight);out<<",\"Boolean_correction\":";write_json(out,error);
    out<<",\"selected_local_output_row\":"<<root_row<<",\"row_by_old_variable\":[";
    for(int i=0;i<c.v;++i){if(i)out<<',';out<<(i<2*c.t?i%c.t:c.t);}
    out<<"],\"coefficient_degree\":1,\"weight_degree\":3,\"scope\":\"local complete binary source; not PHP\"}\n";
    auto certificate=[&](const std::string& name,const Polynomial& source,int budget){
        auto target=r.multiply(weight,r.substitute(source,phi));
        auto red=domain_reduce(r,target,std::vector<int>(c.v,2));verify_reduction(r,target,std::vector<int>(c.v,2),red);
        need(red.remainder.empty() && budget<=degree(source)+3,"complete weighted original-degree image");
        std::map<int,Polynomial> cofs;for(int i=0;i<c.v;++i)if(!red.coefficients[i].empty())cofs[i]=red.coefficients[i];
        out<<"{\"record\":\"source_NS_certificate\",\"t\":"<<c.t<<",\"name\":\""<<name<<"\",\"source_axiom\":";write_json(out,source);
        out<<",\"original_degree\":"<<degree(source)<<",\"weighted_transfer_ceiling\":"<<degree(source)+3<<",\"target\":";write_json(out,target);
        out<<",\"budget\":"<<budget;ns_witness::write_terms(out,r,bools,target,cofs,budget,name);out<<"}\n";++c.source_certificates;
    };
    for(int i=0;i<c.v;++i)certificate("old_"+std::to_string(i),bools[i],5);
    auto blocks=bottoms;blocks.push_back(parent);
    for(unsigned b=0;b<blocks.size();++b){
        for(unsigned i=0;i<blocks[b].companions.size();++i)certificate("companion_"+std::to_string(b)+"_"+std::to_string(i),
            blocks[b].companions[i],b==bottoms.size()?8:6);
        for(int id:blocks[b].variables[0])certificate("coefficient_"+std::to_string(id),r.subtract(r.power(r.variable(id),2),r.variable(id)),5);
    }
    need(c.source_certificates==c.v+4*c.t*c.t+2*c.t,"every original source axiom image");bool control=false;
    for(unsigned bits=0;bits<(1u<<c.v);++bits){
        std::map<int,int> point;for(int i=0;i<c.v;++i)point[i]=(bits>>i)&1;
        bool nonzero=r.evaluate(weight,point);for(const auto& [id,p]:phi)point[id]=r.evaluate(p,point);
        if(nonzero){
            for(const auto& b:blocks){
                int product_value=r.evaluate(b.product,point);
                for(const auto& g:b.inputs)need(!r.residue(product_value*r.evaluate(g,point)),"complete factorized source model");
                for(int id:b.variables[0])need(point[id]==0 || point[id]==1,"original binary coefficient equation");
            }
            out<<"{\"record\":\"conditional_cyclic_source_model\",\"t\":"<<c.t<<",\"old_point\":"<<bits<<",\"assignment\":[";
            for(int i=0;i<fresh;++i){if(i)out<<',';out<<point[i];}out<<"]}\n";++c.models;
        }else if(!control){
            int P=r.evaluate(parent.product,point);
            for(unsigned i=0;i<parent.inputs.size();++i)if(r.residue(P*r.evaluate(parent.inputs[i],point))){
                out<<"{\"record\":\"unweighted_cyclic_control\",\"t\":"<<c.t<<",\"old_point\":"<<bits<<",\"companion_index\":"<<i
                   <<",\"weight_value\":0,\"companion_value\":1,\"assignment\":[";
                for(int j=0;j<fresh;++j){if(j)out<<',';out<<point[j];}out<<"]}\n";control=true;break;
            }
        }
    }
    need(control && c.models==(c.t==4?64:1536),"nonvacuous full model enumeration and weight control");
}
cpp_int ceil_sqrt(const cpp_int& a){
    cpp_int lo=0,hi=1;while(hi*hi<a)hi<<=1;
    while(lo+1<hi){cpp_int mid=(lo+hi)/2;if(mid*mid>=a)hi=mid;else lo=mid;}
    need(hi*hi>=a && (hi-1)*(hi-1)<a,"exact integer root");return hi;
}
void parameter_checks(std::ostream& out){
    for(unsigned ell:{40u,64u,128u}){
        unsigned logell=0;while((1u<<logell)<ell)++logell;
        cpp_int n=cpp_int(1)<<ell,m=n+1,v=m*ell,M=n*n,D=cpp_int(ell)*ell*ell,t=v/2,u=t,e=1;
        while((u&1)==0){u>>=1;e<<=1;}
        cpp_int R=u*((e+1)/2),H=4*ell+2*logell+5,k=ceil_sqrt((v*v*H+R-1)/R),T=2*k+1,B=T*D+k;
        cpp_int num=m*(cpp_int(ell)*(ell-1)*(ell-2)/6)*k*(k-1)*(k-2),den=v*(v-1)*(v-2);
        cpp_int packing=16*(k-1),room=2*B+2*k-1;
        need(2*t<=v && 2*R>=t && 2*R<=v && k>=3 && 2*k<=v && R*k*k>=v*v*H && packing<n,"cyclic range/image/packing conditions");
        bool space=2*num<=den,board=room<=n;
        need(board==(ell>=64) && space==(ell>=64),"positive and negative cyclic domain/room controls");
        out<<"{\"record\":\"arbitrary_cyclic_parameters\",\"ell\":"<<ell<<",\"n\":\""<<n<<"\",\"v\":\""<<v
           <<"\",\"M\":\""<<M<<"\",\"D\":\""<<D<<"\",\"t\":\""<<t<<"\",\"odd_part\":\""<<u<<"\",\"multiplicity\":\""<<e
           <<"\",\"R\":\""<<R<<"\",\"H\":\""<<H<<"\",\"k\":\""<<k<<"\",\"T\":\""<<T<<"\",\"B\":\""<<B
           <<"\",\"epsilon_numerator\":\""<<num<<"\",\"epsilon_denominator\":\""<<den<<"\",\"packing_left\":\""<<packing
           <<"\",\"room_required\":\""<<room<<"\",\"range_image_packing_conditions\":true,\"domain_bound\":"<<(space?"true":"false")
           <<",\"old_degree_bound\":"<<(board?"true":"false")
           <<",\"scope\":\"integer inequalities only; multiplicative orders and field cardinalities are not instantiated\",\"passed\":true}\n";
    }
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");int ext=0,coord=0,kernel=0,source=0,models=0;
        out<<"{\"record\":\"schema\",\"version\":1,\"base_field\":2,\"polynomials\":\"[coefficient,[variable IDs with repetitions]]\","
             "\"extension_coefficients\":\"polynomial-basis bitmasks modulo the given binary polynomial\",\"large_integers\":\"exact decimal strings\"}\n";
        for(int t:{2,3,4,6,8,10,12}){
            CyclicCase c(t,t==4 || t==6);c.setup_checks(out);c.reduction_checks(out);
            if(c.affine)complete_source(out,c);
            ext+=c.extension_certificates;coord+=c.coordinate_certificates;kernel+=c.binary_kernel_certificates;source+=c.source_certificates;models+=c.models;
            out<<"{\"record\":\"cyclic_case_summary\",\"t\":"<<t<<",\"extension_NS_certificates\":"<<c.extension_certificates
               <<",\"coordinate_NS_certificates\":"<<c.coordinate_certificates<<",\"binary_kernel_NS_certificates\":"<<c.binary_kernel_certificates
               <<",\"source_NS_certificates\":"<<c.source_certificates<<",\"conditional_models\":"<<c.models<<",\"passed\":true}\n";
        }
        parameter_checks(out);need(ext==144 && coord==2321 && kernel==2 && source==250 && models==1600,"complete arbitrary-cyclic evidence totals");
        out<<"{\"record\":\"summary\",\"ordinary_NS_certificates\":"<<ext+coord+kernel+source
           <<",\"conditional_source_models\":"<<models<<",\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<"2717 exact NS certificates, seven local decompositions, and 1600 complete source models passed.\n";
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
