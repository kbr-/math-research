// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Degree-sum matching and complete path-exception projection certificates.
#define COLUMN_STATISTIC_FREEZING_NO_MAIN
#include "check_column_statistic_freezing.cpp"
#define MAJORITY_PROFILE_LAYOUTS_NO_MAIN
#include "check_majority_profile_layouts.cpp"

struct ExceptionCounts {
    int small_graphs=0,small_equality_graphs=0,controls=0,local_graphs=0,
        local_equalities=0,statistics=0,profile_cases=0;
} exception_counts;

void degree_sum_controls(std::ostream& out) {
    constexpr int K=4;Matrix graph(K*K);
    for(unsigned mask=0;mask<(1u<<(K*K));mask++) {
        for(int i=0;i<K*K;i++)graph[i]=std::uint8_t((mask>>i)&1u);
        auto [left,right]=minimum_degrees(graph,K);
        if(left+right<K)continue;
        int rewires=0;auto matching=short_matching(graph,K,rewires);
        out<<"{\"record\":\"degree_sum_graph\",\"K\":4,\"row_major_edge_mask\":"<<mask
           <<",\"minimum_left_degree\":"<<left<<",\"minimum_right_degree\":"<<right<<",\"matching\":";
        majority_list(out,matching);out<<",\"short_rewirings\":"<<rewires<<"}\n";
        exception_counts.small_graphs++;
        if(left+right==K)exception_counts.small_equality_graphs++;
    }
    need(exception_counts.small_graphs>209 && exception_counts.small_equality_graphs>0,
         "degree-sum test did not extend the strict-majority domain");
    // A degree-sum of K-1 does not suffice in general.
    Matrix bad(16);std::vector<int> subset={1,2,3},neighbors;
    for(int i=0;i<4;i++)for(int j=0;j<4;j++)bad[4*i+j]=std::uint8_t((i<1)==(j<2));
    auto [left,right]=minimum_degrees(bad,4);
    for(int j=0;j<4;j++) {
        bool hit=false;for(int i:subset)hit=hit || bad[4*i+j];
        if(hit)neighbors.push_back(j);
    }
    need(left+right==3 && neighbors.size()<subset.size(),"degree-sum Hall control");
    out<<"{\"record\":\"degree_sum_control\",\"K\":4,\"minimum_left_degree\":"<<left
       <<",\"minimum_right_degree\":"<<right<<",\"row_major_matrix\":[";
    for(size_t i=0;i<bad.size();i++){if(i)out<<',';out<<int(bad[i]);}
    out<<"],\"left_subset\":";majority_list(out,subset);out<<",\"neighbors\":";
    majority_list(out,neighbors);out<<"}\n";exception_counts.controls++;
}
void exception_family(std::ostream& out,FreezeCounts& count,const std::string& name,
                       int p,int copies,const std::vector<std::vector<CellImage>>& cells) {
    constexpr int N=3;int n=int(cells[0].size()),m=int(cells.size());
    need(n==4*copies+1 && m==n+1 && copies==p*((4+p)/p)-1,"exception fixture parameters");
    const Poly zero(p),one(p,1);
    std::vector<int> row_label(m),column_label(n);
    row_label[0]=n-1;row_label[n]=n;
    for(int i=1;i<n;i++)row_label[i]=((i-1)%4)*copies+(i-1)/4;
    column_label[0]=n-1;
    for(int j=1;j<=copies;j++)column_label[j]=j-1;
    for(int j=copies+1;j<n;j++) {
        int t=j-copies-1;column_label[j]=(t%3+1)*copies+t/3;
    }
    for(const auto* values:{&row_label,&column_label}) {
        std::vector<int> seen(values->size());
        for(int x:*values){need(x>=0 && x<int(seen.size()),"path label range");seen[x]++;}
        for(int x:seen)need(x==1,"path labels are not bijective");
    }
    out<<"{\"record\":\"path_profile\",\"case\":\""<<name
       <<"\",\"physical_row_to_path_pigeon\":";majority_list(out,row_label);
    out<<",\"physical_column_to_path_column\":";majority_list(out,column_label);
    out<<",\"chosen_class_rule\":\"in path column j exclude pigeons j and j+1\","
         "\"distinguished_physical_pigeon\":"<<n<<",\"bad_physical_column\":0,"
         "\"first_matching\":\"physical row 0 to column 0\","
         "\"row_exception_bound\":2,\"column_exception_bound\":2,\"copy_count\":"<<copies<<"}\n";
    std::vector<int> row_exceptions(m),input_values;
    for(int j=0;j<n;j++) {
        std::array<std::vector<int>,2> classes;
        for(int i=0;i<m;i++) {
            bool excluded=row_label[i]==column_label[j] || row_label[i]==column_label[j]+1;
            classes[excluded?1:0].push_back(i);if(excluded)row_exceptions[i]++;
        }
        need(classes[1].size()==2,"wrong column exception count");
        for(int which=0;which<2;which++) {
            Poly value(p);for(int i:classes[which])value=value+cells[i][j].value;
            int expected=j==0?(which==1):(j<=copies?0:(which==0));
            need(value==Poly(p,expected),"exception statistic image");
            out<<"{\"record\":\"exception_statistic\",\"case\":\""<<name<<"\",\"input\":"<<input_values.size()
               <<",\"source_column\":"<<j<<",\"chosen_class\":"<<(which==0?"true":"false")<<",\"source_rows\":";
            majority_list(out,classes[which]);out<<",\"source_degree\":1,\"image\":";jsonpoly(out,value);
            out<<"}\n";input_values.push_back(expected);exception_counts.statistics++;
        }
    }
    need(*std::max_element(row_exceptions.begin(),row_exceptions.end())==2
         && *std::min_element(row_exceptions.begin(),row_exceptions.end())==1
         && row_exceptions[n]==1,"row exceptions/common intersection");
    out<<"{\"record\":\"row_exception_counts\",\"case\":\""<<name<<"\",\"counts\":";
    majority_list(out,row_exceptions);out<<",\"chosen_class_intersection_empty\":true}\n";
    for(int a=0;a<=N;a++)for(int j=0;j<N;j++) {
        Matrix allowance(copies*copies);std::vector<int> actual(copies,-1);
        for(int d=0;d<copies;d++)for(int c=0;c<copies;c++) {
            int row=1+d*4+a,column=1+copies+c*3+j;
            allowance[d*copies+c]=std::uint8_t(row_label[row]!=column_label[column]
                                             && row_label[row]!=column_label[column]+1);
            if(cells[row][column].kind=='x' && cells[row][column].index==a*3+j) {
                need(actual[d]<0,"duplicate source copy image");actual[d]=c;
            }
        }
        auto [left,right]=minimum_degrees(allowance,copies);
        need(left>=copies-2 && right>=copies-2 && left+right>=copies,"local degree-sum bound");
        std::vector<int> seen(copies);
        for(int d=0;d<copies;d++) {
            need(actual[d]>=0 && allowance[d*copies+actual[d]],"projection uses a forbidden edge");
            seen[actual[d]]++;
        }
        for(int value:seen)need(value==1,"projection copy map is not a bijection");
        out<<"{\"record\":\"exception_allowance\",\"case\":\""<<name<<"\",\"residual_row\":"<<a
           <<",\"residual_column\":"<<j<<",\"minimum_left_degree\":"<<left<<",\"minimum_right_degree\":"<<right
           <<",\"projection_permutation\":";majority_list(out,actual);out<<"}\n";
        exception_counts.local_graphs++;
        if(left+right==copies)exception_counts.local_equalities++;
    }
    int arity=int(input_values.size()),chosen=-1;
    for(int i=0;i<arity;i++)if(input_values[i]){chosen=i;break;}
    need(chosen==1,"matching-prefix complement should be the first unit input");
    std::vector<int> beta(arity);beta[chosen]=1;int factor=1;
    for(int i=0;i<arity;i++)factor=(factor+p-beta[i]*input_values[i])%p;
    need(factor==0,"nonzero ENS product");
    for(int i=0;i<arity;i++)need(input_values[i]*factor%p==0
        && (modpow(beta[i],p,p)-beta[i]+p)%p==0,"ENS or field image");
    out<<"{\"record\":\"exception_statistic_block\",\"case\":\""<<name
       <<"\",\"inputs\":\"all exception_statistic records in input order\","
         "\"accuracy\":1,\"level\":1,\"source_product\":\"1-sum_i r_i*g_i\","
         "\"source_companions\":\"g_i times source_product for every i\","
         "\"source_fields\":\"r_i^p-r_i for every i\","
         "\"original_input_degree\":1,\"original_companion_degree\":3,\"original_field_degree\":"<<p
       <<",\"input_images\":";majority_list(out,input_values);out<<",\"coefficient_images\":";
    majority_list(out,beta);out<<",\"all_companion_and_field_images_zero\":true}\n";
    count.blocks++;count.companion_images+=arity;count.field_images+=arity;exception_counts.profile_cases++;
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","usage: check_bounded_exception_layouts --out NEW-PATH.jsonl");
        std::filesystem::path path(argv[2]);need(!std::filesystem::exists(path),"output already exists");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot open output");FreezeCounts count;
        degree_sum_controls(out);
        for(auto [p,copies]:std::vector<std::pair<int,int>>{{2,5},{3,5},{5,4}}) {
            std::vector<std::vector<int>> shifts(4,std::vector<int>(3));
            for(int a=0;a<4;a++)for(int j=0;j<3;j++)if(a==j+1)shifts[a][j]=2;
            freeze_case(out,count,p,copies,1,shifts,exception_family);
        }
        need(count.base_images==13595 && count.base_certificates==689,"complete base counts");
        need(exception_counts.statistics==118 && exception_counts.local_graphs==36
             && exception_counts.local_equalities==3 && count.companion_images==118
             && count.field_images==118,"exception layout counts");
        out<<"{\"record\":\"summary\",\"profiles\":"<<exception_counts.profile_cases
           <<",\"base_images\":"<<count.base_images<<",\"nonzero_base_NS_certificates\":"<<count.base_certificates
           <<",\"local_statistic_images\":"<<exception_counts.statistics<<",\"allowance_graphs\":"<<exception_counts.local_graphs
           <<",\"equality_allowance_graphs\":"<<exception_counts.local_equalities
           <<",\"zero_companion_images\":"<<count.companion_images<<",\"zero_field_images\":"<<count.field_images
           <<",\"exhaustive_degree_sum_graphs\":"<<exception_counts.small_graphs
           <<",\"exhaustive_equality_graphs\":"<<exception_counts.small_equality_graphs
           <<",\"Hall_controls\":"<<exception_counts.controls<<",\"scope_control_pairs\":"<<count.scope_controls
           <<",\"verified\":true}\n";
        out.close();need(bool(out),"failed writing output");
        std::cout<<"Verified "<<exception_counts.small_graphs<<" degree-sum graphs, "<<count.base_images
                 <<" base images ("<<count.base_certificates<<" NS certificates), and "
                 <<exception_counts.statistics<<" local statistics.\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
