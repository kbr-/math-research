// Copyright (c) 2026 Kamil Braun. MIT License; see ../../LICENSE.
#include <boost/multiprecision/cpp_int.hpp>
#include <algorithm>
#include <bitset>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using boost::multiprecision::cpp_int;
using Bits=std::bitset<256>;
using Groups=std::vector<std::vector<unsigned>>;
unsigned weight(unsigned x) { return __builtin_popcount(x); }
void require(bool ok,const char* message) {
    if (!ok) throw std::runtime_error(message);
}
void integers(std::ofstream& out,const std::vector<unsigned>& a) {
    out << '[';
    for (unsigned i=0;i<a.size();++i) {if(i)out<<',';out<<a[i];}
    out << ']';
}
unsigned rank_masks(std::vector<unsigned> rows,unsigned v) {
    std::vector<unsigned> piv(v);
    unsigned rank=0;
    for (unsigned row:rows) {
        for (unsigned j=0;j<v;++j) if ((row>>j)&1) {
            if (piv[j]) row^=piv[j];
            else {piv[j]=row;++rank;break;}
        }
    }
    return rank;
}
void fixture(const std::string& label,unsigned v,const Groups& groups,
             bool disjoint,unsigned expected_min,std::ofstream& out) {
    std::vector<unsigned> A(v),all_probes,zero_points;
    for (unsigned j=0;j<v;++j) A[j]=1u<<j;
    for (unsigned j=1;j<v;++j) A[j]^=A[j-1];
    for (int j=int(v)-2;j>=0;--j) A[j]^=A[j+1];
    const unsigned c=0x25u&((1u<<v)-1);
    require(rank_masks(A,v)==v,"coordinate map not invertible");
    for (const auto& group:groups)
        all_probes.insert(all_probes.end(),group.begin(),group.end());
    out << "{\"type\":\"fixture\",\"label\":\"" << label << "\",\"v\":" << v
        << ",\"affine_rows\":";
    integers(out,A);
    out << ",\"affine_constant_mask\":" << c << ",\"groups_in_u_coordinates\":[";
    for (unsigned j=0;j<groups.size();++j) {if(j)out<<',';integers(out,groups[j]);}
    out << "],\"joint_rank\":" << rank_masks(all_probes,v) << ",\"pair_ranks\":[";
    bool first=true;
    for (unsigned a=0;a<groups.size();++a) for (unsigned b=a+1;b<groups.size();++b) {
        auto rows=groups[a];rows.insert(rows.end(),groups[b].begin(),groups[b].end());
        if(!first)out<<',';
        first=false;
        const unsigned pair_rank=rank_masks(rows,v);
        if(!disjoint)require(pair_rank==4,"control does not have pairwise independence");
        out<<pair_rank;
    }
    auto coordinates=[&](unsigned x) {
        unsigned u=c;
        for (unsigned j=0;j<v;++j) u^=(weight(A[j]&x)&1u)<<j;
        return u;
    };
    for (unsigned x=0;x<(1u<<v);++x) {
        const unsigned u=coordinates(x);
        for (const auto& group:groups) {
            bool zero=true;
            for (unsigned probe:group) zero &= (weight(probe&u)%2==0);
            if (zero) {zero_points.push_back(x);break;}
        }
    }
    out << "],\"union_zero_points\":";integers(out,zero_points);out<<"}\n";
    unsigned minimum=v+1,degree_cases=0,null_vectors=0;
    for (unsigned k=0;k<=v;++k) {
        std::vector<unsigned> features;
        for (unsigned m=0;m<(1u<<v);++m) if(weight(m)<=k)features.push_back(m);
        std::vector<Bits> original,pivot(features.size()),witness(features.size());
        std::vector<bool> used(features.size(),false);
        unsigned rank=0;
        for (unsigned x:zero_points) {
            Bits row,proof;
            for(unsigned j=0;j<features.size();++j)
                if((features[j]&x)==features[j])row.set(j);
            proof.set(original.size());original.push_back(row);
            for(unsigned j=0;j<features.size();++j) if(row[j]) {
                if(used[j]) {row^=pivot[j];proof^=witness[j];}
                else {used[j]=true;pivot[j]=row;witness[j]=proof;++rank;break;}
            }
        }
        std::vector<Bits> kernel;
        for(unsigned free=0;free<features.size();++free) if(!used[free]) {
            Bits x;x.set(free);
            for(int j=int(features.size())-1;j>=0;--j)
                if(used[j] && (pivot[j]&x).count()%2)x.flip(j);
            for(const auto& row:original)require((row&x).count()%2==0,"invalid kernel vector");
            kernel.push_back(x);
        }
        for(unsigned j=0;j<features.size();++j) if(used[j]) {
            Bits check;
            for(unsigned q=0;q<original.size();++q)if(witness[j][q])check^=original[q];
            require(check==pivot[j],"invalid pivot witness");
        }
        unsigned predicted=0;
        if(disjoint) {
            for(unsigned m=0;m<(1u<<v);++m) if(weight(m)<=k) {
                bool meets=true;
                for(const auto& group:groups) {
                    unsigned mask=0;for(unsigned probe:group)mask|=probe;
                    meets &= (m&mask)!=0;
                }
                predicted+=meets;
            }
            require(kernel.size()==predicted,"wrong disjoint-group dimension");
        }
        if(!kernel.empty())minimum=std::min(minimum,k);
        if(!disjoint && k==2)require(kernel.size()==1,"determinant control dimension");
        ++degree_cases;null_vectors+=kernel.size();
        out << "{\"type\":\"degree\",\"label\":\"" << label << "\",\"k\":" << k
            << ",\"features\":";integers(out,features);
        out << ",\"rank\":" << rank << ",\"kernel_dimension\":" << kernel.size();
        if(disjoint)out<<",\"predicted_dimension\":"<<predicted;
        out << ",\"pivots\":[";
        bool first_pivot=true;
        for(unsigned j=0;j<features.size();++j)if(used[j]) {
            if(!first_pivot)out<<',';
            first_pivot=false;
            out<<"{\"column\":"<<j<<",\"row\":\""<<pivot[j]
               <<"\",\"origin_combination\":\""<<witness[j]<<"\"}";
        }
        out << "],\"kernel_basis\":[";
        for(unsigned j=0;j<kernel.size();++j) {if(j)out<<',';out<<'"'<<kernel[j]<<'"';}
        out<<"]}\n";
    }
    require(minimum==expected_min,"wrong first nonzero degree");
    out << "{\"type\":\"fixture_summary\",\"label\":\"" << label
        << "\",\"first_nonzero_degree\":" << minimum << ",\"degree_cases\":" << degree_cases
        << ",\"verified_kernel_vectors\":" << null_vectors << "}\n";
    std::cout << label << ": first degree " << minimum << ", " << degree_cases
              << " degree spaces, " << null_vectors << " verified kernel vectors.\n";
}

cpp_int binom(unsigned n,unsigned k) {
    if(k>n)return 0;
    k=std::min(k,n-k);
    cpp_int a=1;
    for(unsigned j=1;j<=k;++j)a=a*(n-j+1)/j;
    return a;
}
unsigned logceil(unsigned n) {
    unsigned L=0,power=1;
    while(power<n){power*=2;++L;}
    return L;
}
void uniform_bound(unsigned n,unsigned lower,bool expected,std::ofstream& out) {
    const unsigned common_power=n*n-1;
    cpp_int sum=0;
    for(unsigned N=lower;N<=n;++N) {
        const unsigned r=N/2+1,power=N*N-1;
        const cpp_int numerator=binom(n+1,N+1)*binom(n,N)*
                                ((cpp_int(1)<<(r*r))-1);
        sum+=numerator<<(common_power-power);
        out << "{\"type\":\"joint_union_term\",\"n\":"<<n<<",\"lower\":"<<lower
            <<",\"N\":"<<N<<",\"r\":"<<r<<",\"blocks\":"<<r
            <<",\"joint_input_rows\":"<<r*r<<",\"numerator\":\""<<numerator
            <<"\",\"denominator_power\":"<<power<<"}\n";
    }
    const cpp_int denominator=cpp_int(1)<<common_power;
    const bool passes=sum<denominator;
    require(passes==expected,"unexpected uniform union-bound control");
    out<<"{\"type\":\"joint_union_sum\",\"n\":"<<n<<",\"lower\":"<<lower
       <<",\"numerator\":\""<<sum<<"\",\"denominator\":\""<<denominator
       <<"\",\"below_one\":"<<(passes?"true":"false")<<"}\n";
    std::cout<<"Joint stack n="<<n<<" N_min="<<lower<<" union_below_one="<<passes<<'\n';
    if(!expected)return;
    const unsigned h=logceil(n+1),D=2*h+1;
    unsigned boards=0;
    for(unsigned N=2*D;N<=n;++N) {
        const unsigned r=N/2+1,T=std::max(1u,(r+h-1)/h-1);
        const unsigned old_bound=std::min(D+r,T*D),learning=(r-1)*D+r;
        require(2*r>N && 2*old_bound>N && 2*learning>N,"unexpected affordable degree");
        ++boards;
        out<<"{\"type\":\"joint_board_budget\",\"n\":"<<n<<",\"N\":"<<N
           <<",\"h\":"<<h<<",\"D\":"<<D<<",\"rank_and_blocks\":"<<r
           <<",\"joint_rank\":"<<r*r<<",\"first_common_degree\":"<<r
           <<",\"old_optimized_bound\":"<<old_bound
           <<",\"first_learning_ceiling\":"<<learning
           <<",\"target\":"<<N/2<<"}\n";
    }
    std::cout<<"Joint stack n="<<n<<": "<<boards<<" usable-board budgets verified.\n";
}
int main(int argc,char** argv) {
    try {
        require(argc==3 && std::string(argv[1])=="--out",
                "usage: check_common_vanishing_degree --out NEW.jsonl");
        std::ifstream existing(argv[2]);
        require(!existing.good(),"output already exists");
        std::ofstream out(argv[2]);
        require(bool(out),"cannot open output");
        out<<"{\"type\":\"schema\",\"version\":1,\"field\":2,"
             "\"bits\":\"256 characters, index zero at the right\","
             "\"feature_order\":\"increasing old-variable monomial mask\","
             "\"witness_order\":\"union_zero_points\","
             "\"large_integers\":\"decimal strings\",\"randomness\":\"none\"}\n";
        fixture("three_independent_pairs",6,{{1,2},{4,8},{16,32}},true,3,out);
        fixture("three_pairs_two_free_coordinates",8,{{1,2},{4,8},{16,32}},true,3,out);
        fixture("four_independent_pairs",8,{{1,2},{4,8},{16,32},{64,128}},true,4,out);
        fixture("pairwise_independent_jointly_dependent",4,{{1,2},{4,8},{5,10}},false,2,out);
        for(unsigned n:{64u,128u})uniform_bound(n,4*logceil(n+1),true,out);
        uniform_bound(64,8,false,out);
        out.close();
        require(bool(out),"output write failed");
        return 0;
    } catch(const std::exception& e) {
        std::cerr<<e.what()<<'\n';return 1;
    }
}
