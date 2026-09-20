// Exact original-degree NS controls for a supplied low-case quadratic branch map.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>
using M=uint64_t;
using P=std::set<M>;
constexpr int V=7;
void need(bool b,const char* s){if(!b)throw std::runtime_error(s);}
void toggle(P& p,M m){auto it=p.find(m);if(it==p.end())p.insert(m);else p.erase(it);}
P add(P a,const P& b){for(M m:b)toggle(a,m);return a;}
M monomial_product(M a,M b){
    M z=0;
    for(int i=0;i<V;++i){int e=int((a>>(4*i))&15)+int((b>>(4*i))&15);need(e<16,"exponent overflow");z|=M(e)<<(4*i);}
    return z;
}
P mul(const P& a,const P& b){P z;for(M x:a)for(M y:b)toggle(z,monomial_product(x,y));return z;}
P variable(int i){return {M(1)<<(4*i)};}
int degree(const P& p){int d=0;for(M m:p){int e=0;for(int i=0;i<V;++i)e+=int((m>>(4*i))&15);d=std::max(d,e);}return d;}
struct Cert {P remainder;std::array<P,V> cof;};
Cert divide(P p){
    Cert c;
    while(!p.empty()){
        M m=*p.rbegin();p.erase(m);int i=0;
        while(i<V && ((m>>(4*i))&15)<2)++i;
        if(i==V){toggle(c.remainder,m);continue;}
        M unit=M(1)<<(4*i);toggle(c.cof[i],m-2*unit);toggle(p,m-unit);
    }
    return c;
}
P reconstruct(const Cert& c){
    P p=c.remainder;
    for(int i=0;i<V;++i){P x=variable(i);p=add(p,mul(c.cof[i],add(mul(x,x),x)));}
    return p;
}
int ceiling(const Cert& c){int d=degree(c.remainder);for(const P& a:c.cof)if(!a.empty())d=std::max(d,degree(a)+2);return d;}
void polynomial(std::ostream& o,const P& p){o<<'[';bool first=true;for(M m:p){if(!first)o<<',';first=false;o<<m;}o<<']';}
void certificate(std::ostream& o,const Cert& c){
    o<<"{\"remainder\":";polynomial(o,c.remainder);o<<",\"boolean_cofactors\":[";
    for(int i=0;i<V;++i){if(i)o<<',';polynomial(o,c.cof[i]);}
    o<<"],\"actual_ceiling\":"<<ceiling(c)<<'}';
}
int main(int argc,char** argv)try {
    need(argc==3 && std::string(argv[1])=="--out","usage: check_weighted_quadratic_branch --out FILE");
    std::cout<<"Fixed workload: seven old variables, four source inputs, eight certificates and two omitted-component controls; no input-size parameter.\n";
    P one={0};std::array<P,V> x;for(int i=0;i<V;++i)x[i]=variable(i);
    P e=mul(x[5],x[6]), f=add(x[1],x[2]);std::array<P,4> g,beta;
    for(int i=0;i<4;++i)g[i]=add(mul(x[0],x[i+1]),e);
    beta[0]=add(add(one,x[0]),mul(x[0],f));beta[1]=x[0];
    P product=one;for(int i=0;i<4;++i)product=add(product,mul(beta[i],g[i]));
    std::ofstream out(argv[2]);need(bool(out),"cannot open output");
    out<<"{\"scope\":\"explicit binary low-case branch map over old Booleanity; no full PHP instance or general-dichotomy computation\",\"variables\":7,\"encoding\":\"monomial exponent of x_i is nibble i; coefficients are one in F2\",\"accuracy\":1,\"T\":2,\"weight_degree\":1,\"weight\":";polynomial(out,f);
    out<<",\"inputs\":[";for(int i=0;i<4;++i){if(i)out<<',';polynomial(out,g[i]);}
    out<<"],\"coefficient_images\":[";for(int i=0;i<4;++i){if(i)out<<',';polynomial(out,beta[i]);}
    out<<"],\"product_image\":";polynomial(out,product);out<<",\"certificates\":[";
    int count=0;
    for(int type=0;type<2;++type)for(int i=0;i<4;++i){
        P target=type==0?mul(f,mul(g[i],product)):mul(f,add(mul(beta[i],beta[i]),beta[i]));
        Cert c=divide(target);need(reconstruct(c)==target,"certificate identity failed");need(c.remainder.empty(),"accepted weighted image has nonzero remainder");
        int original=type==0?5:2, budget=2*original+1;need(ceiling(c)<=budget,"original-degree budget exceeded");
        if(count++)out<<',';
        out<<"{\"kind\":\""<<(type==0?"companion":"coefficient_booleanity")<<"\",\"input\":"<<i<<",\"original_degree\":"<<original<<",\"allowed_ceiling\":"<<budget<<",\"target\":";polynomial(out,target);out<<",\"certificate\":";certificate(out,c);out<<'}';
    }
    out<<"],\"controls\":[";
    for(int control=0;control<2;++control){
        auto wrong=beta;
        wrong[0]=control==0?add(one,x[0]):mul(x[0],f); // omit high-affine or low-exception contribution
        P badp=one;for(int i=0;i<4;++i)badp=add(badp,mul(wrong[i],g[i]));
        Cert c=divide(mul(f,mul(g[0],badp)));need(!c.remainder.empty(),"omitted-component control failed to detect violation");
        if(control)out<<',';
        out<<"{\"omitted\":\""<<(control==0?"affine_branch_term":"exceptional_low_branch_term")<<"\",\"first_companion_remainder\":";polynomial(out,c.remainder);out<<'}';
    }
    out<<"],\"all_eight_certificates_verified\":true,\"both_controls_detected\":true}\n";
    need(bool(out),"output write failed");
    std::cout<<"Eight exact NS certificates passed with original-degree budgets; both omitted-component controls have nonzero remainder.\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
