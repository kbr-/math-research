// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact GF(4) moment-pairing and density-projection controls.
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using Vec = std::vector<int>;
using Mat = std::vector<Vec>;

void need(bool b, const char* message) { if (!b) throw std::runtime_error(message); }
int mul(int a, int b) {
    int result = 0;
    for (; b; b >>= 1) {
        if (b & 1) result ^= a;
        a <<= 1;
        if (a & 4) a ^= 7; // theta^2 + theta + 1
    }
    return result;
}
int inv(int a) { need(a != 0, "inverse of zero"); return mul(a, a); }
void write(std::ostream& out, const Vec& a) {
    out << '[';
    for (unsigned i = 0; i < a.size(); ++i) { if (i) out << ','; out << a[i]; }
    out << ']';
}
void write(std::ostream& out, const Mat& a) {
    out << '[';
    for (unsigned i = 0; i < a.size(); ++i) { if (i) out << ','; write(out, a[i]); }
    out << ']';
}
struct Solve { Vec solution, pivots; int determinant = 1; };
Solve solve(Mat a, Vec rhs) {
    const int n = int(a.size());
    need(int(rhs.size()) == n, "square solve size");
    Solve answer;
    for (int c = 0; c < n; ++c) {
        int pivot = c;
        while (pivot < n && !a[pivot][c]) ++pivot;
        need(pivot < n, "singular matrix in required nondegenerate control");
        answer.pivots.push_back(pivot);
        std::swap(a[c], a[pivot]); std::swap(rhs[c], rhs[pivot]);
        int d = a[c][c];
        answer.determinant = mul(answer.determinant, d);
        int scale = inv(d);
        for (int j = c; j < n; ++j) a[c][j] = mul(a[c][j], scale);
        rhs[c] = mul(rhs[c], scale);
        for (int i = 0; i < n; ++i) if (i != c && a[i][c]) {
            int factor = a[i][c];
            for (int j = c; j < n; ++j) a[i][j] ^= mul(factor, a[c][j]);
            rhs[i] ^= mul(factor, rhs[c]);
        }
    }
    answer.solution = rhs; return answer;
}
int eval(const Vec& coefficients, int point) {
    int result = 0;
    for (unsigned mask = 0; mask < coefficients.size(); ++mask)
        if ((int(mask) & point) == int(mask)) result ^= coefficients[mask];
    return result;
}
int mean(const Vec& weights, const Vec& values, int monomial = 0) {
    int result = 0;
    for (unsigned point = 0; point < weights.size(); ++point)
        if ((int(point) & monomial) == monomial) result ^= mul(weights[point], values[point]);
    return result;
}
void one_case(std::ostream& out, int variables) {
    const int points = 1 << variables, top = points - 1, last = 1 << (variables - 1);
    const int cutoff = variables - 1;
    Vec weights(points, 1); weights[0] = 2; weights[1] = 3;
    Vec ones(points, 1), moments(points);
    need(mean(weights, ones) == 1, "normalization");
    for (int mask = 0; mask < points; ++mask) moments[mask] = mean(weights, ones, mask);
    Mat gram(top, Vec(top));
    for (int i = 0; i < top; ++i) for (int j = 0; j < top; ++j)
        gram[i][j] = moments[i | j];
    Vec full_rhs(top); full_rhs[0] = 1;
    auto full_solve = solve(gram, full_rhs);
    Vec ids_a, ids_c;
    for (int mask = 1; mask < top; ++mask) {
        ids_c.push_back(mask);
        if (mask != last) ids_a.push_back(mask);
    }
    auto projection = [&](const Vec& ids, Mat& subgram, Solve& solution) {
        subgram.assign(ids.size(), Vec(ids.size())); Vec rhs(ids.size());
        for (unsigned i = 0; i < ids.size(); ++i) {
            rhs[i] = moments[ids[i]];
            for (unsigned j = 0; j < ids.size(); ++j) subgram[i][j] = gram[ids[i]][ids[j]];
        }
        solution = solve(subgram, rhs);
        Vec p(top); p[0] = 1;
        for (unsigned i = 0; i < ids.size(); ++i) p[ids[i]] ^= solution.solution[i];
        return p;
    };
    Mat gram_a, gram_c; Solve solve_a, solve_c;
    Vec p_a = projection(ids_a, gram_a, solve_a), p_c = projection(ids_c, gram_c, solve_c);
    Vec expected_a(top), expected_c(top), corrected_c(top);
    for (int mask = 0; mask < top; ++mask) {
        if ((mask & last) == 0) expected_a[mask] = 1;
        if ((mask & 1) == 0) expected_c[mask] = 2;
    }
    expected_c[0] ^= 3;
    need(p_a == expected_a && p_c == expected_c, "explicit projection polynomials");
    for (int mask = 0; mask < top; ++mask) corrected_c[mask] = mul(2, p_c[mask]);
    Vec values_a(points), values_c(points), values_corrected(points), true_c(points), child_weighted(points);
    Vec squared_corrected(points);
    for (int point = 0; point < points; ++point) {
        values_a[point] = eval(p_a, point); values_c[point] = eval(p_c, point);
        values_corrected[point] = eval(corrected_c, point);
        true_c[point] = point == 0;
        child_weighted[point] = mul(values_a[point], 1 ^ int(bool(point & last)));
        squared_corrected[point] = mul(values_corrected[point], values_corrected[point]);
    }
    for (int id : ids_a) need(mean(weights, values_a, id) == 0, "A orthogonality");
    for (int id : ids_c) need(mean(weights, values_c, id) == 0, "C orthogonality");
    for (int mask = 0; mask < top; ++mask)
        need(mean(weights, values_corrected, mask) == mean(weights, true_c, mask),
             "corrected density matches every old query through cutoff");
    const int left = mean(weights, values_c), right = mean(weights, child_weighted);
    need(left == 1 && right == 2 && (left ^ right) == 3, "mixed-port counterexample");
    need((mean(weights, values_corrected) ^ right) == 0, "corrected mixed port");
    const int power_error = mean(weights, squared_corrected) ^ mean(weights, values_corrected);
    need(power_error == 1, "density multiplication must not replace selector-support moments");
    out << "{\"record\":\"case\",\"old_variables\":" << variables
        << ",\"density_cutoff\":" << cutoff << ",\"source_degree_budget\":5,\"budget_eligible\":"
        << (cutoff >= 5 ? "true" : "false") << ",\"basis_masks\":[";
    for (int mask = 0; mask < top; ++mask) { if (mask) out << ','; out << mask; }
    out << "],\"weights\":"; write(out, weights);
    out << ",\"all_old_moments\":"; write(out, moments);
    out << ",\"full_gram\":"; write(out, gram);
    out << ",\"full_determinant\":" << full_solve.determinant << ",\"full_pivots\":"; write(out, full_solve.pivots);
    out << ",\"A_ideal_basis\":"; write(out, ids_a);
    out << ",\"A_gram\":"; write(out, gram_a);
    out << ",\"A_determinant\":" << solve_a.determinant << ",\"A_projection_density\":"; write(out, p_a);
    out << ",\"C_ideal_basis\":"; write(out, ids_c);
    out << ",\"C_gram\":"; write(out, gram_c);
    out << ",\"C_determinant\":" << solve_c.determinant << ",\"C_projection_density\":"; write(out, p_c);
    out << ",\"corrected_C_density\":"; write(out, corrected_c);
    out << ",\"mixed_port_value\":" << (left ^ right) << ",\"corrected_port_value\":0,\"multiplicative_density_Booleanity_error\":"
        << power_error << ",\"complete_source_models\":[";
    for (int point = 0; point < points; ++point) {
        if (point) out << ',';
        Vec old(variables), a_coefficients(variables - 1), c_coefficients(variables);
        int a_value = 1, c_value = 1;
        for (int i = 0; i < variables; ++i) {
            old[i] = (point >> i) & 1;
            if (old[i] && c_value) { c_coefficients[i] = 1; c_value = 0; }
            if (i < variables - 1 && old[i] && a_value) { a_coefficients[i] = 1; a_value = 0; }
        }
        for (int i = 0; i < variables; ++i) {
            need(old[i] * c_value == 0, "C companion");
            if (i < variables - 1) need(old[i] * a_value == 0, "A companion");
        }
        for (int x : a_coefficients) need((mul(x, x) ^ x) == 0, "A coefficient field");
        for (int x : c_coefficients) need((mul(x, x) ^ x) == 0, "C coefficient field");
        need((c_value ^ mul(a_value, 1 ^ old.back())) == 0, "genuine mixed source port");
        out << "{\"old_bits\":"; write(out, old);
        out << ",\"functional_weight\":" << weights[point] << ",\"A_coefficients\":"; write(out, a_coefficients);
        out << ",\"C_coefficients\":"; write(out, c_coefficients);
        out << ",\"A_product\":" << a_value << ",\"C_product\":" << c_value
            << ",\"all_companions_and_fields_zero\":true}";
    }
    out << "],\"passed\":true}\n";
}
int main(int argc, char** argv) {
    try {
        need(argc == 3 && std::string(argv[1]) == "--out", "usage: --out NEW_PATH");
        std::filesystem::path path = argv[2]; need(!std::filesystem::exists(path), "output exists");
        if (path.has_parent_path()) std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path); need(bool(out), "open output");
        out << "{\"record\":\"schema\",\"field\":\"GF(4), theta^2+theta+1=0\",\"elements\":[\"0\",\"1\",\"theta\",\"theta+1\"],"
               "\"polynomials\":\"coefficient vector indexed by listed squarefree monomial bit masks\","
               "\"source\":\"h=1, A inputs x_1,...,x_(r-1), C inputs x_1,...,x_r, P=1-sum_i coefficient_i*x_i; all companions x_i*P and own coefficient^2-coefficient equations retained\","
               "\"scope\":\"satisfiable Boolean-source controls; weights are functional values, not assignments of non-Boolean source coefficients\"}\n";
        for (int a : {0, 1, 2}) {
            const int determinant = a ^ mul(a, a);
            need(determinant == (a == 2 ? 1 : 0), "one-bit field-size control");
            out << "{\"record\":\"one_bit\",\"moment\":" << a << ",\"determinant\":" << determinant << "}\n";
        }
        one_case(out, 3); one_case(out, 6);
        out << "{\"record\":\"summary\",\"projection_cases\":2,\"nonsingular_matrices\":6,\"complete_source_models\":72,\"one_bit_controls\":3,\"passed\":true}\n";
        need(bool(out), "write output");
        std::cout << "Density controls passed: six nonsingular GF(4) matrices, 72 complete source models, "
                     "and both expected mixed-port and density-squaring failures.\n";
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
