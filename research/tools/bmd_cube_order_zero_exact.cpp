// Exact (rational) order-zero solvability on {0,1}^n by symmetric dual solutions (bmd-r121).
//
// Statement computed.  The system of bmd_cube_order_zero_sym.cpp, over Q instead of F_p.  By
// lem:cube-dual-polynomial-form at l = 0, the savings at (k, 0) on {0,1}^n are >= d+1 with m = k-1 iff there is
// Phi(u_1..u_n) with Phi(0) = 1, deg Phi <= m and [Phi * z^a(u)]_{m-Q} = 0 for every a in {0,1}^n and Q >= 0 with
// 2Q + |a| <= d, where z^a = prod_{a_i=1} r_0(u_i), r_0(u) = sum_{j>=1} kappa_j u^j, kappa_j = (-1)^j C_{j-1}
// (Catalan).  Averaging over S_n reduces to symmetric Phi = 1 + sum_lambda x_lambda m_lambda.  The program solves
// A x = b exactly over Q (FLINT fmpz_mat_can_solve: A X = den B).  A rational solution gives savings >= d+1 at (m+1, 0) in
// characteristic 0; reduced modulo p it gives the same in every characteristic p > 2 not dividing a denominator of
// x (those primes are printed).  Inconsistency over Q gives the negative statement in characteristic 0.
// Usage: bmd_cube_order_zero_exact n d,m[/d,m...]
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <string>
#include <sstream>
#include <algorithm>
#include <chrono>
#include <flint/fmpz.h>
#include <flint/fmpq.h>
#include <flint/fmpz_mat.h>
#include <flint/fmpz_vec.h>
#include <flint/fmpz_factor.h>
using namespace std;

static void partitions(int n, int total, int maxpart, vector<int> &cur, vector<vector<int>> &out) {
    if (total == 0) { vector<int> v = cur; v.resize(n, 0); out.push_back(v); return; }
    if ((int)cur.size() == n) return;
    for (int x = min(total, maxpart); x >= 1; x--) { cur.push_back(x); partitions(n, total - x, x, cur, out); cur.pop_back(); }
}
static void blocks(int n, int k, int D, vector<vector<int>> &out) {
    for (int D1 = 0; D1 <= D; D1++) {
        vector<vector<int>> A, B; vector<int> cur;
        if (k == 0) { if (D1) continue; A.push_back({}); }
        else { vector<vector<int>> t; partitions(k, D1, D1, cur, t); if (D1 == 0) t = {vector<int>(k, 0)}; A = t; }
        if (n - k == 0) { if (D - D1) continue; B.push_back({}); }
        else { vector<vector<int>> t; cur.clear(); partitions(n - k, D - D1, D - D1, cur, t); if (D - D1 == 0) t = {vector<int>(n - k, 0)}; B = t; }
        for (auto &a : A) for (auto &b : B) { vector<int> g = a; g.insert(g.end(), b.begin(), b.end()); out.push_back(g); }
    }
}

static void run(int n, int d, int m) {
    auto t0 = chrono::steady_clock::now();
    // kappa_j = (-1)^j C_{j-1}, C the Catalan numbers
    fmpz *kap = _fmpz_vec_init(m + 2);
    fmpz_t cat; fmpz_init_set_ui(cat, 1);  // C_0
    for (int j = 1; j <= m + 1; j++) {
        fmpz_set(kap + j, cat); if (j % 2) fmpz_neg(kap + j, kap + j);
        // C_j = C_{j-1} * 2(2j-1)/(j+1)
        fmpz_mul_ui(cat, cat, 2 * (2 * j - 1)); fmpz_divexact_ui(cat, cat, j + 1);
    }
    vector<vector<int>> lam; vector<int> ldeg; vector<vector<vector<int>>> perms;
    for (int j = 1; j <= m; j++) {
        vector<vector<int>> t; vector<int> cur; partitions(n, j, j, cur, t);
        for (auto &v : t) {
            lam.push_back(v); ldeg.push_back(j);
            vector<int> s = v; sort(s.begin(), s.end());
            vector<vector<int>> ps; do ps.push_back(s); while (next_permutation(s.begin(), s.end()));
            perms.push_back(ps);
        }
    }
    int nu = lam.size();
    vector<vector<int>> gsAll; vector<int> kAll;
    for (int Q = 0; 2 * Q <= d; Q++) for (int k = 0; k <= n && 2 * Q + k <= d; k++) {
        int D = m - Q; if (D < 0) continue;
        vector<vector<int>> gs; blocks(n, k, D, gs);
        for (auto &g : gs) { gsAll.push_back(g); kAll.push_back(k); }
    }
    long R = gsAll.size();
    fmpz_mat_t A, B, X; fmpz_mat_init(A, R, nu); fmpz_mat_init(B, R, 1); fmpz_mat_init(X, nu, 1);
    fmpz_t den; fmpz_init(den);
    fmpz_t c, acc; fmpz_init(c); fmpz_init(acc);
    for (long gi = 0; gi < R; gi++) {
        const vector<int> &g = gsAll[gi]; int k = kAll[gi]; int D = 0; for (int x : g) D += x;
        bool ok = true; fmpz_one(c);
        for (int i = 0; i < n; i++) { if (i < k) { if (g[i] < 1) { ok = false; break; } fmpz_mul(c, c, kap + g[i]); } else if (g[i]) { ok = false; break; } }
        if (ok) { fmpz_neg(c, c); fmpz_set(fmpz_mat_entry(B, gi, 0), c); }  // Phi_0 = 1 moved to the right-hand side
        for (int L = 0; L < nu; L++) {
            if (ldeg[L] > D - k) break;
            fmpz_zero(acc);
            for (auto &e : perms[L]) {
                bool good = true; fmpz_one(c);
                for (int i = 0; i < n; i++) {
                    if (i < k) { int f = g[i] - e[i]; if (f < 1) { good = false; break; } fmpz_mul(c, c, kap + f); }
                    else if (e[i] != g[i]) { good = false; break; }
                }
                if (good) fmpz_add(acc, acc, c);
            }
            fmpz_set(fmpz_mat_entry(A, gi, L), acc);
        }
    }
    int sol = fmpz_mat_can_solve(X, den, A, B);
    double secs = chrono::duration<double>(chrono::steady_clock::now() - t0).count();
    printf("n=%d d=%d m=%d: %ld equations, %d symmetric unknowns; over Q: %s (%.1f s)\n", n, d, m, R, nu,
           sol ? "solvable" : "not solvable", secs);
    if (sol) {
        // X = den^{-1} * (integer vector); the primes dividing den after removing the content are the bad ones
        fmpz_t L, g; fmpz_init(L); fmpz_init_set(g, den);
        for (int i = 0; i < nu; i++) fmpz_gcd(g, g, fmpz_mat_entry(X, i, 0));
        fmpz_divexact(L, den, g); fmpz_abs(L, L);
        // check the solution exactly: A X == den B
        fmpz_mat_t AX, dB; fmpz_mat_init(AX, R, 1); fmpz_mat_init(dB, R, 1);
        fmpz_mat_mul(AX, A, X); fmpz_mat_scalar_mul_fmpz(dB, B, den);
        printf("  exact verification A x = b: %s; den != 0: %s\n", fmpz_mat_equal(AX, dB) ? "true" : "false", fmpz_is_zero(den) ? "false" : "true");
        fmpz_mat_clear(AX); fmpz_mat_clear(dB); fmpz_clear(g);
        fmpz_factor_t fac; fmpz_factor_init(fac); fmpz_factor(fac, L);
        printf("  primes dividing a denominator of the solution found:");
        for (slong i = 0; i < fac->num; i++) { printf(" "); fmpz_print(fac->p + i); }
        printf("%s\n", fac->num ? "" : " none");
        fmpz_factor_clear(fac); fmpz_clear(L);
    }
    fflush(stdout);
    fmpz_mat_clear(A); fmpz_mat_clear(B); fmpz_mat_clear(X); fmpz_clear(c); fmpz_clear(acc); fmpz_clear(cat); fmpz_clear(den);
    _fmpz_vec_clear(kap, m + 2);
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: %s n d,m[/d,m...]\n", argv[0]); return 2; }
    int n = atoi(argv[1]);
    stringstream ss(argv[2]); string job;
    while (getline(ss, job, '/')) { int d, m; if (sscanf(job.c_str(), "%d,%d", &d, &m) != 2) return 2; run(n, d, m); }
    return 0;
}
