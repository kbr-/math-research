// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Conjugate-coordinate reductions, binary descent, and complete source checks.
#include "binary_extension_polynomial.hpp"
#include "graded_reduction.hpp"
#include "ns_witness.hpp"
#include <boost/multiprecision/cpp_int.hpp>
#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
using namespace domain_polynomial;
using namespace graded_reduction;
using binary_field::SmallField;
using boost::multiprecision::cpp_int;
using namespace binary_extension;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
struct Witness {EP remainder;std::vector<EP> cofs;};
struct Case {
    Arithmetic a;int v;static constexpr int Y=64;Matrix moore,inverse;
    std::map<int,EP> to_y,to_old;std::vector<Polynomial> inputs,old_generators,divisors;
    std::vector<std::map<int,int>> divisor_map;std::unique_ptr<ReductionMap> reduction;
    int extension_certificates=0,binary_certificates=0;
    explicit Case(int modulus):a(modulus),v(2*a.f.d+1){
        int d=a.f.d;moore.resize(d,std::vector<int>(d));
        for(int j=0;j<d;++j)for(int r=0;r<d;++r)moore[j][r]=a.f.power(1<<r,1<<j);
        inverse=invert(a.f,moore);
        for(int j=0;j<d;++j){
            auto X=a.zero(),Z=a.zero(),x=a.zero(),z=a.zero();
            for(int r=0;r<d;++r){
                a.add(X,a.variable(r),moore[j][r]);a.add(Z,a.variable(d+r),moore[j][r]);
                a.add(x,a.variable(Y+r),inverse[j][r]);a.add(z,a.variable(Y+d+r),inverse[j][r]);
            }
            to_old[Y+j]=X;to_old[Y+d+j]=Z;to_y[j]=x;to_y[d+j]=z;
        }
        to_old[Y+v-1]=a.variable(v-1);to_y[v-1]=a.variable(Y+v-1);
        for(int i=0;i<v;++i){
            need(a.substitute(to_y[i],to_old)==a.variable(i),"old-coordinate round trip");
            need(a.substitute(to_old[Y+i],to_y)==a.variable(Y+i),"conjugate-coordinate round trip");
            auto x=a.r.variable(i);old_generators.push_back(a.r.subtract(a.r.power(x,2),x));
        }
        auto A=a.zero(),B=a.zero();
        for(int r=0;r<d;++r){a.add(A,a.variable(r),1<<r);a.add(B,a.variable(d+r),1<<r);}
        inputs=a.multiply(A,B);old_generators.insert(old_generators.end(),inputs.begin(),inputs.end());
        for(int i=0;i<v;++i){
            int next=i;
            if(i<d)next=(i+1)%d;else if(i<2*d)next=d+(i-d+1)%d;
            auto variable=a.r.variable(Y+i);divisors.push_back(a.r.subtract(a.r.power(variable,2),a.r.variable(Y+next)));
            std::map<int,int> image;
            if(i<2*d){
                int row=i%d,shift=i<d?0:d;
                for(int r=0;r<d;++r)if(moore[(row+1)%d][r])image[shift+r]=moore[(row+1)%d][r];
            }else image[i]=1;
            divisor_map.push_back(image);
        }
        for(int j=0;j<d;++j){
            divisors.push_back(a.r.multiply(a.r.variable(Y+j),a.r.variable(Y+d+j)));
            std::map<int,int> image;for(int r=0;r<d;++r)if(moore[j][r])image[v+r]=moore[j][r];
            divisor_map.push_back(image);
        }
        reduction=std::make_unique<ReductionMap>(a.r,divisors);
    }
    Witness reduce(const Polynomial& old){
        auto transformed=a.substitute(a.binary(old),to_y);Witness result{a.zero(),std::vector<EP>(old_generators.size(),a.zero())};
        EP remainder=a.zero();std::vector<EP> coordinate_cofs(divisors.size(),a.zero());
        for(int coordinate=0;coordinate<a.f.d;++coordinate){
            auto normal=reduction->polynomial(transformed[coordinate]);remainder[coordinate]=normal.remainder;
            for(const auto& [id,p]:normal.coefficients)coordinate_cofs[id][coordinate]=p;
        }
        result.remainder=a.substitute(remainder,to_old);
        for(unsigned i=0;i<coordinate_cofs.size();++i)if(!a.empty(coordinate_cofs[i])){
            auto pulled=a.substitute(coordinate_cofs[i],to_old);
            for(const auto& [id,scalar]:divisor_map[i])a.add(result.cofs[id],pulled,scalar);
        }
        return result;
    }
    EP coordinate_remainder(const Polynomial& old){
        auto transformed=a.substitute(a.binary(old),to_y),result=a.zero();
        for(int coordinate=0;coordinate<a.f.d;++coordinate)result[coordinate]=reduction->polynomial(transformed[coordinate]).remainder;
        return result;
    }
    void extension_certificate(std::ostream& out,const std::string& name,const EP& target,
                               const std::vector<EP>& cofs,int budget){
        auto reconstructed=a.zero();int used=0;
        for(unsigned i=0;i<cofs.size();++i)if(!a.empty(cofs[i])){
            used=std::max(used,a.degree_of(cofs[i])+degree(old_generators[i]));
            a.add(reconstructed,a.multiply(cofs[i],a.binary(old_generators[i])));
        }
        need(reconstructed==target && used<=budget,"extension ordinary NS identity and degree");
        out<<"{\"record\":\"extension_NS_certificate\",\"field_dimension\":"<<a.f.d<<",\"name\":\""<<name
           <<"\",\"target\":";a.write(out,target);out<<",\"budget\":"<<budget<<",\"terms\":[";bool comma=false;
        for(unsigned i=0;i<cofs.size();++i)if(!a.empty(cofs[i])){
            if(comma)out<<',';
            comma=true;out<<"{\"axiom_id\":"<<i<<",\"cofactor\":";a.write(out,cofs[i]);out<<'}';
        }
        out<<"],\"witness_degree\":"<<used<<"}\n";++extension_certificates;
    }
    void binary_certificate(std::ostream& out,const std::string& name,const Polynomial& target,
                            const std::map<int,Polynomial>& cofs,int budget){
        out<<"{\"record\":\"binary_NS_certificate\",\"field_dimension\":"<<a.f.d<<",\"name\":\""<<name
           <<"\",\"target\":";write_json(out,target);out<<",\"budget\":"<<budget;
        ns_witness::write_terms(out,a.r,old_generators,target,cofs,budget,name);out<<"}\n";++binary_certificates;
    }
    std::map<int,Polynomial> descend(const std::vector<EP>& cofs) const{
        std::map<int,Polynomial> result;
        for(unsigned i=0;i<cofs.size();++i)if(!cofs[i][0].empty())result[i]=cofs[i][0];
        return result;
    }
    void write_setup(std::ostream& out){
        out<<"{\"record\":\"conjugate_system\",\"field_dimension\":"<<a.f.d<<",\"modulus_bits\":"<<a.f.modulus
           <<",\"old_variables\":"<<v<<",\"coordinate_base_id\":"<<Y<<",\"Moore_matrix\":";matrix_json(out,moore);
        out<<",\"inverse_matrix\":";matrix_json(out,inverse);out<<",\"old_generators\":";write_polynomials(out,old_generators);
        out<<",\"coordinate_divisors\":";write_polynomials(out,divisors);
        out<<",\"order\":\"graded lexicographic\",\"division_priority\":\"twisted square relations, then disjoint products\","
             "\"scope\":\"input equations construct kernels and are not added to the old PHP base\"}\n";
        for(unsigned i=0;i<divisors.size();++i){
            std::vector<EP> cofs(old_generators.size(),a.zero());
            for(const auto& [id,scalar]:divisor_map[i])cofs[id]=a.constant(scalar);
            extension_certificate(out,"divisor_pullback_"+std::to_string(i),a.substitute(a.binary(divisors[i]),to_old),cofs,2);
        }
        std::map<int,int> point;for(int i=0;i<v;++i)point[i]=int(i==1);
        if(a.f.d>=2){
            auto wrong=a.square(to_old[Y]);a.add(wrong,to_old[Y]);
            auto correct=a.substitute(a.binary(divisors[0]),to_old);
            need(a.evaluate(wrong,point)!=0 && a.evaluate(correct,point)==0,"naive conjugate Booleanity must fail");
            int x=1<<(a.f.d-1),y=2;
            need((a.f.mul(x,y)&1)==1 && (x&1)==0 && (y&1)==0,"projection is not multiplicative");
            out<<"{\"record\":\"conjugate_domain_control\",\"field_dimension\":"<<a.f.d<<",\"old_point\":2,"
                 "\"naive_Boolean_value\":"<<a.evaluate(wrong,point)<<",\"correct_domain_value\":0,"
                 "\"projection_product_control\":{\"a\":"<<x<<",\"b\":"<<y<<",\"project_ab\":1,\"project_a_project_b\":0}}\n";
        }
        need(a.f.trace(1)==(a.f.d%2),"trace of the unit");
        out<<"{\"record\":\"descent_unit_control\",\"field_dimension\":"<<a.f.d<<",\"chosen_projection_of_one\":1,"
             "\"trace_of_one\":"<<a.f.trace(1)<<",\"trace_can_preserve_target\":"<<(a.f.d%2?"true":"false")<<"}\n";
    }
};
using Bits=std::array<std::uint64_t,2>;
bool bit(const Bits& row,unsigned j){return (row[j/64]>>(j%64))&1;}
void set_bit(Bits& row,unsigned j){row[j/64]|=std::uint64_t(1)<<(j%64);}
void bit_rows(std::ostream& out,const std::vector<Bits>& rows,unsigned columns){
    out<<'[';
    for(unsigned i=0;i<rows.size();++i){
        if(i)out<<',';
        out<<'"';for(unsigned j=0;j<columns;++j)out<<bit(rows[i],j);out<<'"';
    }
    out<<']';
}
void unsigneds(std::ostream& out,const std::vector<unsigned>& v){
    out<<'[';for(unsigned i=0;i<v.size();++i){if(i)out<<',';out<<v[i];}out<<']';
}
Polynomial mask_polynomial(unsigned mask,int offset=0){
    Monomial m;for(unsigned i=0;i<32;++i)if((mask>>i)&1)m.push_back(offset+i);return {{m,1}};
}
struct Kernel {Polynomial f;Witness witness;std::map<int,Polynomial> binary_cofs;};
Kernel check_kernel(std::ostream& out,Case& c){
    std::vector<unsigned> columns,normal_masks;int d=c.a.f.d;
    for(unsigned mask=0;mask<(1u<<c.v);++mask){
        if(__builtin_popcount(mask)==3)columns.push_back(mask);
        if(__builtin_popcount(mask)>3)continue;
        bool normal=true;for(int j=0;j<d;++j)if(((mask>>j)&1) && ((mask>>(d+j))&1))normal=false;
        if(normal)normal_masks.push_back(mask);
    }
    need(columns.size()<=128,"binary kernel matrix width");
    std::map<unsigned,unsigned> normal_index;
    for(unsigned i=0;i<normal_masks.size();++i)normal_index[normal_masks[i]]=i;
    std::vector<Bits> matrix(d*normal_masks.size(),Bits{0,0});
    for(unsigned j=0;j<columns.size();++j){
        auto rem=c.coordinate_remainder(mask_polynomial(columns[j]));
        for(int coordinate=0;coordinate<d;++coordinate)for(const auto& [m,scalar]:rem[coordinate]){
            need(scalar==1,"binary remainder component");unsigned mask=0;
            for(int id:m){need(id>=Case::Y && id<Case::Y+c.v,"normal variable ID");mask|=1u<<(id-Case::Y);}
            need(__builtin_popcount(mask)==int(m.size()) && normal_index.count(mask),"normal remainder support");
            set_bit(matrix[d*normal_index.at(mask)+coordinate],j);
        }
    }
    auto reduced=matrix;std::vector<unsigned> pivots;
    for(unsigned j=0;j<columns.size() && pivots.size()<reduced.size();++j){
        unsigned rank=pivots.size(),i=rank;while(i<reduced.size() && !bit(reduced[i],j))++i;
        if(i==reduced.size())continue;
        std::swap(reduced[i],reduced[rank]);
        for(unsigned k=0;k<reduced.size();++k)if(k!=rank && bit(reduced[k],j)){
            reduced[k][0]^=reduced[rank][0];reduced[k][1]^=reduced[rank][1];
        }
        pivots.push_back(j);
    }
    std::vector<Bits> basis;
    for(unsigned j=0;j<columns.size();++j)if(std::find(pivots.begin(),pivots.end(),j)==pivots.end()){
        Bits vector{0,0};set_bit(vector,j);
        for(unsigned i=0;i<pivots.size();++i)if(bit(reduced[i],j))set_bit(vector,pivots[i]);
        for(const auto& row:matrix)need((__builtin_parityll(row[0]&vector[0])^__builtin_parityll(row[1]&vector[1]))==0,"binary kernel vector");
        basis.push_back(vector);
    }
    need(!basis.empty(),"auxiliary-bit times an input gives a nonzero kernel");
    Kernel selected;int best_score=-1,selected_index=-1;bool selected_error=false,selected_nonbinary=false;
    for(unsigned index=0;index<basis.size();++index){
        Polynomial f;for(unsigned j=0;j<columns.size();++j)if(bit(basis[index],j))c.a.r.accumulate(f,mask_polynomial(columns[j]));
        auto witness=c.reduce(f);need(c.a.empty(witness.remainder),"strict extension-map kernel");
        auto cofs=c.descend(witness.cofs);auto error=f;bool nonbinary=false;
        for(int j=0;j<d;++j)c.a.r.accumulate(error,c.a.r.multiply(cofs[c.v+j],c.inputs[j]));
        for(const auto& p:witness.cofs)for(int coordinate=1;coordinate<d;++coordinate)nonbinary=nonbinary || !p[coordinate].empty();
        int score=2*int(!error.empty())+int(nonbinary);
        if(score>best_score){best_score=score;selected={f,witness,cofs};selected_index=index;selected_error=!error.empty();selected_nonbinary=nonbinary;}
    }
    out<<"{\"record\":\"binary_kernel_matrix\",\"field_dimension\":"<<d<<",\"old_monomial_masks\":";
    unsigneds(out,columns);out<<",\"normal_coordinate_masks\":";unsigneds(out,normal_masks);
    out<<",\"row_encoding\":\"normal mask index times field dimension plus coefficient coordinate\",\"matrix\":";
    bit_rows(out,matrix,columns.size());out<<",\"rref\":";bit_rows(out,reduced,columns.size());
    out<<",\"pivots\":";unsigneds(out,pivots);out<<",\"kernel_basis\":";bit_rows(out,basis,columns.size());
    out<<",\"rank\":"<<pivots.size()<<",\"kernel_dimension\":"<<basis.size()<<",\"selected_basis_index\":"<<selected_index
       <<",\"selected_has_Boolean_correction\":"<<(selected_error?"true":"false")
       <<",\"selected_has_nonbinary_extension_cofactors\":"<<(selected_nonbinary?"true":"false")<<",\"passed\":true}\n";
    c.extension_certificate(out,"selected_kernel",c.a.binary(selected.f),selected.witness.cofs,3);
    c.binary_certificate(out,"selected_kernel",selected.f,selected.binary_cofs,3);
    return selected;
}
void check_reductions(std::ostream& out,Case& c){
    auto basis=monomials(c.v,3);
    need(basis.size()==unsigned((c.v+1)*(c.v+2)*(c.v+3)/6),"complete ordinary basis through three");
    for(unsigned i=0;i<basis.size();++i){
        Polynomial original{{basis[i],1}};auto w=c.reduce(original);auto target=c.a.binary(original);c.a.add(target,w.remainder);
        out<<"{\"record\":\"ordinary_basis_reduction\",\"field_dimension\":"<<c.a.f.d<<",\"index\":"<<i
           <<",\"original\":";write_json(out,original);out<<",\"old_remainder\":";c.a.write(out,w.remainder);out<<"}\n";
        c.extension_certificate(out,"basis_"+std::to_string(i),target,w.cofs,basis[i].size());
        c.binary_certificate(out,"basis_"+std::to_string(i),target[0],c.descend(w.cofs),basis[i].size());
    }
    if(c.a.f.d>=2){
        int d=c.a.f.d;auto rho=c.a.r.multiply(c.a.r.variable(Case::Y),c.divisors[c.v]);
        auto normal=c.reduction->polynomial(rho);
        auto expected=c.a.r.multiply(c.a.r.variable(Case::Y+1),c.a.r.variable(Case::Y+d));
        need(normal.remainder==expected && !expected.empty(),"map is not a full quotient normal form");
        std::vector<EP> cofs(c.old_generators.size(),c.a.zero());
        for(const auto& [id,scalar]:c.divisor_map[0])c.a.add(cofs[id],c.to_old[Case::Y+d],scalar);
        for(const auto& [id,scalar]:c.divisor_map[c.v])c.a.add(cofs[id],c.to_old[Case::Y],scalar);
        auto target=c.a.substitute(c.a.binary(expected),c.to_old);
        out<<"{\"record\":\"nonquotient_control\",\"field_dimension\":"<<d<<",\"coordinate_ideal_element\":";
        write_json(out,rho);out<<",\"nonzero_coordinate_remainder\":";write_json(out,expected);out<<"}\n";
        c.extension_certificate(out,"nonquotient_relation",target,cofs,3);
        c.binary_certificate(out,"nonquotient_relation",target[0],c.descend(cofs),3);
    }
}
void source_checks(std::ostream& out,Case& c,const Kernel& kernel){
    need(c.a.f.d==2 && c.v==5,"complete source fixture dimension");auto& r=c.a.r;auto one=r.constant(1);
    int fresh=c.v;std::vector<Block> bottoms;std::map<int,Polynomial> phi;
    for(int i=0;i<2;++i)for(int j=0;j<2;++j){
        auto b=make_block(r,{r.subtract(one,r.variable(i)),r.subtract(one,r.variable(2+j))},1,fresh);
        phi[b.variables[0][0]]=one;phi[b.variables[0][1]]=r.variable(i);
        need(r.substitute(b.product,phi)==r.multiply(r.variable(i),r.variable(2+j)),"literal field-source bottom");bottoms.push_back(b);
    }
    std::vector<Polynomial> actual_inputs;
    for(const auto& C:c.inputs){
        Polynomial g;
        for(const auto& [m,scalar]:C){
            need(scalar==1 && m.size()==2 && m[0]<2 && m[1]>=2 && m[1]<4,"actual bilinear input term");
            r.accumulate(g,bottoms[2*m[0]+m[1]-2].product);
        }
        actual_inputs.push_back(g);
    }
    auto parent=make_block(r,actual_inputs,1,fresh);Polynomial error=kernel.f;
    for(int i=0;i<2;++i){
        auto found=kernel.binary_cofs.find(c.v+i);auto beta=found==kernel.binary_cofs.end()?Polynomial{}:found->second;
        need(degree(beta)<=1,"degree-three descended kernel coefficient bound");phi[parent.variables[0][i]]=beta;
        r.accumulate(error,r.multiply(beta,c.inputs[i]));need(r.substitute(parent.inputs[i],phi)==c.inputs[i],"actual field-product coordinate sum");
    }
    need(fresh==15 && r.substitute(parent.product,phi)==r.add(r.subtract(one,kernel.f),error),"full descended parent product");
    std::vector<Polynomial> bools(c.old_generators.begin(),c.old_generators.begin()+c.v);
    out<<"{\"record\":\"descended_source_system\",\"field_dimension\":2,\"old_variables\":5,\"source_variables\":15,"
         "\"old_Boolean_axioms\":";write_polynomials(out,bools);out<<",\"bottoms\":[";
    for(unsigned i=0;i<bottoms.size();++i){if(i)out<<',';write_block(out,bottoms[i]);}
    out<<"],\"parent\":";write_block(out,parent);out<<",\"simultaneous_map\":[";bool comma=false;
    for(const auto& [id,p]:phi){if(comma)out<<',';comma=true;out<<'['<<id<<',';write_json(out,p);out<<']';}
    out<<"],\"weight\":";write_json(out,kernel.f);out<<",\"Boolean_correction\":";write_json(out,error);
    out<<",\"row_by_variable\":[0,1,0,1,2],\"coefficient_degree\":1,\"weight_degree\":3,"
         "\"scope\":\"complete local binary source from the selected strict kernel; not PHP\"}\n";
    int count=0;
    auto certificate=[&](const std::string& name,const Polynomial& source,int budget){
        auto target=r.multiply(kernel.f,r.substitute(source,phi));
        auto red=domain_reduce(r,target,std::vector<int>(c.v,2));verify_reduction(r,target,std::vector<int>(c.v,2),red);
        need(red.remainder.empty() && budget<=degree(source)+3,"weighted old-Boolean source image");
        std::map<int,Polynomial> cofs;for(int i=0;i<c.v;++i)if(!red.coefficients[i].empty())cofs[i]=red.coefficients[i];
        out<<"{\"record\":\"binary_source_NS_certificate\",\"field_dimension\":2,\"name\":\""<<name<<"\",\"target\":";
        write_json(out,target);out<<",\"source_axiom\":";write_json(out,source);
        out<<",\"original_degree\":"<<degree(source)<<",\"weighted_transfer_ceiling\":"<<degree(source)+3<<",\"budget\":"<<budget;
        ns_witness::write_terms(out,r,bools,target,cofs,budget,name);out<<"}\n";++count;++c.binary_certificates;
    };
    for(int i=0;i<c.v;++i)certificate("old_"+std::to_string(i),bools[i],5);
    auto blocks=bottoms;blocks.push_back(parent);
    for(unsigned b=0;b<blocks.size();++b){
        for(unsigned i=0;i<blocks[b].companions.size();++i)certificate("companion_"+std::to_string(b)+"_"+std::to_string(i),
            blocks[b].companions[i],b==bottoms.size()?8:6);
        for(int id:blocks[b].variables[0])certificate("coefficient_"+std::to_string(id),r.subtract(r.power(r.variable(id),2),r.variable(id)),5);
    }
    need(count==25,"all original source images");int models=0;bool counter_saved=false;
    for(unsigned bits=0;bits<32;++bits){
        std::map<int,int> point;for(int i=0;i<c.v;++i)point[i]=(bits>>i)&1;
        bool nonzero=r.evaluate(kernel.f,point);for(const auto& [id,p]:phi)point[id]=r.evaluate(p,point);
        if(nonzero){
            for(const auto& b:blocks){
                for(const auto& p:b.companions)need(!r.evaluate(p,point),"complete conditional field-source model");
                for(int id:b.variables[0])need(point[id]==0 || point[id]==1,"descended coefficient domain");
            }
            out<<"{\"record\":\"conditional_descended_source_model\",\"old_point\":"<<bits<<",\"assignment\":[";
            for(int i=0;i<fresh;++i){if(i)out<<',';out<<point[i];}out<<"]}\n";++models;
        }else if(!counter_saved){
            for(unsigned i=0;i<parent.companions.size();++i)if(r.evaluate(parent.companions[i],point)){
                out<<"{\"record\":\"descended_unweighted_control\",\"old_point\":"<<bits<<",\"companion_index\":"<<i
                   <<",\"weight_value\":0,\"companion_value\":1,\"assignment\":[";
                for(int j=0;j<fresh;++j){if(j)out<<',';out<<point[j];}out<<"]}\n";counter_saved=true;break;
            }
        }
    }
    need(models>0 && models<32 && counter_saved,"nonvacuous source weight and control");
    out<<"{\"record\":\"descended_source_summary\",\"weighted_source_images\":25,\"conditional_models\":"<<models<<",\"passed\":true}\n";
}
cpp_int ceil_sqrt(const cpp_int& a){
    cpp_int lo=0,hi=1;while(hi*hi<a)hi<<=1;
    while(lo+1<hi){cpp_int mid=(lo+hi)/2;if(mid*mid>=a)hi=mid;else lo=mid;}
    need(hi*hi>=a && (hi-1)*(hi-1)<a,"integer square-root ceiling");return hi;
}
void parameters(std::ostream& out){
    for(unsigned ell:{40u,64u,128u}){
        unsigned logell=0;while((1u<<logell)<ell)++logell;
        cpp_int n=cpp_int(1)<<ell,m=n+1,v=m*ell,M=n*n,D=cpp_int(ell)*ell*ell,R=v/2;
        cpp_int H=4*ell+2*logell+5,k=ceil_sqrt((v*v*H+R-1)/R),T=2*k+1,B=T*D+k;
        cpp_int num=m*(cpp_int(ell)*(ell-1)*(ell-2)/6)*k*(k-1)*(k-2),den=v*(v-1)*(v-2);
        cpp_int packing=16*(k-1),room=2*B+2*k-1;
        need(R>=1 && 2*R<=v && k>=3 && 2*k<=v && R*k*k>=v*v*H && 2*num<=den && packing<n,"field-source range/image/domain/packing conditions");
        bool board=room<=n;need(board==(ell>=64),"positive and negative field-source room checks");
        out<<"{\"record\":\"large_field_parameters\",\"ell\":"<<ell<<",\"n\":\""<<n<<"\",\"v\":\""<<v
           <<"\",\"M\":\""<<M<<"\",\"D\":\""<<D<<"\",\"R\":\""<<R<<"\",\"field_degree\":\""<<R
           <<"\",\"H\":\""<<H<<"\",\"k\":\""<<k<<"\",\"T\":\""<<T<<"\",\"B\":\""<<B
           <<"\",\"epsilon_numerator\":\""<<num<<"\",\"epsilon_denominator\":\""<<den<<"\",\"packing_left\":\""<<packing
           <<"\",\"room_required\":\""<<room<<"\",\"range_image_domain_packing_conditions\":true,\"old_degree_bound\":"
           <<(board?"true":"false")<<",\"scope\":\"exact integer bounds; field cardinality is never instantiated\",\"passed\":true}\n";
    }
}
void unital_descent_controls(std::ostream& out){
    int extension=0,binary=0;
    for(int modulus:{7,11,19}){
        Case c(modulus);c.write_setup(out);auto& r=c.a.r;
        auto extra=r.variable(c.v-1),target=r.multiply(extra,c.inputs[0]);
        std::vector<EP> cofs(c.old_generators.size(),c.a.zero());cofs[c.v]=c.a.binary(extra);
        // A nonbinary Koszul syzygy preserves this binary target and tests actual descent.
        c.a.add(cofs[0],c.a.binary(c.old_generators[1]),2);
        c.a.add(cofs[1],c.a.binary(c.old_generators[0]),2);
        need(!cofs[0][1].empty() && !cofs[1][1].empty(),"nonbinary source coefficients in the control");
        c.extension_certificate(out,"binary_target_nonbinary_witness",c.a.binary(target),cofs,4);
        c.binary_certificate(out,"unital_binary_target_descent",target,c.descend(cofs),3);
        Polynomial traced;
        for(unsigned id=0;id<cofs.size();++id){
            Polynomial coefficient;
            for(int j=0;j<c.a.f.d;++j)if(c.a.f.trace(1<<j))r.accumulate(coefficient,cofs[id][j]);
            r.accumulate(traced,r.multiply(coefficient,c.old_generators[id]));
        }
        need(traced==(c.a.f.d%2?target:Polynomial{}),"ordinary trace descends the target only in odd dimension");
        out<<"{\"record\":\"unital_binary_target_control\",\"field_dimension\":"<<c.a.f.d
           <<",\"binary_target\":";write_json(out,target);out<<",\"ordinary_trace_target\":";write_json(out,traced);
        out<<",\"target_preserved_by_chosen_projection\":true,\"ordinary_trace_preserves_target\":"
           <<(c.a.f.d%2?"true":"false")<<",\"extension_degree_budget\":4,\"binary_degree_budget\":3,\"passed\":true}\n";
        extension+=c.extension_certificates;binary+=c.binary_certificates;
    }
    need(extension==33 && binary==3,"focused unital-descent certificate totals");
    out<<"{\"record\":\"summary\",\"mode\":\"unital-descent-only\",\"extension_NS_certificates\":"<<extension
       <<",\"binary_NS_certificates\":"<<binary<<",\"passed\":true}\n";
}
int main(int argc,char** argv){
    try{
        bool focused=argc==4 && std::string(argv[3])=="--unital-descent-only";
        need((argc==3 || focused) && std::string(argv[1])=="--out","usage: --out NEW_PATH [--unital-descent-only]");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");int extension=0,binary=0;
        out<<"{\"record\":\"schema\",\"version\":1,\"polynomials\":\"[coefficient,[variable IDs with repetitions]]\","
             "\"extension_coefficients\":\"polynomial-basis bitmasks in the specified binary field\","
             "\"binary_coefficients\":\"zero or one\",\"large_integers\":\"exact decimal strings\"}\n";
        if(focused){
            unital_descent_controls(out);need(bool(out),"focused output write");
            std::cout<<"36 exact certificates verify unital descent of binary targets with nonbinary witnesses.\n";
            return 0;
        }
        for(int modulus:{3,7,11,19}){
            Case c(modulus);c.write_setup(out);check_reductions(out,c);auto kernel=check_kernel(out,c);
            if(c.a.f.d==2)source_checks(out,c,kernel);
            extension+=c.extension_certificates;binary+=c.binary_certificates;
            out<<"{\"record\":\"field_case_summary\",\"field_dimension\":"<<c.a.f.d
               <<",\"extension_NS_certificates\":"<<c.extension_certificates<<",\"binary_NS_certificates\":"<<c.binary_certificates<<",\"passed\":true}\n";
        }
        parameters(out);need(extension==457 && binary==448,"complete certificate totals");
        out<<"{\"record\":\"summary\",\"extension_NS_certificates\":"<<extension<<",\"binary_NS_certificates\":"<<binary<<",\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<extension+binary<<" exact NS certificates, complete binary kernel matrices, and source/descent controls passed.\n";
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
