# Retained core sharing and optimal linear factor packing

11 September 2026. Session: `relative_implication_chains_20260911_10`.
Full proofs, hypotheses, and limitations are in the
[notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-relative-core-cover).

## Results

An affine global substitution removes blocks covered by retained input tuples
when t retained core factors plus the residual count fit the selected block's
accuracy. It preserves NS/PC degree, supports same-level cores, and explicitly
specializes later inputs. Residual Booleanity certificates use original earlier
levels. Designated cores remain retained.

Blocks containing a full original row or collision tuple instead admit a base
normalizer regardless of additional inputs. Both rules can join the prior source
preprocessing at the same LD bound under the notebook's compatibility conditions.

For nonconstant affine inputs at one level, factor packing gives substitution
degree T=max(1,ceil((2t+k)/h)-1). This is optimal for the prescribed product on
independent inputs. It is not a lower bound for all elimination strategies.
An explicit constant-height tautology proof with a long raw inclusion chain
shows why proof-tree height alone does not control every candidate core forest.
The example does not establish essential cofactor support.

## Complete exact evidence

`checks-01.jsonl` contains 28 cases over p=2,3,5,7. For each prime the linear
parameter triples (h,t,k) are (2,1,1), (2,1,2), (2,2,1), (3,1,4), (3,2,2),
and (3,2,5). One additional case uses (2,1,1) and a nonlinear Boolean residual
x_2*x_3, with an explicit degree-four Booleanity certificate.

The output preserves 176 reconstructed companion-image NS certificates, 364
field-image certificates, and 64 old Booleanity certificates. All original
degrees and their T-scaled budgets are checked. Field certificates never use
the domain equation of a removed variable.

All 24 linear cases attain the prescribed-product degree bound. Twelve later
blocks match direct substitution and reject unchanged inputs. Four omission
countermodels satisfy the retained core companions and old Boolean domains but
make an untested residual image one. These are local ENS data, not PHP refutations
or a finite test of every multi-level composition.

## Reproduction

From the repository root with the shared resource controls active:

```bash
mkdir -p .resource-runtime/bin
./compute.sh --threads 1 c++ -std=c++17 -O3 -Wall -Wextra -Werror \
  research/tools/check_relative_core_cover.cpp \
  -o .resource-runtime/bin/check_relative_core_cover
./compute.sh --threads 1 --timeout 180 \
  .resource-runtime/bin/check_relative_core_cover \
  --out research/results/relative_implication_chains_20260911_10/checks-REPRO.jsonl
```

An output path must be new. The accepted run used GCC 11.4.0, C++17, one thread,
and exact arithmetic with degree guard 64. No dependencies were installed.

## Data coordinates

JSONL schema 1; polynomials are term arrays `[coefficient,[variable_ids]]`, with
sorted repeated IDs encoding powers in the ordinary ring. Variables 0 and 1 are
the core inputs. In linear cases variables 2 onward are independent residuals;
the nonlinear case has residual x_2*x_3. These old variables are Boolean.

Fresh coefficient IDs follow for the original core and selected block. The
retained core keeps its first t coefficient vectors; its later vectors map to
zero. `coefficient_images` records every removed coordinate. `factor_bins` indexes
the saved `fundamental_factors`, whose coefficient arrays use the selected input
order: both core inputs followed by residuals.

`new_certificate_axioms` lists retained core companions followed by the original
Boolean equations, in variable order. Root and selected cofactor arrays refer
to this list. Old Booleanity certificates use the old Boolean variable order.
Field-image certificates refer to `domain_powers`: old variables have exponent
two, coefficient variables exponent p; all cofactors at removed variable IDs
are checked to be zero.

The prescribed product and both original blocks are saved in full. At h=2 in
linear cases, a later one-input ENS block is added on the selected product, with
one factor. Both its original and specialized versions are saved. The omission
witness sets variable 3 to one and every other variable to zero.

## Shared-kernel refactor and provenance

The domain-reduction routine was moved from the MOD checker to the reusable
`research/tools/domain_polynomial.hpp`, used by both checkers. Its affected
existing suite was rerun once; `cmp` confirmed that `mod-domain-recheck.jsonl`
is byte-identical to the accepted cycle-8 MOD output. This is implementation
validation, not new mathematical coverage. Its compile, run, and comparison
commands are preserved in the session archive.

`provenance.json` hashes both current checkers, shared headers, accepted outputs,
and the historical batching source consulted. BIKPRS Definition 6.8 was reread
from the same local source identified in SOURCE_AUDIT.md; the notebook proofs
also reuse the original-degree Booleanity and simulation records.

`timing.html` is embedded in the notebook. The interval includes the preceding
checkpoint's finalization and an explicitly marked publication-approval
interruption. Phase labels describe work windows, not pure cognition; computation
design also involved refining the correctness and degree arguments of the packing
algorithm. The full session archive preserves command output and measured phases.
