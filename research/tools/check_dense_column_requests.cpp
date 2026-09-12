// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// One deterministic mixed occupied/empty witness fixture; no Monte Carlo claim.
#include "pc_boundary.hpp"
#include <cstdint>
#include <numeric>
using namespace boundary_pc;

void integer_list(std::ostream& out,const std::vector<int>& values) {
    out<<'[';
    for(size_t i=0;i<values.size();i++){if(i)out<<',';out<<values[i];}
    out<<']';
}
bool contains(const std::vector<int>& values,int value) {
    return std::find(values.begin(),values.end(),value)!=values.end();
}
std::array<bool,2> occupied_hits(const std::vector<int>& columns) {
    std::array<bool,2> hit{};
    for(size_t i=0;i<columns.size();i++)hit[(int(i)+columns[i])%2]=true;
    return hit;
}
std::array<bool,2> empty_hits(const std::vector<int>& columns) {
    std::array<bool,2> hit{};for(int j:columns)hit[j%2]=true;return hit;
}
void candidate(std::ostream& out,const std::string& kind,
               const std::vector<int>& columns,const std::array<bool,2>& hits) {
    out<<"{\"record\":\"candidate\",\"kind\":\""<<kind<<"\",\"columns\":";
    integer_list(out,columns);
    out<<",\"covered_blocks\":["<<hits[0]<<','<<hits[1]<<"]}\n";
}

int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out",
             "usage: check_dense_column_requests --out NEW-PATH.jsonl");
        std::filesystem::path path(argv[2]);
        need(!std::filesystem::exists(path),"output already exists");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot open output");
        constexpr int p=2,n=24,q=3,K=5,N=3,m=n+1;
        const Poly zero(p),one(p,1);
        need((K+1)%p==0 && (n-q)/K-1==N && n-q>=2*K,"board parameters");
        need(q<=n/8 && q<=n/4,"density size conditions");
        // epsilon=eta=1/2; eta' >= (12-3)/21=3/7.
        constexpr std::uint64_t occupied_num=2*27,occupied_den=64;
        constexpr std::uint64_t empty_num=2*1024,empty_den=16807;
        need(occupied_num<occupied_den && empty_num<empty_den,"union bounds");
        out<<"{\"record\":\"parameters\",\"prime\":2,\"holes\":24,\"rows\":25,"
               "\"occupied_blocks\":2,\"empty_blocks\":2,\"epsilon\":[1,2],\"eta\":[1,2],"
               "\"matching_size\":3,\"copies\":5,\"remaining_empty_density_lower\":[3,7],"
               "\"occupied_failure_bound\":[54,64],\"empty_failure_bound\":[2048,16807],"
               "\"residual_holes\":3,\"selection\":\"deterministic fixture, not random sampling\","
               "\"occupied_edges\":\"block b has (row+column) mod 2 = b\","
               "\"empty_columns\":\"block b has column mod 2 = b\","
               "\"indices\":\"zero based\",\"polynomial_variables\":\"y_i_j at index 3*i+j\"}\n";
        for(int b=0;b<2;b++) {
            int edges=0,columns=0;
            for(int i=0;i<m;i++)for(int j=0;j<n;j++)edges+=((i+j)%2==b);
            for(int j=0;j<n;j++)columns+=(j%2==b);
            need(edges==300 && columns==12,"source densities");
            out<<"{\"record\":\"density\",\"block_parity\":"<<b
               <<",\"occupied_edges\":"<<edges<<",\"empty_columns\":"<<columns<<"}\n";
        }
        std::vector<int> matched_columns;int attempts=0;
        for(int a=0;a<n && matched_columns.empty();a++)
            for(int b=0;b<n && matched_columns.empty();b++)if(b!=a)
                for(int c=0;c<n && matched_columns.empty();c++)if(c!=a && c!=b) {
                    std::vector<int> cols={a,b,c};auto hit=occupied_hits(cols);
                    candidate(out,"ordered matching on rows 0,1,2",cols,hit);attempts++;
                    if(hit[0] && hit[1])matched_columns=cols;
                }
        need(matched_columns==std::vector<int>({0,1,3}) && attempts==2,"matching fixture");
        std::vector<int> empty_columns={2,4,5,6,7},bad_empty={2,4,6,8,10};
        auto hit=empty_hits(empty_columns),miss=empty_hits(bad_empty);
        candidate(out,"chosen empty set",empty_columns,hit);
        candidate(out,"missed odd-column witness control",bad_empty,miss);
        need(hit[0] && hit[1] && miss[0] && !miss[1],"empty-set coverage control");
        for(int j:empty_columns)need(!contains(matched_columns,j),"empty/matched overlap");
        for(int b=0;b<2;b++) {
            int surviving=0;
            for(int j=0;j<n;j++)surviving+=(j%2==b && !contains(matched_columns,j));
            need(surviving>=9,"remaining empty density");
            out<<"{\"record\":\"surviving_empty_columns\",\"parity\":"<<b
               <<",\"count\":"<<surviving<<",\"board_columns\":21}\n";
        }
        const int prefix=(n-q)%K;
        need(prefix==1,"freezing matching prefix");
        for(int j=0;j<n && int(matched_columns.size())<q+prefix;j++)
            if(!contains(matched_columns,j) && !contains(empty_columns,j))matched_columns.push_back(j);
        std::vector<int> copied_columns;
        for(int j=0;j<n;j++)
            if(!contains(matched_columns,j) && !contains(empty_columns,j))copied_columns.push_back(j);
        need(matched_columns==std::vector<int>({0,1,3,8}) && int(copied_columns.size())==K*N,
             "full source layout");
        std::vector<std::vector<Poly>> cells(m,std::vector<Poly>(n,zero));
        for(int i=0;i<q+prefix;i++)cells[i][matched_columns[i]]=one;
        std::vector<Poly> empty;
        for(int j=0;j<N;j++) {
            Poly v=one;for(int i=0;i<=N;i++)v=v-variable(p,i*N+j);empty.push_back(v);
        }
        for(int copy=0;copy<K;copy++)for(int j=0;j<N;j++) {
            int source_column=copied_columns[copy*N+j];
            for(int i=0;i<=N;i++)cells[q+prefix+copy*(N+1)+i][source_column]=variable(p,i*N+j);
            cells[m-1][source_column]=empty[j];
        }
        out<<"{\"record\":\"layout\",\"matched_rows\":[0,1,2,3],\"matched_columns\":";
        integer_list(out,matched_columns);out<<",\"empty_columns\":";integer_list(out,empty_columns);
        out<<",\"copied_columns\":";integer_list(out,copied_columns);
        out<<",\"copied_rows\":\"4+4*copy+i, 0<=copy<5, 0<=i<4\",\"dummy_row\":24}\n";
        std::vector<Poly> sums(n,zero);
        for(int i=0;i<m;i++)for(int j=0;j<n;j++) {
            need(cells[i][j].deg()<=1,"nonaffine cell image");sums[j]=sums[j]+cells[i][j];
            out<<"{\"record\":\"cell_image\",\"row\":"<<i<<",\"column\":"<<j<<",\"image\":";
            jsonpoly(out,cells[i][j]);out<<"}\n";
        }
        for(int j=0;j<n;j++)need(sums[j]==(contains(empty_columns,j)?zero:one),"column sum image");
        const int extra_row=4,extra_column=9;
        const Poly extra=cells[extra_row][extra_column];
        need(extra==variable(p,0),"label-sensitive extra control");
        int input_count=0,nonconstant_extras=0;std::vector<int> chosen_inputs,chosen_values;
        std::vector<int> levels={1,1,2,3};
        for(int b=0;b<4;b++) {
            std::vector<Poly> images;std::vector<int> degrees,columns;
            for(int j=0;j<n;j++) {
                if(b>=2 && j%2!=b-2)continue;
                Poly g= b<2 ? zero : one-sums[j];
                std::vector<int> source_rows;
                if(b<2)for(int i=0;i<m;i++)if((i+j)%2==b) {
                    source_rows.push_back(i);g=g+cells[i][j];
                }
                out<<"{\"record\":\"input_image\",\"block\":"<<b<<",\"index\":"<<images.size()
                   <<",\"source_column\":"<<j<<",\"source_kind\":\""
                   <<(b<2?"sum of listed cells":"one minus full column sum")<<"\",\"source_rows\":";
                integer_list(out,source_rows);out<<",\"source_degree\":1,\"image\":";jsonpoly(out,g);
                out<<"}\n";images.push_back(g);degrees.push_back(1);columns.push_back(j);
            }
            int dependency=b<2?-1:(b==2?0:2);
            if(dependency>=0)need(levels[dependency]<levels[b] && chosen_values[dependency]==1,
                                 "strictly earlier coefficient image");
            out<<"{\"record\":\"input_image\",\"block\":"<<b<<",\"index\":"<<images.size()
               <<",\"source_kind\":\"cell times optional earlier chosen coefficient\","
                 "\"source_cell\":[4,9],\"earlier_block\":"<<dependency<<",\"earlier_input\":"
               <<(dependency<0?-1:chosen_inputs[dependency])<<",\"source_degree\":"<<(b<2?1:2)
               <<",\"image\":";jsonpoly(out,extra);out<<"}\n";
            images.push_back(extra);degrees.push_back(b<2?1:2);nonconstant_extras++;
            int chosen=-1;
            for(size_t i=0;i+1<images.size();i++)if(images[i]==one){chosen=int(i);break;}
            need(chosen>=0,"missing literal nonzero designated input");
            std::vector<int> coefficients(images.size(),0);coefficients[chosen]=1;
            Poly product=one;
            for(size_t i=0;i<images.size();i++)product=product-Poly(p,coefficients[i])*images[i];
            need(product==zero,"nonzero product image");
            int delta=*std::max_element(degrees.begin(),degrees.end());
            std::vector<int> companion_degrees;
            for(size_t i=0;i<images.size();i++) {
                need((images[i]*product)==zero,"nonzero companion image");
                need(powp(Poly(p,coefficients[i]),p)-Poly(p,coefficients[i])==zero,"field image");
                companion_degrees.push_back(degrees[i]+delta+1);
            }
            out<<"{\"record\":\"normalized_block\",\"index\":"<<b<<",\"level\":"<<levels[b]
               <<",\"accuracy\":1,\"source_product\":\"1-sum_i r_block_i*g_block_i\","
                 "\"chosen_input\":"<<chosen<<",\"chosen_source_column\":"<<columns[chosen]
               <<",\"coefficient_images\":";integer_list(out,coefficients);
            out<<",\"original_companion_degrees\":";integer_list(out,companion_degrees);
            out<<",\"product_image\":[],\"all_companion_images_zero\":true,"
                 "\"all_coefficient_field_images_zero\":true,\"nonconstant_extra_image\":";
            jsonpoly(out,extra);out<<"}\n";
            chosen_inputs.push_back(chosen);chosen_values.push_back(coefficients[chosen]);
            input_count+=int(images.size());
        }
        need(input_count==76 && nonconstant_extras==4,"complete fixture counts");
        out<<"{\"record\":\"summary\",\"cell_images\":600,\"column_sum_checks\":24,"
               "\"input_images\":76,\"blocks\":4,\"companion_images\":76,\"field_images\":76,"
               "\"nonconstant_extra_images\":4,\"missed_witness_controls\":2,\"verified\":true}\n";
        out.close();need(bool(out),"failed writing output");
        std::cout<<"Verified four mixed-family blocks, 76 input images, 152 zero axiom images, "
                    "and two missed-witness controls. Saved "<<path<<'\n';
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
