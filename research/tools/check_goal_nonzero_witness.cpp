// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// One proved nonzero input removes coefficients, retaining the actual image.
#include "pc_boundary.hpp"
#include <set>
using namespace boundary_pc;
Poly assign_first_one(const Poly& f,const Block& selected) {
    Poly result(f.p);
    for(const auto& [mon,coefficient]:f.terms) {
        Mon image=mon;bool zero=false;
        for(int v=selected.first;v<selected.end;v++) {
            if(v!=selected.first && image[v])zero=true;
            image[v]=0;
        }
        if(!zero)result.add(image,coefficient);
    }
    return result;
}
int evaluate_at(const Poly& f,const std::array<int,NV>& point) {
    int result=0;
    for(const auto& [mon,coefficient]:f.terms) {
        int value=coefficient;
        for(int v=0;v<NV;v++)value=value*modpow(point[v],mon[v],f.p)%f.p;
        result=(result+value)%f.p;
    }
    return result;
}
void model_check(const std::vector<Poly>& axioms,const std::array<int,NV>& point,int omit=-1) {
    for(size_t i=0;i<axioms.size();i++)if(int(i)!=omit)need(evaluate_at(axioms[i],point)==0,"model axiom");
}
void model_write(std::ostream& out,const std::string& name,const std::array<int,NV>& point,int next,int omit) {
    out<<"{\"record\":\"model\",\"name\":\""<<name<<"\",\"omitted_axiom\":"<<omit<<",\"assignment\":[";
    for(int i=0;i<next;i++) {if(i)out<<',';out<<'['<<i<<','<<point[i]<<']';}
    out<<"]}\n";
}
void trace_check(const Proof& proof,int final,const Poly& target,int bound) {
    need(final>=0 && proof.val(final)==target && proof.degree<=bound,"trace target or degree");
    need(proof.verify() && !proof.verify(final),"trace or corruption check");
}
void test_case(std::ostream& out,int p,int width,int h,bool copied) {
    Poly one(p,1),x=variable(p,0),z=variable(p,width);
    int next=width+1;
    std::vector<Block> earlier;
    if(copied) {earlier.push_back(block({x},1,next));earlier.push_back(block({x},1,next));}
    Poly first=copied?one-earlier[0].product:x;
    Poly H=one-first,goal=copied?earlier[1].product:H;
    std::vector<Poly> inputs{first};for(int i=1;i<width;i++)inputs.push_back(variable(p,i));
    Block selected=block(inputs,h,next),parent=block({selected.product,z},h,next);
    std::vector<Poly> axioms;std::vector<std::string> kinds;
    auto add=[&](const Poly& f,const std::string& kind) {
        int id=int(axioms.size());axioms.push_back(f);kinds.push_back(kind);return id;
    };
    for(int i=0;i<=width;i++) {auto a=variable(p,i);add(a*a-a,"old_boolean");}
    std::vector<int> earlier_comp,selected_comp,parent_comp;
    for(const auto& b:earlier)for(const auto& e:b.axioms)earlier_comp.push_back(add(e,"earlier_companion"));
    for(const auto& b:earlier)for(int i=b.first;i<b.end;i++) {auto r=variable(p,i);add(powp(r,p)-r,"earlier_field");}
    for(const auto& e:selected.axioms)selected_comp.push_back(add(e,"selected_companion"));
    std::set<int> selected_fields;
    for(int i=selected.first;i<selected.end;i++) {auto r=variable(p,i);selected_fields.insert(add(powp(r,p)-r,"selected_field"));}
    for(const auto& e:parent.axioms)parent_comp.push_back(add(e,"retained_parent_companion"));
    for(int i=parent.first;i<parent.end;i++) {auto r=variable(p,i);add(powp(r,p)-r,"retained_parent_field");}
    int goal_index=add(goal,"goal");
    std::vector<int> identity(axioms.size());for(size_t i=0;i<identity.size();i++)identity[i]=int(i);
    auto witness=[&](Proof& proof,const std::vector<int>& mapping) {
        if(!copied)return proof.ax(mapping[goal_index]);
        int left=proof.mul(proof.ax(mapping[earlier_comp[0]]),variable(p,earlier[1].first));
        int right=proof.mul(proof.ax(mapping[earlier_comp[1]]),variable(p,earlier[0].first));
        int delta=proof.lc(left,right,1,-1);
        need(proof.val(delta)==earlier[0].product-earlier[1].product,"copy identity");
        return proof.lc(delta,proof.ax(mapping[goal_index]));
    };
    Proof source(p,axioms);int source_H=witness(source,identity),witness_degree=source.degree;
    need(source.val(source_H)==H,"source nonzero witness");
    for(const auto& line:source.lines)need(assign_first_one(line.value,selected)==line.value,"witness used selected variables");
    int P_line=source.lc(source.ax(selected_comp[0]),source.mul(source_H,selected.product));
    need(source.val(P_line)==selected.product,"derived selected product");
    int final=source.lc(P_line,source.ax(parent_comp[1]));
    Poly target=selected.product+z*parent.product;
    int source_bound=std::max({witness_degree,selected.axioms[0].deg(),parent.axioms[1].deg()});
    trace_check(source,final,target,source_bound);

    std::vector<Poly> retained;std::vector<int> mapping(axioms.size(),-1);
    for(size_t i=0;i<axioms.size();i++) {
        if(kinds[i]=="selected_companion" || kinds[i]=="selected_field")continue;
        mapping[i]=int(retained.size());retained.push_back(assign_first_one(axioms[i],selected));
    }
    Proof replayed(p,retained);int replay_H=witness(replayed,mapping);
    need(replayed.val(replay_H)==H && replayed.degree<=witness_degree,"replayed nonzero witness");
    std::vector<int> image_proofs;
    for(size_t i=0;i<inputs.size();i++) {
        int id=replayed.mul(replay_H,inputs[i]);
        need(replayed.val(id)==assign_first_one(selected.axioms[i],selected),"selected companion image proof");
        image_proofs.push_back(id);
    }
    std::vector<int> lines;
    for(const auto& line:source.lines) {
        int id=-1;
        if(line.rule=='a') {
            auto found=std::find(selected_comp.begin(),selected_comp.end(),line.a);
            if(found!=selected_comp.end())id=image_proofs.at(size_t(found-selected_comp.begin()));
            else if(selected_fields.count(line.a))need(assign_first_one(line.value,selected).terms.empty(),"selected field image");
            else id=replayed.ax(mapping.at(line.a));
        } else if(line.rule=='l') {
            int a=line.a<0?-1:lines.at(line.a),b=line.b<0?-1:lines.at(line.b);
            id=replayed.lc(a,b,line.ca,line.cb);
        } else {
            int a=line.a<0?-1:lines.at(line.a);
            if(line.v<selected.first || line.v>=selected.end)id=replayed.mv(a,line.v);
            else if(line.v==selected.first)id=replayed.lc(a,-1);
        }
        need(replayed.val(id)==assign_first_one(line.value,selected),"PC replayed line image");lines.push_back(id);
    }
    auto image_P=assign_first_one(selected.product,selected),image_Q=assign_first_one(parent.product,selected);
    need(image_P==H && image_P.deg()>0,"product image was incorrectly made constant");
    Poly rebuilt(p,1),fake_zero_parent(p,1);
    for(int u=0;u<h;u++) {
        auto s=variable(p,parent.first+2*u),t=variable(p,parent.first+2*u+1);
        rebuilt=rebuilt*(one-s*H-t*z);fake_zero_parent=fake_zero_parent*(one-t*z);
    }
    need(rebuilt==image_Q && !(fake_zero_parent==image_Q),"retained parent's exact input image");
    int replay_final=lines.at(final);auto image_target=assign_first_one(target,selected);
    trace_check(replayed,replay_final,image_target,std::max(source.degree,witness_degree));
    for(const auto& line:replayed.lines)need(assign_first_one(line.value,selected)==line.value,"selected coefficient survived");
    need(assign_first_one(goal,selected)==goal,"named goal changed");

    out<<"{\"record\":\"case\",\"p\":"<<p<<",\"width\":"<<width<<",\"accuracy\":"<<h
       <<",\"copied_witness\":"<<(copied?"true":"false")<<",\"selected_variables\":["<<selected.first<<','<<selected.end
       <<"],\"parent_variables\":["<<parent.first<<','<<parent.end<<"],\"P\":";jsonpoly(out,selected.product);
    out<<",\"H_product_image\":";jsonpoly(out,H);out<<",\"Q\":";jsonpoly(out,parent.product);
    out<<",\"Q_image\":";jsonpoly(out,image_Q);out<<",\"incorrect_zero_product_parent\":";jsonpoly(out,fake_zero_parent);
    out<<",\"goal\":";jsonpoly(out,goal);out<<",\"source_H_line\":"<<source_H<<",\"replayed_H_line\":"<<replay_H
       <<",\"witness_degree\":"<<witness_degree<<",\"image_proof_lines\":[";
    for(size_t i=0;i<image_proofs.size();i++) {if(i)out<<',';out<<image_proofs[i];}out<<"]}\n";
    source.write(out,"source_target_P_plus_zQ",final);replayed.write(out,"replayed_target_H_plus_zQimage",replay_final);
    out<<"{\"record\":\"axiom_images\",\"items\":[";
    for(size_t i=0;i<axioms.size();i++) {
        if(i)out<<',';
        auto image=assign_first_one(axioms[i],selected);need(image.deg()<=axioms[i].deg(),"image degree increased");
        out<<"{\"original_index\":"<<i<<",\"kind\":\""<<kinds[i]<<"\",\"retained_index\":"<<mapping[i]
           <<",\"original_degree\":"<<axioms[i].deg()<<",\"image_degree\":"<<image.deg()<<",\"image\":";jsonpoly(out,image);out<<'}';
    }
    out<<"]}\n";

    std::array<int,NV> model{};model[0]=model[1]=model[width]=1;
    if(copied)model[earlier[0].first]=model[earlier[1].first]=1;
    model[selected.first]=1;model[parent.first+1]=1;
    model_check(axioms,model);model_check(retained,model);
    need(evaluate_at(inputs[0],model)==1 && evaluate_at(inputs[1],model)==1,"not a nonzero-input fixture");
    need(evaluate_at(target,model)==0 && evaluate_at(image_target,model)==0,"common target model");
    model_write(out,"both_systems_with_goal_and_nonzero_other_input",model,next,-1);

    std::array<int,NV> missing{};missing[1]=1;missing[parent.first]=1;
    model_check(retained,missing,mapping[goal_index]);
    need(evaluate_at(goal,missing)==1 && evaluate_at(H,missing)==1,"missing goal or nonconstant product control");
    need(evaluate_at(assign_first_one(selected.axioms[1],selected),missing)==1,"companion image needs goal");
    need(evaluate_at(image_Q,missing)==0 && evaluate_at(fake_zero_parent,missing)==1,"incorrect zero collapse control");
    model_write(out,"missing_goal_and_false_zero_collapse",missing,next,mapping[goal_index]);
    out<<"{\"record\":\"case_verified\",\"source_degree\":"<<source.degree<<",\"replayed_degree\":"<<replayed.degree
       <<",\"witness_degree\":"<<witness_degree<<",\"product_image_degree\":"<<H.deg()<<",\"all_passed\":true}\n";
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");need(!std::filesystem::exists(argv[2]),"output exists");
        auto dir=std::filesystem::path(argv[2]).parent_path();if(!dir.empty())std::filesystem::create_directories(dir);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"goal_nonzero_witness\",\"seed\":null,\"scope\":\"local satisfiable PC target fixtures with exact nonconstant images, not PHP refutations\"}\n";
        for(int p:{2,3,5}) {test_case(out,p,2,1,false);test_case(out,p,4,1,false);test_case(out,p,2,2,false);test_case(out,p,2,1,true);}
        out<<"{\"record\":\"summary\",\"cases\":12,\"complete_PC_traces\":24,\"nonliteral_copy_cases\":3,\"common_models\":12,\"missing_goal_and_zero_collapse_controls\":12,\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failed");
        std::cout<<"Twelve proved-nonzero-input cases, 24 PC traces, and exact-image controls passed.\n";
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
