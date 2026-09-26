/* Rank of a dense integer matrix modulo a word-size prime p, by FLINT's nmod_mat_rank.
   Input file: int32 rows, cols, then rows*cols int8 entries (row-major); prime p on the command line. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <flint/nmod_mat.h>
int main(int argc, char **argv) {
    if (argc != 3) { fprintf(stderr, "usage: rank_large IN P\n"); return 2; }
    mp_limb_t p = strtoull(argv[2], NULL, 10);
    FILE *f = fopen(argv[1], "rb"); int32_t h[2];
    if (!f || fread(h, 4, 2, f) != 2) return 2;
    long R = h[0], C = h[1]; int8_t *buf = malloc((size_t) R * C);
    if (fread(buf, 1, (size_t) R * C, f) != (size_t) R * C) return 2;
    fclose(f);
    nmod_mat_t A; nmod_mat_init(A, R, C, p);
    for (long i = 0; i < R; i++) for (long j = 0; j < C; j++) {
        long v = buf[(size_t) i * C + j]; nmod_mat_entry(A, i, j) = (mp_limb_t) ((v % (long) p + (long) p) % (long) p); }
    printf("%ld\n", nmod_mat_rank(A));
    return 0;
}
