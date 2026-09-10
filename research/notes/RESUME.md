# Resume here after compaction

**Read this file fully. Do not repeat the full manuscript/reference import.**
Current notes live in `research/notes/`; historical proofs remain in
`php_codex_handoff/manuscript/`. Never write new work inside the handoff.
The user explicitly requested economical context use: short tool outputs and
targeted source excerpts. This file is the restart map, not a substitute for
checking the exact proof when extending a theorem.

## Restart checklist

1. Read this file and the current user request. Obey the workspace and research/AGENTS.md files.
2. Before computations, read `COMPUTATION_RULES.md` and verify
   `./compute.sh --status`. After reboot, run
   `python3 resource-controls/setup.py` if needed.
3. Start a new timing session with `./compute.sh start NAME` from
   the repository root. Mark reading/review separately; time tools and failures;
   end with `./compute.sh report NAME --stop`. Do not invent pure
   reasoning or network-latency measurements.
   Run workloads with `./compute.sh run NAME --threads N -- COMMAND ...`;
   this single executable now combines the resource guard and timing. There is
   no separate current compute.py or timing.py. Defaults: 180-second job timeout
   and an 8,000-byte output tail; full output remains in research/logs/.
4. Load only the definitions, claim proof, or source passage needed for the next
   task. `php_codex_handoff/manuscript/CLAIM_INDEX.md` and parsed entries in `php_codex_handoff/manuscript/claims.json` locate
   labels and TeX ranges; do not dump the whole JSON or manuscript.
5. Maintain new notes and the current audit ledger. Preserve original TeX,
   generated chapter Markdown, archived ZIPs, and historical outputs.
6. Use paths relative to this checkout, not the original machine's home directory.
   `./start-codex.sh` resumes an exact ignored local session ID, or bootstraps a
   fresh session after cloning. Only the main session explicitly being bound runs
   `./tools/remember-codex-session.py`; never bind subagents or unrelated chats.
7. After every research turn, including failed attempts and no-progress turns,
   update the overview and restart notes, archive the completed timing session
   with `./tools/archive-session.py NAME`, and commit the complete related
   checkpoint. Operational logs are ignored; durable evidence belongs in
   research/provenance/ or research/results/. See root AGENTS.md.
   Important computation outputs, including large tables/certificates, belong in
   tracked result files. Computation scripts should expose `--out PATH`; reference
   outputs and provenance in the research log/notebook and commit them with the
   result. Never substitute a truncated terminal preview for the complete data.

## Live notebook: required publication workflow

The user reads the repository-root `notebook.html` through `python3 server.py` at
http://localhost:8000. The browser automatically refreshes when the file changes.
GitHub Pages publication is configured in `.github/workflows/pages.yml`, with
one-time Source=GitHub Actions activation described in README.md. It deploys only
the rendered notebook artifact from `main`; the local server remains independent.
After each research turn, update its **Where we stand**, **The remaining route**
(highest risk first), and **Proposed next step** sections to reflect the current
state. Keep these summaries brief; do not invent progress.

Every substantial new theorem, lemma, proof, counterexample, computation, or
mathematical obstruction must also appear in the notebook's final **Research
record**, not merely in chat or internal Markdown notes. Append entries in
chronological order with a date, title, stable anchor, explicit epistemic status,
precise assumptions/statement, and self-contained argument plus necessary degree
accounting and evidence. Correct earlier mathematics by appending a linked
correction or retraction; preserve the old entry and revise the living overview.
Keep the supporting notes and this restart map consistent with developments.

On resume, read the notebook's three overview sections and only the latest or
relevant record entries. Do not import the entire notebook as it grows. Pure
setup/admin turns do not require a mathematical record entry unless requested.
Every attempted research turn does require an entry, even if it produces nothing
useful. State the attempted approach, outcome, and unresolved issue honestly.
End every such entry with a measured category/elapsed timing table, bold total
first. Generate the fragment from actual data using
`./compute.sh report NAME --stop --html-out research/results/NAME/timing.html`;
embed it, archive timing, and commit the complete entry. Draft the mathematical
entry and overview before the snapshot; disclose that subsequent publication,
archiving, Git finalization, and response delivery are outside that interval.
Do not invent timing categories or confuse failed commands with failed proofs.
Keep future table footnotes to one short sentence, with exceptional details only
when needed. Do not repeat the first entry's long methodology disclaimer; retain
that first entry unchanged and refer to COMPUTATION_RULES.md for the full scope.

## Goal and exact mathematical objects

For each fixed prime p, prove ordinary PHP has superpolynomial fixed-depth
AC^0[p]-Frege proof size:
\(\forall\ell,K\;\exists n_0\;\forall n\ge n_0:
\operatorname{Size}_{\ell,p}(\mathrm{PHP}_n)>n^K\).
**The payoff is NOT established.**

Over F_p use n+1 pigeons, n holes, and
\[
\mathcal F_n=\{\rho_i-1\}_i\cup
\{x_{ij}x_{i'j}:i\ne i'\}\cup\{x_{ij}^2-x_{ij}\}_{i,j},
\qquad \rho_i=\sum_jx_{ij}.
\]
There are **no same-row exclusions**. A Boolean row summing to 1 modulo p can
contain p+1 ones. Do not substitute a functional/chessboard encoding.

An ordinary degree-D design is a normalized linear functional annihilating
\(\mathcal I_D=\operatorname{span}\{qf:\deg(qf)\le D\}\).
PC permits linear combinations and multiplication of an earlier polynomial by
one variable, with ordinary collected line degree bounded by D. Its space
\(\mathcal C_D\) can exceed \(\mathcal I_D\). Neither is the unrestricted ideal.
Reuse satisfies
\(f\in\mathcal C_c\Rightarrow qf\in
\mathcal C_{\max\{c,\deg q+\deg f\}}\): multiply the final polynomial,
not its entire derivation. A design is not multiplicative.

ENS block a has **all** companions
\[
E_{a,i}=g_{a,i}\prod_{u=1}^{h_a}
\left(1-\sum_jr_{a,u,j}g_{a,j}\right)
\]
and field axioms r^p-r. Fresh variables are shared within a block and disjoint
across same-level blocks. Inputs may be nonlinear and use earlier levels.
With nonzero inputs, \(\delta_a=\max_i\deg g_{a,i}\) and original companion
degree \(e_{a,i}=\deg g_{a,i}+h_a(\delta_a+1)\).
Activity/cofactor spaces use this **original joint-variable degree**; later
specialization or Boolean reduction does not retroactively enlarge them.

## What is available, and the obstruction

Working proof tools (focused local audit found no gap, not formal verification):

- `lem:reuse`, `lem:substitution`, `lem:fieldreduction`, `lem:selectors`, Chapter 1.
  Field-ideal membership admits degree-nonincreasing univariate reduction.
- `thm:one-elimination`, `thm:additive`, Chapter 7:
  one block costs (p-1)delta; reverse-level elimination costs
  \(D+(p-1)\sum_a\delta_a\).
- `thm:nested`, Chapter 8: an entire nested input-span chain costs
  \(D+(p-1)\delta\), by replaying the original proof and reusing learned inputs.
- `thm:cores`, Chapter 8: nested cores of degree gamma and residual ranks r_a,
  with representatives of degree eta_a, cost \(TD+(p-1)\gamma\), where
  \(T=\max_a\max\{1,\eta_a(\lceil(p-1)r_a/h_a\rceil-1)_+\}\).
  Quotient variants require supplied bounded-degree base derivations.

Chapter 9 optimizes the **static affine criterion**, including order and batch
partition. Ordering by dimension is optimal. The n graph spaces
\(V_\alpha=\{(u,\alpha u)\}\subset K^q\oplus K^q\) have pairwise zero
intersection, even modulo row equations, and criterion optimum
\(\min\{D+(p-1)n,T(r)D\}\), eventually exceeding n/2.
They are admissible extension data, **not a refutation**. Do not search for a
better static ordering or infer a barrier to every elimination method.

The prefix-pebbling control (`lem:prefixcertificate`, Chapter 7) is a genuine
NS refutation of degree 4h+2 with adjacent-block interactions along a long
chain. Its base can have high NS degree but has PC degree at most three.
Thus sparse local interactions and high ordinary-design degree alone do not
give universal cheap batching; large antichains alone are not an obstruction.

The optional non-Boolean branch has corrected range 2d-1<=n, not d<n.
Generic survival there does not imply Boolean ENS survival. Consult Chapter 2
only if that branch becomes relevant.

## Import and source audit are already done

All eleven chapters were fully read; 117 files and eleven ZIPs passed integrity
checks. Historical suites were not rerun. **All four reference PDFs were imported locally
and extracted** in `research/references/cache/` and `research/references/extracted/`.

- Krajicek, arXiv:2301.10617v3: full extracted text read. Definition 2.1 matches
  ENS; pp. 10-11 / Lemma 4.1 give ordinary designs on the stronger row-exclusive
  system and residual boards. Delete row exclusions to get our base. There is
  a harmless odd-prime sign typo in the p. 10 Boolean-redundancy display.
- Razborov, published 1998 copy: Definition 2.4, printed p. 296 (PDF p. 6),
  lists row sums and both exclusions in the Boolean quotient. Theorem 3.1,
  printed p. 297 (PDF p. 7), gives PC degree >= n/2+1 for every m>n and field.
  Our ordinary-PC derivations map degree-nonincreasingly into his calculus;
  deletion gives the base and residual PC lower bounds. This discharges the
  imported hypothesis in `thm:rigidity`; it does not prove the final payoff.
- BIKPRS, user-supplied author-layout copy: Definitions 6.1/6.4/6.5 distinguish
  Boolean originals from field extension variables. Theorem 6.7(1), PDF p. 26,
  gives polynomially many companions, ell+O(1) levels, and degree
  \((d_0+\log S)(h+1)^{O(\ell)}\) for fixed p. Definition 6.8 and the proof
  on pp. 28-31 construct blocks from disjunction approximations in a balanced
  tree-like Frege proof of height O(log S). Formula depth and derivation height
  are different. TRUE is encoded by zero in this paper. No affordable bound on
  essential cofactor support or residual rank is asserted by the simulation.
- Pebbling, arXiv:2001.02481v1: equations (2.5)-(2.6) and Theorem 3.1 match the
  all-field NS/reversible-pebbling correspondence. Gamma(1,r), from Definition
  4.7 and Lemma 4.9, supplies a single-sink Theta(r^3)-size, Omega(r)-price family.

Detailed provenance, reading coverage, and limitations: `IMPORT_LOG.md` and
`SOURCE_AUDIT.md`. Public Git includes the CC BY 4.0 Krajicek paper only. BIKPRS,
Razborov, and Pebbling PDFs/full text remain ignored local copies; obtain authorized
copies separately on a new machine if needed. All bibliography/audit notes are
preserved. Check reference availability before reading; do not repeat a full import
or claim to recheck sources that are absent. Follow root LICENSE/ATTRIBUTION.md and
THIRD_PARTY_NOTICES.md; cite original mathematical contributions appropriately.

## Next research task and remaining gaps

The missing theorem is **affordable refutation-sensitive elimination** (or a
joint design) for every relevant translated NS certificate, yielding base PC
degree at most \(b_n=\lfloor n/2\rfloor\). A polynomial bound in D,h,log M
would suffice for fixed depth and p, but is unproved.

The first local RESEARCH_LOG.md entry proves an elementary zero-cofactor pruning
lemma: remove a block unused in the actual NS identity by setting its fresh
variables to zero everywhere, including later inputs and cofactors; clean up
zero input coordinates and blocks. Degree does not increase. This avoids
charging irrelevant spread blocks, but does **not** bound essential surviving
support. It is a clarification, not a substantive breakthrough.

Continue by exploiting the **actual balanced simulation certificate**, its
local derivations/cofactors, and richer PHP consequences. Check proposed charges
against the prefix-pebbling control and distinguish spread data from a proof.
Read exact relevant Chapter 7/8 proofs and BIKPRS pp. 28-31 when needed.

The ordinary-PHP to our exact polynomial-base bounded-depth proof transfer
remains to be formalized. Krajicek Lemma 5.1 includes functionality and is not
automatically that transfer. Final closure must cover every fixed p,ell,K.
No proof-size control for the local PC eliminations has been claimed or needed.
