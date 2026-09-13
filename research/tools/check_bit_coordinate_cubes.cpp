// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exhaustive finite checks of disjoint coordinate cubes and coefficient duals.
#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using U64 = std::uint64_t;
void need(bool value, const std::string& message) {
    if (!value) throw std::runtime_error(message);
}
int weight(int mask) { return __builtin_popcount(unsigned(mask)); }
template<class T> void array(std::ostream& out, const std::vector<T>& values) {
    out << '[';
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i) out << ',';
        out << values[i];
    }
    out << ']';
}
struct Cube {
    int axes, representative;
    U64 bitmap = 0;
    std::vector<int> points;
};
Cube cube(int ell, int axes, int representative) {
    Cube result{axes, representative, 0, {}};
    need(!(axes & representative), "noncanonical coset representative");
    for (int sub = 0; sub < (1 << ell); ++sub) if (!(sub & ~axes)) {
        int point = representative | sub;
        result.points.push_back(point);
        result.bitmap |= U64(1) << point;
    }
    need(result.points.size() == (1U << weight(axes)), "cube cardinality");
    return result;
}
struct Counts { U64 families = 0, tuples = 0, boundary_pairs = 0, obstructions = 0; };

void check_family(std::ostream& out, int ell, const std::vector<int>& axes,
                  Counts& counts, bool critical = false) {
    std::vector<Cube> cubes(axes.size());
    std::vector<int> dimensions, representatives(axes.size()), order;
    U64 occupied = 0;
    int degree = 0;
    for (std::size_t i = 0; i < axes.size(); ++i) {
        dimensions.push_back(weight(axes[i]));
        degree += dimensions.back();
        order.push_back(int(i));
    }
    if (critical) std::stable_sort(order.begin(), order.end(),
        [&](int a, int b) { return dimensions[a] > dimensions[b]; });
    // At total degree three, the three unit-axis cubes require an explicit
    // choice: the first available cosets can block every final coset.
    if (critical && ell == 3 && axes.size() == 3) {
        std::vector<int> distinct = axes;
        std::sort(distinct.begin(), distinct.end());
        distinct.erase(std::unique(distinct.begin(), distinct.end()), distinct.end());
        if (distinct.size() == 1) {
            std::vector<int> other;
            for (int axis : {1, 2, 4}) if (axis != axes[0]) other.push_back(axis);
            representatives = {0, other[0], other[1]};
        } else if (distinct.size() == 2) {
            int repeated = std::count(axes.begin(), axes.end(), distinct[0]) == 2
                ? distinct[0] : distinct[1];
            int single = distinct[0] ^ distinct[1] ^ repeated;
            int outside = 7 ^ repeated ^ single;
            int seen = 0;
            for (int i = 0; i < 3; ++i)
                representatives[i] = axes[i] == repeated ? (seen++ ? single : 0) : outside;
        } else {
            representatives = {0, axes[2], axes[0] | axes[1]};
        }
        for (int i = 0; i < 3; ++i) {
            cubes[i] = cube(ell, axes[i], representatives[i]);
            need(!(occupied & cubes[i].bitmap), "exceptional cube placement");
            occupied |= cubes[i].bitmap;
        }
        order.clear();
    }
    for (int index : order) {
        int mask = axes[index];
        int dimension = weight(mask);
        need(dimension > 0, "empty coordinate axis set");
        bool found = false;
        for (int representative = 0; representative < (1 << ell); ++representative) {
            if (representative & mask) continue;
            Cube next = cube(ell, mask, representative);
            if (!(occupied & next.bitmap)) {
                occupied |= next.bitmap;
                representatives[index] = representative;
                cubes[index] = std::move(next);
                found = true;
                break;
            }
        }
        need(found, "greedy cube packing failed");
    }
    need(critical ? degree == ell : degree < ell, "incorrect total degree");
    std::vector<std::vector<int>> missing_row_parities;
    for (int dimension : dimensions)
        missing_row_parities.emplace_back(1 << (degree - dimension), 0);
    int top_coefficient = 0;
    for (int state = 0; state < (1 << degree); ++state) {
        U64 labels = 0;
        int offset = 0, monomial_value = 1;
        for (std::size_t i = 0; i < axes.size(); ++i) {
            int dimension = dimensions[i];
            int point = cubes[i].points[(state >> offset) & ((1 << dimension) - 1)];
            need(!(labels & (U64(1) << point)), "a product tuple repeats a hole");
            labels |= U64(1) << point;
            monomial_value &= ((point & axes[i]) == axes[i]);
            int context = (state & ((1 << offset) - 1))
                | ((state >> (offset + dimension)) << offset);
            missing_row_parities[i][context] ^= 1;
            offset += dimension;
        }
        top_coefficient ^= monomial_value;
        ++counts.tuples;
    }
    need(top_coefficient == 1, "mixed difference misses its leading monomial");
    for (const auto& parities : missing_row_parities)
        for (int parity : parities) need(parity == 0, "missing-row potential survives");
    out << "{\"type\":\"family\",\"ell\":" << ell
        << ",\"id\":" << counts.families++ << ",\"axes\":";
    array(out, axes);
    out << ",\"dimensions\":"; array(out, dimensions);
    out << ",\"degree\":" << degree << ",\"representatives\":";
    array(out, representatives);
    out << ",\"cubes\":[";
    for (std::size_t i = 0; i < cubes.size(); ++i) {
        if (i) out << ',';
        array(out, cubes[i].points);
    }
    out << "],\"tuple_count\":" << (1 << degree)
        << ",\"top_coefficient\":" << top_coefficient
        << ",\"missing_row_basis_parities\":[";
    for (std::size_t i = 0; i < missing_row_parities.size(); ++i) {
        if (i) out << ',';
        array(out, missing_row_parities[i]);
    }
    out << "]}\n";
}

void critical_obstruction(std::ostream& out, int ell, const std::vector<int>& axes,
                          Counts& counts) {
    need(axes.size() == 2 && !(axes[0] & axes[1])
         && (axes[0] | axes[1]) == (1 << ell) - 1, "wrong obstruction axes");
    ++counts.obstructions;
    out << "{\"type\":\"critical_obstruction\",\"ell\":" << ell << ",\"axes\":";
    array(out, axes); out << "}\n";
    for (int a = 0; a < (1 << ell); ++a) if (!(a & axes[0]))
        for (int b = 0; b < (1 << ell); ++b) if (!(b & axes[1])) {
            Cube A = cube(ell, axes[0], a), B = cube(ell, axes[1], b);
            U64 intersection = A.bitmap & B.bitmap;
            need(__builtin_popcountll(intersection) == 1, "critical intersection");
            ++counts.boundary_pairs;
            out << "{\"type\":\"critical_intersection\",\"ell\":" << ell
                << ",\"axes\":"; array(out, axes);
            out << ",\"representatives\":[" << a << ',' << b
                << "],\"intersection\":" << __builtin_ctzll(intersection) << "}\n";
        }
}

void boundary_control(std::ostream& out, int ell, Counts& counts) {
    int first = 1, second = ((1 << ell) - 1) ^ first;
    for (int a = 0; a < (1 << ell); ++a) if (!(a & first))
        for (int b = 0; b < (1 << ell); ++b) if (!(b & second)) {
            Cube A = cube(ell, first, a), B = cube(ell, second, b);
            U64 intersection = A.bitmap & B.bitmap;
            need(__builtin_popcountll(intersection) == 1,
                 "complementary boundary cubes do not meet exactly once");
            ++counts.boundary_pairs;
            out << "{\"type\":\"boundary\",\"ell\":" << ell
                << ",\"degree\":" << ell << ",\"axes\":[" << first << ','
                << second << "],\"representatives\":[" << a << ',' << b
                << "],\"cubes\":[";
            array(out, A.points); out << ','; array(out, B.points);
            out << "],\"intersection\":" << __builtin_ctzll(intersection) << "}\n";
        }
}

int main(int argc, char** argv) {
    try {
        std::filesystem::path output;
        int min_ell = 2, max_ell = 6;
        bool critical = false;
        for (int i = 1; i < argc; ++i) {
            std::string option = argv[i];
            if (option == "--critical") { critical = true; continue; }
            need(i + 1 < argc, "option requires a value");
            if (option == "--out") output = argv[++i];
            else if (option == "--min-ell") min_ell = std::stoi(argv[++i]);
            else if (option == "--max-ell") max_ell = std::stoi(argv[++i]);
            else throw std::runtime_error("unknown option: " + option);
        }
        need(!output.empty(), "required: --out NEW_PATH");
        need(2 <= min_ell && min_ell <= max_ell && max_ell <= 6,
             "supported range: 2 <= min-ell <= max-ell <= 6");
        need(!std::filesystem::exists(output), "refusing to replace existing output");
        if (!output.parent_path().empty())
            std::filesystem::create_directories(output.parent_path());
        std::ofstream out(output);
        need(bool(out), "cannot create output");
        out << "{\"type\":\"schema\",\"version\":2,\"field\":2,\"critical\":"
            << (critical ? "true" : "false") << ',' <<
               "\"scope\":\"coordinate cubes, not full PHP NS matrices\","
               "\"label_bit_order\":\"least significant bit is coordinate zero\","
               "\"missing_row_basis_order\":\"mixed-radix cube indices, row zero first\"}\n";
        const U64 expected_families[] = {0, 0, 2, 15, 142, 1855, 31601};
        const U64 expected_tuples[] = {0, 0, 4, 54, 1024, 27310, 945304};
        const U64 critical_families[] = {0, 0, 5, 46, 613, 10626, 226454};
        Counts total;
        for (int ell = min_ell; ell <= max_ell; ++ell) {
            Counts current;
            std::vector<int> axes;
            std::function<void(int)> enumerate = [&](int remaining) {
                for (int mask = 1; mask < (1 << ell); ++mask) {
                    int dimension = weight(mask);
                    if (dimension > remaining) continue;
                    axes.push_back(mask);
                    if (!critical) check_family(out, ell, axes, current);
                    else if (dimension == remaining) {
                        if (axes.size() == 2 && !(axes[0] & axes[1]))
                            critical_obstruction(out, ell, axes, current);
                        else check_family(out, ell, axes, current, true);
                    }
                    enumerate(remaining - dimension);
                    axes.pop_back();
                }
            };
            enumerate(critical ? ell : ell - 1);
            if (critical) {
                need(current.families + current.obstructions == critical_families[ell],
                     "critical family count");
                need(current.obstructions == U64((1 << ell) - 2), "obstruction count");
                need(current.tuples == current.families * (1 << ell), "critical tuple count");
                need(current.boundary_pairs == current.obstructions * (1 << ell),
                     "critical intersection count");
            } else {
                boundary_control(out, ell, current);
                need(current.families == expected_families[ell], "family count");
                need(current.tuples == expected_tuples[ell], "tuple count");
                need(current.boundary_pairs == U64(1 << ell), "boundary count");
            }
            out << "{\"type\":\"ell_summary\",\"ell\":" << ell
                << ",\"families\":" << current.families
                << ",\"tuples\":" << current.tuples
                << ",\"boundary_pairs\":" << current.boundary_pairs
                << ",\"obstructions\":" << current.obstructions << "}\n";
            total.families += current.families;
            total.tuples += current.tuples;
            total.boundary_pairs += current.boundary_pairs;
            total.obstructions += current.obstructions;
        }
        out << "{\"type\":\"summary\",\"families\":" << total.families
            << ",\"tuples\":" << total.tuples
            << ",\"boundary_pairs\":" << total.boundary_pairs
            << ",\"obstructions\":" << total.obstructions
            << ",\"passed\":true}\n";
        out.close();
        need(bool(out), "output write failed");
        std::cout << "Passed " << total.families << " cube families, "
                  << total.tuples << " injective tuples, and "
                  << total.boundary_pairs << " boundary controls; full output "
                  << output << '\n';
    } catch (const std::exception& error) {
        std::cerr << "ERROR: " << error.what() << '\n';
        return 1;
    }
}
