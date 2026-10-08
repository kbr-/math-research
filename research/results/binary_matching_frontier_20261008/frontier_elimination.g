# General hypothesis: eliminating b from relations on (a,b) and (b,c)
# derives every forbidden (a,c) assignment indicator in ordinary PC degree3.
# Exhaust all 16^2 relation pairs over each of GF(2),GF(3):512 cases,
# 2048 projected assignments,1152 forbidden projections,2304 bag lifts.
# Only three variables, degree<=3, at most eight monomials per polynomial.
# Stage1 tests projection semantics; stage2 constructs exact polynomial
# certificates; stage3 rejects omission of one eliminated-variable value.
# Also exhaust all 64 forbidden-point certificates for two-variable Boolean
# violation polynomials across the two fields, with explicit Boolean cofactors.
fgVars:=[];; fgOne:=1;; fgZero:=0;;
FGIndicator:=function(indices,bits) local p,i;
 p:=fgOne;
 for i in [1..Length(indices)] do
  if bits[i]=1 then p:=p*fgVars[indices[i]]; else p:=p*(fgOne-fgVars[indices[i]]); fi;
 od;
 return p;
end;;
FGAllowed:=function(mask,a,b) return QuoInt(mask,2^(2*a+b)) mod 2=1; end;;
fgCases:=0;; fgProjected:=0;; fgForbidden:=0;; fgLifts:=0;; fgNegative:=0;;
fgPredicateCertificates:=0;;
for fgPrime in [2,3] do
 fgRing:=PolynomialRing(GF(fgPrime),3);; fgVars:=IndeterminatesOfPolynomialRing(fgRing);;
 fgOne:=One(fgRing);; fgZero:=Zero(fgRing);;
 for fgMask in [0..15] do
  fgBad:=Filtered(Tuples([0,1],2),a->not FGAllowed(fgMask,a[1],a[2]));;
  fgPolynomial:=fgZero;;
  for fgAlpha in fgBad do fgPolynomial:=fgPolynomial+FGIndicator([1,2],fgAlpha); od;
  for fgAlpha in fgBad do
   fgTarget:=FGIndicator([1,2],fgAlpha);; fgCertificate:=fgZero;;
   fgLit:=List([1,2],i->FGIndicator([i],[fgAlpha[i]]));;
   for fgGamma in fgBad do
    if fgGamma=fgAlpha then
     fgCertificate:=fgCertificate+(fgVars[1]^2-fgVars[1])*fgLit[2]^2+fgLit[1]*(fgVars[2]^2-fgVars[2]);
    else
     fgDiff:=PositionProperty([1,2],i->fgGamma[i]<>fgAlpha[i]);; fgOther:=3-fgDiff;;
     fgCertificate:=fgCertificate-(fgVars[fgDiff]^2-fgVars[fgDiff])*FGIndicator([fgOther],[fgGamma[fgOther]])*fgLit[fgOther];
    fi;
   od;
   if fgPolynomial*fgTarget-fgTarget<>fgCertificate then Error("Predicate-to-point certificate failed"); fi;
   fgPredicateCertificates:=fgPredicateCertificates+1;
  od;
 od;
 for fgLeft in [0..15] do for fgRight in [0..15] do
  fgCases:=fgCases+1;
  for fgA in [0,1] do for fgC in [0,1] do
   fgProjected:=fgProjected+1;
   fgGood:=Filtered([0,1],b->FGAllowed(fgLeft,fgA,b) and FGAllowed(fgRight,b,fgC));;
   if Length(fgGood)=0 then
    fgForbidden:=fgForbidden+1; fgSum:=fgZero; fgFirst:=fgZero;
    for fgB in [0,1] do
     if not FGAllowed(fgLeft,fgA,fgB) then
      fgParent:=FGIndicator([1,2],[fgA,fgB]);; fgLift:=fgParent*FGIndicator([3],[fgC]);;
     else
      if FGAllowed(fgRight,fgB,fgC) then Error("Missing forbidden parent"); fi;
      fgParent:=FGIndicator([2,3],[fgB,fgC]);; fgLift:=fgParent*FGIndicator([1],[fgA]);;
     fi;
     if fgLift<>FGIndicator([1,2,3],[fgA,fgB,fgC]) then Error("Bag lift certificate failed"); fi;
     fgLifts:=fgLifts+1; fgSum:=fgSum+fgLift;
     if fgB=0 then fgFirst:=fgLift; fi;
    od;
    fgTarget:=FGIndicator([1,3],[fgA,fgC]);;
    if fgSum<>fgTarget then Error("Projection certificate failed"); fi;
    if fgFirst=fgTarget then Error("Omitted-value negative control failed"); fi;
    fgNegative:=fgNegative+1;
   fi;
  od; od;
 od; od;
 Print("field=",fgPrime," completed_all_relation_pairs=256\n");
od;
if [fgCases,fgProjected,fgForbidden,fgLifts,fgNegative]<>[512,2048,1152,2304,1152] then Error("Coverage count mismatch"); fi;
if fgPredicateCertificates<>64 then Error("Predicate coverage mismatch"); fi;
Print("predicate_point_certificates=",fgPredicateCertificates,"\n");
Print("PASS cases=",fgCases," projections=",fgProjected," forbidden=",fgForbidden," lifts=",fgLifts," negative_controls=",fgNegative,"\n");
QUIT;
