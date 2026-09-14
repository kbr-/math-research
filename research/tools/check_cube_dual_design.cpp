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
void run_case(std::ostream& out,int n,int k,int prime,bool higher=false){
    auto mod=[prime](int value){value%=prime;return value<0?value+prime:value;};
    int ell=0;while((1<<ell)<n)++ell;
    int m=n+1,B=k+2;
    need((1<<ell)==n && n>=4 && 4*(k-1)<n && n>=2*B-1 && m<64,"fixture range");
    std::vector<std::vector<int>> lines,axis_sets;
    std::vector<int> directions;
    std::vector<bool> used(n);
    int bit_degree=0;
    for(int i=0;i<k;++i){
        std::vector<int> axes;
        if(higher){
            need(k==2 && (n==16 || n==32),"higher-cube fixture range");
            if(i==0)for(int j=0;j<ell-2;++j)axes.push_back(j);
            else axes.push_back(ell-1);
        }else axes={i%ell};
        axis_sets.push_back(axes);bit_degree+=int(axes.size());
        directions.push_back(axes[0]);bool found=false;
        for(int a=0;a<n && !found;++a){
            bool canonical=true;for(int axis:axes)canonical&=!(a&(1<<axis));
            if(!canonical)continue;
            std::vector<int> cube;bool free=true;
            for(unsigned mask=0;mask<(1u<<axes.size());++mask){
                int vertex=a;for(std::size_t j=0;j<axes.size();++j)
                    if((mask>>j)&1u)vertex|=1<<axes[j];
                cube.push_back(vertex);free&=!used[vertex];
            }
            if(!free)continue;
            lines.push_back(cube);for(int vertex:cube)used[vertex]=true;found=true;
        }
        need(found,"disjoint coordinate cubes");
    }
    need(bit_degree<=B,"selected bit degree exceeds moment degree");
    std::vector<int> available;for(int j=0;j<n;++j)if(!used[j])available.push_back(j);
    need(available.size()>=3,"residual degree-two design");
    int q=available[0],a=available[1],b=available[2];
    std::vector<std::pair<int,int>> path={{q,a},{b,a},{b,q}};
    std::vector<Matching> moments;
    std::map<Matching,int> weights;
    auto put=[&](Matching mon,int value){
        need(weights.emplace(mon,mod(value)).second,"duplicate weighted moment");
        moments.push_back(std::move(mon));
    };
    for(U64 bits=0;bits<(U64(1)<<bit_degree);++bits){
        Matching base;int sign=1,offset=0;
        for(int i=0;i<k;++i){
            int count=int(axis_sets[i].size());
            unsigned endpoint=unsigned((bits>>offset)&((U64(1)<<count)-1));offset+=count;
            base.push_back(i*n+lines[i][endpoint]);
            if((count-__builtin_popcount(endpoint))%2)sign=-sign;
        }
        put(base,sign);
        for(int r=k;r<m;++r){
            auto mon=base;mon.push_back(r*n+q);put(std::move(mon),sign);
        }
        for(int r=k;r<m;++r)for(int s=r+1;s<m;++s)for(const auto& [c,d]:path){
            auto mon=base;mon.push_back(r*n+c);mon.push_back(s*n+d);
            put(std::move(mon),c==b && d==a?-sign:sign);
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
    U64 expected=multiply(U64(1)<<bit_degree,1+U64(m-k)+3*choose(m-k,2));
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
    out<<"{\"record\":\"fixture\",\"name\":\""<<name<<"\",\"field\":"<<prime<<",\"holes\":"<<n
       <<",\"pigeons\":"<<m<<",\"bit_length\":"<<ell<<",\"selected_rows\":"<<k
       <<",\"degree\":"<<B<<",\"normalization\":0,\"directions\":";array(out,directions);
    out<<",\"lines\":[";
    for(std::size_t i=0;i<lines.size();++i){if(i)out<<',';array(out,lines[i]);}
    out<<"],\"residual_columns\":";array(out,available);
    if(higher){
        out<<",\"selected_bit_degree\":"<<bit_degree<<",\"axis_sets\":[";
        for(int i=0;i<k;++i){if(i)out<<',';array(out,axis_sets[i]);}
        out<<"],\"removed_column_count\":"<<n-int(available.size());
    }
    out<<",\"residual_first_moment_column\":"<<q<<",\"residual_pair_path\":[";
    for(std::size_t i=0;i<path.size();++i){if(i)out<<',';out<<'['<<path[i].first<<','<<path[i].second<<']';}
    out<<"],\"nonzero_moments\":"<<moments.size()<<",\"all_row_marginals\":"<<all_rows
       <<",\"stored_marginal_rows\":"<<constraints.size()<<",\"row_linear_basis_dimension\":"<<basis<<"}\n";
    for(std::size_t id=0;id<moments.size();++id){
        out<<"{\"record\":\"moment\",\"id\":"<<id<<",\"cells\":";
        array(out,moments[id]);out<<",\"value\":"<<weights.at(moments[id])<<"}\n";
    }
    int corrupted_failures=0;U64 seen_faces=0,seen_rhs=0,unsigned_failures=0;
    for(const auto& [key,c]:constraints){
        const auto& [row,face]=key;
        int lhs=0;for(int id:c.left)lhs=mod(lhs+weights.at(moments[id]));
        int rhs=c.right>=0?weights.at(moments[c.right]):0;
        need(lhs==rhs,"row marginal failed");
        seen_faces+=c.left.size();seen_rhs+=int(c.right>=0);
        if(int(c.left.size()%prime)!=int(c.right>=0))++unsigned_failures;
        out<<"{\"record\":\"row_marginal\",\"row\":"<<row<<",\"cells\":";
        array(out,face);out<<",\"nonzero_extensions\":";array(out,c.left);
        out<<",\"right_moment\":"<<c.right<<",\"value\":"<<rhs<<"}\n";
        int corrupted=lhs;
        for(int id:c.left)if(id==corrupt)corrupted=mod(corrupted-weights.at(moments[id]));
        if(c.right==corrupt)rhs=0;
        if(corrupted!=rhs){
            ++corrupted_failures;
            out<<"{\"record\":\"corruption_failure\",\"removed_top_moment\":"<<corrupt
               <<",\"row\":"<<row<<",\"cells\":";array(out,face);
            out<<",\"left\":"<<corrupted<<",\"right\":"<<rhs<<"}\n";
        }
    }
    need(seen_faces==face_count && seen_rhs==rhs_count && corrupted_failures==B,"support/negative control audit");
    int nonzero=0;U64 combinations=higher?power(U64((1<<ell)-1),k):power(ell,k);
    U64 checked=0;
    for(U64 code=0;code<combinations;++code){
        U64 temporary=code;std::vector<int> axes(k),masks(k);
        bool chosen=true;
        int total_degree=0;
        for(int i=0;i<k;++i){
            if(higher){
                masks[i]=1+int(temporary%((1<<ell)-1));temporary/=(1<<ell)-1;
                int selected=0;for(int axis:axis_sets[i])selected|=1<<axis;
                chosen&=masks[i]==selected;total_degree+=__builtin_popcount(unsigned(masks[i]));
            }else{
                axes[i]=int(temporary%ell);temporary/=ell;
                masks[i]=1<<axes[i];chosen&=axes[i]==directions[i];
            }
        }
        if(higher && total_degree>bit_degree)continue;
        ++checked;
        int value=0;
        for(const auto& mon:moments){
            if(mon.size()!=std::size_t(k))break; // Moments are sorted by size.
            int coefficient=1;
            for(int i=0;i<k;++i){
                need(mon[i]/n==i,"low-degree moment has wrong row support");
                coefficient&=((mon[i]%n)&masks[i])==masks[i];
            }
            value=mod(value+coefficient*weights.at(mon));
        }
        need(value==int(chosen),"decoded row-linear coordinate");nonzero+=value;
        out<<"{\"record\":\"selected_row_basis_value\",";
        out<<(higher?"\"axis_masks\":":"\"axes\":");array(out,higher?masks:axes);
        out<<",\"value\":"<<value<<"}\n";
    }
    need(nonzero==1,"dual coordinate count");
    if(higher){
        using Term=std::pair<int,std::vector<int>>;
        using Poly=std::vector<Term>;
        auto write_poly=[&](const Poly& poly){
            out<<'[';
            for(std::size_t j=0;j<poly.size();++j){
                if(j)out<<',';
                out<<'['<<mod(poly[j].first)<<',';array(out,poly[j].second);out<<']';
            }
            out<<']';
        };
        auto value=[&](const Poly& poly){
            int result=0;
            for(const auto& [c,mon]:poly){
                need(mon.size()<=std::size_t(B),"target outside moment budget");
                std::map<int,int> requirements;
                for(int bit:mon)requirements[bit/ell]|=1<<(bit%ell);
                for(const auto& matching:moments){
                    if(matching.size()!=requirements.size())continue;
                    bool fits=true;std::size_t j=0;
                    for(const auto& [row,mask]:requirements){
                        int cell=matching[j++];
                        if(cell/n!=row || ((cell%n)&mask)!=mask){fits=false;break;}
                    }
                    if(fits)result=mod(result+c*weights.at(matching));
                }
            }
            return result;
        };
        std::vector<int> qbits,top;
        for(int axis:axis_sets[0])qbits.push_back(axis);
        top=qbits;top.push_back(ell+axis_sets[1][0]);
        int tail=ell+axis_sets[1][0];
        Poly target={{prime-1,qbits},{1,{ell}},{1,{}}};
        Poly multiplier={{1,{tail}}};
        Poly product={{prime-1,top},{1,{ell,tail}},{1,{tail}}};
        need(value(product)==prime-1,"multibit target product");
        out<<"{\"record\":\"higher_cube_target\",\"target\":";write_poly(target);
        out<<",\"multiplier\":";write_poly(multiplier);
        out<<",\"product\":";write_poly(product);
        out<<",\"moment_value\":"<<value(product)<<",\"degree\":"<<bit_degree<<"}\n";
        if(bit_degree+1<=B){
            need(q>0,"nonzero residual label for lower-term control");
            int axis=0;while(!(q&(1<<axis)))++axis;
            auto longer=top;longer.push_back(k*ell+axis);
            Poly control={{1,top},{prime-1,longer}};
            need(value(control)==0,"non-top monomial control");
            out<<"{\"record\":\"non_top_term_control\",\"polynomial\":";write_poly(control);
            out<<",\"moment_value\":0,\"degree\":"<<bit_degree+1
               <<",\"selected_lower_monomial\":";array(out,top);
            out<<",\"scope\":\"a fixed cube witness need not detect a non-top term; not a claim of an old polynomial relation\"}\n";
        }
    }
    if(prime!=2){
        need(unsigned_failures>0,"missing unsigned-moment control");
        out<<"{\"record\":\"unsigned_moment_control\",\"field\":"<<prime
           <<",\"replace_every_nonzero_moment_by\":1,\"failed_marginals\":"
           <<unsigned_failures<<"}\n";
    }
    out<<"{\"record\":\"case_summary\",\"name\":\""<<name<<"\",\"passed\":true,"
         "\"all_unlisted_moments\":0,\"unlisted_marginals\":\"all terms and right side zero\","
         "\"other_row_linear_basis_values\":0,\"selected_axes_checked\":"<<checked
       <<",\"nonzero_basis_values\":1,\"corrupted_marginals\":"<<corrupted_failures<<"}\n";
    std::cout<<name<<": "<<moments.size()<<" nonzero moments; "<<constraints.size()
             <<" sparse marginal rows represent "<<all_rows<<" possible rows; one isolated bit coordinate.\n";
    std::cout<<"Deleting one top moment fails exactly "<<corrupted_failures<<" marginal equations.\n";
}
int main(int argc,char** argv){
    try{
        need(argc>=3 && std::string(argv[1])=="--out",
             "usage: --out NEW_PATH [--prime 2|3|5|7] [--higher-cubes]");
        int prime=2;bool higher=false,prime_set=false;
        for(int a=3;a<argc;++a){
            std::string option=argv[a];
            if(option=="--prime"){
                need(!prime_set && a+1<argc,"prime flag");prime_set=true;prime=std::stoi(argv[++a]);
                need(prime==2 || prime==3 || prime==5 || prime==7,"prime guard");
            }else if(option=="--higher-cubes"){need(!higher,"repeated higher-cubes flag");higher=true;}
            else throw std::runtime_error("unknown argument");
        }
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");
        out<<"{\"record\":\"schema\",\"version\":1,\"field\":"<<prime<<","
              "\"cell_encoding\":\"row*holes+column\","
              "\"ordinary_polynomials\":\"reduce repeated variables using Booleanity; row/column collisions have value zero\","
              "\"sparse_completeness\":\"every nonzero moment contributes all its faces; every nonzero lower moment contributes every missing-row right side\","
              "\"decoder\":\"b_i,t maps to sum over column labels with bit t equal to one of X_i,column\"}\n";
        if(higher){run_case(out,16,2,prime,true);run_case(out,32,2,prime,true);}
        else{run_case(out,8,2,prime);run_case(out,32,6,prime);}
        out<<"{\"record\":\"summary\",\"fixtures\":2,\"passed\":true}\n";
        need(bool(out),"output write");
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
