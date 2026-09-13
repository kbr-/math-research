# Actual mixed coefficients in the affine MP-A identity

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-13-source-MP-mixed-coefficients)
contains the full extraction proof, degree ledger, and remaining source
obligation. This refines the existing MP prefix, identity, and composition
results. It does not establish a new PHP lower bound.

For conclusion block B with inputs g_i, and implication block U with
inputs f_0=a, f_i=g_i, the actual identity is

    b = c + q*a + R,
    q = b*U_0,
    R = sum_i U_i*E_(B,i) + sum_i V_i*E_(U,i)   over F2.

The diagonal prefix coefficients are delta_(i,j)*f_j^(h-1) and
delta_(i,k)*g_k^(h-1). Consequently the joint U_j/B_k coefficient of both
R and q*a is a^h*g_k^h when j=0, and zero otherwise. The two product
targets have zero joint coefficient.

The local correction's extracted arrays Boolean-reduce to affine inputs,
but at j=0 their reduced pair relation is a*g_k. The antecedent term is
essential to the identity. The local correction alone is not an old-target
certificate to which the first-band pair theorem can be applied.

## Degree and scope

For nonzero affine inputs, deg(q)=4h-1 and the local MP-A identity fits
degree 4h. Inserting a supplied antecedent NS certificate of degree d_a
multiplies its nonzero terms to degree 4h-1+d_a, before collection with
other source contributions. This is not a lower bound on the best NS
certificate or on all collected source cofactors.

The explicit old certificate a=(a+z*w)+z*w has degree two. Each displayed
term after multiplication by q has degree 4h+1, although their sum q*a
has degree 4h. PC final-line reuse has the separate ceiling max(d_a,4h).

A distinct one-input block C on z gives a prospective term q*E_C of
degree 6h, with three-block coefficient

    a^(h-1) * g_k^h * z^(h+1).

This demonstrates possible complete support after antecedent multiplication.
It is not asserted to occur essentially in a completed PHP source proof;
its survival after cofactor collection needs a source-specific argument.

## Exact output

`mixed-MP-checks.jsonl` contains five cases:

- Coordinate inputs at h=1,2,3: a=x_0, g_0=x_1, g_1=x_2.
- Affine-offset inputs at h=1,2: a=x_0+x_3,
  g_0=1+x_1+x_3, g_1=x_2+x_4.

The old variables are x_0,...,x_4; z=x_3 and w=x_4 in the ledger controls.
The program uses zero-based g indices, corresponding to g_1,g_2 in the
notebook's displayed MP tuple. B coefficients begin at variable five,
with h rows of arity two; U coefficients follow with h rows of arity three.
The one-input C block follows U in the triple-support control.

Each case verifies 60 diagonal equations and two nonzero omitted-antecedent
coefficients, for totals of 300 and ten. It also checks the complete ordinary
MP identity, the old antecedent certificate, its multiplied terms, and the
nonzero three-block coefficient. The degree triples are:

| h | Local correction | Displayed degree-two antecedent terms | Third-companion term |
| ---: | ---: | ---: | ---: |
| 1 | 4 | 5 | 6 |
| 2 | 8 | 9 | 12 |
| 3 | 12 | 13 | 18 |

The output preserves the full ordinary polynomials for inputs, products,
prefixes, companions, q, R, every extracted array and mixed coefficient,
both old premise axioms, both multiplied premise terms, and the third-block
control. No significant polynomial exists only in the terminal output.

A term is encoded as `[coefficient, [[variable, exponent], ...]]`.
All arithmetic is exact over F2; exponents are ordinary nonnegative
integers, not Boolean masks. The zero polynomial has degree -1.
Diagonal extraction Boolean-reduces only the selected fresh coordinates
and sets other fresh coordinates to zero. Old Boolean reduction is applied
separately for the stated affine-array checks. Original companion and
cofactor degrees are retained throughout.

## Reproduction

From the repository root, use a fresh output path:

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  research/tools/check_mp_composition.cpp -o /tmp/check_mp_composition
./compute.sh run TURN --threads 1 -- \
  /tmp/check_mp_composition --out NEW_MIXED_MP.jsonl --mixed-affine
~~~

The new optional mode reuses the existing sparse ordinary-polynomial
implementation. The historical broad MP suite was not rerun. Compilation
and the targeted exact run passed within the shared resource boundary;
no dependencies were installed. These are local checks, not full source
certificates, PHP refutations, or minimum-degree calculations.

`provenance.json` pins the source, output, this record, and the historical
coefficient-operator source. `timing.html` and the archived session retain
actual phase timing, commands, and complete run output.

The remaining obligation is to control the collected premise/path
contributions at the actual source degree, with sharing and scope explicit,
or construct the necessary higher mixed components. A local prefix bound
does not establish a first-band bound for the completed source certificate.
