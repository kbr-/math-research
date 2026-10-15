# Exhaustive bounded grammar check of homogeneous word-query leaf selection.
# Stages: every constant/letter leaf; every binary-root formula of 3 or 5 nodes;
# every ternary-root formula of 4 nodes. Equal degrees at sums, additive at
# products, degree<=3. Compare the typed leaf-position evaluator to native GAP
# path-matrix evaluation, which selects the free coefficient independently.
# Expected: 380 typed formulas, 998 queries on all words of their degree;
# reject a mixed-degree sum and malformed leaf label; detect a wrong offset.
# Refuted by: a query disagreement, a grammar count mismatch, or an invalid
# degree annotation or offset accepted by the corresponding changed control.
# Possible because: product offsets must accumulate child degrees and sums
# must retain one common interval; removing either changes word coefficients.
iqCount := 0;; iqControls := 0;;
iqLeaf := function(op,value)
  return rec(op:=op,value:=value,args:=[],deg:=op,size:=1);
end;;
iqNode := function(op,args)
  local ds,d;
  ds := List(args,a->a.deg);
  if op=2 then
    if not ForAll(ds,x->x=ds[1]) then return fail; fi;
    d := ds[1];
  else d := Sum(ds); fi;
  if d>3 then return fail; fi;
  return rec(op:=op,args:=args,deg:=d,size:=1+Sum(args,a->a.size));
end;;
iqTyped := function(a)
  if a.op<2 then return a.deg=a.op and a.size=1; fi;
  if not ForAll(a.args,iqTyped) then return false; fi;
  if a.op=2 then return ForAll(a.args,b->b.deg=a.deg); fi;
  return Sum(a.args,b->b.deg)=a.deg;
end;;
iqSelect := function(a,word,start)
  local out,b,off;
  if a.op=0 then return a.value; fi;
  if a.op=1 then return Int(word[start]=a.value); fi;
  if a.op=2 then return Sum(a.args,b->iqSelect(b,word,start)) mod 2; fi;
  out := 1; off := start;
  for b in a.args do
    out := out*iqSelect(b,word,off); off := off+b.deg;
  od;
  return out;
end;;
iqMatrix := function(a,mats,one)
  local out,b;
  if a.op=0 then return a.value*one; fi;
  if a.op=1 then return mats[a.value+1]; fi;
  if a.op=2 then return Sum(a.args,b->iqMatrix(b,mats,one)); fi;
  out := one;
  for b in a.args do out := out*iqMatrix(b,mats,one); od;
  return out;
end;;
iqEncode := function(a)
  if a.op<2 then return [a.op,a.value]; fi;
  return [a.op,List(a.args,iqEncode)];
end;;
iqBySize := [List([0,1],x->iqLeaf(0,x)),[],[],[],[]];;
Append(iqBySize[1],List([0,1],x->iqLeaf(1,x)));
for iqSize in [3,5] do
  for iqLeft in [1..iqSize-2] do
    iqRight := iqSize-1-iqLeft;
    for iqA in iqBySize[iqLeft] do
      for iqB in iqBySize[iqRight] do
        for iqOp in [2,3] do
          iqF := iqNode(iqOp,[iqA,iqB]);
          if iqF<>fail then Add(iqBySize[iqSize],iqF); fi;
        od;
      od;
    od;
  od;
od;
for iqArgs in Tuples(iqBySize[1],3) do
  for iqOp in [2,3] do
    iqF := iqNode(iqOp,iqArgs);
    if iqF<>fail then Add(iqBySize[4],iqF); fi;
  od;
od;
iqForms := Concatenation(iqBySize);;
iqDegrees := List([0..3],d->Number(iqForms,a->a.deg=d));;
if Length(iqForms)<>380 or iqDegrees<>[90,174,92,24] then
  Print("FAIL grammar counts\n"); QUIT_GAP(1);
fi;
iqId := 0;;
for iqF in iqForms do
  if not iqTyped(iqF) then Print("FAIL type check\n"); QUIT_GAP(1); fi;
  iqId := iqId+1;
  Print("FORM ",iqId," degree=",iqF.deg," AST=",iqEncode(iqF),"\n");
  for iqWord in Tuples([0,1],iqF.deg) do
    iqDim := iqF.deg+1;
    iqI := IdentityMat(iqDim,GF(2));
    iqMats := [NullMat(iqDim,iqDim,GF(2)),NullMat(iqDim,iqDim,GF(2))];
    for iqJ in [1..iqF.deg] do
      iqMats[iqWord[iqJ]+1][iqJ][iqJ+1] := One(GF(2));
    od;
    iqExpected := Int(iqMatrix(iqF,iqMats,iqI)[1][iqDim]);
    iqActual := iqSelect(iqF,iqWord,1);
    if iqExpected<>iqActual then Print("FAIL selected coefficient\n"); QUIT_GAP(1); fi;
    iqCount := iqCount+1;
    Print("QUERY ",iqId," ",iqWord," matrix=",iqExpected," selected=",iqActual,"\n");
  od;
od;
iqX := iqLeaf(1,0);; iqY := iqLeaf(1,1);;
iqXY := iqNode(3,[iqX,iqY]);;
if iqNode(2,[iqX,iqXY])<>fail then
  Print("FAIL mixed-degree control\n"); QUIT_GAP(1);
fi;
iqControls := iqControls+1;
iqBadLeaf := iqLeaf(0,1);; iqBadLeaf.deg := 1;;
if iqTyped(iqBadLeaf) then Print("FAIL malformed leaf control\n"); QUIT_GAP(1); fi;
iqControls := iqControls+1;
iqWord := [0,1];;
iqWrong := iqSelect(iqX,iqWord,1)*iqSelect(iqY,iqWord,1);;
if iqSelect(iqXY,iqWord,1)<>1 or iqWrong<>0 then
  Print("FAIL changed offset control\n"); QUIT_GAP(1);
fi;
iqControls := iqControls+1;
if iqCount<>998 or iqControls<>3 then Print("FAIL completion counts\n"); QUIT_GAP(1); fi;
Print("PASS: ",Length(iqForms)," typed formulas, degree counts ",iqDegrees,
      "; ",iqCount," native path-matrix coefficient checks; ",iqControls," negative controls.\n");
QUIT_GAP(0);
