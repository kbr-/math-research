/* Rank over F_3 of sparse matrices read from stdin, using FLINT nmod_mat_rank.
   Input: repeated blocks "rows cols nnz" followed by nnz lines "i j v"; prints one rank per block. */
#include <stdio.h>
#include <flint/nmod_mat.h>
int main(void) {
    long r, c, nnz;
    while (scanf("%ld %ld %ld", &r, &c, &nnz) == 3) {
        nmod_mat_t M; nmod_mat_init(M, r > 0 ? r : 1, c > 0 ? c : 1, 3);
        for (long k = 0; k < nnz; k++) {
            long i, j, v; if (scanf("%ld %ld %ld", &i, &j, &v) != 3) return 1;
            nmod_mat_entry(M, i, j) = (nmod_mat_entry(M, i, j) + (ulong)((v % 3 + 3) % 3)) % 3;
        }
        printf("%ld\n", (r > 0 && c > 0) ? nmod_mat_rank(M) : 0L);
        fflush(stdout);
        nmod_mat_clear(M);
    }
    return 0;
}
