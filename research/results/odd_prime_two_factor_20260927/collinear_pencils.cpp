// Collinear pencils (two-factor criterion cycle, 27 September 2026). The triangle-pair lemma shows that
// l_1^2 l_2^2 in R_4 forces D_X(1)(x)D_Y(2) + D_X(2)(x)D_Y(1) + D_X(1,2)(x)D_Y(1,2) = 0 for disjoint column triples;
// pencils collinear on every triple (rank-one pencils) escape it. Tested statement (conj:shifted-vanishing-criterion
// at k = 2, N >= 8, on the pencils the lemma cannot decide): such a product lies in R_4 only if row-sum shifts make it
// vanish. Input: a pairs file, lines "N|label|l1 columns|l2 columns" (column strings of m digits); for each board N
// the rref of R_4 is computed once and every pair is tested unshifted and under `trials` random row-sum shifts.
// Usage: collinear_pencils m trials seed PAIRS_FILE
#include <flint/nmod_mat.h>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <map>
#include <random>
#include <string>
#include <array>
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
    if (argc < 5) { fprintf(stderr, "usage\n"); return 2; }
    m = atoi(argv[1]); int trials = atoi(argv[2]); unsigned seed = atoi(argv[3]);
    vector<array<string,4>> pairs; { FILE* f = fopen(argv[4], "r"); char buf[4096];
        while (fgets(buf, sizeof buf, f)) { string s(buf); if (s.empty() || s[0] == '#') continue; while (!s.empty() && (s.back() == '\n' || s.back() == '\r')) s.pop_back();
            array<string,4> a; size_t p = 0; for (int k = 0; k < 4; k++) { size_t q = s.find('|', p); a[k] = s.substr(p, q == string::npos ? string::npos : q - p); p = q + 1; }
            pairs.push_back(a); } fclose(f); }
    mt19937 rng(seed); uniform_int_distribution<int> u3(0,2);
    int lastN = -1; nmod_mat_t B; long rankR = 0; vector<long> pivot;
    for (auto& pr : pairs) {
        int n = atoi(pr[0].c_str());
        if (n != lastN) {
            if (lastN >= 0) nmod_mat_clear(B);
            N = n; lastN = n; mons4.clear(); mons3.clear(); idx4.clear(); idx3.clear();
            enumerate(4, mons4, idx4); enumerate(3, mons3, idx3);
            vector<Poly> rs(m); for (int i = 0; i < m; i++) { VI co(m*N, 0); for (int c = 0; c < N; c++) co[i*N+c] = 1; rs[i] = linear(co); }
            nmod_mat_init(B, mons3.size() * m, mons4.size(), 3);
            { size_t r = 0; for (auto& k : mons3) { Poly x; x[k] = 1; for (int i = 0; i < m; i++) { Dense d = toDense(mul(rs[i], x));
                  for (size_t c = 0; c < mons4.size(); c++) nmod_mat_entry(B, r, c) = d[c]; r++; } } }
            rankR = nmod_mat_rref(B);
            pivot.assign(rankR, 0); { long c = 0; for (long r = 0; r < rankR; r++) { while (nmod_mat_entry(B, r, c) == 0) c++; pivot[r] = c; } }
            printf("m=%d N=%d dimAt4=%zu rankR=%ld dimA4=%ld\n", m, N, mons4.size(), rankR, (long)mons4.size() - rankR); fflush(stdout);
        }
        auto inRow = [&](Dense v) { for (long r = 0; r < rankR; r++) { int f = v[pivot[r]]; if (!f) continue;
                for (size_t c = pivot[r]; c < mons4.size(); c++) v[c] = (v[c] + 9 - f * nmod_mat_entry(B, r, c)) % 3; }
            for (auto x : v) if (x) return false; return true; };
        auto parseCols = [&](const string& txt) { VI co(m*N, 0); int c = 0, i = 0;
            for (char ch : txt) { if (ch == ' ') { c++; i = 0; continue; } co[i*N + c] = ch - '0'; i++; }
            if (c != N - 1) { fprintf(stderr, "bad column count in %s\n", txt.c_str()); exit(3); } return co; };
        VI a0 = parseCols(pr[2]), b0 = parseCols(pr[3]);
        Poly p0 = mul(mul(linear(a0), linear(a0)), mul(linear(b0), linear(b0)));
        int inR = 0; bool inR0 = inRow(toDense(p0));
        for (int tr = 0; tr < trials; tr++) { VI a = a0, b = b0;
            for (VI* f : {&a, &b}) { VI shift(m); for (auto& x : shift) x = u3(rng);
                for (int i = 0; i < m; i++) for (int c = 0; c < N; c++) (*f)[i*N + c] = ((*f)[i*N + c] + shift[i]) % 3; }
            Poly l1 = linear(a), l2 = linear(b); inR += inRow(toDense(mul(mul(l1, l1), mul(l2, l2)))); }
        printf("N=%d %s: unshifted product %s, inR_unshifted=%d, inR_shifted=%d/%d\n", N, pr[1].c_str(), p0.empty() ? "zero" : "nonzero", (int)inR0, inR, trials); fflush(stdout);
    }
    if (lastN >= 0) nmod_mat_clear(B); return 0;
}
