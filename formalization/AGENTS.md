# Formalization workflow

Follow the root AGENTS.md opt-in assignment, index maintenance contract, and
research-record policy. Setup and verification commands live in [README.md](README.md);
[COMPUTATION_RULES.md](../COMPUTATION_RULES.md) owns execution and timing.
Use its `formalization` phase and `formal_verification` command category within
the active research session; developing a new mathematical argument remains
`mathematics` under that policy.

Choose a claim directory by the provenance of its individual statement, not
the ancestry of the final theorem: `third-party-claims/` for attributable
literature results, including faithful reformulations and specializations;
`claims/` for project-formulated supporting interfaces or independently
developed generalizations. Preserve source attribution and index every new
mathematical claim. A more general statement alone does not establish novelty,
and a new proof does not transfer authorship of the theorem. Describe adaptations
as such without unsupported novelty claims. The two directories may import each
other without cycles. An unproved target may be a proposition definition in an
explicitly marked interface module, never an axiom or `sorry`. Follow README.md's
metadata convention; file role does not establish claim completion.

- Before proving anything, read the exact indexed claim and relevant proof.
  Draft the Lean statement and compare its variables, domains, quantifiers,
  hypotheses, conclusions, and degree conventions with the notebook. In
  particular, distinguish joint total degree from degree in one variable.
  Distinguish exact values and identities from bounds, approximations, and
  bookkeeping conventions. At each use, check that the available relation
  implies the required conclusion in the correct direction; a valid upper
  bound cannot automatically replace an exact value.
  Before the general proof, inspect relevant boundary
  cases such as constant or zero inputs, empty index sets, and loose parameter
  bounds; these can expose missing hypotheses without substantial computation.
  Record the intended coverage and any differences in the claim-file header.
  Before proof-writing, record a short dependency-and-scope map: the target's
  conclusions, required supporting claims, existing Lean/Mathlib coverage, and
  separately indexed downstream results outside the assignment. Keep it with
  the turn's supporting evidence and reflect the final scope in the research
  record; do not create another live status tracker.
- If the source statement fails, formalize the valid portion and state the
  correction explicitly, with a counterexample to the false portion when
  possible. Preserve the earlier record under the root correction policy.
  Audit the nearest downstream uses within a stated scope, distinguishing
  affected inferences from uses protected by stronger hypotheses. Do not infer
  either global failure or global safety from a bounded audit.
- Maintain the notebook's **Gaps identified by formalization** section in place
  after each formalization cycle. Keep a concise list of links to the entries
  establishing mathematical discrepancies, with brief current correction or
  audit status and relevant follow-up links. Update or retire resolved items
  while preserving their full history in the Research record. Do not duplicate
  proofs there or list a claim merely because it is unformalized; Lean setup
  errors are not mathematical gaps. This section is read by both research and
  formalization agents during resume. In parallel work, follow the root
  coordinator-ownership policy for all living sections.
- Formalize the claim, not necessarily the original proof strategy. Prefer
  explicit constructions when they simplify both the identity and its bounds;
  the first interpolation proof used a recursive quotient instead of division.
  When the proof differs from the informal source, include the complete
  human-readable alternative argument, with hypotheses and degree accounting,
  in the research-record entry introducing the formalization. A Lean source
  link or a description of the proof strategy alone is insufficient.
  Useful generalizations are welcome: choose broader domains, parameters, or
  reusable interfaces when they improve the mathematics or its formalization.
  The requested claim is a required application, not a ceiling on generality.
  Verify that the generalized statement recovers the entire requested claim,
  keep necessary hypotheses explicit, and record its broader scope and proof.
  Distinguish a proved generalization from dropping an assumption without proof;
  defer extensions that would distract from completing the assigned route.
  When a reusable dependency makes a claim's formalization clearer, give it a
  separate Lean file and claim-index entry, with its full human-readable proof
  in the introducing research record. Keep small local helpers in the target
  file unless separating them has a concrete benefit.
- Search the pinned local Mathlib sources for definitions and theorem names
  before guessing APIs or fetching additional modules. Keep imports targeted.
  Give module-level helpers and instances unique qualified names so independently
  checked modules import together; `local instance` restricts visibility, not
  the declaration's global name.
  Separate library setup, elaboration, and syntax failures from mathematical
  gaps in the record. `noncomputable` can be appropriate for abstract Mathlib
  objects; it changes executable code generation, not the proof obligation.
- Use the verification command and evidence options documented in README.md.
  After verification passes, make one focused review of the printed theorem
  types against the informal claim, including implicit assumptions and any
  strengthened hypotheses. Check that the header lists every result being
  claimed. The verifier checks the listed declarations and their axioms; it
  cannot certify statement fidelity or declaration-list completeness.
- Preserve exact verified scope in the notebook and claim index under the root
  policy. Mark an indexed claim formalized only when its entire statement and
  all dependencies needed by its formal proof are covered by checked Lean
  proofs, including dependencies of dependencies. Existing Mathlib proofs may
  supply these dependencies; otherwise formalize them. Do not replace an
  unproved dependency with an axiom or an extra hypothesis and call the original
  claim formalized. A different proof may remove an original dependency, but
  must still prove the full statement and satisfy the alternative-proof record
  rule above. Separately indexed downstream corollaries are separate targets,
  not unfinished dependencies of the claim they use. Treat setup success,
  partial or conditional verification, and full formalization as different
  outcomes. Let concrete friction from subsequent claims justify
  further infrastructure; do not add machinery merely to anticipate it.
