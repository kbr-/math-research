# Minimum weight of the dual of the ternary code spanned by the incidence vectors of 2-dimensional subspaces
# (projective lines) in PG(2,3) and PG(3,3). By the transversality criterion, relations with A = 0 among the
# squared spans of c-spaces of F_3^N correspond to point functions orthogonal to all (N-c)-spaces: N = 3, c = 1
# (lines of PG(2,3)) and N = 4, c = 2 (lines of PG(3,3)). Prediction from the local relations: a difference of
# two (c+1)-space indicators meeting in a c-space has weight 6 and 18 respectively.
LoadPackage("guava");
ptsOf := function(n)
  local V, pts;
  V := GF(3)^n;
  pts := Filtered(Elements(V), v -> not IsZero(v) and First(v, x -> not IsZero(x)) = One(GF(3)));
  return pts;
end;
test := function(n)
  local pts, lines, M, C, D, d;
  pts := ptsOf(n);
  lines := Set(List(Combinations(pts, 2), p -> Set(Filtered(pts, q -> RankMat([p[1], p[2], q]) = 2))));
  M := List(lines, L -> List(pts, function(q) if q in L then return One(GF(3)); else return Zero(GF(3)); fi; end));
  C := GeneratorMatCode(M, GF(3));
  D := DualCode(C);
  d := MinimumDistance(D);
  Print("PG(", n - 1, ",3): points ", Length(pts), ", lines ", Length(lines), ", code dimension ", Dimension(C),
    ", dual dimension ", Dimension(D), ", dual minimum weight ", d, "\n");
end;
test(3);
test(4);
QUIT;
