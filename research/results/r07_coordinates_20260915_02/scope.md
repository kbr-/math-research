# R07 affine coordinates

Continue R07/R08/R16 after affine-system witness release. This cycle targets
full affine coordinate completion and free-coordinate parametrization only.
Fresh-companion degree and scalar cleanup remain separate next obligations.

Given an independent finite family of affine forms with proper span, extend
its independent linear functionals to a dual basis. Reindex the completed
basis by Fin n using basis-index equivalence with the canonical coordinate
dual basis. At a common zero x0, evaluate the dual basis on x-x0 to obtain an
affine equivalence. The designated coordinates equal the input affine forms.
The injection of r selected coordinates leaves n-r free coordinates;
zero-extension followed by the affine inverse parametrizes exactly the common
zero set injectively. No Boolean quotient or pointwise polynomial vanishing
argument is used. Empty selected family and r=n must be included.

Consumer: R15 uses free affine coordinates with ordinary polynomial images;
R08 uses affine coordinate normal form. This claim belongs in claims/ as the
project's precise supporting interface, adapted from the paper's affine basis
completion argument. Generic basis extension is supplied by checked Mathlib.
