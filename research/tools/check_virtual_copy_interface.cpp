// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Reuse the actual weighted-interface engine, without calling earlier suites.
#define VIRTUAL_OR_INTERFACE_NO_MAIN
#include "check_virtual_or_interface.cpp"

struct CopyCounts {int units=0,equalities=0,copies=0,common=0,controls=0;};
int copy_interface(Proof& dst,const Proof& unitA,int endA,const Proof& unitB,int endB,
                   const Poly& a,const Poly& b,const std::vector<int>& annA,
                   const std::vector<int>& annB,const std::vector<int>& differences) {
    need(annA.size()==annB.size() && annA.size()==differences.size(),"copy tuple lengths");
    std::vector<int> av,bu;
    for(size_t i=0;i<annA.size();i++) {
        av.push_back(dst.lc(annA[i],dst.mul(differences[i],a),1,-1));
        bu.push_back(dst.lc(annB[i],dst.mul(differences[i],b)));
    }
    int first=weighted_unit(unitB,endB,dst,a,av);
    int second=weighted_unit(unitA,endA,dst,b,bu);
    int final=dst.lc(first,second,1,-1);
    need(dst.val(final)==a-b,"copy interface target");return final;
}
void copy_point(std::ostream& out,const std::string& kind,int p,
                const std::array<int,NV>& point,int n,const Poly& a,const Poly& b,int omitted=-1) {
    out<<"{\"record\":\""<<kind<<"\",\"p\":"<<p<<",\"point\":";point_json(out,point,n);
    out<<",\"a\":"<<evaluate(a,point)<<",\"b\":"<<evaluate(b,point)
       <<",\"a_minus_b\":"<<evaluate(a-b,point)<<",\"omitted_axiom\":"<<omitted<<"}\n";
}
std::vector<Poly> pebbling_inputs(int p) {
    Poly one(p,1);std::vector<Poly> x,g;
    for(int v=0;v<7;v++)x.push_back(variable(p,v));
    const std::array<std::array<int,2>,3> pred={{{0,1},{2,3},{4,5}}};
    for(int v=0;v<7;v++)g.push_back(v<4?one-x[v]:(one-x[v])*x[pred[v-4][0]]*x[pred[v-4][1]]);
    return g;
}
int positive_sink(Proof& proof,int first) {
    int p=proof.p;Poly one(p,1);std::vector<int> known;
    const std::array<std::array<int,2>,3> pred={{{0,1},{2,3},{4,5}}};
    for(int v=0;v<7;v++) {
        Poly bv=one-variable(p,v);int id=proof.ax(first+v);
        if(v>=4) {
            auto [a,c]=pred[v-4];
            id=proof.lc(id,proof.mul(known.at(a),bv));
            id=proof.lc(id,proof.mul(known.at(c),bv*variable(p,a)));
        }
        need(proof.val(id)==bv,"positive sink proof");known.push_back(id);
    }
    return known.back();
}
std::array<int,NV> unit_point(int omitted) {
    std::array<int,NV> point{};for(int v=0;v<7;v++)point[v]=1;
    const std::array<std::array<int,2>,3> pred={{{0,1},{2,3},{4,5}}};
    if(omitted<7) {
        point[omitted]=0;
        for(int v=std::max(4,omitted+1);v<7;v++)point[v]=point[pred[v-4][0]]*point[pred[v-4][1]];
    }
    return point;
}
void different_genuine(std::ostream& out,int p,CopyCounts& count) {
    Poly one(p,1),x=variable(p,0),y=variable(p,1),z=variable(p,2);
    int next=3;Block A=block({x,z},1,next),B=block({y,z},1,next);
    std::vector<int> sizes(next,p);for(int v=0;v<3;v++)sizes[v]=2;
    auto gamma=domains(p,sizes);
    int eq=int(gamma.size());gamma.push_back(x-y);
    int aa=int(gamma.size());gamma.insert(gamma.end(),A.axioms.begin(),A.axioms.end());
    int bb=int(gamma.size());gamma.insert(gamma.end(),B.axioms.begin(),B.axioms.end());
    int endA=-1,endB=-1;Proof unitA=product_unit(gamma,A,endA),unitB=product_unit(gamma,B,endB);
    std::string suffix="_F"+std::to_string(p);
    trace(out,unitA,"different_unit_A"+suffix,endA,one-A.product,2);
    trace(out,unitB,"different_unit_B"+suffix,endB,one-B.product,2);count.units+=2;
    Proof dst(p,gamma);
    int final=copy_interface(dst,unitA,endA,unitB,endB,A.product,B.product,
                            {dst.ax(aa),dst.ax(aa+1)},{dst.ax(bb),dst.ax(bb+1)},{dst.ax(eq),-1});
    trace(out,dst,"different_genuine_copy"+suffix,final,A.product-B.product,4);count.copies++;
    out<<"{\"record\":\"copy_case\",\"kind\":\"different_genuine\",\"p\":"<<p
       <<",\"equality_degree\":1,\"copy_degree\":"<<dst.degree<<",\"inputs_A\":";
    poly_vector(out,A.inputs);out<<",\"inputs_B\":";poly_vector(out,B.inputs);out<<"}\n";
    for(int mask=0;mask<4;mask++) {
        std::array<int,NV> point{};point[0]=point[1]=mask&1;point[2]=(mask>>1)&1;
        int selected=point[0]?0:1;
        if(point[0] || point[2]){point[A.first+selected]=1;point[B.first+selected]=1;}
        models(gamma,point);need(evaluate(A.product-B.product,point)==0,"genuine copy model");
        copy_point(out,"different_common_model",p,point,next,A.product,B.product);count.common++;
    }
    std::array<int,NV> missing{};missing[0]=1;missing[A.first]=1;
    model_except(gamma,missing,eq);
    need(evaluate(A.product-B.product,missing)!=0,"missing equality control");
    copy_point(out,"missing_input_equality",p,missing,next,A.product,B.product,eq);count.controls++;
    for(int side=0;side<2;side++)for(int j=0;j<2;j++) {
        std::array<int,NV> point{};
        if(j==0)point[0]=point[1]=1;else point[2]=1;
        if(side==0)point[B.first+j]=1;else point[A.first+j]=1;
        int omitted=(side==0?aa:bb)+j;model_except(gamma,point,omitted);
        need(evaluate(A.product-B.product,point)!=0,"missing copy annihilator");
        copy_point(out,"missing_genuine_annihilator",p,point,next,A.product,B.product,omitted);
        count.controls++;
    }
}
void same_virtual(std::ostream& out,int p,CopyCounts& count) {
    Poly one(p,1),zero(p);auto g=pebbling_inputs(p);g.push_back(variable(p,6));
    int next=7;Block A=block(g,1,next);
    std::vector<int> sizes(next,p);for(int v=0;v<7;v++)sizes[v]=2;
    auto gamma=domains(p,sizes);int aa=int(gamma.size());
    gamma.insert(gamma.end(),A.axioms.begin(),A.axioms.end());
    int endA=-1;Proof unitA=product_unit(gamma,A,endA);
    auto ax=gamma;ax.insert(ax.end(),g.begin(),g.end());Proof unitB(p,ax);
    int sink=positive_sink(unitB,int(gamma.size()));
    int endB=unitB.lc(sink,unitB.ax(int(gamma.size())+7));
    std::string suffix="_F"+std::to_string(p);
    trace(out,unitA,"same_unit_genuine"+suffix,endA,one-A.product,4);
    trace(out,unitB,"same_unit_virtual"+suffix,endB,one,3);count.units+=2;
    for(const auto& line:unitB.lines) {
        need(line.value.old(7),"virtual unit not strictly earlier");
        if(line.rule=='a')need(line.a>=int(gamma.size()),"virtual unit uses retained ENS");
    }
    Proof dst(p,gamma);std::vector<int> ann;
    for(int i=0;i<8;i++)ann.push_back(dst.ax(aa+i));
    int final=copy_interface(dst,unitA,endA,unitB,endB,A.product,zero,
                            ann,std::vector<int>(8,-1),std::vector<int>(8,-1));
    trace(out,dst,"same_virtual_copy"+suffix,final,A.product,7);count.copies++;
    out<<"{\"record\":\"copy_case\",\"kind\":\"same_virtual\",\"p\":"<<p
       <<",\"value_degree\":4,\"virtual_unit_degree\":3,\"copy_degree\":"<<dst.degree
       <<",\"input_tuple\":";poly_vector(out,g);out<<"}\n";
    for(int mask=0;mask<128;mask++) {
        std::array<int,NV> point{};for(int v=0;v<7;v++)point[v]=(mask>>v)&1;
        bool found=false;
        for(int i=0;i<8;i++)if(evaluate(g[i],point)!=0){point[A.first+i]=1;found=true;break;}
        need(found,"pebbling tuple has a zero Boolean vector");
        models(gamma,point);need(evaluate(A.product,point)==0,"virtual copy common model");
        copy_point(out,"same_virtual_common_model",p,point,next,A.product,zero);count.common++;
    }
    for(int i=0;i<8;i++) {
        auto point=unit_point(i);model_except(gamma,point,aa+i);
        need(evaluate(A.product,point)==1,"virtual copy missing annihilator");
        copy_point(out,"missing_virtual_copy_annihilator",p,point,next,A.product,zero,aa+i);
        count.controls++;
    }
}
void high_cost_equality(std::ostream& out,int p,CopyCounts& count) {
    Poly one(p,1),zero(p),xN=variable(p,6),z=variable(p,7);
    auto positive=pebbling_inputs(p);
    int next=8;Block A=block({xN,z},1,next);
    std::vector<int> sizes(next,p);for(int v=0;v<8;v++)sizes[v]=2;
    auto gamma=domains(p,sizes);int pos=int(gamma.size());
    gamma.insert(gamma.end(),positive.begin(),positive.end());
    int aa=int(gamma.size());gamma.insert(gamma.end(),A.axioms.begin(),A.axioms.end());
    Proof equality(p,gamma);int q=positive_sink(equality,pos);
    int eq=equality.lc(q,-1,-1,0);
    std::string suffix="_F"+std::to_string(p);
    trace(out,equality,"derived_linear_equality"+suffix,eq,xN-one,3);count.equalities++;
    for(const auto& line:equality.lines)need(line.value.old(7),"equality witness not old");
    int endA=-1;Proof unitA=product_unit(gamma,A,endA);
    auto bx=gamma;bx.push_back(one);bx.push_back(z);Proof unitB(p,bx);
    int endB=unitB.ax(int(gamma.size()));
    trace(out,unitA,"reuse_unit_genuine"+suffix,endA,one-A.product,2);
    trace(out,unitB,"reuse_unit_virtual"+suffix,endB,one,0);count.units+=2;
    Proof dst(p,gamma);std::vector<int> map;
    for(size_t i=0;i<gamma.size();i++)map.push_back(int(i));
    int difference=import_proof(equality,eq,dst,map);
    int final=copy_interface(dst,unitA,endA,unitB,endB,A.product,zero,
                            {dst.ax(aa),dst.ax(aa+1)},{-1,-1},{difference,-1});
    trace(out,dst,"reuse_virtual_copy"+suffix,final,A.product,3);count.copies++;
    out<<"{\"record\":\"copy_case\",\"kind\":\"reused_linear_equality\",\"p\":"<<p
       <<",\"equality_degree\":3,\"equality_polynomial_degree\":1,\"value_degree\":2,"
         "\"copy_degree\":"<<dst.degree<<",\"inputs_A\":";
    poly_vector(out,A.inputs);out<<",\"inputs_B\":";poly_vector(out,{one,z});out<<"}\n";
    for(int bit=0;bit<2;bit++) {
        auto point=unit_point(7);point[7]=bit;point[A.first]=1;
        models(gamma,point);need(evaluate(A.product,point)==0,"reused equality common model");
        copy_point(out,"reuse_common_model",p,point,next,A.product,zero);count.common++;
    }
    for(int v=0;v<7;v++) {
        auto point=unit_point(v);model_except(gamma,point,pos+v);
        need(evaluate(A.product,point)==1,"missing equality dependency");
        copy_point(out,"missing_equality_dependency",p,point,next,A.product,zero,pos+v);count.controls++;
    }
    auto point=unit_point(7);model_except(gamma,point,aa);
    need(evaluate(A.product,point)==1,"missing reused-equality annihilator");
    copy_point(out,"missing_reuse_annihilator",p,point,next,A.product,zero,aa);count.controls++;
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","usage: check_virtual_copy_interface --out PATH");
        std::filesystem::path path(argv[2]);need(!std::filesystem::exists(path),"refuse to overwrite output");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot open output");
        out<<"{\"record\":\"metadata\",\"schema\":1,\"arithmetic\":\"exact Fp ordinary polynomials\","
             "\"monomial_encoding\":\"[coefficient,[[variable,exponent],...]]\","
             "\"zero_polynomial\":[],\"proof_zero_line\":-1,\"randomness\":\"none\","
             "\"scope\":\"local copy interfaces and exact final-line reuse\"}\n";
        CopyCounts count;
        for(int p:{2,3,5}){different_genuine(out,p,count);same_virtual(out,p,count);high_cost_equality(out,p,count);}
        need(count.units==18 && count.equalities==3 && count.copies==9
             && count.common==402 && count.controls==63,"summary counts");
        out<<"{\"record\":\"summary\",\"status\":\"passed\",\"conditional_unit_traces\":"<<count.units
           <<",\"input_equality_traces\":"<<count.equalities<<",\"copy_traces\":"<<count.copies
           <<",\"common_models\":"<<count.common<<",\"missing_witness_controls\":"<<count.controls<<"}\n";
        out.close();need(bool(out),"output write failed");
        std::cout<<"PASS: 18 conditional units, 3 input-equality proofs, 9 copy proofs, "
                   "402 common models, 63 missing-witness controls.\n";
        return 0;
    } catch(const std::exception& error) {std::cerr<<"FAIL: "<<error.what()<<'\n';return 1;}
}
