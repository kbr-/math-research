# Finite retained-interface extension test

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-15-retained-interface-extension-test)
contains the complete finite statement, degree accounting, rank/duality argument,
and limitations. This checkpoint ends the current Spin run at the user's request.

## Result and scope

Over F2, retain accuracy-one ENS blocks A on three independent x coordinates,
B on three independent y coordinates, and C on all six. Include every original
companion and every old and fresh-coefficient Boolean equation. Add first the
complete helper on (x_i+y_i), then the complete helper on
(x_1+y_1+1,x_2+y_2,x_3+y_3). All helpers also have accuracy one and fresh coefficients.

In all three systems the quotient of the 210 formal expressions X_S Z_U with
|S|+2|U|<=5 has dimension 79. Source inclusion makes the relation kernels nested,
so equal rank proves equality of those kernels. Every compatible interface
functional therefore extends. Explicit full-source normalized duals preserve all
210 values of the baseline target separator, and C-AB has minimum ordinary NS
degree six in every case. This is a satisfiable Boolean-base finite test, not a
PHP theorem, arbitrary raw-coefficient extension, or general gluing mechanism.

## Reproduction

Use the protected launcher from the repository root, with a new output path:

```bash
./compute.sh --threads 1 --category local_processing \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_retained_interface.cpp -o /tmp/math-retained-interface
./compute.sh --threads 1 /tmp/math-retained-interface \
  --out /tmp/retained-interface-replay.jsonl
```

The initial target-only version is preserved as
`check_retained_interface_target_only.cpp` alongside its original report
`retained-interface-checks.jsonl`. Compile that version with the same flags plus
`-I research/tools`; its source path is this results directory. The completed
checker produced `retained-interface-moments.jsonl`. Both source versions refuse
to overwrite an existing output. Both compilations and both original exact runs
passed; no dependency was installed.

## Output encoding

Each JSONL stream begins with a schema record. A case supplies every original
block and axiom and the squarefree monomial-mask list in degree/numeric order.
Variable IDs 0..5 are the old coordinates, 6..17 are retained coefficients,
and 18..23 are helper coefficients when present. Coefficients lie in F2.

Each `row` is one original companion multiplied by the squarefree cofactor
given by its variable mask, then Boolean-reduced. Sparse vectors list nonzero
column IDs. Traces list earlier highest-column pivots XORed during elimination.
All companions have original degree three; every cofactor through degree two is
included. Boolean reduction accounts for all field multiples at the same
original degree, with no PC reuse. Ordinary certificates list their axiom IDs,
cofactor polynomials, and checked maximum degree.

The final stream additionally lists 210 `interface_feature` records per case.
Product-mask bits select A, B, C; the old mask selects old coordinates. Records
retain the interpreted vector, source reduction, interface reduction, feature
combination, and baseline functional value. These reproduce the quotient-rank
calculation. Each `interface_dual_extension` records every nonzero coordinate of
a full-source dual and verifies all 210 prescribed values and all source rows.
The full ranks are 1450, 2611, 4251; interface ranks are 79, 79, 79. No new
interface relation was found. Degree-six upper certificates and independent
target separators are also retained.

Metadata records the focused source/degree review and append-only/link checks.
Provenance hashes both reports, both exact source versions, and reused headers.
Timing and complete command outputs accompany the checkpoint. Coding time
includes the compaction interruption; final Git publication is after the snapshot.
