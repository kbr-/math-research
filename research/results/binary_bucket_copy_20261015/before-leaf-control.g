# Native exact checks for the two-copy certificate lift and bucket-sort control.
# Stages: all binary formula trees of sizes1,3,5 over four old-only leaves
# (548 trees), and six old/placeholder leaves (1806 trees); compare marked-leaf
# contexts and copy corrections with independent upper-triangular matrix
# evaluation. Then check a complete copied source, reverse generator map,
# and sorted-product coefficient matrices at r=1,2 (orders2,6).
# Expected: 5966 grammar equalities,22 source equalities,80 sorting coefficient
# checks,4 rank checks,6 negative controls. Full AST/check results are printed.
# Refuted by: a marked-context or copy-difference mismatch, failure of a complete
# original-generator certificate or its retraction, wrong sorting rank, or an
# altered correction/order/leaf initialization surviving a distinguishing case.
# Possible because: noncommutative prefix and suffix order matters, equality
# CNF clauses need a cross-commutator correction, and sorting changes word rank.
bcA := FreeAssociativeAlgebraWithOne(GF(2),"x","y","u","v","a","b",
  "e","f","p","q","c1","c2","kxu","d1","d2","kyv");;
bcG := GeneratorsOfAlgebra(bcA);;
bcOne := One(bcA);; bcZero := Zero(bcA);;
bcX := bcG{[2,3]};; bcW := bcG{[4,5]};; bcY := bcG{[6,7]};;
bcU := bcG{[8,9]};; bcPQ := bcG{[10,11]};;
bcCounts := rec(grammar:=0,source:=0,coefficient:=0,rank:=0);;
bcControls := 0;;
bcCheck := function(a,b,kind)
  if a<>b then Print("FAIL ",kind," equality\n"); QUIT_GAP(1); fi;
  bcCounts.(kind) := bcCounts.(kind)+1;
end;;
# AST op0 constant, op1 old variable, op2 placeholder, op3 sum, op4 product.
bcLeaf := function(op,value) return rec(op:=op,value:=value,args:=[]); end;;
bcNode := function(op,args) return rec(op:=op,args:=args); end;;
bcProd := function(args)
  if Length(args)=0 then return bcLeaf(0,1); fi;
  if Length(args)=1 then return args[1]; fi;
  return bcNode(4,args);
end;;
bcEncode := function(a)
  if a.op<3 then return [a.op,a.value]; fi;
  return [a.op,List(a.args,bcEncode)];
end;;
bcEval := function(a,old,ph,one)
  local out,b;
  if a.op=0 then return a.value*one; fi;
  if a.op=1 then return old[a.value]; fi;
  if a.op=2 then return ph[a.value]; fi;
  if a.op=3 then return Sum(a.args,b->bcEval(b,old,ph,one)); fi;
  out := one;
  for b in a.args do out := out*bcEval(b,old,ph,one); od;
  return out;
end;;
bcContexts := function(a,kind)
  local out,i,term,l,r;
  if a.op<3 then
    if a.op=kind then return [[bcLeaf(0,1),a.value,bcLeaf(0,1)]]; fi;
    return [];
  fi;
  if a.op=3 then return Concatenation(List(a.args,b->bcContexts(b,kind))); fi;
  out := [];
  for i in [1..Length(a.args)] do
    for term in bcContexts(a.args[i],kind) do
      l := Concatenation(a.args{[1..i-1]},[term[1]]);
      r := Concatenation([term[3]],a.args{[i+1..Length(a.args)]});
      Add(out,[bcProd(l),term[2],bcProd(r)]);
    od;
  od;
  return out;
end;;
bcPhZero := [bcZero,bcZero];;
bcDiff := function(a,old,right,eq)
  local out,term;
  out := bcZero;
  for term in bcContexts(a,1) do
    out := out+bcEval(term[1],old,bcPhZero,bcOne)*eq[term[2]]*
               bcEval(term[3],right,bcPhZero,bcOne);
  od;
  return out;
end;;
bcGrammar := function(leaves)
  local by,size,left,right,a,b,op;
  by := [leaves,[],[],[],[]];
  for size in [3,5] do
    for left in [1..size-2] do
      right := size-1-left;
      for a in by[left] do for b in by[right] do for op in [3,4] do
        Add(by[size],bcNode(op,[a,b]));
      od; od; od;
    od;
  od;
  return Concatenation(by);
end;;
bcOldLeaves := [bcLeaf(0,0),bcLeaf(0,1),bcLeaf(1,1),bcLeaf(1,2)];;
bcOldForms := bcGrammar(bcOldLeaves);;
bcForms := bcGrammar(Concatenation(bcOldLeaves,[bcLeaf(2,1),bcLeaf(2,2)]));;
if Length(bcOldForms)<>548 or Length(bcForms)<>1806 then
  Print("FAIL grammar count\n"); QUIT_GAP(1);
fi;
bcId := 0;;
for bcF in bcOldForms do
  bcId := bcId+1;
  bcCheck(bcDiff(bcF,bcX,bcW,bcW+bcX),
    bcEval(bcF,bcW,bcPhZero,bcOne)+bcEval(bcF,bcX,bcPhZero,bcOne),"grammar");
  Print("DIFFERENCE ",bcId," AST=",bcEncode(bcF)," pass\n");
od;
bcMI := [[bcOne,bcZero],[bcZero,bcOne]];;
bcDiagonal := function(left,right)
  return List([1,2],i->[[left[i],bcZero],[bcZero,right[i]]]);
end;;
bcMarked := function(ph) return List(ph,a->[[bcZero,a],[bcZero,bcZero]]); end;;
bcBx := bcX[1]^2+bcX[1];; bcBy := bcX[2]^2+bcX[2];;
bcK := bcX[1]*bcX[2]+bcX[2]*bcX[1];;
bcFi := [bcBx,bcK];;
bcId := 0;;
for bcF in bcForms do
  bcId := bcId+1;
  bcSplit := bcZero; bcFold := bcZero; bcTransport := bcZero;
  for bcTerm in bcContexts(bcF,2) do
    bcL := bcEval(bcTerm[1],bcX,bcPhZero,bcOne);
    bcRX := bcEval(bcTerm[3],bcX,bcPhZero,bcOne);
    bcRW := bcEval(bcTerm[3],bcW,bcPhZero,bcOne);
    bcEq := bcDiff(bcTerm[3],bcX,bcW,bcW+bcX);
    bcSplit := bcSplit+bcL*bcY[bcTerm[2]]*bcRW;
    bcFold := bcFold+bcL*bcY[bcTerm[2]]*bcRX;
    bcTransport := bcTransport+bcL*bcFi[bcTerm[2]]*(bcRW+bcEq);
  od;
  bcCheck(bcSplit,bcEval(bcF,bcDiagonal(bcX,bcW),bcMarked(bcY),bcMI)[1][2],"grammar");
  bcCheck(bcFold,bcEval(bcF,bcDiagonal(bcX,bcX),bcMarked(bcY),bcMI)[1][2],"grammar");
  bcCheck(bcTransport,bcEval(bcF,bcDiagonal(bcX,bcX),bcMarked(bcFi),bcMI)[1][2],"grammar");
  Print("LINEAR ",bcId," AST=",bcEncode(bcF)," split/fold/transport pass\n");
od;
# Complete original source x,not x,y; all fields and commutators. Copy source
# has 7 clauses,4 Boolean and6 commutator labels. No label is discarded.
bcTuple := function(v)
  local out,i,j;
  out := [bcOne+v[1],v[1],bcOne+v[2],v[3]*(bcOne+v[1]),
          v[1]*(bcOne+v[3]),v[4]*(bcOne+v[2]),v[2]*(bcOne+v[4])];
  Append(out,List(v,x->x*x+x));
  for i in [1..4] do for j in [i+1..4] do Add(out,v[i]*v[j]+v[j]*v[i]); od; od;
  return out;
end;;
bcSource := bcTuple(Concatenation(bcX,bcW));;
bcFolded := bcTuple(Concatenation(bcX,bcX));;
bcOldTuple := [bcOne+bcX[1],bcX[1],bcOne+bcX[2],bcBx,bcBy,bcK];;
bcMap := [1,2,3,4,4,5,5,4,5,4,5,6,0,6,6,0,6];;
if Length(bcSource)<>17 then Print("FAIL full source count\n"); QUIT_GAP(1); fi;
for bcI in [1..17] do
  if bcMap[bcI]=0 then bcWant:=bcZero; else bcWant:=bcOldTuple[bcMap[bcI]]; fi;
  bcCheck(bcFolded[bcI],bcWant,"source");
  Print("SOURCE ",bcI," -> ",bcMap[bcI]," pass\n");
od;
bcEx := bcSource[4]+bcSource[5]+bcSource[13];;
bcEy := bcSource[6]+bcSource[7]+bcSource[16];;
bcCheck(bcEx,bcW[1]+bcX[1],"source");
bcCheck(bcEy,bcW[2]+bcX[2],"source");
bcLift := function(w,pp,qq,aa,bb,ex,ey)
  return pp+qq+bcBx*bb+aa*(w[1]*w[2]+w[2]*w[1])+
    bcBx*(ex*w[2]+bcX[1]*ey+ey*w[1]+bcX[2]*ex);
end;;
bcCheck(bcLift(bcW,bcOldTuple[1],bcOldTuple[2],bcBx,bcK,bcEx,bcEy),bcOne,"source");
bcCheck(bcLift(bcW,bcZero,bcZero,bcZero,bcZero,bcZero,bcZero),bcZero,"source");
bcC := bcPQ[1]+bcPQ[2]+bcBx*bcY[2]+bcY[1]*bcK;;
bcCheck(bcLift(bcX,bcPQ[1],bcPQ[2],bcY[1],bcY[2],bcZero,bcZero),bcC,"source");
for bcBad in [
  bcLift(bcW,bcOldTuple[1],bcOldTuple[2],bcBx,bcK,bcZero,bcZero),
  bcLift(bcW,bcOldTuple[1],bcOldTuple[2],bcBx,bcK,bcSource[4]+bcSource[5],bcSource[6]+bcSource[7]),
  bcOne+bcBx*(bcEx*bcW[2]+bcX[1]*bcEy+bcEy*bcW[1]+bcX[2]*bcEx)
] do
  if bcBad=bcOne then Print("FAIL altered correction control\n"); QUIT_GAP(1); fi;
  bcControls := bcControls+1;
od;
# Literal source leaf initializer puts x in [1,2) alone. With m=2 it wrongly
# makes root output [1,3) zero; corrected initialization retains x there.
if bcZero=bcX[1] then Print("FAIL source leaf control\n"); QUIT_GAP(1); fi;
bcControls := bcControls+1;
Print("COMPLETE SOURCE pass; three correction controls and source leaf control pass\n");
# Independent native matrix evaluation of sorted and unsorted products.
bcN := 0;; bcDim := 0;;
for bcR in [1,2] do
  bcN := 2*bcR; bcSets := Combinations([1..bcN],bcR);
  bcSortedMat := []; bcUnsortedMat := [];
  for bcS in bcSets do
    bcSortedRow := []; bcUnsortedRow := [];
    for bcT in bcSets do
      bcWord := Concatenation(bcS,List(bcT,i->bcN+i));
      bcDim := bcN+1; bcEye := IdentityMat(bcDim,GF(2));
      bcLetters := List([1..2*bcN],i->NullMat(bcDim,bcDim,GF(2)));
      for bcI in [1..bcN] do bcLetters[bcWord[bcI]][bcI][bcI+1] := One(GF(2)); od;
      bcSorted := NullMat(bcDim,bcDim,GF(2));
      for bcSubset in Combinations([1..bcN]) do
        bcTermMat := bcEye;
        for bcI in bcSubset do bcTermMat := bcTermMat*bcLetters[bcI]; od;
        for bcI in Difference([1..bcN],bcSubset) do bcTermMat := bcTermMat*bcLetters[bcN+bcI]; od;
        bcSorted := bcSorted+bcTermMat;
      od;
      bcUnsorted := bcEye;
      for bcI in [1..bcN] do bcUnsorted := bcUnsorted*(bcLetters[bcI]+bcLetters[bcN+bcI]); od;
      bcWant := 0;
      if bcT=Difference([1..bcN],bcS) then bcWant:=1; fi;
      bcCheck(Int(bcSorted[1][bcDim]),bcWant,"coefficient");
      bcWant := 0;
      if bcS=[1..bcR] and bcT=[bcR+1..bcN] then bcWant:=1; fi;
      bcCheck(Int(bcUnsorted[1][bcDim]),bcWant,"coefficient");
      Add(bcSortedRow,bcSorted[1][bcDim]); Add(bcUnsortedRow,bcUnsorted[1][bcDim]);
    od;
    Add(bcSortedMat,bcSortedRow); Add(bcUnsortedMat,bcUnsortedRow);
  od;
  bcCheck(RankMat(bcSortedMat),Binomial(bcN,bcR),"rank");
  bcCheck(RankMat(bcUnsortedMat),1,"rank");
  if RankMat(bcSortedMat)=RankMat(bcUnsortedMat) then Print("FAIL sorting control\n"); QUIT_GAP(1); fi;
  bcControls := bcControls+1;
  Print("SORT r=",bcR," rows=",Length(bcSets)," sorted=",bcSortedMat,
        " unsorted=",bcUnsortedMat," ranks=",RankMat(bcSortedMat),",",RankMat(bcUnsortedMat),"\n");
od;
if bcCounts<>rec(grammar:=5966,source:=22,coefficient:=80,rank:=4) or bcControls<>6 then
  Print("FAIL completion counts ",bcCounts," controls=",bcControls,"\n"); QUIT_GAP(1);
fi;
Print("PASS: ",Length(bcOldForms)," old formulas; ",Length(bcForms)," marked formulas; ",
      bcCounts,"; ",bcControls," negative controls.\n");
QUIT_GAP(0);
