# R05 degree-accounting argument (proof design, pending Lean verification)

Write M_S=∏_{i∈S}X_i and X^d=∏_{i∈supp(d)}X_i^{d_i}. Define red(P)=Σ_{d∈supp(P)} coeff_d(P) M_supp(d).

For n≥1, X_i^n−X_i is in the Boolean NS space through n. The n=1 case is zero; for n+1≥2 use
X_i^(n+1)−X_i = X_i^(n−1)(X_i²−X_i)+(X_i^n−X_i).
The new generator multiple has ordinary degree≤n+1, and the earlier certificate embeds monotonically. For a finite set S of positive exponents, induct on S using
AB−ab=A(B−b)+(A−a)b,
where A=X_i^d_i, a=X_i, B=∏_{j∈S}X_j^d_j, b=M_S.
The first summand has NS cost≤Σ_{j∈S}d_j+d_i. The second has cost≤d_i+|S|≤d_i+Σ_{j∈S}d_j. Thus X^d−M_supp(d) has cost at most Σ_i d_i. Scalar combination over P.support gives P−red(P) in NS_degP because each supported monomial has degree≤degP. No degree is reduced silently in the witnesses.

Each M_S has individual degrees≤1 and total degree|S|. Since every support exponent is positive, |supp(d)|≤Σ_i d_i, so red(P) has total degree≤degP. At any F2 point, each positive power x^n equals x, hence red(P) and P agree pointwise.

For the zero-remainder step Lean may reuse Mathlib's finite-field evaluation injectivity. A human-readable argument matching that library route is: the squarefree polynomial space has basis indexed by subsets of the v variables, hence dimension2^v. The space of functions on F2^v also has dimension2^v. Evaluation is onto because each point a has its squarefree indicator δ_a(X)=∏_{a_i=0}(1−X_i)∏_{a_i=1}X_i. Thus evaluation is an isomorphism and a zero-evaluating squarefree polynomial is zero. This covers v=0: both spaces are one-dimensional and the unique indicator is1.

If P vanishes everywhere, red(P)=0 and the certificate becomes a certificate for P itself. Finally every F2 value z satisfies z²=z, so q²−q vanishes everywhere. Its ordinary total degree is≤2degq (including constants and q=0), giving the required Boolean certificate. Under an external ceiling d≥degP or k≥degq, use NS monotonicity to obtain the displayed source bounds d or2k.
