// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact PC traces for old-consequence elimination and implication-boundary replay.
// Fixed synthetic cases, not PHP proofs. Run through compute.sh with --out PATH.
#include <algorithm>
#include <array>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

constexpr int NV=16;
using Mon=std::array<unsigned char,NV>;
void need(bool ok,const std::string& msg) { if(!ok) throw std::runtime_error(msg); }
struct Poly {
    int p;
    std::map<Mon,int> terms;
    explicit Poly(int prime,int c=0):p(prime) { add(Mon{},c); }
    void add(const Mon& m,int c) {
        c=(c%p+p)%p; if(!c) return;
        auto it=terms.find(m);
        if(it==terms.end()) terms.emplace(m,c);
        else if((it->second=(it->second+c)%p)==0) terms.erase(it);
        need(terms.size()<=250000,"polynomial term guard");
    }
    int deg() const {
        int d=-1;
        for(const auto& term:terms) {
            int e=0; for(auto x:term.first) e+=x; d=std::max(d,e);
        }
        return d;
    }
    bool old(int first) const {
        for(const auto& term:terms) for(int i=first;i<NV;i++)
            if(term.first[i]) return false;
        return true;
    }
};
Poly variable(int p,int i) {
    need(i>=0 && i<NV,"variable guard"); Poly q(p); Mon m{};m[i]=1;q.add(m,1);return q;
}
Poly operator+(const Poly& a,const Poly& b) {
    need(a.p==b.p,"mixed fields"); Poly q=a;
    for(const auto& t:b.terms) q.add(t.first,t.second);
    return q;
}
Poly operator-(const Poly& a,const Poly& b) {
    need(a.p==b.p,"mixed fields"); Poly q=a;
    for(const auto& t:b.terms) q.add(t.first,-t.second);
    return q;
}
Poly operator*(const Poly& a,const Poly& b) {
    need(a.p==b.p,"mixed fields"); Poly q(a.p);
    for(const auto& u:a.terms) for(const auto& v:b.terms) {
        Mon m{};
        for(int i=0;i<NV;i++) {
            int e=int(u.first[i])+int(v.first[i]);need(e<=255,"exponent guard");
            m[i]=static_cast<unsigned char>(e);
        }
        // This suite uses only p <= 7, so coefficient products fit int.
        q.add(m,u.second*v.second);
    }
    return q;
}
bool operator==(const Poly& a,const Poly& b) {return a.p==b.p && a.terms==b.terms;}
Poly powp(Poly a,int e) {Poly q(a.p,1);while(e--)q=q*a;return q;}
int modpow(int a,int e,int p) {int q=1;while(e--)q=q*a%p;return q;}
Poly specialize(const Poly& a,int first,const std::array<int,NV>& beta) {
    Poly q(a.p);
    for(const auto& term:a.terms) {
        Mon m=term.first;int c=term.second;
        for(int i=first;i<NV;i++) {c=c*modpow(beta[i],m[i],a.p)%a.p;m[i]=0;}
        q.add(m,c);
    }
    return q;
}
void jsonpoly(std::ostream& out,const Poly& q) {
    out<<'[';bool comma=false;
    for(const auto& term:q.terms) {
        if(comma)out<<',';
        comma=true;out<<'['<<term.second<<",[";bool sep=false;
        for(int i=0;i<NV;i++) if(term.first[i]) {
            if(sep)out<<',';
            sep=true;out<<'['<<i<<','<<int(term.first[i])<<']';
        }
        out<<"]]";
    }
    out<<']';
}
struct Block { Poly product;std::vector<Poly> inputs,coef,axioms;int first,end; };
Block block(std::vector<Poly> inputs,int h,int& next) {
    int p=inputs.at(0).p,first=next;Poly one(p,1),product=one;
    std::vector<Poly> coef(inputs.size(),Poly(p));
    for(int v=0;v<h;v++) {
        Poly linear(p);
        for(size_t i=0;i<inputs.size();i++) {
            Poly r=variable(p,next++);coef[i]=coef[i]+r*product;linear=linear+r*inputs[i];
        }
        product=product*(one-linear);
    }
    std::vector<Poly> axioms;Poly sum(p);
    for(size_t i=0;i<inputs.size();i++) {axioms.push_back(inputs[i]*product);sum=sum+coef[i]*inputs[i];}
    need(sum==one-product,"block telescoping");
    return {product,inputs,coef,axioms,first,next};
}
// Lines are axiom introductions, two-term linear combinations, or multiplication
// by one variable. Index -1 denotes a zero contribution, never an extra axiom.
struct Line { Poly value;char rule;int a=-1,b=-1,ca=1,cb=1,v=-1; };
struct Proof {
    int p,degree=0;
    size_t stored_terms=0;
    std::vector<Poly> axioms;
    std::vector<Line> lines;
    explicit Proof(int prime,std::vector<Poly> ax):p(prime),axioms(std::move(ax)) {}
    Poly val(int i) const {return i<0?Poly(p):lines.at(i).value;}
    int append(Line line) {
        if(line.value.terms.empty())return -1;
        degree=std::max(degree,line.value.deg());stored_terms+=line.value.terms.size();
        need(lines.size()<250000 && stored_terms<=2000000,"proof storage guard");
        lines.push_back(std::move(line));return int(lines.size())-1;
    }
    int ax(int i) {return append({axioms.at(i),'a',i});}
    int lc(int a,int b,int ca=1,int cb=1) {
        return append({Poly(p,ca)*val(a)+Poly(p,cb)*val(b),'l',a,b,ca,cb});
    }
    int mv(int a,int v) {return append({val(a)*variable(p,v),'m',a,-1,1,1,v});}
    int mul(int a,const Poly& q) {
        int total=-1;
        for(const auto& term:q.terms) {
            int id=a;
            for(int v=0;v<NV;v++) for(int j=0;j<term.first[v];j++) id=mv(id,v);
            total=lc(total,id,1,term.second);
        }
        return total;
    }
    bool verify(int corrupt=-1) const {
        for(size_t i=0;i<lines.size();i++) {
            const auto& l=lines[i];Poly expected(p);
            if(l.rule=='a') {
                if(l.a<0 || size_t(l.a)>=axioms.size())return false;
                expected=axioms[l.a];
            } else {
                if(l.a>=int(i) || l.b>=int(i) || l.a< -1 || l.b< -1)return false;
                if(l.rule=='l')expected=Poly(p,l.ca)*val(l.a)+Poly(p,l.cb)*val(l.b);
                else if(l.rule=='m')expected=val(l.a)*variable(p,l.v);
                else return false;
            }
            Poly actual=l.value;
            if(int(i)==corrupt)actual=actual+Poly(p,1);
            if(!(actual==expected))return false;
        }
        return true;
    }
    void write(std::ostream& out,const std::string& name,int final) const {
        out<<"{\"record\":\"proof\",\"name\":\""<<name<<"\",\"axioms\":[";
        for(size_t i=0;i<axioms.size();i++){if(i)out<<',';jsonpoly(out,axioms[i]);}
        out<<"],\"final\":"<<final<<",\"degree\":"<<degree<<",\"lines\":"<<lines.size()<<"}\n";
        for(size_t i=0;i<lines.size();i++) {
            const auto& l=lines[i];
            out<<"{\"record\":\"line\",\"id\":"<<i<<",\"rule\":\""<<l.rule
               <<"\",\"a\":"<<l.a<<",\"b\":"<<l.b<<",\"ca\":"<<l.ca
               <<",\"cb\":"<<l.cb<<",\"variable\":"<<l.v<<",\"poly\":";
            jsonpoly(out,l.value);out<<"}\n";
        }
    }
};
std::vector<Poly> domains(int p,const std::vector<int>& sizes) {
    std::vector<Poly> ax;
    for(size_t i=0;i<sizes.size();i++) {
        Poly x=variable(p,int(i));ax.push_back(powp(x,sizes[i])-x);
    }
    return ax;
}
int field_proof(Proof& dst,const Poly& input,const std::vector<int>& sizes) {
    Poly remainder=input;
    std::vector<Poly> quot(sizes.size(),Poly(dst.p));
    while(true) {
        bool found=false;Mon m{};int coeff=0,v=0;
        for(const auto& term:remainder.terms) {
            for(size_t i=0;i<sizes.size();i++) if(term.first[i]>=sizes[i]) {
                m=term.first;coeff=term.second;v=int(i);found=true;break;
            }
            if(found)break;
        }
        if(!found)break;
        m[v]=static_cast<unsigned char>(m[v]-sizes[v]);
        Poly q(dst.p);q.add(m,coeff);quot[v]=quot[v]+q;
        remainder=remainder-q*dst.axioms.at(v);
    }
    need(remainder.terms.empty(),"nonzero domain remainder");
    int result=-1;
    for(size_t i=0;i<quot.size();i++) if(!quot[i].terms.empty())
        result=dst.lc(result,dst.mul(dst.ax(int(i)),quot[i]));
    need(dst.val(result)==input,"domain representation");return result;
}
// The source's first old_count axioms are identical to dst's old axioms;
// the following entries are this block's companions, then fresh field equations.
template<class ExtensionAxiom>
int replay(const Proof& src,int final,Proof& dst,int old_count,const Block& U,
           const Poly& weight,const std::array<int,NV>& beta,ExtensionAxiom extension) {
    need(weight.old(U.first),"weight contains removed variables");
    for(int i=0;i<old_count;i++) need(src.axioms[i].old(U.first),"old axiom is not fresh");
    std::vector<int> ids;
    for(const auto& line:src.lines) {
        int id=-1;
        if(line.rule=='a') {
            if(line.a<old_count)id=dst.mul(dst.ax(line.a),weight);
            else if(line.a<old_count+int(U.inputs.size()))id=extension(line.a-old_count);
            else need((weight*specialize(line.value,U.first,beta)).terms.empty(),"fresh field axiom survives");
        } else if(line.rule=='l') {
            int a=line.a<0?-1:ids.at(line.a),b=line.b<0?-1:ids.at(line.b);
            id=dst.lc(a,b,line.ca,line.cb);
        } else {
            int a=line.a<0?-1:ids.at(line.a);
            id=line.v<U.first?dst.mv(a,line.v):dst.lc(a,-1,beta[line.v],0);
        }
        need(dst.val(id)==weight*specialize(line.value,U.first,beta),"replayed line mismatch");
        ids.push_back(id);
    }
    return final<0?-1:ids.at(final);
}
int eliminate(const Proof& src,int final,Proof& dst,const Block& U,
              const std::vector<int>& sizes) {
    Poly target=src.val(final);need(target.old(U.first),"target contains removed variables");
    const int p=src.p,old_count=int(dst.axioms.size());
    std::vector<int> products;
    for(size_t j=0;j<U.inputs.size();j++) {
        int sum=-1;
        for(int alpha=1;alpha<p;alpha++) {
            std::array<int,NV> beta{};
            beta[U.first+int(j)]=modpow(alpha,p-2,p);
            Poly chi=Poly(p,1)-powp(U.inputs[j]-Poly(p,alpha),p-1);
            int id=replay(src,final,dst,old_count,U,chi,beta,[&](int i) {
                return field_proof(dst,chi*specialize(U.axioms[i],U.first,beta),sizes);
            });
            sum=dst.lc(sum,id,1,alpha);
        }
        need(dst.val(sum)==U.inputs[j]*target,"learned input-target product");
        products.push_back(sum);
    }
    std::array<int,NV> zero{};
    int square=replay(src,final,dst,old_count,U,target,zero,[&](int i){return products.at(i);});
    need(dst.val(square)==target*target,"squared target");
    int fpow=dst.mul(square,powp(target,p-2));
    int relation=field_proof(dst,powp(target,p)-target,sizes);
    int result=dst.lc(fpow,relation,1,-1);
    need(dst.val(result)==target,"eliminated target");return result;
}
std::vector<Poly> augmented(const std::vector<Poly>& old,const Block& U,int p) {
    auto ax=old;ax.insert(ax.end(),U.axioms.begin(),U.axioms.end());
    for(int i=U.first;i<U.end;i++){Poly r=variable(p,i);ax.push_back(powp(r,p)-r);}
    return ax;
}
void check_proof(Proof& proof,int final,const Poly& target,int bound,int old_variables) {
    need(proof.val(final)==target,"wrong conclusion");need(proof.degree<=bound,"degree ceiling");
    need(proof.verify(),"invalid proof trace");
    need(final>=0 && !proof.verify(final),"corrupted-line control");
    for(const auto& line:proof.lines)need(line.value.old(old_variables),"removed variable remains");
}
void old_case(std::ostream& out,int p,int h,const std::string& kind) {
    Poly x=variable(p,0),y=variable(p,1);
    Poly g=kind=="nonlinear_input"?x*y:x;
    std::vector<int> sizes{p,2};auto old=domains(p,sizes);old.push_back(g*g);
    int next=2;Block U=block({g},h,next);
    Proof src(p,augmented(old,U,p));
    int final=src.lc(src.ax(int(old.size())),src.mul(src.ax(2),U.coef[0]));
    if(kind=="larger_boundary")final=src.mul(final,y*y);
    Poly target=src.val(final);int d=src.degree,k=target.deg(),delta=g.deg();
    need(target==(kind=="larger_boundary"?g*y*y:g),"source consequence");
    need(src.verify(),"invalid source proof");
    Proof dst(p,old);int result=eliminate(src,final,dst,U,sizes);
    int bound=std::max({d+(p-1)*delta,d+k,p*k});
    check_proof(dst,result,target,bound,U.first);
    out<<"{\"record\":\"case\",\"family\":\"old_consequence\",\"kind\":\""<<kind
       <<"\",\"p\":"<<p<<",\"h\":"<<h<<",\"old_variables\":2,\"variables\":"<<next
       <<",\"domain_sizes\":["<<p<<",2],\"delta\":"<<delta<<",\"target_degree\":"<<k
       <<",\"source_degree\":"<<d<<",\"bound\":"<<bound<<",\"actual_degree\":"<<dst.degree<<"}\n";
    src.write(out,"source",final);dst.write(out,"eliminated",result);
    out<<"{\"record\":\"case_passed\",\"corrupted_trace_rejected\":true}\n";
}
void mp_case(std::ostream& out,int p,int h,bool disjunction) {
    Poly one(p,1),x=variable(p,0),y=variable(p,1),b=x;
    int next=2;Block B{Poly(p),{},{},{},2,2};
    if(disjunction){B=block({one-x,y},h,next);b=B.product;}
    int first=next;
    Block U=block(disjunction?std::vector<Poly>{x,one-x,y}:std::vector<Poly>{x,one-x},h,next);
    std::vector<int> sizes(first,p);sizes[0]=sizes[1]=2;
    auto old=domains(p,sizes);int a_index=int(old.size());old.push_back(x);
    int B_index=int(old.size());if(disjunction)old.insert(old.end(),B.axioms.begin(),B.axioms.end());
    auto ax=augmented(old,U,p);int E_index=int(old.size());
    Proof antecedent(p,ax);
    int a_final=antecedent.lc(antecedent.ax(E_index),antecedent.mul(antecedent.ax(a_index),one-U.product));
    need(antecedent.val(a_final)==x && antecedent.verify(),"antecedent source");
    Proof implication(p,ax);
    int c_final=implication.lc(implication.ax(E_index),implication.ax(E_index+1));
    need(implication.val(c_final)==U.product && implication.verify(),"implication source");
    Proof dst(p,old);int learned_a=eliminate(antecedent,a_final,dst,U,sizes);
    std::vector<int> annihilators{dst.mul(learned_a,b)};
    if(disjunction)for(size_t i=0;i<B.axioms.size();i++)annihilators.push_back(dst.ax(B_index+int(i)));
    else annihilators.push_back(field_proof(dst,b*(one-b),sizes));
    std::array<int,NV> zero{};
    int result=replay(implication,c_final,dst,int(old.size()),U,b,zero,[&](int i){return annihilators.at(i);});
    int H=disjunction?0:2;
    int bound=std::max({antecedent.degree+(p-1),implication.degree+b.deg(),H});
    check_proof(dst,result,b,bound,first);
    out<<"{\"record\":\"case\",\"family\":\"implication_boundary\",\"kind\":\""
       <<(disjunction?"disjunction":"atom")<<"\",\"p\":"<<p<<",\"h\":"<<h
       <<",\"old_variables\":"<<first<<",\"variables\":"<<next
       <<",\"antecedent_degree\":"<<antecedent.degree<<",\"implication_degree\":"<<implication.degree
       <<",\"boundary_degree\":"<<b.deg()<<",\"bound\":"<<bound<<",\"actual_degree\":"<<dst.degree
       <<",\"antecedent_uses_removed_block\":true,\"boundary_preserved\":true}\n";
    antecedent.write(out,"antecedent",a_final);implication.write(out,"implication",c_final);
    dst.write(out,"eliminated",result);
    out<<"{\"record\":\"case_passed\",\"corrupted_trace_rejected\":true}\n";
}
void controls(std::ostream& out,int p) {
    Poly one(p,1),x=variable(p,0);int next=1;
    Block U=block({x,one-x},1,next);
    // With only Boolean/domain axioms and U, c is derivable but x need not vanish.
    // x=1,r0=1,r1=0 satisfies the domains and companions, and c=0 while x=1.
    std::array<int,NV> point{};point[0]=1;point[1]=1;
    need(specialize(x*x-x,0,point).terms.empty(),"control domain");
    for(const auto& e:U.axioms)need(specialize(e,0,point).terms.empty(),"control companion");
    need(specialize(U.product,0,point).terms.empty() && specialize(x,0,point)==one,"missing antecedent witness");
    out<<"{\"record\":\"control\",\"kind\":\"missing_annihilator\",\"p\":"<<p
       <<",\"x\":1,\"r0\":1,\"r1\":0,\"c_value\":0,\"b_value\":1}\n";
    Block V=block({U.product},1,next);
    need(!V.axioms[0].old(U.first),"freshness control vacuous");
    // Keep the later block coefficient s while zeroing only r0,r1.
    Poly changed(p);
    for(const auto& term:V.axioms[0].terms) if(!term.first[1] && !term.first[2])changed.add(term.first,term.second);
    need(!(changed==V.axioms[0]),"later input dependency went undetected");
    out<<"{\"record\":\"control\",\"kind\":\"later_block_not_old\",\"p\":"<<p<<",\"before\":";
    jsonpoly(out,V.axioms[0]);out<<",\"after_zeroing_U\":";jsonpoly(out,changed);out<<"}\n";
}
int main(int argc,char** argv) {
    try {
        if(argc==2 && std::string(argv[1])=="--help") {
            std::cout<<"Usage: check_boundary_replay --out NEW_PATH\n";return 0;
        }
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists; choose a new path");
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"boundary_replay\",\"seed\":null,\"arithmetic\":\"exact sparse ordinary polynomials\",\"scope\":\"synthetic PC traces; not PHP or global elimination\"}\n";
        int cases=0;
        for(int p:{2,3,5,7}) {
            for(int h:{1,2}) {
                for(const std::string kind:{"affine_input","nonlinear_input","larger_boundary"}){old_case(out,p,h,kind);++cases;}
                for(bool disj:{false,true}){mp_case(out,p,h,disj);++cases;}
            }
            controls(out,p);
        }
        out<<"{\"record\":\"summary\",\"proof_cases\":"<<cases<<",\"corrupted_trace_controls\":"<<cases
           <<",\"hypothesis_controls\":8,\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failed");
        std::cout<<cases<<" exact PC transformations and corrupted-trace controls passed; 8 hypothesis controls checked.\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
