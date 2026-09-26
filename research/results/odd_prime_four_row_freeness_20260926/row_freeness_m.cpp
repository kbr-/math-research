// Cross-member falls of randomized-prefix members on the weak PHP base's point set, by evaluation ranks.
// Universe: column-injective 0/1 assignments of m rows x Ncol columns with total occupancy = m mod 3
// (the point set P of thm:global-closure-gluing); variables are cells (row*Ncol + col); the monomial
// basis is the column-injective squarefree monomials (others vanish on P). Member b's ideal is
// I(P cap P_b); a cross fall is an element of gr I(P cap all P_b) outside sum_b gr I(P cap P_b).
// Derived from fall_degree.cpp (the Boolean-cube version).
// Statement tested (member-universality follow-up): at fixed total excluded density spread over
// M members (h = 2t+1 dense forms each, t random prefix rows), does the first degree d with
// dim gr I(cap P_b)_d > dim sum_b gr I(P_b)_d stay near N/2 or descend with M?
// In the cube's graded ring (squarefree monomials), (gr I(P))_d = degree-d parts of
// ker(E_{<=d} on P); its dimension is C(N,d) - (rank_d - rank_{d-1}). Exact arithmetic mod 3 (FLINT).
// Usage: row_freeness_m m Ncol h t M dmax seed mode [dump_instance_path | flag]
// General-m version (m - 1 acting row sums) of three_row_freeness.cpp, same indexing and modes,
// plus the suffix +nf (normal form modulo the row sums).
// Mode rowform (added for the three-row test): every member's form 0 has linear part the row-1 sum,
// which the acting Lambda contains, with its own constant; the other forms are random dense.
// Three-row version (m = 3, two acting row sums) of row_freeness.cpp; tor1ByDegree lists d = 1..dmax
// in the indexing of degeneration_tor.m2. Original description follows.
// Row freeness of gr F^Q (fall-line review): the hypothesis of thm:global-closure-gluing, for Q = the
// intersection of the members' allowed sets inside the weak base P. With m = 2 rows, Lambda =
// F_3[r]/(r^3) acts by the row sum r of row 1, and Tor_1^Lambda(F_3, M)_d = (ker r on M_d) / r^2 M_{d-2}
// for M = gr F^Q = R / gr I(Q) (R: column-injective monomials; x^2 and column collisions vanish).
// Prints tor1ByDegree (d = 0..dmax-1) and hilbQ (dim M_d); M = 0 gives Q = P, the base control.
// Member construction and modes are those of span_dependence.cpp.
// Span-dependence test of conj:shared-piece-falls (modes added to core_plus_fill):
//   spandep      member b >= 1 has forms 0 and 1 with linear parts f1 + f2 and f1 + 2 f2, where f1, f2
//                are the linear parts of member b-1's forms 1 and 2 (dependence beyond sharing), own
//                constants, uniformly random prefixes;
//   spandepzero  the same, with member b >= 1's prefix columns 2..h-1 forced to zero and c_1 = -c_0,
//                so that it has a shared piece (the pattern (1,1) on its two dependent forms).
// The flag counts members with a shared piece relative to T = {0, 1} (forms in the partner's span).
// Core-plus-fill test (flat-difference follow-up), modes added to dependent_fall_degree:
//   pairkeep   members 0 and 1 share the linear parts of forms 0 and 1, with their own constants,
//              and every prefix row of theirs has c_1 = -c_0, so the pattern (1,1,0,...,0) stays in
//              ker C (the flat-difference core); members 2..M-1 are independent random dense members;
//   pairmerged the same family with members 0 and 1 merged into one member (the ideal of P_0 cap P_1),
//              so M-1 members; the tested statement is that the remaining cross falls come at the
//              counting-forced degree.
// Dependent-family version (fill-point-falls follow-up): mode chooses how members' forms depend:
//   random     independent uniform dense forms (as in base_fall_degree);
//   sunflower  every member's form 0 has one common linear part, with its own random constant;
//   chain      member b's form 0 has the linear part of member b-1's form 1, with its own constant;
//   shared2    every member's forms 0 and 1 have two common linear parts, with their own constants;
//   points2    as shared2, with prefix row 0 forced to (1, 2, 0, ..., 0), so that each member
//              excludes the points where both shared forms vanish (a codimension-2 flat of the
//              shared span, different for different constants);
//   span:S     every form is a random combination of S fixed random dense linear forms, plus a
//              random constant (joint span of dimension at most S).
// Tested statement (conj:fill-point-falls extended to dependent families): every cross-member fall
// in degree d has hSum(d) >= |cap P_b| / 2.
#include <flint/nmod_mat.h>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <random>
#include <algorithm>
#include <string>
#include <unordered_map>
#include <iterator>
using namespace std;
typedef vector<int> VI;
int N, h, t, M, dmax, mrows, Ncol; unsigned seed; int pieceMembers = 0;
vector<unsigned> mons;           // squarefree monomials as bitmasks, sorted by degree
vector<int> degStart;            // degStart[d] = first index of degree d
static int popc(unsigned x){ return __builtin_popcount(x); }
nmod_mat_t* evalMat(const vector<unsigned>& pts, int d) {   // rows: points, cols: monomials deg <= d
    int cols = degStart[d+1];
    nmod_mat_t* A = new nmod_mat_t[1];
    nmod_mat_init(*A, pts.size(), cols, 3);
    for (size_t r = 0; r < pts.size(); r++)
        for (int c = 0; c < cols; c++)
            nmod_mat_entry(*A, r, c) = ((mons[c] & pts[r]) == mons[c]) ? 1 : 0;
    return A;
}
long rankOn(const vector<unsigned>& pts, int d) {
    if (d < 0) return 0;
    nmod_mat_t* A = evalMat(pts, d);
    long r = nmod_mat_rank(*A);
    nmod_mat_clear(*A); delete[] A; return r;
}
// append the degree-d parts of ker(E_{<=d} on pts) as rows of `acc` (vector of rows)
void topParts(const vector<unsigned>& pts, int d, vector<VI>& acc) {
    nmod_mat_t* A = evalMat(pts, d);
    int cols = degStart[d+1];
    nmod_mat_t X; nmod_mat_init(X, cols, cols, 3);
    long k = nmod_mat_nullspace(X, *A);
    for (long j = 0; j < k; j++) {
        VI v(degStart[d+1] - degStart[d]);
        bool nz = false;
        for (int c = degStart[d]; c < degStart[d+1]; c++) { v[c - degStart[d]] = nmod_mat_entry(X, c, j); if (v[c-degStart[d]]) nz = true; }
        if (nz) acc.push_back(v);
    }
    nmod_mat_clear(X); nmod_mat_clear(*A); delete[] A;
}
long rankRows(const vector<VI>& rows, int width) {
    if (rows.empty()) return 0;
    nmod_mat_t B; nmod_mat_init(B, rows.size(), width, 3);
    for (size_t r = 0; r < rows.size(); r++) for (int c = 0; c < width; c++) nmod_mat_entry(B, r, c) = rows[r][c];
    long rk = nmod_mat_rank(B); nmod_mat_clear(B); return rk;
}
long binom(int n, int k){ long r=1; for(int i=1;i<=k;i++) r = r*(n-k+i)/i; return r; }
int main(int argc, char** argv) {
    if (argc < 8) { fprintf(stderr, "usage\n"); return 2; }
    mrows = atoi(argv[1]); Ncol = atoi(argv[2]); h = atoi(argv[3]); t = atoi(argv[4]); M = atoi(argv[5]); dmax = atoi(argv[6]); seed = atoi(argv[7]);
    N = mrows * Ncol;
    if (argc < 9) { fprintf(stderr, "mode required\n"); return 2; }
    std::string mode = argv[8]; int S = 0;
    // suffix "+nf": reduce every form to its normal form modulo the row equations (no column-0 terms),
    // as conj:relative-row-freeness assumes
    bool normalForm = false;
    if (mode.size() > 3 && mode.compare(mode.size() - 3, 3, "+nf") == 0) { normalForm = true; mode = mode.substr(0, mode.size() - 3); }
    if (mode.rfind("span:", 0) == 0) S = atoi(mode.c_str() + 5);
    else if (mode != "random" && mode != "sunflower" && mode != "chain" && mode != "shared2" && mode != "points2" && mode != "pairkeep" && mode != "pairmerged" && mode != "spandep" && mode != "spandepzero" && mode != "rowform") { fprintf(stderr, "bad mode\n"); return 2; }
    bool flagOnly = argc > 9 && std::string(argv[9]) == "flag";   // print the shared-piece count only
    FILE* dump = (argc > 9 && !flagOnly) ? fopen(argv[9], "w") : nullptr;
    // column-injective assignments: each column empty or one of mrows cells
    vector<unsigned> colInj;
    { long total = 1; for (int c = 0; c < Ncol; c++) total *= (mrows + 1);
      for (long code = 0; code < total; code++) { long r = code; unsigned mask = 0;
        for (int c = 0; c < Ncol; c++) { int v = r % (mrows + 1); r /= (mrows + 1); if (v) mask |= 1u << ((v-1)*Ncol + c); }
        colInj.push_back(mask); } }
    vector<unsigned> base; for (unsigned x : colInj) if (popc(x) % 3 == mrows % 3) base.push_back(x);
    for (int d = 0; d <= Ncol; d++) { degStart.push_back(mons.size()); for (unsigned x : colInj) if (popc(x)==d && d <= dmax) mons.push_back(x); }
    degStart.push_back(mons.size());
    if (dmax > Ncol) dmax = Ncol;
    mt19937 rng(seed); uniform_int_distribution<int> u3(0,2);
    vector<vector<unsigned>> P(M); vector<char> inAll(base.size(), 1);
    // shared structure from a separate stream, so mode random reproduces base_fall_degree exactly
    mt19937 rng2(seed + 1000003u);
    VI common(N); for (auto& a: common) a = u3(rng2);                // sunflower's shared linear part
    vector<VI> spanBasis(S, VI(N)); for (auto& row: spanBasis) for (auto& a: row) a = u3(rng2);
    mt19937 rng3(seed + 2000003u);                                   // own stream, so earlier modes reproduce
    VI common1(N); for (auto& a: common1) a = u3(rng3);              // shared2's second linear part
    VI prevForm1(N), prevF1(N), prevF2(N);                                                  // chain: previous member's form 1
    for (int b = 0; b < M; b++) {
        vector<VI> A(h, VI(N+1)); for (auto& row: A) for (auto& a: row) a = u3(rng);
        if (mode == "sunflower" || mode == "shared2" || mode == "points2") for (int j = 0; j < N; j++) A[0][j] = common[j];
        if ((mode == "shared2" || mode == "points2") && h > 1) for (int j = 0; j < N; j++) A[1][j] = common1[j];
        bool pair = (mode == "pairkeep" || mode == "pairmerged") && b < 2 && h > 1;
        if (pair) for (int j = 0; j < N; j++) { A[0][j] = common[j]; A[1][j] = common1[j]; }
        if (mode == "rowform") for (int j = 0; j < N; j++) A[0][j] = (j < Ncol) ? 1 : 0;   // form 0 = row-1 sum + constant
        bool dep = (mode == "spandep" || mode == "spandepzero") && b > 0 && h > 2;
        if (dep) for (int j = 0; j < N; j++) { A[0][j] = (prevF1[j] + prevF2[j]) % 3; A[1][j] = (prevF1[j] + 2*prevF2[j]) % 3; }
        if (mode == "chain" && b > 0) for (int j = 0; j < N; j++) A[0][j] = prevForm1[j];
        if (S > 0) for (int i = 0; i < h; i++) { VI co(S); for (auto& c: co) c = u3(rng2);
            for (int j = 0; j < N; j++) { int v = 0; for (int k = 0; k < S; k++) v += co[k]*spanBasis[k][j]; A[i][j] = v % 3; } }
        if (h > 1) for (int j = 0; j < N; j++) prevForm1[j] = A[1][j];
        if (h > 2) for (int j = 0; j < N; j++) { prevF1[j] = A[1][j]; prevF2[j] = A[2][j]; }
        // reduction L -> L - sum_r a_{r,0} (r_r - 1): subtract each row's column-0 coefficient from that row and
        // add it to the constant, so L' = L modulo the row equations and L' has no column-0 terms
        if (normalForm) for (int i = 0; i < h; i++) for (int r = 0; r < mrows; r++) { int a = A[i][r*Ncol];
            for (int j = 0; j < Ncol; j++) A[i][r*Ncol + j] = (A[i][r*Ncol + j] + 3 - a) % 3;
            A[i][N] = (A[i][N] + a) % 3; }
        vector<VI> C(t, VI(h)); for (auto& row: C) for (auto& a: row) a = u3(rng);
        if (mode == "points2" && h > 1) { for (int i = 0; i < h; i++) C[0][i] = 0; C[0][0] = 1; C[0][1] = 2; }
        if (pair) for (auto& row: C) row[1] = (3 - row[0]) % 3;
        if (dep && mode == "spandepzero") for (auto& row: C) { row[1] = (3 - row[0]) % 3; for (int i = 2; i < h; i++) row[i] = 0; }
        // shared-piece test: for each partner, T = this member's forms whose linear parts that partner
        // shares; the member has a shared-span piece if for some nonempty subset T' of T the prefix
        // columns outside T' vanish and a nonzero 0/1 pattern on T' lies in ker C (then the excluded set
        // contains the preimage of a set of values of the shared forms alone)
        {   vector<VI> partnerSets;
            if (mode == "sunflower") partnerSets.push_back(VI{0});
            if (mode == "chain") { if (b > 0) partnerSets.push_back(VI{0}); if (b < M-1 && h > 1) partnerSets.push_back(VI{1}); }
            if ((mode == "shared2" || mode == "points2") && h > 1) partnerSets.push_back(VI{0,1});
            if (pair) partnerSets.push_back(VI{0,1});
            if (dep) partnerSets.push_back(VI{0,1});
            if (S > 0) { VI all; for (int i = 0; i < h; i++) all.push_back(i); partnerSets.push_back(all); }
            bool piece = false;
            for (auto& T : partnerSets) for (int sub = 1; sub < (1 << T.size()) && !piece; sub++) {
                vector<char> inT(h, 0); for (size_t k = 0; k < T.size(); k++) if (sub >> k & 1) inT[T[k]] = 1;
                bool zeroOut = true; for (auto& row: C) for (int i = 0; i < h; i++) if (!inT[i] && row[i] % 3) zeroOut = false;
                if (!zeroOut) continue;
                VI idx; for (int i = 0; i < h; i++) if (inT[i]) idx.push_back(i);
                for (int y = 1; y < (1 << idx.size()) && !piece; y++) { bool ker = true;
                    for (auto& row: C) { int v = 0; for (size_t k = 0; k < idx.size(); k++) if (y >> k & 1) v += row[idx[k]]; if (v % 3) ker = false; }
                    if (ker) piece = true; }
            }
            if (piece) pieceMembers++;
        }
        if (dump) { fprintf(dump, "block %d\n", b); for (auto& row: A){ for(int a: row) fprintf(dump,"%d ",a); fprintf(dump,"\n"); }
                    for (auto& row: C){ for(int a: row) fprintf(dump,"%d ",a); fprintf(dump,"\n"); } }
        for (size_t xi = 0; xi < base.size(); xi++) { unsigned x = base[xi];
            VI g(h); bool any=false;
            for (int i = 0; i < h; i++) { int L = A[i][N]; for (int j=0;j<N;j++) if (x>>j&1) L += A[i][j]; g[i] = (L%3==0); any |= g[i]; }
            bool ok = !any;
            for (int j = 0; j < t && !ok; j++) { int s=0; for (int i=0;i<h;i++) s += C[j][i]*g[i]; if (s%3) ok = true; }
            if (ok) P[b].push_back(x); else inAll[xi] = 0;
        }
    }
    if (dump) fclose(dump);
    if (flagOnly) { printf("mode=%s%s h=%d t=%d M=%d seed=%u pieceMembers=%d\n", mode.c_str(), normalForm ? "+nf" : "", h, t, M, seed, pieceMembers); return 0; }
    if (mode == "pairmerged" && M >= 2) {   // replace members 0, 1 by their intersection
        vector<unsigned> a0 = P[0], a1 = P[1], m01; sort(a0.begin(), a0.end()); sort(a1.begin(), a1.end());
        std::set_intersection(a0.begin(), a0.end(), a1.begin(), a1.end(), std::back_inserter(m01));
        P.erase(P.begin() + 1); P[0] = m01; M -= 1;
    }
    vector<unsigned> PI; for (size_t xi=0;xi<base.size();xi++) if (inAll[xi]) PI.push_back(base[xi]);
    char head[256]; snprintf(head, sizeof head, "mode=%s%s m=%d Ncol=%d h=%d t=%d M=%d seed=%u |base|=%zu |capP|=%zu density=%.4f", mode.c_str(), normalForm ? "+nf" : "",mrows,Ncol,h,t,M,seed,base.size(),PI.size(), PI.size()/double(base.size()));
    std::string line(head);  // one atomic line per run, so parallel runs do not interleave
    int k = mrows - 1;                       // acting row sums r_0..r_{k-1} (rows 0..m-2)
    std::unordered_map<unsigned,int> index; for (size_t c = 0; c < mons.size(); c++) index[mons[c]] = c;
    auto colsUsed = [&](unsigned S) { unsigned u = 0; for (int r = 0; r < mrows; r++) u |= (S >> (r*Ncol)) & ((1u<<Ncol)-1); return u; };
    auto applyR = [&](const VI& v, int d, int row) { VI w(degStart[d+2]-degStart[d+1], 0);
        for (int c = 0; c < (int)v.size(); c++) if (v[c]) { unsigned S = mons[degStart[d]+c]; unsigned u = colsUsed(S);
            for (int j = 0; j < Ncol; j++) if (!(u >> j & 1)) { int q = index[S | (1u << (row*Ncol + j))] - degStart[d+1]; w[q] = (w[q] + v[c]) % 3; } }
        return w; };
    auto W = [&](int d) { return (d < 0 || d > dmax) ? 0 : degStart[d+1]-degStart[d]; };
    vector<vector<VI>> K(dmax+1); vector<long> dimK(dmax+1);
    for (int d = 0; d <= dmax; d++) { vector<VI> acc; topParts(PI, d, acc); dimK[d] = rankRows(acc, W(d)); K[d] = acc; }
    line += " hilbQ=";
    for (int d = 0; d <= dmax; d++) { line += (d ? "," : ""); line += std::to_string(W(d) - dimK[d]); }
    // Tor_1^Lambda(F_3, M)_d, Lambda = F_3[r_1..r_k]/(r_i^3), M = R/K: cycles {(a_i) in M_{d-1}^k : sum r_i a_i = 0
    // in M_d} modulo Koszul boundaries r_j c e_i - r_i c e_j (c in M_{d-2}) and Frobenius r_i^2 c e_i (c in M_{d-3}).
    line += " tor1ByDegree=";
    for (int d = 1; d <= dmax; d++) {
        int wp = W(d-1), wd = W(d);
        vector<VI> st = K[d];
        for (int i = 0; i < k; i++) for (int c = 0; c < wp; c++) { VI e(wp, 0); e[c] = 1; st.push_back(applyR(e, d-1, i)); }
        long rankPhi = rankRows(st, wd) - dimK[d];
        long cycles = (long)k * (wp - dimK[d-1]) - rankPhi;
        vector<VI> bd;
        for (int i = 0; i < k; i++) for (auto& kv : K[d-1]) { VI v((size_t)k*wp, 0); for (int c = 0; c < wp; c++) v[(size_t)i*wp + c] = kv[c]; bd.push_back(v); }
        long baseK = rankRows(bd, k*wp);
        if (d >= 2) for (int c = 0; c < W(d-2); c++) { VI e(W(d-2), 0); e[c] = 1;
            vector<VI> img(k); for (int i = 0; i < k; i++) img[i] = applyR(e, d-2, i);
            for (int i = 0; i < k; i++) for (int j = i+1; j < k; j++) { VI v((size_t)k*wp, 0);
                for (int q = 0; q < wp; q++) { v[(size_t)i*wp + q] = img[j][q]; v[(size_t)j*wp + q] = (3 - img[i][q]) % 3; } bd.push_back(v); } }
        if (d >= 3) for (int c = 0; c < W(d-3); c++) { VI e(W(d-3), 0); e[c] = 1;
            for (int i = 0; i < k; i++) { VI a = applyR(applyR(e, d-3, i), d-2, i); VI v((size_t)k*wp, 0);
                for (int q = 0; q < wp; q++) v[(size_t)i*wp + q] = a[q]; bd.push_back(v); } }
        long bdDim = rankRows(bd, k*wp) - baseK;
        line += (d > 1 ? "," : ""); line += std::to_string(cycles - bdDim);
    }
    line += "\n";
    fputs(line.c_str(), stdout); fflush(stdout);
    return 0;
}
