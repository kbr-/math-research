// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exhaustive small-board checks of two restriction-counting identities.
#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using Count = std::uint64_t;
using Wide = __uint128_t;

void require(bool condition, const std::string& message) {
    if (!condition) throw std::runtime_error(message);
}
Count falling(int n, int k) {
    if (k < 0 || k > n) return 0;
    Count answer = 1;
    for (int i = 0; i < k; ++i) answer *= Count(n-i);
    return answer;
}
Count choose(int n, int k) {
    return falling(n,k) / falling(k,k);
}
struct Graph {
    std::string name;
    std::vector<unsigned char> edges;
    Count avoided = 0, bad = 0;
};

void board(std::ostream& out, int n, int residual, int threshold) {
    const int m = n+1, q = n-residual;
    require(threshold >= 1 && threshold <= 2 && threshold <= q,
            "These fixtures test matching thresholds one and two");
    std::vector<Graph> graphs;
    for (const std::string name : {"empty", "complete", "diagonal",
                                  "cyclic_pairs", "row_star", "checkerboard"}) {
        Graph graph{name, std::vector<unsigned char>(m*n)};
        for (int i=0; i<m; ++i) for (int j=0; j<n; ++j) {
            bool edge = name == "complete"
                || (name == "diagonal" && i == j)
                || (name == "cyclic_pairs" && (i == j || i == (j+1)%m))
                || (name == "row_star" && i == 0)
                || (name == "checkerboard" && (i+j)%2 == 0);
            graph.edges[i*n+j] = edge;
        }
        graphs.push_back(std::move(graph));
    }
    std::vector<int> row(m,-1), col(n,-1), free_rows, free_cols;
    std::vector<Count> negative_survival(4,0);
    Count total = 0;
    auto visit = [&]() {
        ++total;
        free_rows.clear(); free_cols.clear();
        for (int i=0; i<m; ++i) if (row[i]<0) free_rows.push_back(i);
        for (int j=0; j<n; ++j) if (col[j]<0) free_cols.push_back(j);
        require(int(free_rows.size()) == residual+1 &&
                int(free_cols.size()) == residual, "Residual shape");
        for (auto& graph : graphs) {
            bool hit = false;
            for (int j=0; j<n; ++j)
                if (col[j]>=0 && graph.edges[col[j]*n+j]) { hit=true; break; }
            if (hit) continue;
            ++graph.avoided;
            bool bad = false;
            for (int i : free_rows) for (int j : free_cols) {
                if (!graph.edges[i*n+j]) continue;
                if (threshold == 1) { bad=true; continue; }
                for (int k : free_rows) for (int l : free_cols)
                    if (k != i && l != j && graph.edges[k*n+l]) bad=true;
            }
            if (bad) ++graph.bad;
        }
        // Fixed disjoint negative literals 1-x_00, ..., 1-x_(t-1,t-1).
        for (int t=1; t<=3; ++t) {
            bool survives = true;
            for (int i=0; i<t; ++i)
                if (!(row[i] == i || (row[i]<0 && col[i]<0))) survives=false;
            if (survives) ++negative_survival[t];
        }
    };
    std::function<void(int,int)> enumerate = [&](int j, int matched) {
        if (j == n) { if (matched == q) visit(); return; }
        if (matched+n-j-1 >= q) enumerate(j+1,matched);
        if (matched == q) return;
        for (int i=0; i<m; ++i) if (row[i]<0) {
            row[i]=j; col[j]=i;
            enumerate(j+1,matched+1);
            row[i]=-1; col[j]=-1;
        }
    };
    enumerate(0,0);
    const Count expected_total = choose(m,q)*choose(n,q)*falling(q,q);
    require(total == expected_total, "Enumeration count");
    const Count positive_num = falling(residual+1,threshold)*falling(residual,threshold);
    const Count positive_den = falling(q,threshold);
    Count positive_nonzero = 0;
    for (const auto& graph : graphs) {
        require(Wide(graph.bad)*positive_den <= Wide(total)*positive_num,
                "Positive switch bound: "+graph.name);
        if (graph.bad) ++positive_nonzero;
        out << "{\"record\":\"positive_request\",\"n\":" << n
            << ",\"N\":" << residual << ",\"q\":" << q
            << ",\"t\":" << threshold << ",\"graph\":\"" << graph.name
            << "\",\"total_matchings\":" << total
            << ",\"avoiding_matchings\":" << graph.avoided
            << ",\"avoiding_with_live_t_matching\":" << graph.bad
            << ",\"probability_bound_numerator\":" << positive_num
            << ",\"probability_bound_denominator\":" << positive_den
            << ",\"edges\":[";
        bool first=true;
        for (int i=0; i<m; ++i) for (int j=0; j<n; ++j) if (graph.edges[i*n+j]) {
            if (!first) out << ',';
            first=false; out << '[' << i << ',' << j << ']';
        }
        out << "]}\n";
    }
    require(positive_nonzero >= 2, "Need nonzero bad-event controls");
    for (int t=1; t<=3; ++t) {
        Count numerator = 0;
        for (int s=0; s<=t; ++s)
            numerator += choose(t,s)*falling(q,s)*
                         falling(residual+1,t-s)*falling(residual,t-s);
        const Count denominator = falling(m,t)*falling(n,t);
        require(Wide(negative_survival[t])*denominator == Wide(total)*numerator,
                "Exact negative-literal survival count");
        require(negative_survival[t] > 0 && negative_survival[t] < total,
                "Nonvacuous negative-literal control");
        out << "{\"record\":\"negative_matching\",\"n\":" << n
            << ",\"N\":" << residual << ",\"q\":" << q << ",\"t\":" << t
            << ",\"total_matchings\":" << total
            << ",\"surviving_matchings\":" << negative_survival[t]
            << ",\"exact_probability_numerator\":" << numerator
            << ",\"exact_probability_denominator\":" << denominator << "}\n";
    }
}

int main(int argc, char** argv) {
    try {
        require(argc == 3 && std::string(argv[1]) == "--out", "Usage: checker --out NEW.jsonl");
        const std::filesystem::path path(argv[2]);
        require(!std::filesystem::exists(path), "Refusing to overwrite output");
        if (!path.parent_path().empty()) std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);
        require(bool(out), "Cannot open output");
        out << "{\"record\":\"metadata\",\"schema\":1,"
               "\"scope\":\"all partial matchings on two fixed boards; six positive graphs "
               "and three fixed negative matchings per board; zero-based edges\"}\n";
        board(out,6,1,1);
        board(out,8,2,2);
        out << "{\"record\":\"summary\",\"boards\":2,\"positive_cases\":12,"
               "\"negative_cases\":6,\"partial_matchings_enumerated\":1708560,"
               "\"checks_passed\":true}\n";
        out.close();
        require(bool(out), "Output write failed");
        std::cout << "Checked 1,708,560 partial matchings; all 18 counting controls passed.\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
