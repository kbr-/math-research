// Exact polynomial-calculus degree over F_2 of the two-partition counting family.
//
// Statement computed (side notebook near-half-pc-degree, review entry-2026-10-10-obstacle-review): m Boolean
// variables, w even, w | m.  A-blocks are {0..w-1}, {w..2w-1}, ...; B-blocks are given by a second partition
// into blocks of size w.  Axioms: every product of w/2+1 variables of one A-block (weight of the block at most
// w/2) and every product of w/2 factors (1 + x_i) of one B-block (weight of the block at least w/2+1).  The
// system is unsatisfiable by counting.  The program works in y_i = 1 + x_i, where the B-axioms are the
// monomials on w/2 variables of one B-block, and in the quotient by them: basis the multilinear monomials
// with at most w/2-1 variables in every B-block.  For d = w/2+1, w/2+2, ... it computes the degree-d closure
// of the A-axioms prod_{i in T} (1 + y_i) in that quotient (span closed under multiplication of members of
// degree < d by a variable) and reports the least d with 1 in the closure: the PC refutation degree, which
// is at most m/2 - m/w + 1 because the quotient has no monomial above degree m/2 - m/w.
//
// Second partitions: "same" (B = A, a control: each block is contradictory alone), "spread" (B(i) = i mod m/w),
// and "random" with a seed (Fisher-Yates on splitmix64).  Output: one JSON line per instance.
// Usage: two_partition_degree M W [dmax=D] KIND[:SEED] [KIND[:SEED] ...]   (m <= 30); dmax stops the search at
// degree D, and the degree is then reported as null when 1 is not reached.
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

typedef uint32_t Mask;
typedef std::vector<uint64_t> Row;

static uint64_t splitmix(uint64_t &s) {
    uint64_t z = (s += 0x9e3779b97f4a7c15ULL);
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}

struct Instance {
    int m, w, cap;
    std::vector<int> bblock;          // variable -> B-block
    std::vector<Mask> bmask;          // B-block -> mask
    std::vector<Mask> monos;          // sorted by degree descending, then by value
    std::vector<int> start;           // unused
    int nwords;

    bool allowed(Mask t) const {
        for (Mask b : bmask) if (__builtin_popcount(t & b) > cap) return false;
        return true;
    }
    int index(Mask t) const {
        int deg = __builtin_popcount(t);
        auto cmp = [](Mask a, Mask b) {
            int da = __builtin_popcount(a), db = __builtin_popcount(b);
            return da != db ? da > db : a < b;
        };
        auto it = std::lower_bound(monos.begin(), monos.end(), t, cmp);
        (void)deg;
        return (it != monos.end() && *it == t) ? int(it - monos.begin()) : -1;
    }
    void enumerate(int d) {
        monos.clear();
        for (Mask t = 0; t < (Mask(1) << m); ++t)
            if (__builtin_popcount(t) <= d && allowed(t)) monos.push_back(t);
        std::sort(monos.begin(), monos.end(), [](Mask a, Mask b) {
            int da = __builtin_popcount(a), db = __builtin_popcount(b);
            return da != db ? da > db : a < b;
        });
        nwords = (int(monos.size()) + 63) / 64;
    }
};

// Returns 1 if the degree-d closure contains 1, else 0; *dim receives the closure's dimension when 1 is
// absent, and the number of rows found before the early exit when 1 is present.
static int closure_has_one(Instance &I, int d, long *dim) {
    I.enumerate(d);
    const int N = int(I.monos.size()), W = I.nwords, m = I.m;
    std::vector<int> mul(size_t(N) * m);          // index of y_v * monomial, -1 if zero or above degree d
    for (int i = 0; i < N; ++i)
        for (int v = 0; v < m; ++v) {
            Mask t = I.monos[i] | (Mask(1) << v);
            mul[size_t(i) * m + v] = (__builtin_popcount(t) <= d && I.allowed(t)) ? I.index(t) : -1;
        }
    std::vector<Row> basis(N);                    // pivot -> row (empty if none)
    std::vector<int> queue;                       // pivots of rows of degree < d awaiting multiplication
    long count = 0;
    auto insert = [&](Row &r) {
        for (int word = 0; word < W; ++word) {
            while (r[word]) {
                int p = word * 64 + __builtin_ctzll(r[word]);
                if (basis[p].empty()) {
                    basis[p] = r;
                    ++count;
                    if (__builtin_popcount(I.monos[p]) < d) queue.push_back(p);
                    return;
                }
                const Row &b = basis[p];
                for (int k = word; k < W; ++k) r[k] ^= b[k];
            }
        }
    };
    // generators: prod_{i in T} (1 + y_i) for T of size w/2+1 inside an A-block
    const int k = I.w / 2 + 1;
    if (k <= d)
        for (int a = 0; a < m / I.w; ++a)
            for (Mask s = 0; s < (Mask(1) << I.w); ++s) {
                if (__builtin_popcount(s) != k) continue;
                Mask T = s << (a * I.w);
                Row r(W, 0);
                for (Mask u = T;; u = (u - 1) & T) {
                    int j = I.index(u);
                    if (j >= 0) r[j / 64] ^= uint64_t(1) << (j % 64);
                    if (u == 0) break;
                }
                insert(r);
            }
    const int one = I.index(0);
    for (size_t q = 0; q < queue.size(); ++q) {
        if (!basis[one].empty()) break;
        const Row src = basis[queue[q]];
        for (int v = 0; v < m; ++v) {
            Row r(W, 0);
            for (int word = 0; word < W; ++word) {
                uint64_t x = src[word];
                while (x) {
                    int i = word * 64 + __builtin_ctzll(x);
                    x &= x - 1;
                    int j = mul[size_t(i) * m + v];
                    if (j >= 0) r[j / 64] ^= uint64_t(1) << (j % 64);
                }
            }
            insert(r);
        }
    }
    *dim = count;
    return basis[one].empty() ? 0 : 1;
}

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: %s M W KIND[:SEED] ...\n", argv[0]); return 2; }
    const int m = atoi(argv[1]), w = atoi(argv[2]);
    if (m < 2 || m > 30 || w < 2 || w % 2 || m % w) { fprintf(stderr, "need w even, w | m, m <= 30\n"); return 2; }
    const int ceiling = m / 2 - m / w + 1;
    int dmax = std::max(ceiling, w / 2 + 1);
    std::vector<std::string> specs;
    for (int i = 3; i < argc; ++i) {
        if (!strncmp(argv[i], "dmax=", 5)) dmax = atoi(argv[i] + 5);
        else specs.push_back(argv[i]);
    }
    std::vector<std::string> out(specs.size());
    #pragma omp parallel for schedule(dynamic, 1)
    for (size_t s = 0; s < specs.size(); ++s) {
        Instance I;
        I.m = m; I.w = w; I.cap = w / 2 - 1;
        std::string kind = specs[s];
        uint64_t seed = 0;
        size_t colon = kind.find(':');
        if (colon != std::string::npos) { seed = strtoull(kind.c_str() + colon + 1, 0, 10); kind = kind.substr(0, colon); }
        std::vector<int> perm(m);
        for (int i = 0; i < m; ++i) perm[i] = i;
        I.bblock.assign(m, 0);
        if (kind == "same") for (int i = 0; i < m; ++i) I.bblock[i] = i / w;
        else if (kind == "spread") for (int i = 0; i < m; ++i) I.bblock[i] = i % (m / w);
        else if (kind == "random") {
            uint64_t st = seed;
            for (int i = m - 1; i > 0; --i) std::swap(perm[i], perm[splitmix(st) % uint64_t(i + 1)]);
            for (int i = 0; i < m; ++i) I.bblock[perm[i]] = i / w;
        } else { out[s] = "{\"error\": \"unknown kind\"}"; continue; }
        I.bmask.assign(m / w, 0);
        for (int i = 0; i < m; ++i) I.bmask[I.bblock[i]] |= Mask(1) << i;
        for (Mask b : I.bmask) if (__builtin_popcount(b) != w) { fprintf(stderr, "bad partition\n"); exit(3); }
        std::string line = "{\"m\": " + std::to_string(m) + ", \"w\": " + std::to_string(w) + ", \"kind\": \"" + kind +
                           "\", \"seed\": " + std::to_string(seed) + ", \"b_block\": [";
        for (int i = 0; i < m; ++i) line += std::to_string(I.bblock[i]) + (i + 1 < m ? ", " : "");
        line += "], \"ceiling\": " + std::to_string(ceiling) + ", \"closures\": [";
        int degree = -1;
        for (int d = w / 2 + 1; d <= dmax; ++d) {
            long dim = 0;
            int has = closure_has_one(I, d, &dim);
            line += std::string(d > w / 2 + 1 ? ", " : "") + "{\"d\": " + std::to_string(d) + ", \"monomials\": " +
                    std::to_string(I.monos.size()) + ", \"dim\": " + std::to_string(dim) + ", \"one\": " +
                    (has ? "true" : "false") + "}";
            if (has) { degree = d; break; }
        }
        line += "], \"degree\": " + (degree < 0 ? std::string("null") : std::to_string(degree)) + "}";
        out[s] = line;
    }
    for (const std::string &l : out) puts(l.c_str());
    return 0;
}
