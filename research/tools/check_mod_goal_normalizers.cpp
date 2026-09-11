// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// MOD goal inputs, aggregate normalizers, and exact retained polynomial images.
#include "pc_boundary.hpp"
#include <set>
using namespace boundary_pc;
Poly constants_on(const Poly& f,const Block& block,const std::array<int,NV>& beta) {
    Poly image(f.p);
    for(const auto& [mon,coefficient]:f.terms) {
        Mon next=mon;int value=coefficient;
        for(int v=block.first;v<block.end;v++) {value=value*modpow(beta[v],next[v],f.p)%f.p;next[v]=0;}
        image.add(next,value);
    }
    return image;
}
int eval(const Poly& f,const std::array<int,NV>& point) {
    int result=0;
    for(const auto& [mon,coefficient]:f.terms) {
        int value=coefficient;
        for(int v=0;v<NV;v++)value=value*modpow(point[v],mon[v],f.p)%f.p;
        result=(result+value)%f.p;
    }
    return result;
}
int inverse(int value,int p) {need(value%p!=0,"zero inverse");return modpow(value,p-2,p);}
void check_model(const std::vector<Poly>& axioms,const std::array<int,NV>& point,int omitted=-1) {
    for(size_t i=0;i<axioms.size();i++)if(int(i)!=omitted)need(eval(axioms[i],point)==0,"model violates retained axiom");
}
void write_point(std::ostream& out,const std::array<int,NV>& point,int next) {
    out<<'[';for(int v=0;v<next;v++) {if(v)out<<',';out<<'['<<v<<','<<point[v]<<']';}out<<']';
}
void verify_trace(const Proof& proof,int final,const Poly& target,int bound) {
    need(final>=0 && proof.val(final)==target && proof.degree<=bound,"trace target or ceiling");
    need(proof.verify() && !proof.verify(final),"trace/corruption verification");
}
struct ModelCounts {int common=0,counter=0,nonboolean=0;};
ModelCounts run_case(std::ostream& out,int p,int k,bool positive,int residue,bool selector,bool copied,bool field_inputs) {
    need((positive && residue==0 && selector) || (!positive && residue!=0),"invalid positive/negative criterion");
    need(!copied || !field_inputs,"copied fixture has Boolean original inputs");
    int h=selector?p-1:1,next=k+1;Poly one(p,1),z=variable(p,k);
    std::vector<Block> earlier;
    if(copied) {earlier.push_back(block({variable(p,0)},1,next));earlier.push_back(block({variable(p,0)},1,next));}
    std::vector<Poly> g,goal_g;
    for(int j=0;j<k;j++) {
        g.push_back(copied && j==0?earlier[0].product:variable(p,j));
        goal_g.push_back(copied && j==0?earlier[1].product:variable(p,j));
    }
    Poly s(p),sb(p);for(int j=0;j<k;j++) {s=s+g[j];sb=sb+goal_g[j];}
    Poly u=Poly(p,residue)-sb,goal=positive?one-powp(u,p-1):powp(u,p-1);
    Poly H=selector?one-powp(s,p-1):one-Poly(p,inverse(residue,p))*s;
    Block selected=block(g,h,next),parent=block({selected.product,z},1,next);
    need(next<=NV,"fixture exceeds PC variable capacity");
    std::vector<int> sizes(next,p);
    for(int v=0;v<=k;v++)sizes[v]=field_inputs && v<k?p:2;
    std::vector<Poly> axioms=domains(p,sizes);std::vector<std::string> kinds(axioms.size(),"domain");
    auto add=[&](const Poly& f,const std::string& kind) {int i=int(axioms.size());axioms.push_back(f);kinds.push_back(kind);return i;};
    std::vector<int> earlier_comp,selected_comp,parent_comp;
    for(const auto& b:earlier)for(const auto& e:b.axioms)earlier_comp.push_back(add(e,"earlier_companion"));
    for(const auto& e:selected.axioms)selected_comp.push_back(add(e,"selected_companion"));
    for(const auto& e:parent.axioms)parent_comp.push_back(add(e,"retained_parent_companion"));
    int goal_index=add(goal,"goal");
    std::vector<int> identity(axioms.size());for(size_t i=0;i<identity.size();i++)identity[i]=int(i);
    auto derive_H=[&](Proof& proof,const std::vector<int>& mapping) {
        int delta=-1;
        if(copied) {
            int a=proof.mul(proof.ax(mapping[earlier_comp[0]]),variable(p,earlier[1].first));
            int b=proof.mul(proof.ax(mapping[earlier_comp[1]]),variable(p,earlier[0].first));
            delta=proof.lc(a,b,1,-1);need(proof.val(delta)==s-sb,"aggregate copy identity");
        }
        if(positive) {
            Poly multiplier(p);for(int a=0;a<p-1;a++)multiplier=multiplier+powp(s,p-2-a)*powp(sb,a);
            int difference=proof.mul(delta,multiplier);
            int result=proof.lc(proof.ax(mapping[goal_index]),difference,1,-1);
            need(proof.val(result)==H,"positive MOD goal normalizer");return result;
        }
        int scalar=proof.ax(mapping[goal_index]);
        if(p>2) {
            int relation=field_proof(proof,powp(u,p)-u,sizes);
            scalar=proof.lc(proof.mul(scalar,u),relation,1,-1);
        }
        need(proof.val(scalar)==u,"scalar extraction");
        int difference=proof.lc(delta,scalar,1,-1); // s-residue
        need(proof.val(difference)==s-Poly(p,residue),"nonzero aggregate witness");
        int result=-1;
        if(selector) {
            Poly multiplier(p);for(int a=0;a<p-1;a++)multiplier=multiplier+Poly(p,modpow(residue,a,p))*powp(s,p-2-a);
            result=proof.lc(proof.mul(difference,multiplier),-1,-1,0);
        } else result=proof.lc(difference,-1,-inverse(residue,p),0);
        need(proof.val(result)==H,"negative MOD goal normalizer");return result;
    };
    std::array<int,NV> beta{};
    for(int row=0;row<h;row++)for(int j=0;j<k;j++)
        beta[selected.first+row*k+j]=selector?inverse(row+1,p):inverse(residue,p);
    auto phi=[&](const Poly& f){return constants_on(f,selected,beta);};
    need(phi(selected.product)==H,"normalizer factor identity");

    Proof source(p,axioms);int source_H=derive_H(source,identity),witness_degree=source.degree;
    for(const auto& line:source.lines)need(phi(line.value)==line.value,"witness uses selected coefficients");
    int sp=-1;for(int index:selected_comp)sp=source.lc(sp,source.ax(index));
    need(source.val(sp)==s*selected.product,"aggregate companion sum");
    Poly weight=selector?powp(s,p-2):Poly(p,inverse(residue,p));
    int selected_proof=source.lc(source.mul(source_H,selected.product),source.mul(sp,weight));
    need(source.val(selected_proof)==selected.product,"source selected-product proof");
    int final=source.lc(selected_proof,source.ax(parent_comp[1]));
    Poly target=selected.product+z*parent.product;
    int source_bound=std::max({witness_degree,H.deg()+selected.product.deg(),parent.axioms[1].deg()});
    verify_trace(source,final,target,source_bound);

    // Keep zero domain-image placeholders so field_proof's variable-indexed
    // domain layout remains aligned; no removed-variable axiom is retained.
    std::vector<Poly> retained;std::vector<int> mapping(axioms.size(),-1);
    for(int i=0;i<next;i++) {mapping[i]=int(retained.size());retained.push_back(phi(axioms[i]));}
    for(size_t i=size_t(next);i<axioms.size();i++)if(kinds[i]!="selected_companion") {
        mapping[i]=int(retained.size());retained.push_back(phi(axioms[i]));
    }
    Proof replayed(p,retained);int replay_H=derive_H(replayed,mapping);
    need(replayed.degree<=witness_degree,"witness replay increased degree");
    std::vector<int> image_proofs;
    for(int j=0;j<k;j++) {int id=replayed.mul(replay_H,g[j]);need(replayed.val(id)==phi(selected.axioms[j]),"companion image proof");image_proofs.push_back(id);}
    std::vector<int> lines;
    for(const auto& line:source.lines) {
        int id=-1;
        if(line.rule=='a') {
            auto found=std::find(selected_comp.begin(),selected_comp.end(),line.a);
            if(found!=selected_comp.end())id=image_proofs.at(size_t(found-selected_comp.begin()));
            else if(line.a>=selected.first && line.a<selected.end)need(phi(line.value).terms.empty(),"selected field image");
            else id=replayed.ax(mapping.at(line.a));
        } else if(line.rule=='l') {
            int a=line.a<0?-1:lines.at(line.a),b=line.b<0?-1:lines.at(line.b);
            id=replayed.lc(a,b,line.ca,line.cb);
        } else {
            int a=line.a<0?-1:lines.at(line.a);
            id=line.v>=selected.first && line.v<selected.end?replayed.lc(a,-1,beta[line.v],0):replayed.mv(a,line.v);
        }
        need(replayed.val(id)==phi(line.value),"replayed line polynomial");lines.push_back(id);
    }
    int replay_final=lines.at(final);auto image_target=phi(target),image_parent=phi(parent.product);
    verify_trace(replayed,replay_final,image_target,std::max(source.degree,witness_degree));
    for(const auto& line:replayed.lines)need(phi(line.value)==line.value,"removed coefficient remains");
    need(phi(goal)==goal && image_parent==one-variable(p,parent.first)*H-variable(p,parent.first+1)*z,"parent/goal image");

    out<<"{\"record\":\"case\",\"p\":"<<p<<",\"matched_inputs\":"<<k<<",\"accuracy\":"<<h
       <<",\"positive_goal_child\":"<<(positive?"true":"false")<<",\"residue\":"<<residue
       <<",\"selector\":"<<(selector?"true":"false")<<",\"copied_inputs\":"<<(copied?"true":"false")
       <<",\"field_input_fixture\":"<<(field_inputs?"true":"false")<<",\"domain_sizes\":[";
    for(size_t i=0;i<sizes.size();i++) {if(i)out<<',';out<<sizes[i];}
    out<<"],\"S_A\":";jsonpoly(out,s);out<<",\"S_B\":";jsonpoly(out,sb);out<<",\"u_B\":";jsonpoly(out,u);
    out<<",\"goal\":";jsonpoly(out,goal);out<<",\"H\":";jsonpoly(out,H);
    out<<",\"H_booleanity\":";jsonpoly(out,H*H-H);out<<",\"selected_product\":";jsonpoly(out,selected.product);
    out<<",\"selected_variables\":["<<selected.first<<','<<selected.end<<"],\"parent_image\":";jsonpoly(out,image_parent);
    out<<",\"coefficient_assignment\":[";
    for(int v=selected.first;v<selected.end;v++) {if(v!=selected.first)out<<',';out<<'['<<v<<','<<beta[v]<<']';}
    out<<"],\"source_H_line\":"<<source_H<<",\"replayed_H_line\":"<<replay_H<<",\"witness_degree\":"<<witness_degree
       <<",\"image_proof_lines\":[";
    for(size_t i=0;i<image_proofs.size();i++) {if(i)out<<',';out<<image_proofs[i];}out<<"]}\n";
    source.write(out,"source_P_plus_zQ",final);replayed.write(out,"replayed_H_plus_zQimage",replay_final);
    out<<"{\"record\":\"axiom_images\",\"items\":[";
    for(size_t i=0;i<axioms.size();i++) {
        if(i)out<<',';
        auto image=phi(axioms[i]);need(image.deg()<=axioms[i].deg(),"axiom image degree");
        out<<"{\"original_index\":"<<i<<",\"retained_index\":"<<mapping[i]<<",\"kind\":\""<<kinds[i]
           <<"\",\"original_degree\":"<<axioms[i].deg()<<",\"image_degree\":"<<image.deg()<<",\"image\":";jsonpoly(out,image);out<<'}';
    }
    out<<"]}\n";

    int radix=field_inputs?p:2,patterns=1;for(int j=0;j<k;j++)patterns*=radix;
    ModelCounts counts;std::set<int> possible_sums;
    for(int code=0;code<patterns;code++) {
        int rest=code;std::array<int,NV> point=beta;std::vector<int> values(k);int nonzero=-1;
        for(int j=0;j<k;j++) {values[j]=rest%radix;rest/=radix;if(values[j])nonzero=j;}
        if(copied) {point[0]=1-values[0];point[earlier[0].first]=point[earlier[1].first]=1;}
        else point[0]=values[0];
        for(int j=1;j<k;j++)point[j]=values[j];
        int f=eval(goal,point),hv=eval(H,point);
        if(selector)need(hv==0 || hv==1,"selector lost field Booleanity");
        std::string status="no_nonzero_companion_image";
        if(f==0) {
            need(hv==0,"normalizer is not implied by goal");point[k]=1;point[parent.first+1]=1;
            check_model(axioms,point);check_model(retained,point);
            need(eval(target,point)==0 && eval(image_target,point)==0,"common model target");
            status="common_model";counts.common++;possible_sums.insert(eval(s,point));
        } else if(hv && nonzero>=0) {
            point[parent.first]=inverse(hv,p);point[k]=0;
            check_model(retained,point,mapping[goal_index]);
            need(eval(phi(selected.axioms[nonzero]),point)!=0,"missing goal did not break companion image");
            if(hv!=1)counts.nonboolean++;
            status="missing_goal_countermodel";counts.counter++;
        }
        out<<"{\"record\":\"input_pattern\",\"status\":\""<<status<<"\",\"values\":[";
        for(int j=0;j<k;j++) {if(j)out<<',';out<<values[j];}
        out<<"],\"goal_value\":"<<f<<",\"H_value\":"<<hv<<",\"H_booleanity_value\":"<<(hv*hv-hv+p)%p
           <<",\"tested_companion\":"<<nonzero<<",\"assignment\":";write_point(out,point,next);out<<"}\n";
    }
    need(counts.common>0 && counts.counter>0,"vacuous goal fixture");
    out<<"{\"record\":\"case_verified\",\"source_degree\":"<<source.degree<<",\"replayed_degree\":"<<replayed.degree
       <<",\"witness_degree\":"<<witness_degree<<",\"common_models\":"<<counts.common<<",\"missing_goal_models\":"<<counts.counter
       <<",\"nonboolean_linear_image_models\":"<<counts.nonboolean<<",\"goal_sums\":[";
    bool comma=false;for(int value:possible_sums) {if(comma)out<<',';comma=true;out<<value;}out<<"],\"all_passed\":true}\n";
    return counts;
}
void invalid_residue(std::ostream& out,int p,bool positive,int residue) {
    int s=0,u=(residue-s+p)%p,goal=positive?(1-modpow(u,p-1,p)+p)%p:modpow(u,p-1,p);
    need(goal==0,"invalid-residue control does not satisfy its goal");
    // p Boolean ones have sum zero. A first original coefficient one makes
    // the original product zero; every factor depending only on s stays one.
    int original_product=1-1,aggregate_product=1;
    for(int a=1;a<p;a++)aggregate_product=aggregate_product*(1-inverse(a,p)*s)%p;
    need(original_product==0 && aggregate_product==1,"aggregate-only residue control");
    out<<"{\"record\":\"invalid_residue_control\",\"p\":"<<p<<",\"positive_goal_child\":"<<(positive?"true":"false")
       <<",\"residue\":"<<residue<<",\"accuracy\":"<<p-1<<",\"boolean_inputs\":[";
    for(int j=0;j<p;j++) {if(j)out<<',';out<<1;}
    out<<"],\"sum\":0,\"goal_value\":0,\"original_first_vector\":[";
    for(int j=0;j<p;j++) {if(j)out<<',';out<<(j==0?1:0);}
    out<<"],\"remaining_original_vectors_zero\":true,\"original_product\":0,\"aggregate_only_product\":1,\"first_companion_image\":1}\n";
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");need(!std::filesystem::exists(argv[2]),"output exists");
        auto dir=std::filesystem::path(argv[2]).parent_path();if(!dir.empty())std::filesystem::create_directories(dir);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");ModelCounts total;int cases=0;
        out<<"{\"schema\":1,\"suite\":\"mod_goal_normalizers\",\"seed\":null,\"scope\":\"local Boolean and explicitly marked field-domain fixtures, not PHP refutations\"}\n";
        auto run=[&](int p,int k,bool pos,int i,bool sel,bool copied,bool field) {
            auto count=run_case(out,p,k,pos,i,sel,copied,field);total.common+=count.common;total.counter+=count.counter;total.nonboolean+=count.nonboolean;cases++;
        };
        for(int p:{2,3,5}) {run(p,p==3?3:2,true,0,true,false,p==5);run(p,2,false,1,false,false,false);}
        for(int p:{3,5})run(p,2,false,2,false,false,false);
        for(int p:{2,3}) {run(p,p==3?3:2,true,0,true,true,false);run(p,2,false,1,false,true,false);}
        run(3,3,false,1,true,false,false);run(5,2,false,1,true,false,true);
        int bad=0;for(int p:{2,3,5}) {invalid_residue(out,p,false,0);bad++;for(int i=1;i<p;i++) {invalid_residue(out,p,true,i);bad++;}}
        out<<"{\"record\":\"summary\",\"cases\":"<<cases<<",\"complete_PC_traces\":"<<2*cases<<",\"common_models\":"<<total.common
           <<",\"missing_goal_models\":"<<total.counter<<",\"nonboolean_linear_image_models\":"<<total.nonboolean
           <<",\"invalid_residue_controls\":"<<bad<<",\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failed");std::cout<<cases<<" MOD-goal cases, "<<2*cases<<" PC traces, and "<<bad<<" residue controls passed.\n";
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
