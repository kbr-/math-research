\\ Discriminant of the trinomial edge polynomial at a merging of two neck rings (30 Sept 2026).
\\ Tested statement: Disc_z(g z^(4M) + h z^(2M) + d) = c * g^a * d^b * (h^2 - 4 g d)^(2M), so if the
\\ merged edge is a genuine trinomial and h^2 - 4gd vanishes simply along a hypersurface of the
\\ cluster region, the Wronskian discriminant has a component of multiplicity 2M there.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
for (M = 2, 4, my(f = g * z^(4 * M) + h * z^(2 * M) + d); emit(Str("M=", M, " Disc = ", factor(poldisc(f, z)))));
