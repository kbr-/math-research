// Row rank profile over GF(3) with fflas-ffpack: for the rows in their given order, the list of rows that
// are independent of all earlier rows.  One factorization answers the rank of every prefix.
#include <fflas-ffpack/fflas-ffpack.h>
#include <givaro/modular.h>
extern "C" long gf3_row_rank_profile(long rows, long cols, float *A, long *profile) {
    typedef Givaro::Modular<float> F; F f(3);
    size_t *prof = nullptr;
    size_t r = FFPACK::RowRankProfile(f, rows, cols, A, cols, prof);
    for (size_t i = 0; i < r; i++) profile[i] = (long)prof[i];
    FFLAS::fflas_delete(prof);
    return (long)r;
}
