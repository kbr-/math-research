// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact nonfactorable-input reductions and complete bounded-sum source maps.
#include "graded_reduction.hpp"
#include "ns_witness.hpp"
#include <boost/multiprecision/cpp_int.hpp>
#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace domain_polynomial;
using namespace graded_reduction;
using boost::multiprecision::cpp_int;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
void write_certificate(std::ostream& out,const Ring& r,const std::vector<Polynomial>& axioms,
                       const std::string& system,const std::string& name,const Polynomial& target,
                       const std::map<int,Polynomial>& cof,int budget,const Polynomial* source=nullptr){
    out<<"{\"record\":\"NS_certificate\",\"system\":\""<<system<<"\",\"name\":\""<<name
       <<"\",\"target\":";write_json(out,target);out<<",\"budget\":"<<budget;
    if(source){
        need(budget<=degree(*source)+3,"complete affine-map weighted source budget");
        out<<",\"source_axiom\":";write_json(out,*source);
        out<<",\"original_degree\":"<<degree(*source)<<",\"weighted_transfer_ceiling\":"<<degree(*source)+3;
    }
    ns_witness::write_terms(out,r,axioms,target,cof,budget,name);out<<"}\n";
}
int normal_map_checks(std::ostream& out){
    Ring r(2,80);auto x=[&](int id){return r.variable(id);};auto one=r.constant(1);
    std::map<int,Polynomial> to_y,to_x;
    std::vector<std::vector<int>> linear_rows;
    for(int i=0;i<8;++i){
        auto forward=x(i),inverse=x(8+i);std::vector<int> row={i};
        if(i<4){
            r.accumulate(forward,x(i+4));r.accumulate(inverse,x(12+i));row.push_back(i+4);
            if(i==0){r.accumulate(forward,one);r.accumulate(inverse,one);}
        }
        to_x[8+i]=forward;to_y[i]=inverse;linear_rows.push_back(row);
    }
    for(int i=0;i<8;++i){
        need(r.substitute(to_y[i],to_x)==x(i),"old coordinate round trip");
        need(r.substitute(to_x[8+i],to_y)==x(8+i),"probe coordinate round trip");
    }
    std::vector<Polynomial> dy,dx;
    for(int i=0;i<8;++i){
        dy.push_back(r.subtract(r.power(x(8+i),2),x(8+i)));
        dx.push_back(r.subtract(r.power(x(i),2),x(i)));
    }
    dy.push_back(r.add(r.multiply(x(8),x(9)),r.multiply(x(10),x(11))));
    dy.push_back(r.add(r.multiply(x(12),x(13)),r.multiply(x(14),x(15))));
    dx.push_back(r.substitute(dy[8],to_x));dx.push_back(r.substitute(dy[9],to_x));
    ReductionMap reducer(r,dy);
    auto pull_coefficients=[&](const std::map<int,Polynomial>& coefficients){
        std::map<int,Polynomial> result;
        for(const auto& [id,c]:coefficients){
            auto pulled=r.substitute(c,to_x);
            if(id<8)for(int variable:linear_rows[id])r.accumulate(result[variable],pulled);
            else r.accumulate(result[id],pulled);
        }
        return result;
    };
    out<<"{\"record\":\"normal_map_system\",\"old_variables\":[0,1,2,3,4,5,6,7],"
         "\"probe_variables\":[8,9,10,11,12,13,14,15],\"old_generators\":";
    write_polynomials(out,dx);out<<",\"coordinate_divisors\":";write_polynomials(out,dy);
    out<<",\"old_to_probe\":[";bool comma=false;
    for(const auto& [id,f]:to_y){if(comma)out<<',';comma=true;out<<'['<<id<<',';write_json(out,f);out<<']';}
    out<<"],\"probe_to_old\":[";comma=false;
    for(const auto& [id,f]:to_x){if(comma)out<<',';comma=true;out<<'['<<id<<',';write_json(out,f);out<<']';}
    out<<"],\"order\":\"graded lexicographic; lower variable ID has higher priority\","
         "\"division_priority\":\"listed Boolean divisors, then listed actual input functions\","
         "\"scope\":\"kernel-construction generators; they are not assumed in the old PHP base\"}\n";
    auto basis=monomials(8,4);need(basis.size()==495,"complete ordinary filtered basis");int certificates=0;
    for(unsigned i=0;i<basis.size();++i){
        Polynomial original{{basis[i],1}};
        auto normal=reducer.polynomial(r.substitute(original,to_y));
        auto remainder=r.substitute(normal.remainder,to_x);
        auto target=r.subtract(original,remainder);
        out<<"{\"record\":\"basis_reduction\",\"index\":"<<i<<",\"original\":";write_json(out,original);
        out<<",\"probe_remainder\":";write_json(out,normal.remainder);
        out<<",\"old_remainder\":";write_json(out,remainder);out<<"}\n";
        write_certificate(out,r,dx,"normal_map","basis_"+std::to_string(i),target,
                          pull_coefficients(normal.coefficients),basis[i].size());++certificates;
    }
    auto rho=r.multiply(r.add(x(8),one),dy[8]);auto relation=reducer.polynomial(rho);
    need(!relation.remainder.empty(),"division map is not the full quotient map");
    auto cof=relation.coefficients;
    for(auto& [id,f]:cof){(void)id;f=r.multiply(r.constant(-1),f);}
    r.accumulate(cof[8],r.add(x(8),one));
    auto old_relation=r.substitute(relation.remainder,to_x);
    out<<"{\"record\":\"nonquotient_control\",\"ideal_element\":";write_json(out,rho);
    out<<",\"nonzero_normal_remainder\":";write_json(out,relation.remainder);
    out<<",\"old_remainder\":";write_json(out,old_relation);out<<"}\n";
    write_certificate(out,r,dx,"normal_map","nonquotient_relation",old_relation,pull_coefficients(cof),3);
    ++certificates;
    std::vector<unsigned> normal_masks,points;
    for(unsigned mask=0;mask<256;++mask)
        if(__builtin_popcount(mask)<=4 && (mask&3)!=3 && (mask&48)!=48)normal_masks.push_back(mask);
    for(unsigned point=0;point<256;++point){
        bool g0=((point&3)==3)^((point&12)==12),g1=((point&48)==48)^((point&192)==192);
        if(!g0 && !g1)points.push_back(point);
    }
    need(normal_masks.size()==120 && points.size()==100,"normal-space and common-zero counts");
    using Row=std::array<std::uint64_t,2>;
    std::vector<Row> matrix(points.size(),Row{0,0});
    for(unsigned i=0;i<points.size();++i)for(unsigned j=0;j<normal_masks.size();++j)
        if((points[i]&normal_masks[j])==normal_masks[j])matrix[i][j/64]|=std::uint64_t(1)<<(j%64);
    auto reduced=matrix;unsigned rank=0;std::vector<unsigned> pivots;
    for(unsigned col=0;col<normal_masks.size() && rank<reduced.size();++col){
        unsigned pivot=rank;
        while(pivot<reduced.size() && !(reduced[pivot][col/64]&(std::uint64_t(1)<<(col%64))))++pivot;
        if(pivot==reduced.size())continue;
        std::swap(reduced[pivot],reduced[rank]);
        for(unsigned i=0;i<reduced.size();++i)if(i!=rank && (reduced[i][col/64]&(std::uint64_t(1)<<(col%64))))
            for(unsigned w=0;w<2;++w)reduced[i][w]^=reduced[rank][w];
        pivots.push_back(col);++rank;
    }
    need(rank==100,"complete common-zero evaluation rank");
    auto rows_json=[&](const std::vector<Row>& rows){
        out<<'[';
        for(unsigned i=0;i<rows.size();++i){
            if(i)out<<',';
            out<<'"';
            for(unsigned j=0;j<normal_masks.size();++j)out<<((rows[i][j/64]>>(j%64))&1);
            out<<'"';
        }
        out<<']';
    };
    out<<"{\"record\":\"functional_quotient_matrix\",\"normal_image_dimension\":120,\"functional_rank\":"
       <<rank<<",\"coordinate_point_masks\":[";
    for(unsigned i=0;i<points.size();++i){if(i)out<<',';out<<points[i];}
    out<<"],\"normal_monomial_masks\":[";
    for(unsigned i=0;i<normal_masks.size();++i){if(i)out<<',';out<<normal_masks[i];}
    out<<"],\"pivots\":[";
    for(unsigned i=0;i<pivots.size();++i){if(i)out<<',';out<<pivots[i];}
    out<<"],\"matrix\":";rows_json(matrix);out<<",\"rref\":";rows_json(reduced);out<<",\"passed\":true}\n";
    need(certificates==496,"normal-map certificate count");return certificates;
}
int binary_rank(std::vector<unsigned> rows){
    unsigned basis[32]={};int rank=0;
    for(unsigned x:rows)for(int j=31;j>=0;--j)if(x&(1u<<j)){
        if(basis[j])x^=basis[j];else{basis[j]=x;++rank;break;}
    }
    return rank;
}
void span_checks(std::ostream& out){
    for(unsigned mask=1;mask<8;++mask){
        unsigned support=0;
        for(unsigned point=0;point<(1u<<12);++point){
            bool value=false;
            for(unsigned i=0;i<3;++i)if(mask&(1u<<i)){
                unsigned group=(point>>(4*i))&15;
                value^=((group&3)==3)^((group&12)==12);
            }
            support+=value;
        }
        unsigned active=__builtin_popcount(mask),expected=(1u<<11)-(1u<<(11-2*active));
        std::vector<unsigned> polar(12);
        for(unsigned i=0;i<3;++i)if(mask&(1u<<i))for(unsigned j=0;j<4;++j)
            polar[4*i+j]=1u<<(4*i+(j^1u));
        int rank=binary_rank(polar);
        need(support==expected && (support&(support-1))!=0 && rank==int(4*active),"product-free input span");
        out<<"{\"record\":\"sum_span_control\",\"input_mask\":"<<mask<<",\"old_variables\":12,"
             "\"support\":"<<support<<",\"polar_rank\":"<<rank<<",\"polar_rows\":[";
        for(unsigned i=0;i<polar.size();++i){if(i)out<<',';out<<polar[i];}
        out<<"],\"basis\":\"q_i=x_(4i)*x_(4i+1)+x_(4i+2)*x_(4i+3)\",\"passed\":true}\n";
    }
}
struct BooleanContext {
    Ring r{2,80};int count=0;std::vector<Polynomial> axioms;
    BooleanContext(){for(int i=0;i<6;++i){auto x=r.variable(i);axioms.push_back(r.subtract(r.power(x,2),x));}}
    void certificate(std::ostream& out,const std::string& name,const Polynomial& target,int budget,
                     const Polynomial* source=nullptr){
        std::vector<int> powers(6,2);auto red=domain_reduce(r,target,powers);
        verify_reduction(r,target,powers,red);need(red.remainder.empty(),"old Boolean source certificate");
        std::map<int,Polynomial> cof;
        for(int i=0;i<6;++i)if(!red.coefficients[i].empty())cof[i]=red.coefficients[i];
        write_certificate(out,r,axioms,"sum_source",name,target,cof,budget,source);++count;
    }
};
void point_json(std::ostream& out,const std::map<int,int>& point,int end){
    out<<'[';for(int i=0;i<end;++i){if(i)out<<',';out<<point.at(i);}out<<']';
}
int source_checks(std::ostream& out){
    BooleanContext c;auto& r=c.r;auto one=r.constant(1);auto x=[&](int i){return r.variable(i);};
    int fresh=6;std::vector<Block> bottoms;std::map<int,Polynomial> phi;
    for(int b=0;b<3;++b){
        auto B=make_block(r,{r.subtract(one,x(2*b)),r.subtract(one,x(2*b+1))},1,fresh);
        phi[B.variables[0][0]]=one;phi[B.variables[0][1]]=x(2*b);bottoms.push_back(B);
    }
    auto parent=make_block(r,{r.add(bottoms[0].product,bottoms[1].product),
        r.add(bottoms[0].product,bottoms[2].product)},1,fresh);
    for(int id:parent.variables[0])phi[id]=x(0);
    auto g0=r.add(r.multiply(x(0),x(1)),r.multiply(x(2),x(3)));
    auto g1=r.add(r.multiply(x(0),x(1)),r.multiply(x(4),x(5)));
    auto weight=r.multiply(x(0),r.add(r.multiply(x(2),x(3)),r.multiply(x(4),x(5))));
    need(r.substitute(parent.inputs[0],phi)==g0 && r.substitute(parent.inputs[1],phi)==g1,"actual summed inputs");
    need(r.substitute(parent.product,phi)==r.subtract(one,weight),"literal summed-input kernel map");
    out<<"{\"record\":\"sum_source_system\",\"field\":2,\"old_variables\":6,\"source_variables\":"
       <<fresh<<",\"weight\":";write_json(out,weight);
    out<<",\"old_Boolean_axioms\":";write_polynomials(out,c.axioms);
    out<<",\"bottoms\":[";
    for(unsigned b=0;b<bottoms.size();++b){if(b)out<<',';write_block(out,bottoms[b]);}
    out<<"],\"parent\":";write_block(out,parent);
    out<<",\"summed_images\":[";write_json(out,g0);out<<',';write_json(out,g1);
    out<<"],\"simultaneous_map\":[";bool comma=false;
    for(const auto& [id,f]:phi){if(comma)out<<',';comma=true;out<<'['<<id<<',';write_json(out,f);out<<']';}
    out<<"],\"scope\":\"actual overlapping two-level sums; local Boolean base, not PHP\"}\n";
    for(int i=0;i<6;++i)c.certificate(out,"weighted_old_"+std::to_string(i),r.multiply(weight,c.axioms[i]),5,&c.axioms[i]);
    std::vector<Block> blocks=bottoms;blocks.push_back(parent);
    for(unsigned b=0;b<blocks.size();++b){
        for(unsigned i=0;i<blocks[b].companions.size();++i){
            const auto& source=blocks[b].companions[i];
            c.certificate(out,"weighted_companion_"+std::to_string(b)+"_"+std::to_string(i),
                          r.multiply(weight,r.substitute(source,phi)),degree(source)+3,&source);
        }
        for(int id:blocks[b].variables[0]){
            auto source=r.subtract(r.power(x(id),2),x(id));
            c.certificate(out,"weighted_field_"+std::to_string(id),
                          r.multiply(weight,r.substitute(source,phi)),5,&source);
        }
    }
    need(c.count==22,"complete summed-source image count");
    int models=0;
    for(int bits=0;bits<64;++bits){
        std::map<int,int> point;for(int i=0;i<6;++i)point[i]=(bits>>i)&1;
        if(!r.evaluate(weight,point))continue;
        for(const auto& [id,f]:phi)point[id]=r.evaluate(f,point);
        for(const auto& B:blocks){
            for(const auto& f:B.companions)need(!r.evaluate(f,point),"conditional complete sum-source model");
            for(int id:B.variables[0])need(point[id]*point[id]-point[id]==0,"coefficient model");
        }
        out<<"{\"record\":\"conditional_sum_source_model\",\"old_point\":"<<bits<<",\"assignment\":";
        point_json(out,point,fresh);out<<"}\n";++models;
    }
    need(models==12,"all nonzero-weight sum-source assignments");
    std::map<int,int> zero_point;for(int i=0;i<6;++i)zero_point[i]=int(i<2);
    auto unweighted=r.substitute(parent.companions[0],phi);
    need(!r.evaluate(weight,zero_point) && r.evaluate(unweighted,zero_point)==1,"sum-source weight control");
    out<<"{\"record\":\"unweighted_sum_source_control\",\"old_point\":3,\"weight_value\":0,"
         "\"companion_value\":1,\"companion_image\":";write_json(out,unweighted);out<<"}\n";
    for(int value=0;value<2;++value){
        auto selector=value?x(0):r.subtract(one,x(0));
        auto branch=r.add(r.multiply(r.constant(value),x(1)),r.multiply(x(2),x(3)));
        auto error=r.multiply(selector,r.subtract(g0,branch));
        out<<"{\"record\":\"probe_restriction\",\"stage\":\"a\",\"value\":"<<value<<",\"input\":";
        write_json(out,g0);out<<",\"selector\":";write_json(out,selector);
        out<<",\"representative\":";write_json(out,branch);out<<"}\n";
        c.certificate(out,"restrict_a_"+std::to_string(value),error,3);
        auto nested_selector=r.multiply(x(0),value?x(1):r.subtract(one,x(1)));
        auto nested_branch=r.add(r.constant(value),r.multiply(x(2),x(3)));
        out<<"{\"record\":\"probe_restriction\",\"stage\":\"a=1,b\",\"value\":"<<value<<",\"input\":";
        write_json(out,g0);out<<",\"selector\":";write_json(out,nested_selector);
        out<<",\"representative\":";write_json(out,nested_branch);out<<"}\n";
        c.certificate(out,"restrict_ab_"+std::to_string(value),
                      r.multiply(nested_selector,r.subtract(g0,nested_branch)),4);
    }
    int other_fresh=6;
    auto expanded=make_block(r,{r.multiply(x(0),x(1)),r.multiply(x(2),x(3))},1,other_fresh);
    auto original=make_block(r,{g0},1,other_fresh);
    std::map<int,int> counter;for(int i=0;i<other_fresh;++i)counter[i]=int(i==0 || i==1 || i==6 || i==7);
    int original_id=original.variables[0][0];
    counter[original_id]=(counter[expanded.variables[0][0]]+counter[expanded.variables[0][1]])%2;
    for(const auto& f:expanded.companions)need(!r.evaluate(f,counter),"expanded companion model");
    need(r.evaluate(original.companions[0],counter)==1,"naive sum-of-coefficients map fails");
    out<<"{\"record\":\"summand_coefficient_countermodel\",\"expanded_block\":";write_block(out,expanded);
    out<<",\"original_block\":";write_block(out,original);
    out<<",\"assignment\":";point_json(out,counter,other_fresh);
    out<<",\"proposed_map\":\"original coefficient = sum of the two expanded coefficients\","
         "\"original_companion_value\":1,\"scope\":\"this proposed map fails; no universal transfer impossibility\"}\n";
    out<<"{\"record\":\"sum_source_summary\",\"weighted_source_images\":22,\"restriction_certificates\":4,"
         "\"conditional_models\":"<<models<<",\"passed\":true}\n";
    return c.count;
}
cpp_int power(cpp_int a,unsigned e){
    cpp_int result=1;while(e){if(e&1)result*=a;a*=a;e>>=1;}return result;
}
cpp_int ceil_root(const cpp_int& a,unsigned e){
    cpp_int lo=0,hi=1;while(power(hi,e)<a)hi<<=1;
    while(lo+1<hi){cpp_int mid=(lo+hi)/2;if(power(mid,e)>=a)hi=mid;else lo=mid;}
    need(power(hi,e)>=a && power(hi-1,e)<a,"integer root");return hi;
}
void parameters(std::ostream& out){
    for(unsigned ell:{128u,256u,512u}){
        unsigned logell=0;while((1u<<logell)<ell)++logell;
        cpp_int n=cpp_int(1)<<ell,v=(n+1)*ell,D=cpp_int(ell)*ell,H=3*ell+logell+5;
        cpp_int k=ceil_root(power(v,7)*H,8);
        std::vector<cpp_int> R(5);bool image_ok=true,range_ok=k>=2 && 2*k<=v;
        for(int j=4;j>=1;--j){
            cpp_int higher=0;for(int u=j+1;u<=4;++u)higher+=u*R[u];
            unsigned degree=std::min(2,j);
            cpp_int numerator=power(v,degree)*(H+higher),denominator=power(k,degree);
            R[j]=(numerator+denominator-1)/denominator;
            image_ok=image_ok && R[j]*denominator>=numerator;
            range_ok=range_ok && j*R[j]<=v;
        }
        cpp_int T=k-1;for(int j=1;j<=4;++j)T+=j*(R[j]-1);
        cpp_int B=T*D+k;bool space=6*k<=n+1 && 192*k<=n,board=4*B<=n;
        need(image_ok && range_ok && space,"bounded-probe finite premises");
        need(board==(ell>=256),"bounded-probe positive/negative old-degree controls");
        out<<"{\"record\":\"bounded_probe_parameters\",\"r\":4,\"s\":2,\"S\":7,\"ell\":"<<ell
           <<",\"M\":\"n^2\",\"n\":\""<<n<<"\",\"v\":\""<<v<<"\",\"D\":\""<<D<<"\",\"H\":\""<<H
           <<"\",\"k\":\""<<k<<"\",\"thresholds_by_probe_rank\":[";
        for(int j=1;j<=4;++j){if(j>1)out<<',';out<<'"'<<R[j]<<'"';}
        out<<"],\"T\":\""<<T<<"\",\"B\":\""<<B<<"\",\"range_space_image_conditions\":true,"
             "\"old_degree_condition\":"<<(board?"true":"false")
           <<",\"scope\":\"exact integer inequalities; branching inventory remains symbolic\",\"passed\":true}\n";
    }
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");
        out<<"{\"record\":\"schema\",\"version\":1,\"polynomials\":\"[coefficient,[variable IDs with repetitions]]\","
             "\"large_integers\":\"exact decimal strings\",\"matrix_entries\":\"binary strings in listed column order\"}\n";
        int certificates=normal_map_checks(out);span_checks(out);certificates+=source_checks(out);parameters(out);
        need(certificates==522,"complete bounded-probe certificate count");
        out<<"{\"record\":\"summary\",\"NS_certificates\":"<<certificates<<",\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<certificates<<" exact NS certificates, full reduction/evaluation matrices, and sum-source controls passed.\n";
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
