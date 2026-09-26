// Relative directness of product tops (closure-route follow-up, 27 September 2026).
// Collision algebra At = tensor over N columns of (F_3 + V_c), dim V_c = m, V_c^2 = 0 (cells x_{ic}; monomials
// are column-injective cell sets). Row sums r_i = sum_c x_{ic}; occupancy s = sum_i r_i. In degree 4:
//   T = span of M product tops l_b^2 l'_b^2 (l, l' linear forms), S = s At_3, R = sum_i r_i At_3 (S inside R).
// G = At/(s) is the graded weak base and A = At/R the weak top algebra modulo row sums. The first-degree purity
// defect of lem:first-degree-purity for tops T is dim((T+S) cap R)/S = rank(T+S) + rank(R) - rank(T+R) - rank(S),
// and the tops are direct in G when rank(T+S) - rank(S) = M. Statement tested (relative product-top
// directness): for random dense forms the defect is 0 until T+R fills At_4. Modes: random (dense l, l'),
// sunflower (l = common dense l_0 for all b), rho (l = row-0 sum without its column-0 cell).
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
// Product square criterion (27 September 2026). Tested statement: for linear forms l_1, l_2 on m rows and
// N columns (degree 4 well below the fill), l_1^2 l_2^2 lies in R_4 = sum_i r_i At_3 iff some l_j is
// congruent modulo the row sums to a single-column form. Second pass: each trial is also classified by whether
// l_1^2 l_2^2 vanishes in At, and every member of R that neither vanishes nor has a single-column factor is
// printed with its column vectors. Membership is decided by reduction against the rref of R_4.
// Padding test: with two extra arguments (column strings of forms on fewer columns, e.g. "202 011 ..."), the
// forms are padded with zero columns to N, shifted by random row sums, and tested for membership instead.
// Usage: product_square m N trials seed [l1columns l2columns]
int main(int argc, char** argv) {
    if (argc < 5) { fprintf(stderr, "usage\n"); return 2; }
    m = atoi(argv[1]); N = atoi(argv[2]); int trials = atoi(argv[3]); unsigned seed = atoi(argv[4]);
    enumerate(4, mons4, idx4); enumerate(3, mons3, idx3);
    vector<Poly> rs(m); for (int i = 0; i < m; i++) { VI co(m*N, 0); for (int c = 0; c < N; c++) co[i*N+c] = 1; rs[i] = linear(co); }
    // echelon basis of R_4, computed once
    nmod_mat_t B; nmod_mat_init(B, mons3.size() * m, mons4.size(), 3);
    { size_t r = 0; for (auto& k : mons3) { Poly x; x[k] = 1; for (int i = 0; i < m; i++) { Dense d = toDense(mul(rs[i], x));
          for (size_t c = 0; c < mons4.size(); c++) nmod_mat_entry(B, r, c) = d[c]; r++; } } }
    long rankR = nmod_mat_rref(B);
    printf("m=%d N=%d seed=%u dimAt4=%zu rankR=%ld\n", m, N, seed, mons4.size(), rankR); fflush(stdout);
    mt19937 rng(seed); uniform_int_distribution<int> u3(0,2);
    auto form = [&](const string& kind) { VI co(m*N, 0);
        VI shift(m); for (auto& a : shift) a = u3(rng);                       // a random row-sum shift
        if (kind == "dense") for (auto& a : co) a = u3(rng);
        else if (kind == "single") { int c0 = rng() % N; for (int i = 0; i < m; i++) co[i*N + c0] = u3(rng); }
        else if (kind == "rankone") { VI q(m), lam(N); for (auto& a : q) a = u3(rng); for (auto& a : lam) a = u3(rng);
            for (int i = 0; i < m; i++) for (int c = 0; c < N; c++) co[i*N + c] = q[i]*lam[c] % 3; }
        else if (kind == "opposite") { VI u(m); for (auto& a : u) a = u3(rng); int c1 = rng() % N, c2 = (c1 + 1 + rng() % (N-1)) % N;
            for (int i = 0; i < m; i++) { co[i*N + c1] = u[i]; co[i*N + c2] = (3 - u[i]) % 3; } }
        for (int i = 0; i < m; i++) for (int c = 0; c < N; c++) co[i*N + c] = (co[i*N + c] + shift[i]) % 3;
        return co; };
    auto singleColumn = [&](const VI& co) { map<VI,int> cnt; for (int c = 0; c < N; c++) { VI u(m); for (int i = 0; i < m; i++) u[i] = co[i*N + c]; cnt[u]++; }
        int best = 0; for (auto& [u, k] : cnt) best = max(best, k); return best >= N - 1; };
    vector<pair<string,string>> kinds = {{"dense","dense"},{"single","dense"},{"rankone","dense"},{"rankone","rankone"},{"opposite","dense"},{"opposite","opposite"},{"single","single"}};
    vector<long> pivot(rankR); { long c = 0; for (long r = 0; r < rankR; r++) { while (nmod_mat_entry(B, r, c) == 0) c++; pivot[r] = c; } }
    auto inRow = [&](Dense v) { for (long r = 0; r < rankR; r++) { int f = v[pivot[r]]; if (!f) continue;
            for (size_t c = pivot[r]; c < mons4.size(); c++) v[c] = (v[c] + 3 * 3 - f * nmod_mat_entry(B, r, c)) % 3; }
        for (auto x : v) if (x) return false; return true; };
    auto show = [&](const VI& co) { string t; for (int c = 0; c < N; c++) { t += c ? " " : ""; for (int i = 0; i < m; i++) t += char('0' + co[i*N + c]); } return t; };
    if (argc >= 7) {
        auto parseCols = [&](const char* txt) { VI co(m*N, 0); int c = 0, i = 0;
            for (const char* p = txt; *p; p++) { if (*p == ' ') { c++; i = 0; continue; } co[i*N + c] = *p - '0'; i++; }
            return co; };
        VI a0 = parseCols(argv[5]), b0 = parseCols(argv[6]); int inR = 0;
        for (int tr = 0; tr < trials; tr++) { VI a = a0, b = b0;
            for (VI* f : {&a, &b}) { VI shift(m); for (auto& x : shift) x = u3(rng);
                for (int i = 0; i < m; i++) for (int c = 0; c < N; c++) (*f)[i*N + c] = ((*f)[i*N + c] + shift[i]) % 3; }
            Poly l1 = linear(a), l2 = linear(b);
            bool member = inRow(toDense(mul(mul(l1, l1), mul(l2, l2)))); inR += member;
            if (tr == 0) printf("padded forms: l1 %s | l2 %s\n", show(a).c_str(), show(b).c_str()); }
        printf("padded trials=%d inR=%d\n", trials, inR); nmod_mat_clear(B); return 0;
    }
    for (auto& [k1, k2] : kinds) { int inR = 0, predicted = 0, agree = 0, zero = 0, unexplained = 0;
        for (int tr = 0; tr < trials; tr++) {
            VI a = form(k1), b = form(k2);
            Poly l1 = linear(a), l2 = linear(b);
            Poly prod = mul(mul(l1, l1), mul(l2, l2));
            bool member = inRow(toDense(prod)), vanishes = prod.empty();
            bool pred = singleColumn(a) || singleColumn(b);
            inR += member; predicted += pred; agree += (member == pred); zero += vanishes;
            if (member && !pred && !vanishes) { unexplained++; printf("  unexplained: l1 columns %s | l2 columns %s\n", show(a).c_str(), show(b).c_str()); }
            if (!member && pred) printf("  UNEXPECTED: predicted but not in R\n");
        }
        printf("kinds=%s,%s trials=%d inR=%d predicted=%d agree=%d vanishing=%d unexplained=%d\n", k1.c_str(), k2.c_str(), trials, inR, predicted, agree, zero, unexplained); fflush(stdout);
    }
    nmod_mat_clear(B); return 0;
}
