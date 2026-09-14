// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Reuse archived complete moments to check target products and selector scope.
#include "ens_symbolic.hpp"
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <set>
#include <string>
using namespace ens_symbolic;
using U128=__uint128_t;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
int integer(const std::string& line,const std::string& key){
    auto pos=line.find("\""+key+"\":");need(pos!=std::string::npos,"missing integer "+key);
    pos+=key.size()+3;char* end=nullptr;
    long value=std::strtol(line.c_str()+pos,&end,10);
    need(end!=line.c_str()+pos && value>=-1 && value<=1000000000,"invalid integer");
    return int(value);
}
std::vector<int> integers(const std::string& line,const std::string& key){
    auto pos=line.find("\""+key+"\":[");need(pos!=std::string::npos,"missing array "+key);
    pos+=key.size()+4;std::vector<int> result;
    while(pos<line.size() && line[pos]!=']'){
        char* end=nullptr;long value=std::strtol(line.c_str()+pos,&end,10);
        need(end!=line.c_str()+pos && value>=0 && value<=1000000000,"array integer");
        result.push_back(int(value));pos=std::size_t(end-line.c_str());
        if(line[pos]==',')++pos;else need(line[pos]==']',"array separator");
    }
    need(pos<line.size() && line[pos]==']',"unterminated array");return result;
}
struct Moment {std::vector<int> cells;int value;};
struct Fixture {
    int p=0,n=0,m=0,ell=0,k=0,B=0;
    std::vector<int> directions;
    std::vector<Moment> moments;
};
int evaluate_moment(const Ring& r,const Polynomial& f,const Fixture& data){
    int total=0;
    for(const auto& [mon,c]:f){
        std::map<int,unsigned> requirement;
        for(int bit:mon){
            int row=bit/data.ell,axis=bit%data.ell;
            need(row<data.m && axis<31,"bit coordinate");
            requirement[row]|=1u<<axis;
        }
        for(const auto& moment:data.moments){
            if(moment.cells.size()!=requirement.size())continue;
            bool fits=true;std::size_t i=0;
            for(const auto& [row,mask]:requirement){
                int cell=moment.cells[i++],column=cell%data.n;
                if(cell/data.n!=row || (unsigned(column)&mask)!=mask){fits=false;break;}
            }
            if(fits)total=r.residue(total+c*moment.value);
        }
    }
    return total;
}
bool leading_before(const Monomial& a,const Monomial& b,int variables){
    if(a.size()!=b.size())return a.size()>b.size();
    for(int v=0;v<variables;++v){
        int aa=int(std::count(a.begin(),a.end(),v)),bb=int(std::count(b.begin(),b.end(),v));
        if(aa!=bb)return aa>bb;
    }
    return false;
}
Monomial leading(const Polynomial& f,int variables){
    need(!f.empty(),"zero leading polynomial");Monomial result=f.begin()->first;
    for(const auto& [mon,c]:f){(void)c;if(leading_before(mon,result,variables))result=mon;}
    return result;
}
void array(std::ostream& out,const std::vector<int>& values){
    out<<'[';for(std::size_t i=0;i<values.size();++i){if(i)out<<',';out<<values[i];}out<<']';
}
void target_case(std::ostream& out,const Fixture& data){
    need(data.p && data.k>=2 && data.k<20 && data.B>=data.k+1,"moment fixture range");
    need(data.directions.size()==std::size_t(data.k) &&
         data.moments.size()==(std::size_t(1)<<data.k),"complete top tensor support");
    Ring r(data.p,64);auto one=r.constant(1);
    auto bit=[&](int row,int axis){return r.variable(row*data.ell+axis);};
    auto first=bit(0,data.directions[0]);
    auto q=r.add(r.add(r.multiply(r.constant(data.p-1),first),
                      bit(1,(data.directions[1]+1)%data.ell)),one);
    auto multiplier=one;
    for(int row=1;row<data.k;++row)multiplier=r.multiply(multiplier,bit(row,data.directions[row]));
    auto product=r.multiply(q,multiplier);
    auto lq=leading(q,data.k*data.ell),lf=leading(multiplier,data.k*data.ell);
    auto lp=leading(product,data.k*data.ell);
    std::set<int> qrows,frows,prows;
    for(int v:lq)qrows.insert(v/data.ell);
    for(int v:lf)frows.insert(v/data.ell);
    for(int v:lp)prows.insert(v/data.ell);
    for(int row:qrows)need(!frows.count(row),"multiplier uses a leading target row");
    need(lp.size()==std::size_t(data.k) && prows.size()==lp.size(),"row-linear top product monomial");
    int mu=evaluate_moment(r,product,data);
    need(mu==data.p-1,"safe product moment");
    bool within_row_term=false;
    for(const auto& [mon,c]:product){
        (void)c;std::set<int> rows;
        for(int v:mon)rows.insert(v/data.ell);
        if(rows.size()<mon.size())within_row_term=true;
    }
    need(within_row_term,"fixture lacks the non-row-linear term");
    out<<"{\"record\":\"safe_target_product\",\"field\":"<<data.p<<",\"holes\":"<<data.n
       <<",\"bit_length\":"<<data.ell<<",\"moment_degree\":"<<data.B<<",\"selected_rows\":"<<data.k
       <<",\"target\":";write_json(out,q);out<<",\"multiplier\":";write_json(out,multiplier);
    out<<",\"product\":";write_json(out,product);
    out<<",\"leading_target\":";array(out,lq);out<<",\"leading_product\":";array(out,lp);
    out<<",\"moment_value\":"<<mu<<",\"has_within_row_term\":true,\"top_moments_used\":"
       <<data.moments.size()<<"}\n";
    auto bad_q=r.subtract(one,first),bad_f=r.multiply(first,multiplier);
    auto bad_product=r.multiply(bad_q,bad_f);
    auto old_boolean=r.subtract(r.power(first,2),first);
    auto cofactor=r.multiply(r.constant(-1),multiplier);
    need(r.multiply(cofactor,old_boolean)==bad_product,"zero-divisor NS witness");
    need(evaluate_moment(r,bad_product,data)==0,"zero-divisor moment control");
    out<<"{\"record\":\"zero_divisor_control\",\"field\":"<<data.p<<",\"holes\":"<<data.n
       <<",\"target\":";write_json(out,bad_q);out<<",\"multiplier\":";write_json(out,bad_f);
    out<<",\"product\":";write_json(out,bad_product);out<<",\"old_Boolean_axiom\":";
    write_json(out,old_boolean);out<<",\"NS_cofactor\":";write_json(out,cofactor);
    out<<",\"witness_degree\":"<<degree(cofactor)+2<<",\"moment_value\":0,"
         "\"both_factors_are_nonzero_Boolean_functions\":true}\n";
}
void NS_record(std::ostream& out,const Ring& r,const std::string& name,
               const std::vector<Polynomial>& axioms,const Polynomial& target,
               const std::vector<std::pair<int,Polynomial>>& cofactors,int budget){
    Polynomial sum;int used=0;
    out<<"{\"record\":\"selector_NS_control\",\"name\":\""<<name<<"\",\"field\":"<<r.p
       <<",\"axioms\":";write_polynomials(out,axioms);out<<",\"target\":";write_json(out,target);
    out<<",\"terms\":[";
    for(std::size_t i=0;i<cofactors.size();++i){
        const auto& [id,q]=cofactors[i];
        r.accumulate(sum,r.multiply(q,axioms.at(id)));
        if(!q.empty() && !axioms[id].empty())used=std::max(used,degree(q)+degree(axioms[id]));
        if(i)out<<',';
        out<<"{\"axiom_id\":"<<id<<",\"cofactor\":";write_json(out,q);out<<'}';
    }
    need(sum==target && used<=budget,"selector NS identity");
    out<<"],\"budget\":"<<budget<<",\"witness_degree\":"<<used<<"}\n";
}
void model(std::ostream& out,const Ring& r,const std::string& name,std::map<int,int> point,
           int variables,const std::vector<Polynomial>& axioms,int omit,const Polynomial& P,int expected){
    for(int i=0;i<variables;++i)point.emplace(i,0);
    out<<"{\"record\":\"selector_model\",\"name\":\""<<name<<"\",\"field\":"<<r.p<<",\"assignment\":[";
    for(int i=0;i<variables;++i){if(i)out<<',';out<<point[i];}
    out<<"],\"omitted_axiom\":"<<omit<<",\"axiom_values\":[";
    for(std::size_t i=0;i<axioms.size();++i){
        int value=r.evaluate(axioms[i],point);need(int(i)==omit || value==0,"selector model");
        if(i)out<<',';
        out<<value;
    }
    int value=r.evaluate(P,point);need(value==expected,"selector product value");
    out<<"],\"product\":";write_json(out,P);out<<",\"product_value\":"<<value<<"}\n";
}
void selector_controls(std::ostream& out,int p){
    Ring r(p,64);auto one=r.constant(1),b=r.variable(0);int fresh=1;
    auto A=make_block(r,{b},1,fresh);
    std::vector<Polynomial> axioms={r.subtract(r.power(b,2),b),
        r.subtract(r.power(r.variable(1),p),r.variable(1)),A.companions[0]};
    auto relation=r.add(r.subtract(A.product,one),b);
    NS_record(out,r,"literal_selector_old_coordinate_relation",axioms,relation,
              {{2,one},{0,A.prefix[0]}},3);
    model(out,r,"literal_selector_at_zero",{{0,0},{1,0}},fresh,axioms,-1,A.product,1);
    model(out,r,"literal_selector_at_one",{{0,1},{1,1}},fresh,axioms,-1,A.product,0);
    out<<"{\"record\":\"partial_moment_counter\",\"field\":"<<p
       <<",\"lambda_1\":1,\"lambda_b\":0,\"lambda_P\":0,\"derived_relation_value\":"
       <<p-1<<",\"scope\":\"old-coordinate values do not allow an independent selector value\"}\n";
    auto x=[&](int i){return r.variable(i);};fresh=5;
    std::vector<Polynomial> forms={r.subtract(x(0),x(2)),r.subtract(x(1),x(3)),x(4)};
    auto C=make_block(r,forms,1,fresh);axioms.clear();
    for(int i=0;i<fresh;++i)axioms.push_back(r.subtract(r.power(x(i),i<5?2:p),x(i)));
    auto E=r.multiply(r.subtract(one,r.power(forms[0],p-1)),r.subtract(one,r.power(forms[1],p-1)));
    int e=int(axioms.size());axioms.push_back(E);
    int first=int(axioms.size());for(const auto& g:C.companions)axioms.push_back(g);
    auto V0=r.power(forms[0],p-2);
    auto V1=r.multiply(r.power(forms[1],p-2),r.subtract(one,r.power(forms[0],p-1)));
    NS_record(out,r,"proper_rank_three_selector_forced_zero",axioms,C.product,
              {{e,C.product},{first,V0},{first+1,V1}},2+2*(p-1));
    model(out,r,"forced_selector_satisfiable_old_collision",{{0,1},{5,1}},fresh,axioms,-1,C.product,0);
    model(out,r,"forced_selector_missing_collision",{},fresh,axioms,e,C.product,1);
}
U128 multiply(U128 a,U128 b){need(!b || a<=~U128(0)/b,"integer overflow");return a*b;}
U128 choose(int n,int k){
    need(k>=0 && k<=n,"binomial range");k=std::min(k,n-k);U128 result=1;
    for(int i=1;i<=k;++i)result=multiply(result,U128(n-k+i))/U128(i);
    return result;
}
std::string decimal(U128 value){
    if(!value)return "0";
    std::string result;
    while(value){result.push_back(char('0'+value%10));value/=10;}
    std::reverse(result.begin(),result.end());return result;
}
void dimensions(std::ostream& out){
    int n=64,ell=6,m=65,k=10,rstar=3*ell*(k+1)+1,v=m*ell;
    U128 image=choose(v-rstar+k,k),power=1;for(int j=0;j<k;++j)power=multiply(power,ell);
    for(int excluded:{0,5,55}){
        U128 denominator=multiply(choose(m-excluded,k),power);
        bool quarter=multiply(4,image)<denominator;
        need(quarter==(excluded<=5),"excluded-row dimension control");
        out<<"{\"record\":\"excluded_row_dimension\",\"holes\":"<<n<<",\"ell\":"<<ell<<",\"k\":"<<k
           <<",\"excluded_rows\":"<<excluded<<",\"high_rank_threshold\":"<<rstar
           <<",\"restriction_dimension\":\""<<decimal(image)<<"\",\"available_top_dimension\":\""
           <<decimal(denominator)<<"\",\"quarter_bound\":"<<(quarter?"true":"false")
           <<",\"scope\":\"dimension comparison only; no final PC degree condition asserted\"}\n";
    }
}
int main(int argc,char** argv){
    try{
        need(argc==5 && std::string(argv[1])=="--moments" && std::string(argv[3])=="--out",
             "usage: --moments ARCHIVED_JSONL --out NEW_PATH");
        std::ifstream input(argv[2]);need(bool(input),"moment input open");
        std::filesystem::path path=argv[4];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");
        out<<"{\"record\":\"schema\",\"version\":1,\"moment_source\":\""<<argv[2]
           <<"\",\"scope\":\"new target evaluations reuse archived complete moment witnesses; no marginal suite rerun\","
             "\"decoder_evaluation\":\"Boolean powers and same-row exclusions give matching moments with required label bits\"}\n";
        Fixture data;std::string line;int fixtures=0,field=0;
        while(std::getline(input,line)){
            if(line.find("\"record\":\"fixture\"")!=std::string::npos){
                if(data.p){target_case(out,data);++fixtures;}
                data=Fixture{};data.p=integer(line,"field");data.n=integer(line,"holes");
                data.m=integer(line,"pigeons");data.ell=integer(line,"bit_length");
                data.k=integer(line,"selected_rows");data.B=integer(line,"degree");
                data.directions=integers(line,"directions");
                need(data.ell>=2 && data.ell<20 && data.n==(1<<data.ell) &&
                     data.m==data.n+1 && data.k>=2 && data.k<20 && data.k<=data.m &&
                     data.B>=data.k+1 && data.n>=2*data.B-1 &&
                     4*(data.k-1)<data.n && integer(line,"normalization")==0,
                     "archived fixture parameters");
                for(int direction:data.directions)need(direction<data.ell,"bit direction");
                need(!field || field==data.p,"mixed moment fields");field=data.p;
            }else if(line.find("\"record\":\"moment\"")!=std::string::npos){
                need(data.p,"moment before fixture");auto cells=integers(line,"cells");
                need(cells.size()>=std::size_t(data.k) && cells.size()<=std::size_t(data.B),
                     "unexpected moment support degree");
                if(cells.size()==std::size_t(data.k)){
                    std::set<int> columns;
                    for(int row=0;row<data.k;++row){
                        need(cells[row]/data.n==row,"top moment rows");
                        need(columns.insert(cells[row]%data.n).second,"collision in moment support");
                    }
                    int value=integer(line,"value");need(value>0 && value<data.p,"moment coefficient");
                    data.moments.push_back({std::move(cells),value});
                }
            }
        }
        need(input.eof() && data.p,"incomplete moment input");
        target_case(out,data);++fixtures;need(fixtures==2,"expected two archived fixtures");
        selector_controls(out,field);dimensions(out);
        out<<"{\"record\":\"summary\",\"field\":"<<field<<",\"target_fixtures\":2,"
             "\"selector_NS_controls\":2,\"selector_models\":4,\"dimension_controls\":3,\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<"F"<<field<<": two safe-product moment evaluations, zero-divisor witnesses, "
                    "two full selector NS controls, and dimension checks passed.\n";
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
