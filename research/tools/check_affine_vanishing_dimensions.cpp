// Copyright (c) 2026 Kamil Braun. MIT License; see ../../LICENSE.
// Exact parameter checks for the notebook's affine common-vanishing criterion.
#include <boost/multiprecision/cpp_int.hpp>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using boost::multiprecision::cpp_int;
using U64 = std::uint64_t;

struct Case {
    std::string label;
    U64 N, M, rank;
    unsigned h, D, k;
    int expected_dimension = -1, expected_degree = -1;
};

unsigned rank_fraction_degree(U64 M) {
    // Smallest k with 8*M*(4/5)^k <= 1, entirely in integer arithmetic.
    cpp_int left = cpp_int(8) * M, right = 1;
    unsigned k = 0;
    while (left > right) {
        left *= 4;
        right *= 5;
        ++k;
    }
    return k;
}

bool run_case(const Case& c, std::ofstream& out) {
    const U64 v = c.N * (c.N + 1);
    if (c.rank > v || c.k == 0 || c.k > c.N || c.D < 2*c.h + 1)
        throw std::runtime_error("invalid checked parameter range");
    const U64 residual_dimension = v - c.rank;
    const U64 T = c.k > 1 ? c.k - 1 : 1;
    const U64 B = T*c.D + c.k;
    cpp_int cv = 1, cz = 1, matching = 1;
    cpp_int ambient = 0, restricted = 0, normal_forms = 0, row_relations = 0;
    out << "{\"type\":\"case\",\"label\":\"" << c.label
        << "\",\"N\":" << c.N << ",\"M\":" << c.M
        << ",\"v\":" << v << ",\"rank_lower_bound\":" << c.rank
        << ",\"h\":" << c.h << ",\"D\":" << c.D
        << ",\"k\":" << c.k << ",\"T\":" << T << ",\"B\":" << B
        << ",\"series\":[";
    for (unsigned j = 0; j <= c.k; ++j) {
        if (j != 0) {
            cv = cv * (v-j+1) / j;
            cz = j <= residual_dimension ? cpp_int(cz * (residual_dimension-j+1) / j)
                                         : cpp_int(0);
            matching = matching * (c.N+2-j) * (c.N+1-j) / j;
            out << ',';
        }
        ambient += cv;
        restricted += cz;
        normal_forms += matching;
        if (j < c.k) row_relations += matching * (c.N+1-j);
        out << "{\"j\":" << j << ",\"ambient_binomial\":\"" << cv
            << "\",\"restricted_binomial\":\"" << cz
            << "\",\"matching_monomials\":\"" << matching << "\"}";
    }
    const cpp_int quotient_lower = normal_forms - row_relations;
    const cpp_int total_restricted = cpp_int(c.M) * restricted;
    const bool dimension_ok = total_restricted < quotient_lower;
    const bool degree_ok = c.N >= 2*B-1;
    const bool fraction_ok = cpp_int(5)*c.rank >= v;
    out << "],\"ambient_dimension\":\"" << ambient
        << "\",\"single_restriction_bound\":\"" << restricted
        << "\",\"all_restrictions_bound\":\"" << total_restricted
        << "\",\"matching_space_dimension\":\"" << normal_forms
        << "\",\"row_relation_count\":\"" << row_relations
        << "\",\"quotient_dimension_lower_bound\":\"" << quotient_lower
        << "\",\"dimension_margin\":\"" << quotient_lower-total_restricted
        << "\",\"dimension_condition\":" << (dimension_ok ? "true" : "false")
        << ",\"stable_degree_condition\":" << (degree_ok ? "true" : "false")
        << ",\"rank_at_least_one_fifth\":" << (fraction_ok ? "true" : "false")
        << ",\"exclusion_criterion\":" << (dimension_ok && degree_ok ? "true" : "false")
        << "}\n";
    if ((c.expected_dimension >= 0 && dimension_ok != (c.expected_dimension != 0)) ||
        (c.expected_degree >= 0 && degree_ok != (c.expected_degree != 0)))
        throw std::runtime_error("explicit control expectation failed: " + c.label);
    std::cout << c.label << ": N=" << c.N << " k=" << c.k << " B=" << B
              << " dimension=" << dimension_ok << " stable_degree=" << degree_ok << '\n';
    return dimension_ok && degree_ok;
}

int main(int argc, char** argv) {
    try {
        if (argc != 3 || std::string(argv[1]) != "--out")
            throw std::runtime_error("usage: check_affine_vanishing_dimensions --out NEW.jsonl");
        std::ifstream existing(argv[2]);
        if (existing.good()) throw std::runtime_error("output already exists");
        std::ofstream out(argv[2]);
        if (!out) throw std::runtime_error("cannot open output");
        out << "{\"type\":\"schema\",\"version\":1,\"field\":2,"
               "\"method\":\"Exact dimension inequalities; no input matrices or proofs constructed\","
               "\"large_integers\":\"decimal strings\",\"randomness\":\"none\"}\n";
        std::vector<Case> cases = {
            {"positive_high_rank", 200, 1000, 36000, 2, 10, 6, 1, 1},
            {"insufficient_vanishing_degree_control", 200, 1000, 36000, 2, 10, 1, 0, 1},
            {"insufficient_board_size_control", 40, 1000, 1476, 2, 10, 6, 1, 0}
        };
        for (unsigned q : {16u,24u,32u,40u,42u,44u,48u,56u,60u}) {
            const U64 n = U64(1) << q;
            const U64 N = U64(1) << (q/2-2);
            cases.push_back({"resistant_scale_q" + std::to_string(q),
                             N,n,(N*N-1)/4,q,q*q,rank_fraction_degree(n)});
        }
        unsigned certified = 0;
        for (const auto& c : cases) certified += run_case(c,out);
        out << "{\"type\":\"summary\",\"cases\":" << cases.size()
            << ",\"certified_parameter_cases\":" << certified
            << ",\"explicit_controls_passed\":true}\n";
        out.close();
        if (!out) throw std::runtime_error("output write failed");
        std::cout << "Saved all exact counts for " << cases.size() << " cases; "
                  << certified << " satisfy both hypotheses.\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << '\n';
        return 1;
    }
}
