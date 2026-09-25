# TODO

## Lean pass for the next revision (not started)

Do this only when the author asks, after the new material is in the sources. References are to
D. Menezes, arXiv:2609.19009 v1.

- [ ] F = g_{2^(n−1)} and F² = g_{2^n} (cheap: multiplicity Schwartz–Zippel is already formalized).
- [ ] The reduction lemma (Lemma 2.2), over F₂ at least: every Q has a k-reduced P with
  deg P ≤ deg Q, order ≥ k of Q − P at the nonzero cube points and ≥ k − 1 at the origin
  (≥ k when deg Q ≤ n + 2k − 3).
- [ ] Hasse interpolation (Lemma 2.3), with the monomial count dim U_k of Sauermann–Wigderson
  (Claim 2.2): the largest piece.
- [ ] The Catalan basis (Theorem 4.1, parts 1–2): the G_{k,d}, |d| ≤ k − 2, form a basis of V_k,
  with ord₀ P = min{|d| : c_d ≠ 0}.
- [ ] The block identity and the Section 4 lower bound through the Catalan basis, including the
  case ℓ = k − 1.
- [ ] Replace each `% TODO Lean` in the sources with a `\lean{...}` link at the new pinned commit,
  and update Appendix B.
