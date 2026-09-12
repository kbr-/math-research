// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Reuse the previous checker's exact formatting and verification helpers.
// Its main and its research suites are not called by this program.
#define main small_probe_unused_main
#include "check_small_probe_normalizers.cpp"
#undef main

struct InterfaceCounts {int units=0,relations=0,common=0,controls=0;};
Proof product_unit(const std::vector<Poly>& gamma,const Block& U,int& final) {
    auto axioms=gamma;axioms.insert(axioms.end(),U.inputs.begin(),U.inputs.end());
    Proof result(U.product.p,axioms);final=-1;
    for(size_t i=0;i<U.inputs.size();i++)
        final=result.lc(final,result.mul(result.ax(int(gamma.size()+i)),U.coef[i]));
    need(result.val(final)==Poly(U.product.p,1)-U.product,"product unit interface");
    return result;
}
int weighted_unit(const Proof& src,int final,Proof& dst,const Poly& weight,
                  const std::vector<int>& products) {
    int base=int(dst.axioms.size());
    need(src.axioms.size()==dst.axioms.size()+products.size(),"interface axiom count");
    for(int i=0;i<base;i++)need(src.axioms[i]==dst.axioms[i],"changed retained system");
    for(size_t i=0;i<products.size();i++)
        need(dst.val(products[i])==weight*src.axioms[base+i],"weighted input mismatch");
    std::vector<int> mapped;
    for(const auto& line:src.lines) {
        int id=-1;
        if(line.rule=='a')id=line.a<base
            ?dst.mul(dst.ax(line.a),weight):products.at(line.a-base);
        else if(line.rule=='l')
            id=dst.lc(line.a<0?-1:mapped.at(line.a),line.b<0?-1:mapped.at(line.b),
                      line.ca,line.cb);
        else id=dst.mv(line.a<0?-1:mapped.at(line.a),line.v);
        need(dst.val(id)==weight*line.value,"weighted interface replay");
        mapped.push_back(id);
    }
    return final<0?-1:mapped.at(final);
}
void model_record(std::ostream& out,const std::string& kind,int p,
                  const std::array<int,NV>& point,int variables,
                  const Poly& a,const Poly& b,const Poly& c,int omitted=-1) {
    out<<"{\"record\":\""<<kind<<"\",\"p\":"<<p<<",\"point\":";
    point_json(out,point,variables);
    out<<",\"a\":"<<evaluate(a,point)<<",\"b\":"<<evaluate(b,point)
       <<",\"c\":"<<evaluate(c,point)<<",\"c_minus_ab\":"<<evaluate(c-a*b,point)
       <<",\"omitted_axiom\":"<<omitted<<"}\n";
}
void model_except(const std::vector<Poly>& gamma,const std::array<int,NV>& point,int omitted) {
    for(size_t i=0;i<gamma.size();i++)
        if(int(i)!=omitted)need(evaluate(gamma[i],point)==0,"countermodel violates retained axiom");
    need(evaluate(gamma.at(omitted),point)!=0,"omitted axiom was not violated");
}

void genuine_case(std::ostream& out,int p,InterfaceCounts& count) {
    Poly one(p,1),x=variable(p,0),y=variable(p,1);
    int next=2;Block A=block({x},1,next),B=block({y},1,next),C=block({x,y},1,next);
    std::vector<int> sizes(next,p);sizes[0]=sizes[1]=2;
    auto gamma=domains(p,sizes);
    int axA=int(gamma.size());gamma.push_back(A.axioms[0]);
    int axB=int(gamma.size());gamma.push_back(B.axioms[0]);
    int axC=int(gamma.size());gamma.insert(gamma.end(),C.axioms.begin(),C.axioms.end());
    int endA=-1,endB=-1,endC=-1;
    Proof unitA=product_unit(gamma,A,endA),unitB=product_unit(gamma,B,endB),
          unitC=product_unit(gamma,C,endC);
    std::string suffix="_F"+std::to_string(p);
    trace(out,unitA,"genuine_unit_A"+suffix,endA,one-A.product,2);
    trace(out,unitB,"genuine_unit_B"+suffix,endB,one-B.product,2);
    trace(out,unitC,"genuine_unit_C"+suffix,endC,one-C.product,2);count.units+=3;

    Proof joined(p,gamma);
    int left=weighted_unit(unitA,endA,joined,C.product,{joined.ax(axC)});
    int right=weighted_unit(unitB,endB,joined,C.product,{joined.ax(axC+1)});
    right=joined.mul(right,A.product);
    int fromA=joined.mul(joined.ax(axA),B.product);
    int fromB=joined.mul(joined.ax(axB),A.product);
    int parent=weighted_unit(unitC,endC,joined,A.product*B.product,{fromA,fromB});
    int final=joined.lc(joined.lc(left,right),parent,1,-1);
    trace(out,joined,"genuine_OR_relation"+suffix,final,C.product-A.product*B.product,6);
    count.relations++;
    out<<"{\"record\":\"genuine_case\",\"p\":"<<p<<",\"degree\":"<<joined.degree
       <<",\"values\":";poly_vector(out,{A.product,B.product,C.product});out<<"}\n";
    for(int mask=0;mask<4;mask++) {
        std::array<int,NV> point{};point[0]=mask&1;point[1]=(mask>>1)&1;
        point[A.first]=point[0];point[B.first]=point[1];
        point[C.first]=point[0];point[C.first+1]=point[0]?0:point[1];
        models(gamma,point);need(evaluate(joined.val(final),point)==0,"genuine model relation");
        model_record(out,"genuine_common_model",p,point,next,A.product,B.product,C.product);
        count.common++;
    }
    for(int j=0;j<2;j++) {
        std::array<int,NV> point{};point[j]=1;
        point[A.first]=point[0];point[B.first]=point[1];
        model_except(gamma,point,axC+j);
        need(evaluate(joined.val(final),point)==1,"parent annihilator control");
        model_record(out,"missing_parent_annihilator",p,point,next,
                     A.product,B.product,C.product,axC+j);count.controls++;
    }
}

void virtual_pebbling_case(std::ostream& out,int p,InterfaceCounts& count) {
    Poly one(p,1),zero(p);
    std::vector<Poly> x,b,g;
    for(int v=0;v<7;v++){x.push_back(variable(p,v));b.push_back(one-x.back());}
    const std::array<std::array<int,2>,3> pred={{{0,1},{2,3},{4,5}}};
    for(int v=0;v<7;v++)g.push_back(v<4?b[v]:b[v]*x[pred[v-4][0]]*x[pred[v-4][1]]);
    int next=7;Block A=block(g,1,next),B=block({x[6]},1,next);
    std::vector<int> sizes(next,p);for(int v=0;v<7;v++)sizes[v]=2;
    auto gamma=domains(p,sizes);int axA=int(gamma.size());
    gamma.insert(gamma.end(),A.axioms.begin(),A.axioms.end());
    int axB=int(gamma.size());gamma.push_back(B.axioms[0]);
    auto tuple=g;tuple.push_back(x[6]);
    auto source_ax=gamma;source_ax.insert(source_ax.end(),tuple.begin(),tuple.end());
    Proof unit(p,source_ax);std::vector<int> known;
    for(int v=0;v<7;v++) {
        int id=unit.ax(int(gamma.size())+v);
        if(v>=4) {
            auto [a,c]=pred[v-4];
            id=unit.lc(id,unit.mul(known.at(a),b[v]));
            id=unit.lc(id,unit.mul(known.at(c),b[v]*x[a]));
        }
        need(unit.val(id)==b[v],"pebbling unit derivation");known.push_back(id);
    }
    int unit_final=unit.lc(known.back(),unit.ax(int(gamma.size())+7));
    std::string suffix="_F"+std::to_string(p);
    trace(out,unit,"virtual_parent_unit"+suffix,unit_final,one,3);count.units++;
    for(const auto& line:unit.lines) {
        need(line.value.old(7),"unit witness has non-earlier coefficient support");
        if(line.rule=='a')need(line.a>=int(gamma.size()),"unit witness uses a retained ENS axiom");
    }
    Proof joined(p,gamma);std::vector<int> products;
    for(int v=0;v<7;v++)products.push_back(joined.mul(joined.ax(axA+v),B.product));
    products.push_back(joined.mul(joined.ax(axB),A.product));
    int ab=weighted_unit(unit,unit_final,joined,A.product*B.product,products);
    int final=joined.lc(ab,-1,-1,0);
    trace(out,joined,"virtual_OR_relation"+suffix,final,zero-A.product*B.product,9);
    count.relations++;
    out<<"{\"record\":\"virtual_case\",\"p\":"<<p<<",\"degree\":"<<joined.degree
       <<",\"unit_degree\":"<<unit.degree<<",\"unit_witness_old_variables\":7,"
         "\"input_tuple\":";poly_vector(out,tuple);out<<",\"values\":";
    poly_vector(out,{A.product,B.product,zero});out<<"}\n";
    for(int mask=0;mask<128;mask++) {
        std::array<int,NV> point{};for(int v=0;v<7;v++)point[v]=(mask>>v)&1;
        for(int v=0;v<7;v++)if(evaluate(g[v],point)!=0){point[A.first+v]=1;break;}
        point[B.first]=point[6];
        models(gamma,point);need(evaluate(joined.val(final),point)==0,"virtual model relation");
        model_record(out,"virtual_common_model",p,point,next,A.product,B.product,zero);
        count.common++;
    }
    for(int omitted=0;omitted<8;omitted++) {
        std::array<int,NV> point{};for(int v=0;v<7;v++)point[v]=1;
        if(omitted<7) {
            point[omitted]=0;
            for(int v=std::max(4,omitted+1);v<7;v++)
                point[v]=point[pred[v-4][0]]*point[pred[v-4][1]];
        }
        int ax=omitted<7?axA+omitted:axB;
        model_except(gamma,point,ax);
        need(evaluate(A.product*B.product,point)==1,"child annihilator control");
        model_record(out,"missing_child_annihilator",p,point,next,
                     A.product,B.product,zero,ax);count.controls++;
    }
}

void missing_unit(std::ostream& out,int p,InterfaceCounts& count) {
    Poly x=variable(p,0),y=variable(p,1),zero(p);
    int next=2;Block A=block({x},1,next),B=block({y},1,next);
    std::vector<int> sizes={2,2,p,p};auto gamma=domains(p,sizes);
    gamma.push_back(A.axioms[0]);gamma.push_back(B.axioms[0]);
    std::array<int,NV> point{};models(gamma,point);
    need(evaluate(x,point)==0 && evaluate(y,point)==0
         && evaluate(A.product*B.product,point)==1,"missing-unit control");
    model_record(out,"missing_virtual_unit_witness",p,point,next,A.product,B.product,zero);
    count.controls++;
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","usage: check_virtual_or_interface --out PATH");
        std::filesystem::path path(argv[2]);need(!std::filesystem::exists(path),"refuse to overwrite output");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot open output");
        out<<"{\"record\":\"metadata\",\"schema\":1,\"arithmetic\":\"exact Fp ordinary polynomials\","
             "\"monomial_encoding\":\"[coefficient,[[variable,exponent],...]]\","
             "\"zero_polynomial\":[],\"proof_zero_line\":-1,\"randomness\":\"none\","
             "\"scope\":\"local unit/annihilator OR interfaces, no global source simulation\"}\n";
        InterfaceCounts count;
        for(int p:{2,3,5}){genuine_case(out,p,count);virtual_pebbling_case(out,p,count);missing_unit(out,p,count);}
        need(count.units==12 && count.relations==6 && count.common==396 && count.controls==33,
             "summary counts");
        out<<"{\"record\":\"summary\",\"status\":\"passed\",\"conditional_PC_traces\":"<<count.units
           <<",\"OR_relation_PC_traces\":"<<count.relations<<",\"common_models\":"<<count.common
           <<",\"missing_witness_controls\":"<<count.controls<<"}\n";
        out.close();need(bool(out),"output write failed");
        std::cout<<"PASS: 12 conditional PC traces, 6 OR-relation PC traces, "
                   "396 common models, 33 missing-witness controls.\n";
        return 0;
    } catch(const std::exception& error) {std::cerr<<"FAIL: "<<error.what()<<'\n';return 1;}
}
