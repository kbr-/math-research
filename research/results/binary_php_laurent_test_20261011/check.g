# Free-algebra checks of the compact local PHP identities, a complete n=1
# generator identity, its Laurent extraction, and the cube-normalization control.
# Expected: 504 local identities, 33 complete n=1 identities, 35 interpolation
# identities, 3 cube controls, 2 trace controls, and 3 nonzero negative controls.
# Stages use only four local variables and a 33-by-33 Vandermonde system.
plK := GF(64);; plA := FreeAssociativeAlgebraWithOne(plK,"x","y","z","w","p","q");;
plG := GeneratorsOfAlgebra(plA);; plVars := plG{[2..5]};;
plOne := One(plA);; plZero := Zero(plA);;
plX := plVars[1];; plY := plVars[2];; plP := plG[6];; plQ := plG[7];;
plNodesAll := Filtered(Elements(plK),x->not IsZero(x));;
plLocal := 0;; plGlobal := 0;; plInterp := 0;; plCube := 0;; plNegative := 0;;
plCheck := function(a,b)
  if a<>b then Print("FAIL identity\n"); QUIT_GAP(1); fi;
end;;
plProd := function(xs)
  if Length(xs)=0 then return plOne; else return Product(xs); fi;
end;;
plAcoef := Zero(plK);; plBcoef := Zero(plK);;
for plAlpha in plNodesAll do
  plAcoef := plAlpha-One(plK); plBcoef := plAlpha^-1-One(plK);
  for plR in [1..4] do
    plXs := plVars{[1..plR]};
    plUs := List(plXs,x->plOne+plAcoef*x);
    plVs := List(plXs,x->plOne+plBcoef*x);
    plRow := plZero;
    for plI in [1..plR] do
      plRow := plRow+plProd(plUs{[1..plI-1]})*plXs[plI]
        *plProd(List(plXs{[plI+1..plR]},x->plOne-x));
    od;
    plCheck(plAlpha^-1*(plProd(plUs)-plProd(List(plXs,x->plOne-x))),plRow);
    plLocal := plLocal+1;
    plColumn := plZero;
    for plI in [1..plR] do
      for plJ in [plI+1..plR] do
        plColumn := plColumn+plAlpha*plBcoef^2*plXs[plI]*plXs[plJ]
          *plProd(plVs{[plJ+1..plR]});
      od;
    od;
    plCheck(plAlpha*plProd(plVs)-(plAlpha*plOne+(One(plK)-plAlpha)*Sum(plXs)),plColumn);
    plLocal := plLocal+1;
  od;
od;
# n=1: M=2, L=4(M+n+1)=16; all 33 Laurent powers tested.
plNodes := plNodesAll{[1..33]};;
plVand := List([-16..16],e->List(plNodes,a->a^e));;
plDelta := function(e) if e=-1 then return One(plK); else return Zero(plK); fi; end;;
plWeights := plVand^-1*List([-16..16],plDelta);;
for plE in [-16..16] do
  plCheck(Sum([1..33],j->plWeights[j]*plNodes[j]^plE),plDelta(plE));
  plInterp := plInterp+1;
od;
plCertificateSum := plZero;; plGoodSum := plZero;; plMissingCommSeen := false;;
for plT in [1..33] do
  plAlpha := plNodes[plT]; plAc := plAlpha-One(plK); plBc := plAlpha^-1-One(plK);
  plUx := plOne+plAc*plX; plUy := plOne+plAc*plY;
  plVx := plOne+plBc*plX; plVy := plOne+plBc*plY;
  plT1 := plAlpha^-1*plUx; plT2 := plAlpha^-1*plUy;
  plH := plAlpha*plOne+(One(plK)-plAlpha)*(plX+plY);
  plLocalPart := plAlpha^-1*(plOne-plX)*plY*plH
    +plT1*plAlpha^-1*(plOne-plY)*plH+plT1*plT2*plAlpha*plBc^2*plX*plY;
  plCommPart := plAlpha^-1*plUx*plAc*plBc*(plY*plX-plX*plY)*plVy;
  plBoolPart := plAlpha^-1*plAc*plBc*((plX^2-plX)*plUy*plVy+(plY^2-plY));
  plCert := plLocalPart-plCommPart-plBoolPart;
  plCheck(plCert,plAlpha^-1*plOne-plX*plY*plH);
  plGlobal := plGlobal+1;
  plCertificateSum := plCertificateSum+plWeights[plT]*plCert;
  plGoodSum := plGoodSum+plWeights[plT]*plX*plY*plH;
  if plCommPart<>plZero then plMissingCommSeen := true; fi;
od;
plCheck(plCertificateSum,plOne); plCheck(plGoodSum,plZero); plInterp := plInterp+2;
if not plMissingCommSeen then Print("FAIL commutator negative control\n"); QUIT_GAP(1); fi;
plNegative := plNegative+1;
plPick := First([1..33],j->not IsZero(plWeights[j]));;
plAlpha := plNodes[plPick];;
if plWeights[plPick]*plX*plY*(plAlpha*plOne+(One(plK)-plAlpha)*(plX+plY))=plZero then
  Print("FAIL interpolation negative control\n"); QUIT_GAP(1);
fi;
plNegative := plNegative+1;
# Cube erasure for contradictory units: formula identity plus free placeholders at old 0/1.
plNormalize := function(x,p,q) return p+(plOne-x)*q+(plOne-x)*x*(p+q); end;;
plCheck(plNormalize(plX,plX,plOne-plX),plOne); plCube := plCube+1;
for plBit in [plZero,plOne] do
  plCheck(plNormalize(plBit,plP,plQ),plP+(plOne-plBit)*plQ); plCube := plCube+1;
od;
if plNormalize(Z(64)*plOne,plP,plQ)-(plP+(plOne-Z(64)*plOne)*plQ)=plZero then
  Print("FAIL non-Boolean negative control\n"); QUIT_GAP(1);
fi;
plNegative := plNegative+1;
plF8 := GF(8);;
plRoot := First(Elements(plF8),a->a^3+a+One(plF8)=Zero(plF8));;
plTr := a->a+a^2+a^4;;
plCheck(plTr(plRoot^2-plRoot),Zero(plF8));
plCheck(plTr(plRoot*(plRoot^2-plRoot)),One(plF8));
Print("PASS: ",plLocal," local row/column identities; ",plGlobal,
  " complete n=1 generator identities; ",plInterp," interpolation identities; ",
  plCube," cube controls; 2 cofactored-trace controls; ",plNegative," negative controls.\n");
QUIT_GAP(0);
