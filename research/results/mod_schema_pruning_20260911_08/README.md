# Constant substitutions for MOD-schema blocks

11 September 2026. Timing session: `mod_schema_pruning_20260911_08`.
The full proofs and limitations are in the
[notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-mod-schema-pruning).

## Accepted findings

Earlier-level NS Booleanity certificates through twice each input's degree allow
one scalar factor per input. Every source block with at most h inputs can
therefore be removed at accuracy h without increasing NS or PC degree.
This extends the applicable Boolean packing condition beyond Booleanity modulo
bare field domains.

The explicit unsimplified expansion of the MOD recursion axiom has six schema
blocks with arities 2, 2, 2, 3, 2, 2. The blocks within its substituted arguments
are separate. All six schema blocks are eligible when h is at least three.
This combines with the preceding h-at-least-four template preprocessing at the
same LD bound.

The scalar substitutions give the MOD axiom an explicit polynomial in t and a.
It has an NS certificate from t^p-t and a^2-a through degree 6p-2. Substituting
the source argument polynomials gives degree at most (6p-2)d, where d bounds
their degrees. The prefix length does not multiply this degree bound.

## Complete evidence

`checks-01.jsonl` retains:

- 12 field-selector cases over primes 2, 3, 5, 7 and ranks 1, 2, 3, with
  independent nonlinear monomial generators, extra dependent inputs, and
  mixed old field/Boolean domains;
- 48 reconstructed domain certificates for all companion images, including
  a zero-input case, and 78 failed omitted-selector controls;
- eight Boolean-packing cases with inputs supplied by earlier ENS products,
  giving 20 complete earlier-companion NS certificates;
- six odd-prime controls showing that the images need not vanish on the bare
  domain grid when the parent companions are omitted;
- a complete MOD-schema AST with argument disjunction widths 17, 19, 23,
  six schema blocks, and a double-negation control that raises one arity to 24;
- four specialized MOD-axiom polynomials and complete domain certificates of
  degrees 10, 16, 28, 40 for p = 2, 3, 5, 7, respectively;
- all 34 field/Boolean grid checks for those axioms;
- interpolation errors and their certificates. Their t-domain cofactor is
  zero; the a-domain quotient has degree at most p-3 for odd p, and the
  binary interpolation error is zero.

The selector and packing examples are symbolic extension data, not PHP
refutations. The Boolean-packing examples use parent accuracy one and target
accuracy two or three; the general theorem allows these different accuracies.
The application to the actual source uses its uniform accuracy.

## Reproduction

From the repository root, with the shared resource controls active:

```bash
mkdir -p .resource-runtime/bin
./compute.sh --threads 1 c++ -std=c++17 -O3 -Wall -Wextra -Werror \
  research/tools/check_mod_schema_pruning.cpp \
  -o .resource-runtime/bin/check_mod_schema_pruning
./compute.sh --threads 1 --timeout 180 \
  .resource-runtime/bin/check_mod_schema_pruning \
  --out research/results/mod_schema_pruning_20260911_08/checks-REPRO.jsonl
```

Use a new output path. The checker refuses to replace existing results.
It used GCC 11.4.0, C++17, one thread, exact arithmetic, and the shared headers
`sparse_polynomial.hpp` and `ens_symbolic.hpp`.
The polynomial kernel now accepts an explicit degree guard; these tests request
64 to cover degree-38 selector images and degree-40 MOD certificates.
The default remains 32. No dependencies were installed.

## Polynomial and certificate encoding

JSONL schema 1. A polynomial is a list of terms
`[coefficient, [variable_ids]]`, with repeated sorted IDs representing powers.
All identities are ordinary polynomial identities before domain reduction.

Field-selector case j uses generator x_(2j)*x_(2j+1). Even variables have field
domain exponent p, odd variables have Boolean exponent two. The first rank
inputs are the chosen basis; extra inputs are explicit linear combinations.
The accuracy includes one unused factor for odd rank. A null original companion
degree marks a zero input.

A domain certificate gives one cofactor per variable for
x_v^(domain_powers[v])-x_v, together with its remainder and maximum summand
degree. The program reconstructs the entire original polynomial from these
cofactors. Omission witnesses set every odd variable to one, every even variable
to zero except the indicated coordinate, and that coordinate to the indicated
nonzero alpha.

Boolean-packing cases reserve 2*arity original Boolean variables. Parent
coefficient IDs follow, with field domain Fp, and each parent block records
its full inputs, product, prefixes, companions, and variable arrays.
The target product is the product of one minus each parent product.
Image certificates list cofactors of the corresponding parent's companions.

The odd-prime control sets the first original variable of every parent to one
and its second to zero. The first parent's active coefficient is p-1, giving
parent product two; the other parents' active coefficients are one, giving
product zero. All other coefficients are zero. This assignment obeys the
bare variable domains but violates the first parent's companion equation.

The AST record is a directed acyclic graph with node IDs, operators, labels,
argument/schema scopes, and child IDs. Arity is computed by flattening only
disjunction nodes, as in the source definition. Its second arity count first
removes double negations. This is a negative control, not the adopted expansion.

The specialized MOD records use variable 0 = t, variable 1 = a, with domain
powers p and two. They record every local product image, the full axiom
polynomial, and both cofactor arrays.

## Provenance and measurement

`provenance.json` hashes the checker, shared headers, accepted output, and the
historical packing source used in the argument. The BIKPRS source is the same
locally supplied copy identified in [SOURCE_AUDIT.md](../../notes/SOURCE_AUDIT.md);
the relevant clauses are Definition 1.1 and Definition 6.8.

`timing.html` is the measured export embedded in the notebook. Preliminary MOD
identities and the selector idea were considered between the preceding snapshot
and this session's start and are not included in this interval. This interval
includes completion of the preceding checkpoint, source review, refinement,
tests, recording, compaction and restoration, and user-requested framework and
context-setting work. The session archive retains full command output.
