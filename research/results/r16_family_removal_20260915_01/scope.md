# R16 simultaneous weighted family removal

Target: paper lem:hybrid / R16, complete finite dependent registry, actual
ordinary PC refutation and supplied literal high-rank witnesses. R15 constructs
those witnesses later; their existence is not silently asserted here.

Registry type sigma ⊕ (Sigma b:kappa, Fin h × iota b), matching the existing
clause registry. Values are canonical FreshENSBlock products embedded by the
same variable map; source system contains old axioms, all Boolean variable
equations and all companions, but no product axioms.

For each low-rank block use R08. For each high-rank block put its literal
coefficient witnesses in a distinguished row and zero elsewhere, giving1-f.
All coefficient images have degree<=k. Low weighted companions have Boolean
NS cost rank+1+degf; high ones have cost2k+1; all coefficient/variable Boolean
images cost3k. Old weighted axioms fit D+degf. All fit B=k(D+1) for h>=1,
k>=1,D>=2h+1. Use R03 weighted replay at kD+degf<=B, with a bound-lifted variant
if individual axiom certificates are already established atB.

No multilinearity of f is needed by this proof: any ordinary polynomial of
degree<=k is Boolean-valued overF2 and R05 supplies f²-f certificates through2k.
Properness is also unnecessary for the removal theorem once literal witnesses
are supplied at every high-rank block; retain the full source application.
No claim that the witness assumption itself is proved by R16.

Final theorem should produce Derives F B f from the actual family refutation.
The coordinator owns living notebook sections and route. Full evidence/MathJax
proof and local checkpoint required before switching back to R15.

Final refinement: all local weighted companion/Boolean certificates fit the
existing replay bound kD+degree(f), so no bound-lifted replay variant was needed.
The final output lifts that bound to k(D+1). The block index type is arbitrary;
only individual input tuples and retained variables require finiteness.
Actual proof dependencies omit the proper-span/coordinate/scalar cleanup and
exact companion-degree results while keeping the explicit D>=2h+1 source
hypothesis. Previously checked helpers remain available to other consumers.
