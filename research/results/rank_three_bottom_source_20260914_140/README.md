# Binary rank-three bottoms and nested affine branches

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-14-rank-three-bottom-source)
contains the working complete source theorem. Conditioning a flat indicator
gives zero or a lower-rank flat indicator. A common kernel can therefore
treat independent triples, independent pairs, and affine branches together.
The direct old-only coefficient degrees add along the branches.

Polynomial-inventory complete two-level sources with proper binary affine
bottoms of rank at most three exclude polylog-degree refutations. The final
old degree is n^(6/7) times polylog(n). The h=1 bottom normalization costs at
most a factor two; h>=2 preserves degree. All original coefficient uses and
parent overlaps are included.

Arbitrary sums of these indicators, ranks growing with n, later nonlinear
levels, and odd-prime affine probes remain outside the theorem.

## Reproduce

From the repository root, with active resource controls and a timing session:

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_combined_quadratic_source.cpp -o /tmp/math-rank-three-source
./compute.sh run TURN --threads 1 --timeout 180 -- \
  /tmp/math-rank-three-source --rank-three --out NEW_OUTPUT_PATH
~~~

Use a new output path. No dependency installation was needed.
Without `--rank-three`, the previous rank-two output is reproduced; its
byte-for-byte comparison to cycle 139 passed after the extension.

## Complete exact evidence

`rank-three-source-checks.jsonl` retains ordinary polynomials as
`[coefficient,[variable IDs with repetitions]]`, every NS cofactor, complete
source systems and simultaneous coefficient maps, and full conditional
assignments. Large integers are exact decimal strings.

The 596 NS certificates comprise:

- 15 bottom-normalization companion and coefficient-domain images at
  accuracies one and two, checked against their respective degree factors;
- 512 exhaustive affine-triple patterns over two Boolean coordinates,
  with canonical zero or flat indicators;
- 2 conditional cubic-to-quadratic comparisons;
- 66 weighted original axiom images and 1 kernel Boolean residual for the
  complete mixed cubic endpoint.

The 512 patterns give 301 inconsistent systems, one rank-zero indicator,
42 rank-one indicators, and 168 rank-two indicators. The conditional cubic
ab(a+b+u) becomes zero or ab according to u, but the unreduced ordinary
polynomial at u=0 is nonzero. This protects the Boolean-ideal distinction.

The mixed endpoint has 18 old variables and four source blocks: a high-triple
tuple, a parent with a high-pair branch, and parents with high- and low-affine
leaves. Its degree-five kernel is z*w times the preceding cycle's cubic
kernel. Thirteen independent affine coordinates reach the high threshold
2*k+3 exactly. Coefficient degree nine is the sum 3+2+4 from two selectors
and a leaf coefficient. Every generator multiple is checked by the shared
NS verifier.

All 14,336 old assignments with nonzero kernel give complete conditional
source models. An unweighted high-triple companion and a missing outer
unit-branch coefficient provide negative controls. These are local Boolean
models, not PHP models in the asymptotic theorem.

Three exact triple-quotient coefficient tables are independently verified
by a multinomial formula; the two small cases also enumerate every Boolean
monomial. The v=60, R3=20, k=30 table has quotient dimension strictly below
the homogeneous domain dimension. No 2^60 enumeration is performed.

Integer parameter checks use M=n^2, source D=ell^2, and normalized D0=2D.
They pass every sufficient condition at ell=256 and 512. At ell=128, the
range, space, and image-count bounds pass but the old-degree bound fails.
The notebook states the integer choices and logarithmic upper bounds.
Large branch inventories are never materialized.

Compilation and all checks passed. The previous default regression is a
tool-preservation check, not a new rank-two result. Earlier matching-moment
and cube suites were not rerun.

`check-metadata.json` records focused artifact and notebook-link checks;
`provenance.json` records source and evidence hashes. The timing journal and
complete command outputs are archived under this session name in
`research/provenance/session-records/`.
