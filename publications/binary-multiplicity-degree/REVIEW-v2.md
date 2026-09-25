# Version 2 readiness review (25 September 2026)

Self-review against [the checklist](../CHECKLIST.md) and one fresh-context AI referee pass
(Claude Opus 5.5). No human or external expert review has occurred.

## Referee pass

The referee checked the lower bound of Section 4 step by step (expansion, the four cases of the
inversion, the lowest part, the forms recursion, the index ranges and the claim that only τ = s
survives the reduction), the construction, the minimum lemma including n = 1 and k = 2^n, and
the claims of the abstract and introduction. It confirmed the minimum formula numerically
for n ≤ 7, k < 300. It found no mathematical gap. Required changes, all applied:

- The "smallest example" with k − ℓ − 1 ≥ 2^n was wrong (n = 2, k = 6); it is now
  n = 1, k = 3, ℓ = 0 (3 against 4, attained by (1 + x)³), with n = 2, k = 5 (8 against 9).
- The abstract said "below that range" for the case k − ℓ − 1 ≥ 2^n; it now names the case.
- The real value n + 2k − 3 of Sauermann and Wigderson now carries its hypothesis n ≥ 2k − 3
  (checked against arXiv:2010.00077v2, Theorem 1.3).
- The grid-vanishing lemma has no [Lean] link (Mathlib's version is used); the introduction now
  says so.
- The wording of the 696-value check count was clarified.

Declined: dropping the unused hypothesis t < k in Lemma 4.5(2), since the Lean statement has it.

## Checklist items addressed

- Boundary claims: the strict comparison of Φ with Menezes' formula for k − ℓ − 1 ≥ 2^n is
  proved in the text and marked as not formalized. The minimum lemma's Lean proof goes through
  the second proof; the text says so.
- References: Alon (1999) checked against Crossref; Menezes' arXiv listing checked on
  25 September 2026 (version 1 only).
- Revision identity: version 2, dated, with a "Changes from version 1" paragraph.
- Verification map: every cited declaration name was checked against the Lean sources by
  script. The aggregate target `claims/BinaryMultiplicityDegreePaper2.lean` passes `verify.sh`
  at commit 86d8a6ba (`research/results/bmd-f2-paper-v2/lean-verification-paper2.txt`).

## Outstanding

- The full checklist pass, with its two outstanding items (independent validation, and the
  author's own checking), is recorded in [CHECKLIST.md](CHECKLIST.md).
- Publication and correspondence are the author's decisions.

The Lean commit 86d8a6ba cited by the paper was pushed to `main` on 25 September 2026.
