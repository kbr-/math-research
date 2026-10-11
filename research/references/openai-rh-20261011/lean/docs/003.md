# The quasi-Riemann hypothesis

The following describes the scope of the Lean formalization related to the following accompanying paper(s):

- [The Quasi-Riemann Hypothesis: A Zero-Free Half-Plane $\Re(s)>7/8$](../../preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/paper.pdf)
- [Uniform exclusion of Landau–Siegel zeros](../../preprints/Uniform-exclusion-of-Landau-Siegel-zeros-October-1-2026/paper.pdf)

## Scope

The quasi-Riemann hypothesis asks for a fixed zero-free half-plane $\Re s>\theta$ with $\theta<1$. The formalization gives $\theta=7/8$ for the Riemann zeta function and every Dirichlet $L$-function, uniformly over all positive moduli and all characters. It also establishes the same bound for finite-order Hecke $L$-functions over $\mathbb Q(\sqrt{-3})$.

The principal-character poles at $s=1$ are excluded in the Dirichlet and Hecke statements. The paper's later applications are not included.

The formalized result gives a uniform logarithmic exclusion region for Landau–Siegel zeros. There is one constant $c>0$ such that every primitive nonprincipal real Dirichlet character of conductor $q\ge3$ and every real zero $0<\beta<1$ of its $L$-function satisfy $1-\beta\ge c/\log q$.

Both character parities are included. No explicit value of $c$ is given. This excludes real zeros in $1-c/\log q<\beta<1$, but does not rule out real zeros elsewhere in $(0,1)$.

## Comparator links

| Result | Comparator statement |
| --- | --- |
| Riemann zeta $7/8$ bound | [QuasiRiemannHypothesis.lean](../ComparatorChallenges/QuasiRiemannHypothesis.lean) |
| Dirichlet $L$-function $7/8$ bound | [DirichletSevenEighths.lean](../ComparatorChallenges/DirichletSevenEighths.lean) |
| Finite-order Hecke $L$-function $7/8$ bound | [HeckeSevenEighths.lean](../ComparatorChallenges/HeckeSevenEighths.lean) |
| Uniform real-zero gap | [SiegelZeros.lean](../ComparatorChallenges/SiegelZeros.lean) |
