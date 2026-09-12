// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact coefficient checks for small-slice reconstruction; no cubic-rank solver.
#include "pc_boundary.hpp"
#include <cstdint>
using namespace boundary_pc;
using Slice=std::pair<int,int>;

std::uint64_t choose_exact(int n,int k) {
    if(k<0 || n<0 || k>n)return 0;
    k=std::min(k,n-k);need(n<=60 && k<=10,"binomial integer guard");
    std::uint64_t value=1;
    for(int i=1;i<=k;i++)value=value*std::uint64_t(n-k+i)/std::uint64_t(i);
    return value;
}
int reconstruct(int n,int p,const std::vector<Slice>& slices,std::vector<int> support) {
    if(std::find(support.begin(),support.end(),0)!=support.end())return 0;
    std::sort(support.begin(),support.end());
    support.erase(std::unique(support.begin(),support.end()),support.end());
    int r=int(support.size()),value=0;
    for(auto [k,weight]:slices)
        value=(value+weight*int(choose_exact(n-1-r,k-r)%p))%p;
    return value;
}
void support_json(std::ostream& out,const std::vector<int>& support) {
    out<<'[';
    for(size_t i=0;i<support.size();i++){if(i)out<<',';out<<support[i];}
    out<<']';
}
struct SliceCounts {int cases=0,monomials=0,residuals=0,controls=0;};
void reconstruction_case(std::ostream& out,SliceCounts& count,int n,int p) {
    need(n%p==0 && n>=3,"divisibility hypothesis");
    int parity=int(choose_exact(n-1,3)%2);
    std::vector<Slice> slices=p==2?std::vector<Slice>{{1,1+parity},{3,1}}
                                      :std::vector<Slice>{{p-1,1}};
    for(auto& slice:slices)slice.second%=p;
    const std::string name="n"+std::to_string(n)+"_F"+std::to_string(p);
    out<<"{\"record\":\"reconstruction\",\"case\":\""<<name<<"\",\"n\":"<<n<<",\"p\":"<<p
       <<",\"target\":\"z_0=0; z_j=1 for j>=1\",\"slice_family\":\"all K-subsets of {1,...,n-1}\","
         "\"polynomial_degree\":2,\"row_average_denominator\":"<<(n+1)%p<<",\"slices\":[";
    bool comma=false;
    for(auto [k,weight]:slices) {
        if(comma)out<<',';
        comma=true;
        int N=n/k-1;
        need((k+1)%p==0,"invalid copy congruence");
        if(weight){need(N>=5,"residual board does not exclude PC degree three");count.residuals++;}
        out<<"{\"K\":"<<k<<",\"weight\":"<<weight<<",\"subset_count\":"<<choose_exact(n-1,k)
           <<",\"residual_holes\":"<<N<<'}';
    }
    out<<"]}\n";
    auto test=[&](std::vector<int> support) {
        int target=std::find(support.begin(),support.end(),0)==support.end()?1:0;
        int value=reconstruct(n,p,slices,support);need(value==target,"quadratic reconstruction");
        out<<"{\"record\":\"monomial_check\",\"case\":\""<<name<<"\",\"variable_factors\":";
        support_json(out,support);out<<",\"target_value\":"<<target<<",\"weighted_slice_value\":"<<value<<"}\n";
        count.monomials++;
    };
    test({});for(int i=0;i<n;i++)test({i});
    for(int i=0;i<n;i++)for(int j=i;j<n;j++)test({i,j});
    count.cases++;
}
void negative_control(std::ostream& out,SliceCounts& count,const std::string& name,
                      int n,int p,const std::vector<Slice>& slices,const std::vector<int>& support) {
    int value=reconstruct(n,p,slices,support);
    int target=std::find(support.begin(),support.end(),0)==support.end()?1:0;
    need(value!=target,"negative control did not separate");
    out<<"{\"record\":\"negative_control\",\"name\":\""<<name<<"\",\"n\":"<<n<<",\"p\":"<<p
       <<",\"slices\":[";
    for(size_t i=0;i<slices.size();i++){if(i)out<<',';out<<'['<<slices[i].first<<','<<slices[i].second<<']';}
    out<<"],\"variable_factors\":";support_json(out,support);
    out<<",\"target_value\":"<<target<<",\"weighted_slice_value\":"<<value<<"}\n";count.controls++;
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","usage: check_occupancy_slice_reconstruction --out NEW-PATH.jsonl");
        std::filesystem::path path(argv[2]);need(!std::filesystem::exists(path),"output already exists");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot open output");SliceCounts count;
        for(auto [n,p]:std::vector<std::pair<int,int>>{{18,2},{20,2},{12,3},{15,3},{25,5},{42,7}})
            reconstruction_case(out,count,n,p);
        negative_control(out,count,"omit binary singleton correction",18,2,{{3,1}},{});
        negative_control(out,count,"singletons cannot reconstruct quadratic terms",18,2,{{1,1}},{1,2});
        negative_control(out,count,"wrong target congruence",13,3,{{2,1}},{});
        negative_control(out,count,"quadratic ceiling is substantive in F3",12,3,{{2,1}},{1,2,3});
        out<<"{\"record\":\"summary\",\"cases\":"<<count.cases<<",\"ordinary_monomial_checks\":"<<count.monomials
           <<",\"active_residual_bounds\":"<<count.residuals<<",\"controls\":"<<count.controls<<",\"verified\":true}\n";
        out.close();need(bool(out),"failed writing output");
        std::cout<<"Verified "<<count.monomials<<" monomial identities, "<<count.residuals
                 <<" residual-board bounds, and "<<count.controls<<" controls.\n";
    } catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
