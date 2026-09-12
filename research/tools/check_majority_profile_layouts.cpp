// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact combinatorial layouts; original base certificates use the universal copy theorem.
#include "pc_boundary.hpp"
#include <cstdint>
#include <random>
using namespace boundary_pc;
using Matrix=std::vector<std::uint8_t>;

void majority_list(std::ostream& out,const std::vector<int>& values) {
    out<<'[';for(size_t i=0;i<values.size();i++){if(i)out<<',';out<<values[i];}out<<']';
}
std::pair<int,int> minimum_degrees(const Matrix& a,int k) {
    std::vector<int> columns(k);int row_min=k;
    for(int i=0;i<k;i++) {
        int sum=0;for(int j=0;j<k;j++){sum+=a[i*k+j];columns[j]+=a[i*k+j];}
        row_min=std::min(row_min,sum);
    }
    return {row_min,*std::min_element(columns.begin(),columns.end())};
}
std::vector<int> short_matching(const Matrix& a,int k,int& rewires) {
    // Caller verifies both minimum degrees exceed k/2.
    std::vector<int> match(k,-1),owner(k,-1);
    for(int i=0;i<k;i++) {
        for(int j=0;j<k;j++)if(owner[j]<0 && a[i*k+j]) {
            match[i]=j;owner[j]=i;break;
        }
        if(match[i]>=0)continue;
        int free=-1;for(int j=0;j<k;j++)if(owner[j]<0){free=j;break;}
        need(free>=0,"no free matching column");
        for(int j=0;j<k;j++)if(a[i*k+j] && owner[j]>=0 && a[owner[j]*k+free]) {
            int previous=owner[j];owner[free]=previous;match[previous]=free;
            owner[j]=i;match[i]=j;rewires++;break;
        }
        need(match[i]>=0,"no short augmenting path");
    }
    std::vector<int> seen(k);
    for(int i=0;i<k;i++) {
        need(match[i]>=0 && match[i]<k && a[i*k+match[i]],"invalid matching edge");
        seen[match[i]]++;
    }
    for(int value:seen)need(value==1,"matching is not bijective");
    return match;
}
std::uint64_t below(std::mt19937_64& rng,std::uint64_t bound) {
    need(bound>0,"empty random range");
    const std::uint64_t threshold=(std::uint64_t(0)-bound)%bound;
    std::uint64_t x;do{x=rng();}while(x<threshold);return x%bound;
}
void exact_shuffle(std::vector<int>& values,std::mt19937_64& rng) {
    for(size_t i=values.size();i>1;i--)std::swap(values[i-1],values[size_t(below(rng,i))]);
}
void rational_bound(std::ostream& out,int n,int k) {
    // epsilon=1/4: 2*n^2*(15/16)^floor(k/2) < 1, checked as positive integers.
    need(n<=20000 && k<=1024,"fixture resource/integer guard");
    std::vector<std::uint32_t> numerator{std::uint32_t(2*n*n)};
    int exponent=k/2;
    for(int step=0;step<exponent;step++) {
        std::uint64_t carry=0;
        for(auto& word:numerator) {
            std::uint64_t value=std::uint64_t(word)*15+carry;
            word=std::uint32_t(value);carry=value>>32;
        }
        if(carry)numerator.push_back(std::uint32_t(carry));
    }
    int high_bits=0;for(auto top=numerator.back();top;top>>=1)high_bits++;
    int bits=32*(int(numerator.size())-1)+high_bits,denominator_bits=4*exponent;
    need(bits<=denominator_bits,"rational union bound is not strictly below one");
    out<<"{\"record\":\"exact_union_bound\",\"n\":"<<n<<",\"K\":"<<k
       <<",\"epsilon\":[1,4],\"formula\":\"2*n^2*(15/16)^floor(K/2)\","
         "\"numerator_base_2_32_little_endian\":[";
    for(size_t i=0;i<numerator.size();i++){if(i)out<<',';out<<numerator[i];}
    out<<"],\"denominator_power_of_two\":"<<denominator_bits
       <<",\"numerator_bit_length\":"<<bits<<",\"strictly_below_one\":true}\n";
}
struct MajorityCounts {int profiles=0,degree_blocks=0,matchings=0,matched_edges=0,small_graphs=0,controls=0,rewires=0;};
void small_controls(std::ostream& out,MajorityCounts& count) {
    constexpr int k=4;Matrix a(k*k);
    for(unsigned mask=0;mask<(1u<<(k*k));mask++) {
        for(int i=0;i<k*k;i++)a[i]=std::uint8_t((mask>>i)&1u);
        auto [left,right]=minimum_degrees(a,k);
        if(2*left<=k || 2*right<=k)continue;
        int rewires=0;auto match=short_matching(a,k,rewires);
        out<<"{\"record\":\"small_graph_matching\",\"K\":4,\"row_major_edge_mask\":"<<mask<<",\"matching\":";
        majority_list(out,match);out<<",\"short_rewirings\":"<<rewires<<"}\n";count.small_graphs++;
    }
    need(count.small_graphs==209,"exhaustive four-by-four graph count");
    for(int type=0;type<3;type++) {
        int size=type==2?5:4;Matrix graph(size*size);std::vector<int> subset;
        for(int i=0;i<size;i++)for(int j=0;j<size;j++)
            graph[i*size+j]=std::uint8_t(type==0?j<3:(type==1?i<3:((i<2)==(j<3))));
        if(type==0)subset={0,1,2,3};
        else if(type==1)subset={3};
        else subset={2,3,4};
        std::vector<int> neighbors;
        for(int j=0;j<size;j++) {
            bool hit=false;for(int i:subset)hit=hit || graph[i*size+j];
            if(hit)neighbors.push_back(j);
        }
        need(neighbors.size()<subset.size(),"Hall control is not deficient");
        auto [left,right]=minimum_degrees(graph,size);
        out<<"{\"record\":\"Hall_control\",\"type\":"<<type<<",\"K\":"<<size
           <<",\"minimum_left_degree\":"<<left<<",\"minimum_right_degree\":"<<right<<",\"matrix\":[";
        for(size_t i=0;i<graph.size();i++){if(i)out<<',';out<<int(graph[i]);}
        out<<"],\"left_subset\":";majority_list(out,subset);out<<",\"neighbors\":";
        majority_list(out,neighbors);out<<"}\n";count.controls++;
    }
}
void profile_case(std::ostream& out,MajorityCounts& count,int p,int k) {
    constexpr int n=6000,quota=4500;int r=n%k,M=n-r,groups=M/k,N=groups-1;
    need((k+1)%p==0 && k<=n/8 && N>=3,"projection parameters");
    need(8*(quota-r)>=5*M,"post-prefix majority bound");
    rational_bound(out,n,k);
    std::uint64_t seed=202609120062ULL+std::uint64_t(p);
    std::mt19937_64 rng(seed);std::vector<int> rows,columns;
    for(int i=r;i<n;i++){rows.push_back(i);columns.push_back(i);}
    exact_shuffle(rows,rng);exact_shuffle(columns,rng);
    for(const auto* order:{&rows,&columns}) {
        std::vector<int> seen(n);
        for(int value:*order){need(value>=r && value<n,"group member outside remaining board");seen[value]++;}
        for(int i=r;i<n;i++)need(seen[i]==1,"group order is not a permutation");
    }
    const std::string name="cyclic_n6000_F"+std::to_string(p)+"_K"+std::to_string(k);
    out<<"{\"record\":\"profile_layout\",\"case\":\""<<name<<"\",\"p\":"<<p<<",\"n\":"<<n
       <<",\"distinguished_pigeon\":6000,\"ordinary_pigeons\":\"0 through 5999\","
         "\"distinguished_class\":\"{6000} union {i: (i-j mod 6000)<4500} in source column j\","
         "\"other_class\":\"complement of distinguished_class\","
         "\"raw_minimum_degree_both_sides\":4500,\"epsilon\":[1,4],\"K\":"<<k
       <<",\"matching_prefix\":"<<r<<",\"prefix_rule\":\"row i matched to column i for 0<=i<r\","
         "\"remaining_side\":"<<M<<",\"post_prefix_degree_lower_bound\":"<<quota-r
       <<",\"residual_holes\":"<<N<<",\"seed\":"<<seed
       <<",\"shuffle\":\"mt19937_64, rejection-sampled Fisher-Yates, rows then columns\","
         "\"group_rule\":\"consecutive groups of K in each saved order\","
         "\"empty_column_group\":0,\"row_order\":";
    majority_list(out,rows);out<<",\"column_order\":";majority_list(out,columns);out<<"}\n";
    Matrix graph(size_t(k)*k);int case_rewires=0,minimum=k;
    for(int a=0;a<groups;a++)for(int b=0;b<groups;b++) {
        for(int d=0;d<k;d++)for(int c=0;c<k;c++) {
            int difference=rows[a*k+d]-columns[b*k+c];if(difference<0)difference+=n;
            graph[d*k+c]=std::uint8_t(difference<quota);
        }
        auto [left,right]=minimum_degrees(graph,k);
        need(2*left>k && 2*right>k,"sampled group fails the majority event");
        minimum=std::min(minimum,std::min(left,right));count.degree_blocks++;
        out<<"{\"record\":\"group_degrees\",\"case\":\""<<name<<"\",\"row_group\":"<<a
           <<",\"column_group\":"<<b<<",\"minimum_left_degree\":"<<left
           <<",\"minimum_right_degree\":"<<right<<"}\n";
        if(b==0)continue;
        int rewires=0;auto match=short_matching(graph,k,rewires);case_rewires+=rewires;
        out<<"{\"record\":\"copy_permutation\",\"case\":\""<<name<<"\",\"residual_row\":"<<a
           <<",\"residual_column\":"<<b-1<<",\"left_copy_to_column_position\":";
        majority_list(out,match);out<<",\"short_rewirings\":"<<rewires<<"}\n";
        count.matchings++;count.matched_edges+=k;
    }
    out<<"{\"record\":\"map_blueprint\",\"case\":\""<<name
       <<"\",\"ordinary_cell_rule\":\"row_order[a*K+d] maps to y_(a,j) only in column_order[(j+1)*K+pi_(a,j)(d)]; other unmatched cells zero\","
         "\"distinguished_row_rule\":\"q_j=1-sum_a y_(a,j) in every column of group j+1; zero in empty group\","
         "\"prefix_images\":\"matched diagonal cells one, other cells in those rows/columns zero\","
         "\"local_statistic_images\":\"distinguished-class sum one outside empty group, zero on empty group; complementary class sum zero everywhere\","
         "\"validation_scope\":\"complete combinatorial layout and edge checks; universal base-image certificates imported from the notebook theorem\","
         "\"minimum_sampled_degree\":"<<minimum<<",\"short_rewirings\":"<<case_rewires<<",\"verified\":true}\n";
    count.rewires+=case_rewires;count.profiles++;
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","usage: check_majority_profile_layouts --out NEW-PATH.jsonl");
        std::filesystem::path path(argv[2]);need(!std::filesystem::exists(path),"output already exists");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot open output");MajorityCounts count;
        small_controls(out,count);profile_case(out,count,2,613);profile_case(out,count,3,614);
        need(count.degree_blocks==162 && count.matchings==144 && count.matched_edges==88344,"layout totals");
        out<<"{\"record\":\"summary\",\"profiles\":"<<count.profiles<<",\"local_degree_checks\":"<<count.degree_blocks
           <<",\"perfect_matchings\":"<<count.matchings<<",\"matched_edges\":"<<count.matched_edges
           <<",\"exhaustive_small_graphs\":"<<count.small_graphs<<",\"Hall_controls\":"<<count.controls
           <<",\"large_layout_short_rewirings\":"<<count.rewires<<",\"verified\":true}\n";
        out.close();need(bool(out),"failed writing output");
        std::cout<<"Verified two 6000-column layouts, "<<count.matchings<<" perfect matchings ("
                 <<count.matched_edges<<" edges), "<<count.small_graphs<<" exhaustive small graphs, and exact union bounds.\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
