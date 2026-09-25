/* Private-tetrahedra check for the tetrahedral design theorem (thread odd-prime-reslin-php).

   Statement tested (the design lemma): on the pattern algebra P(R,L) of the functional board with R = n+1 rows,
   N = n labels, L = N-1, rows {1..4} x [N0] (N0 = floor(R/4)), blocks Q_{x,a} = {(i, x+(i-1)a)} for a in A,
   0 <= x <= N0-1-3a, and on each block the tetrahedra S = {((i, x+(i-1)a), 4+alpha+(i-1)beta)} for beta in B,
   0 <= alpha <= N-6-3beta: if A and B have no pairwise-distinct solutions of x+y=2z or x+2y=3z and
   max B < 1.5 min B, then
     (i)  every cell pair of every tetrahedron lies in no other tetrahedron, and
     (ii) for every tetrahedron S and every cell u not in S there are a,b in S with {a,b,u} a standard 3-face
          of P and neither {a,u} nor {b,u} inside any tetrahedron.
   The program asserts the hypotheses on A and B, builds the family, and counts violations of (i) and (ii),
   which the lemma predicts to be 0.  It also prints M against the capacity gamma_3/(gamma_1-1).

   Modes: "digits" uses the sets of the proof (base-4 {0,1}-digit sets: A = D cap [0, N0/6),
   B = b + (D cap [0, b/2)), b = floor((N-6)/9)); "greedy" uses greedy admissible sets
   (A greedy in [0, (N0-1)/3]; B greedy in [b, 1.5b) with the b maximizing the tetrahedron count).
   Usage: tetra_check n1 n2 ...   (both modes for each n; one pass over the list). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <omp.h>

static int admissible_add(const int *S, int k, int v) {
    /* would S u {v} contain pairwise-distinct x,y,z with x+y=2z or x+2y=3z ? (checks triples containing v) */
    int T[4096]; memcpy(T, S, k * sizeof(int)); T[k] = v; int m = k + 1;
    for (int i = 0; i < m; i++) for (int j = 0; j < m; j++) for (int l = 0; l < m; l++) {
        if (i == j || j == l || i == l) continue;
        if (T[i] != v && T[j] != v && T[l] != v) continue;
        int x = T[i], y = T[j], z = T[l];
        if (x + y == 2 * z || x + 2 * y == 3 * z) return 0;
    }
    return 1;
}
static int admissible(const int *S, int k) {
    for (int i = 0; i < k; i++) for (int j = 0; j < k; j++) for (int l = 0; l < k; l++) {
        if (i == j || j == l || i == l) continue;
        int x = S[i], y = S[j], z = S[l];
        if (x + y == 2 * z || x + 2 * y == 3 * z) return 0;
    }
    return 1;
}
static int digits_set(int X, int *out) {           /* base-4 numbers with digits 0/1, below X */
    int k = 0;
    for (int v = 0; v < X; v++) { int w = v, ok = 1; while (w) { if (w % 4 > 1) { ok = 0; break; } w /= 4; } if (ok) out[k++] = v; }
    return k;
}
static int L_, R_;
static inline int face_ok(int c1, int c2, int c3) { /* cells as r*L+c; standard 3-face of P ? */
    int r[3] = {c1 / L_, c2 / L_, c3 / L_}, f[3] = {c1 % L_, c2 % L_, c3 % L_};
    if (r[0] == r[1] || r[1] == r[2] || r[0] == r[2]) return 0;
    if (f[0] == f[1] || f[1] == f[2] || f[0] == f[2]) return 0;
    for (int i = 0; i < 2; i++) for (int j = 0; j < 2 - i; j++) if (r[j] > r[j + 1]) {
        int t = r[j]; r[j] = r[j + 1]; r[j + 1] = t; t = f[j]; f[j] = f[j + 1]; f[j + 1] = t; }
    for (int i = 0; i < 3; i++) for (int j = i + 1; j < 3; j++) if (f[i] == 0 && f[j] == 1) return 0;
    static const int pat[4][3] = {{0,2,3},{1,0,2},{1,2,0},{1,2,3}};
    for (int p = 0; p < 4; p++) if (f[0] == pat[p][0] && f[1] == pat[p][1] && f[2] == pat[p][2]) return 0;
    return 1;
}
static long count_tetra(int N, int N0, const int *A, int kA, const int *B, int kB) {
    long bl = 0, cw = 0;
    for (int i = 0; i < kA; i++) if (N0 - 3 * A[i] > 0) bl += N0 - 3 * A[i];
    for (int i = 0; i < kB; i++) if (N - 5 - 3 * B[i] > 0) cw += N - 5 - 3 * B[i];
    return bl * cw;
}
static void run(int n, int greedy) {
    int R = n + 1, N = n, L = N - 1, N0 = R / 4; L_ = L; R_ = R;
    int A[4096], B[4096], kA = 0, kB = 0;
    if (!greedy) {
        kA = digits_set((N0 + 5) / 6, A);               /* a < N0/6 */
        int b = (N - 6) / 9, D[4096];
        if (b >= 1) { int kd = digits_set((b + 1) / 2, D); for (int i = 0; i < kd; i++) B[kB++] = b + D[i]; }
    } else {
        for (int a = 0; 3 * a <= N0 - 1; a++) if (admissible_add(A, kA, a)) A[kA++] = a;
        long best = -1; int bestb = 0;
        for (int b = 1; 4 + 3 * b <= N - 2; b++) {
            int T[4096], k = 0;
            for (int v = b; 2 * v < 3 * b; v++) if (4 + 3 * v <= N - 2 && admissible_add(T, k, v)) T[k++] = v;
            long c = count_tetra(N, N0, A, kA, T, k);
            if (c > best) { best = c; bestb = b; memcpy(B, T, k * sizeof(int)); kB = k; }
        }
        (void)bestb;
    }
    /* hypotheses */
    if (!admissible(A, kA) || !admissible(B, kB)) { printf("n=%d: set not admissible\n", n); exit(1); }
    for (int i = 0; i < kB; i++) if (2 * B[i] >= 3 * B[0]) { printf("n=%d: ratio condition fails\n", n); exit(1); }
    long M = count_tetra(N, N0, A, kA, B, kB);
    int g1 = R * L;
    double T3 = (double)L * (L - 1) * (L - 2) - 3.0 * (L - 2) - 4.0;
    double g3 = (double)R * (R - 1) * (R - 2) / 6.0 * T3, cap = g3 / (g1 - 1);
    if (M == 0) { printf("{\"n\":%d,\"mode\":\"%s\",\"M\":0,\"capacity\":%.1f}\n", n, greedy ? "greedy" : "digits", cap); fflush(stdout); return; }
    int *S = malloc(sizeof(int) * 4 * M); long m = 0;
    for (int ia = 0; ia < kA; ia++) { int a = A[ia];
        for (int x = 0; x + 3 * a <= N0 - 1; x++)
            for (int ib = 0; ib < kB; ib++) { int be = B[ib];
                for (int al = 0; al + 3 * be <= N - 6; al++) {
                    for (int i = 0; i < 4; i++) { int row = i * N0 + x + i * a, lab = 4 + al + i * be;
                        if (lab > L - 1 || row >= R) { printf("range error\n"); exit(1); }
                        S[4 * m + i] = row * L + lab; }
                    m++; } } }
    if (m != M) { printf("count mismatch\n"); exit(1); }
    uint8_t *pc = calloc((size_t)g1 * g1, 1);
    for (long j = 0; j < M; j++) for (int i = 0; i < 4; i++) for (int k = 0; k < 4; k++) if (i != k) {
        size_t id = (size_t)S[4 * j + i] * g1 + S[4 * j + k]; if (pc[id] < 255) pc[id]++; }
    long bad_i = 0, bad_ii = 0, bad_face = 0;
    #pragma omp parallel for schedule(dynamic, 64) reduction(+:bad_i,bad_ii,bad_face)
    for (long j = 0; j < M; j++) {
        const int *s = S + 4 * j;
        for (int i = 0; i < 4; i++) for (int k = i + 1; k < 4; k++) {
            if (pc[(size_t)s[i] * g1 + s[k]] != 1) bad_i++;
            for (int l = k + 1; l < 4; l++) if (!face_ok(s[i], s[k], s[l])) bad_face++; }
        for (int u = 0; u < g1; u++) {
            if (u == s[0] || u == s[1] || u == s[2] || u == s[3]) continue;
            int ok = 0;
            for (int i = 0; i < 4 && !ok; i++) for (int k = i + 1; k < 4 && !ok; k++)
                if (face_ok(s[i], s[k], u) && pc[(size_t)s[i] * g1 + u] == 0 && pc[(size_t)s[k] * g1 + u] == 0) ok = 1;
            if (!ok) bad_ii++;
        }
    }
    printf("{\"n\":%d,\"mode\":\"%s\",\"A\":[", n, greedy ? "greedy" : "digits");
    for (int i = 0; i < kA; i++) printf(i ? ",%d" : "%d", A[i]);
    printf("],\"B\":[");
    for (int i = 0; i < kB; i++) printf(i ? ",%d" : "%d", B[i]);
    printf("],\"M\":%ld,\"gamma1\":%d,\"gamma3\":%.0f,\"capacity\":%.1f,\"fraction\":%.4f,"
           "\"violations_i\":%ld,\"violations_ii\":%ld,\"nonface_internal\":%ld}\n",
           M, g1, g3, cap, M / cap, bad_i, bad_ii, bad_face);
    fflush(stdout);
    free(S); free(pc);
}
int main(int argc, char **argv) {
    for (int t = 1; t < argc; t++) { int n = atoi(argv[t]); run(n, 0); run(n, 1); }
    return 0;
}
