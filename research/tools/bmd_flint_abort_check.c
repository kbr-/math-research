/* Does FLINT abort, rather than return silently, when the line certificate's exact-interpolation conditions fail
 * (29 September 2026; cycle bmd-20260929-zzb)?  Mode 1: nmod_inv(0).  Mode 2: nmod_poly_interpolate_nmod_vec_fast with
 * a repeated node.  Mode 3 (control): distinct nodes, must succeed.  Used modulus: p = 2^61 - 1, as in
 * bmd_cube_wronskian_discriminant.c.  Usage: bmd_flint_abort_check MODE; an abort shows as a nonzero exit status. */
#include <stdio.h>
#include <stdlib.h>
#include <flint/flint.h>
#include <flint/nmod_vec.h>
#include <flint/nmod_poly.h>

int main(int argc, char **argv) {
    int mode = argc > 1 ? atoi(argv[1]) : 3;
    mp_limb_t P = (UWORD(1) << 61) - 1;
    nmod_t MOD; nmod_init(&MOD, P);
    if (mode == 1) {
        mp_limb_t r = nmod_inv(0, MOD);
        printf("nmod_inv(0) returned %lu without aborting\n", r);
        return 0;
    }
    mp_limb_t x[4] = {1, 2, 3, 4}, y[4] = {5, 7, 11, 13};
    if (mode == 2) x[3] = 2;
    nmod_poly_t f; nmod_poly_init(f, P);
    nmod_poly_interpolate_nmod_vec_fast(f, x, y, 4);
    int ok = 1;
    for (int i = 0; i < 4; i++) if (nmod_poly_evaluate_nmod(f, x[i]) != y[i]) ok = 0;
    printf("mode %d: interpolation returned; reproduces the data: %s\n", mode, ok ? "yes" : "no");
    nmod_poly_clear(f);
    return 0;
}
