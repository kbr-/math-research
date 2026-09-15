# R12: ordinary compact decoder

Target: extract the paper's full degree-preserving old-base transfer lemma,
including arbitrary PC consequences, exact original axiom-image budgets,
ordinary polynomial injectivity, and degree preservation. ℓ≥2 for axiom-image
transfer; arbitrary m rows is harmless and includes the paper m=2^ℓ+1.
Use the R01 Fin m×Fin(2^ℓ) unary ring and Fin m×Finℓ bit ring. A concrete
finite equivalence identifies unary columns with F2 bit labels.

Construct a polynomial left inverse to the decoder using unit-vector columns.
Both directions are linear substitutions, giving exact ordinary degree and
injectivity without an abstract coordinate-completion dependency. Prove Boolean
images at degree2 and collision images at degreeℓ using R11 and column exclusions.
Prove original bit axiom degrees explicitly, so eligible axiom images can be
replayed at every original proof ceiling B, including small B.

Dependencies R01–R05, R11 and its generic pair certificate, pinned finite type
and polynomial Mathlib APIs. Excluded: transported filtration J, compact-base
lower bounds, matching stability, source ENS families. Preliminary source/API
reading and broad proof planning preceded instrumentation.
