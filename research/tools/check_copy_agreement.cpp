// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Ordinary multi-prime COPY and copy-aware MP identities, with explicit cofactors.
#include "ens_symbolic.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace ens_symbolic;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
Polynomial sum_certificate(const Ring& ring,const std::vector<Polynomial>& axioms,
                           const std::vector<Polynomial>& q){
    need(axioms.size()==q.size(),"certificate arity");Polynomial result;
    for(size_t i=0;i<q.size();i++)ring.accumulate(result,ring.multiply(axioms[i],q[i]));
    return result;
}
void write_certificate(std::ostream& out,const Ring& ring,const std::string& kind,int h,
                       const Polynomial& target,const std::vector<Polynomial>& axioms,
                       const std::vector<Polynomial>& q,int ceiling,bool omission){
    need(sum_certificate(ring,axioms,q)==target,"ordinary identity: "+kind);
    int actual=0;
    for(size_t i=0;i<q.size();i++)actual=std::max(actual,degree(ring.multiply(axioms[i],q[i])));
    need(actual<=ceiling,"degree ceiling: "+kind);
    out<<"{\"record\":\""<<kind<<"\",\"p\":"<<ring.p<<",\"h\":"<<h<<",\"target\":";
    write_json(out,target);out<<",\"axioms\":";write_polynomials(out,axioms);
    out<<",\"cofactors\":";write_polynomials(out,q);
    out<<",\"certificate_degree\":"<<actual<<",\"ceiling\":"<<ceiling
       <<",\"omitted_agreement_terms_rejected\":"<<(omission?"true":"false")<<"}\n";
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","Usage: check_copy_agreement --out NEW_PATH");
        std::string path=argv[2];need(!std::filesystem::exists(path),"output must be new");
        std::ofstream out(path);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"copy_agreement\",\"scope\":\"symbolic identities, not Frege proofs\"}\n";
        int copies=0,mp=0,omissions=0;
        for(int p:{2,3,5,7})for(int h:{1,2}){
            Ring ring(p);Polynomial one=ring.constant(1),zero;
            std::vector<Polynomial> g={ring.multiply(ring.variable(0),ring.variable(1)),
                                      ring.subtract(one,ring.variable(2))};
            std::vector<Polynomial> f={ring.add(g[0],ring.variable(3)),ring.add(g[1],ring.variable(4))};
            Polynomial a=ring.multiply(ring.variable(5),ring.variable(6));
            Polynomial alpha=ring.add(a,ring.variable(7));
            int fresh=8;
            Block left=make_block(ring,g,h,fresh);
            out<<"{\"record\":\"blocks\",\"p\":"<<p<<",\"h\":"<<h<<",\"left\":";
            write_block(out,left);out<<",\"old_premise\":";write_json(out,a);
            out<<",\"implication_premise_copy\":";write_json(out,alpha);out<<"}\n";
            for(bool perturbed:{false,true}){
                auto other_inputs=perturbed?f:g;
                Block right=make_block(ring,other_inputs,h,fresh);
                std::vector<Polynomial> axioms=left.companions,q;
                axioms.insert(axioms.end(),right.companions.begin(),right.companions.end());
                for(const auto& v:right.prefix)q.push_back(v);
                for(const auto& v:left.prefix)q.push_back(ring.subtract(zero,v));
                for(size_t i=0;i<g.size();i++){
                    axioms.push_back(ring.subtract(g[i],other_inputs[i]));
                    q.push_back(ring.subtract(zero,ring.add(ring.multiply(right.prefix[i],left.product),
                                                         ring.multiply(left.prefix[i],right.product))));
                }
                Polynomial target=ring.subtract(left.product,right.product);
                bool rejected=false;
                if(perturbed){
                    auto missing=q;missing[4]=zero;missing[5]=zero;
                    rejected=sum_certificate(ring,axioms,missing)!=target;
                    need(rejected,"input-difference omission control");omissions++;
                }
                out<<"{\"record\":\"copy_right_block\",\"p\":"<<p<<",\"h\":"<<h
                   <<",\"perturbed\":"<<(perturbed?"true":"false")<<",\"block\":";
                write_block(out,right);out<<"}\n";
                write_certificate(out,ring,perturbed?"copy_matched_inputs":"copy_literal_inputs",
                                  h,target,axioms,q,6*h,rejected);copies++;
            }
            Block implication=make_block(ring,{alpha,f[0],f[1]},h,fresh);
            Polynomial q_a=ring.multiply(left.product,implication.prefix[0]);
            std::vector<Polynomial> axioms={implication.product,a};
            axioms.insert(axioms.end(),left.companions.begin(),left.companions.end());
            axioms.insert(axioms.end(),implication.companions.begin(),implication.companions.end());
            axioms.push_back(ring.subtract(alpha,a));
            for(size_t i=0;i<g.size();i++)axioms.push_back(ring.subtract(f[i],g[i]));
            std::vector<Polynomial> q={one,q_a,implication.prefix[1],implication.prefix[2],
                                      zero,ring.subtract(zero,left.prefix[0]),ring.subtract(zero,left.prefix[1]),
                                      q_a};
            for(size_t i=0;i<g.size();i++)
                q.push_back(ring.add(ring.multiply(left.product,implication.prefix[i+1]),
                                    ring.multiply(implication.product,left.prefix[i])));
            auto missing=q;for(size_t i=7;i<missing.size();i++)missing[i]=zero;
            need(sum_certificate(ring,axioms,missing)!=left.product,"MP agreement omission control");
            omissions++;
            out<<"{\"record\":\"implication_block\",\"p\":"<<p<<",\"h\":"<<h<<",\"block\":";
            write_block(out,implication);out<<"}\n";
            write_certificate(out,ring,"copy_mp",h,left.product,axioms,q,6*h,true);mp++;
        }
        out<<"{\"record\":\"summary\",\"copy_identities\":"<<copies<<",\"mp_identities\":"<<mp
           <<",\"omission_controls\":"<<omissions<<",\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failure");
        std::cout<<copies<<" copy and "<<mp<<" MP identities; "<<omissions<<" omission controls.\n";
        return 0;
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
