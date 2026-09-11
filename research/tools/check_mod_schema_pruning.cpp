// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact domain certificates, earlier-companion packing, and MOD-axiom syntax.
#include "ens_symbolic.hpp"
#include <filesystem>
#include <fstream>
#include <functional>
#include <iostream>
#include <memory>
#include <string>
using namespace ens_symbolic;
void need(bool condition,const std::string& why){
    if(!condition)throw std::runtime_error(why);
}
struct Reduction {Polynomial remainder;std::vector<Polynomial> coefficients;int degree=0;};
Reduction domain_reduce(const Ring& ring,Polynomial polynomial,const std::vector<int>& powers){
    Reduction result;result.coefficients.resize(powers.size());const int start_degree=degree(polynomial);
    for(size_t variable=0;variable<powers.size();variable++){
        int exponent=powers[variable];need(exponent==2 || exponent==ring.p,"domain exponent");
        while(true){
            auto found=polynomial.end();
            for(auto term=polynomial.begin();term!=polynomial.end();++term){
                auto range=std::equal_range(term->first.begin(),term->first.end(),int(variable));
                if(range.second-range.first>=exponent){found=term;break;}
            }
            if(found==polynomial.end())break;
            Monomial monomial=found->first;int coefficient=found->second;polynomial.erase(found);
            auto first=std::lower_bound(monomial.begin(),monomial.end(),int(variable));
            int position=int(first-monomial.begin());
            Monomial quotient=monomial;quotient.erase(quotient.begin()+position,quotient.begin()+position+exponent);
            ring.accumulate(result.coefficients[variable],Polynomial{{quotient,coefficient}});
            monomial.erase(monomial.begin()+position,monomial.begin()+position+exponent-1);
            ring.accumulate(polynomial,Polynomial{{monomial,coefficient}});
        }
    }
    result.remainder=std::move(polynomial);
    for(size_t variable=0;variable<powers.size();variable++){
        if(!result.coefficients[variable].empty()){
            result.degree=std::max(result.degree,degree(result.coefficients[variable])+powers[variable]);
        }
    }
    need(result.degree<=start_degree,"domain reduction increased certificate degree");
    return result;
}
void verify_reduction(const Ring& ring,const Polynomial& original,const std::vector<int>& powers,
                      const Reduction& reduction){
    Polynomial reconstructed=reduction.remainder;
    for(size_t variable=0;variable<powers.size();variable++){
        Polynomial x=ring.variable(int(variable));
        Polynomial equation=ring.subtract(ring.power(x,powers[variable]),x);
        ring.accumulate(reconstructed,ring.multiply(reduction.coefficients[variable],equation));
    }
    need(reconstructed==original,"domain certificate reconstruction");
}
void write_reduction(std::ostream& out,const Reduction& result){
    out<<"{\"degree\":"<<result.degree<<",\"remainder\":";write_json(out,result.remainder);
    out<<",\"cofactors\":";write_polynomials(out,result.coefficients);out<<'}';
}
int field_inverse(int value,int p){
    for(int inverse=1;inverse<p;inverse++){
        if(value*inverse%p==1)return inverse;
    }
    throw std::runtime_error("missing field inverse");
}
void check_field_selectors(std::ostream& out){
    int cases=0,images=0,omission_controls=0;
    for(int p:{2,3,5,7})for(int rank:{1,2,3}){
        Ring ring(p,64);std::vector<Polynomial> basis;std::vector<int> domains(2*rank);
        for(int j=0;j<rank;j++){
            basis.push_back(ring.multiply(ring.variable(2*j),ring.variable(2*j+1)));
            domains[2*j]=p;domains[2*j+1]=2;
        }
        std::vector<Polynomial> inputs=basis;Polynomial sum;
        for(const Polynomial& polynomial:basis)ring.accumulate(sum,polynomial);
        inputs.push_back(sum);inputs.push_back(ring.add(basis.front(),basis.back()));
        Polynomial packed=ring.constant(1),zero_test=ring.constant(1);
        std::vector<Polynomial> factors;std::vector<std::pair<int,int>> factor_labels;
        for(int j=0;j<rank;j++){
            zero_test=ring.multiply(zero_test,ring.subtract(ring.constant(1),ring.power(basis[j],p-1)));
            for(int alpha=1;alpha<p;alpha++){
                Polynomial factor=ring.subtract(ring.constant(1),
                    ring.multiply(ring.constant(field_inverse(alpha,p)),basis[j]));
                factors.push_back(factor);factor_labels.push_back({j,alpha});packed=ring.multiply(packed,factor);
            }
        }
        need(packed==zero_test,"constant-selector product identity");
        const int accuracy=rank*(p-1)+(rank%2);
        out<<"{\"record\":\"field_selector_case\",\"p\":"<<p<<",\"rank\":"<<rank
           <<",\"accuracy\":"<<accuracy<<",\"domain_powers\":[";
        for(size_t j=0;j<domains.size();j++){if(j)out<<',';out<<domains[j];}
        out<<"],\"inputs\":";write_polynomials(out,inputs);
        out<<",\"zero_test\":";write_json(out,zero_test);out<<",\"images\":[";
        for(size_t j=0;j<inputs.size();j++){
            Polynomial image=ring.multiply(inputs[j],zero_test);Reduction certificate=domain_reduce(ring,image,domains);
            verify_reduction(ring,image,domains,certificate);need(certificate.remainder.empty(),"selector image not in domains");
            int original=inputs[j].empty()?-1:degree(inputs[j])+accuracy*3;
            if(original>=0)need(certificate.degree<=original,"selector original-degree budget");
            if(j)out<<',';
            out<<"{\"input_index\":"<<j<<",\"original_companion_degree\":";
            if(original<0)out<<"null";else out<<original;
            out<<",\"polynomial\":";write_json(out,image);out<<",\"certificate\":";
            write_reduction(out,certificate);out<<'}';images++;
        }
        out<<"],\"omission_controls\":[";
        for(size_t omitted=0;omitted<factors.size();omitted++){
            Polynomial bad=ring.constant(1);
            for(size_t j=0;j<factors.size();j++){
                if(j!=omitted)bad=ring.multiply(bad,factors[j]);
            }
            auto [coordinate,alpha]=factor_labels[omitted];std::map<int,int> assignment;
            for(int j=0;j<rank;j++){assignment[2*j]=j==coordinate?alpha:0;assignment[2*j+1]=1;}
            int value=ring.evaluate(ring.multiply(basis[coordinate],bad),assignment);
            need(value!=0,"vacuous omitted-selector control");
            if(omitted)out<<',';
            out<<"{\"basis_index\":"<<coordinate<<",\"alpha\":"<<alpha<<",\"value\":"<<value<<'}';
            omission_controls++;
        }
        out<<"]}\n";cases++;
    }
    out<<"{\"record\":\"field_selector_summary\",\"cases\":"<<cases<<",\"images\":"<<images
       <<",\"omission_controls\":"<<omission_controls<<"}\n";
    std::cout<<cases<<" nonlinear field-selector cases, "<<images<<" domain certificates, "
             <<omission_controls<<" omission controls.\n";
}
void check_boolean_packing(std::ostream& out){
    int cases=0,images=0,necessary_earlier_controls=0;
    for(int p:{2,3,5,7})for(int arity:{2,3}){
        Ring ring(p,64);int fresh=2*arity;std::vector<Block> parents;std::vector<Polynomial> inputs;
        for(int j=0;j<arity;j++){
            parents.push_back(make_block(ring,{ring.variable(2*j),ring.variable(2*j+1)},1,fresh));
            inputs.push_back(parents.back().product);
        }
        Polynomial z=ring.constant(1);
        for(const Polynomial& g:inputs)z=ring.multiply(z,ring.subtract(ring.constant(1),g));
        out<<"{\"record\":\"boolean_packing_case\",\"p\":"<<p<<",\"arity\":"<<arity
           <<",\"target_accuracy\":"<<arity<<",\"parent_blocks\":[";
        for(size_t j=0;j<parents.size();j++){if(j)out<<',';write_block(out,parents[j]);}
        out<<"],\"product_image\":";write_json(out,z);out<<",\"images\":[";
        for(int j=0;j<arity;j++){
            Polynomial others=ring.constant(1);
            for(int k=0;k<arity;k++){
                if(k!=j)others=ring.multiply(others,ring.subtract(ring.constant(1),inputs[k]));
            }
            Polynomial image=ring.multiply(inputs[j],z),rhs;std::vector<Polynomial> cofactor;
            int certificate_degree=0;
            for(size_t k=0;k<parents[j].companions.size();k++){
                Polynomial q=ring.multiply(others,parents[j].prefix[k]);cofactor.push_back(q);
                ring.accumulate(rhs,ring.multiply(q,parents[j].companions[k]));
                certificate_degree=std::max(certificate_degree,degree(q)+degree(parents[j].companions[k]));
            }
            need(image==rhs,"earlier-companion Boolean-packing certificate");
            const int original=2+arity*3;need(certificate_degree<=original,"Boolean-packing original budget");
            if(j)out<<',';
            out<<"{\"input_index\":"<<j<<",\"original_companion_degree\":"<<original
               <<",\"certificate_degree\":"<<certificate_degree<<",\"polynomial\":";
            write_json(out,image);out<<",\"earlier_companion_cofactors\":";write_polynomials(out,cofactor);
            out<<'}';images++;
        }
        out<<']';
        if(p>2){
            std::map<int,int> assignment;
            for(int variable=0;variable<fresh;variable++)assignment[variable]=0;
            for(int j=0;j<arity;j++){
                assignment[2*j]=1;
                assignment[parents[j].variables[0][0]]=j==0?p-1:1;
            }
            int value=ring.evaluate(ring.multiply(inputs[0],z),assignment);
            need(value!=0,"earlier companions were not necessary in the control");
            out<<",\"field_only_control_value\":"<<value;necessary_earlier_controls++;
        }
        out<<"}\n";cases++;
    }
    out<<"{\"record\":\"boolean_packing_summary\",\"cases\":"<<cases<<",\"images\":"<<images
       <<",\"necessary_earlier_companion_controls\":"<<necessary_earlier_controls<<"}\n";
    std::cout<<cases<<" Boolean-packing cases, "<<images<<" explicit earlier-companion certificates.\n";
}
struct Formula {
    int id;std::string kind,label,scope;std::vector<std::shared_ptr<Formula>> children;
};
using Node=std::shared_ptr<Formula>;
void check_schema(std::ostream& out){
    std::vector<Node> nodes,macros,arguments;
    auto make=[&](const std::string& kind,std::vector<Node> children,const std::string& label,
                  const std::string& scope){
        Node node=std::make_shared<Formula>(Formula{int(nodes.size()),kind,label,scope,std::move(children)});
        nodes.push_back(node);if(kind=="or" && scope=="schema")macros.push_back(node);return node;
    };
    auto neg=[&](Node child){return make("not",{child},"","schema");};
    for(int width:{17,19,23}){
        std::vector<Node> children;
        for(int j=0;j<width;j++)children.push_back(make("atom",{},"z"+std::to_string(nodes.size()),"argument"));
        arguments.push_back(make("or",children,"argument-"+std::to_string(arguments.size()),"argument"));
    }
    Node arg=arguments[2];
    Node b=make("mod",{arguments[0],arguments[1]},"M-k-i","schema");
    Node c=make("mod",{arguments[0],arguments[1]},"M-k-i-minus-one","schema");
    Node m=make("mod",arguments,"M-k-plus-one-i","schema");
    auto conjunction=[&](Node left,Node right,const std::string& label){
        return neg(make("or",{neg(left),neg(right)},label,"schema"));
    };
    Node left=conjunction(b,neg(arg),"left-conjunction");
    Node right=conjunction(c,arg,"right-conjunction");
    Node rhs=make("or",{left,right},"rhs-disjunction","schema");
    Node forward=make("or",{neg(m),rhs},"forward-direction","schema");
    Node reverse=make("or",{neg(rhs),m},"reverse-direction","schema");
    Node root=conjunction(forward,reverse,"equivalence-conjunction");
    std::function<int(Node,bool)> arity=[&](Node node,bool simplify){
        if(simplify){
            while(node->kind=="not" && node->children[0]->kind=="not")node=node->children[0]->children[0];
        }
        if(node->kind!="or")return 1;
        int count=0;for(Node child:node->children)count+=arity(child,simplify);return count;
    };
    need(macros.size()==6,"MOD schema block count");int maximal=0,altered=0;
    out<<"{\"record\":\"mod_schema_graph\",\"root\":"<<root->id<<",\"nodes\":[";
    for(size_t j=0;j<nodes.size();j++){
        if(j)out<<',';
        const Formula& node=*nodes[j];
        out<<"{\"id\":"<<node.id<<",\"kind\":\""<<node.kind<<"\",\"label\":\""<<node.label
           <<"\",\"scope\":\""<<node.scope<<"\",\"children\":[";
        for(size_t k=0;k<node.children.size();k++){if(k)out<<',';out<<node.children[k]->id;}
        out<<"]}";
    }
    out<<"],\"schema_blocks\":[";
    for(size_t j=0;j<macros.size();j++){
        int exact=arity(macros[j],false),simplified=arity(macros[j],true);
        maximal=std::max(maximal,exact);altered=std::max(altered,simplified);
        if(j)out<<',';
        out<<"{\"node\":"<<macros[j]->id<<",\"label\":\""<<macros[j]->label
           <<"\",\"maximal_arity\":"<<exact<<",\"after_double_negation_simplification\":"<<simplified<<'}';
    }
    out<<"],\"argument_arities\":[17,19,23]}\n";
    need(maximal==3 && altered==24,"MOD syntax expansion/control");
    std::cout<<"Six MOD-schema blocks, maximal arity 3; premature double-negation simplification gives arity 24.\n";
}
void check_pruned_mod_identity(std::ostream& out){
    int assignments=0;
    for(int p:{2,3,5,7}){
        Ring ring(p,64);Polynomial t=ring.variable(0),a=ring.variable(1),one=ring.constant(1);
        Polynomial b=ring.power(t,p-1),c=ring.power(ring.subtract(t,one),p-1);
        Polynomial m=ring.power(ring.subtract(ring.add(t,a),one),p-1);
        Polynomial left=ring.multiply(a,ring.subtract(one,b));
        Polynomial right=ring.multiply(ring.subtract(one,a),ring.subtract(one,c));
        Polynomial q=ring.multiply(ring.subtract(one,left),ring.subtract(one,right));
        Polynomial forward=ring.multiply(ring.subtract(one,m),q);
        Polynomial reverse=ring.multiply(m,ring.subtract(one,q));
        Polynomial full=ring.subtract(one,ring.multiply(ring.subtract(one,forward),ring.subtract(one,reverse)));
        std::vector<int> domains{p,2};
        Reduction certificate=domain_reduce(ring,full,domains);
        verify_reduction(ring,full,domains,certificate);need(certificate.remainder.empty(),"pruned MOD axiom certificate");
        need(degree(full)<=6*p-2,"MOD macro degree bound");
        Polynomial interpolation=ring.subtract(m,ring.add(ring.multiply(a,b),ring.multiply(ring.subtract(one,a),c)));
        Reduction interp=domain_reduce(ring,interpolation,{p,2});
        verify_reduction(ring,interpolation,domains,interp);need(interp.remainder.empty(),"MOD interpolation domains");
        for(int value=0;value<p;value++)for(int bit=0;bit<=1;bit++){
            need(ring.evaluate(full,{{0,value},{1,bit}})==0,"MOD axiom grid semantics");assignments++;
        }
        out<<"{\"record\":\"pruned_mod_axiom\",\"p\":"<<p<<",\"variables\":[\"t\",\"a\"],\"domain_powers\":["
           <<p<<",2],\"b\":";write_json(out,b);out<<",\"c\":";write_json(out,c);
        out<<",\"m\":";write_json(out,m);out<<",\"left_conjunction_product\":";write_json(out,left);
        out<<",\"right_conjunction_product\":";write_json(out,right);out<<",\"rhs_product\":";write_json(out,q);
        out<<",\"forward_product\":";write_json(out,forward);out<<",\"reverse_product\":";write_json(out,reverse);
        out<<",\"axiom_image\":";write_json(out,full);out<<",\"certificate\":";write_reduction(out,certificate);
        out<<",\"interpolation_error\":";write_json(out,interpolation);
        out<<",\"interpolation_domain_certificate\":";write_reduction(out,interp);out<<"}\n";
    }
    out<<"{\"record\":\"pruned_mod_summary\",\"primes\":4,\"grid_assignments\":"<<assignments<<"}\n";
    std::cout<<"Four pruned MOD-axiom certificates, "<<assignments<<" field/Boolean grid assignments.\n";
}
int main(int argc,char** argv){
    try{
        std::string path;
        for(int j=1;j<argc;j++){
            std::string arg=argv[j];
            if(arg=="--out" && j+1<argc)path=argv[++j];
            else throw std::runtime_error("Usage: check_mod_schema_pruning --out NEW_PATH");
        }
        need(!path.empty() && !std::filesystem::exists(path),"new --out required");
        std::ofstream out(path);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"mod_schema_pruning\",\"arithmetic\":\"exact\"}\n";
        check_field_selectors(out);check_boolean_packing(out);check_schema(out);check_pruned_mod_identity(out);
        out<<"{\"record\":\"summary\",\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failure");return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
