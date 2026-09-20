# Preprint self-review checklist

Reusable lessons from the [bit-PHP feedback](bit-php-resolution-over-parities/FEEDBACK.md),
including subsequent author and expert guidance. This is a review template, not
a declaration that any paper has passed. Record findings and dispositions in the
paper's own `FEEDBACK.md` or readiness audit; keep this shared checklist reusable.

Scale the review to the paper. A short observation need not acquire a two-page
overview, a parameter table, an appendix or a formalization merely to tick boxes.
Mark an item not applicable with a brief reason when appropriate. Reviewer
suggestions are inputs to judgment: check their factual premises and preserve
explicit author decisions unless the author changes them.

## 1. Main claim and scope

- [ ] **State the contribution precisely.** Make the main result easy to find in
  the title, abstract and introduction. Distinguish a new theorem, a new proof,
  an application of a known result, and an observation connecting existing work.
- [ ] **Match every headline to the theorem.** Check all quantifiers, domains,
  encodings, inference rules, size measures and restrictions. Define what is
  counted, including initial proof-lines when relevant. Explain which restrictions
  are absent rather than relying on an unexplained adjective such as “general.”
- [ ] **Make quantitative language unambiguous.** Give the actual bound and its
  parameter. Relate different size parameters explicitly; qualify terms such as
  “exponential” where conventions differ. Recheck abstract asymptotics after
  changing parameters or strengthening a theorem.
- [ ] **Separate sufficient criteria from general characterizations.** Preserve
  density factors, side conditions and unproved premises. Do not rename a
  sufficient condition as a size–degree relation, equivalence or general method
  unless that stronger assertion is proved.
- [ ] **State the boundary once, where useful.** Explain the important conclusions
  that do not follow. Keep a caveat next to a statement if omitting it would
  mislead; consolidate repeated scope and novelty disclaimers elsewhere.

## 2. Attribution and literature

- [ ] **Trace both the subject and the proof ingredients.** Credit the introduction
  of a system or method separately from later variants and lower bounds. Cite
  antecedents of intermediate results even when giving a self-contained proof.
- [ ] **Verify references against primary sources.** Check authors, titles, years,
  journal details, page ranges, identifiers and theorem numbers. Do not retain
  bibliographic details from memory or a reviewer's illustrative citation.
- [ ] **Use the right version.** Check revisions and corrections. Identify the
  version when numbering or statements differ, especially for a question the
  paper claims to answer.
- [ ] **Compare like with like.** Align fields, encodings, proof systems, rules,
  regularity/depth hypotheses and size parameters before comparing bounds.
  Explain why the closest prior result does not already imply the claim.
- [ ] **Qualify novelty honestly.** Distinguish established prior work from a
  potentially new formulation or proof. A bounded search with no match does not
  establish priority. Attribute reviewer opinions as opinions, not literature facts.
- [ ] **Check the relevant recent work.** Give the actual scope and date of any
  literature refresh. Do not carry forward a stale date or imply an exhaustive
  review. Use a comparison table only if verified rows improve on the prose.

## 3. Exposition for human readers

- [ ] **Write the abstract in the area's vocabulary.** State the problem, exact
  result and central idea plainly. Mention formal verification accurately when
  it is part of the contribution; keep process history and repeated review-status
  notices out of the abstract.
- [ ] **Explain the proof before its machinery.** For a substantial argument, give
  a readable overview of the main steps, why they fit together and where the hard
  step lies. For a short deduction, a clear introductory paragraph may suffice.
- [ ] **Expose the conceptual center.** Name the decisive construction, invariant
  or bridge, explain why it works, and point directly to the supporting lemma.
  Distinguish nearby notions that the argument cannot interchange, such as
  equality of formal polynomials and equality of their values on a finite set.
- [ ] **Help readers enter the main statements.** Introduce important theorems
  with their purpose and intuition. Explain what their hypotheses accomplish.
  Expand terse nontrivial transitions rather than merely adding more references.
- [ ] **Make the proof's structure visible.** Separate genuinely different cases;
  retain boundary and degenerate cases. Present a key chain of estimates together
  when that makes its logic easier to check.
- [ ] **Use an example when it earns its space.** A small worked instance should
  explain a mechanism, translation or construction that is otherwise hard to
  follow. Do not add examples as decoration or substitute them for a proof.
- [ ] **Explain the relation to previous methods.** Identify the obstacle being
  bypassed and the borrowed ideas. Verify characterizations of others' methods;
  do not portray an unverified interpretation as an established limitation.
- [ ] **Keep useful generality; move incidental generality aside.** The main
  argument should follow the setting readers need. Put optional abstractions in
  a remark or a skippable section, with their full hypotheses. Formal-library
  generality alone is not a reason to complicate the exposition.
- [ ] **Keep supporting detail proportionate.** Retain appendices that supply
  genuinely useful proofs or verification information. Remove repetitive
  summaries and duplicated lemmas rather than cutting essential arguments.

## 4. Terminology, notation and layout

- [ ] **Prefer accepted terminology.** In proof complexity use “proof-lines” or
  “lines” for proof size, with the exact counting convention stated. Reserve
  “nodes” for genuinely graph-theoretic descriptions. Define necessary project
  vocabulary once and connect it to standard terms; formal declaration names
  need not dictate the paper's prose.
- [ ] **Resolve overloaded symbols.** A symbol should not silently change meaning.
  Where parameters are numerous, provide one compact summary of their meanings,
  dependencies and where the main inequalities are used.
- [ ] **Make tables readable.** Use adequate row spacing or restrained horizontal
  rules, sensible column widths and alignment. Check the rendered table, including
  long explanations; do not duplicate a glossary or table without a reader benefit.
- [ ] **Use navigable references.** Use LaTeX labels instead of hard-coded section
  numbers. Verify cross-references after reorganization. Keep long implementation
  names and repository paths out of the proof narrative.

## 5. Mathematical and formal-verification evidence

- [ ] **Review the exact dependency chain.** Check that every invoked result has
  the required hypotheses and that every conversion preserves the claimed
  object and parameter budget. Retain original degree/cost conventions where
  simplification would otherwise conceal a loss.
- [ ] **Use meaningful controls where warranted.** Known easy instances and edge
  cases can reveal a definition, scope or interpretation mistake. Describe what
  a check establishes; one toy example is not a survey of known upper bounds.
- [ ] **Separate evidence types.** Distinguish an informal proof, finite check,
  AI review, independent expert review and formal verification. Reused archived
  evidence is not a fresh run. Verification does not establish novelty or the
  correctness of the correspondence between formal and conventional definitions.
- [ ] **If formalized, verify the actual headline.** Match the paper's definitions,
  rules, hypotheses and quantifiers to the declarations. Explain partial coverage,
  stronger assumptions, or informal additions. Audit transitive dependencies and
  distinguish proved prerequisites from custom axioms or admitted interfaces.
- [ ] **If formalized, provide a compact verification map.** Link paper statements
  to immutable source files, exact declarations and verified scope. Check names
  against the source. Keep the map outside the main mathematical narrative.
- [ ] **If formalized, make reproduction self-contained.** Include in the paper or
  appendix the repository, immutable checkout, prerequisites, commands, expected
  axiom output and applicable kernel-replay instructions. Ensure the pinned
  revision actually contains the aggregate verification module and all cited files.
  A repository README is helpful but cannot replace reader-facing instructions.
- [ ] **Represent independent validation accurately.** Record which external
  definition checks or independent builds have occurred and which remain pending.
  Formalization is conditional here, not a new requirement for every paper.

## 6. Assistance, versions and final checks

- [ ] **Disclose assistance specifically and concisely.** Identify substantial AI
  contributions to mathematical development, literature work, drafting, review
  and formalization, as applicable. Distinguish AI feedback from human review.
  Describe the author's contribution and actual checking honestly, including
  reliance on formal verification where relevant; do not imply checks not done.
- [ ] **Keep development history separate.** Move subscription stories, prompt
  history and model anecdotes to a durably linked history document. Keep only
  the concise disclosure and methodological context needed to understand the paper.
- [ ] **Make revision identity clear.** Include a date and version marker; add
  report identifiers only when assigned. Identify substantive changes and error
  corrections explicitly, and keep cited verification revisions consistent.
- [ ] **Keep the submitted document sufficient for its readers.** Necessary
  explanations, qualifications and verification guidance belong in the paper or
  its appendices. Repository documentation may support it, but there is no assumed
  supplementary README.
- [ ] **Check the finished artifact.** Complete source edits before the final build,
  then check the PDF for legibility, page breaks, equations, tables, links and
  references. Correct warnings or document their harmless scope; verify that the
  retained source and PDF agree and preserve the actual build/review evidence.
- [ ] **Close the review honestly.** In the paper-specific feedback record,
  distinguish applied, already satisfied, declined, not applicable and outstanding
  items. A checked box must not imply that an expert opinion was verified or an
  external action occurred. Release identifiers, hosted CI and publication claims
  must refer to things that actually exist; follow the root Git/publication policy.
