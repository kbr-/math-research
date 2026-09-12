// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact degree-two spaces and falsifying tests for sharp affine PHP Booleanity.
#define TARGET_ANNIHILATORS_NO_MAIN
#include "check_target_annihilators.cpp"

Sparse sparse(const Row& row) {
    Sparse out;for(size_t i=0;i<row.size();i++)if(row[i])out.push_back({int(i),row[i]});
    return out;
}
int dot(const Row& a,const Row& b,int p) {
    need(a.size()==b.size(),"dot dimensions");int value=0;
    for(size_t i=0;i<a.size();i++)value=(value+a[i]*b[i])%p;
    return value;
}
Row affine_booleanity(const Board& b,const Row& a,int p) {
    Row out(b.columns);out[0]=residue(a[0]*a[0]-a[0],p);
    for(int v=0;v<b.variables;v++)out[v+1]=residue((2*a[0]-1)*a[v+1],p);
    for(int v=0;v<b.variables;v++)if(a[v+1])
        for(int w=v;w<b.variables;w++)if(a[w+1]) {
            int index=b.product[v][w];
            if(index>=0)out[index]=residue(out[index]+(v==w?1:2)*a[v+1]*a[w+1],p);
        }
    return out;
}
struct Canonical {
    bool valid=false;int column=-1,constant=0,subset=0;
    std::vector<int> gauges;
};
Canonical classify(const Board& b,const Row& a,int p) {
    need(b.n>=4 && p>2,"classification parameters");
    Canonical answer;answer.constant=a[0];answer.gauges.resize(b.m);
    std::vector<int> spikes(b.m);
    for(int i=0;i<b.m;i++) {
        int background=-1;
        for(int value=0;value<p;value++) {
            int count=0;for(int j=0;j<b.n;j++)count+=a[1+i*b.n+j]==value;
            if(count>=b.n-1){background=value;break;}
        }
        if(background<0)return answer;
        answer.gauges[i]=background;answer.constant=(answer.constant+background)%p;
        for(int j=0;j<b.n;j++)if(a[1+i*b.n+j]!=background) {
            if(answer.column>=0 && answer.column!=j)return answer;
            answer.column=j;spikes[i]=residue(a[1+i*b.n+j]-background,p);
        }
    }
    if(answer.constant!=0 && answer.constant!=1)return answer;
    int sign=answer.constant?p-1:1;
    for(int i=0;i<b.m;i++)if(spikes[i]) {
        if(spikes[i]!=sign)return answer;
        answer.subset|=1<<i;
    }
    if(answer.column<0)answer.column=0;
    answer.valid=true;return answer;
}
struct AffineCounts {int boards=0,cases=0,positive=0,negative=0,duals=0,controls=0;};
void affine_board(std::ostream& out,AffineCounts& count,int n,int p) {
    Board b(n);Basis space(p,b.columns);std::vector<Row> generators;
    for(int i=0;i<b.m;i++) {
        Row ax=b.row_axiom(i,p);generators.push_back(b.lift_affine(ax));
        for(int v=0;v<b.variables;v++)generators.push_back(b.multiply_affine(ax,v,p));
    }
    for(const auto& row:generators)space.add(row);
    int affine_rank=0;
    for(int k=0;k<=b.variables;k++)if(!space.rows[k].empty())affine_rank++;
    need(affine_rank==b.m,"affine rigidity/PC closure failed");
    Row one(b.columns);one[0]=1;
    need(!zero(space.reduce(one)),"unexpected degree-two refutation");
    std::string name="n"+std::to_string(n)+"_F"+std::to_string(p);
    out<<"{\"record\":\"board\",\"name\":\""<<name<<"\",\"n\":"<<n<<",\"p\":"<<p
       <<",\"variables\":"<<b.variables<<",\"normal_columns\":"<<b.columns
       <<",\"normalized_I2_rank\":"<<space.rank<<",\"affine_rank\":"<<affine_rank
       <<",\"PC2_equals_I2\":true,\"normal_monomials\":[";
    for(size_t i=0;i<b.monomials.size();i++) {
        if(i)out<<',';
        out<<'['<<b.monomials[i].first<<','<<b.monomials[i].second<<']';
    }
    out<<"]}\n";
    for(size_t i=0;i<generators.size();i++) {
        out<<"{\"record\":\"original_row_multiple\",\"board\":\""<<name
           <<"\",\"row\":"<<i/(b.variables+1)<<",\"multiplier_variable\":"
           <<int(i%(b.variables+1))-1<<",\"cells\":";
        sparse_json(out,sparse(generators[i]));out<<"}\n";
    }
    space.write(out,name);
    std::vector<Row> dual(b.columns,Row(b.columns));
    for(int i=0;i<b.columns;i++) {
        Row unit(b.columns);unit[i]=1;Row rem=space.reduce(unit);
        for(int k=0;k<b.columns;k++)dual[k][i]=rem[k];
    }
    for(int k=0;k<b.columns;k++)if(space.rows[k].empty()) {
        for(const auto& generator:generators)
            need(dot(dual[k],generator,p)==0,"dual fails an original row multiple");
        out<<"{\"record\":\"dual\",\"board\":\""<<name<<"\",\"index\":"<<k<<",\"cells\":";
        sparse_json(out,sparse(dual[k]));out<<"}\n";count.duals++;
    }
    auto test=[&](const Row& a,const std::string& scope) {
        Row target=affine_booleanity(b,a,p),rem=space.reduce(target);
        bool member=zero(rem);Canonical canonical;
        if(p==2)need(member,"binary affine Booleanity failed");
        else {
            canonical=classify(b,a,p);
            need(canonical.valid==member,"classification disagrees with exact membership");
        }
        int witness=-1,value=0;
        if(!member) {
            for(int k=0;k<b.columns;k++)if(rem[k]){witness=k;value=rem[k];break;}
            need(witness>=0 && space.rows[witness].empty(),"invalid dual pivot");
            need(dot(dual[witness],target,p)==value && value!=0,"invalid separating dual");
        }
        out<<"{\"record\":\"affine_test\",\"board\":\""<<name<<"\",\"scope\":\""<<scope
           <<"\",\"affine_coefficients\":";sparse_json(out,sparse(a));
        out<<",\"Booleanity_in_I2\":"<<(member?"true":"false")
           <<",\"dual_index\":"<<witness<<",\"dual_value\":"<<value;
        if(member && p>2) {
            out<<",\"column\":"<<canonical.column<<",\"constant\":"<<canonical.constant
               <<",\"subset_mask\":"<<canonical.subset<<",\"row_gauges\":[";
            for(size_t i=0;i<canonical.gauges.size();i++){if(i)out<<',';out<<canonical.gauges[i];}
            out<<']';
        }
        out<<"}\n";count.cases++;(member?count.positive:count.negative)++;
        return member;
    };
    if(n==4) {
        int varying=p==5?n:2*n;int total=1;
        for(int i=0;i<=varying;i++)total*=p;
        for(int code=0;code<total;code++) {
            Row a(b.variables+1);int remaining=code;
            for(int i=0;i<=varying;i++){a[i]=remaining%p;remaining/=p;}
            test(a,p==5?"exhaustive_one_row":"exhaustive_two_rows");
        }
        if(p>2) {
            for(int column=0;column<n;column++)for(int mask=0;mask<(1<<b.m);mask++)
                for(int complement=0;complement<2;complement++)for(int gauge=0;gauge<2;gauge++) {
                    Row a(b.variables+1);a[0]=complement;
                    for(int i=0;i<b.m;i++) {
                        int t=gauge?(i+1)%p:0;
                        a[0]=residue(a[0]-t,p);
                        for(int j=0;j<n;j++)a[1+i*n+j]=t;
                        if((mask>>i)&1)a[1+i*n+column]=residue(
                            a[1+i*n+column]+(complement?-1:1),p);
                    }
                    need(test(a,"all_subsets_with_row_gauges"),"canonical positive rejected");
                }
            for(bool same_row:{false,true}) {
                Row a(b.variables+1);a[1]=1;a[1+(same_row?1:n+1)]=1;
                need(!test(a,same_row?"same_row_partial_sum_control":"cross_column_sum_control"),
                     "negative affine control accepted");count.controls++;
            }
        }
    }
    count.boards++;
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","usage: check_affine_php_booleanity --out PATH");
        std::string path=argv[2];need(!std::filesystem::exists(path),"refusing to replace output");
        std::ofstream out(path);need(out.good(),"cannot open output");AffineCounts count;
        out<<"{\"record\":\"schema\",\"version\":1,\"arithmetic\":\"exact prime fields\","
              "\"scope\":\"ordinary weak PHP, degree two\","
              "\"coordinates\":\"constant, linear, then squarefree different-column pairs; same-row pairs kept\"}\n";
        for(int p:{2,3,5})for(int n:{3,4})affine_board(out,count,n,p);
        out<<"{\"record\":\"summary\",\"boards\":"<<count.boards
           <<",\"affine_tests\":"<<count.cases<<",\"positive\":"<<count.positive
           <<",\"negative\":"<<count.negative<<",\"duals\":"<<count.duals
           <<",\"explicit_negative_controls\":"<<count.controls<<"}\n";
        out.flush();need(out.good(),"output failure");
        std::cout<<"Passed "<<count.boards<<" spaces, "<<count.cases<<" affine tests ("
                 <<count.positive<<" positive, "<<count.negative<<" negative), "
                 <<count.duals<<" checked duals; output "<<path<<"\n";return 0;
    } catch(const std::exception& e) {std::cerr<<"ERROR: "<<e.what()<<"\n";return 1;}
}
