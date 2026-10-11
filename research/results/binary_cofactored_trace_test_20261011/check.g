# Companion-only binary descent controls, not an asymptotic degree experiment.
# Prediction: the displayed symbolic OR/affine identities hold with unrestricted
# fresh coefficients. Exhaust all GF(4) affine maps for four coefficients of
# two nested accuracy-two blocks on one Boolean bit. For every nonzero Boolean
# weight satisfying all original companions, both unital trace projections
# preserve both products and all companions on its support. No fresh field
# equation is assumed. Count and print the tested and admitted maps.
# Negative controls: ordinary trace is not unital in GF(4); omitting a
# companion loses value preservation; a nonbinary input invalidates commuting
# coefficient projection with an input. The symbolic identities are checked
# by polynomial expansion, independently of the pointwise model enumeration.
ctK := GF(4);; ctO := One(ctK);; ctZ := Zero(ctK);; ctW := Z(4);;
ctCheck := function(a,b)
  if a<>b then Print("FAIL identity\n"); QUIT_GAP(1); fi;
end;;
ctX := Indeterminate(ctK,"x");; ctR := Indeterminate(ctK,"r");;
ctS := Indeterminate(ctK,"s");; ctT := Indeterminate(ctK,"t");;
ctU := Indeterminate(ctK,"u");;
ctP := (1-ctR*ctX)*(1-ctS*ctX);;
ctPref := ctR+ctS*(1-ctR*ctX);;
ctG := 1-ctP;; ctQ := (1-ctT*ctG)*(1-ctU*ctG);;
ctPref2 := ctT+ctU*(1-ctT*ctG);;
ctCheck(ctP^2-ctP,-ctPref*ctX*ctP);
ctCheck(ctQ^2-ctQ,-ctPref2*ctG*ctQ);
ctCheck((1+ctP+ctQ)^2-(1+ctP+ctQ),ctP^2-ctP+ctQ^2-ctQ);
ctCheck(ctP-ctQ,ctP*(1-ctQ)-ctQ*(1-ctP));
ctSymbolic := 4;;
ctPi := function(z,c) return c*z+(c*z)^2; end;;
ctCs := Filtered(Elements(ctK),c->ctPi(ctO,c)=ctO);;
ctStates := Tuples(Elements(ctK),4);;
ctAt := function(a,x)
  local p,g,q;
  p := (ctO-a[1]*x)*(ctO-a[2]*x); g := ctO-p;
  q := (ctO-a[3]*g)*(ctO-a[4]*g);
  return [p,q,x*p,g*q];
end;;
# A pair of values at 0,1 uniquely specifies each affine coefficient map.
ctMaps := 0;; ctAdmitted := 0;; ctComparisons := 0;; ctNonbinary := 0;;
ctWeights := [[ctO,ctO],[ctZ,ctO],[ctO,ctZ]];;
for ctA0 in ctStates do
  ctV0 := ctAt(ctA0,ctZ);
  for ctA1 in ctStates do
    ctMaps := ctMaps+1; ctV1 := ctAt(ctA1,ctO);
    for ctWeight in ctWeights do
      if ctWeight[1]*ctV0[3]=ctZ and ctWeight[1]*ctV0[4]=ctZ
        and ctWeight[2]*ctV1[3]=ctZ and ctWeight[2]*ctV1[4]=ctZ then
        ctAdmitted := ctAdmitted+1;
        if ForAny([1..4],i->ctWeight[1]*(ctA0[i]^2-ctA0[i])<>ctZ
          or ctWeight[2]*(ctA1[i]^2-ctA1[i])<>ctZ) then
          ctNonbinary := ctNonbinary+1;
        fi;
        for ctC in ctCs do
          ctB0 := List(ctA0,z->ctPi(z,ctC)); ctB1 := List(ctA1,z->ctPi(z,ctC));
          ctN0 := ctAt(ctB0,ctZ); ctN1 := ctAt(ctB1,ctO);
          for ctI in [1..2] do
            ctCheck(ctWeight[1]*(ctV0[ctI]-ctN0[ctI]),ctZ);
            ctCheck(ctWeight[2]*(ctV1[ctI]-ctN1[ctI]),ctZ);
            ctComparisons := ctComparisons+2;
          od;
          for ctI in [3..4] do
            ctCheck(ctWeight[1]*ctN0[ctI],ctZ);
            ctCheck(ctWeight[2]*ctN1[ctI],ctZ);
            ctComparisons := ctComparisons+2;
          od;
        od;
      fi;
    od;
  od;
od;
if ctNonbinary=0 then Print("FAIL nonvacuity\n"); QUIT_GAP(1); fi;
ctNegative := 0;;
ctGood := [ctO,ctW,ctO,ctW];;
ctCheck(ctAt(ctGood,ctO){[3,4]},[ctZ,ctZ]);
if ctAt(List(ctGood,z->ctPi(z,ctO)),ctO)[3]=ctZ then
  Print("FAIL nonunital control\n"); QUIT_GAP(1);
fi;
ctNegative := ctNegative+1;
ctBad := [ctW,ctW,ctZ,ctZ];;
if ctAt(ctBad,ctO)[3]=ctZ or ctAt(ctBad,ctO)[1]
  =ctAt(List(ctBad,z->ctPi(z,ctCs[1])),ctO)[1] then
  Print("FAIL missing companion control\n"); QUIT_GAP(1);
fi;
ctNegative := ctNegative+1;
ctCheck(ctO-ctW^-1*ctW,ctZ);
if ctO-ctPi(ctW^-1,ctCs[1])*ctW=ctZ then
  Print("FAIL nonbinary input control\n"); QUIT_GAP(1);
fi;
ctNegative := ctNegative+1;
Print("PASS: ",ctSymbolic," symbolic identities; ",ctMaps," affine maps; ",
  ctAdmitted," admitted weighted maps; ",ctNonbinary,
  " violate a weighted fresh-field equation; ",ctComparisons,
  " projected value/companion comparisons; ",ctNegative," negative controls.\n");
QUIT_GAP(0);
