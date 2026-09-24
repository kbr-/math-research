// Pure tops of two-input augmented ENS blocks in T = F_3[y_1..y_d]/(y_i^3): m_a = l_{a1}^2 l_{a2}^2.
//
// Condition (P) in degree s: the syzygies of the m_a in degree s are spanned by the member syzygies
// (l_{a1}, l_{a2}) e_a and, for s = 8, the Koszul pairs m_b e_a - m_a e_b.  Per block the rows m_a * mu use the
// quotient basis mu in T_{s-4}(others), the monomials in the d-2 coordinates complementing a nonzero 2x2 minor
// of (l_{a1}, l_{a2}), since m_a (l_{a1}, l_{a2}) = 0.  So (P) in degree s <= 7 says these rows are independent
// (rank M dim T_{s-4}(d-2)), and in degree 8 that their rank is M dim T_4(d-2) - C(M,2) with the Koszul pairs
// independent (checked through the reductions of m_b, b != a, modulo (l_{a1}, l_{a2}) being independent in
// T_4(others) for every a).  (P) for M blocks passes to every prefix, so an elimination that falls short of the
// prefix count is abandoned at once.
//
// Modes:
//   pure_tops single d s Mmax seed koszul distinct
//       ranks of every prefix M (lines "M rank koszul_ok"), forms on stderr; used by reference.py.
//   pure_tops grid DMIN DMAX SMIN SMAX SEEDS
//       for every d in [DMIN, DMAX] and D in [SMIN, SMAX]: M = M_exp(D, d), the largest M whose expected rank fits
//       in every degree 5 <= s <= D; search seeds 7e6 + 1000 d + k, k < SEEDS, for one tuple of M blocks with
//       all 2M forms pairwise non-proportional that satisfies (P) in every degree 5 <= s <= D.  One JSON line per
//       case.  Cases with dim T_D >= 3000 run one at a time with parallel row reduction; the others run in
//       parallel, one case per thread.
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>
#include <omp.h>
using namespace std;

struct Rng { uint64_t st; uint64_t next() { uint64_t z = (st += 0x9e3779b97f4a7c15ULL); z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL; z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL; return z ^ (z >> 31); } };
static int inv3(int x) { return x % 3 == 1 ? 1 : 2; }

struct Ctx {
  int d; vector<int> p3;
  explicit Ctx(int d_) : d(d_), p3(d_ + 1, 1) { for (int i = 1; i <= d; i++) p3[i] = p3[i - 1] * 3; }
  int dig(int c, int i) const { return (c / p3[i]) % 3; }
  int degc(int c) const { int t = 0; for (int i = 0; i < d; i++) t += dig(c, i); return t; }
  vector<uint8_t> mul_lin(const vector<uint8_t>& p, const vector<int>& l) const {
    vector<uint8_t> q(p.size(), 0);
    for (size_t c = 0; c < p.size(); c++) if (p[c]) for (int i = 0; i < d; i++) if (l[i] && dig(c, i) < 2) q[c + p3[i]] = (q[c + p3[i]] + p[c] * l[i]) % 3;
    return q;
  }
  vector<uint8_t> top(const vector<int>& a, const vector<int>& b) const {
    vector<uint8_t> p(p3[d], 0); p[0] = 1; p = mul_lin(p, a); p = mul_lin(p, a); p = mul_lin(p, b); return mul_lin(p, b);
  }
};

static long long Tdim(int d, int s) {  // coefficient of t^s in (1+t+t^2)^d
  vector<long long> c(1, 1);
  for (int k = 0; k < d; k++) { vector<long long> n(c.size() + 2, 0); for (size_t i = 0; i < c.size(); i++) for (int j = 0; j < 3; j++) n[i + j] += c[i]; c = n; }
  return (s >= 0 && s < (int)c.size()) ? c[s] : 0;
}
static long long expected(int d, int s, long long M) { return M * Tdim(d - 2, s - 4) - (s == 8 ? M * (M - 1) / 2 : 0); }

struct Block { vector<int> a, b; int i1, i2; };

static bool proportional(const vector<int>& u, const vector<int>& v, int d) {
  for (int x = 0; x < d; x++) for (int y = x + 1; y < d; y++) if ((u[x] * v[y] - u[y] * v[x] + 9) % 3) return false;
  return true;
}
static vector<Block> sample_blocks(int d, int M, uint64_t seed, bool distinct, FILE* log) {
  Rng r{seed}; vector<Block> bl;
  while ((int)bl.size() < M) {
    Block B; B.a.assign(d, 0); B.b.assign(d, 0); B.i1 = -1;
    for (int i = 0; i < d; i++) { B.a[i] = r.next() % 3; B.b[i] = r.next() % 3; }
    for (int x = 0; x < d && B.i1 < 0; x++) for (int y = x + 1; y < d; y++) if ((B.a[x] * B.b[y] - B.a[y] * B.b[x] + 9) % 3) { B.i1 = x; B.i2 = y; break; }
    if (B.i1 < 0) continue;
    bool clash = false;
    if (distinct) for (auto& C : bl) if (proportional(B.a, C.a, d) || proportional(B.a, C.b, d) || proportional(B.b, C.a, d) || proportional(B.b, C.b, d)) { clash = true; break; }
    if (clash) continue;
    if (log) { fprintf(log, "F"); for (int i = 0; i < d; i++) fprintf(log, " %d", B.a[i]); for (int i = 0; i < d; i++) fprintf(log, " %d", B.b[i]); fprintf(log, "\n"); }
    bl.push_back(B);
  }
  return bl;
}

static int small_rank(vector<vector<uint8_t>> v) {
  int r = 0, n = v.empty() ? 0 : v[0].size();
  for (int c = 0; c < n && r < (int)v.size(); c++) {
    int piv = -1; for (int i = r; i < (int)v.size(); i++) if (v[i][c]) { piv = i; break; }
    if (piv < 0) continue; swap(v[r], v[piv]); int iv = inv3(v[r][c]);
    for (auto& x : v[r]) x = (x * iv) % 3;
    for (int i = 0; i < (int)v.size(); i++) if (i != r && v[i][c]) { int f = v[i][c]; for (int j = c; j < n; j++) v[i][j] = (v[i][j] + 9 - f * v[r][j]) % 3; }
    r++;
  }
  return r;
}

// Koszul independence for the first M blocks: for every a, the reductions of m_b (b != a) modulo (l_a1, l_a2)
// are independent in T_4(others).
static bool koszul_ok(const Ctx& X, const vector<Block>& bl, int M) {
  int d = X.d;
  for (int A = 0; A < M; A++) {
    const Block& P = bl[A]; int x = P.i1, y = P.i2;
    int id = inv3((P.a[x] * P.b[y] - P.a[y] * P.b[x] + 9) % 3);
    vector<int> ax(d, 0), ay(d, 0);
    for (int k = 0; k < d; k++) if (k != x && k != y) {
      int u = (3 - P.a[k]) % 3, v = (3 - P.b[k]) % 3;
      ax[k] = ((P.b[y] * u - P.a[y] * v) % 3 + 3) * id % 3; ay[k] = ((P.a[x] * v - P.b[x] * u) % 3 + 3) * id % 3;
    }
    vector<int> cols; for (int c = 0; c < X.p3[d]; c++) if (X.degc(c) == 4 && X.dig(c, x) == 0 && X.dig(c, y) == 0) cols.push_back(c);
    vector<vector<uint8_t>> vs;
    for (int B = 0; B < M; B++) if (B != A) {
      vector<int> sa(d, 0), sb(d, 0);
      for (int k = 0; k < d; k++) if (k != x && k != y) { sa[k] = (bl[B].a[k] + bl[B].a[x] * ax[k] + bl[B].a[y] * ay[k]) % 3; sb[k] = (bl[B].b[k] + bl[B].b[x] * ax[k] + bl[B].b[y] * ay[k]) % 3; }
      vector<uint8_t> mb = X.top(sa, sb), v(cols.size()); for (size_t j = 0; j < cols.size(); j++) v[j] = mb[cols[j]]; vs.push_back(v);
    }
    if (!vs.empty() && small_rank(vs) < (int)vs.size()) return false;
  }
  return true;
}

// Incremental elimination in degree s over the blocks.  prefix_rank receives the rank after each block.  With
// abort_short, stops as soon as a prefix rank falls below expected(d, s, prefix) and returns false.
static bool eliminate(const Ctx& X, int s, const vector<Block>& bl, int M, bool parallel, bool abort_short, vector<int>* prefix_rank) {
  int d = X.d; vector<int> col(X.p3[d], -1); int ncols = 0;
  for (int c = 0; c < X.p3[d]; c++) if (X.degc(c) == s) col[c] = ncols++;
  vector<vector<uint8_t>> basis; vector<int> pivcol(ncols, -1);
  for (int A = 0; A < M; A++) {
    const Block& B = bl[A]; vector<uint8_t> m = X.top(B.a, B.b);
    vector<pair<int, int>> terms; for (int c = 0; c < X.p3[d]; c++) if (m[c]) terms.push_back({c, m[c]});
    vector<int> mus; for (int c = 0; c < X.p3[d]; c++) if (X.degc(c) == s - 4 && X.dig(c, B.i1) == 0 && X.dig(c, B.i2) == 0) mus.push_back(c);
    int nr = mus.size(); vector<vector<uint8_t>> rows(nr, vector<uint8_t>(ncols, 0));
    #pragma omp parallel for schedule(dynamic) if (parallel)
    for (int r = 0; r < nr; r++) {
      vector<uint8_t>& row = rows[r]; int mu = mus[r];
      for (auto& t : terms) { bool ok = true; for (int i = 0; i < d; i++) if (X.dig(t.first, i) + X.dig(mu, i) > 2) { ok = false; break; }
        if (ok) { int k = col[t.first + mu]; row[k] = (row[k] + t.second) % 3; } }
      for (int c = 0; c < ncols; c++) if (row[c] && pivcol[c] >= 0) { const vector<uint8_t>& pv = basis[pivcol[c]]; int f = 3 - row[c]; for (int j = c; j < ncols; j++) row[j] = (row[j] + f * pv[j]) % 3; }
    }
    for (int r = 0; r < nr; r++) {
      vector<uint8_t>& row = rows[r];
      for (int c = 0; c < ncols; c++) if (row[c] && pivcol[c] >= 0) { const vector<uint8_t>& pv = basis[pivcol[c]]; int f = 3 - row[c]; for (int j = c; j < ncols; j++) row[j] = (row[j] + f * pv[j]) % 3; }
      int lead = -1; for (int c = 0; c < ncols; c++) if (row[c]) { lead = c; break; }
      if (lead < 0) continue; int iv = inv3(row[lead]); for (int j = lead; j < ncols; j++) row[j] = (row[j] * iv) % 3;
      pivcol[lead] = basis.size(); basis.push_back(row);
    }
    if (prefix_rank) prefix_rank->push_back(basis.size());
    if (abort_short && (long long)basis.size() < expected(d, s, A + 1)) return false;
  }
  return true;
}

struct Case { int d, D; long long M; int seeds_tried; long long found_seed; vector<long long> ranks; };

static void run_case(Case& K, int S, bool parallel) {
  Ctx X(K.d); K.found_seed = -1; K.seeds_tried = 0;
  for (int k = 0; k < S && K.found_seed < 0; k++) {
    uint64_t seed = 7000000ULL + 1000ULL * K.d + k; K.seeds_tried = k + 1;
    vector<Block> bl = sample_blocks(K.d, K.M, seed, true, nullptr);
    bool ok = true; vector<long long> ranks;
    for (int s = 5; s <= K.D && ok; s++) {
      vector<int> pr; ok = eliminate(X, s, bl, K.M, parallel, true, &pr);
      if (ok && s == 8) ok = koszul_ok(X, bl, K.M);
      if (ok) ranks.push_back(pr.back());
    }
    if (ok) { K.found_seed = seed; K.ranks = ranks; }
  }
}

int main(int argc, char** argv) {
  string mode = argc > 1 ? argv[1] : "";
  if (mode == "single") {
    int d = atoi(argv[2]), s = atoi(argv[3]), Mmax = atoi(argv[4]); uint64_t seed = strtoull(argv[5], 0, 10); int kos = atoi(argv[6]), distinct = atoi(argv[7]);
    Ctx X(d); vector<Block> bl = sample_blocks(d, Mmax, seed, distinct, stderr); vector<int> pr;
    eliminate(X, s, bl, Mmax, true, false, &pr);
    for (int M = 1; M <= Mmax; M++) printf("%d %d %d\n", M, pr[M - 1], kos ? (int)koszul_ok(X, bl, M) : -1);
    return 0;
  }
  if (mode != "grid") { fprintf(stderr, "usage: pure_tops single d s Mmax seed koszul distinct | grid DMIN DMAX SMIN SMAX SEEDS\n"); return 2; }
  int dmin = atoi(argv[2]), dmax = atoi(argv[3]), smin = atoi(argv[4]), smax = atoi(argv[5]), S = atoi(argv[6]);
  vector<Case> cases;
  for (int d = dmin; d <= dmax; d++) for (int D = smin; D <= smax; D++) {
    long long M = 0;
    auto fits = [&](long long m) { for (int s = 5; s <= D; s++) if (expected(d, s, m) > Tdim(d, s) || expected(d, s, m) <= expected(d, s, m - 1)) return false; return true; };
    while (fits(M + 1)) M++;
    cases.push_back({d, D, M, 0, -1, {}});
  }
  vector<int> big, small;
  for (int i = 0; i < (int)cases.size(); i++) (Tdim(cases[i].d, cases[i].D) >= 3000 ? big : small).push_back(i);
  for (int i : big) run_case(cases[i], S, true);
  #pragma omp parallel for schedule(dynamic, 1)
  for (int j = 0; j < (int)small.size(); j++) run_case(cases[small[j]], S, false);
  for (auto& K : cases) {
    printf("{\"d\": %d, \"D\": %d, \"M\": %lld, \"forms\": %lld, \"seeds_tried\": %d, \"witness_seed\": %lld, \"ranks_s5_to_D\": [", K.d, K.D, K.M, 2 * K.M, K.seeds_tried, K.found_seed);
    for (size_t i = 0; i < K.ranks.size(); i++) printf("%s%lld", i ? ", " : "", K.ranks[i]);
    printf("], \"expected_s5_to_D\": [");
    for (int s = 5; s <= K.D; s++) printf("%s%lld", s > 5 ? ", " : "", expected(K.d, s, K.M));
    printf("]}\n");
  }
  return 0;
}
