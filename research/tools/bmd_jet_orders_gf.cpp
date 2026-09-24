// Exact per-order minimum degrees on a grid S^n, S an F_2-subspace of GF(2^a), via origin jets.
//
// Statement computed.  delta_S(n,k,l) is the least total degree of a formal polynomial over GF(2^a)
// with Hasse multiplicity >= k at every nonzero point of S^n and exactly l at the origin.
//
// Reduction (as in bmd_jet_orders.cpp).  With L(x) = prod_{s in S}(x - s) (monic, degree s = |S|) and
// y_i = L(x_i), polynomials expand uniquely as sum c x^eps y^e with 0 <= eps_i < s, of degree
// max(|eps| + s|e|); (y)^k is the intersection of the m_a^k over a in S^n (CRT, dimension
// s^n C(n+k-1,n)).  Admissible P correspond to origin jets v via P(v) = T(sum_beta v_beta prod_i
// g_{beta_i}(x_i)), g_b = x^b prod_{t in S, t != 0}(1 - x/t)^(2^K), 2^K >= k, which is x^b mod x^k and
// vanishes to order 2^K at every nonzero t in S.  One leftmost-pivot elimination per case.
//
// Usage: bmd_jet_orders_gf a poly n k S0 S1 ... [--out PATH]
//   a: field degree; poly: the irreducible modulus as an integer (e.g. 11 = x^3+x+1 for GF(8));
//   S0 S1 ...: the elements of S as integers (bit i = coefficient of alpha^i), including 0.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>

static int A, POLY, Q;
static std::vector<int> MUL, INV;
static int gmul(int a, int b) { return MUL[a * Q + b]; }
static void init_field() {
    Q = 1 << A; MUL.assign(Q * Q, 0); INV.assign(Q, 0);
    for (int a = 0; a < Q; ++a) for (int b = 0; b < Q; ++b) {
        int r = 0, x = a, y = b;
        while (y) { if (y & 1) r ^= x; y >>= 1; x <<= 1; if (x & Q) x ^= POLY; }
        MUL[a * Q + b] = r;
    }
    for (int a = 1; a < Q; ++a) for (int b = 1; b < Q; ++b) if (gmul(a, b) == 1) INV[a] = b;
}
using Poly = std::vector<int>;
static Poly pmul(const Poly& a, const Poly& b) {
    Poly r(a.size() + b.size() - 1, 0);
    for (size_t i = 0; i < a.size(); ++i) if (a[i]) for (size_t j = 0; j < b.size(); ++j) r[i + j] ^= gmul(a[i], b[j]);
    return r;
}
// f = sum_j (sum_{eps<s} T[eps][j] x^eps) y^j with y = L monic of degree s
static void ybasis(Poly f, const Poly& L, int s, std::vector<std::vector<int>>& T, int jmax) {
    T.assign(s, std::vector<int>(jmax, 0));
    for (int j = 0; ; ++j) {
        while (!f.empty() && !f.back()) f.pop_back();
        if (f.empty()) break;
        Poly quot(f.size() > (size_t)s ? f.size() - s : 0, 0);
        for (int d = (int)f.size() - 1; d >= s; --d) {
            int c = f[d]; if (!c) continue;
            quot[d - s] = c;
            for (int t = 0; t <= s; ++t) f[d - s + t] ^= gmul(c, L[t]);  // subtract c x^(d-s) L
        }
        if (j < jmax) for (int e = 0; e < s && e < (int)f.size(); ++e) T[e][j] = f[e];
        f = quot;
    }
}

int main(int argc, char** argv) {
    if (argc < 6) { std::fprintf(stderr, "usage: bmd_jet_orders_gf a poly n k S... [--out PATH]\n"); return 2; }
    A = std::atoi(argv[1]); POLY = std::atoi(argv[2]); int n = std::atoi(argv[3]), k = std::atoi(argv[4]);
    std::vector<int> S; std::string out;
    for (int i = 5; i < argc; ++i) {
        if (!std::strcmp(argv[i], "--out") && i + 1 < argc) { out = argv[++i]; continue; }
        S.push_back(std::atoi(argv[i]));
    }
    init_field();
    int s = S.size();
    for (int a : S) for (int b : S) if (std::find(S.begin(), S.end(), a ^ b) == S.end()) {
        std::fprintf(stderr, "S is not an additive subgroup\n"); return 2; }
    Poly L = {1};
    for (int t : S) L = pmul(L, Poly{t, 1});  // (x - t) = x + t in characteristic 2
    int K2 = 1; while (K2 < k) K2 *= 2;
    Poly h = {1};
    for (int t : S) if (t) {  // (1 - x/t)^(2^K) = 1 + x^(2^K) / t^(2^K)
        int ti = INV[t], tp = 1; for (int r = 0; r < K2; ++r) tp = gmul(tp, ti);
        Poly f(K2 + 1, 0); f[0] = 1; f[K2] = tp; h = pmul(h, f);
    }
    std::vector<std::vector<std::vector<int>>> T(k);
    for (int b = 0; b < k; ++b) { Poly xb(b + 1, 0); xb[b] = 1; ybasis(pmul(xb, h), L, s, T[b], k); }
    std::vector<std::vector<int>> cols, es;
    { std::vector<int> cur(n, 0);
      struct R { static void go(int i, int left, int n, std::vector<int>& cur, std::vector<std::vector<int>>& o) {
          if (i == n) { o.push_back(cur); return; }
          for (int e = 0; e <= left; ++e) { cur[i] = e; go(i + 1, left - e, n, cur, o); } cur[i] = 0; } };
      R::go(0, k - 1, n, cur, cols); es = cols; }
    std::stable_sort(cols.begin(), cols.end(), [](const std::vector<int>& a, const std::vector<int>& b) {
        int sa = 0, sb = 0; for (int x : a) sa += x; for (int x : b) sb += x; return sa > sb; });
    long C = cols.size();
    std::vector<int> lev(C); std::vector<long> N(k, 0);
    for (long c = 0; c < C; ++c) { int t = 0; for (int x : cols[c]) t += x; lev[c] = t; N[t]++; }
    long npow = 1; for (int i = 0; i < n; ++i) npow *= s;
    int maxdeg = n * (s - 1) + s * (k - 1);
    std::vector<long> pivrow(C, -1);
    std::vector<std::vector<uint8_t>> basis;
    std::vector<long> pivcount(k, 0);
    std::vector<int> delta(k, -1);
    int remaining = k;
    for (int D = maxdeg; D >= 0 && remaining > 0; --D) {
        for (long epsId = 0; epsId < npow; ++epsId) {
            std::vector<int> eps(n); long t = epsId; int pe = 0;
            for (int i = 0; i < n; ++i) { eps[i] = t % s; t /= s; pe += eps[i]; }
            if ((D - pe) % s != 0 || D - pe < 0) continue;
            int se = (D - pe) / s;
            for (const auto& e : es) {
                int t2 = 0; for (int x : e) t2 += x;
                if (t2 != se) continue;
                std::vector<uint8_t> row(C);
                for (long c = 0; c < C; ++c) {
                    int v = 1;
                    for (int i = 0; i < n && v; ++i) v = gmul(v, T[cols[c][i]][eps[i]][e[i]]);
                    row[c] = v;
                }
                long lead = -1;
                for (long c = 0; c < C; ++c) {
                    if (!row[c]) continue;
                    if (pivrow[c] < 0) { lead = c; break; }
                    const auto& br = basis[pivrow[c]];
                    int f = row[c];
                    for (long d = c; d < C; ++d) if (br[d]) row[d] ^= gmul(f, br[d]);
                }
                if (lead < 0) continue;
                int iv = INV[row[lead]];
                for (long d = lead; d < C; ++d) row[d] = gmul(row[d], iv);
                pivrow[lead] = basis.size(); basis.push_back(row); pivcount[lev[lead]]++;
            }
        }
        for (int l = 0; l < k; ++l)
            if (delta[l] < 0 && !(pivcount[l] < N[l])) { delta[l] = D; --remaining; }
    }
    std::string js = "{\"a\": " + std::to_string(A) + ", \"S\": [";
    for (size_t i = 0; i < S.size(); ++i) js += (i ? ", " : "") + std::to_string(S[i]);
    js += "], \"n\": " + std::to_string(n) + ", \"k\": " + std::to_string(k) + ", \"delta\": [";
    for (int l = 0; l < k; ++l) js += (l ? ", " : "") + std::to_string(delta[l]);
    js += "]}\n";
    if (!out.empty()) { FILE* f = std::fopen(out.c_str(), "w"); std::fputs(js.c_str(), f); std::fclose(f); }
    std::fputs(js.c_str(), stdout);
    return 0;
}
