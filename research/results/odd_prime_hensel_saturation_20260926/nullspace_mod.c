/* Right nullspace of a dense matrix modulo a small prime p, by FLINT's nmod_mat_nullspace.
   Input file: int32 rows, cols, p, then rows*cols uint8 entries (row-major, already reduced mod p).
   Output file: int32 rows(=cols of input), nullity, then rows*nullity uint8 entries (row-major). */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <flint/nmod_mat.h>
int main(int argc, char **argv) {
    if (argc != 3) { fprintf(stderr, "usage: nullspace_mod IN OUT\n"); return 2; }
    FILE *f = fopen(argv[1], "rb"); int32_t h[3];
    if (!f || fread(h, 4, 3, f) != 3) return 2;
    long R = h[0], C = h[1]; mp_limb_t p = (mp_limb_t) h[2];
    uint8_t *buf = malloc((size_t) R * C);
    if (fread(buf, 1, (size_t) R * C, f) != (size_t) R * C) return 2;
    fclose(f);
    nmod_mat_t A, X; nmod_mat_init(A, R, C, p);
    for (long i = 0; i < R; i++) for (long j = 0; j < C; j++) nmod_mat_entry(A, i, j) = buf[(size_t) i * C + j];
    free(buf);
    nmod_mat_init(X, C, C, p);
    long nul = nmod_mat_nullspace(X, A);
    FILE *g = fopen(argv[2], "wb"); int32_t o[2] = {(int32_t) C, (int32_t) nul}; fwrite(o, 4, 2, g);
    for (long i = 0; i < C; i++) for (long j = 0; j < nul; j++) { uint8_t v = (uint8_t) nmod_mat_entry(X, i, j); fwrite(&v, 1, 1, g); }
    fclose(g); nmod_mat_clear(A); nmod_mat_clear(X);
    return 0;
}
