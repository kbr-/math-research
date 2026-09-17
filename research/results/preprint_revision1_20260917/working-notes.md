# Working notes: preprint revision 1 (turn preprint_revision1_20260917)

State that must survive compaction. FEEDBACK.md ticks are the other persistent state.

- Read so far: whitepaper.tex, references.tex, sections 01-07, start of 08 (appendix).
- Rules from the user: no PDF build until all doable items are done; one commit at the end;
  tick items when done; skip items needing the user's input.
- Plan order: (1) literature verification by web search, (2) references + intro related work,
  (3) abstract/title/date, (4) overview section, (5) sections 2-6 exposition edits,
  (6) section 7 exponential corollary + generic section, (7) section 8 condensation,
  (8) commit hash, (9) build, (10) notebook entry, finish-turn, commit.

## Log
- Compaction happened after reading; Resume protocol redone (RESUME, COMPUTATION_RULES, living sections). Next: literature web checks.

## Literature verification (web, 17 Sept 2026)
- Khaniki, "On Proof Complexity of Resolution over Polynomial Calculus", ACM TOCL 23 (2022),
  doi 10.1145/3506702, ECCC TR20-034: almost quadratic dag-like lower bounds for
  Res(PC_d/F), F finite (includes Res(lin_F)), on mod q Tseitin (char != q) and random k-CNF;
  tree-like superpoly/exponential incl. PHP. EGI25 remarks its rule set differs. VERIFIED abstract.
- Part-Tzameret, "Resolution with Counting: Dag-Like Lower Bounds and Different Moduli",
  ITCS 2020 / Comput. Complexity 2021 (doi 10.1007/s00037-020-00202-x): first superpolynomial
  dag-like Res(lin_R) bounds; subset sum exponential over Q (large characteristic). VERIFIED.
  So the reader's recollection is right in substance: over Q (rationals), not mod 2.
- Alekseev-Itsykson STOC 2025 pp. 584-595 doi 10.1145/3717823.3718150 (lifting, regular/bounded depth). VERIFIED.
- Efremenko-Itsykson CCC 2025 LIPIcs 339 8:1-8:24 doi 10.4230/LIPIcs.CCC.2025.8 (amortized closure). VERIFIED.
- Gryaznov-Pudlak-Talebanfard CCC 2022 LIPIcs 234 4:1-4:16 doi 10.4230/LIPIcs.CCC.2022.4. VERIFIED.
- "Efremenko-Garlik-Itsykson 2026" NOT FOUND. Closest: Efremenko-Itsykson, "Strong ETH holds for
  bounded-depth Res(+)", STOC 2026 doi 10.1145/3798129.3800804, ECCC TR25-188. Cite that; tell user.
- From memory, not re-fetched (standard): Razborov 1998 CC 7:291-324; IPS 1999 CC 8:127-144;
  Alekhnovich-Razborov Proc. Steklov 242 (2003); Miksa-Nordstrom CCC 2015; Raz-Tzameret APAL 155 (2008).
  Flag for the author to double check page numbers.

## Edit plan decided after rereading (post-compaction)
- Lean links pin b47e9b1ef1f5b273822001983e83d35d7acbe117 (contains the five new modules).
- Title -> "An exponential lower bound ..."; Thm 1.1 = exponential (l>=32), Cor 1.2 = old 2^{Kl} form.
- New files: sections/01b-overview.tex (overview, terminology, parameters, worked example, why
  earlier approaches stall, scope), generic section inserted in 07 before the framework section.
- Rename registry slot count N -> N_reg (N stays unary columns).
- Strip "over any field"/"no finite-dimensional" remarks from 02,04,05,06; one remark in Sec 2.
- 8.3 -> one paragraph; story moved verbatim to DEVELOPMENT_HISTORY.md (+ version-1 source at b47e9b1).
- Worked example: resolve (u=1) with (u=0), h=1: P_A=1-ru, P_B=1-s(1-u); derivation of 1.
- DONE so far: whitepaper.tex (title/abstract/date/hash), 01 intro rewritten, 01b overview new, generality cleanup + N_reg in 02/04/05/06, intuition paragraphs 03/04/05/06, Thm 4.7 proof expanded. TODO: 07 (exp corollary proof, generic section, caveat consolidation, 8.3), references, README, DEVELOPMENT_HISTORY.md, FEEDBACK ticks, build, notebook entry.
- DONE: 07 (exp proof, generic section, 8.3 condensed), references, README verify section, DEVELOPMENT_HISTORY.md, novelty re-search 17 Sept (nothing found). TODO: FEEDBACK ticks, build+fix, notebook entry, living section sentence, finish-turn, commit.
