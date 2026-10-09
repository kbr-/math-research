/* Exact binary Hilbert function of one paired central modular row.
 *
 * Tested statement (conj:paired-row-symbols).  For a paired central row on h
 * pairs with pair weights a_1..a_h mod an odd prime q and least signed zero-sum
 * size w, the number g(s) of standard monomials of degree s over F_2 equals
 * binom(h,s) for every s >= h-w+3.  prop:straddling-flat-sharpness predicts
 * g(h-w+2) > binom(h,h-w+2).
 *
 * The allowed set is R = {(x_u, x_v) : sum_j a_j y_j = 0 mod q}, with
 * y_j = x_u + x_v - 1 (all signs eps_j = +1; a sign change is the coordinate
 * change x_v -> 1 - x_v, which preserves degrees).  g(s) is computed as the
 * rank increase of the evaluations on R of polynomials of degree <= s, by the
 * closure V_s = V_{s-1} + sum_i x_i * (new basis vectors of level s-1), with
 * bit-packed Gaussian elimination.  Weights are redrawn until they have
 * distinct classes {a,-a} and least zero-sum size exactly the requested w;
 * both are asserted by exhaustive enumeration of signed subsets.
 *
 * Usage: row_hilbert h q w seed   (one JSON line on stdout)
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int h, q;
static int a[32];

static uint64_t rng_state;
static uint64_t rng(void) {
    rng_state ^= rng_state << 13; rng_state ^= rng_state >> 7; rng_state ^= rng_state << 17;
    return rng_state;
}

/* least support of a nonzero y in {-1,0,1}^h with sum a_j y_j = 0 mod q, capped at h+1 */
static int best;
static void search(int idx, int used, int sum) {
    if (used >= best) return;
    if (used > 0 && sum % q == 0) { best = used; return; }
    if (idx == h) return;
    search(idx + 1, used + 1, (sum + a[idx]) % q);
    search(idx + 1, used + 1, (sum - a[idx] + q) % q);
    search(idx + 1, used, sum);
}
static int zero_sum_size(void) { best = h + 1; search(0, 0, 0); return best; }

int main(int argc, char **argv) {
    if (argc != 5) { fprintf(stderr, "usage: row_hilbert h q w seed\n"); return 2; }
    h = atoi(argv[1]); q = atoi(argv[2]);
    int want = atoi(argv[3]);
    rng_state = strtoull(argv[4], NULL, 10) * 0x9E3779B97F4A7C15ULL + 1;
    int k = 2 * h, tries = 0, w;
    for (;;) {
        tries++;
        if (tries > 2000000) { fprintf(stderr, "no weights found\n"); return 3; }
        int ok = 1;
        for (int j = 0; j < h; j++) a[j] = 1 + (int)(rng() % (uint64_t)(q - 1));
        for (int i = 0; i < h && ok; i++)
            for (int j = i + 1; j < h; j++)
                if (a[i] == a[j] || a[i] + a[j] == q) { ok = 0; break; }
        if (!ok) continue;
        w = zero_sum_size();
        if (w == want) break;
    }
    /* points: bit j = x_u of pair j, bit h+j = x_v of pair j; y_j = x_u + x_v - 1 */
    uint32_t total = 1u << k, np = 0, cap = 1u << 16;
    uint32_t *pts = malloc(cap * sizeof *pts);
    uint32_t npref = 0;
    for (uint32_t x = 0; x < total; x++) {
        long s = 0; int pref = 1;
        for (int j = 0; j < h; j++) {
            int y = (int)((x >> j) & 1) + (int)((x >> (h + j)) & 1) - 1;
            if (y) pref = 0;
            s += (long)a[j] * y;
        }
        s %= q; if (s < 0) s += q;
        if (s == 0) {
            if (np == cap) { cap *= 2; pts = realloc(pts, cap * sizeof *pts); }
            pts[np++] = x; npref += (uint32_t)pref;
        }
    }
    if (npref != (1u << h)) { fprintf(stderr, "preferred cube miscounted\n"); return 4; }
    int words = (int)((np + 63) / 64);
    uint64_t *mask = calloc((size_t)k * words, sizeof *mask);       /* x_i as a function on R */
    for (uint32_t p = 0; p < np; p++)
        for (int i = 0; i < k; i++)
            if ((pts[p] >> i) & 1) mask[(size_t)i * words + p / 64] |= 1ULL << (p % 64);
    uint64_t *basis = malloc((size_t)np * words * sizeof *basis);   /* row with lowest set bit p */
    char *has = calloc(np, 1);
    uint64_t *cur = malloc((size_t)np * words * sizeof *cur);       /* new vectors of the last level */
    uint64_t *nxt = malloc((size_t)np * words * sizeof *nxt);
    uint64_t *tmp = malloc((size_t)words * sizeof *tmp);
    long g[64]; memset(g, 0, sizeof g);
    /* level 0: the constant one */
    for (int t = 0; t < words; t++) cur[t] = ~0ULL;
    if (np % 64) cur[words - 1] = (1ULL << (np % 64)) - 1;
    memcpy(basis, cur, (size_t)words * sizeof *cur); has[0] = 1;   /* lowest set bit of all-ones is 0 */
    long ncur = 1, rank = 1; g[0] = 1;
    int top = 0;
    for (int s = 1; s <= k && rank < (long)np; s++) {
        long nn = 0;
        for (long c = 0; c < ncur; c++) {
            for (int i = 0; i < k; i++) {
                int nz = 0;
                for (int t = 0; t < words; t++) {
                    tmp[t] = cur[(size_t)c * words + t] & mask[(size_t)i * words + t];
                    nz |= tmp[t] != 0;
                }
                if (!nz) continue;
                for (int t = 0; t < words; t++) {
                    while (tmp[t]) {
                        int b = __builtin_ctzll(tmp[t]);
                        uint32_t p = (uint32_t)t * 64 + (uint32_t)b;
                        if (!has[p]) {
                            memcpy(basis + (size_t)p * words, tmp, (size_t)words * sizeof *tmp);
                            has[p] = 1;
                            memcpy(nxt + (size_t)nn * words, tmp, (size_t)words * sizeof *tmp);
                            nn++; rank++;
                            goto next_candidate;
                        }
                        const uint64_t *row = basis + (size_t)p * words;
                        for (int u = t; u < words; u++) tmp[u] ^= row[u];
                    }
                }
            next_candidate:;
            }
        }
        g[s] = nn; top = s;
        uint64_t *sw = cur; cur = nxt; nxt = sw; ncur = nn;
        if (nn == 0) break;
    }
    if (rank != (long)np) { fprintf(stderr, "closure did not reach all points\n"); return 5; }
    printf("{\"h\": %d, \"q\": %d, \"w\": %d, \"seed\": %s, \"tries\": %d, \"points\": %u, \"weights\": [",
           h, q, w, argv[4], tries, np);
    for (int j = 0; j < h; j++) printf("%s%d", j ? ", " : "", a[j]);
    printf("], \"g\": [");
    for (int s = 0; s <= top; s++) printf("%s%ld", s ? ", " : "", g[s]);
    printf("]}\n");
    return 0;
}
