// Exact polynomial-calculus refutation degree over F_2 of a system of multilinear polynomials.
//
// Statement computed: for polynomials f_1..f_R in the multilinear ring F_2[y_1..y_N]/(y_i^2 - y_i), the least
// D <= dmax such that 1 lies in the degree-D closure C_D: the smallest space containing the f_j of degree
// at most D and closed under multiplication of its members of degree below D by a variable.  This is the
// polynomial-calculus refutation degree with the Boolean axioms built in.  For each D the closure is computed
// by elimination on the monomials of degree at most D, ordered by degree descending, so that a row's pivot is
// its leading monomial and the members of degree below D are spanned by the rows with pivots of degree below
// D; each such row is multiplied by every variable once.  It stops as soon as the constant enters.
//
// Input (a file): "N R", then R lines "k m_1 ... m_k", a polynomial as k monomials, each a bit mask of its
// variables (0 is the constant).  N <= 26.  Output: one JSON line with, for each D tried, the closure's
// dimension when 1 is not in it, and the degree (null when 1 is not reached by dmax).
// Usage: f2_closure_degree INSTANCE DMAX
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>

typedef uint32_t Mask;
typedef std::vector<uint64_t> Row;

static int first_bit(const Row &r, size_t from = 0) {
    for (size_t w = from; w < r.size(); ++w)
        if (r[w]) return int(w * 64 + __builtin_ctzll(r[w]));
    return -1;
}

// Returns 1 if 1 is in the degree-d closure; otherwise 0 with *dim its dimension.
static int closure(int n, int d, const std::vector<std::vector<Mask>> &polys, long *dim) {
    std::vector<Mask> monos;
    for (Mask t = 0; t < (Mask(1) << n); ++t)
        if (__builtin_popcount(t) <= d) monos.push_back(t);
    std::sort(monos.begin(), monos.end(), [](Mask a, Mask b) {
        int da = __builtin_popcount(a), db = __builtin_popcount(b);
        return da != db ? da > db : a > b;
    });
    const int count = int(monos.size()), words = (count + 63) / 64;
    std::vector<int> index(size_t(1) << n, -1);
    for (int i = 0; i < count; ++i) index[monos[i]] = i;
    std::vector<Row> basis(count);
    std::vector<int> pending;                    // pivots of rows not yet multiplied
    long size = 0;
    auto insert = [&](Row &r) -> int {           // 1 if the row is the constant, the last monomial
        int p = first_bit(r);
        while (p >= 0 && !basis[p].empty()) {
            const Row &b = basis[p];
            for (int w = p / 64; w < words; ++w) r[w] ^= b[w];
            p = first_bit(r, p / 64);
        }
        if (p < 0) return 0;
        basis[p] = r;
        ++size;
        if (p == count - 1) return 1;
        if (__builtin_popcount(monos[p]) < d) pending.push_back(p);
        return 0;
    };
    for (const auto &poly : polys) {
        int degree = 0;
        for (Mask t : poly) degree = std::max(degree, __builtin_popcount(t));
        if (degree > d) continue;
        Row r(words, 0);
        for (Mask t : poly) r[index[t] / 64] ^= uint64_t(1) << (index[t] % 64);
        if (insert(r)) return 1;
    }
    while (!pending.empty()) {
        const int p = pending.back();
        pending.pop_back();
        const Row source = basis[p];
        for (int v = 0; v < n; ++v) {
            Row r(words, 0);
            for (int w = p / 64; w < words; ++w) {
                uint64_t bits = source[w];
                while (bits) {
                    const int i = w * 64 + __builtin_ctzll(bits);
                    bits &= bits - 1;
                    const int j = index[monos[i] | (Mask(1) << v)];
                    r[j / 64] ^= uint64_t(1) << (j % 64);
                }
            }
            if (insert(r)) return 1;
        }
    }
    *dim = size;
    return 0;
}

int main(int argc, char **argv) {
    if (argc != 3) { fprintf(stderr, "usage: %s INSTANCE DMAX\n", argv[0]); return 2; }
    FILE *in = fopen(argv[1], "r");
    int n, rows;
    if (!in || fscanf(in, "%d %d", &n, &rows) != 2 || n < 1 || n > 26) {
        fprintf(stderr, "bad instance header\n");
        return 2;
    }
    std::vector<std::vector<Mask>> polys(rows);
    for (auto &poly : polys) {
        int k;
        if (fscanf(in, "%d", &k) != 1) { fprintf(stderr, "bad row\n"); return 2; }
        poly.resize(k);
        for (auto &t : poly) {
            unsigned long value;
            if (fscanf(in, "%lu", &value) != 1 || value >= (1ul << n)) { fprintf(stderr, "bad monomial\n"); return 2; }
            t = Mask(value);
        }
    }
    fclose(in);
    const int dmax = atoi(argv[2]);
    printf("{\"variables\": %d, \"rows\": %d, \"dmax\": %d, \"dimensions\": {", n, rows, dmax);
    int degree = -1;
    bool first = true;
    for (int d = 0; d <= dmax && degree < 0; ++d) {
        long dim = 0;
        if (closure(n, d, polys, &dim)) degree = d;
        else { printf("%s\"%d\": %ld", first ? "" : ", ", d, dim); first = false; }
    }
    if (degree >= 0) printf("}, \"degree\": %d}\n", degree);
    else printf("}, \"degree\": null}\n");
    return 0;
}
