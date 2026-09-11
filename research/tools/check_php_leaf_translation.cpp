// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact truth-convention, leaf-certificate, and later-block substitution checks.
#include "sparse_polynomial.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <set>
#include <string>
using namespace sparse_polynomial;
void need(bool condition,const std::string& why){
    if(!condition)throw std::runtime_error(why);
}
struct Block {
    std::vector<Polynomial> inputs,companions;
    Polynomial product;
    std::vector<std::vector<int>> variables;
};
Block block(const Ring& ring,std::vector<Polynomial> inputs,int accuracy,int& fresh){
    Block result;result.inputs=std::move(inputs);result.product=ring.constant(1);
    for(int u=0;u<accuracy;u++){
        Polynomial factor=ring.constant(1);std::vector<int> variables;
        for(const Polynomial& g:result.inputs){
            variables.push_back(fresh);
            ring.accumulate(factor,ring.multiply(ring.variable(fresh++),g),-1);
        }
        result.variables.push_back(std::move(variables));
        result.product=ring.multiply(result.product,factor);
    }
    for(const Polynomial& g:result.inputs)result.companions.push_back(ring.multiply(g,result.product));
    return result;
}
void write_block(std::ostream& out,const Block& b){
    out<<"{\"product\":";write_json(out,b.product);out<<",\"companions\":[";
    for(size_t j=0;j<b.companions.size();j++){
        if(j)out<<',';
        write_json(out,b.companions[j]);
    }
    out<<"],\"coefficient_variables\":[";
    for(size_t u=0;u<b.variables.size();u++){
        if(u)out<<',';
        out<<'[';
        for(size_t j=0;j<b.variables[u].size();j++){
            if(j)out<<',';
            out<<b.variables[u][j];
        }
        out<<']';
    }
    out<<"]}";
}
std::map<int,Polynomial> leaf_images(const Ring& ring,const Block& row,const Block& column){
    std::map<int,Polynomial> result;
    for(size_t u=0;u<row.variables.size();u++){
        for(int variable:row.variables[u])result[variable]=ring.constant(u==0?1:0);
    }
    for(size_t u=0;u<column.variables.size();u++){
        result[column.variables[u][0]]=ring.constant(u==0?1:0);
        result[column.variables[u][1]]=u==0?ring.variable(0):ring.constant(0);
    }
    return result;
}
void check_leaves(std::ostream& out){
    int cases=0,truth_assignments=0,weak_rows=0,omissions=0,companions=0;
    for(int p:{2,3,5,7}){
        Ring ring(p);
        for(int n:std::set<int>{2,3,p+1}){
            Polynomial rho;std::vector<Polynomial> row_inputs;
            for(int j=0;j<n;j++){
                Polynomial variable=ring.variable(j);row_inputs.push_back(variable);ring.accumulate(rho,variable);
            }
            Polynomial row_axiom=ring.subtract(rho,ring.constant(1));
            Polynomial x=ring.variable(0),y=ring.variable(n),collision=ring.multiply(x,y);
            Polynomial qsum=ring.subtract(rho,ring.constant(n-1));
            Polynomial star_row=ring.power(qsum,p-1);
            std::map<int,Polynomial> truth_flip;
            for(int j=0;j<n*(n+1);j++)truth_flip[j]=ring.subtract(ring.constant(1),ring.variable(j));
            Polynomial flipped_row=ring.substitute(star_row,truth_flip);
            Polynomial expected_row=ring.power(row_axiom,p-1);
            Polynomial star_column=ring.multiply(ring.subtract(ring.constant(1),x),
                                                 ring.subtract(ring.constant(1),y));
            need(flipped_row==expected_row,"MOD-row truth convention");
            need(ring.substitute(star_column,truth_flip)==collision,"collision truth convention");
            Polynomial boolean=ring.subtract(ring.multiply(x,x),x);
            need(ring.substitute(boolean,truth_flip)==boolean,"Boolean truth convention");
            for(int mask=0;mask<(1<<n);mask++){
                int weight=__builtin_popcount(static_cast<unsigned>(mask));std::map<int,int> values;
                for(int j=0;j<n;j++)values[j]=(mask>>j)&1;
                int value=ring.evaluate(flipped_row,values);
                need((value==0)==(weight%p==1),"MOD-row assignment semantics");
                if(value==0)need(weight>0,"empty row accepted by MOD-one");
                if(weight==p+1){
                    need(value==0,"legal p+1-ones row rejected");weak_rows++;
                }
                truth_assignments++;
            }
            for(int h:{1,2,3}){
                int fresh=n*(n+1);
                Block row=block(ring,row_inputs,h,fresh);
                Block column=block(ring,{ring.subtract(ring.constant(1),x),
                                        ring.subtract(ring.constant(1),y)},h,fresh);
                Polynomial row_rhs;
                for(const Polynomial& e:row.companions)ring.accumulate(row_rhs,e);
                ring.accumulate(row_rhs,ring.multiply(row.product,row_axiom),-1);
                need(row_rhs==row.product,"row leaf certificate");
                Polynomial column_rhs=column.companions[0];
                ring.accumulate(column_rhs,ring.multiply(x,column.companions[1]));
                ring.accumulate(column_rhs,ring.multiply(column.product,collision));
                need(column_rhs==column.product,"collision leaf certificate");
                Polynomial omit_row=row_rhs;ring.accumulate(omit_row,ring.multiply(row.product,row_axiom));
                Polynomial omit_collision=column_rhs;
                ring.accumulate(omit_collision,ring.multiply(column.product,collision),-1);
                need(omit_row!=row.product && omit_collision!=column.product,"leaf omission controls");omissions+=2;
                auto images=leaf_images(ring,row,column);
                Polynomial row_image=ring.substitute(row.product,images);
                Polynomial column_image=ring.substitute(column.product,images);
                need(row_image==ring.subtract(ring.constant(1),rho),"row-block normalization");
                need(column_image==collision,"collision-block normalization");
                for(size_t j=0;j<row.companions.size();j++){
                    Polynomial image=ring.substitute(row.companions[j],images);
                    need(image==ring.multiply(row_inputs[j],row_image),"row companion substitution");
                    need(degree(row.companions[j])==2*h+1 && degree(image)<=2,"row original/image degrees");
                    companions++;
                }
                for(size_t j=0;j<column.companions.size();j++){
                    Polynomial image=ring.substitute(column.companions[j],images);
                    need(image==ring.multiply(column.inputs[j],collision),"column companion substitution");
                    need(degree(column.companions[j])==2*h+1 && degree(image)<=3,"column original/image degrees");
                    companions++;
                }
                Polynomial field=ring.subtract(ring.power(x,p),x),geometric;
                for(int e=0;e<=p-2;e++)ring.accumulate(geometric,ring.power(x,e));
                need(field==ring.multiply(boolean,geometric),"removed coefficient field certificate");
                out<<"{\"record\":\"leaf_case\",\"p\":"<<p<<",\"n\":"<<n<<",\"h\":"<<h
                   <<",\"old_variable_count\":"<<n*(n+1)<<",\"translated_MOD_row\":";
                write_json(out,flipped_row);out<<",\"translated_collision\":";write_json(out,collision);
                out<<",\"row_block\":";write_block(out,row);out<<",\"column_block\":";write_block(out,column);
                out<<",\"row_leaf_certificate_degree\":"<<2*h+1
                   <<",\"collision_leaf_certificate_degree\":"<<2*h+2
                   <<",\"row_product_image\":";write_json(out,row_image);
                out<<",\"column_product_image\":";write_json(out,column_image);
                out<<",\"field_image\":";write_json(out,field);
                out<<",\"boolean_field_cofactor\":";write_json(out,geometric);
                out<<",\"omission_controls\":2}\n";cases++;
            }
        }
    }
    out<<"{\"record\":\"leaf_summary\",\"cases\":"<<cases<<",\"semantic_assignments\":"<<truth_assignments
       <<",\"accepted_p_plus_one_rows\":"<<weak_rows<<",\"companion_images\":"<<companions
       <<",\"omission_controls\":"<<omissions<<"}\n";
    std::cout<<cases<<" leaf cases, "<<truth_assignments<<" truth-convention assignments, "
             <<weak_rows<<" legal p+1 rows, "<<companions<<" companion images.\n";
}
void check_later_blocks(std::ostream& out){
    for(int p:{2,3,5,7}){
        Ring ring(p);int n=2,fresh=6;Polynomial x=ring.variable(0),y=ring.variable(2);
        std::vector<Polynomial> row_inputs{x,ring.variable(1)};
        Block row=block(ring,row_inputs,1,fresh);
        Block column=block(ring,{ring.subtract(ring.constant(1),x),
                                ring.subtract(ring.constant(1),y)},1,fresh);
        std::vector<Polynomial> old_inputs{ring.subtract(row.product,column.product),
            ring.subtract(ring.constant(1),ring.multiply(row.product,column.product))};
        int later_fresh=fresh;Block later=block(ring,old_inputs,2,fresh);
        auto images=leaf_images(ring,row,column);std::vector<Polynomial> new_inputs;
        for(const Polynomial& input:old_inputs)new_inputs.push_back(ring.substitute(input,images));
        Block rebuilt=block(ring,new_inputs,2,later_fresh);
        need(later_fresh==fresh,"retained coefficient variables changed");
        need(ring.substitute(later.product,images)==rebuilt.product,"later product substitution");
        out<<"{\"record\":\"later_block_case\",\"p\":"<<p<<",\"n\":"<<n
           <<",\"source_block\":";write_block(out,later);out<<",\"specialized_block\":";write_block(out,rebuilt);
        out<<",\"degree_pairs\":[";
        for(size_t j=0;j<later.companions.size();j++){
            Polynomial image=ring.substitute(later.companions[j],images);
            need(image==rebuilt.companions[j],"later companion substitution");
            need(degree(image)<=degree(later.companions[j]),"later degree increased");
            need(image!=later.companions[j],"unchanged-later-input negative control is vacuous");
            if(j)out<<',';
            out<<'['<<degree(later.companions[j])<<','<<degree(image)<<']';
        }
        out<<"],\"unchanged_input_controls\":2}\n";
    }
    std::cout<<"Four later-block cases: both dependent inputs and all companions specialized exactly.\n";
}
void check_boolean_step(std::ostream& out){
    int valid_premises=0;
    for(int mask=0;mask<32;mask++){
        bool a=mask&1,b=mask&2,c=mask&4,z=mask&8,m=mask&16;
        bool recurrence=m==((b && !z)||(c && z));
        bool premise=(!a || !b) && (!a || !z) && recurrence;
        if(premise){
            need(!a || !m,"fixed Boolean induction template");valid_premises++;
        }
    }
    out<<"{\"record\":\"boolean_induction_template\",\"assignments\":32,\"satisfying_premises\":"
       <<valid_premises<<",\"all_implications_valid\":true}\n";
}
int main(int argc,char** argv){
    try{
        std::string path;
        for(int j=1;j<argc;j++){
            std::string arg=argv[j];
            if(arg=="--out" && j+1<argc)path=argv[++j];
            else throw std::runtime_error("Usage: check_php_leaf_translation --out NEW_PATH");
        }
        need(!path.empty() && !std::filesystem::exists(path),"new --out required");
        std::ofstream out(path);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"ordinary_php_leaf_translation\",\"arithmetic\":\"exact\"}\n";
        check_leaves(out);check_later_blocks(out);check_boolean_step(out);
        out<<"{\"record\":\"summary\",\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failure");return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
