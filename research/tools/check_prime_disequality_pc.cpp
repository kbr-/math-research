// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Primitive ordinary-PC traces for the explicitly defined affine-disequality calculus.
#include "pc_boundary.hpp"
using namespace boundary_pc;
int verified=0;
int evaluate(const Poly& f,const std::array<int,NV>& point){
    int value=0;
    for(const auto& [mon,c]:f.terms){
        int term=c;
        for(int i=0;i<NV;++i)term=term*modpow(point[i],mon[i],f.p)%f.p;
        value=(value+term)%f.p;
    }
    return value;
}
int companion_axioms(std::vector<Poly>& axioms,const Block& b){
    int first=int(axioms.size());axioms.insert(axioms.end(),b.axioms.begin(),b.axioms.end());
    return first;
}
Block empty_block(int p,int next){return {Poly(p,1),{},{},{},next,next};}
int input_index(const Block& b,const Poly& g){
    for(std::size_t i=0;i<b.inputs.size();++i)if(b.inputs[i]==g)return int(i);
    throw std::runtime_error("missing conclusion context");
}
void block_data(std::ostream& out,const std::string& name,const Block& b,int h){
    out<<"{\"record\":\"block\",\"name\":\""<<name<<"\",\"field\":"<<b.product.p
       <<",\"accuracy\":"<<h<<",\"first_coefficient\":"<<b.first
       <<",\"end_coefficient\":"<<b.end<<",\"inputs\":[";
    for(std::size_t i=0;i<b.inputs.size();++i){if(i)out<<',';jsonpoly(out,b.inputs[i]);}
    out<<"],\"product\":";jsonpoly(out,b.product);out<<",\"prefixes\":[";
    for(std::size_t i=0;i<b.coef.size();++i){if(i)out<<',';jsonpoly(out,b.coef[i]);}
    out<<"]}\n";
}
void parameters(std::ostream& out,const std::string& name,int p,int h,
                const std::vector<int>& sizes,const std::string& scope){
    out<<"{\"record\":\"case_parameters\",\"name\":\""<<name<<"\",\"field\":"<<p
       <<",\"accuracy\":"<<h<<",\"scope\":\""<<scope<<"\",\"domain_exponents\":[";
    for(std::size_t i=0;i<sizes.size();++i){if(i)out<<',';out<<sizes[i];}
    out<<"]}\n";
}
void finish(std::ostream& out,const std::string& name,const Proof& proof,int final,
            const Poly& target,int budget){
    need(proof.val(final)==target && proof.degree<=budget && proof.verify(),"PC replay "+name);
    need(final>=0 && !proof.verify(final),"corrupted trace not rejected");
    proof.write(out,name,final);
    out<<"{\"record\":\"verified_case\",\"name\":\""<<name<<"\",\"field\":"<<proof.p
       <<",\"budget\":"<<budget<<",\"actual_degree\":"<<proof.degree
       <<",\"primitive_lines\":"<<proof.lines.size()
       <<",\"stored_terms\":"<<proof.stored_terms<<"}\n";
    ++verified;
    std::cout<<name<<": "<<proof.lines.size()<<" primitive lines, degree "<<proof.degree
             <<" <= "<<budget<<".\n";
}
void assign_block(const Block& b,std::array<int,NV>& point){
    for(int i=b.first;i<b.end;++i)point[i]=0;
    for(std::size_t i=0;i<b.inputs.size();++i){
        int value=evaluate(b.inputs[i],point);
        if(value){point[b.first+int(i)]=modpow(value,b.product.p-2,b.product.p);break;}
    }
}
void model(std::ostream& out,const std::string& name,const std::array<int,NV>& point,
           int variables,const std::vector<Poly>& axioms,const std::vector<int>& omitted,
           const std::vector<std::pair<std::string,Poly>>& observations){
    out<<"{\"record\":\"typed_model\",\"name\":\""<<name<<"\",\"assignment\":[";
    for(int i=0;i<variables;++i){if(i)out<<',';out<<point[i];}
    out<<"],\"omitted_axiom_ids\":[";
    for(std::size_t i=0;i<omitted.size();++i){if(i)out<<',';out<<omitted[i];}
    out<<"],\"axiom_values\":[";
    for(std::size_t i=0;i<axioms.size();++i){
        int value=evaluate(axioms[i],point);
        bool skip=std::find(omitted.begin(),omitted.end(),int(i))!=omitted.end();
        need(skip || value==0,"model violates a retained axiom");
        if(i)out<<',';
        out<<value;
    }
    out<<"],\"observed\":[";
    for(std::size_t i=0;i<observations.size();++i){
        if(i)out<<',';
        out<<"{\"name\":\""<<observations[i].first<<"\",\"polynomial\":";
        jsonpoly(out,observations[i].second);
        out<<",\"value\":"<<evaluate(observations[i].second,point)<<'}';
    }
    out<<"]}\n";
}
int p_cut(Proof& pc,const std::vector<Block>& premises,const std::vector<int>& known,
          const std::vector<int>& pivots,const Block& target,int target_first,
          const Poly& u,const std::vector<int>& sizes){
    int p=pc.p;Poly one(p,1),partition(p);
    need(premises.size()==std::size_t(p) && known.size()==premises.size(),"p-way premise count");
    int domain=field_proof(pc,powp(u,p)-u,sizes),result=-1;
    for(int a=0;a<p;++a){
        const auto& A=premises[a];int pivot=pivots[a];
        auto g=u-Poly(p,a);
        need(A.inputs[pivot]==g,"pivot label mismatch");
        int relation=pc.mul(known[a],target.product);
        for(std::size_t i=0;i<A.inputs.size();++i)if(int(i)!=pivot){
            int j=input_index(target,A.inputs[i]);
            relation=pc.lc(relation,pc.mul(pc.ax(target_first+j),A.coef[i]));
        }
        need(pc.val(relation)==target.product-A.coef[pivot]*g*target.product,"cut prefix relation");
        auto chi=one-powp(g,p-1);partition=partition+chi;
        int piece=pc.mul(relation,chi);
        piece=pc.lc(piece,pc.mul(domain,A.coef[pivot]*target.product),1,-1);
        need(pc.val(piece)==chi*target.product,"residue selector piece");
        result=pc.lc(result,piece);
    }
    need(partition==one && pc.val(result)==target.product,"selector partition conclusion");
    return result;
}
int weakening(Proof& pc,const Block& C,int known,const Block& D,int first,
              const std::vector<std::vector<int>>& witness){
    need(witness.size()==C.inputs.size(),"weakening row count");
    int result=pc.mul(known,D.product);
    for(std::size_t i=0;i<C.inputs.size();++i){
        need(witness[i].size()==D.inputs.size(),"weakening column count");
        Poly input(pc.p);int image=-1;
        for(std::size_t j=0;j<D.inputs.size();++j){
            input=input+Poly(pc.p,witness[i][j])*D.inputs[j];
            if(witness[i][j])image=pc.lc(image,pc.ax(first+int(j)),1,witness[i][j]);
        }
        need(input==C.inputs[i] && pc.val(image)==input*D.product,"affine-span weakening witness");
        result=pc.lc(result,pc.mul(image,C.coef[i]));
    }
    need(pc.val(result)==D.product,"weakening conclusion");return result;
}
int initial(Proof& pc,const Block& C,int first,int old_equation){
    int p=pc.p;Poly one(p,1),E=one;
    for(const auto& g:C.inputs)E=E*(one-powp(g,p-1));
    need(pc.axioms[old_equation]==E,"prime-field initial encoding");
    int result=pc.mul(pc.ax(old_equation),C.product);Poly prefix=one;
    for(std::size_t i=0;i<C.inputs.size();++i){
        result=pc.lc(result,pc.mul(pc.ax(first+int(i)),prefix*powp(C.inputs[i],p-2)));
        prefix=prefix*(one-powp(C.inputs[i],p-1));
    }
    need(pc.val(result)==C.product,"initial clause conclusion");return result;
}
void cut_case(std::ostream& out,int p,int h,bool Boolean_sum){
    int old=Boolean_sum?p:2,next=old;
    Poly u(p),z=variable(p,old-1);
    if(Boolean_sum){for(int i=0;i<p-1;++i)u=u+variable(p,i);}
    else u=variable(p,0);
    std::vector<Block> A;std::vector<int> pivots;
    for(int a=0;a<p;++a){
        std::vector<Poly> inputs;
        if(a==0)inputs.push_back(z);
        pivots.push_back(int(inputs.size()));inputs.push_back(u-Poly(p,a));
        A.push_back(block(inputs,h,next));
    }
    auto T=block({z},h,next);need(next<=NV,"fixture variable count");
    std::vector<int> sizes(next,p);
    if(Boolean_sum)for(int i=0;i<old;++i)sizes[i]=2;
    else sizes[1]=2;
    auto ax=domains(p,sizes);
    for(const auto& a:A)companion_axioms(ax,a);
    int first=companion_axioms(ax,T);std::vector<int> assumptions;
    for(const auto& a:A){assumptions.push_back(int(ax.size()));ax.push_back(a.product);}
    Proof pc(p,ax);std::vector<int> known;
    for(int id:assumptions)known.push_back(pc.ax(id));
    int final=p_cut(pc,A,known,pivots,T,first,u,sizes);
    std::string name="p_cut_F"+std::to_string(p)+"_h"+std::to_string(h)+(Boolean_sum?"_Boolean_sum":"_field_pivot");
    parameters(out,name,p,h,sizes,"conditional premise-value proofs; old pivot domain explicitly typed");
    for(int a=0;a<p;++a)block_data(out,name+"/A"+std::to_string(a),A[a],h);
    block_data(out,name+"/T",T,h);
    finish(out,name,pc,final,T.product,4*h+p-1);
    std::array<int,NV> point{};point[old-1]=1;
    for(const auto& a:A)assign_block(a,point);
    assign_block(T,point);need(evaluate(T.product,point)==0,"satisfiable cut model");
    model(out,name+"/satisfiable",point,next,ax,{},{{"conclusion",T.product}});
    for(int a=0;a<p;++a){
        point={};
        if(Boolean_sum){for(int i=0;i<a;++i)point[i]=1;}
        else point[0]=a;
        for(const auto& b:A)assign_block(b,point);
        assign_block(T,point);
        need(evaluate(u,point)==a && evaluate(T.product,point)==1,"missing-residue assignment");
        model(out,name+"/missing_residue_"+std::to_string(a),point,next,ax,{assumptions[a]},
              {{"omitted_premise",A[a].product},{"conclusion",T.product}});
    }
}
void weakening_case(std::ostream& out,int p,int h){
    int next=3;auto x=[&](int i){return variable(p,i);};
    auto C=block({x(0)+Poly(p,2)*x(1),x(1)-x(2)},h,next);
    auto D=block({x(0),x(1),x(2)},h,next);
    std::vector<int> sizes(next,p);for(int i=0;i<3;++i)sizes[i]=2;
    auto ax=domains(p,sizes);companion_axioms(ax,C);int first=companion_axioms(ax,D);
    int premise=int(ax.size());ax.push_back(C.product);Proof pc(p,ax);
    int final=weakening(pc,C,pc.ax(premise),D,first,{{1,2,0},{0,1,-1}});
    std::string name="weakening_F"+std::to_string(p)+"_h"+std::to_string(h);
    parameters(out,name,p,h,sizes,"full-field affine-span weakening with a conditional premise");
    block_data(out,name+"/C",C,h);block_data(out,name+"/D",D,h);
    finish(out,name,pc,final,D.product,4*h);
    for(int bit:{0,1}){
        std::array<int,NV> point{};point[0]=bit;assign_block(C,point);assign_block(D,point);
        need(evaluate(D.product,point)==1-bit,"weakening model");
        model(out,name+(bit?"/satisfiable":"/missing_premise"),point,next,ax,
              bit?std::vector<int>{}:std::vector<int>{premise},{{"conclusion",D.product}});
    }
}
void tautology_case(std::ostream& out,int p,int h){
    int next=1;auto x=variable(p,0);Poly one(p,1);
    auto D=block({x,one-x},h,next);
    std::vector<int> sizes(next,p);auto ax=domains(p,sizes);int first=companion_axioms(ax,D);
    Proof pc(p,ax);int final=pc.lc(pc.ax(first),pc.ax(first+1));
    std::string name="tautology_F"+std::to_string(p)+"_h"+std::to_string(h);
    parameters(out,name,p,h,sizes,"unit affine span over the full field");
    block_data(out,name+"/D",D,h);finish(out,name,pc,final,D.product,2*h+1);
    std::array<int,NV> point{};point[0]=2;assign_block(D,point);
    need(evaluate(D.product,point)==0,"tautology model");
    model(out,name+"/nonBoolean_field_value",point,next,ax,{},{{"conclusion",D.product}});
}
void Boolean_domain_case(std::ostream& out,int p,int h,int a){
    need(a>=2 && a<p,"Boolean domain exclusion label");
    int next=1;auto b=variable(p,0);Poly one(p,1);
    auto D=block({b-Poly(p,a)},h,next);
    std::vector<int> sizes(next,p);sizes[0]=2;
    auto ax=domains(p,sizes);int first=companion_axioms(ax,D);Proof pc(p,ax);
    int w0=modpow(p-a,p-2,p),w1=modpow((1-a+p)%p,p-2,p);
    Poly slope(p,w1-w0),w=Poly(p,w0)+slope*b;
    need(w*D.inputs[0]-one==slope*(b*b-b),"affine inverse modulo Booleanity");
    int final=pc.lc(pc.mul(pc.ax(first),w),pc.mul(pc.ax(0),slope*D.product),1,-1);
    std::string name="Boolean_domain_F"+std::to_string(p)+"_h"+std::to_string(h)+"_exclude"+std::to_string(a);
    parameters(out,name,p,h,sizes,"explicit excluded-residue clause from the old Boolean equation");
    block_data(out,name+"/D",D,h);finish(out,name,pc,final,D.product,2*h+2);
    for(int bit:{0,1}){
        std::array<int,NV> point{};point[0]=bit;assign_block(D,point);
        need(evaluate(D.product,point)==0,"Boolean domain model");
        model(out,name+"/Boolean_"+std::to_string(bit),point,next,ax,{},{{"conclusion",D.product}});
    }
    std::array<int,NV> point{};point[0]=a;assign_block(D,point);
    need(evaluate(D.product,point)==1,"omitted Boolean domain countermodel");
    model(out,name+"/missing_Boolean_axiom",point,next,ax,{0},{{"conclusion",D.product}});
}
void compact_initial_case(std::ostream& out,int p,int h){
    int next=4;auto x=[&](int i){return variable(p,i);};Poly one(p,1);
    auto C=block({x(0)-x(2),x(1)-x(3)},h,next);
    std::vector<int> sizes(next,p);for(int i=0;i<4;++i)sizes[i]=2;
    auto ax=domains(p,sizes);int first=companion_axioms(ax,C);Poly E=one;
    for(const auto& g:C.inputs)E=E*(one-powp(g,p-1));
    int old=int(ax.size());ax.push_back(E);Proof pc(p,ax);
    int final=initial(pc,C,first,old);
    std::string name="compact_pair_ell2_F"+std::to_string(p)+"_h"+std::to_string(h);
    parameters(out,name,p,h,sizes,"satisfiable two-row bit encoding; original equality degree 2(p-1)");
    block_data(out,name+"/C",C,h);finish(out,name,pc,final,C.product,2*h+2*(p-1));
    std::array<int,NV> point{};point[0]=1;assign_block(C,point);
    need(evaluate(C.product,point)==0,"distinct label model");
    model(out,name+"/distinct_labels",point,next,ax,{},{{"conclusion",C.product}});
    point={};assign_block(C,point);need(evaluate(C.product,point)==1,"equal-label control");
    model(out,name+"/missing_collision_axiom",point,next,ax,{old},{{"conclusion",C.product}});
}
void composed_case(std::ostream& out,int p,int h){
    int next=1;auto u=variable(p,0);Poly one(p,1);std::vector<Block> A;
    for(int a=0;a<p;++a)A.push_back(block({u-Poly(p,a)},h,next));
    auto T=empty_block(p,next);std::vector<int> sizes(next,p);auto ax=domains(p,sizes);
    std::vector<int> comp,old;
    for(const auto& a:A)comp.push_back(companion_axioms(ax,a));
    for(int a=0;a<p;++a){old.push_back(int(ax.size()));ax.push_back(one-powp(u-Poly(p,a),p-1));}
    Proof pc(p,ax);std::vector<int> known;
    for(int a=0;a<p;++a)known.push_back(initial(pc,A[a],comp[a],old[a]));
    int final=p_cut(pc,A,known,std::vector<int>(p,0),T,-1,u,sizes);
    std::string name="composed_partition_refutation_F"+std::to_string(p)+"_h"+std::to_string(h);
    parameters(out,name,p,h,sizes,"artificial inconsistent residue partition; actual initial proofs, no added premise-value axioms, not PHP");
    for(int a=0;a<p;++a)block_data(out,name+"/A"+std::to_string(a),A[a],h);
    finish(out,name,pc,final,one,4*h+p-1);
    for(int a=0;a<p;++a){
        std::array<int,NV> point{};point[0]=a;
        for(const auto& b:A)assign_block(b,point);
        model(out,name+"/missing_initial_"+std::to_string(a),point,next,ax,{old[a]},{{"final_target",one}});
    }
}
void semantic_cover_case(std::ostream& out){
    int p=3,h=1,next=2;auto u=variable(p,0),z=variable(p,1);
    std::vector<Block> A,B;
    for(int a=0;a<p;++a)A.push_back(block({u-Poly(p,a)+Poly(p,a)*z},h,next));
    for(int a=0;a<p;++a)B.push_back(block({z,u-Poly(p,a)},h,next));
    auto T=block({z},h,next);
    std::vector<int> sizes(next,p);sizes[1]=2;auto ax=domains(p,sizes);
    std::vector<int> bc,assumptions;
    for(const auto& a:A)companion_axioms(ax,a);
    for(const auto& b:B)bc.push_back(companion_axioms(ax,b));
    int target=companion_axioms(ax,T);
    for(const auto& a:A){assumptions.push_back(int(ax.size()));ax.push_back(a.product);}
    Proof pc(p,ax);std::vector<int> known;
    for(int a=0;a<p;++a)known.push_back(weakening(pc,A[a],pc.ax(assumptions[a]),B[a],bc[a],{{a,1}}));
    int final=p_cut(pc,B,known,std::vector<int>(p,1),T,target,u,sizes);
    std::string name="semantic_affine_cover_F3";
    parameters(out,name,p,h,sizes,"three semantic premises reduced to affine-span weakenings and a p-way cut");
    for(int a=0;a<p;++a){
        block_data(out,name+"/A"+std::to_string(a),A[a],h);
        block_data(out,name+"/B"+std::to_string(a),B[a],h);
    }
    block_data(out,name+"/T",T,h);finish(out,name,pc,final,T.product,4*h+p-1);
    for(int u0=0;u0<p;++u0)for(int z0=0;z0<p;++z0){
        std::array<int,NV> point{};point[0]=u0;point[1]=z0;bool all=true;
        out<<"{\"record\":\"full_field_semantic_check\",\"u\":"<<u0<<",\"z\":"<<z0<<",\"premise_forms\":[";
        for(int a=0;a<p;++a){
            int value=evaluate(A[a].inputs[0],point);all&=value!=0;
            if(a)out<<',';
            out<<value;
        }
        need(!all || z0!=0,"invalid full-field semantic inference");
        out<<"],\"conclusion_form\":"<<z0<<"}\n";
    }
    std::array<int,NV> point{};point[0]=point[1]=1;
    for(const auto& a:A)assign_block(a,point);
    for(const auto& b:B)assign_block(b,point);
    assign_block(T,point);model(out,name+"/satisfiable",point,next,ax,{},{{"conclusion",T.product}});
    for(int a=0;a<p;++a){
        point={};point[0]=a;
        for(const auto& b:A)assign_block(b,point);
        for(const auto& b:B)assign_block(b,point);
        assign_block(T,point);
        need(evaluate(T.product,point)==1,"semantic missing premise control");
        model(out,name+"/missing_premise_"+std::to_string(a),point,next,ax,{assumptions[a]},
              {{"conclusion",T.product}});
    }
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");
        out<<"{\"record\":\"schema\",\"version\":1,\"polynomials\":\"[coefficient,[[variable,exponent],...]]\","
             "\"PC_rules\":\"axiom, two-term field-linear combination, multiply by one variable\","
             "\"domains\":\"per-case exponents: old bits use 2, genuine field coordinates and coefficients use p\","
             "\"scope\":\"defined affine-disequality calculus; not general odd-prime equation clauses\"}\n";
        for(int p:{3,5})for(int h:{1,2}){
            cut_case(out,p,h,false);
            if(h==1)cut_case(out,p,h,true);
            weakening_case(out,p,h);tautology_case(out,p,h);
            for(int a=2;a<p;++a)Boolean_domain_case(out,p,h,a);
            compact_initial_case(out,p,h);composed_case(out,p,h);
        }
        semantic_cover_case(out);
        need(verified==31,"case inventory");
        out<<"{\"record\":\"summary\",\"verified_PC_traces\":"<<verified<<",\"passed\":true}\n";
        need(bool(out),"output write");
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
