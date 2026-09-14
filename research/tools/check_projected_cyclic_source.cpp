// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Projected cyclic inputs, affine intersections, and complete shared-weight sources.
#include "cyclic_coordinates.hpp"
#include "extension_reduction.hpp"
#include "ns_witness.hpp"
#include <boost/multiprecision/cpp_int.hpp>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <set>
using namespace domain_polynomial;
using namespace binary_extension;
using cyclic_coordinates::Coordinates;
using extension_reduction::ExtensionReduction;
using boost::multiprecision::cpp_int;
using Cof=std::map<int,Polynomial>;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
int binary_rank(const Ring& r,const std::vector<Polynomial>& rows){
    std::map<Monomial,Polynomial> basis;
    for(auto p:rows)while(!p.empty()){
        auto head=graded_reduction::leading(p);auto found=basis.find(head);
        if(found==basis.end()){basis[head]=p;break;}r.accumulate(p,found->second);
    }
    return basis.size();
}
void span_record(std::ostream& out,const Ring& r,const std::string& name,const std::vector<Polynomial>& H){
    std::vector<Polynomial> quadratic;
    for(const auto& p:H){Polynomial q;for(const auto& [m,c]:p)if(m.size()==2)q[m]=c;quadratic.push_back(q);}
    int full=binary_rank(r,H),rank=binary_rank(r,quadratic);auto unit=H;unit.push_back(r.constant(1));
    bool contains_unit=binary_rank(r,unit)==full;
    std::string regime=contains_unit?"unit":rank>=6?"high_quadratic":full-rank>=9?"high_affine":"low";
    need(regime==name,"intended source regime");
    out<<"{\"record\":\"input_span\",\"name\":\""<<name<<"\",\"inputs\":";write_polynomials(out,H);
    out<<",\"quadratic_rank\":"<<rank<<",\"affine_intersection_dimension\":"<<full-rank
       <<",\"contains_unit\":"<<(contains_unit?"true":"false")<<",\"k\":3,\"regime\":\""<<regime<<"\"}\n";
}
struct Pulled {EP remainder;std::vector<EP> cofs;};
struct Projection {
    Coordinates& g;Matrix U,local,tracking;std::vector<Polynomial> offsets,H,generators;
    std::vector<int> columns,pivots,selected;std::vector<EP> divisors;
    std::vector<std::map<int,int>> pullback;std::unique_ptr<ExtensionReduction> reduction;
    int extension_count=0,binary_count=0;
    Projection(Coordinates& geometry,Matrix projection,std::vector<Polynomial> affine)
        :g(geometry),U(std::move(projection)),offsets(std::move(affine)){
        int I=U.size();need(I>0 && int(offsets.size())==I,"projected input arity");
        local.resize(I,std::vector<int>(g.t));tracking.resize(I,std::vector<int>(I));
        for(int i=0;i<I;++i){
            need(int(U[i].size())==g.t,"projection width");Polynomial h=offsets[i];tracking[i][i]=1;
            for(int j=0;j<g.t;++j){
                need(U[i][j]==0 || U[i][j]==1,"binary source projection");
                if(U[i][j])g.a.r.accumulate(h,g.inputs[j]);
                for(int k=0;k<g.t;++k)local[i][k]^=g.a.f.mul(U[i][j],g.right_inverse[j][k]);
            }
            H.push_back(h);auto represented=g.a.substitute(g.a.binary(offsets[i]),g.to_y);
            for(int j=0;j<g.t;++j)g.a.add(represented,g.a.binary(g.local_products[j]),local[i][j]);
            need(represented==g.a.substitute(g.a.binary(h),g.to_y),"actual projected input and affine tail");
        }
        generators=g.boolean;generators.insert(generators.end(),H.begin(),H.end());
        for(int j=0;j<g.t;++j)columns.push_back(j);
        auto order=g.order();std::vector<Monomial> heads;
        for(const auto& C:g.local_products)heads.push_back(graded_reduction::leading(C,order));
        std::sort(columns.begin(),columns.end(),[&](int i,int j){return order(heads[j],heads[i]);});
        for(int col:columns){
            int rank=pivots.size(),row=rank;while(row<I && !local[row][col])++row;
            if(row==I)continue;
            std::swap(local[row],local[rank]);std::swap(tracking[row],tracking[rank]);
            int inv=g.a.f.power(local[rank][col],g.a.f.q-2);
            for(auto& x:local[rank])x=g.a.f.mul(x,inv);
            for(auto& x:tracking[rank])x=g.a.f.mul(x,inv);
            for(int i=0;i<I;++i)if(i!=rank && local[i][col]){
                int scalar=local[i][col];
                for(int j=0;j<g.t;++j)local[i][j]^=g.a.f.mul(scalar,local[rank][j]);
                for(int j=0;j<I;++j)tracking[i][j]^=g.a.f.mul(scalar,tracking[rank][j]);
            }
            pivots.push_back(col);
        }
        need(!pivots.empty(),"positive quadratic projection rank");std::vector<int> parity[2];
        for(unsigned row=0;row<pivots.size();++row)parity[(pivots[row]%g.e)%2].push_back(row);
        selected=parity[0].size()>=parity[1].size()?parity[0]:parity[1];
        for(int i=0;i<g.v;++i){divisors.push_back(g.a.binary(g.domain_divisors[i]));pullback.push_back(g.domain_pullback[i]);}
        std::set<int> used;
        for(int row:selected){
            auto polynomial=g.a.zero();
            for(int j=0;j<g.t;++j)g.a.add(polynomial,g.a.binary(g.local_products[j]),local[row][j]);
            for(int i=0;i<I;++i)g.a.add(polynomial,g.a.substitute(g.a.binary(offsets[i]),g.to_y),tracking[row][i]);
            auto head=extension_reduction::leading(g.a,polynomial,order);
            need(head==heads[pivots[row]] && head.size()==2,"projected pivot leading monomial");
            need(used.insert(head[0]).second && used.insert(head[1]).second,"parity-selected disjoint heads");
            divisors.push_back(polynomial);std::map<int,int> map;
            for(int i=0;i<I;++i)if(tracking[row][i])map[g.v+i]=tracking[row][i];
            pullback.push_back(map);
        }
        need(2*selected.size()>=pivots.size(),"half the projection rank survives");
        reduction=std::make_unique<ExtensionReduction>(g.a,divisors,order);
    }
    void ext_certificate(std::ostream& out,const std::string& name,const EP& target,const std::vector<EP>& cofs,int budget){
        auto reconstructed=g.a.zero();int used=0;
        for(unsigned i=0;i<cofs.size();++i)if(!g.a.empty(cofs[i])){
            used=std::max(used,g.a.degree_of(cofs[i])+degree(generators[i]));g.a.add(reconstructed,g.a.multiply(cofs[i],g.a.binary(generators[i])));
        }
        need(reconstructed==target && used<=budget,"projected extension NS witness");
        out<<"{\"record\":\"extension_NS_certificate\",\"t\":"<<g.t<<",\"name\":\""<<name<<"\",\"target\":";
        g.a.write(out,target);out<<",\"budget\":"<<budget<<",\"terms\":[";bool comma=false;
        for(unsigned i=0;i<cofs.size();++i)if(!g.a.empty(cofs[i])){
            if(comma)out<<',';
            comma=true;out<<"{\"axiom_id\":"<<i<<",\"cofactor\":";g.a.write(out,cofs[i]);out<<'}';
        }
        out<<"],\"witness_degree\":"<<used<<"}\n";++extension_count;
    }
    Cof descend(const std::vector<EP>& cofs){Cof result;for(unsigned i=0;i<cofs.size();++i)if(!cofs[i][0].empty())result[i]=cofs[i][0];return result;}
    void bin_certificate(std::ostream& out,const std::string& name,const Polynomial& target,const Cof& cofs,int budget){
        out<<"{\"record\":\"binary_NS_certificate\",\"t\":"<<g.t<<",\"name\":\""<<name<<"\",\"target\":";
        write_json(out,target);out<<",\"budget\":"<<budget;ns_witness::write_terms(out,g.a.r,generators,target,cofs,budget,name);out<<"}\n";++binary_count;
    }
    Pulled reduce(const Polynomial& old){
        auto normal=reduction->polynomial(g.a.substitute(g.a.binary(old),g.to_y));
        Pulled result{g.a.substitute(normal.remainder,g.to_old),std::vector<EP>(generators.size(),g.a.zero())};
        for(const auto& [divisor,p]:normal.coefficients){
            auto old_cof=g.a.substitute(p,g.to_old);for(const auto& [id,scalar]:pullback[divisor])g.a.add(result.cofs[id],old_cof,scalar);
        }
        return result;
    }
    void checks(std::ostream& out){
        out<<"{\"record\":\"projected_cyclic_system\",\"t\":"<<g.t<<",\"old_variables\":"<<g.v
           <<",\"auxiliary_field_dimension\":"<<g.a.f.d<<",\"modulus_bits\":"<<g.a.f.modulus
           <<",\"coordinate_base_id\":"<<Coordinates::Y<<",\"projection\":";matrix_json(out,U);out<<",\"offsets\":";write_polynomials(out,offsets);
        out<<",\"original_generators\":";write_polynomials(out,generators);out<<",\"left_Taylor_matrix\":";matrix_json(out,g.left);
        out<<",\"right_Taylor_matrix\":";matrix_json(out,g.right);out<<",\"left_inverse\":";matrix_json(out,g.left_inverse);
        out<<",\"right_inverse\":";matrix_json(out,g.right_inverse);out<<",\"row_reduced_local_coefficients\":";matrix_json(out,local);
        out<<",\"original_row_tracking\":";matrix_json(out,tracking);out<<",\"ordered_columns\":[";
        for(unsigned i=0;i<columns.size();++i){if(i)out<<',';out<<columns[i];}out<<"],\"pivots\":[";
        for(unsigned i=0;i<pivots.size();++i){if(i)out<<',';out<<pivots[i];}out<<"],\"selected_rows\":[";
        for(unsigned i=0;i<selected.size();++i){if(i)out<<',';out<<selected[i];}out<<"],\"coordinate_divisors\":[";
        for(unsigned i=0;i<divisors.size();++i){if(i)out<<',';g.a.write(out,divisors[i]);}out<<"],\"selected_heads\":[";
        for(unsigned i=g.v;i<divisors.size();++i){if(i>unsigned(g.v))out<<',';write_json(out,Polynomial{{reduction->heads[i],1}});}
        out<<"],\"scope\":\"projected inputs including affine tails; discarded cyclic outputs are not generators\"}\n";
        for(unsigned i=0;i<divisors.size();++i){
            std::vector<EP> cofs(generators.size(),g.a.zero());for(const auto& [id,scalar]:pullback[i])cofs[id]=g.a.constant(scalar);
            ext_certificate(out,"divisor_pullback_"+std::to_string(i),g.a.substitute(divisors[i],g.to_old),cofs,2);
        }
        auto basis=graded_reduction::monomials(g.v,3);
        for(unsigned i=0;i<basis.size();++i){
            Polynomial p{{basis[i],1}};auto old=reduce(p);auto target=g.a.binary(p);g.a.add(target,old.remainder);
            out<<"{\"record\":\"ordinary_basis_reduction\",\"t\":"<<g.t<<",\"index\":"<<i<<",\"original\":";write_json(out,p);
            out<<",\"old_remainder\":";g.a.write(out,old.remainder);out<<"}\n";
            ext_certificate(out,"basis_"+std::to_string(i),target,old.cofs,basis[i].size());
            bin_certificate(out,"basis_"+std::to_string(i),target[0],descend(old.cofs),basis[i].size());
        }
        out<<"{\"record\":\"projection_summary\",\"t\":"<<g.t<<",\"projection_rank\":"<<pivots.size()
           <<",\"selected_disjoint_pairs\":"<<selected.size()<<",\"ordinary_basis_size\":"<<basis.size()
           <<",\"extension_NS_certificates\":"<<extension_count<<",\"binary_NS_certificates\":"<<binary_count<<",\"passed\":true}\n";
    }
};
struct BooleanWitnesses {
    const Ring& r;std::vector<Polynomial> axioms;
    explicit BooleanWitnesses(const Ring& ring,int variables):r(ring){for(int i=0;i<variables;++i){auto x=r.variable(i);axioms.push_back(r.subtract(r.power(x,2),x));}}
    Cof direct(const Polynomial& p) const{
        auto red=domain_reduce(r,p,std::vector<int>(axioms.size(),2));verify_reduction(r,p,std::vector<int>(axioms.size(),2),red);
        need(red.remainder.empty(),"small Boolean certificate");Cof result;
        for(unsigned i=0;i<axioms.size();++i)if(!red.coefficients[i].empty())result[i]=red.coefficients[i];
        return result;
    }
    Cof scaled(const Cof& c,const Polynomial& factor) const{
        Cof result;for(const auto& [id,p]:c){auto q=r.multiply(p,factor);if(!q.empty())result[id]=q;}return result;
    }
    void add(Cof& a,const Cof& b) const{for(const auto& [id,p]:b)r.accumulate(a[id],p);}
    Polynomial product(const std::vector<Polynomial>& factors) const{
        auto p=r.constant(1);for(const auto& q:factors)p=r.multiply(p,q);return p;
    }
    Cof product_booleanity(const std::vector<Polynomial>& factors) const{
        Cof result;
        for(unsigned i=0;i<factors.size();++i){
            auto factor=r.constant(1);
            for(unsigned j=0;j<factors.size();++j)if(j!=i)factor=r.multiply(factor,j<i?r.power(factors[j],2):factors[j]);
            auto error=r.subtract(r.power(factors[i],2),factors[i]);add(result,scaled(direct(error),factor));
        }
        return result;
    }
};
struct Parent {
    std::string name;Block source;std::vector<Polynomial> H,beta;Polynomial mapped_product;
};
struct SourceWriter {
    const Ring& r;const BooleanWitnesses& b;std::ostream& out;int count=0;
    void write(const std::string& system,const std::string& name,const Polynomial& original,
               const Polynomial& image,const Polynomial& weight,const Cof& cofs,int declared_degree,int T,int budget){
        auto target=r.multiply(weight,image);int ceiling=T*declared_degree+degree(weight);
        need(budget<=ceiling,"source original-degree ceiling");
        out<<"{\"record\":\"source_NS_certificate\",\"system\":\""<<system<<"\",\"name\":\""<<name<<"\",\"source_axiom\":";
        write_json(out,original);out<<",\"source_polynomial_degree\":"<<degree(original)<<",\"original_degree_ceiling\":"<<declared_degree
           <<",\"weighted_transfer_ceiling\":"<<ceiling<<",\"target\":";write_json(out,target);out<<",\"budget\":"<<budget;
        ns_witness::write_terms(out,r,b.axioms,target,cofs,budget,name);out<<"}\n";++count;
    }
};
int companion_ceiling(const Block& block,int input){
    int maximum=0;for(const auto& g:block.inputs)maximum=std::max(maximum,degree(g));
    return degree(block.inputs[input])+block.accuracy*(maximum+1);
}
void degree_gap(std::ostream& out,const Ring& r,const std::vector<Polynomial>& bools,
                const Parent& parent,const Polynomial& weight,const std::vector<Polynomial>& cofs,int t){
    auto generators=bools;generators.insert(generators.end(),parent.H.begin(),parent.H.end());Cof witness;
    for(unsigned i=0;i<cofs.size();++i)if(!cofs[i].empty())witness[bools.size()+i]=cofs[i];
    out<<"{\"record\":\"affine_intersection_NS_certificate\",\"generators\":";write_polynomials(out,generators);
    out<<",\"target\":";write_json(out,weight);out<<",\"budget\":4";
    int used=ns_witness::write_terms(out,r,generators,weight,witness,4,"original quadratic-input degree");out<<"}\n";
    need(used==4,"affine pullback retains original degree four");Monomial detector{0,t+1,2*t};
    need(weight.count(detector) && weight.at(detector)==1,"nonzero separating target coefficient");
    std::string coefficient_row;
    for(const auto& g:generators){
        need(degree(g)==2,"all original input-system generators are quadratic");
        for(int variable=-1;variable<int(bools.size());++variable){
            auto multiple=variable<0?g:r.multiply(g,r.variable(variable));
            int value=multiple.count(detector)?multiple.at(detector):0;need(value==0,"all ordinary degree-three multiples annihilated");coefficient_row.push_back('0');
        }
    }
    out<<"{\"record\":\"NS_degree_three_separator\",\"target_monomial\":[0,"<<t+1<<','<<2*t
       <<"],\"target_value\":1,\"multiple_order\":\"generator order, then constant and old variables in increasing order\","
         "\"coefficient_row\":\""<<coefficient_row<<"\",\"scope\":\"normalized input-plus-Boolean ideal, not PHP\"}\n";
    std::vector<Polynomial> lines;std::vector<int> input_lines;
    auto line=[&](const std::string& op,const Polynomial& p,const std::vector<int>& predecessors,int variable,int axiom){
        need(degree(p)<=3,"ordinary PC degree three");
        out<<"{\"record\":\"PC_degree_three_line\",\"index\":"<<lines.size()<<",\"operation\":\""<<op<<"\",\"polynomial\":";write_json(out,p);
        out<<",\"predecessors\":[";for(unsigned i=0;i<predecessors.size();++i){if(i)out<<',';need(predecessors[i]<int(lines.size()),"earlier PC premise");out<<predecessors[i];}
        out<<']';if(variable>=0)out<<",\"variable\":"<<variable;if(axiom>=0)out<<",\"axiom_id\":"<<axiom;out<<"}\n";
        lines.push_back(p);return int(lines.size()-1);
    };
    for(unsigned i=0;i<parent.H.size();++i)input_lines.push_back(line("axiom",parent.H[i],{},-1,bools.size()+i));
    std::vector<int> products;
    for(int i=0;i<t;++i){
        auto A=r.add(lines[input_lines[0]],lines[input_lines[i+1]]);need(A==r.variable(i),"affine cancellation in PC");
        int Ai=line("linear_combination",A,{input_lines[0],input_lines[i+1]},-1,-1);
        auto partial=r.multiply(lines[Ai],r.variable(2*t));int Ai_extra=line("multiply_variable",partial,{Ai},2*t,-1);
        for(int j=0;j<t;++j)if((j-i+t)%t<6)products.push_back(line("multiply_variable",r.multiply(partial,r.variable(t+j)),{Ai_extra},t+j,-1));
    }
    Polynomial total;for(int id:products)r.accumulate(total,lines[id]);need(total==weight,"PC target reconstruction");
    line("linear_combination",total,products,-1,-1);
}
struct JointResult {int source_certificates=0,models=0,low_nonzero_products=0;};
JointResult joint_source(std::ostream& out,Projection& projection){
    auto& g=projection.g;auto& r=g.a.r;need(g.t==8 && g.v==17,"joint source fixture");
    BooleanWitnesses bools(r,g.v);SourceWriter writer{r,bools,out};auto one=r.constant(1),extra=r.variable(16);
    Polynomial selected;for(int i=0;i<6;++i)r.accumulate(selected,g.inputs[i]);auto weight=r.multiply(extra,selected);
    auto high_witness=projection.reduce(weight);need(g.a.empty(high_witness.remainder),"shared multiplier is a strict projected kernel");
    projection.ext_certificate(out,"shared_source_kernel",g.a.binary(weight),high_witness.cofs,3);
    auto high_cofs=projection.descend(high_witness.cofs);projection.bin_certificate(out,"shared_source_kernel",weight,high_cofs,3);
    int fresh=g.v;std::vector<Block> bottoms;std::map<int,Polynomial> phi;
    for(int i=0;i<g.t;++i)for(int j=0;j<g.t;++j){
        auto B=make_block(r,{r.subtract(one,r.variable(i)),r.subtract(one,r.variable(g.t+j))},1,fresh);
        phi[B.variables[0][0]]=one;phi[B.variables[0][1]]=r.variable(i);bottoms.push_back(B);
        need(r.substitute(B.product,phi)==r.multiply(r.variable(i),r.variable(g.t+j)),"reused bottom product");
    }
    std::vector<Polynomial> raw_cyclic;
    for(int i=0;i<g.t;++i){Polynomial p;for(int j=0;j<g.t;++j)r.accumulate(p,bottoms[g.t*j+(j+i)%g.t].product);raw_cyclic.push_back(p);}
    auto parent=[&](const std::string& name,const Matrix& U,const std::vector<Polynomial>& offsets){
        Parent result;result.name=name;std::vector<Polynomial> raw;
        for(unsigned i=0;i<U.size();++i){
            auto h=offsets[i],p=offsets[i];for(int j=0;j<g.t;++j)if(U[i][j]){r.accumulate(h,g.inputs[j]);r.accumulate(p,raw_cyclic[j]);}
            result.H.push_back(h);raw.push_back(p);
        }
        result.source=make_block(r,raw,1,fresh);result.beta.resize(U.size());return result;
    };
    std::vector<Parent> parents;
    parents.push_back(parent("high_quadratic",projection.U,projection.offsets));
    for(int i=0;i<6;++i)parents[0].beta[i]=high_cofs[g.v+i];
    Matrix affine_U(10,std::vector<int>(8));std::vector<Polynomial> affine_offsets(10);
    for(int i=0;i<10;++i){affine_U[i][0]=1;if(i)affine_offsets[i]=r.variable(i-1);}
    parents.push_back(parent("high_affine",affine_U,affine_offsets));
    for(int i=0;i<8;++i){
        Polynomial B;for(int j=0;j<8;++j)if((j-i+8)%8<6)r.accumulate(B,r.variable(8+j));
        parents[1].beta[i+1]=r.multiply(extra,B);r.accumulate(parents[1].beta[0],parents[1].beta[i+1]);
    }
    Matrix low_U(6,std::vector<int>(8));low_U[0][0]=low_U[2][0]=low_U[4][0]=1;low_U[1][1]=low_U[3][1]=low_U[4][1]=1;
    std::vector<Polynomial> low_offsets(6);low_offsets[2]=r.variable(14);low_offsets[3]=r.variable(15);
    parents.push_back(parent("low",low_U,low_offsets));
    std::vector<Polynomial> basis={r.variable(14),r.variable(15),g.inputs[0],g.inputs[1]},factors,prefixes;
    auto prefix=one;
    for(const auto& h:basis){prefixes.push_back(prefix);factors.push_back(r.subtract(one,h));prefix=r.multiply(prefix,factors.back());}
    parents[2].beta[0]=r.add(prefixes[0],prefixes[2]);parents[2].beta[1]=r.add(prefixes[1],prefixes[3]);
    parents[2].beta[2]=prefixes[0];parents[2].beta[3]=prefixes[1];
    Matrix unit_U(2,std::vector<int>(8));unit_U[0][0]=unit_U[1][0]=1;
    parents.push_back(parent("unit",unit_U,{Polynomial{},one}));parents[3].beta={one,one};
    int actual_T=1;
    for(auto& P:parents){
        span_record(out,r,P.name,P.H);
        auto product=one;
        for(unsigned i=0;i<P.H.size();++i){
            actual_T=std::max(actual_T,degree(P.beta[i]));phi[P.source.variables[0][i]]=P.beta[i];
            r.accumulate(product,r.multiply(P.beta[i],P.H[i]));
            need(r.substitute(P.source.inputs[i],phi)==P.H[i],"actual parent input including offsets");
        }
        P.mapped_product=product;need(r.substitute(P.source.product,phi)==product,"literal complete parent map");
    }
    need(actual_T==4 && fresh==169,"joint map degree and complete variable count");
    need(parents[0].mapped_product==r.subtract(one,weight) && parents[1].mapped_product==r.subtract(one,weight),"two high-regime products");
    need(parents[2].mapped_product==prefix && parents[3].mapped_product.empty(),"low and unit products");
    degree_gap(out,r,g.boolean,parents[1],weight,parents[1].beta,g.t);
    out<<"{\"record\":\"joint_source_system\",\"old_variables\":17,\"source_variables\":169,\"weight\":";write_json(out,weight);
    out<<",\"variable_image_degree\":4,\"old_Boolean_axioms\":";write_polynomials(out,g.boolean);out<<",\"bottoms\":[";
    for(unsigned i=0;i<bottoms.size();++i){if(i)out<<',';write_block(out,bottoms[i]);}out<<"],\"parents\":[";
    for(unsigned i=0;i<parents.size();++i){if(i)out<<',';out<<"{\"name\":\""<<parents[i].name<<"\",\"block\":";write_block(out,parents[i].source);out<<'}';}
    out<<"],\"simultaneous_map\":[";bool comma=false;
    for(const auto& [id,p]:phi){if(comma)out<<',';comma=true;out<<'['<<id<<',';write_json(out,p);out<<']';}
    out<<"],\"low_basis\":";write_polynomials(out,basis);out<<",\"low_prefixes\":";write_polynomials(out,prefixes);
    out<<",\"scope\":\"complete two-level local source; old PHP is not part of this fixture\"}\n";
    auto f_boolean=bools.direct(r.subtract(r.power(weight,2),weight));
    for(int i=0;i<g.v;++i)writer.write("joint","old_"+std::to_string(i),g.boolean[i],g.boolean[i],weight,
        Cof{{i,weight}},2,actual_T,5);
    for(unsigned b=0;b<bottoms.size();++b){
        int A=b/8,B=8+b%8;
        for(int i=0;i<2;++i){
            int variable=i?B:A;auto scalar=r.variable(i?A:B);
            auto image=r.multiply(scalar,r.subtract(r.power(r.variable(variable),2),r.variable(variable)));
            writer.write("joint","bottom_companion_"+std::to_string(b)+"_"+std::to_string(i),bottoms[b].companions[i],image,weight,
                         Cof{{variable,r.multiply(weight,scalar)}},companion_ceiling(bottoms[b],i),actual_T,6);
        }
        for(int id:bottoms[b].variables[0]){
            auto source=r.subtract(r.power(r.variable(id),2),r.variable(id));auto image=r.subtract(r.power(phi[id],2),phi[id]);
            writer.write("joint","bottom_field_"+std::to_string(id),source,image,weight,bools.scaled(bools.direct(image),weight),2,actual_T,5);
        }
    }
    std::vector<Cof> basis_booleans,prefix_booleans;
    for(const auto& h:basis)basis_booleans.push_back(bools.direct(r.subtract(r.power(h,2),h)));
    for(unsigned i=0;i<prefixes.size();++i)prefix_booleans.push_back(bools.product_booleanity(std::vector<Polynomial>(factors.begin(),factors.begin()+i)));
    std::vector<std::vector<int>> low_basis_rows={{2},{3},{0,2},{1,3},{2,3},{}};
    std::vector<Cof> low_companions(6),low_fields(6);
    for(int i=0;i<6;++i)for(int j:low_basis_rows[i]){
        std::vector<Polynomial> rest;for(int k=0;k<4;++k)if(k!=j)rest.push_back(factors[k]);
        bools.add(low_companions[i],bools.scaled(basis_booleans[j],bools.product(rest)));
    }
    low_fields[0]=prefix_booleans[0];bools.add(low_fields[0],prefix_booleans[2]);
    low_fields[1]=prefix_booleans[1];bools.add(low_fields[1],prefix_booleans[3]);low_fields[2]=prefix_booleans[0];low_fields[3]=prefix_booleans[1];
    for(unsigned b=0;b<parents.size();++b){auto& P=parents[b];
        for(unsigned i=0;i<P.H.size();++i){
            auto image=r.multiply(P.H[i],P.mapped_product);Cof cofs;
            if(b<2)cofs=bools.scaled(f_boolean,P.H[i]);else if(b==2)cofs=bools.scaled(low_companions[i],weight);
            int budget=image.empty()?0:(b<2?8:11);
            writer.write("joint",P.name+"_companion_"+std::to_string(i),P.source.companions[i],image,weight,cofs,companion_ceiling(P.source,i),actual_T,budget);
        }
        for(unsigned i=0;i<P.beta.size();++i){
            int id=P.source.variables[0][i];auto source=r.subtract(r.power(r.variable(id),2),r.variable(id));auto image=r.subtract(r.power(P.beta[i],2),P.beta[i]);
            Cof cofs=bools.scaled(b==2?low_fields[i]:bools.direct(image),weight);
            writer.write("joint",P.name+"_field_"+std::to_string(i),source,image,weight,cofs,2,actual_T,image.empty()?0:3+2*degree(P.beta[i]));
        }
    }
    need(writer.count==321,"all original joint-source axiom images");
    for(int i=0;i<6;++i){
        auto& P=parents[2];auto image=r.multiply(P.H[i],P.mapped_product);
        writer.write("low_unweighted","companion_"+std::to_string(i),P.source.companions[i],image,one,low_companions[i],companion_ceiling(P.source,i),actual_T,image.empty()?0:8);
        int id=P.source.variables[0][i];auto source=r.subtract(r.power(r.variable(id),2),r.variable(id));image=r.subtract(r.power(P.beta[i],2),P.beta[i]);
        writer.write("low_unweighted","field_"+std::to_string(i),source,image,one,low_fields[i],2,actual_T,image.empty()?0:2*degree(P.beta[i]));
    }
    JointResult result;result.source_certificates=writer.count;
    for(unsigned B=0;B<256;++B)if(__builtin_parity(B&63)){
        std::map<int,int> point;for(int i=0;i<g.v;++i)point[i]=0;point[0]=point[16]=1;
        for(int j=0;j<8;++j)point[8+j]=(B>>j)&1;
        need(r.evaluate(weight,point)==1,"specified source model domain");
        for(const auto& [id,p]:phi)point[id]=r.evaluate(p,point);
        auto validate=[&](const Block& block){int P=r.evaluate(block.product,point);
            for(const auto& h:block.inputs)need(!r.residue(P*r.evaluate(h,point)),"complete joint source model");
            for(const auto& row:block.variables)for(int id:row)need(point[id]==0 || point[id]==1,"all coefficient domains");};
        for(const auto& b:bottoms)validate(b);
        for(const auto& P:parents)validate(P.source);
        int low_value=r.evaluate(parents[2].source.product,point);result.low_nonzero_products+=low_value;
        out<<"{\"record\":\"joint_source_model\",\"B_mask\":"<<B<<",\"low_product_value\":"<<low_value<<",\"assignment\":[";
        for(int i=0;i<fresh;++i){if(i)out<<',';out<<point[i];}out<<"]}\n";++result.models;
    }
    need(result.models==128 && result.low_nonzero_products==8,"specified full model domain and nonzero low product");
    std::map<int,int> counter;for(int i=0;i<g.v;++i)counter[i]=0;counter[0]=counter[8]=1;
    for(const auto& [id,p]:phi)counter[id]=r.evaluate(p,counter);
    need(!r.evaluate(weight,counter) && r.evaluate(parents[0].source.companions[0],counter)==1,"unweighted high-source map fails");
    out<<"{\"record\":\"unweighted_joint_control\",\"weight_value\":0,\"companion_value\":1,\"assignment\":[";
    for(int i=0;i<fresh;++i){if(i)out<<',';out<<counter[i];}out<<"]}\n";
    out<<"{\"record\":\"joint_source_summary\",\"weighted_axiom_images\":321,\"unweighted_low_images\":12,\"models\":128,"
         "\"models_with_low_product_one\":8,\"model_scope\":\"A0=1, other A=0, extra=1, and B masks with odd first-six parity; not all old assignments\",\"passed\":true}\n";
    return result;
}
int mixed_accuracy(std::ostream& out){
    Ring r(2,80);BooleanWitnesses bools(r,2);SourceWriter writer{r,bools,out};auto one=r.constant(1);
    int fresh=2;auto bottom=make_block(r,{r.subtract(one,r.variable(0)),r.subtract(one,r.variable(1))},2,fresh);
    auto parent=make_block(r,{bottom.product},3,fresh);need(fresh==9,"heterogeneous-accuracy source variables");
    std::map<int,Polynomial> phi;
    for(unsigned row=0;row<bottom.variables.size();++row)for(int j=0;j<2;++j)
        phi[bottom.variables[row][j]]=row==0?(j==0?one:r.variable(0)):Polynomial{};
    for(unsigned row=0;row<parent.variables.size();++row)phi[parent.variables[row][0]]=row==0?one:Polynomial{};
    auto product=r.multiply(r.variable(0),r.variable(1));
    need(r.substitute(bottom.product,phi)==product && r.substitute(parent.product,phi)==r.subtract(one,product),"first-row maps at different accuracies");
    out<<"{\"record\":\"mixed_accuracy_system\",\"old_variables\":2,\"source_variables\":9,\"old_Boolean_axioms\":";
    write_polynomials(out,bools.axioms);out<<",\"bottom\":";write_block(out,bottom);out<<",\"parent\":";write_block(out,parent);
    out<<",\"simultaneous_map\":[";bool comma=false;
    for(const auto& [id,p]:phi){if(comma)out<<',';comma=true;out<<'['<<id<<',';write_json(out,p);out<<']';}out<<"]}\n";
    for(int i=0;i<2;++i)writer.write("mixed_accuracy","old_"+std::to_string(i),bools.axioms[i],bools.axioms[i],one,Cof{{i,one}},2,1,2);
    std::vector<Block> blocks={bottom,parent};
    for(unsigned b=0;b<blocks.size();++b){
        for(unsigned i=0;i<blocks[b].companions.size();++i){
            auto image=r.substitute(blocks[b].companions[i],phi);int declared=companion_ceiling(blocks[b],i);
            writer.write("mixed_accuracy","companion_"+std::to_string(b)+"_"+std::to_string(i),blocks[b].companions[i],image,one,bools.direct(image),declared,1,degree(image));
            if(b==1)need(declared==19 && degree(image)==4,"original accuracy-dependent companion degree is retained");
        }
        for(const auto& row:blocks[b].variables)for(int id:row){
            auto source=r.subtract(r.power(r.variable(id),2),r.variable(id)),image=r.substitute(source,phi);
            writer.write("mixed_accuracy","field_"+std::to_string(id),source,image,one,bools.direct(image),2,1,degree(image));
        }
    }
    need(writer.count==12,"all mixed-accuracy axioms");
    for(unsigned bits=0;bits<4;++bits){
        std::map<int,int> point{{0,int(bits&1)},{1,int((bits>>1)&1)}};
        for(const auto& [id,p]:phi)point[id]=r.evaluate(p,point);
        for(const auto& block:blocks){
            for(const auto& p:block.companions)need(!r.evaluate(p,point),"complete mixed-accuracy model");
            for(const auto& row:block.variables)for(int id:row)need(point[id]==0 || point[id]==1,"all mixed-accuracy coefficient fields");
        }
        out<<"{\"record\":\"mixed_accuracy_model\",\"old_point\":"<<bits<<",\"assignment\":[";
        for(int i=0;i<fresh;++i){if(i)out<<',';out<<point[i];}out<<"]}\n";
    }
    return writer.count;
}
cpp_int cube(const cpp_int& x){return x*x*x;}
cpp_int ceil_cube_root(const cpp_int& a){
    cpp_int lo=0,hi=1;while(cube(hi)<a)hi<<=1;
    while(lo+1<hi){cpp_int mid=(lo+hi)/2;if(cube(mid)>=a)hi=mid;else lo=mid;}
    need(cube(hi)>=a && cube(hi-1)<a,"integer cube-root ceiling");return hi;
}
void parameters(std::ostream& out){
    for(unsigned ell:{64u,128u,256u}){
        unsigned logell=0;while((1u<<logell)<ell)++logell;
        cpp_int n=cpp_int(1)<<ell,v=(n+1)*ell,M=n*n,D=cpp_int(ell)*ell*ell,H=4*ell+2*logell+5;
        cpp_int k=ceil_cube_root(v*v*H),T=6*k-1,B=T*D+k;
        bool domain=192*k<=n,room=4*B<=n;
        need(k>=3 && 2*k<=v && cube(k)>=v*v*H && domain,"projected-source domain and image bounds");
        need(room==(ell>=128),"positive and negative projected-source room controls");
        out<<"{\"record\":\"projected_source_parameters\",\"ell\":"<<ell<<",\"n\":\""<<n<<"\",\"v\":\""<<v
           <<"\",\"M\":\""<<M<<"\",\"D\":\""<<D<<"\",\"H\":\""<<H<<"\",\"k\":\""<<k<<"\",\"T\":\""<<T
           <<"\",\"B\":\""<<B<<"\",\"cube_volume_condition\":true,\"image_conditions\":true,\"old_degree_condition\":"
           <<(room?"true":"false")<<",\"passed\":true}\n";
    }
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");int ext=0,bin=0;
        out<<"{\"record\":\"schema\",\"version\":1,\"polynomials\":\"[coefficient,[variable IDs with repetitions]]\","
             "\"extension_coefficients\":\"polynomial-basis bitmasks modulo the supplied binary polynomial\","
             "\"PC_linear_combinations\":\"sum of listed predecessor lines over F2; expandable into binary additions\","
             "\"large_integers\":\"exact decimal strings\"}\n";
        {
            Coordinates g(3);Matrix U={{1,0,0},{0,1,0},{1,1,0}};auto x=g.a.r.variable(6),one=g.a.r.constant(1);
            Projection p(g,U,{x,one,g.a.r.add(x,one)});p.checks(out);
            need(p.pivots.size()==2 && p.selected.size()==2,"field projection rank and matching");ext+=p.extension_count;bin+=p.binary_count;
        }
        JointResult joint;
        {
            Coordinates g(8);Matrix U(6,std::vector<int>(8));for(int i=0;i<6;++i)U[i][i]=1;
            Projection p(g,U,std::vector<Polynomial>(6));p.checks(out);
            need(p.pivots.size()==6 && p.selected.size()==3,"proper projected high-rank tuple");joint=joint_source(out,p);
            ext+=p.extension_count;bin+=p.binary_count;
        }
        int mixed=mixed_accuracy(out);parameters(out);
        need(ext==1290 && bin==1261 && joint.source_certificates==333 && mixed==12,"complete projected-source certificate totals");
        out<<"{\"record\":\"summary\",\"ordinary_NS_certificates\":"<<ext+bin+joint.source_certificates+mixed+1
           <<",\"joint_models\":"<<joint.models<<",\"mixed_accuracy_models\":4,\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<"2897 exact NS certificates, shared-weight source regimes, and original-degree controls passed.\n";
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
