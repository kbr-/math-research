// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Complete row-state source images and the PHP density-completion control.
#include "ns_witness.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace ens_symbolic;
void need(bool b, const char* why) { if (!b) throw std::runtime_error(why); }
int gf4mul(int a, int b) {
    int result = 0;
    for (; b; b >>= 1) { if (b & 1) result ^= a; a <<= 1; if (a & 4) a ^= 7; }
    return result;
}
struct RowBase {
    const Ring& ring;
    int labels, offset, row_id;
    std::vector<Polynomial> axioms;
    std::map<std::pair<int,int>,int> exclusions;
    RowBase(const Ring& r, int n, int off): ring(r), labels(n), offset(off) {
        Polynomial rho;
        for (int j = 0; j < labels; ++j) {
            auto x = ring.variable(offset+j); ring.accumulate(rho, x);
            axioms.push_back(ring.subtract(ring.multiply(x,x),x));
        }
        for (int j = 0; j < labels; ++j) for (int k = j+1; k < labels; ++k) {
            exclusions[{offset+j,offset+k}] = int(axioms.size());
            axioms.push_back(ring.multiply(ring.variable(offset+j),ring.variable(offset+k)));
        }
        row_id = int(axioms.size());
        axioms.push_back(ring.subtract(rho,ring.constant(1)));
    }
    std::map<int,Polynomial> prove(const Polynomial& target) const {
        std::map<int,Polynomial> proof; Polynomial normal;
        for (const auto& [original,c]: target) {
            Monomial m = original;
            for (int v: m) need(v>=offset && v<offset+labels,"nonold variable in row certificate");
            if (!m.empty() && m.front()!=m.back()) {
                int a=m.front(), b=m.back(); Monomial q=m;
                q.erase(std::find(q.begin(),q.end(),a)); q.erase(std::find(q.begin(),q.end(),b));
                ring.accumulate(proof[exclusions.at({a,b})],Polynomial{{q,c}}); continue;
            }
            while (m.size()>1) {
                int v=m.front(); Monomial q=m; q.pop_back(); q.pop_back();
                ring.accumulate(proof[v-offset],Polynomial{{q,c}}); m.pop_back();
            }
            ring.accumulate(normal,Polynomial{{m,c}});
        }
        int constant=0;
        auto where=normal.find(Monomial{}); if (where!=normal.end()) constant=where->second;
        if (constant) {
            auto multiplier=ring.constant(-constant);
            ring.accumulate(proof[row_id],multiplier);
            ring.accumulate(normal,ring.multiply(multiplier,axioms[row_id]),-1);
        }
        need(normal.empty(),"target does not vanish on row states"); return proof;
    }
};
int main(int argc, char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2]; need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path); need(bool(out),"open output");
        const int bits=6, n=64, offset=1000;
        Ring ring(2,32); RowBase base(ring,n,offset); auto one=ring.constant(1);
        int fresh=bits; std::vector<Polynomial> old_bits;
        for(int i=0;i<bits;++i)old_bits.push_back(ring.variable(i));
        std::vector<Polynomial> a_inputs(old_bits.begin(),old_bits.end()-1);
        auto a=make_block(ring,a_inputs,1,fresh), c=make_block(ring,old_bits,1,fresh);
        std::map<int,Polynomial> sigma;
        for(int i=0;i<bits;++i) {
            Polynomial L;
            for(int z=0;z<n;++z)if((z>>i)&1)ring.accumulate(L,ring.variable(offset+z));
            sigma[i]=L;
        }
        for(const auto* block: {&a,&c}) {
            for(unsigned i=0;i<block->inputs.size();++i) {
                Polynomial profile;
                for(int z=0;z<n;++z) {
                    int first=-1;
                    for(unsigned j=0;j<block->inputs.size();++j)if((z>>j)&1){first=int(j);break;}
                    if(first==int(i))ring.accumulate(profile,ring.variable(offset+z));
                }
                sigma[block->variables[0][i]]=profile;
            }
        }
        auto value_c=ring.variable(offset);
        auto value_a=ring.add(value_c,ring.variable(offset+(1<<(bits-1))));
        auto image_a=ring.substitute(a.product,sigma), image_c=ring.substitute(c.product,sigma);
        out << "{\"record\":\"schema\",\"source_field\":2,\"functional_value_field\":\"GF(4), theta^2+theta+1\","
               "\"element_encoding\":[\"0\",\"1\",\"theta\",\"theta+1\"],\"php_rows\":65,\"php_columns\":64,"
               "\"density_cutoff\":5,\"old_pairing_degree\":10,\"source_degree_budget\":6,\"target_row_offset\":1000,"
               "\"scope\":\"complete local source image certificates; global PHP design and full pairing existence proved in notebook, not numerically constructed\"}\n";
        out << "{\"record\":\"source\",\"A\":"; write_block(out,a);
        out << ",\"C\":"; write_block(out,c);
        out << ",\"own_fields\":\"r^2-r for every listed coefficient\",\"sigma\":[";
        bool comma=false;
        for(const auto& [v,image]:sigma){if(comma)out<<',';comma=true;out<<"{\"variable\":"<<v<<",\"image\":";write_json(out,image);out<<'}';}
        out << "],\"A_image\":";write_json(out,image_a);
        out << ",\"C_image\":";write_json(out,image_c);
        out << ",\"A_value\":";write_json(out,value_a);
        out << ",\"C_value\":";write_json(out,value_c);out<<"}\n";
        out << "{\"record\":\"local_old_axioms\",\"axioms\":";write_polynomials(out,base.axioms);out<<"}\n";
        int certificates=0;
        auto certificate=[&](const std::string& name,const Polynomial& target,int budget) {
            auto proof=base.prove(target);
            out << "{\"record\":\"ns_certificate\",\"name\":\""<<name<<"\",\"original_budget\":"<<budget<<",\"target\":";
            write_json(out,target);ns_witness::write_terms(out,ring,base.axioms,target,proof,budget,name);
            out << ",\"passed\":true}\n";++certificates;
        };
        for(int i=0;i<bits;++i)certificate("old_bit_Booleanity_"+std::to_string(i),ring.subtract(ring.multiply(sigma[i],sigma[i]),sigma[i]),2);
        for(const auto* block:{&a,&c}) {
            std::string name=block==&a?"A":"C";
            for(unsigned i=0;i<block->companions.size();++i)
                certificate(name+"_companion_"+std::to_string(i),ring.substitute(block->companions[i],sigma),3);
            for(int v:block->variables[0])
                certificate(name+"_own_field_"+std::to_string(v),ring.subtract(ring.multiply(sigma[v],sigma[v]),sigma[v]),2);
        }
        certificate("A_canonical_value",ring.subtract(image_a,value_a),2);
        certificate("C_canonical_value",ring.subtract(image_c,value_c),2);
        certificate("A_value_Booleanity",ring.subtract(ring.multiply(value_a,value_a),value_a),2);
        certificate("C_value_Booleanity",ring.subtract(ring.multiply(value_c,value_c),value_c),2);
        auto last_literal=ring.subtract(one,sigma[bits-1]);
        certificate("actual_mixed_port_image",ring.subtract(image_c,ring.multiply(image_a,last_literal)),5);
        certificate("canonical_mixed_port",ring.subtract(value_c,ring.multiply(value_a,last_literal)),2);
        need(certificates==34,"complete certificate count");
        int normalization=0,mixed=0,bad_mixed=0,query_failure=0,bad_annihilator=0,determinant=1;
        out << "{\"record\":\"row_states\",\"states\":[";
        for(int z=0;z<n;++z) {
            if(z)out<<',';
            std::map<int,int> point;
            for(int k=0;k<n;++k)point[offset+k]=z==k;
            int va=ring.evaluate(value_a,point),vc=ring.evaluate(value_c,point);
            int pa=ring.evaluate(image_a,point),pc=ring.evaluate(image_c,point);
            need(va==pa && vc==pc,"canonical image state");
            int weight=z==0?2:z==1?3:1;
            int last=(z>>(bits-1))&1;
            int old_unit=(z==0 || z==1)?1:3;
            int old_corrected=gf4mul(2,old_unit);
            normalization^=weight;determinant=gf4mul(determinant,weight);
            mixed^=gf4mul(weight,vc ^ gf4mul(va,1^last));
            bad_mixed^=gf4mul(weight,old_unit ^ gf4mul(va,1^last));
            if(z==0)query_failure^=gf4mul(weight,old_corrected^vc);
            if(z==1)bad_annihilator^=gf4mul(weight,old_unit);
            out << "{\"label\":"<<z<<",\"functional_weight\":"<<weight<<",\"A_value\":"<<va<<",\"C_value\":"<<vc<<",\"coefficient_values\":[";
            bool more=false;
            for(const auto* block:{&a,&c})for(int v:block->variables[0]) {
                if(more)out<<',';
                more=true;
                int x=ring.evaluate(sigma[v],point);need(x==0 || x==1,"binary coefficient state");
                out << '['<<v<<','<<x<<']';
            }
            out << "]}";
        }
        out << "],\"row_Gram_diagonal\":[";
        for(int z=0;z<n;++z){if(z)out<<',';out<<(z==0?2:z==1?3:1);}
        out << "],\"row_Gram_determinant\":"<<determinant<<",\"row_Gram_rank\":64,\"normalization\":"<<normalization
            <<",\"corrected_mixed_port\":"<<mixed<<",\"old_unit_mixed_error\":"<<bad_mixed
            <<",\"old_corrected_density_new_query_error\":"<<query_failure<<",\"old_unit_new_annihilator_error\":"<<bad_annihilator<<"}\n";
        need(normalization==1 && determinant!=0 && mixed==0,"PHP row-density correction");
        need(bad_mixed==3 && query_failure==1 && bad_annihilator==3,"missing row-state query controls");
        out << "{\"record\":\"summary\",\"ns_certificates\":34,\"local_row_states\":64,\"complete_source_coefficient_fields\":11,\"passed\":true}\n";
        need(bool(out),"write output");
        std::cout << "PHP density completion: 34 ordinary NS certificates, 64 row states, and all query-space controls passed.\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
