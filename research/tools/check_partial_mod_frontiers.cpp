// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Complete MP replay with two selected argument copies and one residual argument.
#include "pc_boundary.hpp"
using namespace boundary_pc;

template<class AxiomImage>
int mapped(const Proof& src,int final,Proof& dst,const Poly& weight,int first,AxiomImage image) {
    std::vector<int> ids;std::array<int,NV> zero{};
    for(const auto& line:src.lines) {
        int id=-1;
        if(line.rule=='a')id=image(line.a);
        else if(line.rule=='l')id=dst.lc(line.a<0?-1:ids.at(line.a),line.b<0?-1:ids.at(line.b),line.ca,line.cb);
        else if(line.v<first)id=dst.mv(line.a<0?-1:ids.at(line.a),line.v);
        need(dst.val(id)==weight*specialize(line.value,first,zero),"mapped line mismatch");ids.push_back(id);
    }
    return final<0?-1:ids.at(final);
}
bool uses(const Poly& f,int first,int end) {
    for(const auto& [m,c]:f.terms) { (void)c;for(int i=first;i<end;i++)if(m[i])return true; }
    return false;
}
void trace(std::ostream& out,const std::string& name,const Proof& proof,int final,
           const Poly& target,int bound,int old=-1) {
    need(proof.val(final)==target && proof.verify() && proof.degree<=bound,"trace "+name);
    need(final>=0 && !proof.verify(final),"corrupt final line accepted");
    if(old>=0)for(const auto& line:proof.lines)need(line.value.old(old),"selected variable survives");
    proof.write(out,name,final);
    std::vector<bool> used(proof.lines.size(),false),axiom(proof.axioms.size(),false);used[final]=true;
    int cone_degree=0;
    for(int j=int(proof.lines.size())-1;j>=0;j--)if(used[j]) {
        const auto& line=proof.lines[j];cone_degree=std::max(cone_degree,line.value.deg());
        if(line.rule=='a')axiom[line.a]=true;
        else {if(line.a>=0)used[line.a]=true;if(line.rule=='l' && line.b>=0)used[line.b]=true;}
    }
    out<<"{\"record\":\"verified\",\"name\":\""<<name<<"\",\"degree\":"<<proof.degree
       <<",\"bound\":"<<bound<<",\"final_cone_degree\":"<<cone_degree<<",\"used_axioms\":[";
    bool comma=false;for(size_t i=0;i<axiom.size();i++)if(axiom[i]) {if(comma)out<<',';comma=true;out<<i;}
    out<<"],\"corruption_rejected\":true}\n";
}
void fixture(std::ostream& out,int id,int p,int width,int h,bool derived_inputs,bool true_arguments=false) {
    need(!true_arguments || !derived_inputs,"true-argument fixture uses direct inputs");
    Poly one(p,1);int propositions=width+1,next=propositions;
    std::vector<Poly> primitive;std::vector<Block> lower;
    if(derived_inputs) {
        for(int j=0;j<propositions;j++) {
            auto x=variable(p,j);lower.push_back(block({x,one-x},1,next));primitive.push_back(lower.back().product);
        }
    } else for(int j=0;j<propositions;j++)primitive.push_back(variable(p,j));
    std::vector<Poly> inputs(primitive.begin(),primitive.end()-1);
    Block Q=block({primitive.back()},h,next);int first=next;
    Block P=block(inputs,h,next),bar=block(inputs,h,next);int s=P.product.deg();
    need(Q.product.deg()==s,"fixture degree mismatch");
    std::vector<int> sizes(next,p);for(int j=0;j<propositions;j++)sizes[j]=2;
    auto axioms=domains(p,sizes);std::vector<int> primitive_indices(propositions,-1);
    for(int j=0;j<propositions;j++) {
        if(true_arguments && j!=0 && j!=propositions-1)continue;
        primitive_indices[j]=int(axioms.size());
        if(true_arguments)axioms.push_back(primitive[j]-one);
        else if(derived_inputs)axioms.insert(axioms.end(),lower[j].axioms.begin(),lower[j].axioms.end());
        else axioms.push_back(primitive[j]);
    }
    int q_start=int(axioms.size());axioms.insert(axioms.end(),Q.axioms.begin(),Q.axioms.end());
    int p_start=int(axioms.size());axioms.insert(axioms.end(),P.axioms.begin(),P.axioms.end());
    int bar_start=int(axioms.size());axioms.insert(axioms.end(),bar.axioms.begin(),bar.axioms.end());
    auto old=domains(p,std::vector<int>(sizes.begin(),sizes.begin()+first));
    old.insert(old.end(),axioms.begin()+next,axioms.begin()+p_start);
    for(const auto& ax:old)need(ax.old(first),"old axiom is not fresh");
    auto goal=inputs;goal.push_back(Q.product);
    for(const auto& f:goal)need(f.old(first),"goal input is not fresh");
    auto clean_axioms=old;clean_axioms.insert(clean_axioms.end(),goal.begin(),goal.end());
    out<<"{\"record\":\"case\",\"id\":"<<id<<",\"p\":"<<p<<",\"width\":"<<width
       <<",\"accuracy\":"<<h<<",\"derived_inputs\":"<<(derived_inputs?"true":"false")
       <<",\"true_arguments\":"<<(true_arguments?"true":"false")
       <<",\"selected_first_variable\":"<<first<<",\"argument_product_degree\":"<<s
       <<",\"retained_Q\":";jsonpoly(out,Q.product);
    out<<",\"selected_P\":";jsonpoly(out,P.product);out<<",\"selected_left_copy\":";jsonpoly(out,bar.product);
    out<<",\"goal_inputs\":[";for(size_t j=0;j<goal.size();j++) {if(j)out<<',';jsonpoly(out,goal[j]);}
    out<<"],\"axiom_groups\":{\"domains\":"<<next<<",\"primitive_starts\":[";
    for(size_t j=0;j<primitive_indices.size();j++) {if(j)out<<',';out<<primitive_indices[j];}
    out<<"],\"Q\":"<<q_start<<",\"P\":"<<p_start<<",\"left_P\":"<<bar_start
       <<"},\"selected_field_ranges\":[["<<P.first<<','<<P.end<<"],["<<bar.first<<','<<bar.end
       <<"]],\"retained_Q_range\":["<<Q.first<<','<<Q.end<<"]}\n";
    if(true_arguments) {
        std::array<int,NV> point{},zero{};point[0]=point[propositions-1]=1;
        point[Q.first]=point[P.first]=point[bar.first]=1;
        for(const auto& ax:axioms)need(specialize(ax,0,point).terms.empty(),"true-argument system is not satisfied");
        for(size_t j=1;j<goal.size();j++)need(specialize(goal[j],0,point).terms.empty(),"other goal input not zero in control");
        auto image=specialize(P.axioms[0],first,zero);
        need(specialize(image,0,point)==one,"selected image must not be an old consequence");
        out<<"{\"record\":\"conditional_image_model\",\"case\":"<<id<<",\"assignment\":[";
        for(int j=0;j<next;j++) {if(j)out<<',';out<<point[j];}
        out<<"],\"all_original_axioms_zero\":true,\"all_other_goal_inputs_zero\":true,\"missing_goal_coordinate\":0,"
             "\"selected_companion_image\":";jsonpoly(out,image);
        out<<",\"image_value\":1,\"axiom_array_source\":\"the following selected_pair_copy proof\"}\n";
    }
    Proof copy(p,axioms);int difference=-1;
    for(int j=0;j<width;j++) {
        difference=copy.lc(difference,copy.mul(copy.ax(p_start+j),bar.coef[j]));
        difference=copy.lc(difference,copy.mul(copy.ax(bar_start+j),P.coef[j]),1,-1);
    }
    Poly delta=P.product-bar.product;
    trace(out,"selected_pair_copy",copy,difference,delta,2*s);
    std::array<int,NV> zero{};need(specialize(delta,first,zero).terms.empty(),"copy difference survives pair removal");
    for(bool negative:{false,true}) {
        int residue=negative?1:true_arguments?2%p:0;
        std::string sign=negative?"negative_residue_one":residue==0?"positive_residue_zero":"positive_residue_two";
        Poly u=P.product+Q.product-Poly(p,2-residue),v=bar.product+Q.product-Poly(p,2-residue);
        auto source_axioms=axioms;if(negative)source_axioms.push_back(u);
        Proof source(p,source_axioms);
        int sum=-1;
        if(true_arguments) {
            int pv=source.lc(source.ax(p_start),source.mul(source.ax(primitive_indices[0]),P.product),1,-1);
            int qv=source.lc(source.ax(q_start),source.mul(source.ax(primitive_indices.back()),Q.product),1,-1);
            need(source.val(pv)==P.product && source.val(qv)==Q.product,"forced true argument proof");
            sum=source.lc(pv,qv);
        } else {
            std::vector<int> input_proofs;
            for(int j=0;j<propositions;j++) {
                int q=source.ax(primitive_indices[j]);
                if(derived_inputs)q=source.lc(q,source.ax(primitive_indices[j]+1));
                need(source.val(q)==primitive[j],"primitive zero-value proof");input_proofs.push_back(q);
            }
            for(int j=0;j<width;j++)sum=source.lc(sum,source.mul(input_proofs[j],P.coef[j]),1,-1);
            sum=source.lc(sum,source.mul(input_proofs.back(),Q.coef[0]),1,-1);
        }
        need(source.val(sum)==P.product+Q.product-Poly(p,true_arguments?0:2),"antecedent scalar preparation");
        int source_final=sum;
        if(negative)source_final=true_arguments?source.lc(sum,source.ax(int(axioms.size())),1,-1)
                                              :source.lc(source.ax(int(axioms.size())),sum,1,-1);
        for(const auto& line:source.lines)need(!uses(line.value,bar.first,bar.end),"antecedent proof uses the implication copy");
        trace(out,sign+"_antecedent",source,source_final,negative?one:u,s+(true_arguments?1:0));

        Poly power=powp(v,p-1),alpha=negative?one-power:power,common(p);
        if(negative)common=powp(v,p-2);
        else for(int j=0;j<p-1;j++)common=common+Poly(p,modpow((residue+p-1)%p,j,p))*powp(v,p-2-j);
        auto implication_axioms=std::vector<Poly>{alpha};implication_axioms.insert(implication_axioms.end(),goal.begin(),goal.end());
        Proof implication(p,implication_axioms);int unit=implication.ax(0);
        for(int j=0;j<width;j++)unit=implication.lc(unit,implication.mul(implication.ax(j+1),common*bar.coef[j]),1,negative?-1:1);
        unit=implication.lc(unit,implication.mul(implication.ax(width+1),common),1,negative?1:-1);
        for(const auto& line:implication.lines)need(!uses(line.value,P.first,P.end),"implication uses the antecedent-child copy");
        trace(out,sign+"_implication_input_refutation",implication,unit,one,(p-1)*s);

        auto joined_axioms=axioms;joined_axioms.insert(joined_axioms.end(),goal.begin(),goal.end());
        Proof joined(p,joined_axioms);
        int copied_difference=mapped(copy,difference,joined,one,NV,[&](int a){return joined.ax(a);});
        int antecedent_value=-1;
        if(!negative) {
            int scalar=mapped(source,source_final,joined,one,NV,[&](int a){return joined.ax(a);});
            int left_scalar=joined.lc(scalar,copied_difference,1,-1);
            need(joined.val(left_scalar)==v,"left scalar conversion");
            antecedent_value=joined.mul(left_scalar,powp(v,p-2));
        } else {
            int relation=field_proof(joined,v-powp(v,p),sizes);
            int weighted_assumption=joined.lc(relation,joined.mul(copied_difference,alpha));
            need(joined.val(weighted_assumption)==alpha*u,"negative weighted assumption");
            antecedent_value=mapped(source,source_final,joined,alpha,NV,[&](int a) {
                if(a<int(axioms.size()))return joined.mul(joined.ax(a),alpha);
                need(a==int(axioms.size()),"unexpected extra assumption");return weighted_assumption;
            });
        }
        need(joined.val(antecedent_value)==alpha,"antecedent value");
        int final=mapped(implication,unit,joined,one,NV,[&](int a) {
            return a==0?antecedent_value:joined.ax(int(axioms.size())+a-1);
        });
        int bound=negative?p*s+(true_arguments?1:0):std::max(2*s,(p-1)*s);
        trace(out,sign+"_joined_MP",joined,final,one,bound);
        Proof clean(p,clean_axioms);
        int clean_final=mapped(joined,final,clean,one,first,[&](int a) {
            Poly q=specialize(joined.axioms[a],first,zero);if(q.terms.empty())return -1;
            auto found=std::find(clean.axioms.begin(),clean.axioms.end(),q);
            need(found!=clean.axioms.end(),"no old axiom or goal input for an image");return clean.ax(int(found-clean.axioms.begin()));
        });
        trace(out,sign+"_partial_frontier_replay",clean,clean_final,one,joined.degree,first);
        Poly residual=Q.product-Poly(p,1-residue);
        need(residual.deg()>0 && specialize(u,first,zero)==residual && specialize(v,first,zero)==residual,"residual scalar lost");
        for(const auto& f:goal)need(specialize(f,first,zero)==f,"goal was changed");
        for(int j=0;j<width;j++) {
            need(specialize(P.axioms[j],first,zero)==inputs[j],"first companion image");
            need(specialize(bar.axioms[j],first,zero)==inputs[j],"second companion image");
            need(specialize(P.coef[j],first,zero).terms.empty() && specialize(bar.coef[j],first,zero).terms.empty(),"copy prefix survives");
        }
        // Removing Q as well would change the named goal input to one.
        need(specialize(Q.product,Q.first,zero)==one && !(Q.product==one),"protected goal control");
        out<<"{\"record\":\"partial_ledger\",\"sign\":\""<<sign<<"\",\"residue\":"<<residue
           <<",\"source_scalar\":";jsonpoly(out,u);out<<",\"residual_scalar\":";jsonpoly(out,residual);
        out<<",\"retained_field_relation\":";jsonpoly(out,residual-powp(residual,p));
        out<<",\"scalar_is_nonconstant\":true,\"goal_unchanged\":true,\"copy_prefix_images_zero\":true,"
             "\"removed_argument_copies\":2,\"retained_argument_copies\":1,"
             "\"zeroing_Q_changes_goal_input_to_one\":true}\n";
    }
}
void controls(std::ostream& out) {
    for(int p:{2,3}) {
        // Literal coverage of x alone does not justify the zeroed y companion.
        Poly x=variable(p,0),y=variable(p,1);auto old=domains(p,{2,2});old.push_back(x);
        std::array<int,NV> point{};point[1]=1;
        for(const auto& f:old)need(specialize(f,0,point).terms.empty(),"coverage-control old model");
        need(specialize(y,0,point)==Poly(p,1),"uncovered image control");
        out<<"{\"record\":\"missing_coverage_control\",\"p\":"<<p<<",\"selected_inputs\":[\"x\",\"y\"],"
             "\"goal\":[\"x\"],\"old_boolean_model\":[0,1],\"uncovered_y_image\":1}\n";
    }
}
int main(int argc,char** argv) {
    try {
        need((argc==3 || argc==4) && std::string(argv[1])=="--out","--out NEW_PATH [--true-arguments-only] required");
        bool true_only=argc==4;
        if(true_only)need(std::string(argv[3])=="--true-arguments-only","unknown option");
        need(!std::filesystem::exists(argv[2]),"output exists");
        auto parent=std::filesystem::path(argv[2]).parent_path();if(!parent.empty())std::filesystem::create_directories(parent);
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"partial_mod_frontiers\",\"seed\":null,"
               "\"scope\":\"complete two-copy algebraic MP with explicit antecedent and implication input proofs\"}\n";
        if(true_only) {
            fixture(out,8,2,3,1,false,true);fixture(out,9,3,3,1,false,true);
        } else {
            int id=0;
            for(int p:{2,3}) {
                fixture(out,id++,p,2,1,false);fixture(out,id++,p,4,1,false);
                fixture(out,id++,p,2,2,false);fixture(out,id++,p,2,1,true);
            }
            controls(out);
        }
        out<<"{\"record\":\"summary\",\"cases\":"<<(true_only?2:8)<<",\"pc_traces\":"<<(true_only?18:72)
           <<",\"missing_coverage_controls\":"<<(true_only?0:2)<<",\"conditional_image_models\":"<<(true_only?2:0)
           <<",\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failed");
        std::cout<<(true_only?"Two true-argument cases and 18 PC traces":"Eight partial-frontier cases and 72 PC traces")
                 <<" passed with their controls.\n";
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
