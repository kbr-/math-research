// Relative directness of product tops (closure-route follow-up, 27 September 2026).
// Collision algebra At = tensor over N columns of (F_3 + V_c), dim V_c = m, V_c^2 = 0 (cells x_{ic}; monomials
// are column-injective cell sets). Row sums r_i = sum_c x_{ic}; occupancy s = sum_i r_i. In degree 4:
//   T = span of M product tops l_b^2 l'_b^2 (l, l' linear forms), S = s At_3, R = sum_i r_i At_3 (S inside R).
// G = At/(s) is the graded weak base and A = At/R the weak top algebra modulo row sums. The first-degree purity
// defect of lem:first-degree-purity for tops T is dim((T+S) cap R)/S = rank(T+S) + rank(R) - rank(T+R) - rank(S),
// and the tops are direct in G when rank(T+S) - rank(S) = M. Statement tested (relative product-top
// directness): for random dense forms the defect is 0 until T+R fills At_4. Modes: random (dense l, l'),
// sunflower (l = common dense l_0 for all b), rho (l = row-0 sum without its column-0 cell).
// U-shifted sunflower (local-independence review, 27 September 2026): modes ushift2 and rshift2 give BOTH factors of
// every top a fresh shift, l = l0 + shift_b and l2 = l0' + shift'_b, with l0 and l0' fixed dense forms free of column 0.
// ushift2 shifts by truncated row sums r'_i (columns 1..N-1, normalized); rshift2 by full row sums r_i. Tested
// statement (U-shifted sunflower collapse): modulo R the ushift2 tops lie in P + U*Q_1 + U*Q_2, of dimension <= 1 + 2m,
// while their rank in G grows with M, so the tops-only purity defect is at least rank_G - 1 - 2m.
// Column perturbation (column-fibers cycle, 27 September 2026): mode colpert represents the same members as ushift2
// sparsely, l = w0 - p_b . (column-0 cells), l2 = w1 - p'_b . (column-0 cells), which agree with ushift2's forms
// modulo the row equations r_i = 1. Tested statement (column-perturbation affinity): the tops are affine in the
// perturbations in A~ itself (products of two column-0 cells vanish), so rank in G is at most 1 + 2m and the purity
// defect is bounded independently of M.
// Row-shifted sunflower (closure-line review, 27 September 2026): mode rowsun takes l = l_0 + sum_i p_i r_i with a
// fresh random shift p per member, so the tops agree with the sunflower's modulo R but not in G. Tested
// statement: the tops-only purity defect of rowsun exceeds the exact sunflower's bound dim(l_0^2 G_2 cap mG).
// The tops-only count: rank_A(T) <= dim(l_0^2 At_2 mod R), while rank in G grows with the number of shifts.
// Usage: relative_directness m N mode seed M1 M2 ...   (prints one line per M, from one pass of rank calls)
#include <flint/nmod_mat.h>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <map>
#include <random>
#include <string>
using namespace std;
typedef vector<int> VI;
int m, N;
// a monomial: vector of (column, row) with distinct columns, stored as a canonical key: for each column, 0 = empty, 1+i = row i
typedef vector<unsigned char> Key;
map<Key,int> idx4, idx3; vector<Key> mons4, mons3;
void enumerate(int deg, vector<Key>& out, map<Key,int>& idx) {
    // columns chosen by combination, rows by product
    vector<int> cols(deg); for (int i = 0; i < deg; i++) cols[i] = i;
    while (true) {
        long tot = 1; for (int i = 0; i < deg; i++) tot *= m;
        for (long code = 0; code < tot; code++) { Key k(N, 0); long c = code;
            for (int i = 0; i < deg; i++) { k[cols[i]] = 1 + c % m; c /= m; }
            idx[k] = out.size(); out.push_back(k); }
        int i = deg - 1; while (i >= 0 && cols[i] == N - deg + i) i--; if (i < 0) break;
        cols[i]++; for (int j = i+1; j < deg; j++) cols[j] = cols[j-1] + 1;
    }
}
// sparse polynomial in At: map Key -> coeff mod 3
typedef map<Key,int> Poly;
Poly mul(const Poly& a, const Poly& b) { Poly r;
    for (auto& [ka, ca] : a) for (auto& [kb, cb] : b) { Key k(N); bool ok = true;
        for (int c = 0; c < N && ok; c++) { if (ka[c] && kb[c]) ok = false; else k[c] = ka[c] ? ka[c] : kb[c]; }
        if (!ok) continue; int v = (r[k] + ca * cb) % 3; if (v) r[k] = v; else r.erase(k); }
    return r; }
Poly linear(const VI& coef) { Poly p; for (int c = 0; c < N; c++) for (int i = 0; i < m; i++) { int a = coef[i*N + c] % 3; if (a) { Key k(N,0); k[c] = 1+i; p[k] = a; } } return p; }
// rows are stored densely (one byte per degree-4 monomial) to keep memory small
typedef vector<unsigned char> Dense;
Dense toDense(const Poly& p) { Dense d(mons4.size(), 0); for (auto& [k, c] : p) d[idx4[k]] = c; return d; }
long rankOf(const vector<const Dense*>& rows) {
    if (rows.empty()) return 0;
    nmod_mat_t A; nmod_mat_init(A, rows.size(), mons4.size(), 3);
    for (size_t r = 0; r < rows.size(); r++) for (size_t c = 0; c < mons4.size(); c++) nmod_mat_entry(A, r, c) = (*rows[r])[c];
    long rk = nmod_mat_rank(A); nmod_mat_clear(A); return rk; }
int main(int argc, char** argv) {
    if (argc < 6) { fprintf(stderr, "usage\n"); return 2; }
    m = atoi(argv[1]); N = atoi(argv[2]); string mode = argv[3]; unsigned seed = atoi(argv[4]);
    vector<int> Ms; for (int a = 5; a < argc; a++) Ms.push_back(atoi(argv[a]));
    enumerate(4, mons4, idx4); enumerate(3, mons3, idx3);
    vector<Poly> rs(m); for (int i = 0; i < m; i++) { VI co(m*N, 0); for (int c = 0; c < N; c++) co[i*N+c] = 1; rs[i] = linear(co); }
    Poly s; { VI co(m*N, 1); s = linear(co); }
    vector<Dense> Rrows, Srows;
    for (auto& k : mons3) { Poly x; x[k] = 1; for (int i = 0; i < m; i++) Rrows.push_back(toDense(mul(rs[i], x))); Srows.push_back(toDense(mul(s, x))); }
    auto ptrs = [](const vector<Dense>& v) { vector<const Dense*> p; for (auto& d : v) p.push_back(&d); return p; };
    long rankR = rankOf(ptrs(Rrows)), rankS = rankOf(ptrs(Srows));
    mt19937 rng(seed); uniform_int_distribution<int> u3(0,2);
    auto dense = [&]() { VI co(m*N); for (auto& a : co) a = u3(rng); return linear(co); };
    Poly l0 = dense();
    Poly rho; { VI co(m*N, 0); for (int c = 1; c < N; c++) co[0*N + c] = 1; rho = linear(co); }
    int Mmax = 0; for (int M : Ms) Mmax = max(Mmax, M);
    vector<Dense> tops;
    for (int b = 0; b < Mmax; b++) {
        Poly l = (mode == "sunflower") ? l0 : (mode == "rho") ? rho : dense();
        if (mode == "rowsun") { VI co(m*N, 0); for (int i = 0; i < m; i++) { int p = u3(rng); for (int c = 0; c < N; c++) co[i*N + c] = p; }
            l = l0; for (auto& [k, c] : linear(co)) { int v = (l[k] + c) % 3; if (v) l[k] = v; else l.erase(k); } }
        Poly l2 = dense();
        if (mode == "ushift2" || mode == "rshift2" || mode == "colpert") {
            static Poly w0, w1; static bool init = false;
            auto noCol0 = [&]() { VI co(m*N); for (int i = 0; i < m; i++) for (int c = 0; c < N; c++) co[i*N + c] = c ? u3(rng) : 0; return linear(co); };
            if (!init) { w0 = noCol0(); w1 = noCol0(); init = true; }
            auto shifted = [&](const Poly& w) { VI co(m*N, 0);
                for (int i = 0; i < m; i++) { int p = u3(rng);
                    if (mode == "colpert") co[i*N + 0] = (3 - p) % 3;
                    else for (int c = (mode == "ushift2" ? 1 : 0); c < N; c++) co[i*N + c] = p; }
                Poly r = w; for (auto& [k, c] : linear(co)) { int v = (r[k] + c) % 3; if (v) r[k] = v; else r.erase(k); } return r; };
            l = shifted(w0); l2 = shifted(w1);
        }
        tops.push_back(toDense(mul(mul(l, l), mul(l2, l2))));
    }
    printf("m=%d N=%d mode=%s seed=%u dimAt4=%zu rankR=%ld rankS=%ld dimA4=%ld\n", m, N, mode.c_str(), seed, mons4.size(), rankR, rankS, (long)mons4.size() - rankR);
    fflush(stdout);
    for (int M : Ms) {
        vector<const Dense*> TS, TR;
        for (int b = 0; b < M; b++) { TS.push_back(&tops[b]); TR.push_back(&tops[b]); }
        for (auto& d : Srows) TS.push_back(&d);
        for (auto& d : Rrows) TR.push_back(&d);
        long rTS = rankOf(TS), rTR = rankOf(TR);
        long defect = rTS + rankR - rTR - rankS, directG = rTS - rankS;
        printf("mode=%s seed=%u M=%d rankT_in_G=%ld purityDefect=%ld rankT_mod_R=%ld\n", mode.c_str(), seed, M, directG, defect, rTR - rankR);
        fflush(stdout);
    }
    return 0;
}
