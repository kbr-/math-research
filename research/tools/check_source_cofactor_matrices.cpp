// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact formal MP cofactors, subset-state matrix programs, and scoped controls.
#include "sparse_polynomial.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <numeric>
#include <string>
using namespace sparse_polynomial;
using Affine=std::vector<int>; // constant, then variable coefficients
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
template<class T>void array(std::ostream& out,const std::vector<T>& a){
    out<<'[';for(std::size_t i=0;i<a.size();++i){if(i)out<<',';out<<a[i];}out<<']';
}
Polynomial affine_poly(const Ring& ring,const Affine& a){
    auto result=ring.constant(a[0]);
    for(std::size_t i=1;i<a.size();++i)ring.accumulate(result,ring.variable(int(i-1)),a[i]);
    return result;
}
int weighted_degree(const Polynomial& p,const std::vector<int>& weights){
    int result=0;
    for(const auto& [m,c]:p){
        (void)c;int d=0;for(int v:m)d+=weights.at(v);result=std::max(result,d);
    }
    return result;
}
Polynomial multilinear(const Ring& ring,const Polynomial& p){
    Polynomial result;
    for(const auto& [m,c]:p){
        auto reduced=m;reduced.erase(std::unique(reduced.begin(),reduced.end()),reduced.end());
        ring.accumulate(result,Polynomial{{reduced,c}});
    }
    return result;
}
struct Term{int scalar,module;std::vector<Affine> factors;};
Polynomial expanded(const Ring& ring,const Term& term){
    auto result=ring.constant(term.scalar);
    for(const auto& factor:term.factors)result=ring.multiply(result,affine_poly(ring,factor));
    return result;
}
int programs=0;
Polynomial program(std::ostream& out,const Ring& ring,const std::vector<Term>& terms,
                   const std::vector<int>& order,const std::string& name,bool ml,int delta){
    int width=0,delta_position=-1;
    for(const auto& term:terms)width+=1<<term.factors.size();
    if(delta>=0){
        auto found=std::find(order.begin(),order.end(),delta);
        need(found!=order.end(),"missing delta variable");
        delta_position=int(found-order.begin());
    }
    out<<"{\"type\":\"matrix_program\",\"p\":"<<ring.p<<",\"name\":\""<<name
       <<"\",\"order\":";array(out,order);
    out<<",\"old_variables\":3,\"width\":"<<width<<",\"multilinear_old\":"
       <<(ml?"true":"false")<<",\"delta_variable\":"<<delta<<",\"blocks\":[";
    Polynomial result;int block_id=0;
    for(const auto& term:terms){
        int t=int(term.factors.size()),dimension=1<<t,full=dimension-1;
        std::vector<Polynomial> values(dimension);
        std::vector<int> initial(dimension);
        for(int S=0;S<dimension;++S){
            int c=term.scalar;
            for(int j=0;j<t;++j)if((S>>j)&1)c=ring.residue(c*term.factors[j][0]);
            initial[S]=c;values[S]=ring.constant(c);
        }
        if(block_id)out<<',';
        out<<"{\"term\":"<<block_id++<<",\"dimension\":"<<dimension<<",\"initial\":";
        array(out,initial);out<<",\"final_state\":"<<full<<",\"matrices\":[";
        for(std::size_t position=0;position<order.size();++position){
            int variable=order[position];std::vector<Polynomial> next(dimension);
            bool reduce=variable<3 && (ml || (delta>=0 && int(position)<delta_position));
            bool divide=variable==delta;
            if(position)out<<',';
            out<<"{\"variable\":"<<variable<<",\"entries\":[";
            bool comma=false;
            for(int S=0;S<dimension;++S){
                int available=full^S;
                for(int T=available;;T=(T-1)&available){
                    int coefficient=1;
                    for(int j=0;j<t;++j)if((T>>j)&1)
                        coefficient=ring.residue(coefficient*term.factors[j][variable+1]);
                    int d=__builtin_popcount(unsigned(T));
                    if(coefficient){
                        int low=d,high=d;
                        if(divide){low=0;high=d-2;}
                        else if(reduce){low=high=d?1:0;}
                        for(int exponent=low;exponent<=high;++exponent){
                            if(comma)out<<',';
                            comma=true;
                            out<<'['<<S<<','<<(S|T)<<','<<exponent<<','<<coefficient<<']';
                            auto multiplier=Polynomial{{Monomial(exponent,variable),coefficient}};
                            ring.accumulate(next[S|T],ring.multiply(values[S],multiplier));
                        }
                    }
                    if(T==0)break;
                }
            }
            out<<"]}";values=std::move(next);
        }
        out<<"]}";ring.accumulate(result,values[full]);
    }
    out<<"],\"output\":";write_json(out,result);out<<"}\n";++programs;
    return result;
}
std::vector<Polynomial> split_placeholders(const Ring& ring,const Polynomial& C,int modules){
    std::vector<Polynomial> result(modules);
    for(const auto& [m,c]:C){
        Monomial q;int placeholder=-1;
        for(int v:m){
            if(v>=3){need(placeholder<0,"not linear in placeholders");placeholder=v-3;}
            else q.push_back(v);
        }
        need(placeholder>=0 && placeholder<modules,"missing placeholder");
        ring.accumulate(result[placeholder],Polynomial{{q,c}});
    }
    return result;
}
void source_fixture(std::ostream& out,int p){
    Ring ring(p,32);constexpr int old=3,modules=14,variables=17;
    auto one=ring.constant(1);std::vector<Affine> values(15,Affine(variables+1));
    for(int i=0;i<14;++i){
        values[i][0]=i%p;values[i][1]=1;values[i][2]=i&1;values[i][3]=(i>>1)&1;
    }
    values[1]=values[0];values[14][0]=1;
    std::vector<Polynomial> v;
    for(const auto& a:values)v.push_back(affine_poly(ring,a));
    std::vector<std::pair<int,int>> children={{0,1},{2,3},{4,5},{6,7},{8,9},{10,11},{12,13}};
    std::vector<Polynomial> H(modules);
    H[0]=v[0];for(int i=2;i<8;++i)H[i-1]=v[i];
    for(int i=8;i<15;++i){
        auto [a,c]=children[i-8];
        H[i-1]=ring.subtract(ring.add(v[c],ring.multiply(v[a],v[i])),v[i]);
    }
    using TermsByModule=std::vector<std::vector<Term>>;
    std::vector<TermsByModule> factored(15,TermsByModule(modules));
    std::vector<std::vector<Polynomial>> Q(15,std::vector<Polynomial>(modules));
    for(int i=0;i<8;++i){
        int id=i<2?0:i-1;
        factored[i][id].push_back({1,id,{}});Q[i][id]=one;
    }
    for(int i=8;i<15;++i){
        auto [a,c]=children[i-8];int own=i-1;
        for(int j=0;j<modules;++j){
            factored[i][j]=factored[c][j];
            for(auto term:factored[a][j]){
                term.factors.push_back(values[i]);factored[i][j].push_back(std::move(term));
            }
            Q[i][j]=ring.add(Q[c][j],ring.multiply(v[i],Q[a][j]));
        }
        factored[i][own].push_back({ring.residue(-1),own,{}});
        ring.accumulate(Q[i][own],one,-1);
    }
    for(int i=0;i<15;++i){
        Polynomial sum;
        for(int j=0;j<modules;++j)ring.accumulate(sum,ring.multiply(Q[i][j],H[j]));
        need(sum==v[i],"MP recurrence identity");
    }
    std::vector<int> weights={1,2,4};
    std::vector<int> costs;
    for(const auto& h:H){int cost=weighted_degree(h,weights)+2;costs.push_back(cost);}
    weights.insert(weights.end(),costs.begin(),costs.end());
    std::vector<Term> terms;Polynomial C;
    for(int j=0;j<modules;++j){
        Polynomial q;
        for(auto term:factored[14][j]){
            ring.accumulate(q,expanded(ring,term));
            Affine placeholder(variables+1);placeholder[old+j+1]=1;
            term.factors.push_back(placeholder);terms.push_back(std::move(term));
        }
        need(q==Q[14][j],"path expansion");
        ring.accumulate(C,ring.multiply(q,ring.variable(old+j)));
    }
    need(terms.size()==15,"contribution count");
    std::map<int,Polynomial> substitution;
    for(int j=0;j<modules;++j)substitution[old+j]=H[j];
    need(ring.substitute(C,substitution)==one,"formal IPS identity");
    int budget=weighted_degree(C,weights);
    auto ML=multilinear(ring,C);need(ML!=C,"vacuous Boolean correction");
    out<<"{\"type\":\"source_fixture\",\"p\":"<<p<<",\"old_variables\":3,"
           "\"proof_height\":3,\"proof_nodes\":15,\"modules\":[";
    for(int j=0;j<modules;++j){if(j)out<<',';write_json(out,H[j]);}
    out<<"],\"module_costs\":";array(out,costs);
    out<<",\"variable_weights\":";array(out,weights);
    out<<",\"budget\":"<<budget<<",\"cofactors\":[";
    for(int j=0;j<modules;++j){if(j)out<<',';write_json(out,Q[14][j]);}
    out<<"],\"certificate\":";write_json(out,C);
    out<<",\"multilinear_certificate\":";write_json(out,ML);
    out<<",\"factored_terms\":[";
    for(std::size_t i=0;i<terms.size();++i){
        if(i)out<<',';
        out<<"{\"scalar\":"<<terms[i].scalar<<",\"module\":"<<terms[i].module<<",\"factors\":[";
        for(std::size_t j=0;j<terms[i].factors.size();++j){if(j)out<<',';array(out,terms[i].factors[j]);}
        out<<"]}";
    }
    out<<"],\"scope\":\"formal MP identity with declared cost labels, not instantiated ENS witnesses\"}\n";
    std::vector<std::vector<int>> orders(3,std::vector<int>(variables));
    std::iota(orders[0].begin(),orders[0].end(),0);
    orders[1]=orders[0];std::reverse(orders[1].begin(),orders[1].end());
    for(int i=0;i<variables;++i)orders[2][i]=(5*i)%variables;
    for(int order=0;order<3;++order){
        auto ordinary=program(out,ring,terms,orders[order],"ordinary_order"+std::to_string(order),false,-1);
        auto reduced=program(out,ring,terms,orders[order],"multilinear_order"+std::to_string(order),true,-1);
        need(ordinary==C && reduced==ML,"matrix program equality");
    }
    Polynomial difference,formal_refutation=ring.substitute(ML,substitution);
    std::vector<Polynomial> old_field_cofactors;
    for(int variable=0;variable<old;++variable){
        auto D=program(out,ring,terms,orders[0],"delta"+std::to_string(variable),false,variable);
        auto z=ring.variable(variable),field=ring.subtract(ring.multiply(z,z),z);
        need(weighted_degree(D,weights)+2*weights[variable]<=budget || D.empty(),"weighted correction budget");
        ring.accumulate(difference,ring.multiply(D,field));
        auto parts=split_placeholders(ring,D,modules);Polynomial B;
        for(int j=0;j<modules;++j)ring.accumulate(B,ring.multiply(parts[j],H[j]));
        ring.accumulate(formal_refutation,ring.multiply(B,field));
        old_field_cofactors.push_back(std::move(B));
    }
    need(difference==ring.subtract(C,ML) && formal_refutation==one,"Boolean correction identity");
    out<<"{\"type\":\"Boolean_correction\",\"p\":"<<p<<",\"old_field_cofactors\":[";
    for(std::size_t i=0;i<old_field_cofactors.size();++i){
        if(i)out<<',';
        write_json(out,old_field_cofactors[i]);
    }
    out<<"],\"budget\":"<<budget<<",\"verified\":true}\n";
    if(p==3){
        std::map<int,int> point;
        for(int i=0;i<variables;++i)point[i]=0;
        point[0]=2;point[3]=1;
        need(ring.residue(ring.evaluate(C,point)-ring.evaluate(ML,point))==2,"nonBoolean point");
        out<<"{\"type\":\"ordinary_vs_Boolean_control\",\"p\":3,\"old_values\":[2,0,0],"
               "\"placeholder_one\":0,\"other_placeholders\":0,\"difference\":2}\n";
    }
    std::cout<<"F"<<p<<": 15 MP nodes, 15 factored contributions, 9 matrix programs, budget "<<budget<<".\n";
}
void realization_control(std::ostream& out,int h){
    Ring ring(2,64);auto one=ring.constant(1),P=one;
    std::vector<Polynomial> inputs,factors;
    for(int i=0;i<h;++i){
        auto sum=ring.add(ring.variable(i),ring.variable(h+i));
        inputs.push_back(ring.add(one,sum));P=ring.multiply(P,sum);
    }
    for(int u=0;u<h;++u){
        auto factor=one;
        for(int j=0;j<h;++j)
            ring.accumulate(factor,ring.multiply(ring.variable(2*h+u*h+j),inputs[j]),-1);
        factors.push_back(factor);
    }
    std::map<int,Polynomial> scalar;
    for(int u=0;u<h;++u)for(int j=0;j<h;++j)scalar[2*h+u*h+j]=ring.constant(u==j);
    auto image=one;for(const auto& factor:factors)image=ring.multiply(image,ring.substitute(factor,scalar));
    need(image==P && degree(P)==h && P.size()==std::size_t(1<<h),"selector image");
    out<<"{\"type\":\"selector_realization_control\",\"accuracy\":"<<h
       <<",\"original_product_degree\":"<<2*h<<",\"formal_selector_width\":1,\"inputs\":[";
    for(int i=0;i<h;++i){if(i)out<<',';write_json(out,inputs[i]);}
    out<<"],\"factored_original_product\":[";
    for(int i=0;i<h;++i){if(i)out<<',';write_json(out,factors[i]);}
    out<<"],\"coefficient_map\":\"r[u,j]=1 iff u=j; all other own coefficients zero\","
           "\"image\":";write_json(out,P);
    out<<",\"cut_order\":\"all x variables, then all y variables\","
           "\"coefficient_matrix_rows\":[";
    for(int A=0;A<(1<<h);++A){
        int B=((1<<h)-1)^A;Monomial monomial;
        for(int j=0;j<h;++j){
            if((A>>j)&1)monomial.push_back(j);
            if((B>>j)&1)monomial.push_back(h+j);
        }
        std::sort(monomial.begin(),monomial.end());
        need(P.count(monomial) && P.at(monomial)==1,"permutation matrix coefficient");
        if(A)out<<',';
        out<<'['<<A<<','<<B<<",1]";
    }
    out<<"],\"rank\":"<<(1<<h)<<",\"companion_certificates\":[";
    for(int i=0;i<h;++i){
        auto q=ring.constant(-1);
        for(int j=0;j<h;++j)if(j!=i)
            q=ring.multiply(q,ring.add(ring.variable(j),ring.variable(h+j)));
        auto target=ring.multiply(inputs[i],P);Polynomial sum;
        if(i)out<<',';
        out<<"{\"input\":"<<i<<",\"target\":";write_json(out,target);
        out<<",\"witness_degree\":"<<h+1<<",\"original_budget\":"<<2*h+1<<",\"terms\":[";
        for(int j=0;j<2;++j){
            int variable=j?h+i:i;auto x=ring.variable(variable);
            auto axiom=ring.subtract(ring.multiply(x,x),x);
            ring.accumulate(sum,ring.multiply(q,axiom));
            if(j)out<<',';
            out<<"{\"cofactor\":";write_json(out,q);
            out<<",\"axiom\":";write_json(out,axiom);out<<'}';
        }
        need(sum==target,"realization companion certificate");out<<"]}";
    }
    out<<"]}\n";
}
void field_controls(std::ostream& out){
    for(int p:{2,3,5,7})for(int n:{4,8,16}){
        std::vector<int> residues,zeros;
        for(int weight=0;weight<=n;++weight){
            int value=(n+1-weight)%p;residues.push_back(value);
            if(value==0)zeros.push_back(weight);
        }
        need(zeros.empty()==(p>n+1),"subset-sum field condition");
        out<<"{\"type\":\"subset_sum_field_control\",\"p\":"<<p<<",\"n\":"<<n
           <<",\"value_by_Hamming_weight\":";array(out,residues);
        out<<",\"zero_weights\":";array(out,zeros);
        out<<",\"unsatisfiable\":"<<(zeros.empty()?"true":"false")<<"}\n";
    }
}
int nested_realization(std::ostream& out,int h){
    Ring ring(2,64);int pairs=h*h,modifier=2*pairs,fresh=modifier+1;
    auto one=ring.constant(1),P=one;
    std::vector<Polynomial> sums,child_values;
    std::vector<std::vector<Polynomial>> child_inputs,child_factors;
    std::map<int,Polynomial> scalar;
    for(int b=0;b<h;++b){
        auto value=one;std::vector<Polynomial> inputs,factors;
        for(int j=0;j<h;++j){
            int i=b*h+j;
            auto s=ring.add(ring.variable(i),ring.variable(pairs+i));
            sums.push_back(s);value=ring.multiply(value,s);inputs.push_back(ring.add(one,s));
        }
        for(int u=0;u<h;++u){
            auto factor=one;
            for(int j=0;j<h;++j){
                int id=fresh++;scalar[id]=ring.constant(u==j);
                ring.accumulate(factor,ring.multiply(ring.variable(id),inputs[j]),-1);
            }
            factors.push_back(factor);
        }
        auto actual=one;
        for(const auto& factor:factors)actual=ring.multiply(actual,ring.substitute(factor,scalar));
        need(actual==value,"nested child image");
        child_inputs.push_back(inputs);child_factors.push_back(factors);
        child_values.push_back(value);P=ring.multiply(P,value);
    }
    std::vector<Polynomial> parent_inputs,parent_factors;
    std::map<int,Polynomial> realize=scalar;realize[modifier]=ring.constant(0);
    for(int b=0;b<h;++b){
        int selector=1000+b;realize[selector]=child_values[b];
        parent_inputs.push_back(ring.add(ring.subtract(one,ring.variable(selector)),ring.variable(modifier)));
    }
    for(int u=0;u<h;++u){
        auto factor=one;
        for(int b=0;b<h;++b){
            int id=fresh++;realize[id]=ring.constant(u==b);
            ring.accumulate(factor,ring.multiply(ring.variable(id),parent_inputs[b]),-1);
        }
        parent_factors.push_back(factor);
    }
    auto actual_parent=one;
    for(const auto& factor:parent_factors)
        actual_parent=ring.multiply(actual_parent,ring.substitute(factor,realize));
    need(actual_parent==P && P.size()==std::size_t(1<<pairs),"nested parent image");
    out<<"{\"type\":\"nested_selector_realization_control\",\"accuracy\":"<<h
       <<",\"pair_count\":"<<pairs<<",\"modifier_variable\":"<<modifier
       <<",\"child_selector_ids_start\":1000,\"original_parent_product_degree\":"<<h*(2*h+1)
       <<",\"original_parent_companion_degree\":"<<2*h*h+3*h
       <<",\"formal_parent_selector_width\":1,\"child_inputs\":[";
    for(int b=0;b<h;++b){
        if(b)out<<',';
        out<<'[';
        for(int j=0;j<h;++j){if(j)out<<',';write_json(out,child_inputs[b][j]);}
        out<<']';
    }
    out<<"],\"child_product_factors\":[";
    for(int b=0;b<h;++b){
        if(b)out<<',';
        out<<'[';
        for(int u=0;u<h;++u){if(u)out<<',';write_json(out,child_factors[b][u]);}
        out<<']';
    }
    out<<"],\"parent_inputs_in_child_selectors\":[";
    for(int b=0;b<h;++b){if(b)out<<',';write_json(out,parent_inputs[b]);}
    out<<"],\"parent_product_factors\":[";
    for(int u=0;u<h;++u){if(u)out<<',';write_json(out,parent_factors[u]);}
    out<<"],\"specialization\":\"identity coefficient rows in each block and modifier=0; child selectors use their saved product definitions\","
           "\"image\":";write_json(out,P);
    out<<",\"coefficient_matrix_rows\":[";
    for(int A=0;A<(1<<pairs);++A){
        int B=((1<<pairs)-1)^A;Monomial m;
        for(int i=0;i<pairs;++i){
            if((A>>i)&1)m.push_back(i);
            if((B>>i)&1)m.push_back(pairs+i);
        }
        std::sort(m.begin(),m.end());
        need(P.count(m) && P.at(m)==1,"nested cut matrix");
        if(A)out<<',';
        out<<'['<<A<<','<<B<<",1]";
    }
    out<<"],\"rank\":"<<(1<<pairs)<<",\"companion_certificates\":[";
    int count=0;
    auto witness=[&](const std::string& name,const Polynomial& target,
                     const std::vector<std::pair<Polynomial,int>>& terms,int bound){
        Polynomial sum;int degree_used=0;
        if(count)out<<',';
        out<<"{\"name\":\""<<name<<"\",\"target\":";write_json(out,target);
        out<<",\"original_budget\":"<<bound<<",\"terms\":[";
        for(std::size_t k=0;k<terms.size();++k){
            auto [q,v]=terms[k];auto x=ring.variable(v);
            auto axiom=ring.subtract(ring.multiply(x,x),x);
            auto product=ring.multiply(q,axiom);ring.accumulate(sum,product);
            degree_used=std::max(degree_used,degree(product));
            if(k)out<<',';
            out<<"{\"cofactor\":";write_json(out,q);
            out<<",\"axiom\":";write_json(out,axiom);out<<'}';
        }
        need(sum==target && degree_used<=bound,"nested companion witness");
        out<<"],\"witness_degree\":"<<degree_used<<'}';++count;
    };
    for(int b=0;b<h;++b)for(int j=0;j<h;++j){
        auto q=ring.constant(-1);
        for(int k=0;k<h;++k)if(k!=j)q=ring.multiply(q,sums[b*h+k]);
        int i=b*h+j;
        witness("child"+std::to_string(b)+"/input"+std::to_string(j),
                ring.multiply(child_inputs[b][j],child_values[b]),{{q,i},{q,pairs+i}},2*h+1);
    }
    for(int b=0;b<h;++b){
        std::vector<std::pair<Polynomial,int>> terms;
        for(int j=0;j<h;++j){
            auto q=ring.constant(-1);
            for(int c=0;c<h;++c)if(c!=b)q=ring.multiply(q,child_values[c]);
            for(int k=0;k<h;++k)if(k!=j)
                q=ring.multiply(q,ring.power(sums[b*h+k],k<j?2:1));
            terms.push_back({q,b*h+j});terms.push_back({q,pairs+b*h+j});
        }
        witness("parent/input"+std::to_string(b),
                ring.multiply(ring.subtract(one,child_values[b]),P),terms,2*h*h+3*h);
    }
    out<<"],\"companion_certificate_count\":"<<count<<"}\n";
    return count;
}
int main(int argc,char** argv){
    try{
        need((argc==3 || (argc==4 && std::string(argv[3])=="--nested")) &&
             std::string(argv[1])=="--out","usage: --out NEW_PATH [--nested]");
        bool nested=argc==4;
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"refusing existing output");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot create output");
        out<<"{\"type\":\"schema\",\"version\":1,\"matrix_entries\":\"[from,to,power,coefficient]; omitted entries zero\","
               "\"program_blocks\":\"direct sum, with the displayed initial vectors and final states\","
               "\"polynomials\":\"coefficient and ordinary variable-list pairs\",\"randomness\":\"none\"}\n";
        source_fixture(out,2);source_fixture(out,3);
        for(int h:{4,6,8})realization_control(out,h);
        int nested_certificates=0;
        if(nested)for(int h:{2,3})nested_certificates+=nested_realization(out,h);
        field_controls(out);need(programs==18,"program count");
        out<<"{\"type\":\"summary\",\"source_fixtures\":2,\"matrix_programs\":18,\"selector_controls\":3,"
               "\"companion_image_certificates\":18,\"field_scope_cases\":12";
        if(nested){
            need(nested_certificates==18,"nested certificate count");
            out<<",\"nested_selector_controls\":2,\"nested_companion_certificates\":"<<nested_certificates;
        }
        out<<",\"passed\":true}\n";
        out.close();need(bool(out),"write failed");
        std::cout<<"Passed 18 complete matrix programs, three selector controls, and twelve field-scope cases.\n";
        if(nested)std::cout<<"Also passed two source-shaped depth-two controls, ranks 16 and 512, with 18 complete companion certificates.\n";
    }catch(const std::exception& error){std::cerr<<"ERROR: "<<error.what()<<'\n';return 1;}
}
