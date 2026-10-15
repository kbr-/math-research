# Exact finite-field validation of field-first certificate normalization.
# Predictions: prefix coefficients at every old point agree with an independent
# first-nonzero inverse, P vanishes, and all placeholder-basis tests pass.
# Refuted by: Any unequal coefficient or nonzero residual on the complete grid.
# Possible because: Prefix powers and field ordering can produce different values.
# Negative control: moving x before the fields changes the selected placeholder
# whenever x is nonbinary; both algorithms are evaluated before asserting failure.
# This checks the stated finite grids, not the universal proof or circuit bounds.
epAssert := function(ok, msg)
  if not ok then Print("FAILED ", msg, "\n"); QUIT_GAP(1); fi;
end;
epCounts := [];
epZero := 0;; epA := [];; epF := [];;
for epQ in [4,8] do
  epK := GF(epQ); epZero := Zero(epK); epOne := One(epK);
  epBasisChecks := 0; epOrderChanges := 0; epPoints := 0;
  epLimit := epQ^2 * 4;
  epAssert(epLimit <= 1000, "enumeration size guard");
  for epX in Elements(epK) do
    for epZ in Elements(epK) do
      epF := [epX^2+epX,epZ^2+epZ,epX,epOne+epX];
      epPrefix := epOne; epA := [];
      for epI in [1..4] do
        Add(epA,epF[epI]^(epQ-2)*epPrefix);
        epPrefix := epPrefix*(epOne-epF[epI]^(epQ-1));
      od;
      epAssert(epPrefix=epZero,"P vanishes on full extension grid");
      epFirst := PositionProperty(epF, v -> v<>epZero);
      epExpected := List([1..4],i -> epZero);
      epExpected[epFirst] := Inverse(epF[epFirst]);
      # C=Y3+Y4. C'=A+P*C, evaluated on every placeholder basis vector.
      for epI in [1..4] do
        epC := epZero;
        if epI in [3,4] then epC:=epOne; fi;
        epAssert(epA[epI]+epPrefix*epC=epExpected[epI],"basis coefficient");
        epBasisChecks := epBasisChecks+1;
      od;
      epAssert(Sum([1..4],i->epA[i]*epF[i])+epPrefix=epOne,"telescoping");
      if epX<>epZero and epX<>epOne then
        # Altered source order: [x,1+x,Bx,Bz]. Compare in original label order.
        epWrong := [Inverse(epX),epZero,epZero,epZero];
        epWrongOriginal := [epWrong[3],epWrong[4],epWrong[1],epWrong[2]];
        epAssert(epWrongOriginal<>epExpected,"control differs before testing");
        epAssert(epWrongOriginal[1]=epZero and epExpected[1]<>epZero,
                 "field-first rule is false for the changed order");
        epOrderChanges := epOrderChanges+1;
      fi;
      epPoints := epPoints+1;
    od;
  od;
  epAssert(epPoints=epQ^2 and epBasisChecks=epLimit and
           epOrderChanges=(epQ-2)*epQ,"completion counts");
  Add(epCounts,[epQ,epPoints,epBasisChecks,epOrderChanges]);
od;
# Independent symbolic telescope in the multivariate polynomial ring over F2.
epR := PolynomialRing(GF(2),["u","v"]);;
epVars := IndeterminatesOfPolynomialRing(epR);;
epU:=epVars[1];; epV:=epVars[2];; epOne:=One(epR);;
for epQ in [4,8] do
  epF:=[epU^2+epU,epV^2+epV,epU,epOne+epU];
  epP:=epOne; epSum:=Zero(epR);
  for epI in [1..4] do
    epSum:=epSum+epF[epI]^(epQ-1)*epP;
    epP:=epP*(epOne-epF[epI]^(epQ-1));
  od;
  epAssert(epSum+epP=epOne,"formal telescope");
od;
Print("q, old points, placeholder basis checks, changed-order controls\n");
for epRow in epCounts do Print(epRow,"\n"); od;
Print("Formal telescopes checked: ",Length(epCounts),"\n");
Print("PASS extension-prefix completion\n");
QUIT_GAP(0);
