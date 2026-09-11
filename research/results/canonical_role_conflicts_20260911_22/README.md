# Mixed Booleanity modes and canonical roles

11 September 2026. The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-mixed-booleanity)
proves sharp Booleanity rebuilding for retained, unit-product, packed, and
base-zero modes, and the same-degree outer NS/PC transfer under its explicit
access conditions. It also records the ordinary-PHP-compatible choices and a
separate local wide-product identity with an optimal coefficient-degree bound.
Global coverage of wide direct-use blocks remains open.

## Reproduce

With the shared resource controls active, from the repository root:

```bash
mkdir -p research/tmp
./compute.sh --threads 1 c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_mixed_booleanity.cpp -o research/tmp/check_mixed_booleanity
./compute.sh --threads 1 research/tmp/check_mixed_booleanity \
  --out research/results/canonical_role_conflicts_20260911_22/checks-REPRO.jsonl
```

Use a new output path; its parent is created automatically. GCC 11.4.0, C++17,
one thread, and the unchanged sparse polynomial/ENS kernels were used. No
dependencies were installed. Compilation and all mathematical checks passed.
The complete accepted output is 1,028,036 bytes.

## Source representation and exact evidence

There are 12 cases over p=2,3, widths k=3,7, and three modes for the argument
A=P_(x_1,...,x_k): retain, unit product, or base zero 1-rho with rho=sum x_i.
Accuracy is two. Subsequent gates I=P_(A,b) and J=P_(I,c) are packed globally.
The same I is both a directly used gate and an argument whose Booleanity is
requested. One global assignment serves both roles.

Base IDs 0 through k-1 are Boolean x_i; IDs k,k+1 are Boolean b,c. Remaining
IDs are coefficient variables. The complete original argument block is saved.
The original I and J are a factored DAG with explicit input references, accuracy,
coefficient-variable matrices, and product-degree ledger. They need not be
expanded before their immediate constant specialization. Their original
product degrees are 10 and 22, with companion degrees (14,11) and (32,23).
The argument's original product degree is four and companion degrees are five.

Every selected coefficient image is recorded and its field equation maps to
zero. The output gives all specialized products and retained/base axiom arrays,
plus 104 exact NS certificates with complete cofactors. These cover argument,
I, and J Booleanity, every packed companion image, and every base-zero argument
companion. Booleanity is checked through twice the specialized value degree;
companion images are checked against their original degrees. Certificate
reconstructions equal the target and reject adding a nonzero constant error.

Polynomial terms are `[coefficient, [sorted repeated variable IDs]]`, using
the sparse kernel encoding. In unit mode A'=1, I'=0, J'=1-c: the last selected
product is nonconstant and still has the required Booleanity certificate.
In base-zero mode the old base contains rho-1, and the sharp argument
Booleanity identity is (1-rho)^2-(1-rho)=rho(rho-1).

Each case also saves a model of its old axioms where forcing I=1 would make
one directly requested companion equal one, although I's Booleanity would be
zero. Packing gives I'=0 at that same model. Retained cases satisfy every
argument companion; base-zero cases satisfy their single row equation. These
are satisfiable controls, not full inconsistent PHP instances.

The general mixed theorem, PHP assumption accounting, and optimal local
wide-product coefficient bound are analytic arguments in the notebook. This
checker does not compile an arbitrary Frege proof or audit all its ports.
The previously established PHP clause identities were not recomputed.

## Provenance and timing

`provenance.json` hashes the checker, unchanged sparse/ENS kernels, and complete
output. The source reading was the exact earlier projection and Booleanity-port
entry in the notebook; no new paper was downloaded or imported.

`timing.html` is embedded in the entry. Initial preparation includes the prior
research and timing-policy checkpoints, their shared publication audit, and
authorized push. The reading window includes early formulation of the mixed
theorem alongside source interpretation. Coding was marked in a separate call
before the code patch was drafted, following the corrected timing rule.
Mathematics includes proof review, degree accounting, and notebook drafting.
No historical suite or rendering build was repeated. Complete evidence is in
`research/provenance/session-records/canonical_role_conflicts_20260911_22/`.
