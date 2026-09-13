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

constexpr int NV = 32;
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
int main(int argc,char** argv) {
    try {
        if(argc==2 && std::string(argv[1])=="--help") {
            std::cout<<"Exact fixed-case suite; usage: check_mp_composition --out PATH\n"; return 0;
        }
        bool mixed=argc==4 && std::string(argv[3])=="--mixed-affine";
        if((argc!=3 && !mixed) || std::string(argv[1])!="--out") throw std::runtime_error("--out PATH [--mixed-affine] required");
        if(mixed){std::ifstream existing(argv[2]);require(!existing.good(),"output exists");}
        std::ofstream out(argv[2]); require(bool(out),"cannot open output");
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
