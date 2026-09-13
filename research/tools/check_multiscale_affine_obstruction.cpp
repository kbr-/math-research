// Copyright (c) 2026 Kamil Braun. MIT License; see ../../LICENSE.
#include <boost/multiprecision/cpp_int.hpp>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
using boost::multiprecision::cpp_int;

cpp_int binom(unsigned n, unsigned k) {
    if (k > n) return 0;
    k = std::min(k,n-k);
    cpp_int a = 1;
    for (unsigned j=1; j<=k; ++j) a = a*(n-j+1)/j;
    return a;
}
unsigned dyadic(unsigned n) {
    unsigned r=1;
    while (2*r<=n) r*=2;
    return r;
}
unsigned logceil(unsigned n) {
    unsigned L=0, power=1;
    while (power<n) {power*=2; ++L;}
    return L;
}
void union_check(unsigned n, unsigned lower, bool expected, std::ofstream& out) {
    const unsigned common_power=n*n-1;
    cpp_int sum=0;
    for (unsigned N=lower; N<=n; ++N) {
        const unsigned r=dyadic(N), power=N*N-1;
        const cpp_int numerator=binom(n,2)*binom(n+1,N+1)*binom(n,N)*
                                ((cpp_int(1)<<(2*r))-1);
        sum += numerator<<(common_power-power);
        out << "{\"type\":\"union_term\",\"n\":" << n << ",\"lower\":" << lower
            << ",\"N\":" << N << ",\"r\":" << r << ",\"numerator\":\""
            << numerator << "\",\"denominator_power\":" << power << "}\n";
    }
    const cpp_int denominator=cpp_int(1)<<common_power;
    const bool passes=sum<denominator;
    out << "{\"type\":\"union_sum\",\"n\":" << n << ",\"lower\":" << lower
        << ",\"numerator\":\"" << sum << "\",\"denominator\":\"" << denominator
        << "\",\"below_one\":" << (passes?"true":"false") << "}\n";
    if (passes!=expected) throw std::runtime_error("union-bound control failed");
    std::cout << "n=" << n << " N_min=" << lower << " union_below_one=" << passes << '\n';
}
void criterion_check(unsigned n, std::ofstream& out) {
    const unsigned h=logceil(n+1), D=2*h+1;
    unsigned boards=0, degree_cases=0;
    for (unsigned N=2*D; N<=n; ++N) {
        ++boards;
        const unsigned v=N*(N+1), r=dyadic(N);
        const unsigned T=std::max(1u,(r+h-1)/h-1);
        const unsigned old_bound=std::min(D+n,T*D);
        if (2*old_bound<=N) throw std::runtime_error("old criterion unexpectedly affordable");
        out << "{\"type\":\"board\",\"n\":" << n << ",\"N\":" << N << ",\"r\":" << r
            << ",\"M\":" << n << ",\"h\":" << h << ",\"D\":" << D
            << ",\"old_T\":" << T << ",\"old_optimized_bound\":" << old_bound
            << ",\"target_floor_N_over_2\":" << N/2 << "}\n";
        for (unsigned k=1; k<=N; ++k) {
            const unsigned B=std::max(1u,k-1)*D+k;
            if (2*B-1>N) break;
            ++degree_cases;
            cpp_int ambient=0, restricted=0, u=0, t=0, matching=1;
            for (unsigned j=0; j<=k; ++j) {
                ambient+=binom(v,j);
                restricted+=binom(v-r,j);
                if (j) matching=matching*(N+2-j)*(N+1-j)/j;
                u+=matching;
                if (j<k) t+=(N+1-j)*matching;
            }
            const cpp_int qlower=u-t;
            const bool two_block_obstruction=2*restricted>=ambient;
            const bool full_dimension_failure=n*restricted>=qlower;
            if (!two_block_obstruction || !full_dimension_failure)
                throw std::runtime_error("dimension criterion unexpectedly passes");
            out << "{\"type\":\"degree_case\",\"n\":" << n << ",\"N\":" << N
                << ",\"k\":" << k << ",\"B\":" << B << ",\"ambient\":\"" << ambient
                << "\",\"single_restriction_bound\":\"" << restricted
                << "\",\"matching_count\":\"" << u << "\",\"row_relation_count\":\""
                << t << "\",\"quotient_lower_bound\":\"" << qlower
                << "\",\"two_block_obstruction\":true,\"full_dimension_failure\":true}\n";
        }
    }
    out << "{\"type\":\"criterion_summary\",\"n\":" << n << ",\"boards\":" << boards
        << ",\"feasible_degree_cases\":" << degree_cases << ",\"all_checks_passed\":true}\n";
    std::cout << "n=" << n << ": " << boards << " boards, " << degree_cases
              << " feasible degree cases; both recorded tests remain insufficient.\n";
}
int main(int argc, char** argv) {
    try {
        if (argc!=3 || std::string(argv[1])!="--out")
            throw std::runtime_error("usage: check_multiscale_affine_obstruction --out NEW.jsonl");
        std::ifstream existing(argv[2]);
        if (existing.good()) throw std::runtime_error("output already exists");
        std::ofstream out(argv[2]);
        if (!out) throw std::runtime_error("cannot open output");
        out << "{\"type\":\"schema\",\"version\":1,\"arithmetic\":\"exact integers\","
               "\"scope\":\"Union-bound and parameter audit; no affine matrices constructed\","
               "\"randomness\":\"none\",\"large_integers\":\"decimal strings\"}\n";
        for (unsigned n : {64u,128u}) {
            union_check(n,4*logceil(n+1),true,out);
            criterion_check(n,out);
        }
        union_check(64,8,false,out);
        out.close();
        if (!out) throw std::runtime_error("output write failed");
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << '\n';
        return 1;
    }
}
