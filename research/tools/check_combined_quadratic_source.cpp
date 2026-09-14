// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Direct old-only quadratic maps, quotient counts, cube costs, and parameters.
#include "domain_polynomial.hpp"
#include "ns_witness.hpp"
#include <boost/multiprecision/cpp_int.hpp>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
using namespace domain_polynomial;
using boost::multiprecision::cpp_int;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
cpp_int choose(unsigned n,unsigned k){
    if(k>n)return 0;
    k=std::min(k,n-k);cpp_int result=1;
    for(unsigned i=1;i<=k;++i){result*=n-k+i;result/=i;}return result;
}
cpp_int power(cpp_int a,unsigned e){
    cpp_int result=1;
    while(e){if(e&1)result*=a;a*=a;e>>=1;}return result;
}
cpp_int ceil_sqrt(const cpp_int& a){
    if(a==0)return 0;
    cpp_int lo=0,hi=1;
    while(hi*hi<a)hi<<=1;
    while(lo+1<hi){
        cpp_int mid=(lo+hi)/2;
        if(mid*mid>=a)hi=mid;else lo=mid;
    }
    need(hi*hi>=a && (hi-1)*(hi-1)<a,"integer square root");return hi;
}
void quotient_counts(std::ostream& out){
    for(auto [v,R,k]:std::vector<std::tuple<unsigned,unsigned,unsigned>>{{4,2,2},{12,6,4},{16,8,5}}){
        std::vector<cpp_int> coefficients(k+1);coefficients[0]=1;
        for(unsigned factor=0;factor<v-R;++factor){
            unsigned weight=factor<R?2:1;
            for(unsigned j=k;j>0;--j)coefficients[j]+=weight*coefficients[j-1];
        }
        std::vector<unsigned long long> enumeration(k+1);
        for(unsigned mask=0;mask<(1u<<v);++mask){
            unsigned d=__builtin_popcount(mask);if(d>k)continue;
            bool allowed=true;
            for(unsigned j=0;j<R;++j)if((mask&(3u<<(2*j)))==(3u<<(2*j))){allowed=false;break;}
            if(allowed)++enumeration[d];
        }
        cpp_int J=0;
        for(unsigned j=0;j<=k;++j){need(coefficients[j]==enumeration[j],"complete quotient enumeration");J+=coefficients[j];}
        cpp_int domain=choose(v,k);
        cpp_int lhs=J*power(cpp_int(v)*v,R);
        cpp_int rhs=domain*(v+1)*power(cpp_int(v)*v-cpp_int(k)*k,R);
        need(lhs<=rhs,"exact rational quotient bound");
        out<<"{\"record\":\"quotient_count\",\"v\":"<<v<<",\"pairs\":"<<R<<",\"degree\":"<<k
           <<",\"homogeneous_domain\":\""<<domain<<"\",\"quotient_through_degree\":\""<<J
           <<"\",\"standard_monomials_by_degree\":[";
        for(unsigned j=0;j<=k;++j){if(j)out<<',';out<<'"'<<coefficients[j]<<'"';}
        out<<"],\"rational_bound_left\":\""<<lhs<<"\",\"rational_bound_right\":\""<<rhs
           <<"\",\"incorrect_affine_flat_dimension\":\""<<choose(v-2*R+k,k)<<"\",\"passed\":true}\n";
    }
}
void occupation_count(std::ostream& out){
    const unsigned n=2048,m=n+1,ell=11,v=m*ell,k=6,budget=n/16;
    using Table=std::vector<std::vector<cpp_int>>;
    Table dp(k+1,std::vector<cpp_int>(budget+1));dp[0][0]=1;
    for(unsigned row=0;row<m;++row){
        Table next(k+1,std::vector<cpp_int>(budget+1));
        for(unsigned j=0;j<=k;++j)for(unsigned w=0;w<=budget;++w)if(dp[j][w]!=0)
            for(unsigned d=0;d<=std::min(ell,k-j);++d){
                unsigned cost=(1u<<(2*d))-1;if(w+cost>budget)break;
                next[j+d][w+cost]+=dp[j][w]*choose(ell,d);
            }
        dp.swap(next);
    }
    std::vector<cpp_int> cap(k+1);cap[0]=1;
    for(unsigned row=0;row<m;++row){
        std::vector<cpp_int> next(k+1);
        for(unsigned j=0;j<=k;++j)for(unsigned d=0;d<=std::min(2u,k-j);++d)
            next[j+d]+=cap[j]*choose(ell,d);
        cap.swap(next);
    }
    cpp_int good=0,total=choose(v,k),sum_weight=0;
    for(const auto& a:dp[k])good+=a;
    for(unsigned s=1;s<=std::min(ell,k);++s)
        sum_weight+=m*power(cpp_int(3),s)*choose(ell,s)*choose(v-s,k-s);
    need(good>cap[k] && good<=total,"weighted space strictly contains row-cap-two fixture");
    need((total-good)*n<=16*sum_weight,"exact Markov control");
    out<<"{\"record\":\"occupation_count\",\"n\":"<<n<<",\"m\":"<<m<<",\"ell\":"<<ell<<",\"k\":"<<k
       <<",\"weight_budget\":"<<budget<<",\"total\":\""<<total<<"\",\"good\":\""<<good
       <<"\",\"row_cap_two\":\""<<cap[k]<<"\",\"sum_weight_over_all_monomials\":\""<<sum_weight
       <<"\",\"degree_weight_counts\":[";
    bool comma=false;
    for(unsigned j=0;j<=k;++j)for(unsigned w=0;w<=budget;++w)if(dp[j][w]!=0){
        if(comma)out<<',';
        comma=true;out<<'['<<j<<','<<w<<",\""<<dp[j][w]<<"\"]";
    }
    out<<"],\"scope\":\"complete truncated counting table; no common-kernel PHP instance\",\"passed\":true}\n";
}
void cube_checks(std::ostream& out){
    const unsigned n=2048;
    std::vector<std::vector<std::vector<unsigned>>> cases={{{0,1,2},{1,3,4}},{{0,2,4},{1,5},{3}}};
    for(unsigned c=0;c<cases.size();++c){
        std::vector<bool> used(n);unsigned W=0,k=0,deleted=0;
        std::vector<std::vector<unsigned>> cubes;
        for(const auto& axes:cases[c]){
            unsigned d=axes.size(),mask=0;for(unsigned a:axes)mask|=1u<<a;
            W+=(1u<<(2*d))-1;k+=d;bool found=false;
            for(unsigned base=0;base<n && !found;++base){
                if(base&mask)continue;
                std::vector<unsigned> vertices;bool free=true;
                for(unsigned s=mask;;s=(s-1)&mask){
                    unsigned z=base^s;vertices.push_back(z);free=free && !used[z];if(s==0)break;
                }
                if(free){for(unsigned z:vertices)used[z]=true;deleted+=vertices.size();cubes.push_back(vertices);found=true;}
            }
            need(found,"disjoint descending-axis cube placement");
        }
        need(W<=n/16 && k<=n/16 && deleted<=n/16,"weighted cube bounds");
        out<<"{\"record\":\"cube_packing\",\"case\":"<<c<<",\"n\":"<<n<<",\"k\":"<<k
           <<",\"weight\":"<<W<<",\"deleted_labels\":"<<deleted<<",\"axes\":[";
        for(unsigned i=0;i<cases[c].size();++i){
            if(i)out<<',';
            out<<'[';
            for(unsigned j=0;j<cases[c][i].size();++j){if(j)out<<',';out<<cases[c][i][j];}out<<']';
        }
        out<<"],\"cubes\":[";
        for(unsigned i=0;i<cubes.size();++i){
            if(i)out<<',';
            out<<'[';
            for(unsigned j=0;j<cubes[i].size();++j){if(j)out<<',';out<<cubes[i][j];}out<<']';
        }
        out<<"],\"passed\":true}\n";
    }
}
void parameters(std::ostream& out){
    for(unsigned ell:{64u,128u,256u}){
        const unsigned c=2;unsigned logell=0;while((1u<<logell)<ell)++logell;
        cpp_int n=cpp_int(1)<<ell,v=(n+1)*ell,D=cpp_int(ell)*ell;
        cpp_int H=(c+1)*ell+logell+4;
        cpp_int R=ceil_sqrt(v*H),affine_log=c*ell+2*R+3;
        cpp_int numerator=v*v*H,rounded=(numerator+R-1)/R;
        cpp_int ka=ceil_sqrt(v*affine_log),kq=ceil_sqrt(rounded),k=std::max(ka,kq);
        cpp_int T=2*k+2*R-1,B=T*D+k;
        bool rank_ok=2*R<=v,k_ok=k>=2 && 2*k<=v;
        bool space_ok=6*k<=n+1 && 192*k<=n;
        bool images_ok=k*k>=v*affine_log && R*k*k>=v*v*H;
        bool board_ok=4*B<=n;
        need(rank_ok && k_ok && space_ok && images_ok,"integer parameter premises");
        need(board_ok==(ell>=128),"positive and negative old-degree controls");
        out<<"{\"record\":\"finite_parameters\",\"ell\":"<<ell<<",\"inventory_exponent\":"<<c
           <<",\"n\":\""<<n<<"\",\"v\":\""<<v<<"\",\"D\":\""<<D<<"\",\"R\":\""<<R
           <<"\",\"k\":\""<<k<<"\",\"T\":\""<<T<<"\",\"B\":\""<<B<<"\",\"high_pair_log_bound\":\""<<H
           <<"\",\"affine_log_bound\":\""<<affine_log<<"\",\"space_and_image_conditions\":true,"
             "\"old_degree_condition\":"<<(board_ok?"true":"false")
           <<",\"branch_inventory\":\"bounded symbolically by n^2*4^R; not materialized\","
             "\"scope\":\"exact sufficient integer inequalities; no large polynomial or branch enumeration\","
             "\"passed\":true}\n";
    }
}
struct Context {
    Ring r{2,80};int old=11,count=0;
    std::vector<Polynomial> axioms;
    Context(){for(int i=0;i<old;++i){auto x=r.variable(i);axioms.push_back(r.subtract(r.power(x,2),x));}}
    void certificate(std::ostream& out,const std::string& name,const Polynomial& target,int budget,
                     const Polynomial* source=nullptr){
        std::vector<int> powers(old,2);auto red=domain_reduce(r,target,powers);
        verify_reduction(r,target,powers,red);need(red.remainder.empty(),"old Boolean certificate remainder");
        std::map<int,Polynomial> cof;
        for(int i=0;i<old;++i)if(!red.coefficients[i].empty())cof[i]=red.coefficients[i];
        out<<"{\"record\":\"NS_certificate\",\"name\":\""<<name<<"\",\"target\":";write_json(out,target);
        out<<",\"budget\":"<<budget;
        if(source){
            need(budget<=4*degree(*source)+3,"weighted source-degree ceiling");
            out<<",\"source_axiom\":";write_json(out,*source);
            out<<",\"original_degree\":"<<degree(*source)<<",\"weighted_transfer_ceiling\":"<<4*degree(*source)+3;
        }
        ns_witness::write_terms(out,r,axioms,target,cof,budget,name);out<<"}\n";++count;
    }
};
void point_json(std::ostream& out,const std::map<int,int>& point,int end){
    out<<'[';for(int i=0;i<end;++i){if(i)out<<',';out<<point.at(i);}out<<']';
}
int combined_map(std::ostream& out){
    Context c;auto& r=c.r;auto one=r.constant(1);
    auto x=[&](int i){return r.variable(i);};
    auto q0=r.multiply(r.add(x(0),x(1)),r.add(x(0),x(2)));
    auto q1=r.multiply(r.add(x(3),x(4)),r.add(x(3),x(5)));
    auto representation=r.add(r.multiply(x(3),q0),r.multiply(x(0),q1));
    std::vector<int> powers(c.old,2);auto reduction=domain_reduce(r,representation,powers);
    verify_reduction(r,representation,powers,reduction);
    auto f=reduction.remainder;need(degree(f)==3,"kernel degree");
    for(const auto& [mon,coefficient]:f){
        (void)coefficient;
        need(mon.size()==3 && std::adjacent_find(mon.begin(),mon.end())==mon.end(),"homogeneous squarefree kernel");
    }
    auto E=r.subtract(f,representation);need(!E.empty(),"nonliteral quadratic kernel membership");
    std::map<int,Polynomial> flat={{1,x(0)},{4,x(3)}};
    need(r.substitute(q0,flat).empty() && r.substitute(q1,flat).empty(),"ordinary product zero flat");
    auto wrong_literal=r.substitute(f,flat);need(!wrong_literal.empty(),"Boolean kernel is not ordinary-flat vanishing");
    auto chi00=r.multiply(r.subtract(one,x(6)),r.subtract(one,x(7)));
    auto chi11=r.multiply(x(6),x(7));
    std::vector<int> zi={0,1,2,3,4,5,8,9,10};
    std::vector<Polynomial> dense={chi11};
    for(int i:zi)dense.push_back(r.multiply(r.add(x(6),x(i)),r.add(x(7),x(i))));
    auto gamma_a=r.add(r.multiply(x(1),x(3)),r.multiply(x(2),x(3)));
    r.accumulate(gamma_a,r.multiply(x(3),x(4)));
    r.accumulate(gamma_a,r.multiply(x(3),x(5)));
    r.accumulate(gamma_a,r.multiply(x(4),x(5)));
    auto gamma_d=r.multiply(x(1),x(2));
    need(r.add(r.multiply(x(0),gamma_a),r.multiply(x(3),gamma_d))==f,"literal high-affine kernel representation");
    need(zi.size()==2*3+3,"high-affine rank threshold");
    int fresh=c.old;
    std::vector<Block> blocks;
    blocks.push_back(make_block(r,{q0,q1},1,fresh));
    blocks.push_back(make_block(r,dense,1,fresh));
    blocks.push_back(make_block(r,{dense[0],dense[1],dense[4]},1,fresh));
    std::map<int,Polynomial> phi;
    for(const auto& A:blocks)for(int id:A.variables[0])phi[id]=Polynomial{};
    phi[blocks[0].variables[0][0]]=x(3);phi[blocks[0].variables[0][1]]=x(0);
    phi[blocks[1].variables[0][0]]=chi11;
    phi[blocks[1].variables[0][1]]=r.multiply(chi00,gamma_a);
    phi[blocks[1].variables[0][4]]=r.multiply(chi00,gamma_d);
    phi[blocks[2].variables[0][0]]=chi11;
    phi[blocks[2].variables[0][1]]=chi00;
    phi[blocks[2].variables[0][2]]=r.multiply(chi00,r.subtract(one,x(0)));
    int maximum_degree=0;
    for(const auto& [id,beta]:phi){(void)id;maximum_degree=std::max(maximum_degree,degree(beta));}
    need(maximum_degree==4,"additive selector/coefficient degree");
    out<<"{\"record\":\"combined_system\",\"field\":2,\"old_variables\":11,\"source_variables\":"<<fresh
       <<",\"kernel_degree\":3,\"maximum_coefficient_degree\":4,\"high_independent_pairs\":2,"
         "\"low_parent_coordinate_dimension\":2,\"high_affine_branch_rank\":9,\"kernel\":";
    write_json(out,f);out<<",\"quadratic_kernel_cofactors\":[";write_json(out,x(3));out<<',';write_json(out,x(0));
    out<<"],\"quadratic_kernel_Boolean_residual\":";write_json(out,E);
    out<<",\"nonzero_ordinary_flat_restriction\":";write_json(out,wrong_literal);
    out<<",\"old_Boolean_axioms\":";write_polynomials(out,c.axioms);
    out<<",\"source_blocks\":[";
    for(unsigned i=0;i<blocks.size();++i){if(i)out<<',';write_block(out,blocks[i]);}
    out<<"],\"source_coefficient_domains\":[";
    for(int id=c.old;id<fresh;++id){if(id>c.old)out<<',';write_json(out,r.subtract(r.power(x(id),2),x(id)));}
    out<<"],\"simultaneous_map\":[";bool comma=false;
    for(const auto& [id,beta]:phi){if(comma)out<<',';comma=true;out<<'['<<id<<',';write_json(out,beta);out<<']';}
    out<<"],\"scope\":\"local mixed high-pair/high-affine/low-affine controls, not a full PHP parameter instance\"}\n";
    c.certificate(out,"quadratic_kernel_Boolean_residual",E,3);
    std::vector<Polynomial> unweighted;
    for(int i=0;i<c.old;++i){
        auto target=r.multiply(f,c.axioms[i]);
        c.certificate(out,"weighted_old_"+std::to_string(i),target,5,&c.axioms[i]);
    }
    for(unsigned b=0;b<blocks.size();++b){
        for(unsigned i=0;i<blocks[b].companions.size();++i){
            const auto& source=blocks[b].companions[i];need(degree(source)==5,"source companion degree");
            auto mapped=r.substitute(source,phi);unweighted.push_back(mapped);
            c.certificate(out,"weighted_companion_"+std::to_string(b)+"_"+std::to_string(i),
                          r.multiply(f,mapped),11,&source);
        }
        for(int id:blocks[b].variables[0]){
            auto source=r.subtract(r.power(x(id),2),x(id));
            c.certificate(out,"weighted_coefficient_field_"+std::to_string(id),
                          r.multiply(f,r.substitute(source,phi)),11,&source);
        }
    }
    int models=0;
    for(int bits=0;bits<(1<<c.old);++bits){
        std::map<int,int> point;
        for(int i=0;i<c.old;++i)point[i]=(bits>>i)&1;
        if(!r.evaluate(f,point))continue;
        for(const auto& [id,beta]:phi)point[id]=r.evaluate(beta,point);
        for(const auto& A:blocks){
            for(const auto& g:A.companions)need(!r.evaluate(g,point),"conditional complete source model");
            for(int id:A.variables[0])need(point[id]*point[id]-point[id]==0,"source Boolean coefficient model");
        }
        out<<"{\"record\":\"conditional_model\",\"old_point\":"<<bits<<",\"assignment\":";
        point_json(out,point,fresh);out<<"}\n";++models;
    }
    need(models==448,"complete nonzero-kernel model count");
    std::map<int,int> point;for(int i=0;i<c.old;++i)point[i]=int(i==1 || i==2);
    need(!r.evaluate(f,point) && r.evaluate(unweighted[0],point)==1,"unweighted high-pair countermodel");
    out<<"{\"record\":\"unweighted_countermodel\",\"old_point\":6,\"kernel_value\":0,"
         "\"high_pair_companion_value\":1,\"companion_image\":";write_json(out,unweighted[0]);out<<"}\n";
    need(c.count==42,"complete certificate inventory");
    out<<"{\"record\":\"combined_summary\",\"NS_certificates\":"<<c.count
       <<",\"weighted_source_images\":41,\"conditional_models\":"<<models<<",\"passed\":true}\n";
    return c.count;
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");
        out<<"{\"record\":\"schema\",\"version\":1,\"polynomials\":\"[coefficient,[variable IDs with repetitions]]\","
             "\"large_integers\":\"exact decimal strings\"}\n";
        quotient_counts(out);occupation_count(out);cube_checks(out);parameters(out);
        int count=combined_map(out);
        out<<"{\"record\":\"summary\",\"NS_certificates\":"<<count<<",\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<count<<" exact NS certificates, 448 models, and quotient/cube/parameter controls passed.\n";
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
