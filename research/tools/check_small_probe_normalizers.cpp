// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact PC extraction/replay and Boolean-cube controls for small linear probes.
#include "pc_boundary.hpp"
using namespace boundary_pc;

int evaluate(const Poly& f,const std::array<int,NV>& point) {
    int result=0;
    for(const auto& [mon,coefficient]:f.terms) {
        int value=coefficient;
        for(int v=0;v<NV;v++)value=value*modpow(point[v],mon[v],f.p)%f.p;
        result=(result+value)%f.p;
    }
    return result;
}
void point_json(std::ostream& out,const std::array<int,NV>& point,int n) {
    out<<'[';
    for(int i=0;i<n;i++){if(i)out<<',';out<<point[i];}
    out<<']';
}
void poly_vector(std::ostream& out,const std::vector<Poly>& items) {
    out<<'[';
    for(size_t i=0;i<items.size();i++){if(i)out<<',';jsonpoly(out,items[i]);}
    out<<']';
}
void models(const std::vector<Poly>& ax,const std::array<int,NV>& point) {
    for(const auto& f:ax)need(evaluate(f,point)==0,"purported model violates an axiom");
}
void trace(std::ostream& out,const Proof& proof,const std::string& name,
           int final,const Poly& target,int ceiling) {
    need(final>=0 && proof.val(final)==target,"wrong trace conclusion");
    need(proof.degree<=ceiling,"trace degree ceiling");
    need(proof.verify() && !proof.verify(final),"trace or corrupted-line control");
    proof.write(out,name,final);
}
int ns(std::ostream& out,const std::string& name,const std::vector<Poly>& ax,
       const std::vector<Poly>& cof,const Poly& target,int ceiling) {
    need(ax.size()==cof.size(),"NS array lengths");
    Poly sum(target.p);int degree=0;
    for(size_t i=0;i<ax.size();i++) {
        Poly term=ax[i]*cof[i];sum=sum+term;degree=std::max(degree,term.deg());
    }
    need(sum==target && degree<=ceiling,"NS identity or degree");
    out<<"{\"record\":\"ns_certificate\",\"name\":\""<<name<<"\",\"p\":"<<target.p
       <<",\"degree\":"<<degree<<",\"axioms\":";
    poly_vector(out,ax);out<<",\"cofactors\":";poly_vector(out,cof);
    out<<",\"target\":";jsonpoly(out,target);out<<"}\n";
    return degree;
}
int import_proof(const Proof& src,int final,Proof& dst,const std::vector<int>& axmap) {
    std::vector<int> lines;
    for(const auto& line:src.lines) {
        int id=-1;
        if(line.rule=='a')id=dst.ax(axmap.at(line.a));
        else if(line.rule=='l')
            id=dst.lc(line.a<0?-1:lines.at(line.a),line.b<0?-1:lines.at(line.b),
                      line.ca,line.cb);
        else id=dst.mv(line.a<0?-1:lines.at(line.a),line.v);
        need(dst.val(id)==line.value,"imported proof line");lines.push_back(id);
    }
    return final<0?-1:lines.at(final);
}
Poly affine_image(const Poly& f,const Block& U,const std::vector<Poly>& beta) {
    Poly image(f.p);
    for(const auto& [mon,coefficient]:f.terms) {
        Mon old=mon;
        for(int v=U.first;v<U.end;v++)old[v]=0;
        Poly term(f.p);term.add(old,coefficient);
        for(int v=U.first;v<U.end;v++)
            if(mon[v])term=term*powp(beta.at(v-U.first),mon[v]);
        image=image+term;
    }
    return image;
}
struct Counts {int traces=0,ns_certificates=0,common=0,missing_goal=0,cube=0,units=0;};

void positive_checks(std::ostream& out,Counts& counts) {
    const int p=3;
    Poly one(p,1),b=variable(p,0),x=variable(p,1),y=variable(p,2),w=variable(p,3);
    Poly f=x+y,J=one-f*f,H=(one-b)*J;
    std::vector<int> old_sizes(4,2);
    auto boolean=domains(p,old_sizes),retained=boolean;
    retained.push_back(H);
    auto unit_ax=retained;unit_ax.push_back(b);unit_ax.push_back(f);
    Proof unit(p,unit_ax);
    int unit_final=unit.lc(unit.lc(unit.ax(4),unit.ax(5)),
                           unit.mul(unit.ax(6),(one-b)*f));
    trace(out,unit,"probe_unit_refutation",unit_final,one,3);counts.traces++;

    Proof extracted(p,retained);
    int bH=extracted.mul(extracted.ax(0),Poly(p,-1)*J);
    Poly frobenius=powp(f,p)-f;
    int frob=field_proof(extracted,frobenius,old_sizes);
    int fH=extracted.mul(frob,Poly(p,-1)*(one-b));
    need(extracted.val(bH)==b*H && extracted.val(fH)==f*H,"weighted probes");
    std::vector<int> weighted;
    for(const auto& line:unit.lines) {
        int id=-1;
        if(line.rule=='a') {
            if(line.a==5)id=bH;
            else if(line.a==6)id=fH;
            else id=extracted.mul(extracted.ax(line.a),H);
        } else if(line.rule=='l')
            id=extracted.lc(line.a<0?-1:weighted.at(line.a),
                            line.b<0?-1:weighted.at(line.b),line.ca,line.cb);
        else id=extracted.mv(line.a<0?-1:weighted.at(line.a),line.v);
        need(extracted.val(id)==H*line.value,"weighted refutation replay");
        weighted.push_back(id);
    }
    int Hline=weighted.at(unit_final);
    trace(out,extracted,"extracted_normalizer",Hline,H,6);counts.traces++;
    std::vector<Poly> Hcof={J*J,(one-b)*f*(x+one),(one-b)*f*(y+one),Poly(p)};
    ns(out,"selector_product_Booleanity",boolean,Hcof,H*H-H,6);counts.ns_certificates++;
    std::vector<Poly> fcof={Poly(p),x+one,y+one,Poly(p)};
    ns(out,"affine_coefficient_field_image",boolean,fcof,frobenius,3);counts.ns_certificates++;
    out<<"{\"record\":\"probe_data\",\"p\":3,\"old_variables\":[\"b\",\"x\",\"y\",\"w\"],"
          "\"boolean_probes\":";
    poly_vector(out,{b});out<<",\"field_probes\":";poly_vector(out,{f});
    out<<",\"factor_count\":3,\"weight_degree\":3,\"input_rank\":4,\"goal\":";
    jsonpoly(out,H);out<<"}\n";

    for(bool affine:{false,true}) {
        const int h=affine?2:3;int next=4;
        Block U=block({b,x,y,w},h,next);
        std::vector<Poly> beta(4*h,Poly(p));
        beta[0]=one;
        if(affine) {beta[5]=f;beta[6]=f;}
        else {beta[5]=one;beta[6]=one;beta[9]=Poly(p,2);beta[10]=Poly(p,2);}
        auto phi=[&](const Poly& q){return affine_image(q,U,beta);};
        need(phi(U.product)==H,"constant/affine factor realization");
        for(const auto& q:beta)need(q.deg()<=int(affine),"coefficient degree");
        std::vector<int> sizes(next,p);for(int v=0;v<4;v++)sizes[v]=2;
        auto source_ax=domains(p,sizes);
        source_ax.insert(source_ax.end(),U.axioms.begin(),U.axioms.end());
        int goal_index=int(source_ax.size());source_ax.push_back(H);
        Proof source(p,source_ax);
        int source_H=import_proof(extracted,Hline,source,{0,1,2,3,goal_index});
        int Eb=source.ax(next),Ex=source.ax(next+1),Ey=source.ax(next+2);
        int source_P=source.lc(source.lc(source.mul(source_H,U.product),Eb),
                               source.mul(source.lc(Ex,Ey),(one-b)*f));
        need(source.val(source_P)==U.product,"source product identity");
        int selected_field=U.first+5;
        int final=source.lc(source_P,source.ax(selected_field));
        Poly target=U.product+source_ax[selected_field];
        std::string mode=affine?"affine_h2":"constant_h3";
        trace(out,source,mode+"_source",final,target,2*h+3);counts.traces++;

        Proof replayed(p,retained);
        int replay_H=import_proof(extracted,Hline,replayed,{0,1,2,3,4});
        std::vector<int> images;
        for(const auto& g:U.inputs)images.push_back(replayed.mul(replay_H,g));
        std::vector<int> replay_lines;
        int used_nonzero_fields=0;
        for(const auto& line:source.lines) {
            int id=-1;
            if(line.rule=='a') {
                if(line.a<4)id=replayed.ax(line.a);
                else if(line.a<next) {
                    Poly field_image=phi(line.value);
                    if(!field_image.terms.empty()) {
                        id=field_proof(replayed,field_image,old_sizes);
                        used_nonzero_fields++;
                    }
                } else if(line.a<next+4)id=images.at(line.a-next);
                else {need(line.a==goal_index,"unknown source axiom");id=replayed.ax(4);}
            } else if(line.rule=='l')
                id=replayed.lc(line.a<0?-1:replay_lines.at(line.a),
                               line.b<0?-1:replay_lines.at(line.b),line.ca,line.cb);
            else {
                int a=line.a<0?-1:replay_lines.at(line.a);
                id=line.v>=U.first && line.v<U.end
                    ?replayed.mul(a,beta.at(line.v-U.first)):replayed.mv(a,line.v);
            }
            need(replayed.val(id)==phi(line.value),"affine proof replay");
            replay_lines.push_back(id);
        }
        int replay_final=replay_lines.at(final);
        trace(out,replayed,mode+"_replayed",replay_final,phi(target),6);counts.traces++;
        for(const auto& line:replayed.lines)need(line.value.old(4),"removed coefficient survives");
        need(used_nonzero_fields==int(affine),"nonzero field-image use control");
        out<<"{\"record\":\"normalizer_case\",\"mode\":\""<<mode
           <<"\",\"accuracy\":"<<h<<",\"selected_range\":["<<U.first<<','<<U.end
           <<"],\"coefficient_images\":";
        poly_vector(out,beta);out<<",\"product\":";jsonpoly(out,U.product);
        out<<",\"product_image\":";jsonpoly(out,H);
        out<<",\"target_image\":";jsonpoly(out,phi(target));
        out<<",\"source_degree\":"<<source.degree<<",\"replayed_degree\":"<<replayed.degree
           <<",\"used_nonzero_field_images\":"<<used_nonzero_fields<<"}\n";
        int common=0;
        for(int mask=0;mask<16;mask++) {
            std::array<int,NV> point{};
            for(int v=0;v<4;v++)point[v]=(mask>>v)&1;
            for(int v=U.first;v<U.end;v++)point[v]=evaluate(beta[v-U.first],point);
            bool valid=evaluate(H,point)==0;
            if(valid) {
                models(source_ax,point);models(retained,point);
                need(evaluate(target,point)==0 && evaluate(phi(target),point)==0,"model target");
                common++;counts.common++;
            }
            out<<"{\"record\":\"old_Boolean_point\",\"mode\":\""<<mode
               <<"\",\"common_model\":"<<(valid?"true":"false")<<",\"point\":";
            point_json(out,point,next);out<<",\"H\":"<<evaluate(H,point)
               <<",\"companion_images\":";
            out<<'[';for(int j=0;j<4;j++){if(j)out<<',';out<<evaluate(U.inputs[j]*H,point);}out<<"]}\n";
        }
        need(common==14,"positive fixture common-model count");
        std::array<int,NV> counter{};counter[3]=1;
        models(boolean,counter);
        need(evaluate(H,counter)==1 && evaluate(w*H,counter)==1,"missing-goal countermodel");
        out<<"{\"record\":\"missing_goal_control\",\"mode\":\""<<mode<<"\",\"point\":";
        point_json(out,counter,4);out<<",\"H\":1,\"wH\":1}\n";counts.missing_goal++;
    }
}

void pebbling_checks(std::ostream& out,int p,Counts& counts) {
    Poly one(p,1);
    std::vector<Poly> x,b,g;
    for(int v=0;v<7;v++){x.push_back(variable(p,v));b.push_back(one-x.back());}
    const std::array<std::array<int,2>,3> predecessors={{{0,1},{2,3},{4,5}}};
    for(int v=0;v<7;v++)
        g.push_back(v<4?b[v]:b[v]*x[predecessors[v-4][0]]*x[predecessors[v-4][1]]);
    g.push_back(x[6]);
    auto boolean=domains(p,std::vector<int>(7,2)),axioms=boolean;
    axioms.insert(axioms.end(),g.begin(),g.end());
    Proof proof(p,axioms);std::vector<int> known;
    for(int v=0;v<7;v++) {
        int result=proof.ax(7+v);
        if(v>=4) {
            auto [a,c]=predecessors[v-4];
            result=proof.lc(result,proof.mul(known.at(a),b[v]));
            result=proof.lc(result,proof.mul(known.at(c),b[v]*x[a]));
        }
        need(proof.val(result)==b[v],"topological pebbling PC identity");known.push_back(result);
    }
    int final=proof.lc(known.back(),proof.ax(14));
    trace(out,proof,"pebbling_refutation_F"+std::to_string(p),final,one,3);counts.traces++;
    out<<"{\"record\":\"pebbling_case\",\"p\":"<<p<<",\"predecessors\":[[],[],[],[],[0,1],[2,3],[4,5]],"
          "\"cube_coordinates\":[0,1,2,3,7],\"independent_inputs\":8,\"probe_factor_lower_bound\":5,"
          "\"input_polynomials\":";
    poly_vector(out,g);out<<"}\n";
    for(int v=0;v<8;v++) {
        std::vector<Poly> factors;std::vector<int> variables;
        if(v==7){factors={x[6]};variables={6};}
        else {
            factors.push_back(b[v]);variables.push_back(v);
            if(v>=4)for(int pred:predecessors[v-4]){factors.push_back(x[pred]);variables.push_back(pred);}
        }
        std::vector<Poly> cof(7,Poly(p));
        for(size_t j=0;j<factors.size();j++) {
            Poly weight=one;
            for(size_t l=0;l<j;l++)weight=weight*factors[l];
            for(size_t l=j+1;l<factors.size();l++)weight=weight*powp(factors[l],2);
            cof[variables[j]]=cof[variables[j]]+weight;
        }
        ns(out,"pebbling_Booleanity_F"+std::to_string(p)+"_g"+std::to_string(v),
           boolean,cof,g[v]*g[v]-g[v],2*g[v].deg());counts.ns_certificates++;
    }
    for(int omitted=0;omitted<8;omitted++) {
        std::array<int,NV> point{};for(int v=0;v<7;v++)point[v]=1;
        if(omitted<7) {
            point[omitted]=0;
            for(int v=std::max(4,omitted+1);v<7;v++)
                point[v]=point[predecessors[v-4][0]]*point[predecessors[v-4][1]];
        }
        models(boolean,point);
        for(int j=0;j<8;j++)need(evaluate(g[j],point)==int(j==omitted),"unit violation vector");
        out<<"{\"record\":\"unit_violation\",\"p\":"<<p<<",\"omitted\":"<<omitted<<",\"point\":";
        point_json(out,point,7);out<<",\"violations\":[";
        for(int j=0;j<8;j++){if(j)out<<',';out<<evaluate(g[j],point);}out<<"]}\n";counts.units++;
    }
    for(int mask=1;mask<32;mask++) {
        std::array<int,NV> point{};
        for(int v=0;v<4;v++)point[v]=1-((mask>>v)&1);
        bool sink=(mask&16)!=0;
        for(int v=4;v<7;v++)
            point[v]=sink?1:point[predecessors[v-4][0]]*point[predecessors[v-4][1]];
        models(boolean,point);
        for(int j=0;j<8;j++) {
            int expected=j<4?((mask>>j)&1):(j==7?int(sink):0);
            need(evaluate(g[j],point)==expected,"antichain Boolean cube");
        }
        out<<"{\"record\":\"antichain_cube_point\",\"p\":"<<p<<",\"mask\":"<<mask<<",\"point\":";
        point_json(out,point,7);out<<",\"violations\":[";
        for(int j=0;j<8;j++){if(j)out<<',';out<<evaluate(g[j],point);}out<<"]}\n";counts.cube++;
        if(mask==3) {
            int sum=0;for(const auto& q:g)sum=(sum+evaluate(q,point))%p;
            need(sum!=1,"constant-span separating point");
            out<<"{\"record\":\"one_not_in_span_control\",\"p\":"<<p
               <<",\"forcing_unit_coefficients\":true,\"sum_of_inputs\":"<<sum
               <<",\"point\":";point_json(out,point,7);out<<"}\n";
        }
    }
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","usage: check_small_probe_normalizers --out PATH");
        std::filesystem::path path(argv[2]);
        need(!std::filesystem::exists(path),"refuse to overwrite output");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot open output");
        out<<"{\"record\":\"metadata\",\"schema\":1,\"arithmetic\":\"exact Fp ordinary polynomials\","
              "\"monomial_encoding\":\"[coefficient,[[variable,exponent],...]]\","
              "\"zero_polynomial\":[],\"proof_zero_line\":-1,\"randomness\":\"none\","
              "\"scope\":\"small-probe certificates and generic Boolean pebbling controls\"}\n";
        Counts counts;positive_checks(out,counts);
        for(int p:{2,3,5})pebbling_checks(out,p,counts);
        need(counts.traces==9 && counts.ns_certificates==26 && counts.common==28
             && counts.missing_goal==2 && counts.cube==93 && counts.units==24,"summary counts");
        out<<"{\"record\":\"summary\",\"status\":\"passed\",\"complete_PC_traces\":"<<counts.traces
           <<",\"NS_certificates\":"<<counts.ns_certificates<<",\"common_models\":"<<counts.common
           <<",\"missing_goal_controls\":"<<counts.missing_goal
           <<",\"antichain_cube_points\":"<<counts.cube<<",\"unit_violation_points\":"<<counts.units<<"}\n";
        out.close();need(bool(out),"output write failed");
        std::cout<<"PASS: 9 complete PC traces, 26 NS certificates, 28 common models, "
                   "2 missing-goal controls, 93 antichain cube points, 24 unit points.\n";
        return 0;
    } catch(const std::exception& error) {std::cerr<<"FAIL: "<<error.what()<<'\n';return 1;}
}
