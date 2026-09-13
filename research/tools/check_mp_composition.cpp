// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact ordinary-polynomial checks of the notebook's local MP identities.
// Compile with: c++ -std=c++17 -O2 -o research/tmp/check_mp_composition FILE
// Run through compute.sh with --out PATH. Fixed cases; no random seed.
#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
#include "binary_php.hpp"

constexpr int NV = 64;
using Mon = std::array<unsigned char, NV>;
struct Poly {
    int p;
    std::map<Mon, int> t;
    explicit Poly(int prime, int c = 0): p(prime) {
        c = (c % p + p) % p;
        if (c) t[Mon{}] = c;
    }
    void addterm(const Mon& m, int c) {
        c = (c % p + p) % p;
        if (!c) return;
        auto it = t.find(m);
        if (it == t.end()) t.emplace(m,c);
        else if ((it->second = (it->second+c)%p) == 0) t.erase(it);
        if (t.size() > 500000) throw std::runtime_error("polynomial term guard exceeded");
    }
    int degree() const {
        int d = -1;
        for (const auto& [m,c]: t) {
            int e = 0;
            for (auto x: m) e += x;
            d = std::max(d,e);
        }
        return d;
    }
};
Poly var(int p, int i) {
    if (i < 0 || i >= NV) throw std::runtime_error("variable guard exceeded");
    Poly a(p); Mon m{}; m[i]=1; a.t[m]=1; return a;
}
Poly operator+(const Poly& a, const Poly& b) {
    if (a.p!=b.p) throw std::runtime_error("mixed fields");
    Poly r=a; for (const auto& [m,c]: b.t) r.addterm(m,c); return r;
}
Poly operator-(const Poly& a, const Poly& b) {
    if (a.p!=b.p) throw std::runtime_error("mixed fields");
    Poly r=a; for (const auto& [m,c]: b.t) r.addterm(m,-c); return r;
}
Poly operator*(const Poly& a, const Poly& b) {
    if (a.p!=b.p) throw std::runtime_error("mixed fields");
    Poly r(a.p);
    for (const auto& [m,c]: a.t) for (const auto& [n,d]: b.t) {
        Mon v{};
        for (int i=0;i<NV;i++) {
            int e=int(m[i])+int(n[i]);
            if (e>255) throw std::runtime_error("exponent guard exceeded");
            v[i]=static_cast<unsigned char>(e);
        }
        // p <= 5 in this suite; multiplication and addition cannot overflow int.
        r.addterm(v,c*d);
    }
    return r;
}
Poly power(Poly a, int n) {
    Poly r(a.p,1); while(n--) r=r*a; return r;
}
Poly zero_after(const Poly& a, int first) {
    Poly r(a.p);
    for (const auto& [m,c]: a.t) {
        bool keep=true;
        for(int i=first;i<NV;i++) if(m[i]) {keep=false;break;}
        if(keep) r.addterm(m,c);
    }
    return r;
}
void require(bool yes, const std::string& msg) {
    if (!yes) throw std::runtime_error(msg);
}
struct Block {
    Poly A;
    std::vector<Poly> U, E;
};
Block block(const std::vector<Poly>& inputs, int h, int& nextvar) {
    int p=inputs.at(0).p; Poly one(p,1), prefix=one;
    std::vector<Poly> u(inputs.size(), Poly(p));
    for (int v=0;v<h;v++) {
        Poly linear(p);
        for (size_t i=0;i<inputs.size();i++) {
            Poly r=var(p,nextvar++);
            u[i]=u[i]+r*prefix;
            linear=linear+r*inputs[i];
        }
        prefix=prefix*(one-linear);
    }
    std::vector<Poly> e;
    Poly expansion(p);
    for(size_t i=0;i<inputs.size();i++) {
        e.push_back(inputs[i]*prefix);
        expansion=expansion+u[i]*inputs[i];
    }
    require((one-prefix-expansion).t.empty(),"telescoping identity");
    return {prefix,u,e};
}
// Explicit original-axiom representations, retaining individual summands.
struct Term { Poly cofactor, axiom; };
Poly value(const std::vector<Term>& rep, int p) {
    Poly total(p); for(const auto& t:rep) total=total+t.cofactor*t.axiom; return total;
}
int cost(const std::vector<Term>& rep) {
    int d=0; for(const auto& t:rep) d=std::max(d,(t.cofactor*t.axiom).degree()); return d;
}
Poly geometric(const Poly& x, int n) {
    Poly s(x.p), q(x.p,1); for(int i=0;i<n;i++){s=s+q;q=q*x;} return s;
}

void check_case(std::ostream& out, int p, int h, const std::string& kind) {
    Poly one(p,1), x=var(p,0), y=var(p,1), z=var(p,2);
    Poly a=x+y*y, b(p);
    int nextvar=3;
    std::vector<Poly> g;
    std::vector<Term> H;
    Block B{Poly(p),{},{} };
    bool disj=kind.rfind("disjunction_",0)==0;
    int subdegree=2;
    if(disj) {
        g= kind=="disjunction_affine" ? std::vector<Poly>{one-x,one-y}
                                     : std::vector<Poly>{one-x*y,x-y*y+z};
        B=block(g,h,nextvar); b=B.A;
    } else if(kind=="singleton_atom") {
        b=x; H.push_back({one,x*x-x}); g={one-b};
    } else if(kind=="singleton_neg_disjunction") {
        B=block({one-x,one-y},h,nextvar); b=one-B.A;
        for(size_t i=0;i<B.E.size();i++) H.push_back({Poly(p)-B.U[i],B.E[i]});
        subdegree=std::max(subdegree,B.A.degree()); g={one-b};
    } else if(kind=="singleton_mod_field") {
        // x is Boolean and z is an earlier field variable: different domains.
        Poly t=x+z; b=power(t,p-1); Poly multiplier=power(t,p-2);
        H.push_back({multiplier*geometric(x,p-1),x*x-x});
        H.push_back({multiplier,power(z,p)-z}); g={one-b};
    } else throw std::runtime_error("unknown case");
    std::vector<Poly> inputs{a}; inputs.insert(inputs.end(),g.begin(),g.end());
    Block U=block(inputs,h,nextvar);
    Poly q=b*U.U[0];
    std::vector<Term> W;
    if(disj) {
        for(size_t i=0;i<g.size();i++) {
            W.push_back({U.U[i+1],B.E[i]});
            W.push_back({Poly(p)-B.U[i],U.E[i+1]});
        }
    } else {
        require((value(H,p)-(b*b-b)).t.empty(),"Booleanity certificate");
        for(const auto& t:H) W.push_back({Poly(p)-U.U[1]*t.cofactor,t.axiom});
        W.push_back({Poly(p, -1),U.E[1]});
    }
    Poly rhs=U.A+q*a+value(W,p), residual=b-rhs;
    require(residual.t.empty(),"MP coefficient identity");
    // Omit a nonzero correction. This must fail in the ordinary ring even when
    // domain reduction would erase a Boolean axiom; quotient tests are not enough.
    Poly omitted=W.front().cofactor*W.front().axiom;
    require(!omitted.t.empty(),"vacuous negative control");
    require(!(b-(rhs-omitted)).t.empty(),"missing correction went undetected");
    int L=std::max({1,subdegree,a.degree(),b.degree(),U.A.degree()});
    for(const auto& f:g) L=std::max(L,f.degree());
    int w=L+1, mu=h*w, ns=(disj?2:3)*h*w, pc=2*h*w;
    require(q.degree()<=mu,"premise multiplier bound");
    require((q*a).degree()<=pc,"PC final-line product bound");
    require(cost(W)<=ns,"flattened local certificate bound");
    if(!disj) {
        require(cost(H)<=pc,"Booleanity derivation bound");
        require((U.U[1]*(b*b-b)).degree()<=pc,"PC Booleanity reuse bound");
        require(U.E[1].degree()<=pc,"implication companion degree");
    } else require(cost(W)<=pc,"disjunction PC local cost");
    out << "{\"case\":\"" << kind << "\",\"p\":"<<p<<",\"h\":"<<h
        <<",\"variables\":"<<nextvar<<",\"L\":"<<L
        <<",\"antecedent_degree\":"<<a.degree()<<",\"conclusion_degree\":"<<b.degree()
        <<",\"implication_degree\":"<<U.A.degree()<<",\"multiplier_degree\":"<<q.degree()
        <<",\"local_certificate_degree\":"<<cost(W)<<",\"ns_bound\":"<<ns
        <<",\"pc_bound\":"<<pc<<",\"identity_residual_terms\":"<<residual.t.size()
        <<",\"omitted_correction_residual_terms\":"<<omitted.t.size()<<"}\n";
}
Poly diagonal(const Poly& a,int first,const std::vector<int>& selected) {
    std::array<bool,NV> keep{};for(int i:selected)keep[i]=true;Poly result(a.p);
    for(const auto& [m,c]:a.t) {
        bool valid=true;
        for(int i=first;i<NV;i++)if((keep[i] && !m[i]) || (!keep[i] && m[i])){valid=false;break;}
        if(valid){Mon old=m;for(int i=first;i<NV;i++)old[i]=0;result.addterm(old,c);}
    }
    return result;
}
Poly old_boolean(const Poly& a) {
    Poly result(a.p);
    for(const auto& [m,c]:a.t){Mon reduced=m;for(auto& e:reduced)e=e?1:0;result.addterm(reduced,c);}
    return result;
}
void polynomial(std::ostream& out,const std::string& name,const Poly& a) {
    out<<"{\"type\":\"polynomial\",\"name\":\""<<name<<"\",\"degree\":"<<a.degree()<<",\"terms\":[";
    bool first=true;
    for(const auto& [m,c]:a.t) {
        if(!first)out<<',';
        first=false;out<<'['<<c<<",[";bool coordinate=true;
        for(int j=0;j<NV;j++)if(m[j]){if(!coordinate)out<<',';coordinate=false;out<<'['<<j<<','<<int(m[j])<<']';}
        out<<"]]";
    }
    out<<"]}\n";
}
void mixed_affine(std::ostream& out,int h,bool offset) {
    const int p=2,old=5;Poly one(p,1),a=var(p,0),z=var(p,3),w=var(p,4);
    std::vector<Poly> g{var(p,1),var(p,2)};
    if(offset){a=a+z;g={one+var(p,1)+z,var(p,2)+w};}
    int next=old,bstart=next;Block B=block(g,h,next);int ustart=next;
    std::vector<Poly> f{a};f.insert(f.end(),g.begin(),g.end());Block U=block(f,h,next);
    Poly q=B.A*U.U[0],correction(p);
    for(int i=0;i<2;i++)correction=correction+U.U[i+1]*B.E[i]-B.U[i]*U.E[i+1];
    require((B.A-U.A-q*a-correction).t.empty(),"mixed MP-A ordinary identity");
    require(q.degree()==4*h-1 && correction.degree()==4*h,"sharp local affine degrees");
    std::string tag=std::string(offset?"offset":"coordinate")+"_h"+std::to_string(h);
    out<<"{\"type\":\"mixed_case\",\"name\":\""<<tag<<"\",\"h\":"<<h<<",\"old_variables\":"<<old
       <<",\"B_start\":"<<bstart<<",\"U_start\":"<<ustart<<",\"B_arity\":2,\"U_arity\":3}\n";
    polynomial(out,tag+"/a",a);
    for(int i=0;i<2;i++)polynomial(out,tag+"/g"+std::to_string(i),g[i]);
    polynomial(out,tag+"/b",B.A);polynomial(out,tag+"/c",U.A);polynomial(out,tag+"/q",q);
    polynomial(out,tag+"/local_correction",correction);
    for(int i=0;i<2;i++) {
        polynomial(out,tag+"/V"+std::to_string(i),B.U[i]);
        polynomial(out,tag+"/E_B"+std::to_string(i),B.E[i]);
    }
    for(int i=0;i<3;i++) {
        polynomial(out,tag+"/U"+std::to_string(i),U.U[i]);
        polynomial(out,tag+"/E_U"+std::to_string(i),U.E[i]);
    }
    int checks=0,nonzero_omissions=0;
    for(int j=0;j<3;j++)for(int k=0;k<2;k++) {
        std::vector<int> us,bs;
        for(int v=0;v<h;v++){us.push_back(ustart+3*v+j);bs.push_back(bstart+2*v+k);}
        for(int i=0;i<3;i++) {
            Poly extracted=diagonal(U.U[i],old,us),expected=i==j?power(f[j],h-1):Poly(p);
            require((extracted-expected).t.empty(),"prefix U diagonal");++checks;
        }
        for(int i=0;i<2;i++) {
            Poly extracted=diagonal(B.U[i],old,bs),expected=i==k?power(g[k],h-1):Poly(p);
            require((extracted-expected).t.empty(),"prefix V diagonal");++checks;
        }
        std::vector<int> both=us;both.insert(both.end(),bs.begin(),bs.end());
        Poly local=diagonal(correction,old,both),antecedent=diagonal(q*a,old,both);
        Poly expected=j==0?power(a,h)*power(g[k],h):Poly(p);
        require((local-expected).t.empty() && (antecedent-expected).t.empty(),"mixed antecedent contribution");
        require(diagonal(B.A-U.A,old,both).t.empty(),"single-block target mixed coefficient");checks+=3;
        if(j==0){require(!local.t.empty(),"omitted-antecedent control vacuous");++nonzero_omissions;}
        Poly left(p);
        for(int i=0;i<2;i++)left=left+diagonal(U.U[i+1],old,us)*g[i];
        Poly right(p);
        for(int i=0;i<2;i++)right=right+diagonal(B.U[i],old,bs)*f[i+1];
        require((old_boolean(left)-(j?g[j-1]:Poly(p))).t.empty(),"left affine array reduction");
        require((old_boolean(right)-g[k]).t.empty(),"right affine array reduction");checks+=2;
        std::string suffix="/j"+std::to_string(j)+"_k"+std::to_string(k);
        polynomial(out,tag+suffix+"/mixed_local",local);
        polynomial(out,tag+suffix+"/mixed_antecedent",antecedent);
        polynomial(out,tag+suffix+"/array_left",left);
        polynomial(out,tag+suffix+"/array_right",right);
    }
    Poly F1=a+z*w,F2=z*w;
    require((F1+F2-a).t.empty(),"old antecedent certificate");
    require((q*F1+q*F2-q*a).t.empty(),"flattened antecedent identity");
    require((q*F1).degree()==4*h+1 && (q*F2).degree()==4*h+1,"flattened antecedent cost");
    polynomial(out,tag+"/old_F1",F1);polynomial(out,tag+"/old_F2",F2);
    polynomial(out,tag+"/q_F1",q*F1);polynomial(out,tag+"/q_F2",q*F2);
    int cstart=next;Block C=block({z},h,next);Poly triple=q*C.E[0];
    require(triple.degree()==6*h,"third-block term degree");
    std::vector<int> selected;
    for(int v=0;v<h;v++){selected.push_back(bstart+2*v);selected.push_back(ustart+3*v);selected.push_back(cstart+v);}
    Poly extracted=diagonal(triple,old,selected);
    require((extracted-power(g[0],h)*power(a,h-1)*power(z,h+1)).t.empty() && !extracted.t.empty(),
            "third-block complete-support control");
    polynomial(out,tag+"/third_companion",C.E[0]);polynomial(out,tag+"/q_third_companion",triple);
    polynomial(out,tag+"/triple_diagonal",extracted);
    out<<"{\"type\":\"mixed_result\",\"name\":\""<<tag<<"\",\"diagonal_checks\":"<<checks
       <<",\"nonzero_omission_controls\":"<<nonzero_omissions<<",\"q_degree\":"<<q.degree()
       <<",\"local_correction_degree\":"<<correction.degree()<<",\"flattened_degree_two_premise\":"<<4*h+1
       <<",\"third_companion_term_degree\":"<<triple.degree()<<",\"variables\":"<<next<<"}\n";
    std::cout<<tag<<": "<<checks<<" diagonal checks, "<<nonzero_omissions
             <<" antecedent-omission controls; local "<<4*h<<", flattened premise "<<4*h+1
             <<", third companion "<<6*h<<".\n";
}
void domain_booleanity(std::ostream& out,const std::string& tag,const Poly& value_poly) {
    Poly target=value_poly*value_poly-value_poly,pending=target;
    std::vector<Poly> coefficients(NV,Poly(2));int steps=0;
    while(!pending.t.empty()) {
        auto it=std::prev(pending.t.end());Mon mon=it->first;int coefficient=it->second;
        pending.t.erase(it);int variable=-1;
        for(int j=0;j<NV;j++)if(mon[j]>=2){variable=j;break;}
        require(variable>=0,"nonzero Boolean normal-form remainder");
        Mon quotient=mon;quotient[variable]-=2;coefficients[variable].addterm(quotient,coefficient);
        --mon[variable];pending.addterm(mon,coefficient);++steps;
    }
    Poly check(2);int ceiling=0,used=0;
    for(int j=0;j<NV;j++)if(!coefficients[j].t.empty()) {
        Poly x=var(2,j),term=coefficients[j]*(x*x-x);check=check+term;
        ceiling=std::max(ceiling,term.degree());++used;
        polynomial(out,tag+"/domain_cofactor_"+std::to_string(j),coefficients[j]);
    }
    require((check-target).t.empty() && ceiling<=2*value_poly.degree(),"field-only Booleanity certificate");
    polynomial(out,tag+"/Booleanity_target",target);
    out<<"{\"type\":\"domain_certificate\",\"name\":\""<<tag<<"\",\"degree\":"<<ceiling
       <<",\"used_domain_axioms\":"<<used<<",\"reduction_steps\":"<<steps<<"}\n";
}
int at_point(const Poly& a,const std::array<bool,NV>& point) {
    int value=0;
    for(const auto& [m,c]:a.t) {
        bool nonzero=true;for(int j=0;j<NV;j++)if(m[j] && !point[j]){nonzero=false;break;}
        if(nonzero)value=(value+c)%a.p;
    }
    return value;
}
void proper_or_union(std::ostream& out,int h) {
    const int r=2*h+1,old=2*r;int next=old;
    std::vector<Poly> g,k,all;
    for(int i=0;i<r;i++){g.push_back(var(2,i));k.push_back(var(2,r+i));}
    all=g;all.insert(all.end(),k.begin(),k.end());
    int start1=next;Block B1=block(g,h,next);int start2=next;Block B2=block(k,h,next);
    int start0=next;Block B0=block(all,h,next);
    std::string tag="proper_union_h"+std::to_string(h);
    out<<"{\"type\":\"proper_union_case\",\"name\":\""<<tag<<"\",\"h\":"<<h
       <<",\"child_rank\":"<<r<<",\"union_rank\":"<<2*r<<",\"packing_threshold\":"<<2*h
       <<",\"old_variables\":"<<old<<",\"B1_start\":"<<start1<<",\"B2_start\":"<<start2
       <<",\"B0_start\":"<<start0<<",\"variables\":"<<next<<"}\n";
    polynomial(out,tag+"/P0",B0.A);polynomial(out,tag+"/P1",B1.A);polynomial(out,tag+"/P2",B2.A);
    std::vector<Poly> c0,c1,c2;
    for(int i=0;i<r;i++)c0.push_back(B1.U[i]);
    for(int i=0;i<r;i++)c0.push_back(B1.A*B2.U[i]);
    for(int i=0;i<r;i++){c1.push_back(Poly(2)-B2.A*B0.U[i]);c2.push_back(Poly(2)-B1.A*B0.U[r+i]);}
    Poly certificate(2);int ceiling=0;
    auto add=[&](const std::string& label,const Poly& cofactor,const Poly& axiom) {
        Poly term=cofactor*axiom;certificate=certificate+term;ceiling=std::max(ceiling,term.degree());
        polynomial(out,tag+"/"+label+"/cofactor",cofactor);polynomial(out,tag+"/"+label+"/axiom",axiom);
    };
    for(int i=0;i<2*r;i++)add("E0_"+std::to_string(i),c0[i],B0.E[i]);
    for(int i=0;i<r;i++){add("E1_"+std::to_string(i),c1[i],B1.E[i]);add("E2_"+std::to_string(i),c2[i],B2.E[i]);}
    Poly target=B0.A-B1.A*B2.A;
    require((certificate-target).t.empty() && ceiling==6*h,"proper OR union certificate");
    polynomial(out,tag+"/union_target",target);
    int checks=0;
    for(int i=0;i<r;i++) {
        Poly term=c1[i]*B1.E[i];require(c1[i].degree()==4*h-1,"two-foreign-block cofactor degree");
        for(int j=0;j<r;j++) {
            std::vector<int> foreign,three;
            for(int v=0;v<h;v++){foreign.push_back(start0+2*r*v+i);foreign.push_back(start2+r*v+j);}
            Poly coefficient=diagonal(c1[i],old,foreign);
            require((coefficient-power(g[i],h-1)*power(k[j],h)).t.empty() && !coefficient.t.empty(),
                    "proper union collected cofactor extraction");
            three=foreign;for(int v=0;v<h;v++)three.push_back(start1+r*v+i);
            Poly mixed=diagonal(term,old,three);
            require((mixed-power(g[i],2*h)*power(k[j],h)).t.empty() && !old_boolean(mixed).t.empty(),
                    "proper union three-block term extraction");
            polynomial(out,tag+"/i"+std::to_string(i)+"_j"+std::to_string(j)+"/foreign_cofactor",coefficient);
            polynomial(out,tag+"/i"+std::to_string(i)+"_j"+std::to_string(j)+"/triple_term",mixed);checks+=2;
        }
    }
    domain_booleanity(out,tag+"/P0",B0.A);domain_booleanity(out,tag+"/P1",B1.A);domain_booleanity(out,tag+"/P2",B2.A);
    std::array<bool,NV> point{};point[0]=true;point[start1]=true;
    require(at_point(target,point)==1,"field-only comparison countermodel");
    out<<"{\"type\":\"field_only_countermodel\",\"name\":\""<<tag<<"\",\"one_variables\":[0,"<<start1
       <<"],\"P0\":"<<at_point(B0.A,point)<<",\"P1\":"<<at_point(B1.A,point)
       <<",\"P2\":"<<at_point(B2.A,point)<<",\"union_difference\":1}\n";
    out<<"{\"type\":\"proper_union_result\",\"name\":\""<<tag<<"\",\"certificate_degree\":"<<ceiling
       <<",\"cofactor_degree\":"<<4*h-1<<",\"extraction_checks\":"<<checks
       <<",\"Booleanity_certificates\":3,\"all_child_ranks_above_packing\":true}\n";
    std::cout<<tag<<": ranks "<<r<<','<<r<<','<<2*r<<" exceed packing "<<2*h
             <<"; NS certificate "<<ceiling<<", "<<checks<<" support checks and three field-only Booleanity certificates.\n";
}
void proper_or_degree(std::ostream& out) {
    using binary_php::Word;using binary_php::Bits;using binary_php::Space;
    const int h=1,r=3,old=6,D=5;int next=old;
    std::vector<Poly> g,k,all;
    for(int i=0;i<r;i++){g.push_back(var(2,i));k.push_back(var(2,r+i));}
    all=g;all.insert(all.end(),k.begin(),k.end());
    Block B1=block(g,h,next),B2=block(k,h,next),B0=block(all,h,next);
    require(next==18,"degree-test variable budget");
    std::vector<Word> monomials{0};Word limit=Word(1)<<next;
    for(int d=1;d<=D;d++)for(Word mask=(Word(1)<<d)-1;mask<limit;) {
        monomials.push_back(mask);Word low=mask&(-mask),raised=mask+low;
        mask=raised+(((raised^mask)/low)>>2);
    }
    const int width=int(monomials.size());std::unordered_map<Word,int> position;
    for(int i=0;i<width;i++)position.emplace(monomials[i],i);
    out<<"{\"type\":\"degree_board\",\"variables\":"<<next<<",\"degree\":"<<D
       <<",\"original_companion_degree\":3,\"monomial_masks\":[";
    for(int i=0;i<width;i++){if(i)out<<',';out<<monomials[i];}out<<"]}\n";
    auto vector=[&](const Poly& p,Word q) {
        Bits value=binary_php::blank(width);
        for(const auto& [m,c]:p.t) {
            Word mask=q;for(int j=0;j<NV;j++)if(m[j]){require(j<next,"unexpected degree-test variable");mask|=Word(1)<<j;}
            require(c==1 && position.count(mask),"Boolean vector range");binary_php::flip(value,position.at(mask));
        }
        return value;
    };
    std::vector<Poly> axioms=B0.E;axioms.insert(axioms.end(),B1.E.begin(),B1.E.end());
    axioms.insert(axioms.end(),B2.E.begin(),B2.E.end());Space span(width);int generators=0;
    for(int f=0;f<int(axioms.size());f++) {
        require(axioms[f].degree()==3,"original companion degree changed");
        polynomial(out,"degree/E"+std::to_string(f),axioms[f]);
        for(Word q:monomials) {
            if(__builtin_popcountll(q)>D-3)break;
            std::vector<int> trace;int pivot=span.add(vector(axioms[f],q),&trace);++generators;
            out<<"{\"type\":\"degree_step\",\"axiom\":"<<f<<",\"cofactor_mask\":"<<q<<",\"trace\":[";
            for(size_t j=0;j<trace.size();j++){if(j)out<<',';out<<trace[j];}
            out<<"],\"pivot\":"<<pivot;
            if(pivot>=0){out<<",\"basis\":";binary_php::sparse_json(out,span.rows[pivot]);}
            out<<"}\n";
        }
    }
    Poly target_poly=B0.A-B1.A*B2.A;Bits target=vector(target_poly,0);
    std::vector<int> trace;Bits remainder=span.reduce(target,&trace);bool member=binary_php::zero(remainder);
    polynomial(out,"degree/target",target_poly);
    out<<"{\"type\":\"degree_target\",\"vector\":";binary_php::sparse_json(out,target);
    out<<",\"trace\":[";for(size_t j=0;j<trace.size();j++){if(j)out<<',';out<<trace[j];}
    out<<"],\"remainder\":";binary_php::sparse_json(out,remainder);
    if(!member) {
        Bits dual=span.separating_dual(target);
        require(!binary_php::bit(target,0),"zero-point target value");
        if(!binary_php::bit(dual,0))binary_php::flip(dual,0);
        for(const Bits& row:span.rows)if(!row.empty())require(!binary_php::dot(row,dual),"normalized dual lost annihilation");
        require(binary_php::dot(target,dual)==1,"dual target value");
        out<<",\"normalized_separating_dual\":";binary_php::sparse_json(out,dual);
    }
    out<<"}\n{\"type\":\"degree_result\",\"degree\":5,\"variables\":"<<next<<",\"columns\":"<<width
       <<",\"generator_multiples\":"<<generators<<",\"rank\":"<<span.rank
       <<",\"target_member\":"<<(member?"true":"false")<<",\"explicit_upper_degree\":6}\n";
    std::cout<<"Proper OR union: "<<generators<<" NS generator multiples, rank "<<span.rank<<'/'<<width
             <<"; degree-five target membership "<<(member?"true":"false")<<".\n";
}
int main(int argc,char** argv) {
    try {
        if(argc==2 && std::string(argv[1])=="--help") {
            std::cout<<"Exact fixed-case suite; usage: check_mp_composition --out PATH\n"; return 0;
        }
        bool mixed=argc==4 && std::string(argv[3])=="--mixed-affine";
        bool proper=argc==4 && std::string(argv[3])=="--proper-or-union";
        bool degree=argc==4 && std::string(argv[3])=="--proper-or-degree";
        if((argc!=3 && !mixed && !proper && !degree) || std::string(argv[1])!="--out")
            throw std::runtime_error("--out PATH [--mixed-affine|--proper-or-union|--proper-or-degree] required");
        if(mixed || proper || degree){std::ifstream existing(argv[2]);require(!existing.good(),"output exists");}
        std::ofstream out(argv[2]); require(bool(out),"cannot open output");
        if(degree) {
            out<<"{\"schema\":1,\"suite\":\"proper_OR_degree_five\",\"p\":2,"
                 "\"scope\":\"Exact NS axiom-multiple span after degree-complete Boolean reduction; no PC closure\"}\n";
            proper_or_degree(out);out.close();require(bool(out),"output write failed");return 0;
        }
        if(proper) {
            out<<"{\"schema\":1,\"suite\":\"proper_OR_union\",\"p\":2,\"seed\":null,"
                 "\"encoding\":\"terms are [coefficient,[[variable,ordinary exponent],...]]; field axiom j is x_j^2-x_j\","
                 "\"scope\":\"Actual source local comparison schema above packing rank, not a full PHP proof or minimum-degree result\"}\n";
            for(int h:{1,2})proper_or_union(out,h);
            out.close();require(bool(out),"output write failed");return 0;
        }
        if(mixed) {
            out<<"{\"schema\":1,\"suite\":\"MP_A_mixed_affine\",\"p\":2,\"seed\":null,"
                 "\"encoding\":\"terms are [coefficient,[[variable,ordinary exponent],...]]; zero has degree -1\","
                 "\"scope\":\"Local identities and supplied-term ledgers, not full source certificates or minimum NS degrees\"}\n";
            for(int h:{1,2,3})mixed_affine(out,h,false);
            for(int h:{1,2})mixed_affine(out,h,true);
            out.close();require(bool(out),"output write failed");return 0;
        }
        out<<"{\"schema\":1,\"suite\":\"mp_composition\",\"arithmetic\":\"exact sparse ordinary polynomials over F_p\",\"seed\":null,\"scope\":\"synthetic local identities, not PHP refutations or a global elimination check\"}\n";
        int count=0;
        for(int p:{2,3,5}) for(int h:{1,2,3})
            for(const std::string kind:{"disjunction_affine","disjunction_nonlinear","singleton_atom","singleton_neg_disjunction","singleton_mod_field"}) {
                if(h==3 && kind.rfind("singleton_",0)==0) continue;
                check_case(out,p,h,kind); ++count;
            }
        // Tiny Boolean-domain countermodel to blanket zero specialization.
        // a=b=x, h=1, c=1-r0*x-r1*(1-x). At r0=r1=0, R=x-1,
        // which is nonzero at the domain-satisfying assignment x=0.
        for(int p:{2,3,5}) {
            Poly one(p,1), x=var(p,0);
            int nextvar=1; Block U=block({x,one-x},1,nextvar);
            Poly localR=Poly(p)-U.U[1]*(x*x-x)-U.E[1];
            Poly R=zero_after(localR,1);
            require((zero_after(U.A,1)-one).t.empty(),"specialized implication");
            require(zero_after(x*U.U[0],1).t.empty(),"specialized multiplier");
            require((R-(x-one)).t.empty(),"specialized residual polynomial");
            require((x*x-x).t.count(Mon{})==0,"Boolean domain at x=0");
            require(R.t.at(Mon{})==p-1,"zero-specialization countermodel");
            out<<"{\"control\":\"blanket_zero_specialization\",\"p\":"<<p
               <<",\"x\":0,\"domain_axiom_value\":0,\"residual_value\":"<<p-1<<"}\n";
        }
        out<<"{\"summary\":{\"identity_cases\":"<<count<<",\"omission_controls\":"<<count
           <<",\"zero_specialization_controls\":3,\"all_passed\":true}}\n";
        out.close(); require(bool(out),"output write failed");
        std::cout<<count<<" exact identity/degree cases and "<<count
                 <<" omitted-correction controls passed; 3 zero-specialization countermodels checked.\n";
    } catch(const std::exception& e) { std::cerr<<e.what()<<"\n"; return 1; }
}
