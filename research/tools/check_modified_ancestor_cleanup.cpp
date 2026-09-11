// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Complete PC replay with an inner block removed and its parent retained.
#include "pc_boundary.hpp"
#include <set>
using namespace boundary_pc;

Poly zero_inner(const Poly& f,const Block& inner) {
    Poly result(f.p);
    for(const auto& [mon,coefficient]:f.terms) {
        bool removed=false;
        for(int v=inner.first;v<inner.end;v++)removed=removed || mon[v]!=0;
        if(!removed)result.add(mon,coefficient);
    }
    return result;
}
bool avoids_inner(const Poly& f,const Block& inner) {
    return zero_inner(f,inner)==f;
}
int evaluate(const Poly& f,const std::array<int,NV>& point) {
    int result=0;
    for(const auto& [mon,coefficient]:f.terms) {
        int value=coefficient;
        for(int v=0;v<NV;v++)value=value*modpow(point[v],mon[v],f.p)%f.p;
        result=(result+value)%f.p;
    }
    return result;
}
void point_check(const std::vector<Poly>& axioms,const std::array<int,NV>& point,int omitted=-1) {
    for(size_t i=0;i<axioms.size();i++)if(int(i)!=omitted)
        need(evaluate(axioms[i],point)==0,"point violates a non-omitted axiom");
}
void point_write(std::ostream& out,const std::string& name,const std::array<int,NV>& point,
                 int next,int omitted,int tested,int value) {
    out<<"{\"record\":\"point\",\"name\":\""<<name<<"\",\"omitted_axiom\":"<<omitted
       <<",\"tested_axiom\":"<<tested<<",\"tested_value\":"<<value<<",\"assignment\":[";
    for(int v=0;v<next;v++) {if(v)out<<',';out<<'['<<v<<','<<point[v]<<']';}
    out<<"]}\n";
}
void verify_trace(const Proof& proof,int final,const Poly& target,int bound) {
    need(final>=0 && proof.val(final)==target,"wrong trace target");
    need(proof.degree<=bound && proof.verify(),"trace verification or degree");
    need(!proof.verify(final),"corrupted final line was accepted");
}
void run_case(std::ostream& out,int p,int h,bool complement) {
    Poly one(p,1),x=variable(p,0),y=variable(p,1),z=variable(p,2);
    int next=3;
    Block inner=block({x,y},h,next);
    Poly parent_input=complement?one-inner.product:inner.product;
    Block parent=block({parent_input,z},h,next);
    std::vector<Poly> original;
    std::vector<std::string> kinds;
    auto add=[&](const Poly& f,const std::string& kind) {
        int id=int(original.size());original.push_back(f);kinds.push_back(kind);return id;
    };
    for(int v=0;v<3;v++) {auto a=variable(p,v);add(a*a-a,"old_boolean");}
    std::vector<int> inner_comp,parent_comp,goals;
    std::set<int> inner_fields;
    for(const auto& f:inner.axioms)inner_comp.push_back(add(f,"selected_companion"));
    for(int v=inner.first;v<inner.end;v++) {
        auto a=variable(p,v);inner_fields.insert(add(powp(a,p)-a,"selected_field"));
    }
    for(const auto& f:parent.axioms)parent_comp.push_back(add(f,"retained_ancestor_companion"));
    for(int v=parent.first;v<parent.end;v++) {
        auto a=variable(p,v);add(powp(a,p)-a,"retained_ancestor_field");
    }
    goals.push_back(add(x,"goal_input"));goals.push_back(add(y,"goal_input"));
    Proof source(p,original);
    int difference=-1;
    for(size_t i=0;i<goals.size();i++)
        difference=source.lc(difference,source.mul(source.ax(goals[i]),inner.coef[i]));
    need(source.val(difference)==one-inner.product,"input prefix proof");
    int x_line=source.lc(source.ax(inner_comp[0]),source.mul(difference,x));
    need(source.val(x_line)==x,"selected companion plus input proof");
    int final=source.lc(x_line,source.ax(parent_comp[1]));
    Poly target=x+z*parent.product;
    int source_bound=std::max(inner.product.deg()+1,parent.product.deg()+1);
    verify_trace(source,final,target,source_bound);

    std::vector<Poly> retained;
    std::vector<int> mapping(original.size(),-1);
    for(size_t i=0;i<original.size();i++) {
        if(kinds[i]=="selected_companion" || kinds[i]=="selected_field")continue;
        mapping[i]=int(retained.size());retained.push_back(zero_inner(original[i],inner));
    }
    Proof replayed(p,retained);
    std::vector<int> input_witnesses;
    for(int i:goals)input_witnesses.push_back(replayed.ax(mapping[i]));
    std::vector<int> lines;
    for(const auto& line:source.lines) {
        int id=-1;
        if(line.rule=='a') {
            if(line.a==inner_comp[0])id=input_witnesses[0];
            else if(line.a==inner_comp[1])id=input_witnesses[1];
            else if(inner_fields.count(line.a))need(zero_inner(line.value,inner).terms.empty(),"selected field survives");
            else id=replayed.ax(mapping.at(line.a));
        } else if(line.rule=='l') {
            int a=line.a<0?-1:lines.at(line.a),b=line.b<0?-1:lines.at(line.b);
            id=replayed.lc(a,b,line.ca,line.cb);
        } else {
            int a=line.a<0?-1:lines.at(line.a);
            if(line.v<inner.first || line.v>=inner.end)id=replayed.mv(a,line.v);
        }
        need(replayed.val(id)==zero_inner(line.value,inner),"specialized line mismatch");
        lines.push_back(id);
    }
    int replay_final=lines.at(final);
    Poly specialized_parent=zero_inner(parent.product,inner);
    Poly specialized_target=zero_inner(target,inner);
    verify_trace(replayed,replay_final,specialized_target,2*h+1);
    need(replayed.degree<=std::max(source.degree,1),"common replay ceiling");
    for(const auto& line:replayed.lines)need(avoids_inner(line.value,inner),"removed coefficient remains");
    need(avoids_inner(x,inner) && avoids_inner(y,inner),"named goal changed");

    Poly regenerated(p,1),constant(p,complement?0:1);
    for(int u=0;u<h;u++) {
        auto s=variable(p,parent.first+2*u),t=variable(p,parent.first+2*u+1);
        regenerated=regenerated*(one-s*constant-t*z);
    }
    need(regenerated==specialized_parent && specialized_parent.deg()==2*h,"retained ENS product or degree");
    need(zero_inner(parent_input,inner)==constant,"specialized parent input");
    need(zero_inner(parent.axioms[0],inner)==constant*regenerated,"first retained companion image");
    need(zero_inner(parent.axioms[1],inner)==z*regenerated,"second retained companion image");
    need(!(specialized_parent==parent.product),"parent was not modified");
    need(specialized_target.deg()>0,"fixture target became constant");

    out<<"{\"record\":\"case\",\"p\":"<<p<<",\"accuracy\":"<<h
       <<",\"parent_first_input\":\""<<(complement?"1-P":"P")<<"\",\"inner_variables\":["
       <<inner.first<<','<<inner.end<<"],\"parent_variables\":["<<parent.first<<','<<parent.end
       <<"],\"source_bound\":"<<source_bound<<",\"replayed_bound\":"<<2*h+1<<",\"input_witness_ceiling\":1,\"P\":";
    jsonpoly(out,inner.product);out<<",\"Q\":";jsonpoly(out,parent.product);
    out<<",\"specialized_Q\":";jsonpoly(out,specialized_parent);out<<"}\n";
    source.write(out,"source_target_x_plus_zQ",final);
    replayed.write(out,"replayed_target_x_plus_zQ",replay_final);
    out<<"{\"record\":\"axiom_images\",\"items\":[";
    for(size_t i=0;i<original.size();i++) {
        if(i)out<<',';
        auto image=zero_inner(original[i],inner);
        need(image.deg()<=original[i].deg(),"image increased ordinary degree");
        out<<"{\"original_index\":"<<i<<",\"kind\":\""<<kinds[i]<<"\",\"retained_index\":"<<mapping[i]
           <<",\"original_degree\":"<<original[i].deg()<<",\"image_degree\":"<<image.deg()<<",\"image\":";
        jsonpoly(out,image);out<<'}';
    }
    out<<"]}\n";

    // Original and transformed systems with every goal assumption have a model.
    std::array<int,NV> satisfying{};satisfying[2]=1;satisfying[parent.first+1]=1;
    point_check(original,satisfying);point_check(retained,satisfying);
    need(evaluate(target,satisfying)==0 && evaluate(specialized_target,satisfying)==0,"model target");
    point_write(out,"both_systems_with_goals",satisfying,next,-1,-1,0);

    // The retained ancestor's image need not follow from original axioms when
    // the covered goal input is absent. The original complete ENS system is satisfied.
    std::array<int,NV> changed{};changed[0]=1;changed[inner.first]=1;
    int changed_axiom=parent_comp[0];
    if(complement) {changed[2]=1;changed[parent.first]=1;changed_axiom=parent_comp[1];}
    point_check(original,changed,goals[0]);
    need(evaluate(zero_inner(original[changed_axiom],inner),changed)==1,"ancestor image control");
    point_write(out,"original_model_violates_retained_image",changed,next,goals[0],changed_axiom,1);

    // The selected xP image is x, and is not implied by the specialized retained
    // system plus the other goal input. Its proof really requires the x assumption.
    std::array<int,NV> missing{};missing[0]=1;
    if(!complement)missing[parent.first]=1;
    point_check(retained,missing,mapping[goals[0]]);
    need(evaluate(zero_inner(original[inner_comp[0]],inner),missing)==1,"goal witness control");
    point_write(out,"missing_x_goal_in_specialized_system",missing,next,mapping[goals[0]],inner_comp[0],1);
    out<<"{\"record\":\"case_verified\",\"source_degree\":"<<source.degree
       <<",\"replayed_degree\":"<<replayed.degree<<",\"source_lines\":"<<source.lines.size()
       <<",\"replayed_lines\":"<<replayed.lines.size()<<",\"parent_retained\":true,\"all_passed\":true}\n";
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists");
        auto directory=std::filesystem::path(argv[2]).parent_path();
        if(!directory.empty())std::filesystem::create_directories(directory);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"modified_ancestor_cleanup\",\"seed\":null,"
              "\"scope\":\"satisfiable local target-derivation fixtures, not PHP refutations or a global source schedule\"}\n";
        for(int p:{2,3,5})for(int h:{1,2})for(bool complement:{false,true})run_case(out,p,h,complement);
        out<<"{\"record\":\"summary\",\"cases\":12,\"complete_PC_traces\":24,\"common_models\":12,\"countercontrols\":24,\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failed");
        std::cout<<"Twelve nested cleanup cases, 24 full PC traces, and 36 model/control checks passed.\n";
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
