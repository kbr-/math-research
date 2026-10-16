"""Exact parameters for the increment count and kernel-count tightness at l = 16.

Statements tested (finite arithmetic for the entry entry-2026-10-16-increment-count):

1. Sliding-window chain.  At l = 16, n = 2^16, m = n + 1, v = m*l, h = 3l, k = ceil(sqrt(m ln 4)),
   r_* = h(k+1)+1, d = v - r_*: a chain of W windows of r_* consecutive bits, each shifted by one,
   has increment count C_eff = 1 + (W-1)k/(d+k) and satisfies m ln(4 C_eff) <= k^2 for W = 19,
   while the published inventory condition m ln(4W) <= k^2 fails, and no shared subspace of
   dimension > h(k+1) lies in two windows (their intersection has dimension r_* - 1 = h(k+1) or less).
   Expected: the largest admissible W is printed and is at least 19; the published condition fails
   already at W = 2.
   Refuted by: a printed largest admissible W below 19, or the published condition holding at W = 19.
   Possible because: the margin m ln(4 C_eff) versus k^2 is small, so a mistaken k or d changes it.

2. Tightness.  With q0 = exp(-r_* k / (v - r_* - k)), a lower bound for the probability that a fixed
   set of at most k bits misses a uniform r_*-subset of the v bits, and M0 = floor(k ln(v+1)/q0) + 1,
   the first-moment bound H exp(-q0 M0) < 1 holds with H <= (v+1)^k.
   Expected: M0 printed (about 3e5), the exponent k ln(v+1) - q0 M0 negative, and ln M0 compared
   with the published admissible ln(4M) <= k^2/m.
   Refuted by: a nonnegative printed exponent k ln(v+1) - q0 M0 for the printed M0.
   Possible because: M0 is defined by a floor, and a wrong q0 or k would break the inequality.

3. Tightness at every admissible k'.  With K = n/4, G = 3l(n/4+2)+1 and
   q1 = ((v - G - K)/v)^K, a lower bound for the probability that a fixed set of at most K bits
   misses a uniform G-subset, M1 = floor(K ln(v+1)/q1) + 1 random coordinate blocks of rank G have,
   with positive probability, no common kernel in L_K, hence none in L_k' for any k' <= K.
   Computed in logarithms: ln M1 <= ln(K ln(v+1) + 1) - ln q1.  Expected: ln q1 about -23777,
   ln M1 about 23786, against the largest published admissible ln(4M) <= K^2/m, about 4096, and
   G > h(K+1), so every block is high-rank at every admissible k'.
   Refuted by: G <= h(K+1), or a printed ln M1 bound below K^2/m, which would leave no gap.
   Possible because: G, K and the probability bound depend on l and could be mis-specified.
"""
import argparse
import json
import math
from fractions import Fraction


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    ell = 16
    n = 2 ** ell
    m = n + 1
    v = m * ell
    h = 3 * ell
    k = math.isqrt(int(m * math.log(4))) + 1
    assert (k - 1) ** 2 < m * math.log(4) <= k * k, 'k is the ceiling of sqrt(m ln 4)'
    assert 4 * (k - 1) < n and k <= m
    r_star = h * (k + 1) + 1
    d = v - r_star
    ratio = Fraction(k, d + k)
    # Largest W with m ln(4 C_eff) <= k^2, C_eff = 1 + (W-1) k/(d+k).
    limit = math.exp(k * k / m) / 4
    w_max = 1 + math.floor((limit - 1) / float(ratio))
    def admissible(w):
        return m * math.log(4 * (1 + (w - 1) * float(ratio))) <= k * k
    assert admissible(w_max) and not admissible(w_max + 1)
    published_19 = m * math.log(4 * 19) <= k * k
    published_2 = m * math.log(4 * 2) <= k * k
    margin_19 = k * k - m * math.log(4 * (1 + 18 * float(ratio)))
    # Tightness.
    expo = r_star * k / (v - r_star - k)
    q0 = math.exp(-expo)
    m0 = math.floor(k * math.log(v + 1) / q0) + 1
    first_moment_exponent = k * math.log(v + 1) - q0 * m0
    result = dict(ell=ell, n=n, m=m, v=v, h=h, k=k, k_squared=k * k, m_ln4=m * math.log(4),
                  r_star=r_star, d=d, ratio=float(ratio), w_max=w_max, margin_at_19=margin_19,
                  published_condition_at_19=published_19, published_condition_at_2=published_2,
                  tightness_exponent=expo, q0=q0, M0=m0, ln_M0=math.log(m0),
                  first_moment_exponent=first_moment_exponent,
                  published_ln4M_bound=k * k / m)
    big_k = n // 4
    rank_g = 3 * ell * (n // 4 + 2) + 1
    assert rank_g > h * (big_k + 1) and rank_g + big_k < v and 4 * (big_k - 1) < n
    ln_q1 = big_k * math.log((v - rank_g - big_k) / v)
    ln_m1_bound = math.log(big_k * math.log(v + 1) + 1) - ln_q1
    result.update(K=big_k, G=rank_g, h_times_K_plus_1=h * (big_k + 1), v_minus_G_minus_K=v - rank_g - big_k,
                  ln_q1=ln_q1, ln_M1_upper=ln_m1_bound, published_max_ln4M=big_k * big_k / m,
                  gap_ratio=ln_m1_bound / (big_k * big_k / m))
    for key, value in result.items():
        print(f'{key} = {value}')
    with open(args.out, 'w') as handle:
        json.dump(result, handle, indent=1)
    assert w_max >= 19 and not published_19 and not published_2 and first_moment_exponent < 0
    assert ln_m1_bound > big_k * big_k / m
    print('PASS')


if __name__ == '__main__':
    main()
