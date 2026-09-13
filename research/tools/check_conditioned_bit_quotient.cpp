// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact ingredients for conditioned target separation; not a large PHP matrix.
#include <boost/multiprecision/cpp_int.hpp>
#include <bitset>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using boost::multiprecision::cpp_int;
using U64 = std::uint64_t;
using Poly = std::bitset<1024>;
void need(bool condition, const std::string& why) {
    if (!condition) throw std::runtime_error(why);
}
template<class T> void array(std::ostream& out, const std::vector<T>& values) {
    out << '[';
    for (std::size_t i=0;i<values.size();++i) {
        if (i) out << ',';
        out << values[i];
    }
    out << ']';
}
std::vector<int> terms(const Poly& p) {
    std::vector<int> result;
    for (std::size_t i=p._Find_first();i<p.size();i=p._Find_next(i))
        result.push_back(int(i));
    return result;
}
int degree(int mask) { return __builtin_popcount(unsigned(mask)); }
int leading(const Poly& p) {
    int result=-1;
    for (int mask:terms(p))
        if (result<0 || degree(mask)>degree(result) ||
            (degree(mask)==degree(result) && mask>result)) result=mask;
    return result;
}
Poly multiply(const Poly& p, int monomial) {
    Poly result;
    for (int mask:terms(p)) result.flip(mask|monomial);
    return result;
}
U64 random_word(U64& state) {
    state ^= state << 13; state ^= state >> 7; state ^= state << 17;
    return state;
}
bool row_linear(int mask, int rows, int ell) {
    for (int i=0;i<rows;++i)
        if (degree((mask>>(ell*i))&((1<<ell)-1))>1) return false;
    return true;
}
void multiplication_case(const Poly& f, int id, const char* family,
                         std::ostream& out, U64& total_columns, U64& quadratic_rows) {
    constexpr int rows=5,ell=2,t=2;
    int lead=leading(f),d=degree(lead),allowed=(1<<(rows*ell))-1;
    need(lead>=0,"zero weight");
    for (int i=0;i<rows;++i)
        if ((lead>>(ell*i))&3) allowed &= ~(3<<(ell*i));
    out << "{\"type\":\"weight\",\"id\":" << id << ",\"family\":\"" << family
        << "\",\"rows\":5,\"ell\":2,\"multiplier_degree\":2,\"f_masks\":";
    array(out,terms(f));
    out << ",\"leading_mask\":" << lead << ",\"degree\":" << d
        << ",\"allowed_bit_mask\":" << allowed << "}\n";
    std::vector<Poly> pivots(1024);
    int rank=0;
    for (int monomial=0;monomial<1024;++monomial) {
        if ((monomial&~allowed) || degree(monomial)>t ||
            !row_linear(monomial,rows,ell)) continue;
        Poly product=multiply(f,monomial),reduced=product;
        need(leading(product)==(lead|monomial),"leading product changed");
        need(degree(leading(product))==d+degree(monomial),"degree lost");
        for (int mask:terms(product)) {
            need(degree(mask)<=d+t,"product total degree");
            if (!row_linear(mask,rows,ell)) ++quadratic_rows;
        }
        std::vector<int> reductions;
        int pivot=-1;
        for (int j=1023;j>=0;--j) if (reduced[j]) {
            if (pivots[j].any()) { reduced ^= pivots[j]; reductions.push_back(j); }
            else { pivot=j; pivots[j]=reduced; break; }
        }
        need(pivot>=0,"dependent candidate product");
        ++rank; ++total_columns;
        out << "{\"type\":\"multiplication_column\",\"weight\":" << id
            << ",\"multiplier_mask\":" << monomial << ",\"product_masks\":";
        array(out,terms(product));
        out << ",\"reductions\":"; array(out,reductions);
        out << ",\"pivot\":" << pivot << ",\"residual_masks\":";
        array(out,terms(reduced)); out << "}\n";
    }
    int remaining=rows-d;
    int expected=1+remaining*ell+remaining*(remaining-1)/2*ell*ell;
    need(rank==expected,"candidate dimension");
    out << "{\"type\":\"weight_summary\",\"id\":" << id
        << ",\"rank\":" << rank << ",\"expected\":" << expected << "}\n";
}
void cubes(std::ostream& out,U64& state) {
    constexpr int ell=7,n=128,K=8;
    need(16*(K-1)<n && K>ell,"new cube range");
    int cases=0,tuples=0;
    for (int pairs=0;pairs<=4;++pairs) for (int repeat=0;repeat<32;++repeat) {
        std::vector<int> axes;
        for (int i=0;i<K-pairs;++i) {
            int a=int(random_word(state)%ell),mask=1<<a;
            if (i<pairs) {
                int b=int(random_word(state)%(ell-1));
                if (b>=a) ++b;
                mask |= 1<<b;
            }
            axes.push_back(mask);
        }
        for (int i=int(axes.size())-1;i>0;--i)
            std::swap(axes[i],axes[random_word(state)%U64(i+1)]);
        std::vector<bool> occupied(n);
        std::vector<int> representatives;
        std::vector<std::vector<int>> points,parities;
        for (int mask:axes) {
            std::vector<int> subspaces;
            for (int z=0;z<n;++z) if (!(z&~mask)) subspaces.push_back(z);
            int found=-1;
            for (int a=0;a<n && found<0;++a) if (!(a&mask)) {
                bool good=true;
                for (int z:subspaces) if (occupied[a|z]) good=false;
                if (good) found=a;
            }
            need(found>=0,"disjoint coordinate cubes unavailable");
            representatives.push_back(found);
            for (int& z:subspaces) { z|=found; occupied[z]=true; }
            points.push_back(subspaces);
            parities.push_back(std::vector<int>(1<<(K-degree(mask))));
        }
        int coefficient=0;
        for (int tuple=0;tuple<(1<<K);++tuple) {
            std::vector<bool> used(n);
            int offset=0,value=1;
            for (std::size_t i=0;i<axes.size();++i) {
                int di=degree(axes[i]);
                int z=points[i][(tuple>>offset)&((1<<di)-1)];
                need(!used[z],"tuple has a collision");
                used[z]=true;
                value &= ((z&axes[i])==axes[i]);
                int context=(tuple&((1<<offset)-1))|((tuple>>(offset+di))<<offset);
                parities[i][context]^=1;
                offset+=di;
            }
            need(offset==K,"total cube dimension");
            coefficient ^= value; ++tuples;
        }
        need(coefficient==1,"coefficient dual");
        for (const auto& row:parities) for (int v:row)
            need(v==0,"missing-row dual");
        out << "{\"type\":\"cube_family\",\"id\":" << cases++ << ",\"ell\":7,"
               "\"total_degree\":8,\"maximum_row_degree\":2,\"axis_masks\":";
        array(out,axes); out << ",\"representatives\":"; array(out,representatives);
        out << ",\"points\":[";
        for (std::size_t i=0;i<points.size();++i) {
            if (i) out << ',';
            array(out,points[i]);
        }
        out << "],\"leading_coefficient\":1,\"missing_row_parities\":[";
        for (std::size_t i=0;i<parities.size();++i) {
            if (i) out << ',';
            array(out,parities[i]);
        }
        out << "]}\n";
    }
    need(cases==160 && tuples==40960,"cube counts");
    out << "{\"type\":\"cube_summary\",\"families\":160,\"tuples\":40960}\n";
}
void triangle_control(std::ostream& out) {
    Poly sum;
    for (int i=0;i<3;++i) for (int j=i+1;j<3;++j) {
        Poly equality; equality.set(0);
        for (int t=0;t<3;++t)
            equality ^= multiply(equality,1<<(3*i+t)) ^ multiply(equality,1<<(3*j+t));
        sum ^= equality;
        out << "{\"type\":\"control_equality\",\"rows\":[" << i << ',' << j
            << "],\"polynomial_masks\":"; array(out,terms(equality)); out << "}\n";
    }
    int maximum_row_degree=0;
    for (int mask:terms(sum)) for (int i=0;i<3;++i)
        maximum_row_degree=std::max(maximum_row_degree,degree((mask>>(3*i))&7));
    need(sum[0] && degree(leading(sum))==3 && maximum_row_degree==2,"triangle control");
    out << "{\"type\":\"old_relation_control\",\"n\":8,\"ell\":3,\"degree\":3,"
           "\"maximum_row_degree\":2,\"certificate\":\"sum of the three saved equalities\","
           "\"certificate_degree\":3,\"cube_condition\":false,\"polynomial_masks\":";
    array(out,terms(sum)); out << "}\n";
}
cpp_int row_dimension(U64 rows,U64 ell,U64 t) {
    cpp_int term=1,result=1;
    for (U64 j=1;j<=t && j<=rows;++j) {
        term=term*(rows-j+1)*ell/j; result+=term;
    }
    return result;
}
void dimensions(std::ostream& out) {
    struct Case { const char* name; U64 n,d,t,B; bool cubes,stable; };
    std::vector<Case> cases={
        {"finite-active",128,3,5,61,true,true},
        {"cube-criterion-inactive",128,4,5,60,false,true},
        {"stability-criterion-inactive",128,3,5,62,true,false},
        {"source-scale",U64(1)<<22,9216,9216,1843200,true,true}
    };
    for (const auto& c:cases) {
        U64 ell=__builtin_ctzll(c.n),m=c.n+1;
        bool cube=16*(c.d+c.t-1)<c.n,stable=c.B>=c.t && c.B+c.d<=c.n/2;
        need(cube==c.cubes && stable==c.stable,"dimension guard control");
        cpp_int lower=row_dimension(m-c.d,ell,c.t);
        cpp_int unconditioned=row_dimension(m,ell,c.t);
        out << "{\"type\":\"dimension_case\",\"name\":\"" << c.name << "\",\"n\":" << c.n
            << ",\"ell\":" << ell << ",\"weight_degree\":" << c.d
            << ",\"target_degree\":" << c.t << ",\"conditioned_budget\":" << c.B
            << ",\"cube_condition\":" << (cube?"true":"false")
            << ",\"stable_proper_range\":" << (stable?"true":"false")
            << ",\"candidate_dimension\":\"" << lower
            << "\",\"unconditioned_row_linear_dimension\":\"" << unconditioned
            << "\",\"naive_next_coefficient_degree\":" << c.t
            << ",\"naive_next_refutation_bound\":" << c.t*c.B
            << ",\"conditioned_PC_barrier\":" << c.n/2-c.d+1 << "}\n";
        std::cout << c.name << ": cube=" << cube << ", stable=" << stable << '\n';
    }
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];
        need(!std::filesystem::exists(path),"refusing existing output");
        if (!path.parent_path().empty()) std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path); need(bool(out),"cannot create output");
        U64 state=202609130110ULL,columns=0,quadratic_rows=0;
        out << "{\"type\":\"schema\",\"version\":1,\"field\":2,\"seed\":202609130110,"
               "\"polynomials\":\"arrays of squarefree bit-mask monomials\","
               "\"scope\":\"Boolean multiplication ranks, coefficient duals, one actual old-relation control, and exact dimension formulas\"}\n";
        int id=0;
        for (int choice=1;choice<(1<<11);++choice) {
            Poly f;
            if (choice&1) f.set(0);
            for (int bit=0;bit<10;++bit) if (choice&(1<<(bit+1))) f.set(1<<bit);
            multiplication_case(f,id++,"all_affine_weights",out,columns,quadratic_rows);
        }
        for (int trial=0;trial<128;++trial) {
            Poly f;
            int bound=2+trial%2;
            for (int mask=0;mask<1024;++mask)
                if (degree(mask)<=bound && row_linear(mask,5,2) &&
                    random_word(state)%4==0) f.flip(mask);
            need(f.any(),"random zero weight");
            multiplication_case(f,id++,"mixed_row_linear_weights",out,columns,quadratic_rows);
        }
        need(id==2175 && quadratic_rows>0,"nonvacuous multiplication suite");
        cubes(out,state);
        triangle_control(out);
        dimensions(out);
        out << "{\"type\":\"summary\",\"weights\":" << id << ",\"columns\":" << columns
            << ",\"product_terms_using_two_bits_in_a_row\":" << quadratic_rows
            << ",\"cube_families\":160,\"cube_tuples\":40960,"
               "\"old_relation_controls\":1,\"dimension_cases\":4,\"passed\":true}\n";
        out.close(); need(bool(out),"write failed");
        std::cout << "Passed " << id << " weights and " << columns
                  << " complete multiplication columns; 160 cube duals; one old relation; four ledgers.\n";
    } catch (const std::exception& error) {
        std::cerr << "ERROR: " << error.what() << '\n'; return 1;
    }
}
