// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Search exact rational two-factor covers, then certify them in prime fields.
#define STABLE_IDEAL_NORMALIZERS_NO_MAIN
#include "check_stable_ideal_normalizers.cpp"
#include <numeric>

struct Rat {
    long long n=0,d=1;
    Rat(long long numerator=0,long long denominator=1) {
        need(denominator!=0,"zero rational denominator");
        if(denominator<0){numerator=-numerator;denominator=-denominator;}
        long long g=std::gcd(numerator<0?-numerator:numerator,denominator);
        n=numerator/g;d=denominator/g;
        need((n<0?-n:n)<=1000000000LL && d<=1000000000LL,"rational arithmetic guard");
    }
    bool zero() const {return n==0;}
};
Rat operator+(const Rat& a,const Rat& b){return Rat(a.n*b.d+b.n*a.d,a.d*b.d);}
Rat operator-(const Rat& a,const Rat& b){return Rat(a.n*b.d-b.n*a.d,a.d*b.d);}
Rat operator*(const Rat& a,const Rat& b){return Rat(a.n*b.n,a.d*b.d);}
Rat operator/(const Rat& a,const Rat& b){return Rat(a.n*b.d,a.d*b.n);}
bool operator==(const Rat& a,const Rat& b){return a.n==b.n && a.d==b.d;}
using RatVec=std::vector<Rat>;
struct RatSolution {bool feasible;RatVec coefficients;int rank;};
RatSolution rational_solve(const std::vector<Dense>& matrix) {
    const int rows=int(matrix.size()),cols=21;
    std::vector<RatVec> a(rows,RatVec(cols+1));
    for(int i=0;i<rows;i++) {
        need(int(matrix[i].size())==cols,"feature width");
        for(int j=0;j<cols;j++)a[i][j]=Rat(matrix[i][j]);
        a[i][cols]=Rat(1);
    }
    int rank=0;std::vector<int> pivots;
    for(int c=0;c<cols && rank<rows;c++) {
        int pivot=rank;while(pivot<rows && a[pivot][c].zero())pivot++;
        if(pivot==rows)continue;
        std::swap(a[pivot],a[rank]);Rat divisor=a[rank][c];
        for(int j=c;j<=cols;j++)a[rank][j]=a[rank][j]/divisor;
        for(int i=0;i<rows;i++)if(i!=rank && !a[i][c].zero()) {
            Rat multiplier=a[i][c];
            for(int j=c;j<=cols;j++)a[i][j]=a[i][j]-multiplier*a[rank][j];
        }
        pivots.push_back(c);rank++;
    }
    for(int i=rank;i<rows;i++)if(!a[i][cols].zero())return {false,{},rank};
    RatVec result(cols);
    for(int i=0;i<rank;i++)result[pivots[i]]=a[i][cols];
    for(int i=0;i<rows;i++) {
        Rat sum;
        for(int j=0;j<cols;j++)sum=sum+Rat(matrix[i][j])*result[j];
        need(sum==Rat(1),"rational primal verification");
    }
    return {true,result,rank};
}
void ratvec_json(std::ostream& out,const RatVec& vector) {
    out<<'[';bool comma=false;
    for(size_t i=0;i<vector.size();i++)if(!vector[i].zero()) {
        if(comma)out<<',';
        comma=true;out<<'['<<i<<','<<vector[i].n<<','<<vector[i].d<<']';
    }
    out<<']';
}
std::array<int,NV> column_point(int code) {
    std::array<int,NV> point{};
    for(int j=0;j<3;j++){int s=code%3;code/=3;if(s)point[2*j+s-1]=1;}
    return point;
}
Dense features(int code) {
    auto point=column_point(code);Dense result(21);
    for(int j=0;j<3;j++) {
        int g=point[2*j]-point[2*j+1];
        result[7*j]=g;
        for(int v=0;v<6;v++)result[7*j+v+1]=g*point[v];
    }
    return result;
}
std::uint32_t random_step(std::uint32_t& seed) {
    seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;return seed;
}
bool dyadic(const RatVec& v) {
    for(const auto& q:v)if((q.d&(q.d-1))!=0)return false;
    return true;
}
long long score(const RatVec& a,const RatVec& b) {
    long long result=0;
    for(const auto* v:{&a,&b})for(const auto& q:*v)if(!q.zero()) {
        result+=100+(q.n<0?-q.n:q.n)+q.d;
        if(q.d>2)result+=1000*q.d;
    }
    return result;
}
void integer_list(std::ostream& out,const std::vector<int>& values) {
    out<<'[';for(size_t i=0;i<values.size();i++){if(i)out<<',';out<<values[i];}out<<']';
}
Rat factor_value(const RatVec& coefficient,int code) {
    Dense f=features(code);Rat value(1);
    for(int i=0;i<21;i++)value=value-Rat(f[i])*coefficient[i];
    return value;
}
int rational_residue(const Rat& a,int p) {
    int d=int(a.d%p);need(d!=0,"denominator is not invertible in test field");
    return int((a.n%p+p)%p)*modpow(d,p-2,p)%p;
}
int main(int argc,char** argv) {
    std::string path;std::uint32_t seed=20260912;int attempts=2000;
    try {
        for(int i=1;i<argc;i++) {
            std::string arg=argv[i];
            if(arg=="--out" && i+1<argc)path=argv[++i];
            else if(arg=="--seed" && i+1<argc)seed=std::stoul(argv[++i]);
            else if(arg=="--attempts" && i+1<argc)attempts=std::stoi(argv[++i]);
            else throw std::runtime_error("usage: check_ternary_affine_triples --out PATH [--seed N] [--attempts N]");
        }
        need(!path.empty() && attempts>0 && attempts<=10000 && seed!=0,"search arguments");
        need(!std::ifstream(path).good(),"refusing to overwrite output");
        std::ofstream out(path);need(out.good(),"cannot open output");
        out<<"{\"record\":\"schema\",\"version\":1,\"seed\":"<<seed<<",\"attempts\":"<<attempts
           <<",\"states\":\"base-three column codes: empty, positive cell, negative cell\","
             "\"coefficient_order\":\"input j, then constant and x1,y1,x2,y2,x3,y3\","
             "\"arithmetic\":\"exact guarded rational search and exact prime-field certificates\"}\n";
        RatVec best_a,best_b;std::vector<int> best_first,best_second;
        long long best_score=std::numeric_limits<long long>::max();int best_attempt=-1,feasible=0,dyadic_count=0;
        for(int attempt=0;attempt<attempts;attempt++) {
            std::vector<int> order(26);std::iota(order.begin(),order.end(),1);
            for(int i=25;i>0;i--)std::swap(order[i],order[random_step(seed)%(i+1)]);
            std::vector<int> first(order.begin(),order.begin()+13),second(order.begin()+13,order.end());
            std::sort(first.begin(),first.end());std::sort(second.begin(),second.end());
            if(first.front()!=1)std::swap(first,second);
            std::vector<Dense> rows_a,rows_b;
            for(int state:first)rows_a.push_back(features(state));
            for(int state:second)rows_b.push_back(features(state));
            RatSolution a=rational_solve(rows_a),b=rational_solve(rows_b);
            bool both=a.feasible && b.feasible,is_dyadic=both && dyadic(a.coefficients) && dyadic(b.coefficients);
            if(both)feasible++;
            if(is_dyadic)dyadic_count++;
            out<<"{\"record\":\"attempt\",\"index\":"<<attempt<<",\"first\":";
            integer_list(out,first);out<<",\"second\":";integer_list(out,second);
            out<<",\"first_rank\":"<<a.rank<<",\"second_rank\":"<<b.rank
               <<",\"feasible\":"<<(both?"true":"false")<<",\"dyadic\":"<<(is_dyadic?"true":"false");
            if(both) {
                out<<",\"first_coefficients\":";ratvec_json(out,a.coefficients);
                out<<",\"second_coefficients\":";ratvec_json(out,b.coefficients);
            }
            out<<"}\n";
            if(is_dyadic && score(a.coefficients,b.coefficients)<best_score) {
                best_score=score(a.coefficients,b.coefficients);
                best_a=a.coefficients;best_b=b.coefficients;
                best_first=first;best_second=second;best_attempt=attempt;
            }
        }
        if(best_attempt<0) {
            out<<"{\"record\":\"summary\",\"found\":false,\"feasible_partitions\":"<<feasible
               <<",\"dyadic_partitions\":"<<dyadic_count<<"}\n";
            out.flush();need(out.good(),"output failure");
            std::cout<<"No dyadic cover found in "<<attempts<<" attempts; full search output "<<path<<"\n";return 0;
        }
        out<<"{\"record\":\"selected_cover\",\"attempt\":"<<best_attempt<<",\"score\":"<<best_score
           <<",\"first_states\":";integer_list(out,best_first);
        out<<",\"second_states\":";integer_list(out,best_second);
        out<<",\"first_coefficients\":";ratvec_json(out,best_a);
        out<<",\"second_coefficients\":";ratvec_json(out,best_b);out<<"}\n";
        for(int code=0;code<27;code++) {
            Rat a=factor_value(best_a,code),b=factor_value(best_b,code);
            need(a*b==Rat(code==0?1:0),"universal rational state cover");
            out<<"{\"record\":\"rational_state\",\"code\":"<<code
               <<",\"factor_values\":[["<<a.n<<','<<a.d<<"],["<<b.n<<','<<b.d<<"]]}\n";
        }
        StableCounts count;
        for(int p:{3,5,7}) {
            Poly one(p,1),selector=one;std::vector<NFRule> rules;
            for(int v=0;v<6;v++)rules.push_back(domain_rule(p,v,2));
            std::vector<Poly> input;
            for(int j=0;j<3;j++) {
                Poly x=variable(p,2*j),y=variable(p,2*j+1);Mon pair{};pair[2*j]=pair[2*j+1]=1;
                rules.push_back({x*y,pair});input.push_back(x-y);selector=selector*(one-x-y);
            }
            std::vector<Poly> beta;
            for(const auto* row:{&best_a,&best_b})for(int j=0;j<3;j++) {
                Poly b(p,rational_residue((*row)[7*j],p));
                for(int v=0;v<6;v++)b=b+Poly(p,rational_residue((*row)[7*j+v+1],p))*variable(p,v);
                beta.push_back(b);
            }
            std::string name="ternary_triple_F"+std::to_string(p);
            auto norm=certify(out,count,name,input,rules,6,2,beta);
            need(norm.H.deg()==4 && normal_form(norm.H,rules).value==selector,"triple degree and selector");
            for(int code=0;code<27;code++)
                state(out,count,name,rules,input,6,column_point(code),selector,&norm);
        }
        out<<"{\"record\":\"summary\",\"found\":true,\"feasible_partitions\":"<<feasible
           <<",\"dyadic_partitions\":"<<dyadic_count<<",\"selected_attempt\":"<<best_attempt
           <<",\"rational_states\":27,\"prime_fields\":3,\"normalizations\":"<<count.normalizations
           <<",\"NS_certificates\":"<<count.ns<<",\"common_models\":"<<count.source_models<<"}\n";
        out.flush();need(out.good(),"output failure");
        std::cout<<"Found universal dyadic cover at attempt "<<best_attempt
                 <<"; "<<count.ns<<" exact NS certificates and "<<count.source_models
                 <<" field models; output "<<path<<"\n";return 0;
    }catch(const std::exception& e){std::cerr<<"ERROR: "<<e.what()<<"\n";return 1;}
}
