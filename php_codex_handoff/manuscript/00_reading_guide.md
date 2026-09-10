# How to read this record

This is a mathematical consolidation, not a transcript and not a claim that the payoff has been achieved. It begins with the independent work undertaken after the initial uploaded research report. The report's older assertions are not silently imported as theorems; the corrections and changes of direction relevant to this conversation are recorded in Appendix [Chapter A](chapters/11_appendices.md#app-ledger).

Each lemma supplies its assumptions and a proof of the claim made here. Repeated arguments have been factored into reusable preliminary lemmas; references between chapters are internal to this document. Results inherited from the literature are explicitly marked *Imported input*. Their original proofs are not reproduced or claimed as our work. Statements involving the published PHP lower bound are conditional on the encoding match spelled out in Chapter [Chapter 10](chapters/10_route.md#ch-route).

**Status convention.** Unless marked imported or open, the results below are the *working derivations obtained in the conversation*. Typesetting them as lemmas records their mathematical content; it does not certify novelty, independent verification, or a machine-checked general proof. A complete audit of the proof transformations remains an explicit obligation. The computational supplements establish only the finite checks described in their scope notes.

**Three separations matter throughout.** The non-Boolean graded ring $\overline B$ is not the Boolean PHP ring. A design annihilating bounded-degree original-axiom multiples need not annihilate all bounded-degree polynomial-calculus consequences. Finally, generic linear restrictions are not the full leveled extension systems produced by a Frege simulation. None of these distinctions is erased by the notation.

**Degree convention.** An extension axiom retains its original degree in old and new variables. Specialization or Boolean reduction may lower the degree of its image, but does not retroactively enlarge the set of allowed multipliers in the original degree-$D$ design. Zero polynomials are omitted wherever a degree is used.

**Editorial changes.** Definitions, finite-dimensional duality, and degree-nonincreasing reductions are made explicit so the proofs can be followed without earlier messages. Conservative versus sharper degree bounds are identified. No missing global compatibility or simulation-transfer theorem has been supplied by assumption without being labeled.

# The argument at a glance {#the-argument-at-a-glance .unnumbered}

  Branch                 Endpoint and limitation
  ---------------------- ---------------------------------------------------------------------------------------------------------------------------------------------------------------
  Graded algebra         Koszul vanishing and the initial Hilbert function hold in the proved range $2d-1\le n$. The originally proposed range $d<n$ is false.
  Generic restrictions   A determinant functional survives $t$ generic restrictions when $t+2d-1\le n$. This concerns the non-Boolean ring only.
  Exact liftings         Reweighting, factor packing, shared conditioning, base-aware substitutions, and supported moment corrections give explicit constructions with stated budgets.
  PC elimination         Blocks can be eliminated at additive degree cost. Equal spans, nested spans, and nested cores with low-rank residuals can be batched more cheaply.
  Decomposition          For affine data the current cost criterion is exactly optimizable. There are polynomial-size admissible families whose optimum still exceeds $n/2$.
  Remaining theorem      Use the actual translated Nullstellensatz refutation and PHP structure to obtain a base PC refutation below the available linear-degree threshold.

# Notation quick reference {#notation-quick-reference .unnumbered}

  ------------------ --------------------------------------------------------------------
  $\overline B$      Non-Boolean column-exclusive ring with equal row sums.
  $\mathcal F_n$     Boolean linear-row PHP axioms, without row exclusion.
  $\mathcal I_D$     Span of original-axiom multiples of total degree at most $D$.
  $\mathcal C_D$     Polynomial-calculus consequences derivable within degree $D$.
  $h,\ \delta,\ D$   Extension accuracy, maximum input degree, and target proof degree.
  $B,\ T$            Required base degree and polynomial-substitution degree inflation.
  ------------------ --------------------------------------------------------------------

**Reading paths.** Chapters 1--2 contain the graded-algebra branch. Chapters 3--6 develop explicit functionals and their limitations. Chapters 7--9 give the current proof-elimination route and its decomposition obstruction. Chapter 10 states the remaining goal and risk-ordered proof obligations; Appendix C provides a compact budget reference.
