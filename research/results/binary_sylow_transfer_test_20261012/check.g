# Exact controls for the rectangular-transfer and adjugate-gauge statements over F2.
# Refuted by: a nonzero low-degree formal transfer, changed matrix product, or failed
# weighted gauge identity on any enumerated assignment with its hypotheses satisfied.
# Possible because: deleting the inverse-side correction, using the matrix instead of
# its adjugate, or dropping the pivot weight changes these actual identities.
# Predictions: every stated identity passes; the gauge omissions and formal-power control are detected.
# The fixed fixtures enumerate all assignments, not solutions of the inconsistent rank base.
# Symbolic transfer tests ordinary polynomial monomials, without Boolean reduction.
# Stages: one symbolic gauge; all point assignments of two bounded gauge fixtures;
# one complete low-degree symbolic transfer basis; nonzero threshold witnesses.
# No asymptotic conclusion is inferred from these finite checks.

sgF := GF(2);;
sgZero := Zero(sgF);;
sgOne := One(sgF);;
sgActiveRing := sgF;;
sgChecks := 0;;
sgControls := rec(noWeight := false, noRight := false, noAdjugate := false);;

sgCheck := function(ok, label)
  sgChecks := sgChecks + 1;
  if not ok then Error(Concatenation("FAILED: ", label)); fi;
end;;

sgMatrix := function(v, rows, cols)
  return List([1..rows], i -> v{[(i-1)*cols+1..i*cols]});
end;;

sgAdjugate := function(mat)
  local k, i, j, rr, cc, adj;
  k := Length(mat);
  if k = 1 then return [[One(mat[1][1])]]; fi;
  adj := NullMat(k,k,sgActiveRing);
  for i in [1..k] do
    for j in [1..k] do
      rr := Filtered([1..k], a -> a <> j);
      cc := Filtered([1..k], a -> a <> i);
      adj[i][j] := DeterminantMat(List(rr, a -> mat[a]{cc}));
    od;
  od;
  return adj;
end;;

sgShear := function(n,k,x)
  local h,i,j;
  h := IdentityMat(n,sgActiveRing);
  for i in [1..k] do
    for j in [1..n-k] do h[i][k+j] := x[i][j]; od;
  od;
  return h;
end;;

sgGauge := function(a,b,k,badAdj)
  local n,mat,c,w,x,h;
  n := Length(b);
  mat := List([1..k], i -> a[i]{[1..k]});
  c := List([1..k], i -> a[i]{[k+1..n]});
  w := DeterminantMat(mat);
  if badAdj then x := mat*c; else x := sgAdjugate(mat)*c; fi;
  h := sgShear(n,k,x);
  return rec(a:=a*h,b:=h*b,w:=w,h:=h,c:=c);
end;;

sgUpper := function(n)
  local positions,bits,u,i,all;
  positions := Concatenation(List([1..n-1], i -> List([i+1..n], j -> [i,j])));
  all := [];
  for bits in Tuples([sgZero,sgOne],Length(positions)) do
    u := IdentityMat(n,sgF);
    for i in [1..Length(positions)] do
      u[positions[i][1]][positions[i][2]] := bits[i];
    od;
    Add(all,u);
  od;
  return all;
end;;

# A symbolic nontrivial adjugate case, with the group parameter itself indeterminate.
sgRing := PolynomialRing(sgF,14);;
sgActiveRing := sgRing;;
sgV := IndeterminatesOfPolynomialRing(sgRing);;
sgA := sgMatrix(sgV{[1..6]},2,3);;
sgB := sgMatrix(sgV{[7..12]},3,2);;
sgY := sgMatrix(sgV{[13..14]},2,1);;
sgH := sgShear(3,2,sgY);;
sgG := sgGauge(sgA,sgB,2,false);;
sgG2 := sgGauge(sgA*sgH,sgH*sgB,2,false);;
sgN := sgH-IdentityMat(3,sgRing);;
sgCheck(sgG.a*sgG.b=sgA*sgB,"symbolic AB is fixed");
sgCheck(List([1..2],i->sgG.a[i]{[3]})=(One(sgRing)+sgG.w)*sgG.c,
        "symbolic pivot block equals (1+W)C");
sgCheck(sgG2.a-sgG.a=(One(sgRing)+sgG.w)*sgA*sgN,"symbolic A equivariance defect");
sgCheck(sgG2.b-sgG.b=(One(sgRing)+sgG.w)*sgN*sgB,"symbolic B equivariance defect");
sgCheck(sgG2.w=sgG.w,"symbolic pivot weight fixed");
Print("Symbolic adjugate fixture: all five polynomial identities passed.\n");

# Two fixtures cover a hard-base shape and a genuinely nonconstant 2x2 adjugate.
sgActiveRing := sgF;;
sgNn := 0;; sgK := 0;; sgBad := rec();;
for sgCase in [[3,2,1],[2,3,2]] do
  sgM := sgCase[1];; sgNn := sgCase[2];; sgK := sgCase[3];;
  sgBits := 2*sgM*sgNn;; sgCount := 2^sgBits;;
  if sgCount>4096 then Error("Fixture exceeds the predeclared assignment budget"); fi;
  sgGroup := List(Tuples([sgZero,sgOne],sgK*(sgNn-sgK)),
                  v->sgShear(sgNn,sgK,sgMatrix(v,sgK,sgNn-sgK)));;
  sgNonzero := 0;; sgBefore := sgChecks;;
  Print("Gauge fixture ",sgCase,": ",sgCount," assignments, ",Length(sgGroup)," shears.\n");
  for sgVector in Tuples([sgZero,sgOne],sgBits) do
    sgA := sgMatrix(sgVector{[1..sgM*sgNn]},sgM,sgNn);;
    sgB := sgMatrix(sgVector{[sgM*sgNn+1..sgBits]},sgNn,sgM);;
    sgG := sgGauge(sgA,sgB,sgK,false);;
    sgPivot := List([1..sgK],i->sgG.a[i]{[sgK+1..sgNn]});;
    sgCheck(sgG.a*sgG.b=sgA*sgB,"point AB");
    sgCheck(sgG.w*sgPivot=NullMat(sgK,sgNn-sgK,sgF),"weighted pivot block");
    if sgG.w=sgOne then sgNonzero:=sgNonzero+1; fi;
    if not sgControls.noRight and sgG.a*sgB<>sgA*sgB then
      sgControls.noRight:=true;
      Print("Omitted B correction detected at ",sgCase," with A=",sgA," B=",sgB,".\n");
    fi;
    sgBad := sgGauge(sgA,sgB,sgK,true);;
    if not sgControls.noAdjugate and sgBad.w*List([1..sgK],i->sgBad.a[i]{[sgK+1..sgNn]})
       <>NullMat(sgK,sgNn-sgK,sgF) then
      sgControls.noAdjugate:=true;
      Print("Wrong adjugate detected at ",sgCase," with A=",sgA,".\n");
    fi;
    for sgH in sgGroup do
      sgG2 := sgGauge(sgA*sgH,sgH*sgB,sgK,false);;
      sgCheck(sgG2.w=sgG.w,"point weight invariance");
      sgCheck(sgG.w*sgG2.a=sgG.w*sgG.a,"weighted A invariance");
      sgCheck(sgG.w*sgG2.b=sgG.w*sgG.b,"weighted B invariance");
      if not sgControls.noWeight and (sgG2.a<>sgG.a or sgG2.b<>sgG.b) then
        sgControls.noWeight:=true;
        Print("Omitted weight detected at ",sgCase," with A=",sgA," B=",sgB," H=",sgH,".\n");
      fi;
    od;
  od;
  sgCheck(sgNonzero>0 and sgNonzero<sgCount,"both pivot strata occur");
  Print("Completed ",sgCount," assignments; W=1 on ",sgNonzero,
        "; checks=",sgChecks-sgBefore,".\n");
od;

# Formal transfer: every ordinary monomial of degree below floor(4^2/4).
sgRing := PolynomialRing(sgF,8);; sgV := IndeterminatesOfPolynomialRing(sgRing);;
sgA := [sgV{[1..4]}];; sgB := List(sgV{[5..8]},x->[x]);;
sgGroup := sgUpper(4);;
sgTransforms := List(sgGroup,u->Concatenation((sgA*u)[1],List(u^-1*sgB,r->r[1])));;
sgMonomials := Concatenation(List([0..3],d->UnorderedTuples([1..8],d)));;
Print("Formal trace: ",Length(sgMonomials)," monomials, ",Length(sgGroup)," group elements.\n");
for sgIndices in sgMonomials do
  sgTrace := Zero(sgRing);;
  for sgImage in sgTransforms do
    sgTerm := One(sgRing);;
    for sgIndex in sgIndices do sgTerm:=sgTerm*sgImage[sgIndex]; od;
    sgTrace := sgTrace+sgTerm;
  od;
  sgCheck(IsZero(sgTrace),"formal low-degree full transfer");
od;

# The sharp rectangular formula is formal: a Boolean evaluation could not detect
# wrongly replacing det(M)^2 by det(M), so compare the actual symbolic transfer.
sgRing2 := PolynomialRing(sgF,8);; sgA2 := sgMatrix(IndeterminatesOfPolynomialRing(sgRing2),2,4);;
sgActiveRing := sgRing2;; sgRectPoly := Zero(sgRing2);;
for sgParams in Tuples([sgZero,sgOne],4) do
  sgRectH := sgShear(4,2,sgMatrix(sgParams,2,2));;
  sgImageA := sgA2*sgRectH;; sgTerm := One(sgRing2);;
  for sgI in [1..2] do
    for sgJ in [3..4] do sgTerm:=sgTerm*sgImageA[sgI][sgJ]; od;
  od;
  sgRectPoly := sgRectPoly+sgTerm;
od;
sgDet := DeterminantMat(List([1..2],i->sgA2[i]{[1..2]}));;
sgCheck(sgRectPoly=sgDet^2,"sharp rectangular formal transfer formula");
sgCheck(sgRectPoly<>sgDet,"formal determinant power must not be Boolean-reduced");
Print("Rectangular formal trace equals det(M)^2 and differs from det(M): ",sgRectPoly,".\n");

# Nonzero evaluations of the boundary and full-group witnesses; no asymptotic extrapolation.
sgActiveRing := sgF;;
sgRect := List(Tuples([sgZero,sgOne],4),v->sgShear(4,2,sgMatrix(v,2,2)));;
sgRectTrace := sgZero;;
for sgH in sgRect do
  sgRectTrace := sgRectTrace+Product(Concatenation(List([1..2],i->sgH[i]{[3..4]})));
od;
sgCheck(sgRectTrace=sgOne,"rectangular degree-four threshold witness");
sgFullTrace := sgZero;;
for sgH in sgGroup do
  sgFullTrace := sgFullTrace+Product(Concatenation(List([1..3],i->sgH[i]{[i+1..4]})));
od;
sgCheck(sgFullTrace=sgOne,"full degree-six nonzero witness");
sgCheck(sgControls.noWeight and sgControls.noRight and sgControls.noAdjugate,
        "all independent omission controls detected");
Print("PASS: ",sgChecks," exact checks; all controls detected.\n");
QUIT;
