# Test seed masks and the unrestricted prefix-splicing scalar control.
# The normalized graph is checked separately; this does not enumerate its
# entire expanded compiled certificate or replace the parameter-wide proof.
# Predictions: every full mask vanishes, seed quotient coefficients have their
# independent binary/inverse values, and all placeholder-basis values agree.
# Refuted by: Any unequal coefficient or nonzero full-mask grid value.
# Possible because: Missing a variable block permits nonbinary source values,
# and the seed quotient or prefix indices can alter a placeholder coefficient.
# Control: remove the x seed block at x nonbinary,z0, first assert the full
# and altered masks differ, then verify the altered mask fails vanishing.
ppAssert:=function(ok,msg)
 if not ok then Print("FAILED ",msg,"\n"); QUIT_GAP(1); fi;
end;
ppR:=PolynomialRing(GF(2),["b"]);;
ppB:=IndeterminatesOfPolynomialRing(ppR)[1];;
ppOneP:=One(ppR);;
ppOut:=OutputTextFile("research/results/binary_powered_prefix_20261015/field-grid.txt",false);;
SetPrintFormattingStatus(ppOut,false);
AppendTo(ppOut,"q kind x z seedR1 seedR2 mask basis_coefficients lookup_coefficients\n");
ppPoints:=0;; ppBasis:=0;; ppControls:=0;; ppExpectedPoints:=0;; ppExpectedBasis:=0;;
ppZero:=0;; ppE:=0;;
for ppQ in [4,8] do
 ppK:=GF(ppQ); ppZero:=Zero(ppK); ppOne:=One(ppK); ppE:=ppQ-1;
 ppAssert(ppQ^2*6<1000,"finite grid size guard");
 ppPowers:=Concatenation(List([1..5],i->1),[2..ppE],List([1..ppE+1],i->ppE));
 ppAssert(Length(ppPowers)=2*ppE+5,"seed line count");
 ppMaskPoly:=ppOneP;
 for ppPower in ppPowers do ppMaskPoly:=ppMaskPoly*(ppOneP-ppB^ppPower); od;
 ppQR:=QuotientRemainder(ppOneP-ppMaskPoly,ppB);
 ppAssert(IsZero(ppQR[2]),"formal seed quotient");
 ppCoeffPoly:=ppQR[1];
 ppAssert(Value(ppCoeffPoly,Zero(GF(2)))=One(GF(2)),"binary seed coefficient");
 for ppKind in ["units","or_cut"] do
  if ppKind="units" then ppM:=2; else ppM:=3; fi;
  ppV:=ppM+3;
  ppExpectedPoints:=ppExpectedPoints+ppQ^2;
  ppExpectedBasis:=ppExpectedBasis+ppQ^2*ppV;
  for ppX in Elements(ppK) do
   for ppZ in Elements(ppK) do
    ppBX:=ppX^2+ppX; ppBZ:=ppZ^2+ppZ;
    ppRX:=Value(ppMaskPoly,ppBX); ppRZ:=Value(ppMaskPoly,ppBZ);
    ppCX:=Value(ppCoeffPoly,ppBX); ppCZ:=Value(ppCoeffPoly,ppBZ);
    ppBinaryX:=ppX=ppZero or ppX=ppOne;
    ppBinaryZ:=ppZ=ppZero or ppZ=ppOne;
    ppAssert((ppBinaryX and ppRX=ppOne) or (not ppBinaryX and ppRX=ppZero),"x flag");
    ppAssert((ppBinaryZ and ppRZ=ppOne) or (not ppBinaryZ and ppRZ=ppZero),"z flag");
    if ppKind="units" then ppF:=[ppOne+ppX,ppX];
    else ppF:=[(ppOne+ppX)*(ppOne+ppZ),ppX,ppZ]; fi;
    ppP:=ppOne;
    for ppFvalue in ppF do ppP:=ppP*(ppOne-ppFvalue); od;
    # Two complete input rounds precede each old-dependent reference.
    ppMask:=ppRX*ppRZ*ppP^2;
    ppAssert(ppMask=ppZero,"complete old-dependent mask");
    ppA:=List([1..ppV],i->ppZero);
    ppA[ppM+1]:=ppCX; ppA[ppM+2]:=ppRX*ppCZ;
    ppPrefix:=ppOne;
    for ppI in [1..ppM] do
      ppA[ppI]:=ppRX*ppRZ*(ppOne+ppP)*ppPrefix;
      ppPrefix:=ppPrefix*(ppOne-ppF[ppI]);
    od;
    ppLookup:=List([1..ppV],i->ppZero);
    if not ppBinaryX then ppLookup[ppM+1]:=Inverse(ppBX);
    elif not ppBinaryZ then
      ppLookup[ppM+1]:=ppOne; ppLookup[ppM+2]:=Inverse(ppBZ);
    else
      ppLookup[ppM+1]:=ppOne; ppLookup[ppM+2]:=ppOne;
      # Independently find the first violated original clause from truth bits.
      if ppKind="units" then
        if ppX=ppZero then ppFirst:=1; else ppFirst:=2; fi;
      else
        if ppX=ppZero and ppZ=ppZero then ppFirst:=1;
        elif ppX=ppOne then ppFirst:=2; else ppFirst:=3; fi;
      fi;
      for ppI in [1..ppFirst] do ppLookup[ppI]:=ppOne; od;
    fi;
    for ppI in [1..ppV] do
      ppAssert(ppA[ppI]=ppLookup[ppI],"placeholder basis scalar values");
      ppBasis:=ppBasis+1;
    od;
    if not ppBinaryX and ppZ=ppZero then
      ppOmitted:=ppRZ*ppP^2;
      ppAssert(ppOmitted<>ppMask,"omitted block changes the mask");
      ppAssert(ppOmitted<>ppZero,"altered mask fails vanishing");
      ppControls:=ppControls+1;
    fi;
    AppendTo(ppOut,ppQ," ",ppKind," ",ppX," ",ppZ," ",ppRX," ",ppRZ," ",ppMask,
             " ",ppA," ",ppLookup,"\n");
    ppPoints:=ppPoints+1;
   od;
  od;
 od;
od;
ppAssert(ppPoints=ppExpectedPoints and ppBasis=ppExpectedBasis and ppControls>0,"completion counts");
AppendTo(ppOut,"SUMMARY points=",ppPoints," basis=",ppBasis," controls=",ppControls,"\n");
CloseStream(ppOut);
Print("Full scalar old points: ",ppPoints,"\n");
Print("Placeholder-basis checks: ",ppBasis,"\n");
Print("Nonzero omitted-block controls: ",ppControls,"\n");
Print("PASS powered-prefix field completion\n");
QUIT_GAP(0);
