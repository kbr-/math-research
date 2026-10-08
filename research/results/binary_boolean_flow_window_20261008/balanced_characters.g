# Exact local ordinary-polynomial certificates for Boolean character balancing.
# Fixed informative controls: q=3 over GF(4), q=5 over GF(16), three variables.
# All 34 unit products, 152 phase-weighted cancellations, and 112 oriented
# vertex/charge interpolations of valence 1..3. No graph-size extrapolation.
# Stage 1 checks units modulo an explicit degree-two Boolean multiple;
# stage 2 checks the cancellation rewrite; stage 3 checks the vertex encoding.
bfOne:=1;; bfZero:=0;; bfRoot:=1;; bfMod:=3;; bfVars:=[];;
BFChar:=function(a,i) return bfOne+(bfRoot^(a mod bfMod)-1)*bfVars[i]; end;;
BFProd:=function(xs) local p,x; p:=bfOne; for x in xs do p:=p*x; od; return p; end;;
bfUnits:=0;; bfCancellations:=0;; bfVertices:=0;; bfNegative:=0;;
for bfCase in [[3,4,1],[5,16,3]] do
 bfMod:=bfCase[1];; bfField:=GF(bfCase[2]);;
 bfRoot:=Z(bfCase[2])^bfCase[3];;
 if Order(bfRoot)<>bfMod then Error("Root order mismatch"); fi;
 bfRing:=PolynomialRing(bfField,3);; bfVars:=IndeterminatesOfPolynomialRing(bfRing);;
 bfOne:=One(bfRing);; bfZero:=Zero(bfRing);; bfBool:=bfVars[1]^2-bfVars[1];;
 Print("field=",Size(bfField)," modulus=",bfMod," variables=3\n");
 for bfA in [0..bfMod-1] do for bfB in [0..bfMod-1] do
  bfCoeff:=(bfRoot^bfA-1)*(bfRoot^bfB-1);;
  if BFChar(bfA,1)*BFChar(bfB,1)-BFChar(bfA+bfB,1)<>bfCoeff*bfBool then
   Error("Unit multiplication certificate failed");
  fi;
  bfUnits:=bfUnits+1;
  for bfC in [0..bfMod-1] do
   bfKappa:=bfRoot^bfC;;
   bfCoeff:=((bfRoot^bfA-1)-bfKappa*(bfRoot^bfB-1))*(bfRoot^((-bfB) mod bfMod)-1);;
   bfLeft:=(BFChar(bfA,1)-bfKappa*BFChar(bfB,1))*BFChar(-bfB,1);;
   bfRight:=BFChar(bfA-bfB,1)-bfKappa*bfOne;;
   if bfLeft-bfRight<>bfCoeff*bfBool then Error("Cancellation certificate failed"); fi;
   bfCancellations:=bfCancellations+1;
  od;
 od; od;
 if BFChar(1,1)^2=BFChar(2,1) then Error("Negative control lost Boolean correction"); fi;
 bfNegative:=bfNegative+1;
 for bfD in [1..3] do
  for bfSigns in Tuples([-1,1],bfD) do
   for bfCharge in [0..bfMod-1] do
    bfVertex:=BFProd(List([1..bfD],i->BFChar(bfSigns[i],i)))-bfRoot^bfCharge*bfOne;;
    bfExpansion:=bfZero;;
    for bfBits in Tuples([0,1],bfD) do
     bfSum:=Sum([1..bfD],i->bfSigns[i]*bfBits[i]);;
     bfCoeff:=bfRoot^(bfSum mod bfMod)-bfRoot^bfCharge;;
     if (bfCoeff=Zero(bfField))<>((bfSum mod bfMod)=bfCharge) then Error("Forbidden tuple mismatch"); fi;
     bfIndicator:=BFProd(List([1..bfD],i->bfBits[i]*bfVars[i]+(1-bfBits[i])*(bfOne-bfVars[i])));;
     bfExpansion:=bfExpansion+bfCoeff*bfIndicator;
    od;
    if bfVertex<>bfExpansion then Error("Vertex interpolation certificate failed"); fi;
    bfVertices:=bfVertices+1;
   od;
  od;
 od;
od;
if [bfUnits,bfCancellations,bfVertices,bfNegative]<>[34,152,112,2] then Error("Coverage count mismatch"); fi;
Print("PASS units=",bfUnits," cancellations=",bfCancellations," vertex_interpolations=",bfVertices," negative_controls=",bfNegative,"\n");
QUIT;
