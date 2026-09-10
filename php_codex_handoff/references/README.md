# Direct mathematical references to import

These are the **four entries in the current compendium's bibliography**, with the same citation keys. This list does not import every older citation from the superseded initial report or recursively expand all four bibliographies. All source-specific mathematical assertions remain attributed/conditional exactly as in the compendium.

No full external paper was successfully downloaded into this export. Direct network downloads failed in the runtime; the manifest contains public download candidates, not claims that those candidates were fetched. Web reading of source records is distinct from possession of local files. `import_status.json` records the export state; the importer updates it with actual local outcomes.

Run:

```bash
python tools/import_references.py --list
python tools/import_references.py --fetch --extract
```

A missing PDF, blocked publisher response, wrong content type, and failed extraction are distinct statuses. The importer does not bypass paywalls, logins, captchas, or access controls. If a publisher candidate is unavailable, use an openly supplied author copy or a legitimately obtained local copy and record its origin/version in the manifest/status. Do not mistake a title-matching alternative paper for the cited theorem.

## BIKPRS

**S. R. Buss, R. Impagliazzo, J. Krajíček, P. Pudlák, A. A. Razborov, J. Sgall.** *Proof complexity in algebraic systems and bounded depth Frege systems with modular counting.* Computational Complexity 6(3), 256–298, 1996/1997 (year convention preserved from the manuscript).

Canonical record: <https://doi.org/10.1007/BF01294258>.

**Use in this project:** the original bounded-depth modular Frege-to-ENS simulation. The manuscript cites its needed statement through Krajíček's Theorem 5.2. Verify the actual original theorem/section during import rather than guessing a theorem number. Trace the encoding, block construction, accuracy, level count, and degree factors. The handoff does not infer a cheap static decomposition from the simulation.

## Krajicek

**Jan Krajíček.** *Extended Nullstellensatz proof systems.* arXiv:2301.10617v3, 2023. Pinned version: **v3, 27 September 2023**.

Record: <https://arxiv.org/abs/2301.10617v3>.  
Math-readable HTML: <https://arxiv.org/html/2301.10617v3>.  
PDF: <https://arxiv.org/pdf/2301.10617v3>.

**Import targets:** Definition 2.1 (ENS companions, freshness, levels, field equations); Lemma 4.1 (the exact PHP system/design statement); Theorem 5.2 (simulation and parameters). Section 3 gives pseudo-solutions and conflict-pair context, but do not promote any candidate property there into a theorem without reading it. The source's system may include extra row exclusions; match equations explicitly.

This version and the above named locations are the ones cited in the manuscript. Downloading a later revision must be recorded as a distinct version comparison.

## Razborov

**Alexander A. Razborov.** *Lower bounds for the polynomial calculus.* Computational Complexity 7, 291–324, 1998.

Canonical record: <https://doi.org/10.1007/s000370050013>.

**Import targets:** the algebraic-PHP PC degree lower bound, its exact axioms and field hypotheses, and the form applying to residual boards after partial matchings. The compendium records a threshold of at least $n/2+1$ over every field, but keeps the exact encoding match as an application obligation. Do not substitute the later “Non-Binomial Case” paper for this reference.

## Pebbling

**Susanna F. de Rezende, Or Meir, Jakob Nordström, Robert Robere.** *Nullstellensatz Size-Degree Trade-offs from Reversible Pebbling.* arXiv:2001.02481; preliminary version CCC 2019 (as recorded in the source bibliography).

Record: <https://arxiv.org/abs/2001.02481>.  
Math-readable HTML: <https://arxiv.org/html/2001.02481>.  
PDF: <https://arxiv.org/pdf/2001.02481>.

**Import targets:** Theorem 3.1 (NS degree versus reversible pebbling, exact encoding and field scope); Carlson–Savage graph discussion and the stated single-sink parameterization used in the compendium. The arXiv ID was not version-pinned in the manuscript; record the actual revision fetched.

**Use in this project:** calibrate the counterexample to generic cheap batching from ordinary designs. The explicit prefix certificate is in our Lemma 7.1; the external graph lower bound is imported, not proved in the handoff.

## Import/audit record

The manifest contains `reading_targets` and `audit_questions`. The importer only acquires files and optionally extracts text; it cannot certify that a mathematical match has been checked. Enter theorem-level findings and coverage in `notes/IMPORT_LOG.md`.

For paper equations, extracted PDF text is a search aid, not an authority for lost superscripts or formulas. Prefer original TeX or math-readable HTML where available, or inspect the relevant PDF pages. Do not use OCR by default.

External papers retain their own copyright/license terms. This bundle contains their bibliographic metadata and acquisition tools, not a redistribution license.
