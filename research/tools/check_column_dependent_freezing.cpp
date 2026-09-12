// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Twisted copy maps: complete base images and column-specific partition statistics.
#define COLUMN_STATISTIC_FREEZING_NO_MAIN
#include "check_column_statistic_freezing.cpp"

int local_partition_images=0,refinement_rows=0,refinement_cases=0;
void twisted_indices(std::ostream& out,const std::vector<int>& items) {
    out<<'[';for(size_t i=0;i<items.size();i++){if(i)out<<',';out<<items[i];}out<<']';
}
void local_partition_family(std::ostream& out,FreezeCounts& count,const std::string& name,
                            int p,int copies,const std::vector<std::vector<CellImage>>& cells) {
    constexpr int N=3;int m=int(cells.size()),n=int(cells.at(0).size());
    need(copies>=2 && n==copies*(N+1) && m==n+1,"twisted fixture dimensions");
    const Poly zero(p),one(p,1);
    std::vector<std::string> signatures(m);
    std::vector<int> input_values;
    auto add_input=[&](int column,const std::vector<int>& rows,int expected) {
        Poly sum(p);for(int i:rows)sum=sum+cells[i][column].value;
        need(sum==Poly(p,expected),"class statistic image");
        out<<"{\"record\":\"local_statistic\",\"case\":\""<<name<<"\",\"input\":"<<input_values.size()
           <<",\"source_column\":"<<column<<",\"source_rows\":";
        twisted_indices(out,rows);out<<",\"source_degree\":1,\"image\":";jsonpoly(out,sum);out<<"}\n";
        input_values.push_back(expected);
        local_partition_images++;
    };
    std::vector<int> all_rows;for(int i=0;i<m;i++)all_rows.push_back(i);
    for(int j=0;j<copies;j++)add_input(j,all_rows,0);
    for(int c=0;c<copies;c++)for(int j=0;j<N;j++) {
        int column=copies+c*N+j;std::vector<int> active,inactive;
        for(int i=0;i<m;i++) {
            bool present=cells[i][column].kind!='0';
            signatures[i]+=present?'1':'0';
            (present?active:inactive).push_back(i);
        }
        need(int(active.size())==N+2 && active.back()==m-1,"active class shape");
        add_input(column,active,1);add_input(column,inactive,0);
    }
    for(int i=0;i<m;i++)for(int k=0;k<i;k++)
        need(signatures[i]!=signatures[k],"global common refinement is not discrete");
    out<<"{\"record\":\"common_refinement\",\"case\":\""<<name
       <<"\",\"signature_order\":\"active classes in copy-major (c,j) order\",\"signatures\":[";
    for(int i=0;i<m;i++){if(i)out<<',';out<<'\"'<<signatures[i]<<'\"';}
    out<<"],\"singleton_classes\":"<<m<<",\"largest_class\":1,\"verified\":true}\n";
    refinement_rows+=m;refinement_cases++;

    int arity=int(input_values.size()),chosen=-1;
    for(int i=0;i<arity;i++)if(input_values[i]){chosen=i;break;}
    need(chosen>=0,"all local statistics vanished");
    std::vector<int> beta(arity,0);beta[chosen]=1;
    int factor=1;
    for(int i=0;i<arity;i++)factor=(factor+p-beta[i]*input_values[i])%p;
    need(factor==0,"nonzero family factor image");
    for(int i=0;i<arity;i++) {
        need(input_values[i]*factor%p==0 && (modpow(beta[i],p,p)-beta[i]+p)%p==0,
             "companion or field image");
    }
    out<<"{\"record\":\"full_local_statistic_block\",\"case\":\""<<name
       <<"\",\"input_definitions\":\"all local_statistic records in input-index order\","
         "\"accuracy\":1,\"level\":1,\"source_product\":\"1-sum_i r_i*g_i\","
         "\"source_companions\":\"g_i times source_product, for every input i\","
         "\"source_coefficient_fields\":\"r_i^p-r_i for every input i\","
         "\"arity\":"<<arity<<",\"original_input_degree\":1,\"original_companion_degree\":3,"
         "\"original_field_degree\":"<<p<<",\"input_images\":";
    twisted_indices(out,input_values);out<<",\"coefficient_images\":";twisted_indices(out,beta);
    out<<",\"product_image\":0,\"all_companion_and_field_images_zero\":true}\n";
    count.blocks++;count.companion_images+=arity;count.field_images+=arity;
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","usage: check_column_dependent_freezing --out NEW-PATH.jsonl");
        std::filesystem::path path(argv[2]);need(!std::filesystem::exists(path),"output already exists");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot open output");FreezeCounts count;
        for(auto [p,copies]:std::vector<std::pair<int,int>>{{3,2},{2,3},{5,4}}) {
            std::vector<std::vector<int>> shifts(4,std::vector<int>(3));
            for(int a=0;a<4;a++){shifts[a][1]=a%copies;shifts[a][2]=a/copies;}
            out<<"{\"record\":\"copy_permutations\",\"p\":"<<p<<",\"copies\":"<<copies
               <<",\"formula\":\"column_copy=(source_copy+shift[a][j]) mod copies\",\"shifts\":[";
            for(int a=0;a<4;a++){if(a)out<<',';twisted_indices(out,shifts[a]);}out<<"]}\n";
            freeze_case(out,count,p,copies,0,shifts,local_partition_family);
        }
        need(count.base_images==3939 && count.base_certificates==444,"base image totals");
        need(count.companion_images==63 && count.field_images==63
             && local_partition_images==63 && refinement_rows==39 && refinement_cases==3,"family totals");
        out<<"{\"record\":\"summary\",\"cases\":"<<count.cases<<",\"base_images\":"<<count.base_images
           <<",\"nonzero_base_NS_certificates\":"<<count.base_certificates
           <<",\"whole_column_checks\":"<<count.columns<<",\"local_statistic_images\":"<<local_partition_images
           <<",\"singleton_refinement_rows\":"<<refinement_rows<<",\"statistic_blocks\":"<<count.blocks
           <<",\"zero_companion_images\":"<<count.companion_images<<",\"zero_field_images\":"<<count.field_images
           <<",\"scope_control_pairs\":"<<count.scope_controls<<",\"verified\":true}\n";
        out.close();need(bool(out),"failed writing output");
        std::cout<<"Verified "<<count.base_images<<" base images ("<<count.base_certificates
                 <<" NS certificates), "<<local_partition_images<<" local statistics, and three discrete refinements.\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
