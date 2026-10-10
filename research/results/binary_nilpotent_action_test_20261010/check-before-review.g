# Boolean face conjugation over F_2. Exhaust all basis columns for m=1..4:
# M_i^dual e_H = 1_(i in H)(e_H+e_(H-i)); Z e_H=sum_(S subset H)e_S.
# Test Z^2=I, (Z-I)^2=0, M_i=Z D_i Z, and the transpose selector formula.
# This is a full fresh Boolean algebra, not an augmented PC quotient.
bfField := GF(2);;
bfCases := 0;; bfColumns := 0;; bfSelectors := 0;;
for bfM in [1..4] do
  bfSets := Combinations([1..bfM]);;
  bfN := Length(bfSets);;
  bfZ := NullMat(bfN,bfN,bfField);;
  for bfH in [1..bfN] do
    for bfS in [1..bfN] do
      if IsSubset(bfSets[bfH],bfSets[bfS]) then
        bfZ[bfS][bfH] := One(bfField);
      fi;
    od;
  od;
  bfId := IdentityMat(bfN,bfField);;
  if bfZ*bfZ <> bfId or (bfZ-bfId)^2 <> 0*bfId then
    Error("incidence inverse or nilpotence");
  fi;
  for bfI in [1..bfM] do
    bfD := NullMat(bfN,bfN,bfField);;
    bfMop := NullMat(bfN,bfN,bfField);;
    for bfH in [1..bfN] do
      if bfI in bfSets[bfH] then
        bfD[bfH][bfH] := One(bfField);
        bfMop[bfH][bfH] := One(bfField);
        bfS := Position(bfSets,Difference(bfSets[bfH],[bfI]));;
        bfMop[bfS][bfH] := One(bfField);
      fi;
    od;
    if bfMop <> bfZ*bfD*bfZ or bfMop^2 <> bfMop then
      Error("actual multiplication conjugation");
    fi;
    bfColumns := bfColumns+bfN;
  od;
  # The coefficient of r_H in Z^vee(r_S) is one exactly for H containing S.
  # Independently evaluate that polynomial on all Boolean points.
  for bfS in [1..bfN] do
    for bfA in [1..bfN] do
      bfValue := Zero(bfField);;
      for bfH in [1..bfN] do
        if IsSubset(bfSets[bfA],bfSets[bfH]) then
          bfValue := bfValue+bfZ[bfS][bfH];
        fi;
      od;
      bfExpected := Zero(bfField);;
      if bfSets[bfA]=bfSets[bfS] then bfExpected:=One(bfField); fi;
      if bfValue<>bfExpected then Error("transpose point selector"); fi;
    od;
    if bfZ[bfS][Position(bfSets,[1..bfM])]<>One(bfField) then
      Error("missing full-degree coefficient");
    fi;
    bfSelectors := bfSelectors+1;
  od;
  bfEmpty := Position(bfSets,[]);;
  bfSingleton := Position(bfSets,[1]);;
  if bfZ[bfEmpty][bfSingleton]<>One(bfField) then
    Error("normalization negative control");
  fi;
  bfCases:=bfCases+1;
  Print("m=",bfM," dimension=",bfN," PASS\n");
od;
Print("PASS ",bfCases," algebras; ",bfColumns,
      " multiplication basis columns; ",bfSelectors,
      " full-degree point selectors; 4 normalization negative controls.\n");
QUIT;
