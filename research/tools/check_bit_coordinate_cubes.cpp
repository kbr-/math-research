// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exhaustive finite checks of disjoint coordinate cubes and coefficient duals.
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
struct Counts { U64 families = 0, tuples = 0, boundary_pairs = 0; };

void check_family(std::ostream& out, int ell, const std::vector<int>& axes,
                  Counts& counts) {
    std::vector<Cube> cubes;
    std::vector<int> dimensions, representatives;
    U64 occupied = 0;
    int degree = 0;
    for (int mask : axes) {
        int dimension = weight(mask);
        dimensions.push_back(dimension);
        degree += dimension;
        bool found = false;
        for (int representative = 0; representative < (1 << ell); ++representative) {
            if (representative & mask) continue;
            Cube next = cube(ell, mask, representative);
            if (!(occupied & next.bitmap)) {
                occupied |= next.bitmap;
                representatives.push_back(representative);
                cubes.push_back(std::move(next));
                found = true;
                break;
            }
        }
        need(found, "greedy cube packing failed");
    }
    need(degree < ell, "positive family exceeds strict degree budget");
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
        for (int i = 1; i < argc; ++i) {
            std::string option = argv[i];
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
        out << "{\"type\":\"schema\",\"version\":1,\"field\":2,"
               "\"scope\":\"coordinate cubes, not full PHP NS matrices\","
               "\"label_bit_order\":\"least significant bit is coordinate zero\","
               "\"missing_row_basis_order\":\"mixed-radix cube indices, row zero first\"}\n";
        const U64 expected_families[] = {0, 0, 2, 15, 142, 1855, 31601};
        const U64 expected_tuples[] = {0, 0, 4, 54, 1024, 27310, 945304};
        Counts total;
        for (int ell = min_ell; ell <= max_ell; ++ell) {
            Counts current;
            std::vector<int> axes;
            std::function<void(int)> enumerate = [&](int remaining) {
                for (int mask = 1; mask < (1 << ell); ++mask) {
                    int dimension = weight(mask);
                    if (dimension > remaining) continue;
                    axes.push_back(mask);
                    check_family(out, ell, axes, current);
                    enumerate(remaining - dimension);
                    axes.pop_back();
                }
            };
            enumerate(ell - 1);
            boundary_control(out, ell, current);
            need(current.families == expected_families[ell], "family count");
            need(current.tuples == expected_tuples[ell], "tuple count");
            need(current.boundary_pairs == U64(1 << ell), "boundary count");
            out << "{\"type\":\"ell_summary\",\"ell\":" << ell
                << ",\"families\":" << current.families
                << ",\"tuples\":" << current.tuples
                << ",\"boundary_pairs\":" << current.boundary_pairs << "}\n";
            total.families += current.families;
            total.tuples += current.tuples;
            total.boundary_pairs += current.boundary_pairs;
        }
        out << "{\"type\":\"summary\",\"families\":" << total.families
            << ",\"tuples\":" << total.tuples
            << ",\"boundary_pairs\":" << total.boundary_pairs
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
