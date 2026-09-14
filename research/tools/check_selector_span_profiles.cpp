// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact source-profile audit: an adapted basis replaces many dependent positions.
#include "domain_polynomial.hpp"
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <string>
using namespace domain_polynomial;
using U64=std::uint64_t;
using U128=__uint128_t;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
Ring ring(2,64);
std::vector<Polynomial> axioms;
std::vector<std::string> names;
int certificate_count=0;
int add_axiom(const std::string& name,const Polynomial& f){
    int id=int(axioms.size());axioms.push_back(f);names.push_back(name);return id;
}
struct Cert {Polynomial target;std::map<int,Polynomial> cof;};
Cert ax(int id){return {axioms.at(id),{{id,ring.constant(1)}}};}
Cert scale(Cert c,const Polynomial& q){
    c.target=ring.multiply(c.target,q);
    for(auto& [id,f]:c.cof){(void)id;f=ring.multiply(f,q);}return c;
}
void plus(Cert& a,const Cert& b){
    ring.accumulate(a.target,b.target);
    for(const auto& [id,f]:b.cof)ring.accumulate(a.cof[id],f);
}
Cert Boolean_certificate(const Polynomial& f,int variables){
    std::vector<int> sizes(variables,2);
    auto red=domain_reduce(ring,f,sizes);verify_reduction(ring,f,sizes,red);
    need(red.remainder.empty(),"Boolean remainder");
    Cert result;result.target=f;
    for(std::size_t i=0;i<red.coefficients.size();++i)
        if(!red.coefficients[i].empty())result.cof[int(i)]=red.coefficients[i];
    return result;
}
void write_cert(std::ostream& out,const std::string& name,const Cert& c,int budget){
    Polynomial sum;int used=0;bool comma=false;
    out<<"{\"record\":\"NS_certificate\",\"name\":\""<<name<<"\",\"target\":";
    write_json(out,c.target);out<<",\"budget\":"<<budget<<",\"terms\":[";
    for(const auto& [id,q]:c.cof)if(!q.empty() && !axioms.at(id).empty()){
        ring.accumulate(sum,ring.multiply(q,axioms[id]));
        used=std::max(used,degree(q)+degree(axioms[id]));
        if(comma)out<<',';
        comma=true;out<<"{\"axiom_id\":"<<id<<",\"cofactor\":";write_json(out,q);out<<'}';
    }
    need(sum==c.target && used<=budget,"NS certificate "+name);
    out<<"],\"witness_degree\":"<<used<<"}\n";++certificate_count;
}
int rank(std::vector<U64> rows){
    U64 pivots[64]{};int value=0;
    for(U64 row:rows)while(row){
        int top=63-__builtin_clzll(row);
        if(pivots[top])row^=pivots[top];
        else{pivots[top]=row;++value;break;}
    }
    return value;
}
U64 combine(U64 coefficients,const std::vector<U64>& rows){
    U64 result=0;
    for(std::size_t i=0;i<rows.size();++i)if((coefficients>>i)&1)result^=rows[i];
    return result;
}
int weighted_degree(U64 row){
    int result=0;
    for(int j=0;j<11;++j)if((row>>j)&1)result=std::max(result,j<9?1:4);
    return result;
}
void assign(const Block& block,std::map<int,int>& point){
    for(const auto& row:block.variables)for(int id:row)point[id]=0;
    for(std::size_t i=0;i<block.inputs.size();++i)
        if(ring.evaluate(block.inputs[i],point)){point[block.variables[0][i]]=1;break;}
}
U128 checked_multiply(U128 a,U128 b){
    need(!b || a<=~U128(0)/b,"128-bit count overflow");return a*b;
}
U128 choose(int n,int k){
    if(k<0 || k>n)return 0;
    k=std::min(k,n-k);U128 result=1;
    for(int i=1;i<=k;++i)result=checked_multiply(result,U128(n-k+i))/U128(i);
    return result;
}
U128 power(U128 a,int e){U128 result=1;while(e--)result=checked_multiply(result,a);return result;}
std::string decimal(U128 value){
    if(!value)return "0";
    std::string result;
    while(value){result.push_back(char('0'+value%10));value/=10;}
    std::reverse(result.begin(),result.end());return result;
}
void dimension_checks(std::ostream& out){
    for(const auto& fixture:std::vector<std::pair<int,int>>{{14,9},{28,7},{56,5},{4,17}}){
        int h=fixture.first,k=fixture.second,n=64,ell=6,m=n+1,v=m*ell,rstar=h*(k+1)+1;
        need(rstar<=v,"dimension fixture rank");
        U128 image=choose(v-rstar+k,k),top=checked_multiply(choose(m,k),power(ell,k));
        bool quarter=checked_multiply(4,image)<top;
        need(quarter==(h>=2*(ell+1)),"accuracy dimension control");
        out<<"{\"record\":\"dimension_control\",\"holes\":"<<n<<",\"bit_length\":"<<ell
           <<",\"blocks\":1,\"accuracy\":"<<h<<",\"k\":"<<k<<",\"high_rank_threshold\":"<<rstar
           <<",\"restriction_dimension\":\""<<decimal(image)<<"\",\"top_row_linear_dimension\":\""
           <<decimal(top)<<"\",\"quarter_bound_holds\":"<<(quarter?"true":"false")
           <<",\"scope\":\"exact dimension comparison only; no final PHP degree inequality is asserted\"}\n";
    }
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");
        int h=2,old=9,next=old;
        auto x=[](int i){return ring.variable(i);};auto one=ring.constant(1);
        auto B0=make_block(ring,{x(5),x(6)},h,next);
        auto B1=make_block(ring,{x(7),x(8)},h,next);
        auto F=ring.add(B0.product,B1.product);need(degree(F)==4,"nonlinear selector span");
        std::vector<Polynomial> g={x(0)};
        for(int i=1;i<5;++i)g.push_back(ring.add(x(i),F));
        std::vector<int> input_degrees;for(const auto& f:g)input_degrees.push_back(degree(f));
        need(input_degrees==std::vector<int>({1,4,4,4,4}),"original input degrees");
        std::vector<Polynomial> K={g[0]};
        for(int i=2;i<5;++i)K.push_back(ring.add(g[i],g[1]));
        for(const auto& f:K){
            need(degree(f)==1,"affine intersection");
            for(const auto& [mon,c]:f){(void)c;for(int id:mon)need(id<old,"affine part is not old-only");}
        }
        int first_A=next;auto A=make_block(ring,K,h,next);
        for(int i=0;i<next;++i)
            need(add_axiom("Boolean/"+std::to_string(i),ring.subtract(ring.power(x(i),2),x(i)))==i,"domain indices");
        for(int b=0;b<2;++b){
            const auto& block=b?B1:B0;
            for(int i=0;i<2;++i)add_axiom("B"+std::to_string(b)+"/"+std::to_string(i),block.companions[i]);
        }
        std::vector<int> A_comp;
        for(int i=0;i<4;++i)A_comp.push_back(add_axiom("affine_core/"+std::to_string(i),A.companions[i]));
        int w=h*(4+1),s=2*h+4;
        auto tail=ring.subtract(one,g[1]),V=ring.multiply(A.product,tail);
        need(degree(V)==s && s<=w,"source value cost");
        std::vector<Polynomial> prefix(5);
        prefix[0]=A.prefix[0];prefix[1]=A.product;
        for(int i=2;i<5;++i){prefix[i]=A.prefix[i-1];ring.accumulate(prefix[1],A.prefix[i-1]);}
        auto residual=ring.subtract(one,V);
        for(int i=0;i<5;++i){
            need(degree(prefix[i])+input_degrees[i]<=w,"original input-weighted prefix bound");
            ring.accumulate(residual,ring.multiply(prefix[i],g[i]),-1);
        }
        need(residual.empty(),"original-prefix pullback");
        std::vector<U64> rows={U64(1)};
        for(int i=1;i<5;++i)rows.push_back((U64(1)<<i)|(U64(1)<<9)|(U64(1)<<10));
        std::vector<U64> basis_coefficients={1,6,10,18,2},basis;
        for(U64 row:basis_coefficients)basis.push_back(combine(row,rows));
        std::vector<U64> inverse={1,16,18,20,24},dependent;
        for(int i=0;i<5;++i){
            dependent.push_back(rows[i]>>9);
            need(combine(inverse[i],basis)==rows[i],"basis inverse");
            for(int j=0;j<5;++j)if((inverse[i]>>j)&1)
                need(weighted_degree(basis[j])<=input_degrees[i],"adapted degree filtration");
        }
        need(rank(rows)==5 && rank(dependent)==1 && rank({basis[0],basis[1],basis[2],basis[3]})==4,
             "complete affine intersection dimension");
        out<<"{\"record\":\"schema\",\"field\":2,\"polynomials\":\"[coefficient,[variable IDs with repetitions]]\","
             "\"scope\":\"costed source-value profile, not a map of arbitrary original raw coefficients\"}\n";
        out<<"{\"record\":\"system\",\"old_Boolean_variables\":"<<old<<",\"variables\":"<<next<<",\"axioms\":[";
        for(std::size_t i=0;i<axioms.size();++i){
            if(i)out<<',';
            out<<"{\"id\":"<<i<<",\"name\":\""<<names[i]<<"\",\"polynomial\":";write_json(out,axioms[i]);out<<'}';
        }
        out<<"],\"bottom_blocks\":[";
        write_block(out,B0);out<<',';write_block(out,B1);
        out<<"],\"affine_core\":";write_block(out,A);out<<"}\n";
        out<<"{\"record\":\"source_profile\",\"accuracy\":2,\"dependent_positions\":4,\"dependent_span_rank\":1,"
             "\"old_affine_intersection_dimension\":4,\"original_input_degrees\":[1,4,4,4,4],"
             "\"original_product_weight\":"<<w<<",\"constructed_cost\":"<<s
           <<",\"formal_column_names\":[\"b0\",\"b1\",\"b2\",\"b3\",\"b4\",\"y0\",\"y1\",\"y2\",\"y3\",\"Z_B0\",\"Z_B1\"],"
             "\"source_row_bitmasks\":[";
        for(int i=0;i<5;++i){if(i)out<<',';out<<rows[i];}
        out<<"],\"basis_from_source_bitmasks\":[";
        for(int i=0;i<5;++i){if(i)out<<',';out<<basis_coefficients[i];}
        out<<"],\"source_from_basis_bitmasks\":[";
        for(int i=0;i<5;++i){if(i)out<<',';out<<inverse[i];}
        out<<"],\"inputs\":";write_polynomials(out,g);
        out<<",\"prefixes\":";write_polynomials(out,prefix);
        out<<",\"value\":";write_json(out,V);out<<"}\n";
        auto boolG=Boolean_certificate(ring.subtract(ring.power(g[1],2),g[1]),first_A);
        for(const auto& [id,q]:boolG.cof){(void)q;need(id<first_A,"input Booleanity uses the new core");}
        write_cert(out,"selected_input_Booleanity_below_core",boolG,8);
        write_cert(out,"exact_original_prefix_residual",Cert{residual,{}},w);
        auto pivot=scale(boolG,A.product);
        need(pivot.target==ring.multiply(g[1],V),"selected input companion");
        std::vector<Cert> companions(5);companions[0]=scale(ax(A_comp[0]),tail);companions[1]=pivot;
        for(int i=2;i<5;++i){companions[i]=scale(ax(A_comp[i-1]),tail);plus(companions[i],pivot);}
        for(int i=0;i<5;++i){
            need(companions[i].target==ring.multiply(g[i],V),"original companion target");
            write_cert(out,"original_companion/"+std::to_string(i),companions[i],w+input_degrees[i]);
        }
        Cert boolA;
        for(int i=0;i<4;++i)plus(boolA,scale(ax(A_comp[i]),A.prefix[i]));
        need(boolA.target==ring.subtract(ring.power(A.product,2),A.product),"core Booleanity");
        write_cert(out,"affine_core_Booleanity",boolA,4*h);
        auto boolV=scale(boolA,ring.power(tail,2));plus(boolV,scale(boolG,A.product));
        need(boolV.target==ring.subtract(ring.power(V,2),V),"value Booleanity");
        write_cert(out,"source_value_Booleanity",boolV,2*w);
        auto wrong_prefix=prefix;wrong_prefix[1]=A.product;
        auto wrong_residual=ring.subtract(one,V);
        for(int i=0;i<5;++i)ring.accumulate(wrong_residual,ring.multiply(wrong_prefix[i],g[i]),-1);
        need(!wrong_residual.empty(),"missing-prefix control is zero");
        auto wrong_value_companion=ring.multiply(g[1],A.product);
        bool prefix_control=false,tail_control=false;int ones=0,zeroes=0;
        for(int bits=0;bits<(1<<old);++bits){
            std::map<int,int> point;
            for(int i=0;i<next;++i)point[i]=i<old?(bits>>i)&1:0;
            assign(B0,point);assign(B1,point);assign(A,point);
            int a=ring.evaluate(A.product,point),t=ring.evaluate(tail,point),value=a*t;
            int expected=1,prefix_sum=0;
            for(int i=0;i<5;++i){
                int gi=ring.evaluate(g[i],point);expected&=1-gi;
                prefix_sum^=ring.evaluate(prefix[i],point)*gi;
                need(gi*value==0,"model companion");
            }
            need(value==expected && prefix_sum==1-value,"model value and prefix");
            ones+=value;zeroes+=1-value;
            out<<"{\"record\":\"old_Boolean_model\",\"bits\":"<<bits<<",\"assignment\":[";
            for(int i=0;i<next;++i){if(i)out<<',';out<<point[i];}
            out<<"],\"axiom_values\":[";
            for(std::size_t i=0;i<axioms.size();++i){
                int v=ring.evaluate(axioms[i],point);need(v==0,"retained model axiom");
                if(i)out<<',';
                out<<v;
            }
            out<<"],\"canonical_value\":"<<value<<",\"original_prefix_sum\":"<<prefix_sum<<"}\n";
            if(!prefix_control && ring.evaluate(wrong_residual,point)){
                out<<"{\"record\":\"negative_control\",\"name\":\"missing_original_prefix_pullback\","
                     "\"witness_old_bits\":"<<bits<<",\"polynomial\":";write_json(out,wrong_residual);
                out<<",\"value\":1}\n";prefix_control=true;
            }
            if(!tail_control && ring.evaluate(wrong_value_companion,point)){
                out<<"{\"record\":\"negative_control\",\"name\":\"dropping_the_nonlinear_tail\","
                     "\"witness_old_bits\":"<<bits<<",\"polynomial\":";write_json(out,wrong_value_companion);
                out<<",\"value\":1}\n";tail_control=true;
            }
        }
        need(prefix_control && tail_control && ones && zeroes,"nonvacuity controls");
        out<<"{\"record\":\"ungraded_basis_control\",\"old_input_degree\":1,"
             "\"representation_basis_degrees\":[4,4],\"original_companion_allowance\":11,"
             "\"naive_constructed_profile_allowance\":12,"
             "\"scope\":\"violates the adapted-degree hypothesis; not a minimum-degree lower bound\"}\n";
        dimension_checks(out);
        out<<"{\"record\":\"summary\",\"NS_certificates\":"<<certificate_count
           <<",\"old_Boolean_models\":512,\"value_one_models\":"<<ones
           <<",\"value_zero_models\":"<<zeroes<<",\"dimension_controls\":4,\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<certificate_count<<" complete NS certificates and 512 retained-system models passed.\n";
        std::cout<<"Four dependent positions have rank one; exact original prefix and degree controls passed.\n";
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
