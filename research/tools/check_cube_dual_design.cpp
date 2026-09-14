// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Independent sparse audit of cube times residual matching-design functionals.
#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <map>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
using U64=std::uint64_t;
using Matching=std::vector<int>;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
U64 multiply(U64 a,U64 b){
    need(!b || a<=std::numeric_limits<U64>::max()/b,"integer overflow");return a*b;
}
U64 choose(int n,int k){
    if(k<0 || k>n)return 0;
    k=std::min(k,n-k);U64 value=1;
    for(int i=1;i<=k;++i)value=multiply(value,U64(n-k+i))/U64(i);
    return value;
}
U64 power(U64 base,int e){U64 value=1;for(int i=0;i<e;++i)value=multiply(value,base);return value;}
template<class T>void array(std::ostream& out,const std::vector<T>& values){
    out<<'[';for(std::size_t i=0;i<values.size();++i){if(i)out<<',';out<<values[i];}out<<']';
}
U64 row_mask(const Matching& M,int n){
    U64 mask=0;for(int cell:M)mask|=U64(1)<<(cell/n);return mask;
}
struct Constraint {std::vector<int> left;int right=-1;};
void run_case(std::ostream& out,int n,int k){
    int ell=0;while((1<<ell)<n)++ell;
    int m=n+1,B=k+2;
    need((1<<ell)==n && n>=4 && 4*(k-1)<n && n>=2*B-1 && m<64,"fixture range");
    std::vector<std::vector<int>> lines;
    std::vector<int> directions;
    std::vector<bool> used(n);
    for(int i=0;i<k;++i){
        int direction=i%ell;directions.push_back(direction);bool found=false;
        for(int a=0;a<n && !found;++a){
            int b=a^(1<<direction);
            if(a<b && !used[a] && !used[b]){
                lines.push_back({a,b});used[a]=used[b]=true;found=true;
            }
        }
        need(found,"disjoint lines");
    }
    std::vector<int> available;for(int j=0;j<n;++j)if(!used[j])available.push_back(j);
    need(available.size()>=3,"residual degree-two design");
    int q=available[0],a=available[1],b=available[2];
    std::vector<std::pair<int,int>> path={{q,a},{b,a},{b,q}};
    std::vector<Matching> moments;
    for(U64 bits=0;bits<(U64(1)<<k);++bits){
        Matching base;for(int i=0;i<k;++i)base.push_back(i*n+lines[i][(bits>>i)&1]);
        moments.push_back(base);
        for(int r=k;r<m;++r){
            auto mon=base;mon.push_back(r*n+q);moments.push_back(std::move(mon));
        }
        for(int r=k;r<m;++r)for(int s=r+1;s<m;++s)for(const auto& [c,d]:path){
            auto mon=base;mon.push_back(r*n+c);mon.push_back(s*n+d);moments.push_back(std::move(mon));
        }
    }
    std::sort(moments.begin(),moments.end(),[](const auto& x,const auto& y){
        if(x.size()!=y.size())return x.size()<y.size();
        return x<y;
    });
    std::map<Matching,int> index;
    for(std::size_t id=0;id<moments.size();++id){
        const auto& mon=moments[id];
        U64 rows=0,columns=0;
        for(int cell:mon){
            U64 rr=U64(1)<<(cell/n),cc=U64(1)<<(cell%n);
            need(!(rows&rr) && !(columns&cc),"nonmatching support");
            rows|=rr;columns|=cc;
        }
        need(mon.size()<=std::size_t(B) && index.emplace(mon,int(id)).second,"duplicate or oversized moment");
    }
    U64 expected=multiply(U64(1)<<k,1+U64(m-k)+3*choose(m-k,2));
    need(moments.size()==expected,"complete tensor support count");
    std::map<std::pair<int,Matching>,Constraint> constraints;
    U64 face_count=0,rhs_count=0;int corrupt=-1;
    for(std::size_t id=0;id<moments.size();++id){
        const auto& mon=moments[id];
        if(mon.size()==std::size_t(B) && corrupt<0)corrupt=int(id);
        for(std::size_t pos=0;pos<mon.size();++pos){
            int row=mon[pos]/n;auto face=mon;face.erase(face.begin()+pos);
            constraints[{row,face}].left.push_back(int(id));++face_count;
        }
        if(mon.size()<std::size_t(B)){
            U64 rows=row_mask(mon,n);
            for(int row=0;row<m;++row)if(!((rows>>row)&1)){
                auto& c=constraints[{row,mon}];
                need(c.right<0,"duplicate right moment");c.right=int(id);++rhs_count;
            }
        }
    }
    need(corrupt>=0,"missing top moment control");
    U64 all_rows=0,falling=1;
    for(int s=0;s<B;++s){
        if(s)falling=multiply(falling,U64(n-s+1));
        U64 add=multiply(multiply(choose(m,s),falling),U64(m-s));
        need(all_rows<=std::numeric_limits<U64>::max()-add,"constraint count overflow");all_rows+=add;
    }
    U64 basis=0;for(int s=0;s<=k;++s)basis+=multiply(choose(m,s),power(ell,s));
    std::string name="n"+std::to_string(n)+"_k"+std::to_string(k)+"_B"+std::to_string(B);
    out<<"{\"record\":\"fixture\",\"name\":\""<<name<<"\",\"field\":2,\"holes\":"<<n
       <<",\"pigeons\":"<<m<<",\"bit_length\":"<<ell<<",\"selected_rows\":"<<k
       <<",\"degree\":"<<B<<",\"normalization\":0,\"directions\":";array(out,directions);
    out<<",\"lines\":[";
    for(std::size_t i=0;i<lines.size();++i){if(i)out<<',';array(out,lines[i]);}
    out<<"],\"residual_columns\":";array(out,available);
    out<<",\"residual_first_moment_column\":"<<q<<",\"residual_pair_path\":[";
    for(std::size_t i=0;i<path.size();++i){if(i)out<<',';out<<'['<<path[i].first<<','<<path[i].second<<']';}
    out<<"],\"nonzero_moments\":"<<moments.size()<<",\"all_row_marginals\":"<<all_rows
       <<",\"stored_marginal_rows\":"<<constraints.size()<<",\"row_linear_basis_dimension\":"<<basis<<"}\n";
    for(std::size_t id=0;id<moments.size();++id){
        out<<"{\"record\":\"moment\",\"id\":"<<id<<",\"cells\":";
        array(out,moments[id]);out<<",\"value\":1}\n";
    }
    int corrupted_failures=0;U64 seen_faces=0,seen_rhs=0;
    for(const auto& [key,c]:constraints){
        const auto& [row,face]=key;
        int lhs=int(c.left.size()%2),rhs=c.right>=0?1:0;
        need(lhs==rhs,"row marginal failed");
        seen_faces+=c.left.size();seen_rhs+=rhs;
        out<<"{\"record\":\"row_marginal\",\"row\":"<<row<<",\"cells\":";
        array(out,face);out<<",\"nonzero_extensions\":";array(out,c.left);
        out<<",\"right_moment\":"<<c.right<<",\"value\":"<<rhs<<"}\n";
        int corrupted=lhs;
        for(int id:c.left)if(id==corrupt)corrupted^=1;
        if(c.right==corrupt)rhs^=1;
        if(corrupted!=rhs){
            ++corrupted_failures;
            out<<"{\"record\":\"corruption_failure\",\"removed_top_moment\":"<<corrupt
               <<",\"row\":"<<row<<",\"cells\":";array(out,face);
            out<<",\"left\":"<<corrupted<<",\"right\":"<<rhs<<"}\n";
        }
    }
    need(seen_faces==face_count && seen_rhs==rhs_count && corrupted_failures==B,"support/negative control audit");
    int nonzero=0;U64 combinations=power(ell,k);
    for(U64 code=0;code<combinations;++code){
        U64 temporary=code;std::vector<int> axes(k);
        bool chosen=true;
        for(int i=0;i<k;++i){axes[i]=int(temporary%ell);temporary/=ell;chosen&=axes[i]==directions[i];}
        int value=0;
        for(const auto& mon:moments){
            if(mon.size()!=std::size_t(k))break; // Moments are sorted by size.
            int coefficient=1;
            for(int i=0;i<k;++i){
                need(mon[i]/n==i,"low-degree moment has wrong row support");
                coefficient&=(mon[i]%n>>axes[i])&1;
            }
            value^=coefficient;
        }
        need(value==int(chosen),"decoded row-linear coordinate");nonzero+=value;
        out<<"{\"record\":\"selected_row_basis_value\",\"axes\":";array(out,axes);
        out<<",\"value\":"<<value<<"}\n";
    }
    need(nonzero==1,"dual coordinate count");
    out<<"{\"record\":\"case_summary\",\"name\":\""<<name<<"\",\"passed\":true,"
         "\"all_unlisted_moments\":0,\"unlisted_marginals\":\"all terms and right side zero\","
         "\"other_row_linear_basis_values\":0,\"selected_axes_checked\":"<<combinations
       <<",\"nonzero_basis_values\":1,\"corrupted_marginals\":"<<corrupted_failures<<"}\n";
    std::cout<<name<<": "<<moments.size()<<" nonzero moments; "<<constraints.size()
             <<" sparse marginal rows represent "<<all_rows<<" possible rows; one isolated bit coordinate.\n";
    std::cout<<"Deleting one top moment fails exactly "<<corrupted_failures<<" marginal equations.\n";
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");
        out<<"{\"record\":\"schema\",\"version\":1,\"field\":2,"
              "\"cell_encoding\":\"row*holes+column\","
              "\"ordinary_polynomials\":\"reduce repeated variables using Booleanity; row/column collisions have value zero\","
              "\"sparse_completeness\":\"every nonzero moment contributes all its faces; every nonzero lower moment contributes every missing-row right side\","
              "\"decoder\":\"b_i,t maps to sum over column labels with bit t equal to one of X_i,column\"}\n";
        run_case(out,8,2);run_case(out,32,6);
        out<<"{\"record\":\"summary\",\"fixtures\":2,\"passed\":true}\n";
        need(bool(out),"output write");
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
