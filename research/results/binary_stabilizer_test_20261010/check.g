# Exact calibration of the D=2 truncated graded Boolean envelope.
# General hypothesis: the algebra is associative, connected graded, has only
# trivial idempotents, and its near-full degree space has a full stabilizer.
# This checks the smallest nontrivial boundary case, not an asymptotic bound.
# Stages: native structure constants; all 125 basis triples; all 32 elements;
# native product-space rank; untruncated one-bit positive control.
stRequire := function(ok, msg)
  if not ok then
    Print("FAIL: ", msg, "\n");
    QUIT_GAP(1);
  fi;
end;
stF := GF(2);;
stD := 2;;
stN := 1 + 2*stD;;
stRequire(stN=5 and 2^stN=32, "fixed exhaustive size");
Print("SIZE D=",stD," dimension=",stN," elements=",2^stN,
      " basis_triples=",stN^3,"\n");
stDeg := [0,1,1,2,2];;
stType := [0,0,1,0,1];;
stTable := EmptySCTable(stN,Zero(stF));;
for stI in [1..stN] do
  for stJ in [1..stN] do
    stK := stDeg[stI]+stDeg[stJ];
    if stK<=stD then
      if stK=0 then stTarget:=1;
      else stTarget:=2*stK+Maximum(stType[stI],stType[stJ]);
      fi;
      SetEntrySCTable(stTable,stI,stJ,[One(stF),stTarget]);
    fi;
  od;
od;
stA := AlgebraByStructureConstants(stF,stTable);;
stBasis := CanonicalBasis(stA);;
stV := BasisVectors(stBasis);;
stZero := Zero(stA);;
stUnit := stV[1];;
stAssoc := 0;;
for stI in stV do
  stRequire(stUnit*stI=stI and stI*stUnit=stI,"unit");
  for stJ in stV do
    for stK in stV do
      stRequire((stI*stJ)*stK=stI*(stJ*stK),"associativity");
      stAssoc:=stAssoc+1;
    od;
  od;
od;
stRequire(stV[3]*stV[3]=stV[2]*stV[3],"homogenized Booleanity x^2=z*x");
stRequire(stV[2]^3=stZero and stV[4]<>stZero,"z nilpotence and nonzero top");
stElems := List(Tuples([Zero(stF),One(stF)],stN),
                c->LinearCombination(stBasis,c));;
stIdems := Filtered(stElems, x->x*x=x);;
stRequire(Set(stIdems)=Set([stZero,stUnit]),"only trivial idempotents");
stPositive := Filtered(stElems, x->Coefficients(stBasis,x)[1]=Zero(stF));;
for stI in stPositive do
  stRequire(stI^3=stZero,"positive ideal cube zero");
od;
stProducts := [];;
for stI in stV{[1..3]} do
  for stJ in stV{[1..3]} do
    Add(stProducts,Coefficients(stBasis,stI*stJ));
  od;
od;
stRank := RankMat(stProducts);;
stRequire(stRank=stN,"degree-one product spans full envelope");
stOldTable:=EmptySCTable(2,Zero(stF));;
SetEntrySCTable(stOldTable,1,1,[One(stF),1]);
SetEntrySCTable(stOldTable,1,2,[One(stF),2]);
SetEntrySCTable(stOldTable,2,1,[One(stF),2]);
SetEntrySCTable(stOldTable,2,2,[One(stF),2]);
stOld:=AlgebraByStructureConstants(stF,stOldTable);;
stOldBasis:=CanonicalBasis(stOld);;
stOldElems:=List(Tuples([Zero(stF),One(stF)],2),
                 c->LinearCombination(stOldBasis,c));;
stOldCount:=Number(stOldElems,x->x*x=x);;
stRequire(stOldCount=4,"untruncated Boolean algebra has four idempotents");
Print("PASS basis_triples=",stAssoc," elements=",Length(stElems),
      " idempotents=",Length(stIdems)," positive_nilpotents=",Length(stPositive),
      " product_rank=",stRank," old_boolean_idempotents=",stOldCount,"\n");
QUIT_GAP(0);
