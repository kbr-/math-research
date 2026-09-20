# Exact one-row predicate trade lifts

These controls accompany the notebook's
[`row-predicate-trade-lift`](https://kbr.is-a.dev/math-research/#row-predicate-trade-lift)
and local literal-MP fan application. They do not construct a complete ENS source
design or settle multirow compatibility.

The fixed board has four rows and sixteen labels. Old degree-two data are extended
through degree three. Predicates are all four bits of the label of row zero. The
checker runs over F2, F3 and F5, with no random choices, matrix-space search or
new dependencies. Its 14,945 matching monomials through degree three are bounded
before use; the only linear solves have five rows and twelve columns.

Reproduce from the repository root with a fresh output path:

```bash
./compute.sh --threads 1 g++ -O2 -std=c++17 -Wall -Wextra -Werror \
  research/tools/check_row_predicate_trade_lift.cpp -o /tmp/check_row_predicate_trade_lift
./compute.sh --threads 1 /tmp/check_row_predicate_trade_lift --out /tmp/row-fan-moments.json
```

For each field the output preserves three signed trades, all available label sets,
desired predicate moments, exact zero-sum row factors, the resulting top trade
correction, all target defects and verification counts. A matching key has five
bits per row: zero means absent, otherwise the value is label+1. Sparse entries are
`[matching_key, field_value]`; omitted entries are zero. All correction moments
below degree three and all target-defect moments below degree two are zero.

The prescribed old B functional is evaluation at the injection `[9,0,1,2]` through
degree two. The extended B is the same point functional plus the recorded top
correction through degree three. For predicate t, the prescribed C functional is
`(1-bit_t(9))*point - target_defect_t` through degree two. These formulas and the
sparse output specify the complete moment arrays, including their zeros.

Per field, 3,860 row-marginal equations, 6,020 conditioning equations and 6,020
MP equations passed. Linear right-inverse choices were checked. Omitting the
correction causes 24 MP violations. The failed-rank control uses the indicator of
label 3 after deleting labels 3,4,5,6: its desired row factor is inconsistent,
and the recorded target matching already uses column 3 in another row, proving
that its requested conditioned moment cannot be lifted.

The first build rejected one misleading-indentation warning, corrected before
the accepted build and run. The measured session also includes the user's Pages
CI detour; it found a prior deployment-token failure followed by a successful
unchanged workflow and a live current notebook. No Pages code was changed.
