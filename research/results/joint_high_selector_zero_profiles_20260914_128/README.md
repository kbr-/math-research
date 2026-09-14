# Joint high-selector zeroes and source profiles

The [notebook proof](https://kbr.is-a.dev/math-research/#entry-2026-09-14-joint-high-selector-zero-profiles)
extends the old-target theorem after adding zero equations for all eligible
high-affine-rank first-level products. Their weighted images cost pk.

In the binary costed source, a constrained bottom value has a complete zero
profile with its original prefix residual and cost. Deleting those selector
columns before applying the adapted-rank criterion gives a further restricted
source exclusion. General surviving low-rank dependence remains open.

## Reproduce

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra research/tools/check_joint_selector_zero.cpp \
  -o /tmp/math-joint-selector-zero
./compute.sh run TURN --threads 1 -- \
  /tmp/math-joint-selector-zero --out NEW_OUTPUT_PATH
~~~

Use a new output path and run from the repository root with active resource
controls. The checker uses exact compiled arithmetic and installs no packages.

## Evidence

The output contains 50 complete NS certificates:

- 14 over F2 and 22 over F3 check two simultaneous weighted selector images,
  all their companions, and every coefficient-field image, including zero images.
- 12 check the binary source's zero-value prefixes, projected-input comparisons,
  parent prefix, companions, and Booleanity.
- Two literal-selector certificates show why arbitrary low-rank products cannot
  be constrained to zero while preserving old affine targets.

Every system record supplies its full axiom list. Certificate terms identify
axioms and preserve all cofactors; polynomials use
[coefficient,[variable IDs with repetitions]]. Source blocks and coefficient maps
are explicit, with original degree budgets and actual witness degrees.

The two-level fixture retains 144 canonical models satisfying both clamps and
one missing-clamp countermodel. The literal controls retain two further models.
Unweighted-image counterexamples and an actual odd-prime coefficient value two
are included separately.

These small rank-two tuples test local image identities and conditional source
profiles. They are not high-rank instances of the asymptotic theorem, and their
old bases are local Boolean domains, not PHP. The notebook's dimension argument
supplies the high-rank guarantee.

All checks passed. The final compilation was clean. Source/dependency hashes,
full command evidence, and measured timing are retained with the checkpoint.
