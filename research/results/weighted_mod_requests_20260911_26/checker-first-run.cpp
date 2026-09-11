// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Complete signed MOD-to-disjunction PC joins and fresh-frontier zero replay.
#include "pc_boundary.hpp"
using namespace boundary_pc;

template<class AxiomImage>
int weighted(const Proof& src,int final,Proof& dst,const Poly& weight,AxiomImage axiom) {
    std::vector<int> ids;
    for(const auto& line:src.lines) {
        int id=-1;
        if(line.rule=='a')id=axiom(line.a);
        else if(line.rule=='l')id=dst.lc(line.a<0?-1:ids.at(line.a),line.b<0?-1:ids.at(line.b),line.ca,line.cb);
        else id=dst.mv(line.a<0?-1:ids.at(line.a),line.v);
        need(dst.val(id)==weight*line.value,"weighted join mismatch");ids.push_back(id);
    }
    return final<0?-1:ids.at(final);
}
int zero_replay(const Proof& src,int final,Proof& dst,int first) {
    std::array<int,NV> zero{};std::vector<int> ids;
    for(const auto& line:src.lines) {
        int id=-1;
        if(line.rule=='a') {
            Poly q=specialize(src.axioms.at(line.a),first,zero);
            if(!q.terms.empty()) {
                auto found=std::find(dst.axioms.begin(),dst.axioms.end(),q);
                need(found!=dst.axioms.end(),"image is neither an old axiom nor a goal input");
                id=dst.ax(int(found-dst.axioms.begin()));
            }
        } else if(line.rule=='l')
            id=dst.lc(line.a<0?-1:ids.at(line.a),line.b<0?-1:ids.at(line.b),line.ca,line.cb);
        else if(line.v<first)id=dst.mv(line.a<0?-1:ids.at(line.a),line.v);
        need(dst.val(id)==specialize(line.value,first,zero),"zero replay mismatch");ids.push_back(id);
    }
    return final<0?-1:ids.at(final);
}
void trace(std::ostream& out,const std::string& name,const Proof& proof,int final,
           const Poly& target,int bound,int old_variables=-1) {
    need(proof.val(final)==target && proof.verify() && proof.degree<=bound,"proof: "+name);
    need(final>=0 && !proof.verify(final),"corruption control");
    if(old_variables>=0)for(const auto& l:proof.lines)need(l.value.old(old_variables),"removed variable remains");
    std::vector<bool> used(proof.lines.size(),false);used.at(final)=true;
    std::vector<bool> ax(proof.axioms.size(),false);int cone_degree=0,cone_lines=0;
    for(int j=int(proof.lines.size())-1;j>=0;j--)if(used[j]) {
        cone_lines++;const auto& line=proof.lines[j];cone_degree=std::max(cone_degree,line.value.deg());
        if(line.rule=='a')ax[line.a]=true;
        else {if(line.a>=0)used[line.a]=true;if(line.rule=='l' && line.b>=0)used[line.b]=true;}
    }
    proof.write(out,name,final);
    out<<"{\"record\":\"verified\",\"name\":\""<<name<<"\",\"whole_trace_degree\":"<<proof.degree
       <<",\"bound\":"<<bound<<",\"final_cone_degree\":"<<cone_degree
       <<",\"final_cone_lines\":"<<cone_lines<<",\"used_axioms\":[";
    bool comma=false;for(size_t i=0;i<ax.size();i++)if(ax[i]) {if(comma)out<<',';comma=true;out<<i;}
    out<<"],\"corruption_rejected\":true}\n";
}
void fixture(std::ostream& out,int id,int p,int width,int h,int count,bool multiple) {
    const int old_variables=multiple?count:width;int next=old_variables;
    Poly one(p,1),sum(p);std::vector<Block> blocks;std::vector<Poly> goal;
    for(int j=0;j<count;j++) {
        std::vector<Poly> inputs;
        if(multiple) {auto x=variable(p,j);inputs={x,one-x};}
        else for(int i=0;i<width;i++)inputs.push_back(variable(p,i));
        blocks.push_back(block(inputs,h,next));sum=sum+blocks.back().product;
        goal.insert(goal.end(),inputs.begin(),inputs.end());
    }
    need(count%p!=0,"fixture needs nonzero true-argument residue");
    std::vector<int> sizes(next,p);for(int i=0;i<old_variables;i++)sizes[i]=2;
    auto axioms=domains(p,sizes);int base=-1;
    if(!multiple) {base=int(axioms.size());axioms.push_back(variable(p,0)-one);}
    std::vector<int> starts;
    for(const auto& b:blocks) {starts.push_back(int(axioms.size()));axioms.insert(axioms.end(),b.axioms.begin(),b.axioms.end());}
    auto old=domains(p,std::vector<int>(old_variables,2));
    if(!multiple)old.push_back(variable(p,0)-one);
    auto clean_axioms=old;clean_axioms.insert(clean_axioms.end(),goal.begin(),goal.end());
    out<<"{\"record\":\"case\",\"id\":"<<id<<",\"p\":"<<p<<",\"accuracy\":"<<h
       <<",\"frontier_blocks\":"<<count<<",\"multiple\":"<<(multiple?"true":"false")
       <<",\"old_variables\":"<<old_variables<<",\"goal_inputs\":[";
    for(size_t i=0;i<goal.size();i++) {if(i)out<<',';jsonpoly(out,goal[i]);}
    out<<"],\"blocks\":[";
    for(size_t j=0;j<blocks.size();j++) {
        if(j)out<<',';
        const auto& b=blocks[j];out<<"{\"first_variable\":"<<b.first<<",\"end_variable\":"<<b.end
           <<",\"first_companion_axiom\":"<<starts[j]<<",\"product\":";jsonpoly(out,b.product);
        out<<",\"prefixes\":[";for(size_t i=0;i<b.coef.size();i++) {if(i)out<<',';jsonpoly(out,b.coef[i]);}
        out<<"]}";
    }
    out<<"],\"old_base_satisfiable\":true,\"source_scope\":\"complete algebraic MP interface; no primitive Frege compiler\"}\n";
    for(bool negative:{false,true}) {
        const int residue=negative?0:count%p;
        Poly u=sum-Poly(p,count-residue);
        auto source_axioms=axioms;
        if(negative)source_axioms.push_back(u);
        Proof source(p,source_axioms);int sum_proof=-1;
        for(size_t j=0;j<blocks.size();j++) {
            int pj=source.ax(starts[j]);
            if(multiple)pj=source.lc(pj,source.ax(starts[j]+1));
            else pj=source.lc(pj,source.mul(source.ax(base),blocks[j].product),1,-1);
            need(source.val(pj)==blocks[j].product,"argument value proof");sum_proof=source.lc(sum_proof,pj);
        }
        int final=sum_proof;
        if(negative)final=source.lc(sum_proof,source.ax(int(axioms.size())),modpow(count%p,p-2,p),-modpow(count%p,p-2,p));
        std::string sign=negative?"negative":"positive";
        trace(out,sign+"_scalar",source,final,negative?one:u,2*h+1);

        auto joined_axioms=axioms;joined_axioms.insert(joined_axioms.end(),goal.begin(),goal.end());
        Proof joined(p,joined_axioms);Poly power=powp(u,p-1),alpha=negative?one-power:power;
        int value=-1;
        if(negative) {
            value=weighted(source,final,joined,alpha,[&](int a) {
                return a<int(axioms.size())?joined.mul(joined.ax(a),alpha):field_proof(joined,alpha*u,sizes);
            });
        } else {
            int scalar=weighted(source,final,joined,one,[&](int a){return joined.ax(a);});
            value=joined.mul(scalar,powp(u,p-2));
        }
        need(joined.val(value)==alpha,"antecedent conversion");
        Poly Q(p);
        if(negative)Q=Poly(p,-1)*powp(u,p-2);
        else for(int j=0;j<p-1;j++)Q=Q+Poly(p,modpow(residue,j,p))*powp(u,p-2-j);
        Poly identity=alpha;int unit=value,coordinate=0;
        for(const auto& b:blocks)for(size_t i=0;i<b.inputs.size();i++) {
            auto co=Q*b.coef[i];identity=identity+co*b.inputs[i];
            unit=joined.lc(unit,joined.mul(joined.ax(int(axioms.size())+coordinate++),co));
        }
        need(identity==one,"implication input unit identity");
        int bound=source.degree+(p-1)*u.deg();
        out<<"{\"record\":\"implication_unit\",\"sign\":\""<<sign<<"\",\"residue\":"<<residue
           <<",\"scalar\":";jsonpoly(out,u);out<<",\"antecedent_value\":";jsonpoly(out,alpha);
        out<<",\"common_prefix_multiplier\":";jsonpoly(out,Q);out<<"}\n";
        trace(out,sign+"_joined_mp",joined,unit,one,bound);
        Proof late(p,clean_axioms);int late_unit=zero_replay(joined,unit,late,old_variables);
        trace(out,sign+"_joined_then_zero",late,late_unit,one,joined.degree,old_variables);
        Proof direct(p,clean_axioms);int direct_unit=zero_replay(source,final,direct,old_variables);
        if(!negative)direct_unit=direct.lc(direct_unit,-1,modpow(residue,p-2,p),0);
        trace(out,sign+"_direct_frontier",direct,direct_unit,one,source.degree,old_variables);
    }
}
void controls(std::ostream& out) {
    for(int p:{2,3,5})for(bool negative:{false,true}) {
        int residue=negative?1:0;
        int value=modpow(residue,p-1,p);if(negative)value=(1-value+p)%p;
        need(value==0,"invalid residue must permit a true antecedent with all arguments false");
        out<<"{\"record\":\"invalid_residue\",\"p\":"<<p<<",\"negative\":"<<(negative?"true":"false")
           <<",\"residue\":"<<residue<<",\"all_argument_products\":1,\"all_goal_inputs\":0,"
             "\"antecedent_value\":0,\"disjunction_value\":1}\n";
    }
    for(int p:{2,3}) {
        Poly one(p,1),x=variable(p,0),s=variable(p,1),r=variable(p,2);
        Poly a=one-r*x,later=a*(one-s*a);std::array<int,NV> zero{};
        auto image=specialize(later,2,zero);
        need(!later.old(2) && image==one-s && !(image==later),"later-axiom freshness control");
        std::array<int,NV> point{};point[0]=1;point[2]=1;
        need(specialize(later,0,point).terms.empty() && specialize(image,0,point)==one,"later-image model");
        out<<"{\"record\":\"nonfresh_retained_axiom\",\"p\":"<<p<<",\"variables\":[\"x\",\"s\",\"r\"],"
             "\"original\":";jsonpoly(out,later);out<<",\"r_zero_image\":";jsonpoly(out,image);
        out<<",\"point\":[1,0,1],\"original_value\":0,\"image_value\":1,"
             "\"scope\":\"unchanged-retained-system claim fails; not an obstruction to a repaired specialization\"}\n";
    }
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");
        auto parent=std::filesystem::path(argv[2]).parent_path();if(!parent.empty())std::filesystem::create_directories(parent);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"mod_frontier_replay\",\"seed\":null}\n";
        int id=0;
        for(int p:{2,3}) {fixture(out,id++,p,3,1,1,false);fixture(out,id++,p,5,1,1,false);fixture(out,id++,p,2,2,1,false);}
        for(int k:{3,5})fixture(out,id++,2,2,1,k,true);
        for(int k:{2,4})fixture(out,id++,3,2,1,k,true);
        for(int k:{2,3})fixture(out,id++,5,2,1,k,true);
        controls(out);
        out<<"{\"record\":\"summary\",\"cases\":12,\"pc_traces\":96,\"scope_controls\":8,\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failed");
        std::cout<<"Twelve fresh-frontier cases, 96 PC traces, and eight scope controls passed.\n";
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
