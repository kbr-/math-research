# Pure cyclic sums through binary field-product certificates

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-14-cyclic-sums-costed-pairs)
gives the working theorem, full degree ledger, and source application. It
removes the private heads from the preceding cyclic-tail example, for
lengths t=2^s-1. The argument uses binary coordinates throughout; extension
fields organize polynomial identities without changing ENS coefficient domains.

For polynomial inventory and polylogarithmic source degree, t=Theta(v) gives
old degree sqrt(n) times polylog(n). Arbitrary quadratic input spaces, other
cyclic factorizations, and later nonlinear levels are not thereby covered.

## Reproduce

From the repository root, with active resource controls and a timing session:

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_cyclic_field_source.cpp -o /tmp/math-cyclic-field-source
./compute.sh run TURN --threads 1 --timeout 180 -- \
  /tmp/math-cyclic-field-source --out NEW_OUTPUT_PATH
~~~

Output paths must be new. No dependencies were installed. Polynomial terms
are `[coefficient,[variable IDs with repetitions]]`, over F2. Matrix rows are
integer bitmasks with lower bits corresponding to lower input indices.
Large parameter integers are exact decimal strings.

## Exact evidence

`cyclic-field-source-checks.jsonl` retains 80 ordinary NS certificates:

- 30 pair certificates for every x_i*z_j in binary field dimensions
  one, two, three, and four, through degree d+2;
- one degree-five pulled-back cyclic kernel certificate;
- 49 complete weighted actual-source images, including every original
  companion, coefficient domain, and old Boolean equation.

For the local field products, the irreducible moduli have coefficient
bitmasks 3,7,11,19. Full multiplication tables and polynomial inverse
coordinates are retained. All nonzero residues pass the unit check.
The pair coefficients have degree at most d. The checker reconstructs
every ordinary witness and charges every generator multiple separately.

Twenty-six nonzero scalar combinations of product components have polar
rank 2d. For d>=2 this rules out expressing a coordinate pair as a constant
combination of the component equations. All 56 zero-product assignments
are saved. The F4 countermodel A=B=3 satisfies C0=0 but has C1=1 and
x0*z0=1, showing why an input component cannot simply be omitted.

The exact CRT cases t=3,7,15 use factor lists [3,7], [3,11,13], and
[3,7,19,25,31]. Their product is verified to be X^t-1. The two binary maps
for A(X^-1) and B(X) are invertible; forward and inverse matrices are saved.
Every quadratic product coordinate equals the recorded constant combination
of the actual cyclic inputs. Complete input and component polynomials are
retained; these are coefficient checks, not enumeration of 2^30 points.

The actual source has a0,a1,a2,b0,b1,b2 at old IDs 0..5 and an extra old
bit at ID 6. Nine reused rank-two bottoms and one three-input parent give
28 source variables in total. The multiplier is the extra bit times one
F4 diagonal coordinate pair. It is homogeneous cubic with row cap two
under the saved partition. Parent coefficients have degree at most three.

Its kernel identity has a nonzero Boolean correction E through degree
five. The parent product maps to 1-f+E, and the checker preserves that
correction. The 49 weighted source certificates have budgets at most ten,
each within its original 3e+3 ceiling. All sixteen nonzero-weight source
models are saved. At old point 9 an unweighted companion has value one
while the multiplier is zero. This is a local Boolean fixture, not PHP.

## Parameters and provenance

With M=n^2,D=ell^3,v=(n+1)*ell, choose the largest t=2^s-1 with 2t<=v,
R=t,c=s+2. The exact integer logarithm upper bound is
H=3*ell+ceil(log2(ell))+4. Set k=ceil(sqrt(ceil(v^2*H/R))) and
T=max(2k+1,k+s-2). The output includes the rational row-cap loss, cube
packing bound, and old-degree room inequality.

Every sufficient condition passes at ell=64,128. At ell=40 the image,
domain, and cube-packing bounds pass, but old-degree room fails. The large
parameter cases are distinct from the small algebra fixtures.

One compilation failed because a helper name collided with std::apply.
Renaming the helper resolved it; the next compilation and exact run passed.
The separately committed shared-reduction refactor was also checked once:
the preceding bounded-probe verifier output is byte-identical to cycle 141.

Standard algebra provenance: J.S. Milne,
[Fields and Galois Theory](https://www.jmilne.org/math/CourseNotes/FT.pdf),
finite fields and Corollary 4.22 (PDF page 54), and the Chinese remainder
map, Theorem 8.1 (PDF page 105), accessed 14 September 2026. These support
the small-degree factorization and residue decomposition. The notebook
states the source application and all degree accounting separately.
No third-party full text is included in this checkpoint.

`check-metadata.json` records the focused evidence and touched-link check;
`provenance.json` records code and evidence hashes. Timing and complete
command outputs, including the compiler failure and its recovery, are
archived under this session name in `research/provenance/session-records/`.
