/* Contact locus on random planes of configurations over F_p (1 October 2026; cycle bmd-20261001-d).
 *
 * Setting of lem:cube-contact-plane-criterion: R = binom(N,2), H_k(X,Y) = [T^k]((1+XT)(1+YT))^(-3/2),
 * A_L(a) = (H_k(a_i,a_j))_{i<j, k<=L}, an R x (L+1) matrix; the contact locus is K = {a separated :
 * rank A_(R+1)(a) < R}.  (K) says codim K >= 3, equivalently that a generic projective plane of
 * configurations modulo a -> t a + s 1 contains no separated point of K (part (2) of the lemma).
 *
 * For each of NPLANES random planes a = x alpha + y beta + z gamma over F_p, this counts the separated
 * F_p-points of the plane with rank A_(R+1) < R (contact R+4, the locus K) and, as a control, with
 * rank A_R < R (contact R+3, expected codimension two, so finitely many points on a plane, some of them
 * usually rational).  A hit for K at a random plane is evidence of a codimension-two component (or of a
 * reduction artefact at p); no hits is consistent with (K) but proves nothing.
 *
 * Coefficients by the recurrence (k+1) f_(k+1) = -(a+b)(k+3/2) f_k - ab(k+2) f_(k-1) for
 * f = ((1+aT)(1+bT))^(-3/2); ranks by FLINT nmod_mat_rank.  Self-tests: the recurrence against the
 * product of the two binomial series, and the symmetric configuration {+-1,+-2,+-5/3,+-7/2} at N = 8,
 * which lies in K (check:cube-symmetric-outside-eprime).
 *
 * Usage: bmd_cube_contact_plane_count N p nplanes seed OUT.  OpenMP over the points of a plane.
 */
#include <flint/flint.h>
#include <flint/nmod_vec.h>
#include <flint/nmod_mat.h>
#include <flint/ulong_extras.h>
#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static ulong P;
static nmod_t MOD;

static ulong inv(ulong x) { return n_invmod(x, P); }

/* fill rows: for each pair i<j, coefficients f_0..f_L of ((1+a_iT)(1+a_jT))^(-3/2) */
/* optional generic series F (F_0 = 1, other coefficients random): H_k = [T^k] F(a_iT) F(a_jT) */
static ulong *GEN = NULL;

static void fill(nmod_mat_t A, const ulong *a, int N, int L, const ulong *invk, ulong half3) {
  int row = 0;
  if (GEN) {
    ulong x[512], y[512];
    for (int i = 0; i < N; i++)
      for (int j = i + 1; j < N; j++) {
        ulong pi = 1, pj = 1;
        for (int r = 0; r <= L; r++) {
          x[r] = nmod_mul(GEN[r], pi, MOD); y[r] = nmod_mul(GEN[r], pj, MOD);
          pi = nmod_mul(pi, a[i], MOD); pj = nmod_mul(pj, a[j], MOD);
        }
        for (int k = 0; k <= L; k++) {
          ulong s = 0;
          for (int r = 0; r <= k; r++) s = nmod_add(s, nmod_mul(x[r], y[k - r], MOD), MOD);
          nmod_mat_entry(A, row, k) = s;
        }
        row++;
      }
    return;
  }
  for (int i = 0; i < N; i++)
    for (int j = i + 1; j < N; j++) {
      ulong s = nmod_add(a[i], a[j], MOD), pr = nmod_mul(a[i], a[j], MOD);
      ulong fm1 = 0, f = 1;
      nmod_mat_entry(A, row, 0) = 1;
      for (int k = 0; k < L; k++) {
        /* f_(k+1) = -[s (k + 3/2) f_k + pr (k+2) f_(k-1)] / (k+1) */
        ulong c1 = nmod_add(k % P, half3, MOD);
        ulong t = nmod_add(nmod_mul(nmod_mul(s, c1, MOD), f, MOD),
                           nmod_mul(nmod_mul(pr, (ulong)(k + 2) % P, MOD), fm1, MOD), MOD);
        ulong fn = nmod_neg(nmod_mul(t, invk[k + 1], MOD), MOD);
        fm1 = f; f = fn;
        nmod_mat_entry(A, row, k + 1) = f;
      }
      row++;
    }
}

static int separated(const ulong *a, int N) {
  for (int i = 0; i < N; i++)
    for (int j = i + 1; j < N; j++)
      if (a[i] == a[j]) return 0;
  return 1;
}

int main(int argc, char **argv) {
  if (argc < 6) { fprintf(stderr, "usage: N p nplanes seed OUT\n"); return 1; }
  int N = atoi(argv[1]); P = strtoul(argv[2], 0, 10); int nplanes = atoi(argv[3]);
  ulong seed = strtoul(argv[4], 0, 10); const char *outp = argv[5];
  nmod_init(&MOD, P);
  int R = N * (N - 1) / 2, L = R + 1;
  if (P <= (ulong)(L + 2)) { fprintf(stderr, "p too small\n"); return 1; }
  ulong *invk = malloc((L + 2) * sizeof(ulong));
  for (int k = 1; k <= L + 1; k++) invk[k] = inv(k);
  ulong half3 = nmod_mul(3, inv(2), MOD);
  FILE *out = fopen(outp, "a");
  if (argc >= 7) { /* generic series mode: F_0 = 1, F_r uniform random modulo p (seeded by argv[6]) */
    if (L + 1 > 512) { fprintf(stderr, "L too large\n"); return 1; }
    flint_rand_t sg; flint_randinit(sg); ulong s2 = strtoul(argv[6], 0, 10); flint_randseed(sg, s2, s2 ^ 0x5bd1e995UL);
    GEN = malloc((L + 1) * sizeof(ulong)); GEN[0] = 1;
    for (int r = 1; r <= L; r++) GEN[r] = n_randint(sg, P);
    flint_randclear(sg);
    fprintf(out, "N=%d p=%lu: generic series mode, F_r random (seed %lu), H_k = [T^k]F(a_iT)F(a_jT)\n", N, P, s2);
  }
  /* self-test 1: recurrence against the product of the binomial series b_r = binom(-3/2, r) */
  if (!GEN) {
    ulong a2[2] = {5, 11};
    nmod_mat_t A; nmod_mat_init(A, 1, L + 1, P);
    fill(A, a2, 2, L, invk, half3);
    ulong *b = malloc((L + 1) * sizeof(ulong)); b[0] = 1;
    for (int r = 1; r <= L; r++) { /* b_r = b_(r-1) * (-3/2 - r + 1) / r */
      ulong num = nmod_sub(nmod_neg(half3, MOD), (ulong)(r - 1) % P, MOD);
      b[r] = nmod_mul(nmod_mul(b[r - 1], num, MOD), invk[r], MOD);
    }
    int ok = 1;
    for (int k = 0; k <= L; k++) {
      ulong s = 0, pa = 1;
      for (int r = 0; r <= k; r++) {
        ulong pb = n_powmod2(11, k - r, P);
        s = nmod_add(s, nmod_mul(nmod_mul(b[r], pa, MOD), nmod_mul(b[k - r], pb, MOD), MOD), MOD);
        pa = nmod_mul(pa, 5, MOD);
      }
      if (s != nmod_mat_entry(A, 0, k)) ok = 0;
    }
    fprintf(out, "N=%d p=%lu: self-test recurrence %s\n", N, P, ok ? "passed" : "FAILED");
    nmod_mat_clear(A); free(b);
    if (!ok) { fclose(out); return 2; }
  }
  /* self-test 2: symmetric configuration at N = 8 lies in K */
  if (N == 8) {
    ulong c[8]; long nums[4] = {1, 2, 5, 7}; long dens[4] = {1, 1, 3, 2};
    for (int m = 0; m < 4; m++) { ulong v = nmod_mul(nums[m], inv(dens[m]), MOD); c[2 * m] = v; c[2 * m + 1] = nmod_neg(v, MOD); }
    nmod_mat_t A; nmod_mat_init(A, R, L + 1, P); fill(A, c, N, L, invk, half3);
    slong rk = nmod_mat_rank(A);
    fprintf(out, "N=8 p=%lu: symmetric control {+-1,+-2,+-5/3,+-7/2}: rank A_(R+1) = %ld (R = %d), %s\n", P, (long)rk, R, rk < R ? "in K as recorded" : "NOT in K: FAILED");
    nmod_mat_clear(A);
  }
  flint_rand_t st; flint_randinit(st); flint_randseed(st, seed, seed ^ 0x9e3779b9UL);
  for (int pl = 0; pl < nplanes; pl++) {
    ulong *al = malloc(3 * N * sizeof(ulong));
    for (int i = 0; i < 3 * N; i++) al[i] = n_randint(st, P);
    long npts = (long)P * P + P + 1;
    long nsep = 0, hitK = 0, hitC = 0;
    char *hitlist = malloc(1 << 16); hitlist[0] = 0; size_t hl = 0;
#pragma omp parallel reduction(+ : nsep, hitK, hitC)
    {
      nmod_mat_t A, B; nmod_mat_init(A, R, L + 1, P); nmod_mat_init(B, R, L, P);
      ulong *a = malloc(N * sizeof(ulong));
#pragma omp for schedule(dynamic, 256)
      for (long t = 0; t < npts; t++) {
        ulong x, y, z;
        if (t < (long)P * P) { x = 1; y = t / P; z = t % P; }
        else if (t < (long)P * P + (long)P) { x = 0; y = 1; z = t - (long)P * P; }
        else { x = 0; y = 0; z = 1; }
        for (int i = 0; i < N; i++)
          a[i] = nmod_add(nmod_add(nmod_mul(x, al[i], MOD), nmod_mul(y, al[N + i], MOD), MOD), nmod_mul(z, al[2 * N + i], MOD), MOD);
        if (!separated(a, N)) continue;
        nsep++;
        fill(A, a, N, L, invk, half3);
        for (int r = 0; r < R; r++) for (int k = 0; k < L; k++) nmod_mat_entry(B, r, k) = nmod_mat_entry(A, r, k);
        if (nmod_mat_rank(B) < R) {
          hitC++;
          fill(A, a, N, L, invk, half3);
          if (nmod_mat_rank(A) < R) {
            hitK++;
#pragma omp critical
            { if (hl < 60000) hl += snprintf(hitlist + hl, 65536 - hl, " [%lu:%lu:%lu]", x, y, z); }
          }
        }
      }
      nmod_mat_clear(A); nmod_mat_clear(B); free(a);
    }
    fprintf(out, "N=%d p=%lu plane %d: separated points %ld; rank A_R < R (control, contact R+3): %ld; rank A_(R+1) < R (K): %ld%s%s\n",
            N, P, pl, nsep, hitC, hitK, hitK ? "; K points" : "", hitlist);
    fflush(out);
    free(al); free(hitlist);
  }
  fclose(out);
  free(invk);
  flint_randclear(st);
  return 0;
}
