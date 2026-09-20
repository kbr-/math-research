// Finite controls for support-restricted affine-span stratum interpolation.
// Build with C++17; --out persists every tested point and coefficient image.
#include <array>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

int mod(int x, int p) { x %= p; return x < 0 ? x + p : x; }
int power(int x, int e, int p) {
    int y = 1;
    while (e > 0) { if (e & 1) y = mod(y * x, p); x = mod(x * x, p); e >>= 1; }
    return y;
}
std::vector<int> normalizer(const std::vector<int>& q, int p) {
    std::vector<int> beta;
    int prefix = 1;
    for (int x : q) {
        beta.push_back(mod(power(x, p - 2, p) * prefix, p));
        prefix = mod(prefix * (1 - power(x, p - 1, p)), p);
    }
    return beta;
}
std::vector<int> inputs(int a, const std::array<int,3>& zeta, int x, int z, int p) {
    if (a == 0) return {zeta[0], zeta[1], mod(z + zeta[2], p)};
    return {mod(x + zeta[0] + zeta[1], p), mod(z + 2*zeta[0] + zeta[1], p)};
}
void array_json(std::ostream& out, const std::vector<int>& v) {
    out << '[';
    for (std::size_t i=0; i<v.size(); ++i) { if (i) out << ','; out << v[i]; }
    out << ']';
}
int main(int argc, char** argv) {
    if (argc != 3 || std::string(argv[1]) != "--out") {
        std::cerr << "Usage: check_flat_stratum_map --out FILE.json\n"; return 2;
    }
    std::filesystem::path destination(argv[2]);
    if (!destination.parent_path().empty()) std::filesystem::create_directories(destination.parent_path());
    std::ofstream out(destination);
    if (!out) throw std::runtime_error("Cannot open output file");
    int failures=0, weighted_checks=0, field_checks=0, partition_checks=0;
    std::array<int,3> negative_companion{}, negative_partition{};
    out << "{\n\"scope\":\"Pointwise finite controls, not graph separation or an asymptotic proof\","
        << "\n\"fields\":[2,3,5],\"old_variables\":[\"x\",\"y\",\"z\"],"
        << "\n\"bottom_inputs\":[\"x\",\"y\",\"x+y\"],"
        << "\n\"rank_cutoff\":1,\"parent_input_counts\":[3,2],\n\"points\":[\n";
    bool first=true;
    const std::array<int,3> primes{2,3,5};
    for (std::size_t ip=0; ip<primes.size(); ++ip) {
        const int p=primes[ip];
        for (int x=0; x<2; ++x) for (int y=0; y<2; ++y) for (int z=0; z<2; ++z) {
            const std::array<int,3> g{x,y,mod(x+y,p)};
            std::array<int,3> bottom_beta{}, zeta{};
            for (int i=0; i<3; ++i) {
                bottom_beta[i]=power(g[i],p-2,p);
                zeta[i]=mod(1-bottom_beta[i]*g[i],p);
                ++field_checks;
                if (mod(power(bottom_beta[i],p,p)-bottom_beta[i],p)) ++failures;
                if (mod(g[i]*zeta[i],p)) ++failures;
            }
            const int f = p == 2 ? x : mod(power(x,p-1,p)+power(y,p-1,p),p);
            if (!first) out << ",\n";
            first=false;
            out << "{\"p\":"<<p<<",\"old\":["<<x<<','<<y<<','<<z<<"],\"f\":"<<f
                <<",\"bottom_beta\":";
            array_json(out,{bottom_beta.begin(),bottom_beta.end()});
            out << ",\"bottom_products\":";
            array_json(out,{zeta.begin(),zeta.end()});
            out << ",\"parents\":[";
            for (int a=0; a<2; ++a) {
                const int m = a == 0 ? 3 : 2;
                std::vector<int> pi(m+1,0);
                pi[0]=1;
                int active=0, active_index=0;
                for (int c=0; c<m; ++c) {
                    pi[c+1]=zeta[c]; pi[0]=mod(pi[0]-zeta[c],p);
                    if (zeta[c]) { ++active; active_index=c+1; }
                }
                bool partition_ok=active<=1;
                for (int u=0; u<=m; ++u)
                    partition_ok = partition_ok && pi[u] == (u==active_index ? 1 : 0);
                if (f) { ++partition_checks; if (!partition_ok) ++failures; }
                else if (!partition_ok) ++negative_partition[ip];
                const auto q=inputs(a,zeta,x,z,p);
                std::vector<int> beta(q.size(),0);
                for (int u=0; u<=m; ++u) {
                    std::array<int,3> reference_pattern{0,0,0};
                    if (u) reference_pattern[u-1]=1;
                    const auto gamma=normalizer(inputs(a,reference_pattern,x,z,p),p);
                    for (std::size_t i=0; i<beta.size(); ++i)
                        beta[i]=mod(beta[i]+pi[u]*gamma[i],p);
                }
                int product=1, expected=1;
                for (std::size_t i=0; i<q.size(); ++i) {
                    product=mod(product-beta[i]*q[i],p);
                    expected=mod(expected*(1-power(q[i],p-1,p)),p);
                    ++field_checks;
                    if (mod(power(beta[i],p,p)-beta[i],p)) ++failures;
                }
                if (f && product!=expected) ++failures;
                for (int input:q) {
                    ++weighted_checks;
                    if (mod(f*input*product,p)) ++failures;
                    if (!f && mod(input*product,p)) ++negative_companion[ip];
                }
                if (a) out << ',';
                out << "{\"a\":"<<a<<",\"pi\":";
                array_json(out,pi); out << ",\"inputs\":"; array_json(out,q);
                out << ",\"beta\":"; array_json(out,beta);
                out << ",\"product\":"<<product<<",\"expected_zero_indicator\":"<<expected
                    <<",\"partition_correct\":"<<(partition_ok ? "true" : "false")<<'}';
            }
            out << "]}";
        }
        if (!negative_companion[ip] || !negative_partition[ip]) ++failures;
    }
    out << "\n],\"weighted_companion_checks\":"<<weighted_checks
        <<",\"coefficient_field_checks\":"<<field_checks
        <<",\"support_partition_checks\":"<<partition_checks
        <<",\"negative_control\":\"Replace f by one without excluding the rank-two intersection\","
        <<"\"negative_companion_failures_by_prime\":";
    array_json(out,{negative_companion.begin(),negative_companion.end()});
    out << ",\"negative_partition_failures_by_prime\":";
    array_json(out,{negative_partition.begin(),negative_partition.end()});
    out << ",\"unexpected_failures\":"<<failures<<",\"passed\":"<<(failures ? "false":"true")<<"\n}\n";
    out.close();
    std::cout << "24 Boolean points; " << weighted_checks << " weighted companions; "
              << field_checks << " fields; " << partition_checks << " support partitions.\n"
              << "Missing-boundary controls fail over every tested prime. Unexpected failures: "
              << failures << ". Complete output: " << destination.string() << '\n';
    return failures ? 1 : 0;
}
