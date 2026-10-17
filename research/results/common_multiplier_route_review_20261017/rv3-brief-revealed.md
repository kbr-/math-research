# Revealed stage: correctness review of the window review (same reviewer)

Read-only. The route is now revealed: the review draft is /home/kbr/.claude/jobs/354c41d4/tmp/rv3-draft.html
(title, status, gate, Meta and process assessment pending), with its sentence listing
/home/kbr/.claude/jobs/354c41d4/tmp/rv3-sentences.txt. Results excerpts: rv3-results.md (now with
check:top-degree-partition-kernels, check:dense-linear-kernels, conj:representative-sum-transfer,
conj:linear-kernel-transfer, check:functional-factor-kernels, ex:top-degree-linear-killer). Saved outputs used:
research/results/common_multiplier_linear_sizes_20261017/rep_sum.json and pair_saving.json (worktree
/home/kbr/dev/math-auxiliary/research/tmp/common-multiplier-worktree). Spec of the correction:
research/results/common_multiplier_route_review_20261017/claim-spec.json.

Correctness items:
1. Obstacle: the claim that on every board where the refutation degree is recorded the last proper degree is
   ceil(N/2); the use of lem:native-restriction (a); "closure kernels beyond the domain's occur only for errors
   no numbering admits".
2. Decisive test: the Trivial cases (translation invariance of J, a, b), Power (a <= b <= dim J; the
   inapplicability of the numbering lemma), and the Instance check's figures: dim W = 4, dim J = 5 for each
   non-congruent pair, the summed condition 12 >= 9. Are the three outcomes and what each would mean stated
   rightly? Is any instance already decided?
3. The Correction (your finding), its Hypotheses and Degenerate cases, and the spec.
4. The Decision's reading of the union-of-supports clause, and the Extra requirements paragraph.
5. The Review paragraph's five answers.

Second-stage request: try the step at which the Attempt stops, deciding a (the best single representative
pair's domain common kernel plus W) at the 4x3 instance, by hand or any small reasoning; say what you find.
Then, as the open point: is the testbed conclusion (leave pigeonhole systems if dim J = a) right, and which
system would you take next?

Process audit: as in your definition; propose title and status.
Report: verdict; required changes as short bullets; Attempt result; suggestions marked unverified; edit nothing.
