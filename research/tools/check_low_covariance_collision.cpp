// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact binary quadratic moments and an adaptive linear-query collision search.
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

using Matrix = std::vector<std::vector<int>>;
void need(bool ok, const std::string& why) {
    if (!ok) throw std::runtime_error(why);
}
void integers(std::ostream& out, const std::vector<int>& v) {
    out << '[';
    for (size_t i=0; i<v.size(); ++i) { if (i) out << ','; out << v[i]; }
    out << ']';
}
int ceil_log2(int n) {
    int k=0, power=1;
    while (power<n) { power*=2; ++k; }
    return k;
}
int rank(Matrix a) {
    int r=0;
    for (int c=0; c<int(a.size()); ++c) {
        int p=r;
        while (p<int(a.size()) && !a[p][c]) ++p;
        if (p==int(a.size())) continue;
        std::swap(a[p],a[r]);
        for (int i=r+1; i<int(a.size()); ++i)
            if (a[i][c])
                for (int j=c; j<int(a.size()); ++j) a[i][j]^=a[r][j];
        ++r;
    }
    return r;
}
struct Checks { long total=0, failures=0; };
Checks moment_checks(int n, const std::vector<int>& mu, const Matrix& a) {
    Checks result;
    auto check=[&](bool ok) { ++result.total; result.failures+=!ok; };
    const int m=n+1, v=m*n;
    for (int i=0; i<m; ++i) {
        int value=0;
        for (int j=0; j<n; ++j) value^=mu[i*n+j];
        check(value==1);
        for (int x=0; x<v; ++x) {
            value=mu[x];
            for (int j=0; j<n; ++j) value^=a[x][i*n+j];
            check(value==0);
        }
    }
    for (int x=0; x<v; ++x) {
        check(a[x][x]==mu[x]);
        for (int y=x+1; y<v; ++y) {
            check(a[x][y]==a[y][x]);
            if (x/n==y/n || x%n==y%n) check(a[x][y]==0);
        }
    }
    return result;
}
void moment_case(std::ostream& out, int n) {
    const int v=n*(n+1);
    std::vector<int> destinations(n+1),mu(v),u(v),w(v);
    for (int i=2; i<=n; ++i) destinations[i]=i-1;
    for (int i=0; i<=n; ++i) mu[i*n+destinations[i]]=1;
    u[0]=u[1]=1; w[n]=w[n+2]=1;
    Matrix a(v,std::vector<int>(v)),b=a,control=a;
    for (int x=0; x<v; ++x) for (int y=0; y<v; ++y) {
        b[x][y]=(u[x]&w[y])^(w[x]&u[y]);
        control[x][y]=mu[x]&mu[y];
        a[x][y]=control[x][y]^b[x][y];
    }
    const auto checked=moment_checks(n,mu,a);
    const auto rejected=moment_checks(n,mu,control);
    const int r=rank(b);
    need(checked.failures==0 && r==2,"Rank-two design failed");
    need(rejected.failures>0,"Deleting the covariance must violate a column axiom");
    out << "{\"record\":\"moments\",\"n\":" << n << ",\"mean_destinations\":";
    integers(out,destinations);
    out << ",\"u_support\":[0,1],\"v_support\":";
    integers(out,{n,n+2});
    out << ",\"A_rows\":[";
    for (int x=0; x<v; ++x) {
        if (x) out << ',';
        out << '"'; for (int y=0; y<v; ++y) out << a[x][y]; out << '"';
    }
    out << "],\"covariance_rank\":" << r
        << ",\"constraint_checks\":" << checked.total
        << ",\"failures\":" << checked.failures
        << ",\"zero_covariance_control_failures\":" << rejected.failures << "}\n";
    std::cout << "n=" << n << ": rank 2, " << checked.total
              << " moment checks passed; zero-covariance control rejected.\n";
}
struct Search {
    int n,queries=0;
    const std::vector<int>& destination;
    std::ostream& out;
    bool first=true;
    void prefix(const char* kind) {
        if (!first) out << ',';
        first=false;
        out << "{\"kind\":\"" << kind << '"';
        ++queries;
    }
    int column_query(const std::vector<int>& cols) {
        int answer=int(cols.size())&1;
        for (int d:destination)
            if (std::find(cols.begin(),cols.end(),d)!=cols.end()) answer^=1;
        prefix("column_defect_sum");
        out << ",\"columns\":"; integers(out,cols);
        out << ",\"answer\":" << answer << '}';
        return answer;
    }
    int row_query(int j, const std::vector<int>& rows) {
        int answer=0;
        for (int i:rows) answer^=(destination[i]==j);
        prefix("column_row_sum");
        out << ",\"column\":" << j << ",\"rows\":"; integers(out,rows);
        out << ",\"answer\":" << answer << '}';
        return answer;
    }
    std::vector<int> run() {
        std::vector<int> cols(n);
        std::iota(cols.begin(),cols.end(),0);
        while (cols.size()>1) {
            auto mid=cols.begin()+cols.size()/2;
            std::vector<int> left(cols.begin(),mid),right(mid,cols.end());
            cols=column_query(left)?left:right;
        }
        const int j=cols[0],k=ceil_log2(n+1);
        int difference=0;
        for (int bit=0; bit<k; ++bit) {
            std::vector<int> rows;
            for (int i=0; i<=n; ++i) if ((i>>bit)&1) rows.push_back(i);
            difference|=row_query(j,rows)<<bit;
        }
        need(difference!=0,"Two distinct row labels must have nonzero XOR");
        int bit=0;
        while (!((difference>>bit)&1)) ++bit;
        std::vector<int> candidates;
        for (int i=0; i<=n; ++i) if ((i>>bit)&1) candidates.push_back(i);
        while (candidates.size()>1) {
            auto mid=candidates.begin()+candidates.size()/2;
            std::vector<int> left(candidates.begin(),mid),right(mid,candidates.end());
            candidates=row_query(j,left)?left:right;
        }
        int a=candidates[0],b=a^difference;
        need(b>=0 && b<=n && a!=b,"Recovered row pair is invalid");
        need(destination[a]==j && destination[b]==j,"Leaf is not a collision");
        need(queries<=ceil_log2(n)+2*k-1,"Query budget exceeded");
        return {a,b,j};
    }
};
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","Usage: checker --out PATH");
        std::filesystem::path path=argv[2];
        need(!std::filesystem::exists(path),"Refusing to replace an existing output");
        if (!path.parent_path().empty()) std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);
        need(bool(out),"Cannot create output");
        out << "{\"record\":\"schema\",\"field\":2,\"variable_index\":\"i*n+j\","
               "\"column_defect_sum\":\"sum_{j in columns}(1+sum_i X_ij)\","
               "\"column_row_sum\":\"sum_{i in rows} X_i,column\","
               "\"scope\":\"four full quadratic designs; complete collision-column/row-pair "
               "query traces with canonical bijections on other rows; no higher-degree computation\"}\n";
        for (int n:{3,4,6,8}) moment_case(out,n);
        long cases=0;
        for (int n:{3,4,6,8,12,16}) {
            int max_queries=0;
            long board_cases=0;
            for (int j=0; j<n; ++j) for (int a=0; a<=n; ++a)
                for (int b=a+1; b<=n; ++b) {
                    std::vector<int> destination(n+1,j);
                    int next=0;
                    for (int i=0; i<=n; ++i) if (i!=a && i!=b) {
                        if (next==j) ++next;
                        destination[i]=next++;
                    }
                    out << "{\"record\":\"query_case\",\"n\":" << n
                        << ",\"collision_column\":" << j << ",\"collision_rows\":";
                    integers(out,{a,b});
                    out << ",\"mean_destinations\":"; integers(out,destination);
                    out << ",\"queries\":[";
                    Search search{n,0,destination,out};
                    auto leaf=search.run();
                    out << "],\"leaf_rows_and_column\":"; integers(out,leaf);
                    out << ",\"query_count\":" << search.queries
                        << ",\"leaf_marginals\":[1,1],\"column_axiom_moment\":0}\n";
                    max_queries=std::max(max_queries,search.queries);
                    ++cases; ++board_cases;
                }
            const int bound=ceil_log2(n)+2*ceil_log2(n+1)-1;
            out << "{\"record\":\"query_summary\",\"n\":" << n << ",\"cases\":" << board_cases
                << ",\"max_queries\":" << max_queries << ",\"proved_bound\":" << bound << "}\n";
            std::cout << "n=" << n << ": " << board_cases << " collision cases, max "
                      << max_queries << " linear queries <= " << bound << ".\n";
        }
        out << "{\"record\":\"summary\",\"query_cases\":" << cases << ",\"all_passed\":true}\n";
        out.close(); need(bool(out),"Output write failed");
        std::cout << "All " << cases << " query cases passed. Full output: " << path << '\n';
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n'; return 1;
    }
}
