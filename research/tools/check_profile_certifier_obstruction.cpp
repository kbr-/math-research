// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact approximate-majority circuit and certifying-polynomial rank controls.
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <random>
#include <stdexcept>
#include <vector>

using Matrix = std::vector<std::vector<int>>;
void require(bool ok, const char* message) {
    if (!ok) throw std::runtime_error(message);
}
int power_mod(int a, int e, int p) {
    int result = 1;
    for (; e; e >>= 1, a = a * a % p)
        if (e & 1) result = result * a % p;
    return result;
}
Matrix inverse_mod(Matrix a, int p) {
    const int n = a.size();
    Matrix inverse(n, std::vector<int>(n));
    for (int i = 0; i < n; ++i) inverse[i][i] = 1;
    for (int col = 0; col < n; ++col) {
        int pivot = col;
        while (pivot < n && a[pivot][col] == 0) ++pivot;
        require(pivot < n, "Hamming-ball evaluation matrix is invertible");
        std::swap(a[pivot], a[col]);
        std::swap(inverse[pivot], inverse[col]);
        const int scale = power_mod(a[col][col], p - 2, p);
        for (int j = 0; j < n; ++j) {
            a[col][j] = a[col][j] * scale % p;
            inverse[col][j] = inverse[col][j] * scale % p;
        }
        for (int i = 0; i < n; ++i) if (i != col) {
            const int factor = a[i][col];
            for (int j = 0; j < n; ++j) {
                a[i][j] = (a[i][j] - factor * a[col][j] % p + p) % p;
                inverse[i][j] = (inverse[i][j] - factor * inverse[col][j] % p + p) % p;
            }
        }
    }
    return inverse;
}
void verify_inverse(const Matrix& a, const Matrix& b, int p) {
    const int n = a.size();
    for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) {
        int ab = 0, ba = 0;
        for (int k = 0; k < n; ++k) {
            ab = (ab + a[i][k] * b[k][j]) % p;
            ba = (ba + b[i][k] * a[k][j]) % p;
        }
        require(ab == (i == j) && ba == (i == j), "two-sided inverse certificate");
    }
}
void vector_json(std::ostream& out, const std::vector<int>& row) {
    out << '[';
    for (unsigned i = 0; i < row.size(); ++i) {
        if (i) out << ',';
        out << row[i];
    }
    out << ']';
}
void matrix_json(std::ostream& out, const Matrix& a) {
    out << '[';
    for (unsigned i = 0; i < a.size(); ++i) {
        if (i) out << ',';
        vector_json(out, a[i]);
    }
    out << ']';
}
int main(int argc, char** argv) {
    try {
        require(argc == 3 && std::string(argv[1]) == "--out", "usage: --out NEW_PATH");
        const std::filesystem::path path = argv[2];
        require(!std::filesystem::exists(path), "output already exists");
        if (path.has_parent_path()) std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);
        require(bool(out), "output open");
        constexpr int v = 8, universe = 1 << v, a = v / 3;
        constexpr unsigned seed = 1490001;
        int t = 0;
        while ((1 << t) < v * v * v) ++t;
        int three_power = 1;
        for (int i = 0; i < t; ++i) three_power *= 3;
        const int r = (4 * v * three_power + (1 << t) - 1) / (1 << t);
        std::mt19937 rng(seed);
        Matrix circuit(v, std::vector<int>(r));
        for (auto& group : circuit) for (int& mask : group) {
            mask = 0;
            for (int j = 0; j < t; ++j) mask |= 1 << (rng() & (v - 1));
        }
        std::vector<int> truth(universe), basis, low, high;
        for (int point = 0; point < universe; ++point) {
            int value = 1;
            for (const auto& group : circuit) {
                bool accepted = false;
                for (int mask : group)
                    if ((point & mask) == mask) { accepted = true; break; }
                if (!accepted) { value = 0; break; }
            }
            truth[point] = value;
            int weight = __builtin_popcount(unsigned(point));
            if (weight <= a) require(value == 0, "low Hamming-ball value");
            if (weight >= v - a) require(value == 1, "high Hamming-ball value");
            if (weight <= a) {
                basis.push_back(point);
                low.push_back(point);
                high.push_back((universe - 1) ^ point);
            }
        }
        require(basis.size() == 37 && t == 9 && r == 1231, "exact fixture parameters");
        out << "{\"record\":\"schema\",\"version\":1,\"masks\":\"bit i denotes old variable i\","
               "\"circuit\":\"AND of groups; each group is an OR of positive AND masks\","
               "\"repeated_literals\":\"sampling repetitions removed inside each AND; repeated terms retained\"}\n";
        out << "{\"record\":\"circuit\",\"variables\":" << v << ",\"seed\":" << seed
            << ",\"sampled_width\":" << t << ",\"terms_per_group\":" << r
            << ",\"groups\":"; matrix_json(out, circuit); out << "}\n";
        out << "{\"record\":\"truth_table\",\"values\":"; vector_json(out, truth);
        out << ",\"order\":\"increasing old-bit mask\",\"passed\":true}\n";
        int ranks = 0, positives = 0;
        for (int p : {2, 3, 5}) for (int side : {0, 1}) {
            const auto& points = side == 0 ? low : high;
            Matrix evaluation(points.size(), std::vector<int>(basis.size()));
            for (unsigned i = 0; i < points.size(); ++i) {
                require(truth[points[i]] == side, "opposite-output interpolation points");
                for (unsigned j = 0; j < basis.size(); ++j)
                    evaluation[i][j] = (points[i] & basis[j]) == basis[j];
            }
            const auto inverse = inverse_mod(evaluation, p);
            verify_inverse(evaluation, inverse, p);
            out << "{\"record\":\"certifier_rank_certificate\",\"prime\":" << p
                << ",\"vanishing_output\":" << side << ",\"degree_cap\":" << a
                << ",\"rank\":37,\"row_masks\":"; vector_json(out, points);
            out << ",\"monomial_masks\":"; vector_json(out, basis);
            out << ",\"evaluation_matrix\":"; matrix_json(out, evaluation);
            out << ",\"inverse\":"; matrix_json(out, inverse);
            out << ",\"passed\":true}\n";
            ++ranks;
        }
        for (int side : {0, 1}) {
            int chosen = -1, best = side == 0 ? -1 : v + 1;
            for (int point = 0; point < universe; ++point) if (truth[point] == side) {
                const int weight = __builtin_popcount(unsigned(point));
                if ((side == 0 && weight > best) || (side == 1 && weight < best)) {
                    chosen = point; best = weight;
                }
            }
            require(chosen >= 0, "nonempty output side");
            const int literal_mask = side == 0 ? ((universe - 1) ^ chosen) : chosen;
            const int degree = __builtin_popcount(unsigned(literal_mask));
            require(degree > a, "positive certificate is above the forbidden degree window");
            std::vector<int> support;
            for (int point = 0; point < universe; ++point) {
                const bool present = side == 0 ? (point & literal_mask) == 0 :
                                                (point & literal_mask) == literal_mask;
                if (present) {
                    require(truth[point] == side, "positive certificate support is monochromatic");
                    support.push_back(point);
                }
            }
            require(!support.empty(), "nonzero positive certificate");
            out << "{\"record\":\"positive_certifier\",\"output\":" << side
                << ",\"literal_value\":" << side << ",\"literal_mask\":" << literal_mask
                << ",\"polynomial\":\"product of x_i for value one, product of (1-x_i) for value zero\","
                   "\"degree\":" << degree << ",\"support_masks\":";
            vector_json(out, support);
            out << ",\"fields\":[2,3,5],\"passed\":true}\n";
            ++positives;
        }
        for (int h : {1, 2, 6}) {
            int w1 = 2*h, w2 = h*(w1+1), w3 = h*(w2+1);
            out << "{\"record\":\"source_degree_ledger\",\"accuracy\":" << h
                << ",\"bottom_weight\":" << w1 << ",\"middle_weight\":" << w2
                << ",\"top_weight\":" << w3
                << ",\"scope\":\"symbolic three-level evaluation source; not an expanded source-model enumeration\"}\n";
        }
        out << "{\"record\":\"summary\",\"old_assignments\":256,\"bottom_terms\":9848,"
               "\"invertible_evaluation_certificates\":" << ranks
            << ",\"positive_certifiers\":" << positives << ",\"passed\":true}\n";
        require(bool(out), "output write");
        std::cout << "Approximate-majority circuit: 256 assignments, six exact rank certificates, "
                     "and two positive certifiers passed.\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << '\n';
        return 1;
    }
}
