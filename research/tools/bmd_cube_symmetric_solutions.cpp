// S_n-invariant homogeneous solutions of the threshold system on {0,1}^n (entry-2026-09-26-cube-symmetric-kernel).
//
// Statement computed.  For savings h = d+1 and m, the threshold ideal I^{(h)}_m consists of the top coordinates W_m of
// the solutions W of sum_c A_{(Q,r),c}(y) W_c(y) = 0 for all rows (Q, r), r in {0,1}^n, 2Q+|r| <= d, where
// A_{(Q,r),c} is the coefficient of T^c in T^Q prod_{r_i=1} w_i, w_i = sum_j C_j y_i^j T^j, C_j = binom(1/2,j) 4^j
// (rows built from w_i span the same module as those from the root curve z_i = (1-w_i)/2).  A homogeneous solution of
// excess l has W_c homogeneous of degree l + m - c.  S_n permutes the rows and fixes the columns, so it acts on
// solutions; this program computes the S_n-invariant solutions of a given excess l over F_p, p = 32003:
//   unknowns: W_c = sum_lambda x_{c,lambda} m_lambda, m_lambda the monomial symmetric function of the partition lambda
//             of l + m - c into at most n parts;
//   equations: for one row per S_n-orbit, (Q, r = 1^s 0^(n-s)), the coefficient of y^alpha in the row polynomial, for
//             alpha of degree l + m - Q up to the stabilizer S_s x S_(n-s) (the row polynomial is invariant under it).
// A_{(Q,r),c} = sum_{j in N^s, |j| = c - Q} prod C_{j_i} y_i^{j_i} involves only y_1..y_s, so the coefficient of y^alpha
// in A m_lambda is sum_j prod C_{j_i} [sort(alpha - (j, 0)) = lambda].  The program prints the dimension of the
// invariant solution space and the span of the invariant top coordinates W_m (degree l) in the basis m_lambda.
//
// Usage: bmd_cube_symmetric_solutions n,d,m,l/n,d,m,lo:hi/...   (one run, a series of jobs; lo:hi scans the
// excess upward and stops at the first nonzero invariant top span)
#include <flint/flint.h>
#include <flint/nmod_mat.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <vector>
#include <algorithm>
#include <string>
#include <chrono>

typedef std::vector<int> V;
static const mp_limb_t P = 32003;

static void partitions(int D, int n, int maxp, V& cur, std::vector<V>& out) {  // descending, length n (zero padded)
    if ((int)cur.size() == n) { if (D == 0) out.push_back(cur); return; }
    for (int x = std::min(D, maxp); x >= 0; --x) { cur.push_back(x); partitions(D - x, n, x, cur, out); cur.pop_back(); }
}
// all alpha in N^n with |alpha| = D, first s entries descending, last n-s entries descending
static void orbit_reps(int D, int n, int s, std::vector<V>& out) {
    for (int a = 0; a <= D; ++a) {  // a = degree in the first s variables
        std::vector<V> A, B; V cur;
        if (s > 0) partitions(a, s, a, cur, A); else if (a == 0) A.push_back(V()); cur.clear();
        if (n - s > 0) partitions(D - a, n - s, D - a, cur, B); else if (D - a == 0) B.push_back(V());
        for (auto& x : A) for (auto& y : B) { V z = x; z.insert(z.end(), y.begin(), y.end()); out.push_back(z); }
    }
}
static void compositions_bounded(int t, const V& bound, int i, V& cur, std::vector<V>& out) {  // j with |j| = t, j <= bound
    if (i == (int)bound.size()) { if (t == 0) out.push_back(cur); return; }
    for (int x = 0; x <= std::min(t, bound[i]); ++x) { cur[i] = x; compositions_bounded(t - x, bound, i + 1, cur, out); }
    cur[i] = 0;
}

static long run(int n, int d, int m, int l) {
    auto t0 = std::chrono::steady_clock::now();
    // C_j mod P: C_0 = 1, C_j = C_{j-1} (6 - 4j) / j
    std::vector<mp_limb_t> C(m + l + 2, 0); C[0] = 1;
    nmod_t mod; nmod_init(&mod, P);
    for (int j = 1; j < (int)C.size(); ++j) {
        long num = 6 - 4L * j; num %= (long)P; if (num < 0) num += P;
        C[j] = nmod_mul(nmod_mul(C[j - 1], num, mod), n_invmod(j, P), mod);
    }
    // columns: (c, lambda)
    std::vector<std::map<V, long>> colIndex(m + 1);
    long ncols = 0;
    for (int c = 0; c <= m; ++c) {
        int D = l + m - c; if (D < 0) continue;
        std::vector<V> parts; V cur; partitions(D, n, D, cur, parts);
        for (auto& lam : parts) colIndex[c][lam] = ncols++;
    }
    // rows
    std::vector<std::vector<std::pair<long, mp_limb_t>>> rows;
    for (int Q = 0; 2 * Q <= d; ++Q) for (int s = 0; s <= n && 2 * Q + s <= d; ++s) {
        int D = l + m - Q; if (D < 0) continue;
        std::vector<V> alphas; orbit_reps(D, n, s, alphas);
        for (auto& al : alphas) {
            std::map<long, mp_limb_t> acc;
            V bound(al.begin(), al.begin() + s);
            for (int c = Q; c <= m; ++c) {
                int t = c - Q; int Dc = l + m - c; if (Dc < 0) continue;
                std::vector<V> js; V cur(s, 0);
                if (s == 0) { if (t == 0) js.push_back(V()); } else compositions_bounded(t, bound, 0, cur, js);
                for (auto& j : js) {
                    mp_limb_t coef = 1;
                    for (int i = 0; i < s; ++i) coef = nmod_mul(coef, C[j[i]], mod);
                    V beta = al; for (int i = 0; i < s; ++i) beta[i] -= j[i];
                    std::sort(beta.begin(), beta.end(), std::greater<int>());
                    auto it = colIndex[c].find(beta);
                    if (it == colIndex[c].end()) { std::fprintf(stderr, "missing column\n"); std::exit(3); }
                    acc[it->second] = nmod_add(acc[it->second], coef, mod);
                }
            }
            std::vector<std::pair<long, mp_limb_t>> row;
            for (auto& kv : acc) if (kv.second) row.push_back(kv);
            if (!row.empty()) rows.push_back(row);
        }
    }
    long nrows = rows.size();
    nmod_mat_t A; nmod_mat_init(A, nrows, ncols, P);
    for (long i = 0; i < nrows; ++i) for (auto& e : rows[i]) nmod_mat_entry(A, i, e.first) = e.second;
    nmod_mat_t X; nmod_mat_init(X, ncols, ncols, P);
    long nullity = nmod_mat_nullspace(X, A);
    // tops: columns of block c = m
    std::vector<V> topParts; for (auto& kv : colIndex[m]) topParts.push_back(kv.first);
    nmod_mat_t Tm; nmod_mat_init(Tm, nullity, topParts.size(), P);
    for (long k = 0; k < nullity; ++k) for (size_t q = 0; q < topParts.size(); ++q)
        nmod_mat_entry(Tm, k, q) = nmod_mat_entry(X, colIndex[m][topParts[q]], k);
    long topRank = nullity ? nmod_mat_rref(Tm) : 0;
    double secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    std::printf("n=%d d=%d m=%d l=%d: rows %ld cols %ld invariant solutions %ld, invariant top span dim %ld", n, d, m, l, nrows, ncols, nullity, topRank);
    std::printf(" (basis m_lambda:");
    for (auto& lam : topParts) { std::printf(" ("); for (int x : lam) if (x) std::printf("%d", x); std::printf(")"); }
    std::printf(") secs %.2f\n", secs);
    for (long k = 0; k < topRank; ++k) {
        std::printf("  top %ld:", k);
        for (size_t q = 0; q < topParts.size(); ++q) std::printf(" %lu", (unsigned long)nmod_mat_entry(Tm, k, q));
        std::printf("\n");
    }
    std::fflush(stdout);
    nmod_mat_clear(A); nmod_mat_clear(X); nmod_mat_clear(Tm);
    return topRank;
}

int main(int argc, char** argv) {
    if (argc < 2) { std::fprintf(stderr, "usage: %s n,d,m,l/...\n", argv[0]); return 2; }
    std::string s = argv[1]; size_t pos = 0;
    while (pos < s.size()) {
        size_t e = s.find('/', pos); if (e == std::string::npos) e = s.size();
        int n, d, m, l, lhi;
        std::string job = s.substr(pos, e - pos);
        // "n,d,m,l" runs one excess; "n,d,m,lo:hi" scans excesses lo..hi and stops at the first nonzero top span
        if (std::sscanf(job.c_str(), "%d,%d,%d,%d:%d", &n, &d, &m, &l, &lhi) == 5) {
            long r = 0; int x = l;
            for (; x <= lhi && r == 0; ++x) r = run(n, d, m, x);
            if (r) std::printf("scan n=%d d=%d m=%d: least excess with an invariant top = %d\n", n, d, m, x - 1);
            else std::printf("scan n=%d d=%d m=%d: no invariant top for excess %d..%d\n", n, d, m, l, lhi);
            std::fflush(stdout);
        } else if (std::sscanf(job.c_str(), "%d,%d,%d,%d", &n, &d, &m, &l) == 4) run(n, d, m, l);
        else { std::fprintf(stderr, "bad job\n"); return 2; }
        pos = e + 1;
    }
    return 0;
}
