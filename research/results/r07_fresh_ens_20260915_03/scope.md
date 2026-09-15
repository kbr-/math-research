# Canonical fresh ENS block and scalar cleanup

Remaining R07: exact factor/product/companion degrees and scalar elimination.
Use variables sigma ⊕ (Fin h × iota); ordinary old inputs are renamed through
Sum.inl, and every coefficient is its own Sum.inr variable. Registry users
embed/rename this whole type. Prove rename naturality and degree preservation
for injective embeddings, not a duplicate family-specific block definition.

Over any field, when all input degrees are <=1 and a selected input has exact
degree1, every factor has exact degree2. Specialize all coefficients but its
selected slot to zero to obtain 1-r*g, whose degree is exactly2. Linear
substitution bounds the original degree from below; the explicit expression
bounds it above. Products have exact2h by the domain law and nonzero factors;
nonzero proper companions then have exact2h+1. h=0 has empty product1 and
companiondegree1 and must remain included in degree statements.

Scalar cleanup is binary (or requires scalar-domain certificates): over F2,
constants satisfy c^2=c. Zero inputs permit all coefficients0. A unit span
requires h>=1; put a unit combination in row0 and zero in other rows, giving
product0 and all companion/Boolean coefficient images0. Ordinary old variables
are untouched. Apply the verified PC substitution theorem with degree bound1
and discard zero images, retaining the original PC ceiling.

These helpers are extracted from the paper's scalar cleanup argument, not the
larger affine exclusion theorem. No novelty claim. Keep exact original degrees
separate from upper ceilings and record all checks under this cycle.
