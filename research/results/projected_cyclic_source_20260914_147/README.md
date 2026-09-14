# Projected cyclic sources with affine offsets

The [notebook proof](https://kbr.is-a.dev/math-research/#entry-2026-09-14-projected-cyclic-source)
covers arbitrary binary projections of cyclic multiplication outputs, with old
affine offsets and independent affine operand probes. High quadratic rank gives
disjoint leading pairs after local row reduction. Low quadratic rank uses either
an affine-intersection kernel or a complete basis-prefix normalizer. A common
cube-volume multiplier gives old degree n^(2/3)*polylog(n) at polynomial inventory
and polylogarithmic source degree. Every original source axiom and coefficient
domain is retained, also with different positive accuracies at different blocks.

This is a restricted two-level source theorem. It does not establish a cyclic
representation for the general Frege source or a depth-uniform elimination step.

## Reproduce

From the repository root, with resource controls and an active timing session:

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_projected_cyclic_source.cpp -o /tmp/math-projected-cyclic-source
./compute.sh run TURN --threads 1 --timeout 180 -- \
  /tmp/math-projected-cyclic-source --out NEW_OUTPUT_PATH
~~~

The checker refuses to replace existing output. No dependencies were installed.
The cyclic coordinate construction is shared with the preceding verifier;
`extension_reduction.hpp` supports monic divisors with binary-extension coefficients.

## Complete exact evidence

`projected-cyclic-source-checks.jsonl` stores polynomial terms as
`[coefficient,[variable IDs with repetitions]]`. Extension coefficients are
polynomial-basis bitmasks modulo the supplied binary polynomial. Matrices, original
generators, row tracking, local divisors, targets, and ordinary NS cofactors are
retained. Large parameter values are exact decimal strings.

The 2,897 ordinary NS certificates comprise 1,290 auxiliary-field witnesses,
1,261 binary descents, one affine-intersection witness in the original quadratic
generators, and 345 complete source-axiom images.

- The length-three projection has rank two over F4, nonbinary lower coefficients,
  affine offsets, and a dependent third query. Every ordinary monomial through
  degree three in seven variables is reduced: 120 cases.
- The length-eight projection retains six of eight outputs and supplies three
  disjoint parity-selected heads. All 1,140 ordinary monomials through degree
  three in seventeen variables are reduced. The discarded outputs are never
  added as generators.
- One complete source has seventeen old variables, sixty-four reused rank-two
  bottoms, four parents, and 169 total variables. Its parents have quadratic-rank
  and affine-intersection-dimension pairs (6,0), (1,9), (2,2), and (1,1), exercising
  all four regimes with the same cubic multiplier. All 321 weighted original
  axiom images are saved, including a zero query with its original degree ceiling.
  Twelve further certificates check the low parent without the multiplier.
- Its 128 saved models enumerate the stated restricted domain: A0=1, other A=0,
  z=1, and all B masks with odd parity among the first six positions. The last
  two B positions vary freely. Eight models have low product equal to one.
  This is not enumeration of all old assignments or a selector-clamping theorem.
  An unweighted high companion fails at a saved zero-weight point.
- A separate source has bottom accuracy two and parent accuracy three, with nine
  total variables. All twelve original axioms and all four old assignments are
  checked. The parent companion has original degree nineteen; its Boolean-zero
  image has degree four. The original ceiling is retained.

Both source fixtures are local Boolean systems, not PHP models.

## Original-degree and parameter controls

The affine-intersection example has minimum NS degree four and minimum PC degree
three for its cubic target in the specified normalized input-plus-Boolean system.
The output retains the NS witness, a full 486-entry separating coefficient row
for all degree-three generator multiples, and a 75-line PC derivation. Listed
multi-input additions can be expanded into binary additions through degree three.
This is not a claim about old-PHP filtration or about adding those input equations
as axioms to the complete ENS source.

For M=n^2 and D=ell^3, the exact parameter checks use
H=4*ell+2*ceil(log2(ell))+5 and k=ceil((v^2*H)^(1/3)). The cube-volume and image
conditions pass at ell=64,128,256. Old-degree room fails at 64 and passes at
128 and 256. No large finite fields are instantiated for these parameter checks.

Compilation and the mathematical checks passed. After extracting the shared
cyclic-coordinate construction, a protected compatibility job compiled and ran
the preceding arbitrary-length checker; its complete output was byte-identical
to the saved cycle 146 result.

`check-metadata.json` records the focused evidence and touched-link review;
`provenance.json` records code and evidence hashes. Timing and full command outputs
are archived under this session in `research/provenance/session-records/`.
