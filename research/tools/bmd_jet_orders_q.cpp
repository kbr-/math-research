// Exact per-order minimum degrees on the full grid F_p^n (p prime), via origin jets.
//
// Statement computed.  delta_p(n,k,l) is the least total degree of a formal polynomial P over F_p
// with Hasse multiplicity >= k at every nonzero point of F_p^n and exactly l at the origin.
//
// Reduction (as in bmd_jet_orders.cpp, with y_i = x_i^p - x_i).  Polynomials expand uniquely as
// sum c x^eps y^e with 0 <= eps_i < p, of degree max(|eps| + p|e|).  Terms with |e| >= k lie in
// (y)^k, inside every m_a^k; the span of the terms with |e| < k maps isomorphically onto the product
// of the jet spaces (CRT, dimension p^n C(n+k-1,n)).  Admissible P correspond to origin jets v via
// P(v) = T(sum_beta v_beta prod_i g_{beta_i}(x_i)), g_b = x^b (1 - x^((p-1) p^K)), p^K >= k, which is
// x^b mod x^k and vanishes to order p^K at every nonzero a.  One leftmost-pivot elimination with
// columns in descending |beta| and rows in descending degree gives delta_p(n,k,l) for every l.
//
// Usage: bmd_jet_orders_q p n k [--out PATH] [--cube] [--witness L DW] [--mult BITS:M ...]
//        bmd_jet_orders_q --series p1,p2,... n k1,k2,... OUTDIR [--cube]
// --series runs every (p, k) in one process and writes OUTDIR/p{p}-n{n}-k{k}.json for each.
// --mult (cube only): multiplicity M instead of k at the nonzero point BITS (e.g. 111:9).
// --cube: the cube {0,1}^n over F_p instead of the full grid (y = x^2 - x, eps in {0,1}).
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>
#include <chrono>

static int P;
static int S;  // grid size per coordinate: P (full grid F_p^n) or 2 (cube {0,1}^n)
static int md(long a) { a %= P; return a < 0 ? a + P : a; }
static int inv(int a) { for (int b = 1; b < P; ++b) if (a * b % P == 1) return b; return 0; }

// f = sum_j (sum_{eps<S} T[eps][j] x^eps) y^j, y = x^S - x; returns T[eps][j] for j < jmax.
static void ybasis(std::vector<int> f, std::vector<std::vector<int>>& T, int jmax) {
    T.assign(S, std::vector<int>(jmax, 0));
    for (int j = 0; ; ++j) {
        while (!f.empty() && f.back() == 0) f.pop_back();
        if (f.empty()) break;
        // divide f by the monic y = x^p - x: f = quot * y + rem, deg rem < p
        std::vector<int> quot(f.size() > (size_t)S ? f.size() - S : 0, 0);
        for (int d = (int)f.size() - 1; d >= S; --d) {
            int c = f[d];
            if (!c) continue;
            quot[d - S] = c;
            f[d] = 0;
            f[d - S + 1] = md(f[d - S + 1] + c);  // subtract c x^(d-S) (x^S - x): adds c x^(d-S+1)
        }
        if (j < jmax) for (int e = 0; e < S && e < (int)f.size(); ++e) T[e][j] = f[e];
        f = quot;
    }
}

static int run_one(int argc, char** argv) {
    if (argc < 4) { std::fprintf(stderr, "usage: bmd_jet_orders_q p n k [--out PATH]\n"); return 2; }
    P = std::atoi(argv[1]); int n = std::atoi(argv[2]), k = std::atoi(argv[3]);
    S = P;
    int wl = -1, wd = -1;
    std::vector<std::pair<unsigned, int>> pointMult;  // --mult BITS:M (cube only): multiplicity M at point BITS
    std::string out;
    for (int i = 4; i < argc; ++i) {
        if (!std::strcmp(argv[i], "--out") && i + 1 < argc) out = argv[++i];
        else if (!std::strcmp(argv[i], "--cube")) S = 2;
        else if (!std::strcmp(argv[i], "--witness") && i + 2 < argc) { wl = std::atoi(argv[++i]); wd = std::atoi(argv[++i]); }
        else if (!std::strcmp(argv[i], "--mult") && i + 1 < argc) {
            std::string a = argv[++i]; size_t c = a.find(':'); unsigned bits = 0;
            for (size_t j = 0; j < c; ++j) if (a[j] == '1') bits |= 1u << j;
            pointMult.push_back({bits, std::atoi(a.c_str() + c + 1)});
        }
    }
    auto t0 = std::chrono::steady_clock::now();
    // Per-point multiplicities (cube only): every nonzero point needs multiplicity mult[a] (default k).
    // The truncation order is K = max of all of them; a point with mult[a] < K gets free jet columns
    // gamma with mult[a] <= |gamma| < K, lifted by prod_i g^{(a_i)}_{gamma_i}(x_i), where
    // g^{(1)}_b = (x-1)^b x^(p^K) is (x-1)^b near 1 and vanishes to order p^K at 0.
    const int kUser = k;
    std::vector<int> mult(1u << n, k);
    if (!pointMult.empty() && S != 2) { std::fprintf(stderr, "--mult needs --cube\n"); return 2; }
    for (auto& pm : pointMult) mult[pm.first] = pm.second;
    for (unsigned a = 1; a < (1u << n) && S == 2; ++a) k = std::max(k, mult[a]);
    long pK = 1; while (pK < k) pK *= P;
    std::vector<std::vector<std::vector<int>>> T(k);  // T[b][eps][j]
    for (int b = 0; b < k; ++b) {
        long top = b + (S - 1) * pK;  // g_b = x^b (1 - x^((S-1) p^K)): order p^K at every nonzero grid value
        std::vector<int> f(top + 1, 0);
        f[b] = 1; f[top] = md(-1);
        ybasis(f, T[b], k);
    }
    std::vector<std::vector<std::vector<int>>> T1(k);  // g^{(1)}_b = (x-1)^b x^(p^K), cube only
    for (int b = 0; b < k && S == 2; ++b) {
        std::vector<int> f(b + pK + 1, 0);
        for (int j = 0; j <= b; ++j) {  // (x-1)^b = sum C(b,j) x^j (-1)^(b-j)
            long c = 1; for (int t = 0; t < j; ++t) c = c * (b - t) / (t + 1);
            f[pK + j] = md((((b - j) % 2) ? -1 : 1) * (c % P));
        }
        ybasis(f, T1[b], k);
    }
    std::vector<std::vector<int>> cols, es;
    { std::vector<int> cur(n, 0);
      struct R { static void go(int i, int left, int n, std::vector<int>& cur, std::vector<std::vector<int>>& o) {
          if (i == n) { o.push_back(cur); return; }
          for (int e = 0; e <= left; ++e) { cur[i] = e; go(i + 1, left - e, n, cur, o); } cur[i] = 0; } };
      R::go(0, k - 1, n, cur, cols); es = cols; }
    std::stable_sort(cols.begin(), cols.end(), [](const std::vector<int>& a, const std::vector<int>& b) {
        int sa = 0, sb = 0; for (int x : a) sa += x; for (int x : b) sb += x; return sa > sb; });
    // extra free columns first (point, local jet), then the origin jets in descending |beta|
    std::vector<unsigned> colPoint;
    { std::vector<std::vector<int>> extra; std::vector<unsigned> ep;
      for (unsigned a = 1; a < (1u << n) && S == 2; ++a)
          for (const auto& g : es) { int sg = 0; for (int x : g) sg += x; if (sg >= mult[a]) { extra.push_back(g); ep.push_back(a); } }
      colPoint = ep; colPoint.resize(ep.size() + cols.size(), 0);
      extra.insert(extra.end(), cols.begin(), cols.end()); cols = extra; }
    long C = cols.size();
    std::vector<int> lev(C); std::vector<long> N(k, 0);
    for (long c = 0; c < C; ++c) {
        int s = 0; for (int x : cols[c]) s += x;
        lev[c] = colPoint[c] ? -1 : s; if (!colPoint[c]) N[s]++;
    }
    long npow = 1; for (int i = 0; i < n; ++i) npow *= S;
    int maxdeg = n * (S - 1) + S * (k - 1);
    std::vector<long> pivrow(C, -1);
    std::vector<std::vector<uint8_t>> basis;
    std::vector<long> pivcount(k, 0);
    std::vector<int> delta(k, -1);
    int remaining = k; long rowsUsed = 0;
    for (int D = maxdeg; D >= 0 && remaining > 0; --D) {
        for (long epsId = 0; epsId < npow; ++epsId) {
            std::vector<int> eps(n); long t = epsId; int pe = 0;
            for (int i = 0; i < n; ++i) { eps[i] = t % S; t /= S; pe += eps[i]; }
            if ((D - pe) % S != 0 || D - pe < 0) continue;
            int se = (D - pe) / S;
            for (const auto& e : es) {
                int s = 0; for (int x : e) s += x;
                if (s != se) continue;
                std::vector<uint8_t> row(C);
                for (long c = 0; c < C; ++c) {
                    long v = 1;
                    for (int i = 0; i < n && v; ++i)
                        v = v * (((colPoint[c] >> i) & 1u) ? T1 : T)[cols[c][i]][eps[i]][e[i]] % P;
                    row[c] = v;
                }
                ++rowsUsed;
                long lead = -1;
                for (long c = 0; c < C; ++c) {
                    if (!row[c]) continue;
                    if (pivrow[c] < 0) { lead = c; break; }
                    const auto& br = basis[pivrow[c]];
                    int f = row[c];  // basis rows are normalized to leading 1
                    for (long d = c; d < C; ++d) if (br[d]) row[d] = md(row[d] - f * br[d]);
                }
                if (lead < 0) continue;
                int iv = inv(row[lead]);
                for (long d = lead; d < C; ++d) row[d] = row[d] * iv % P;
                pivrow[lead] = basis.size();
                basis.push_back(row);
                if (lev[lead] >= 0) pivcount[lev[lead]]++;
            }
        }
        for (int l = 0; l < k; ++l)
            if (delta[l] < 0 && !(pivcount[l] < N[l])) { delta[l] = D; --remaining; }
        if (D == wd + 1) {
            // --witness L DW: a jet of order L with deg P(v) <= DW (one free level-L column set to 1)
            long freeCol = -1;
            for (long c = 0; c < C && freeCol < 0; ++c) if (lev[c] == wl && pivrow[c] < 0) freeCol = c;
            if (freeCol < 0) { std::printf("witness: none of order %d with degree <= %d\n", wl, wd); return 0; }
            std::vector<int> v(C, 0); v[freeCol] = 1;
            for (long c = C - 1; c >= 0; --c) {
                if (pivrow[c] < 0) continue;
                const auto& br = basis[pivrow[c]];
                long s = 0;
                for (long d = c + 1; d < C; ++d) if (br[d] && v[d]) s += br[d] * v[d];
                v[c] = md(-s);
            }
            std::printf("witness p=%d grid=%d n=%d k=%d order %d degree<=%d\nterms eps|e|coef:\n", P, S, n, k, wl, wd);
            for (long epsId = 0; epsId < npow; ++epsId) {
                std::vector<int> eps(n); long t = epsId;
                for (int i = 0; i < n; ++i) { eps[i] = t % S; t /= S; }
                for (const auto& e : es) {
                    long s = 0;
                    for (long c = 0; c < C; ++c) if (v[c]) {
                        long term = v[c];
                        for (int i = 0; i < n && term; ++i)
                            term = term * (((colPoint[c] >> i) & 1u) ? T1 : T)[cols[c][i]][eps[i]][e[i]] % P;
                        s += term;
                    }
                    if (md(s) == 0) continue;
                    for (int i = 0; i < n; ++i) std::printf("%d%s", eps[i], i + 1 < n ? "," : "|");
                    for (int i = 0; i < n; ++i) std::printf("%d%s", e[i], i + 1 < n ? "," : "|");
                    std::printf("%d\n", md(s));
                }
            }
            return 0;
        }
    }
    double secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    std::string js = "{\"p\": " + std::to_string(P) + ", \"grid\": " + std::to_string(S) + ", \"n\": " + std::to_string(n) + ", \"k\": " + std::to_string(k) +
        ", \"columns\": " + std::to_string(C) + ", \"rows_used\": " + std::to_string(rowsUsed) +
        ", \"seconds\": " + std::to_string(secs) + ", \"delta\": [";
    for (int l = 0; l < k; ++l) js += (l ? ", " : "") + std::to_string(delta[l]);
    (void)kUser;
    js += "]}\n";
    if (!out.empty()) { FILE* f = std::fopen(out.c_str(), "w"); std::fputs(js.c_str(), f); std::fclose(f); }
    std::fputs(js.c_str(), stdout);
    return 0;
}

static std::vector<int> parse_list(const char* s) {
    std::vector<int> v; while (*s) { v.push_back(std::atoi(s)); while (*s && *s != ',') ++s; if (*s) ++s; } return v;
}

int main(int argc, char** argv) {
    if (argc >= 6 && !std::strcmp(argv[1], "--series")) {
        std::vector<int> ps = parse_list(argv[2]), ks = parse_list(argv[4]);
        bool cube = argc > 6 && !std::strcmp(argv[6], "--cube");
        for (int p : ps) for (int k : ks) {
            std::string sp = std::to_string(p), sk = std::to_string(k);
            std::string out = std::string(argv[5]) + "/p" + sp + "-n" + argv[3] + "-k" + sk + ".json";
            std::vector<std::string> a = {argv[0], sp, argv[3], sk, "--out", out};
            if (cube) a.push_back("--cube");
            std::vector<char*> av; for (auto& x : a) av.push_back(&x[0]);
            int rc = run_one((int)av.size(), av.data());
            std::fflush(stdout);
            if (rc) return rc;
        }
        return 0;
    }
    return run_one(argc, argv);
}
