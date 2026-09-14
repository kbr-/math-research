// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact ordinary-PC traces for the affine-clause rules, using the existing verifier.
#include "pc_boundary.hpp"
using namespace boundary_pc;
int evaluate(const Poly& p,const std::array<int,NV>& point){
    int sum=0;for(const auto& [m,c]:p.terms){
        int term=c;for(int i=0;i<NV;++i)term=term*modpow(point[i],m[i],p.p)%p.p;
        sum=(sum+term)%p.p;
    }return sum;
}
int companions(std::vector<Poly>& ax,const Block& b){
    int first=int(ax.size());ax.insert(ax.end(),b.axioms.begin(),b.axioms.end());return first;
}
Block empty_block(int next){return {Poly(2,1),{},{},{},next,next};}
int input_index(const Block& b,const Poly& g){
    for(std::size_t i=0;i<b.inputs.size();++i)if(b.inputs[i]==g)return int(i);
    throw std::runtime_error("context not present in resolvent");
}
int resolution(Proof& pc,const Block& A,int knownA,int pivotA,
               const Block& B,int knownB,int pivotB,const Block& T,
               int target_companions,int variables){
    Poly one(2,1),ell=A.inputs[pivotA];
    need(ell+B.inputs[pivotB]==one,"noncomplementary pivots");
    auto relation=[&](const Block& C,int known,int pivot){
        int result=pc.mul(known,T.product);
        for(std::size_t i=0;i<C.inputs.size();++i)if(int(i)!=pivot){
            int index=input_index(T,C.inputs[i]);
            result=pc.lc(result,pc.mul(pc.ax(target_companions+index),C.coef[i]));
        }
        need(pc.val(result)==T.product-C.coef[pivot]*C.inputs[pivot]*T.product,"prefix relation");
        return result;
    };
    int ra=relation(A,knownA,pivotA),rb=relation(B,knownB,pivotB);
    int cut=pc.mul(ra,one-ell);
    int domain=field_proof(pc,ell*ell-ell,std::vector<int>(variables,2));
    cut=pc.lc(cut,pc.mul(domain,A.coef[pivotA]*T.product),1,-1);
    need(pc.val(cut)==(one-ell)*T.product,"cut literal");
    int result=pc.lc(rb,pc.mul(cut,B.coef[pivotB]));
    need(pc.val(result)==T.product,"resolution conclusion");return result;
}
int weakening(Proof& pc,const Block& C,int knownC,const Block& D,int target_companions,
              const std::vector<std::vector<int>>& rows){
    need(rows.size()==C.inputs.size(),"weakening witness row count");
    int result=pc.mul(knownC,D.product);
    for(std::size_t i=0;i<C.inputs.size();++i){
        need(rows[i].size()==D.inputs.size(),"weakening witness column count");
        Poly input(2);int image=-1;
        for(std::size_t j=0;j<D.inputs.size();++j)if(rows[i][j]){
            input=input+D.inputs[j];image=pc.lc(image,pc.ax(target_companions+int(j)));
        }
        need(input==C.inputs[i],"invalid semantic-weakening witness");
        need(pc.val(image)==C.inputs[i]*D.product,"weakening input image");
        result=pc.lc(result,pc.mul(image,C.coef[i]));
    }
    need(pc.val(result)==D.product,"weakening conclusion");return result;
}
int initial(Proof& pc,const Block& C,int first,int old_equation){
    Poly one(2,1),E=one;
    for(const auto& g:C.inputs)E=E*(one-g);
    need(pc.axioms[old_equation]==E,"initial encoding");
    int result=pc.mul(pc.ax(old_equation),C.product);
    Poly prefix=one;
    for(std::size_t i=0;i<C.inputs.size();++i){
        result=pc.lc(result,pc.mul(pc.ax(first+int(i)),prefix));
        prefix=prefix*(one-C.inputs[i]);
    }
    need(pc.val(result)==C.product,"initial approximation proof");return result;
}
void block_data(std::ostream& out,const std::string& name,const Block& b,int h){
    out<<"{\"record\":\"block\",\"name\":\""<<name<<"\",\"accuracy\":"<<h
       <<",\"first_coefficient\":"<<b.first<<",\"end_coefficient\":"<<b.end
       <<",\"inputs\":[";
    for(std::size_t i=0;i<b.inputs.size();++i){if(i)out<<',';jsonpoly(out,b.inputs[i]);}
    out<<"],\"product\":";jsonpoly(out,b.product);out<<",\"prefixes\":[";
    for(std::size_t i=0;i<b.coef.size();++i){if(i)out<<',';jsonpoly(out,b.coef[i]);}
    out<<"]}\n";
}
void finish(std::ostream& out,const std::string& name,const Proof& proof,int final,const Poly& target,int budget){
    need(proof.val(final)==target && proof.degree<=budget && proof.verify(),"PC trace verification");
    need(!proof.verify(final),"corruption control");
    proof.write(out,name,final);
    out<<"{\"record\":\"verified_case\",\"name\":\""<<name<<"\",\"budget\":"<<budget
       <<",\"actual_degree\":"<<proof.degree<<",\"proof_lines\":"<<proof.lines.size()
       <<",\"stored_polynomial_terms\":"<<proof.stored_terms<<"}\n";
    std::cout<<name<<": "<<proof.lines.size()<<" primitive PC lines, degree "
             <<proof.degree<<" <= "<<budget<<".\n";
}
void assign_block(const Block& b,int h,std::array<int,NV>& point){
    for(int i=b.first;i<b.end;++i)point[i]=0;
    for(std::size_t i=0;i<b.inputs.size();++i)if(evaluate(b.inputs[i],point)){
        point[b.first+int(i)]=1;break;
    }
    (void)h;
}
void write_model(std::ostream& out,const std::string& name,const std::array<int,NV>& point,
                 int variables,const std::vector<Poly>& base,
                 const std::vector<std::pair<std::string,Poly>>& observed){
    for(const auto& g:base)need(evaluate(g,point)==0,"model violates a base equation");
    out<<"{\"record\":\"Boolean_model\",\"name\":\""<<name<<"\",\"assignment\":[";
    for(int i=0;i<variables;++i){if(i)out<<',';out<<point[i];}
    out<<"],\"observed\":[";
    for(std::size_t i=0;i<observed.size();++i){
        if(i)out<<',';
        out<<"{\"name\":\""<<observed[i].first<<"\",\"value\":"
           <<evaluate(observed[i].second,point)<<'}';
    }
    out<<"]}\n";
}
void resolution_case(std::ostream& out,int h){
    Poly one(2,1);auto x=[&](int i){return variable(2,i);};
    auto a=one+x(0)+x(2),b=x(1)+x(3),ell=one+x(2)+x(3);
    int next=4;
    auto A=block({a,ell},h,next),B=block({b,one-ell},h,next),T=block({a,b},h,next);
    auto axiom=domains(2,std::vector<int>(next,2));
    companions(axiom,A);companions(axiom,B);int target=companions(axiom,T);
    auto base=axiom;
    int pa=int(axiom.size());axiom.push_back(A.product);
    int pb=int(axiom.size());axiom.push_back(B.product);
    Proof proof(2,axiom);
    int result=resolution(proof,A,proof.ax(pa),1,B,proof.ax(pb),1,T,target,next);
    std::string name="resolution_h"+std::to_string(h);
    block_data(out,name+"/A",A,h);block_data(out,name+"/B",B,h);block_data(out,name+"/T",T,h);
    finish(out,name,proof,result,T.product,4*h+1);
    std::array<bool,3> found{};
    for(unsigned bits=0;bits<16;++bits){
        std::array<int,NV> point{};for(int i=0;i<4;++i)point[i]=(bits>>i)&1;
        for(const auto* block:{&A,&B,&T})assign_block(*block,h,point);
        int va=evaluate(A.product,point),vb=evaluate(B.product,point),vt=evaluate(T.product,point);
        int type=(va==0 && vb==0 && vt==0)?0:(va==0 && vb==1 && vt==1)?1:(va==1 && vb==0 && vt==1)?2:-1;
        if(type>=0 && !found[type]){
            found[type]=true;
            write_model(out,name+(type==0?"/satisfiable":type==1?"/missing_B":"/missing_A"),point,next,base,
                        {{"premise_A",A.product},{"premise_B",B.product},{"target",T.product}});
        }
    }
    need(found[0] && found[1] && found[2],"missing nonvacuity controls");
}
void weakening_case(std::ostream& out,int h){
    auto x=[&](int i){return variable(2,i);};int next=3;
    auto C=block({x(0)+x(1),x(1)+x(2)},h,next),D=block({x(0),x(1),x(2)},h,next);
    auto axiom=domains(2,std::vector<int>(next,2));companions(axiom,C);int dest=companions(axiom,D);
    auto base=axiom;int premise=int(axiom.size());axiom.push_back(C.product);
    Proof proof(2,axiom);
    int result=weakening(proof,C,proof.ax(premise),D,dest,{{1,1,0},{0,1,1}});
    std::string name="weakening_h"+std::to_string(h);
    block_data(out,name+"/C",C,h);block_data(out,name+"/D",D,h);
    finish(out,name,proof,result,D.product,4*h);
    for(int bit:{0,1}){
        std::array<int,NV> point{};point[0]=bit;assign_block(C,h,point);assign_block(D,h,point);
        need(evaluate(C.product,point)==1-bit && evaluate(D.product,point)==1-bit,"weakening model control");
        write_model(out,name+(bit?"/satisfiable":"/missing_premise"),point,next,base,
                    {{"premise",C.product},{"target",D.product}});
    }
    std::array<int,NV> zero{};
    auto bad=Poly(2,1)+x(0);
    need(evaluate(bad,zero)==1 && evaluate(x(0),zero)==0 && evaluate(x(1),zero)==0 && evaluate(x(2),zero)==0,
         "invalid weakening countermodel");
    out<<"{\"record\":\"invalid_weakening_control\",\"case\":\""<<name
       <<"\",\"old_assignment\":[0,0,0],\"bad_premise_true_indicator\":";
    jsonpoly(out,bad);out<<",\"conclusion_true_indicators\":[";
    for(int i=0;i<3;++i){if(i)out<<',';jsonpoly(out,x(i));}
    out<<"],\"entailed\":false}\n";
}
void tautology_case(std::ostream& out,int h){
    Poly one(2,1);auto g=one+variable(2,0)+variable(2,1);int next=2;
    auto D=block({g,one-g},h,next);auto axiom=domains(2,std::vector<int>(next,2));
    int start=companions(axiom,D);Proof proof(2,axiom);
    int result=proof.lc(proof.ax(start),proof.ax(start+1));
    finish(out,"tautology_h"+std::to_string(h),proof,result,D.product,2*h+1);
}
void initial_case(std::ostream& out,int h){
    auto x=[&](int i){return variable(2,i);};Poly one(2,1);int next=4;
    auto C=block({x(0)+x(2),x(1)+x(3)},h,next);
    auto axiom=domains(2,std::vector<int>(next,2));int c=companions(axiom,C);
    int equation=int(axiom.size());axiom.push_back((one-C.inputs[0])*(one-C.inputs[1]));
    Proof proof(2,axiom);int result=initial(proof,C,c,equation);
    std::string name="initial_ell2_h"+std::to_string(h);
    block_data(out,name+"/C",C,h);finish(out,name,proof,result,C.product,2*h+2);
    std::array<int,NV> point{};point[2]=1;assign_block(C,h,point);
    write_model(out,name+"/satisfiable_two_row_base",point,next,axiom,{{"target",C.product}});
}
void full_two_hole(std::ostream& out,int h){
    auto x=[&](int i){return variable(2,i);};Poly one(2,1);
    auto g0=x(0)+x(1),g1=x(1)+x(2),g2=x(0)+x(2);int next=3;
    auto C01=block({g0},h,next),C12=block({g1},h,next),C02=block({g2},h,next);
    auto W=block({one-g2,one-g1},h,next),D=block({one-g2},h,next),T=empty_block(next);
    auto axiom=domains(2,std::vector<int>(next,2));
    int c01=companions(axiom,C01),c12=companions(axiom,C12),c02=companions(axiom,C02);
    int cw=companions(axiom,W),cd=companions(axiom,D);
    int old=int(axiom.size());axiom.push_back(one-g0);axiom.push_back(one-g1);axiom.push_back(one-g2);
    Proof proof(2,axiom);
    int a=initial(proof,C01,c01,old),b=initial(proof,C12,c12,old+1),c=initial(proof,C02,c02,old+2);
    int w=weakening(proof,C01,a,W,cw,{{1,1}});
    int d=resolution(proof,W,w,1,C12,b,0,D,cd,next);
    int final=resolution(proof,D,d,0,C02,c,0,T,0,next);
    std::string name="full_two_hole_h"+std::to_string(h);
    for(const auto& [label,block]:std::vector<std::pair<std::string,Block>>{
            {"C01",C01},{"C12",C12},{"C02",C02},{"W",W},{"D",D}})
        block_data(out,name+"/"+label,block,h);
    need((one-g0)+(one-g1)+(one-g2)==one,"small-board range control");
    out<<"{\"record\":\"scope\",\"case\":\""<<name
       <<"\",\"pigeons\":3,\"holes\":2,\"ell\":1,"
         "\"note\":\"Complete composition control; ell=1 lies outside the ell>=2 affine-bit lower-bound theorem, and this old base already refutes in degree one.\"}\n";
    finish(out,name,proof,final,one,4*h+1);
}
void semantic_pair_case(std::ostream& out,int h){
    Poly one(2,1);auto x=variable(2,0),y=variable(2,1);int next=2;
    auto A=block({x},h,next),B=block({y},h,next),D=block({one+x+y},h,next);
    auto W0=block({one+x+y,x},h,next),W1=block({one+x+y,one+x},h,next);
    auto axiom=domains(2,std::vector<int>(next,2));
    companions(axiom,A);companions(axiom,B);int dest=companions(axiom,D);
    int w0=companions(axiom,W0),w1=companions(axiom,W1);auto base=axiom;
    int pa=int(axiom.size());axiom.push_back(A.product);
    int pb=int(axiom.size());axiom.push_back(B.product);
    Proof proof(2,axiom);
    int a=weakening(proof,A,proof.ax(pa),W0,w0,{{0,1}});
    int b=weakening(proof,B,proof.ax(pb),W1,w1,{{1,1}});
    int result=resolution(proof,W0,a,1,W1,b,1,D,dest,next);
    std::string name="semantic_pair_h"+std::to_string(h);
    for(const auto& [label,block]:std::vector<std::pair<std::string,Block>>{
            {"A",A},{"B",B},{"D",D},{"W0",W0},{"W1",W1}})
        block_data(out,name+"/"+label,block,h);
    finish(out,name,proof,result,D.product,4*h+1);
    for(const auto& [vx,vy]:std::vector<std::pair<int,int>>{{1,1},{1,0},{0,1}}){
        std::array<int,NV> point{};point[0]=vx;point[1]=vy;
        for(const auto* block:{&A,&B,&D,&W0,&W1})assign_block(*block,h,point);
        need(evaluate(A.product,point)==1-vx && evaluate(B.product,point)==1-vy,"semantic premise values");
        need(evaluate(D.product,point)==(vx^vy),"semantic target value");
        write_model(out,name+(vx&&vy?"/satisfiable":vx?"/missing_B":"/missing_A"),point,next,base,
                    {{"premise_A",A.product},{"premise_B",B.product},{"target",D.product}});
    }
    out<<"{\"record\":\"affine_two_cover\",\"case\":\""<<name
       <<"\",\"conclusion_false_points\":[[0,1],[1,0]],"
         "\"first_premise_false_half\":[[0,1]],\"second_premise_false_half\":[[1,0]],"
         "\"separator\":\"x_0\",\"proper_binary_inference\":true}\n";
}
int main(int argc,char** argv){
    try{
        need((argc==3 || (argc==4 && std::string(argv[3])=="--semantic")) &&
             std::string(argv[1])=="--out","usage: --out NEW_PATH [--semantic]");
        bool semantic=argc==4;
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");
        out<<"{\"record\":\"schema\",\"version\":1,\"field\":2,"
              "\"polynomials\":\"coefficient and sparse [variable,exponent] pairs\","
              "\"PC_rules\":\"a=axiom, l=two-term linear combination, m=multiply by one variable; -1 is zero contribution\","
              "\"linear_clause_literals\":\"g=1 is true; all g=0 falsifies the clause\"}\n";
        for(int h:{1,2}){
            resolution_case(out,h);weakening_case(out,h);tautology_case(out,h);
            initial_case(out,h);full_two_hole(out,h);
        }
        if(semantic)for(int h:{1,2})semantic_pair_case(out,h);
        out<<"{\"record\":\"summary\",\"verified_PC_traces\":"<<(semantic?12:10)<<",\"resolution_models\":6,"
              "\"weakening_models\":4,\"initial_satisfying_models\":2,"
              "\"invalid_weakening_controls\":2";
        if(semantic)out<<",\"semantic_inference_traces\":2,\"semantic_inference_models\":6";
        out<<",\"passed\":true}\n";
        need(bool(out),"output write");
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
