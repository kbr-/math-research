/* Which subsets of F_3^3 are solution sets of pairwise coherent product systems (grid up-sets for some basis and
   coordinatewise orders), and which selector arrangements (complements of unions of affine planes, at most one
   plane per direction) have allowed sets that are not.  Points are indexed x = a + 3b + 9c.
   Output: counts of describable sets, and for the smallest number of planes giving a nonempty non-describable
   allowed set, the number of such arrangements and one example per allowed-set size.
   Usage: ./describable OUT.txt */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
static int dirs[13][3], nd = 0;
static int val(const int *d, int x) { int a = x % 3, b = (x / 3) % 3, c = x / 9; return (d[0]*a + d[1]*b + d[2]*c) % 3; }
int main(int argc, char **argv) {
    for (int a = 0; a < 3; a++) for (int b = 0; b < 3; b++) for (int c = 0; c < 3; c++) {
        if (!a && !b && !c) continue;                      /* projective points: first nonzero coordinate 1 */
        int f = a ? a : (b ? b : c); if (f != 1) continue;
        dirs[nd][0] = a; dirs[nd][1] = b; dirs[nd][2] = c; nd++;
    }
    /* up-sets of the grid {0,1,2}^3 in the product order, as 27-bit masks over grid points g = l0 + 3 l1 + 9 l2 */
    static uint32_t ups[1 << 12]; int nu = 0;
    for (uint32_t m = 0; m < (1u << 27); m++) {            /* enumerate via closure test: 134M, fast enough in C */
        int ok = 1;
        for (int g = 0; g < 27 && ok; g++) if (m >> g & 1) {
            int l0 = g % 3, l1 = (g / 3) % 3, l2 = g / 9;
            if (l0 < 2 && !(m >> (g + 1) & 1)) ok = 0;
            if (l1 < 2 && !(m >> (g + 3) & 1)) ok = 0;
            if (l2 < 2 && !(m >> (g + 9) & 1)) ok = 0;
        }
        if (ok) ups[nu++] = m;
    }
    uint8_t *desc = calloc(1u << 24, 1);                  /* bitset over 2^27 subsets */
    int perms[6][3] = {{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}}; long nb = 0;
    for (int i = 0; i < nd; i++) for (int j = i + 1; j < nd; j++) for (int k = j + 1; k < nd; k++) {
        /* independence: determinant nonzero mod 3 */
        int *u = dirs[i], *v = dirs[j], *w = dirs[k];
        int det = u[0]*(v[1]*w[2]-v[2]*w[1]) - u[1]*(v[0]*w[2]-v[2]*w[0]) + u[2]*(v[0]*w[1]-v[1]*w[0]);
        if (((det % 3) + 3) % 3 == 0) continue; nb++;
        for (int p0 = 0; p0 < 6; p0++) for (int p1 = 0; p1 < 6; p1++) for (int p2 = 0; p2 < 6; p2++) {
            int gidx[27];                                  /* point x -> grid index under this basis and orders */
            for (int x = 0; x < 27; x++)
                gidx[x] = perms[p0][val(u, x)] + 3 * perms[p1][val(v, x)] + 9 * perms[p2][val(w, x)];
            for (int q = 0; q < nu; q++) {
                uint32_t m = ups[q], s = 0;
                for (int x = 0; x < 27; x++) if (m >> gidx[x] & 1) s |= 1u << x;
                desc[s >> 3] |= 1 << (s & 7);
            }
        }
    }
    long ndesc = 0; for (uint32_t s = 1; s < (1u << 27); s++) if (desc[s >> 3] >> (s & 7) & 1) ndesc++;
    FILE *out = fopen(argv[1], "w");
    fprintf(out, "directions %d, bases %ld, grid up-sets %d, describable nonempty subsets %ld of %u\n", nd, nb, nu, ndesc, (1u << 27) - 1);
    /* selector arrangements: for each direction, no plane or the plane val = 0,1,2 (4 choices), 4^13 total */
    uint32_t planes[13][3];
    for (int d = 0; d < nd; d++) for (int c = 0; c < 3; c++) { planes[d][c] = 0; for (int x = 0; x < 27; x++) if (val(dirs[d], x) == c) planes[d][c] |= 1u << x; }
    long cnt[14] = {0}; long ex_by_size[28]; int best = 99; memset(ex_by_size, -1, sizeof ex_by_size);
    long total = 1; for (int d = 0; d < nd; d++) total *= 4;
    long nondesc_by_k[14] = {0};
    for (long code = 0; code < total; code++) {
        uint32_t forb = 0; long cc = code; int k = 0;
        for (int d = 0; d < nd; d++) { int c = cc % 4; cc /= 4; if (c) { forb |= planes[d][c - 1]; k++; } }
        uint32_t P = ~forb & ((1u << 27) - 1);
        if (!P) continue;
        if (!(desc[P >> 3] >> (P & 7) & 1)) { nondesc_by_k[k]++; if (k <= best) { best = k; int sz = __builtin_popcount(P); if (ex_by_size[sz] < 0) ex_by_size[sz] = code; } }
    }
    fprintf(out, "non-describable nonempty allowed sets by number of planes k:");
    for (int k = 0; k <= nd; k++) fprintf(out, " %d:%ld", k, nondesc_by_k[k]); fprintf(out, "\nsmallest k = %d; examples (allowed-set size: code, planes as direction(value)):\n", best);
    for (int sz = 0; sz < 28; sz++) if (ex_by_size[sz] >= 0) {
        long cc = ex_by_size[sz]; int k = 0; fprintf(out, "size %d: code %ld:", sz, ex_by_size[sz]);
        for (int d = 0; d < nd; d++) { int c = cc % 4; cc /= 4; if (c) { fprintf(out, " (%d%d%d)=%d", dirs[d][0], dirs[d][1], dirs[d][2], c - 1); k++; } }
        fprintf(out, "  [k=%d]\n", k);
    }
    fclose(out); return 0;
}
