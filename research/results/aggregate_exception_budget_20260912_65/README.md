# A total exception budget and a hard residual

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-total-exception-budget)
contains the complete trimming proof, finite size conditions, degree ledger,
and analytic controls. This record preserves its dependencies and measurement
scope; it is not a separate live mathematical summary.

This was an analytic cycle. A matching of size equal to the larger of the two
marked sets covers all pigeons and columns whose exception degree exceeds B.
Each set has size at most floor(E/(B+1)). The remaining profile has both absolute
exception bounds at most B. The notebook composes this with:

- [Bounded-exception layouts](https://kbr-.github.io/math-research/#bounded-exception-elimination)
  and the degree-sum matching proof at equality.
- [Majority-profile layouts](https://kbr-.github.io/math-research/#majority-profile-elimination)
  and their exact size, probability, and characteristic conditions.
- [Local-statistic package transfer](https://kbr-.github.io/math-research/#column-dependent-package-elimination)
  preserving original NS/PC degree and existing witness ceilings.

The deterministic asymptotic conditions are ED=o(n^2) and pD=o(n), with D>=1.
The fixed-density route assumes E<=(1/12-eta)n^2 for fixed 0<eta<1/12.
The constant 1/12 is sufficient for this estimate, not asserted optimal.
Source qualification is still an open hypothesis.

No numerical computation was required and no historical suite was rerun.
The zero-exception limit, one concentrated exceptional pigeon, and the vanishing
margin at the displayed finite boundary are checked by explicit algebra in the
entry. Prior finite evidence remains in:

- ../bounded_exception_layouts_20260912_64/checks-01.jsonl
- ../majority_profile_layouts_20260912_62/checks-01.jsonl
- ../column_dependent_freezing_20260912_61/checks-01.jsonl

The initial outline was measured in the preceding cycle. This session began
with checkpoint and publication work, including the separate commit preserving
the user's renewed standing push authorization. A brief documentation follow-up
was mixed with preparation; its Markdown fetch failed, and the HTML documentation
was read successfully. The reviewed public history passed its check and was pushed.
The mathematics phase then covered the detailed proof and notebook drafting.

The timing fragment, archived session, and provenance manifest preserve measured
work and hashes of the cited finite evidence. No old check is presented as a new run.
