-- Degrees of the first-step curve and of the polar complete intersection on a random plane (cycle bmd-20261009-de).
-- Input: the file written by research/tools/bmd_plane_minors.cpp (minorList: the maximal minors of [b_0..b_N] omitting
-- columns 0..N; collisionForms: a_i and a_i - a_j on the plane).  Statement tested: conj:cube-four-first-step-self-link
-- needs deg T_d = lambda(lambda+1)/2.  Off collisions, V(T_d) is the zero set of all maximal minors
-- (cor:cube-first-step-brill-noether) and V(F, delta F) = V(Delta, M_{N-1}) (lem:cube-polar-minor-identity).
-- The affine lengths after saturating by the collision forms are printed; at d = 2 they must be 120 and 240 - 60.
-- Speed: the minors share a large collision factor (degree 50 of 65 at d = 2); it is divided out first, by exact
-- division by each collision form while it divides every generator, so the saturations work on low-degree generators.
-- Usage: M2 --script bmd_plane_degrees.m2 IN.m2 P [full]
args = drop(scriptCommandLine, 1);
p = value args#1;
R = ZZ/p[x, y];
load args#0;
co = product collisionForms;
N = #minorList - 1;
strip = L -> (
    L = select(L, f -> f != 0);
    for l in collisionForms do while all(L, f -> f % l == 0) do L = apply(L, f -> f // l);
    L);
Tgens = strip minorList;
print("T generators after stripping: degrees " | toString unique apply(Tgens, first @@ degree));
Tsat = saturate(ideal Tgens, co);
print("T: dim " | toString dim Tsat | ", length " | toString degree Tsat);
CIgens = strip {minorList#N, minorList#(N-1)};
CI = saturate(ideal CIgens, co);
print("(Delta, M_{N-1}) off collisions: length " | toString degree CI);
if #args > 2 then (
    print("T reduced points: " | toString degree radical Tsat);
    print("link of T inside CI: length " | toString degree saturate(CI : Tsat, co)));
