# Local Laurent identities and formal coefficient extraction; not an asymptotic rank experiment.
wrK := GF(16);; wrA := FreeAssociativeAlgebraWithOne(wrK,"x","y","z");;
wrG := GeneratorsOfAlgebra(wrA);; wrVars := wrG{[2..4]};;
wrOne := One(wrA);; wrZero := Zero(wrA);;
wrPoints := Filtered(Elements(wrK),a->not IsZero(a));;
wrEdge := 0;; wrStars := 0;; wrInterpolation := 0;; wrTraceChecks := 0;; wrNegative := 0;;
wrCheck := function(a,b)
  if a<>b then Print("FAIL Laurent identity\n"); QUIT_GAP(1); fi;
end;;
for wrAlpha in wrPoints do
  wrX := wrVars[1];
  wrU := wrAlpha*(wrOne-wrX)+wrAlpha^-1*wrX;
  wrV := wrAlpha^-1*(wrOne-wrX)+wrAlpha*wrX;
  wrCheck(wrU*wrV-wrOne,(wrAlpha-wrAlpha^-1)^2*(wrX^2-wrX));
  wrEdge := wrEdge+1;
  for wrB in [1..3] do
    for wrSigns in Tuples([-1,1],wrB) do
      wrProduct := wrOne;
      for wrJ in [1..wrB] do
        wrProduct := wrProduct*(wrAlpha^wrSigns[wrJ]*(wrOne-wrVars[wrJ])
          +wrAlpha^(-wrSigns[wrJ])*wrVars[wrJ]);
      od;
      wrExpanded := wrZero;
      for wrBits in Tuples([0,1],wrB) do
        wrNet := Sum([1..wrB],j->wrSigns[j]*(1-2*wrBits[j]));
        wrIndicator := wrOne;
        for wrJ in [1..wrB] do
          if wrBits[wrJ]=1 then wrIndicator := wrIndicator*wrVars[wrJ];
          else wrIndicator := wrIndicator*(wrOne-wrVars[wrJ]); fi;
        od;
        wrExpanded := wrExpanded+wrAlpha^wrNet*wrIndicator;
      od;
      wrCheck(wrProduct,wrExpanded);
      wrStars := wrStars+1;
    od;
  od;
od;
# All Laurent monomials in [-4,4], the complete range for a two-edge graph.
wrNodes := wrPoints{[1..9]};;
wrVand := List([-4..4],e->List(wrNodes,a->a^e));;
wrDelta := function(e)
  if e=0 then return One(wrK); else return Zero(wrK); fi;
end;;
wrRhs := List([-4..4],wrDelta);;
wrWeights := wrVand^-1*wrRhs;;
for wrE in [-4..4] do
  wrCheck(Sum([1..9],j->wrWeights[j]*wrNodes[j]^wrE),wrDelta(wrE));
  wrInterpolation := wrInterpolation+1;
od;
# Path with three vertices: positive local generating functions are
# a(1-x), a^2 x(1-y), a y. Their product is a^4 H with H nonzero formally.
wrH := (wrOne-wrVars[1])*wrVars[1]*(wrOne-wrVars[2])*wrVars[2];;
wrCheck(Sum([1..9],j->wrWeights[j]*wrNodes[j]^4*wrH),wrZero);
wrInterpolation := wrInterpolation+1;
wrPick := First([1..9],j->not IsZero(wrWeights[j]));;
if wrWeights[wrPick]*wrNodes[wrPick]^4*wrH=wrZero then
  Print("FAIL omitted-point negative control\n"); QUIT_GAP(1);
fi;
wrNegative := wrNegative+1;
wrR := 2;; wrF := GF(4);;
wrTr := x->Sum([0..wrR-1],j->x^(2^j));;
for wrQ in [4,16] do
  wrF := GF(wrQ); wrR := LogInt(wrQ,2);
  wrBeta := First(Elements(wrF),x->wrTr(x)=One(wrF));
  for wrA0 in Elements(wrF) do
    wrT := wrTr(wrBeta*wrA0);
    wrCheck(wrT^2,wrT);
    wrTraceChecks := wrTraceChecks+1;
  od;
  wrCheck(wrTr(wrBeta),One(wrF));
od;
wrOmega := Z(4);;
for wrA0 in Elements(GF(4)) do
  wrC0 := wrOmega^2*wrA0+wrOmega*wrA0^2;
  wrCheck(wrC0^2,wrC0);
od;
Print("PASS: ",wrEdge," edge identities; ",wrStars," star expansions; ",
  wrInterpolation," interpolation identities; ",wrTraceChecks,
  " trace projections; 4 conjugate projections; ",wrNegative," negative control.\n");
QUIT_GAP(0);
