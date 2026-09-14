# Degree-adapted source profiles from nonlinear selector rank

The [full notebook proof](https://kbr.is-a.dev/math-research/#entry-2026-09-14-selector-span-source-profiles)
upgrades the binary source's dependent-position condition to a dependent-span
rank condition. An adapted basis exposes the old affine intersection; the
profile prefixes are then pulled back to the original input list with individual
degree bounds preserved.

The cycle initially considered multilevel branching, but a source-specific
profile construction sufficed. No general raw-coefficient branching theorem is
claimed. The ordinary source compiler and an accuracy-dependent affine bound
give the stated polynomial necessary rank condition for hypothetical compact
proofs of fixed source depth.

## Reproduce

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra research/tools/check_selector_span_profiles.cpp \
  -o /tmp/math-selector-span-profile
./compute.sh run TURN --threads 1 -- \
  /tmp/math-selector-span-profile --out NEW_OUTPUT_PATH
~~~

Use the repository root and active resource controls. Output must be new.
The checker uses the existing exact sparse polynomial and Boolean-certificate
helpers, plus guarded 128-bit integer counts. No dependencies are installed.

## Evidence

NS-basis-profiles.jsonl preserves:

- A genuine two-level local source shape with four selector-dependent positions
  and dependent rank one, at h=2. Two old-affine bottom blocks are retained.
- The complete formal input, basis, and inverse matrices. Their column namespace
  consists of nine old bits and two formal selector names.
- The original parent input degrees (1,4,4,4,4), weight ten, affine core, exact
  original prefixes, and value of constructed cost eight.
- Nine full NS certificates, including all original companions and strict
  earlier-support Booleanity for the selected nonlinear input.
- All 512 old Boolean states with complete satisfying coefficient assignments
  and every retained axiom value.
- Countermodels for omitting the prefix pullback and for dropping the nonlinear
  tail. An ungraded-basis degree control does not claim an NS lower bound.
- Four exact dimension comparisons, including a failure when the accuracy
  hypothesis is omitted. Large integers are stored as decimal strings.

Raw polynomials use [coefficient,[variable IDs with repetitions]], with ordinary
powers. Source-profile degree checks preserve every original input's bound.
The fixture is a satisfiable local source-profile check, not a complete PHP proof
or a numerical instance of the asymptotic rank obstruction.

All builds and checks passed. The cycle reused the recorded full affine
intersection, weighted selector-degree reflection, product profiles, and direct
PC source compiler. Their exact dependencies and limitations are linked in the
notebook. No new external source was needed.

Source/dependency hashes, complete command evidence, and measured timing
accompany the checkpoint.
