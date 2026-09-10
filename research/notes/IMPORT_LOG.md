# Import log

## Export state

The original TeX source, final PDF, eleven computation archives, and extracted archive contents are local. The Markdown conversion retained 68 proof blocks and all 14 labeled equation anchors; those are structural checks, not proof verification. Four direct mathematical references are listed. Their full texts are not locally cached in the export because direct downloads failed in that runtime.

The agent starting a new local session must fill the following coverage record. Do not copy export actions into a claim that the local session has read or verified the content.

## Local manuscript reading coverage

| File | Read ranges/sections | Complete? | Questions/findings |
|---|---|---|---|
| HANDOFF.md | Lines 1-437 | Yes | Complete entry point; scope and missing payoff retained. |
| manuscript/00_reading_guide.md | Lines 1-37 | Yes | Source hierarchy and degree convention retained. |
| manuscript/chapters/01_foundations.md | Lines 1-130 | Yes | Exact bases; NS/PC distinction; reuse, substitutions, selectors. |
| manuscript/chapters/02_graded.md | Lines 1-147 | Yes | Corrected Koszul range; generic witness limited to non-Boolean ring. |
| manuscript/chapters/03_reweighting.md | Lines 1-83 | Yes | Scalar repair and shared conditioning; no universal cheap weight. |
| manuscript/chapters/04_packing.md | Lines 1-99 | Yes | Packing degree and pointwise barriers; original degrees retained. |
| manuscript/chapters/05_baseaware.md | Lines 1-55 | Yes | Complete reread after combined tool output truncated an earlier view. |
| manuscript/chapters/06_moments.md | Lines 1-127 | Yes | Supported/mixed moment systems and their distinct scopes. |
| manuscript/chapters/07_elimination.md | Lines 1-111 | Yes | Prefix obstruction and additive PC elimination; selected TeX cross-check. |
| manuscript/chapters/08_batching.md | Lines 1-105 | Yes | Nested and core/residual proofs; selected original TeX cross-check. |
| manuscript/chapters/09_decomposition.md | Lines 1-118 | Yes | Exact static criterion; spread is extension data, not a refutation. |
| manuscript/chapters/10_route.md | Lines 1-103 | Yes | All three payoff hypotheses and fixed-prime/depth/exponent quantifiers. |
| manuscript/chapters/11_appendices.md | Lines 1-106 | Yes | Full corrections ledger, historical scopes, and budget/dependency map. |

## External references

| Citation key | Acquired source/version/hash | Extracted? | Read locations | Theorem/encoding match checked? |
|---|---|---|---|---|
| BIKPRS | User-supplied author-layout copy; hash in SOURCE_AUDIT.md | Yes | Definitions 6.1/6.4/6.5/6.8; Theorem 6.7(1) and construction excerpts | Simulation parameters and construction structure checked; no full-paper proof audit |
| Krajicek | arXiv:2301.10617v3; SHA-256 below | Yes | Full extracted text; PDF p. 10 visual | ENS syntax, ordinary-design deletion/residual match, simulation statement checked |
| Razborov | User-supplied published 1998 copy; hash in SOURCE_AUDIT.md | Yes | Definitions 2.1/2.4 and Theorem 3.1; PDF pp. 6-7 visual | PC degree convention, base deletion, residual matching checked |
| Pebbling | arXiv:2001.02481v1; SHA-256 below | Yes | Sections 2.1-2.2, Theorem 3.1, selected Section 4.2 statements | Encoding, field scope, c=1 graph parameters checked |

## Import report

Full local manuscript read; all four external papers acquired and extracted. See the detailed record below and MATHEMATICAL_CHECKPOINT.md. The two initially missing papers were supplied by the user; see the follow-up below.

## Local session import_20260910_01 (10 September 2026)

The full reading guide and all eleven chapters were read in bounded tool outputs.
The duplicate FULL_RESEARCH.md and optional manuscript PDF were not counted as
additional material. Reading is not a claim of independent verification of every
proof. The full claim index was read; claims.json was parsed to locate the central
proofs and their listed dependencies (74 records, 68 proof blocks). Selected
original TeX was checked for reuse/substitution, field identities, additive
elimination, and core/residual absorption. The JSON dependency lists are extracted
cross-references, not necessarily exhaustive mathematical dependencies.

The local AGENTS.md, status/audit ledger, timing instructions, reference README
and manifest, checks/README.md, and A09/A10/A11 scope READMEs were read. No
historical computation suite was run. File-integrity verification passed for all
117 checked files and all eleven original ZIPs, with seven mutable files skipped.

### Acquisition and extraction

- Krajicek: downloaded https://arxiv.org/pdf/2301.10617v3; pinned v3,
  27 September 2023. PDF SHA-256:
  `7b867671d32383351116da27533f0691bd4237607084ed5b36329d399021d886`.
  Extracted successfully with pdftotext -layout. All 702 extracted-text lines
  were read; the PHP equations on PDF page 10 were also inspected visually.
- Pebbling: downloaded https://arxiv.org/pdf/2001.02481. The retrieved paper is
  arXiv:2001.02481v1 (8 January 2020); the title page says 9 January 2020 and
  identifies the CCC 2019 preliminary version. PDF SHA-256:
  `28b92f864587723e8c580e46d3db27f7da2096b963253790e64dc0575a64c655`.
  Extracted successfully with pdftotext -layout. Read lines 1-75, 250-415,
  645-707, and 750-785: preliminaries/encoding, Theorem 3.1, and relevant
  Carlson–Savage definitions and parameter statements. No full-paper read claimed.
- BIKPRS: publisher endpoint returned HTML, not a PDF. Buss's public author copy
  was located, but retrieval failed TLS verification even with the existing
  system CA bundle explicitly selected. No certificate verification was disabled.
  The original Theorem 6.7(1) has NOT yet been read. Requested BIKPRS.pdf from user.
- Razborov: publisher endpoint returned HTML. The author-index retrieval failed
  TLS verification, including the CA-bundle retry. No original lower-bound
  statement or proof has yet been read. Requested Razborov.pdf from user.

All download attempts are preserved in references/import_status.json and
references/author_source_import.json (with earlier import records nested where
applicable), plus the timed command outputs. The original reference manifest was
not edited. Browser lookups also encountered timeouts/cache misses. After the
user offered help, further download retries were stopped.

### Source-level findings

1. Krajicek Definition 2.1 (PDF pp. 3-4) matches all companions, shared fresh
   variables within one block, disjointness between same-level blocks, dependence
   on earlier levels, and field-valued extension variables with r^p-r equations.
2. Krajicek p. 10 explicitly includes column exclusions, same-row exclusions,
   row sums 1-sum_j x_ij, and Boolean equations. Deleting same-row exclusions and
   changing row-generator signs leaves exactly our base F_n. Lemma 4.1 and the
   following restrictions paragraph (p. 11) therefore give the required ordinary
   designs, also on residual boards, by axiom deletion. This checks the design
   input; it does not replace a PC-degree lower bound.
3. The displayed Boolean-axiom redundancy identity on p. 10 has a sign typo at
   odd primes: with the printed Q_i=1-sum_j x_ij and Q_{i;j,k}=x_ij x_ik, the
   correct identity is x_ij^2-x_ij = -x_ij Q_i - sum_{k!=j} Q_{i;j,k}.
   The printed plus sign produces an extra twice-the-row-cross-products term.
   Boolean axioms are explicitly included in the source system, so this typo
   does not obstruct the deletion argument or change our base.
4. Krajicek Theorem 5.2 (p. 13) explicitly cites BIKPRS Theorem 6.7(1), supplies
   polynomially many companions, level bound ell+O(1), arbitrary accuracy h>=1,
   and degree (O(1)+log k)(h+1)^{O(ell)}. Its preceding paragraph describes
   bottom-up disjunction approximation. It supplies no bound on chain covers,
   residual ranks, or essential certificate-cofactor support. The original
   construction and its cofactors remain to be inspected in BIKPRS.
5. Krajicek Lemma 5.1 concerns a formulation that includes row functionality.
   It does not by itself discharge the ordinary-PHP to our weaker polynomial
   base proof-transfer obligation. The direction and exact formulas still matter.
6. Pebbling equations (2.5)-(2.6), with Boolean axioms, match F_G exactly up to
   harmless signs. Theorem 3.1 is explicitly over any field and identifies NS
   degree with reversible pebbling space. Definition 4.7 and Lemma 4.9 give
   Gamma(c,r), size Theta(c r^3+c^2 r^2), indegree at most two, and standard
   price r+2. Choosing c=1 gives a single-sink family of size Theta(r^3), whose
   reversible price is at least r+2. This verifies the parameter input used for
   the generic-batching obstruction; no new finite computation is needed.

### Timing scope

Instrumentation started after the initial handoff/instructions/tool inspection.
That initial reading is therefore outside the measured interval. Reading phases
include interpretation; early web lookups and some command orchestration were
mixed with reading/preparation before explicit network-phase bracketing. Timed
subprocess runs include failures. Neither pure reasoning time nor pure network
latency is claimed. See logs/import_20260910_01.jsonl and its final summary.


## Follow-up: reference_finish_20260910_01 and workspace separation

The user supplied both missing PDFs in php_codex_handoff/cache/. They were
located, copied to the working reference cache, extracted, and checked at the
targeted source locations. No further network requests were made. The failed
first extraction command (before locating the files in that alternate directory)
is included in timing. See SOURCE_AUDIT.md for version identification, hashes,
exact reading ranges, the original simulation structure, and the PC-degree bridge.
The imported premise of affine rigidity is now matched; final elimination and
ordinary-PHP proof transfer remain open.

At the user's request, all post-handoff artifacts were moved to research/.
The four modified historical files were restored from php_codex_handoff.zip,
and all 128 original package files were verified byte-for-byte. New tools,
notes, logs, cached PDFs, extracted text, user-supplied originals, and rendered
inspection pages are outside the handoff. Current helpers write only in research/.
Earlier log paths record where commands actually ran and were not falsified.
The preceding initial-import section is historical: its pending-file statements
have been resolved by this follow-up. Use RESUME.md after compaction; do not
repeat the manuscript import.
