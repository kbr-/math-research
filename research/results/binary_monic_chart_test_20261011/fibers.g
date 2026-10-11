# Prediction: varying one coefficient coordinate in a spare row preserves
# every weighted product and companion of the three-block source below.
# The active row is moved to the other row before the variation. Original
# parent coefficient maps remain fixed; only their source inputs are rebuilt.
# Exhaust 3 blocks, 2 target rows, 2 input slots, the 4 multilinear monomials
# on 2 old bits, and all GF(4) scalars. Check all four old Boolean points.
# Independent oracle: canonical products are [(1+x)(1+y),0,xy].
# Controls must distinguish active-row variation, raw coefficient readers,
# and the omitted fresh-field equations. No degree extrapolation is claimed.
sfF := GF(4);; sfOne := One(sfF);; sfZero := Zero(sfF);;
sfBits := [sfZero,sfOne];; sfPoints := Tuples(sfBits,2);;
sfCheck := function(a,b)
  if a<>b then Print("FAIL identity\n"); QUIT_GAP(1); fi;
end;;
sfValues := function(rows,x,y)
  local p,g,a,k,b,u;
  p := Product(List([1,2],u->sfOne-rows[1][u][1]*x-rows[1][u][2]*y));
  g := [x+p,y+p];
  a := Product(List([1,2],u->sfOne-rows[2][u][1]*g[1]-rows[2][u][2]*g[2]));
  k := [p,x+y];
  b := Product(List([1,2],u->sfOne-rows[3][u][1]*k[1]-rows[3][u][2]*k[2]));
  return [p,a,b,x*p,y*p,g[1]*a,g[2]*a,k[1]*b,k[2]*b];
end;;
sfRows := function(x,y,block,target)
  local p,active,rows,j,rr;
  p := (sfOne+x)*(sfOne+y);
  active := [[sfOne,sfOne+x],[sfOne,sfOne+x+p],[sfOne,sfOne+p]];
  rows := List([1..3],j->[[sfZero,sfZero],[sfZero,sfZero]]);
  for j in [1..3] do
    rr := 1; if j=block then rr:=3-target; fi;
    rows[j][rr] := ShallowCopy(active[j]);
  od;
  return rows;
end;;
sfCases:=0;; sfComparisons:=0;; sfNegatives:=0;;
for sfBlock in [1..3] do
  for sfTarget in [1,2] do
    for sfInput in [1,2] do
      for sfMono in [1..4] do
        for sfLambda in Elements(sfF) do
          sfCases:=sfCases+1;
          for sfPoint in sfPoints do
            sfX:=sfPoint[1]; sfY:=sfPoint[2];
            sfMaps:=sfRows(sfX,sfY,sfBlock,sfTarget);
            sfM:=[sfOne,sfX,sfY,sfX*sfY][sfMono];
            sfMaps[sfBlock][sfTarget][sfInput]:=sfLambda*sfM;
            sfExpected:=[(sfOne+sfX)*(sfOne+sfY),sfZero,sfX*sfY,
              sfZero,sfZero,sfZero,sfZero,sfZero,sfZero];
            sfGot:=sfValues(sfMaps,sfX,sfY);
            sfCheck(sfGot,sfExpected);
            sfComparisons:=sfComparisons+Length(sfGot);
          od;
        od;
      od;
    od;
  od;
od;
# Move the perturbation to the active bottom row; x=1,y=0 distinguishes it.
sfMaps:=sfRows(sfOne,sfZero,1,2);;
sfMaps[1][1][1]:=sfZero;
if sfValues(sfMaps,sfOne,sfZero)[4]=sfZero then
  Print("FAIL active-row control\n"); QUIT_GAP(1);
fi;
sfNegatives:=sfNegatives+1;
# A later all-zero-row block reading the raw spare coefficient changes.
sfBefore:=sfRows(sfOne,sfZero,1,2);;
sfAfter:=StructuralCopy(sfBefore);; sfAfter[1][2][1]:=sfOne;;
sfCheck(sfValues(sfAfter,sfOne,sfZero),sfValues(sfBefore,sfOne,sfZero));
sfRawComp:=function(r) return r*(sfOne-sfZero*r)*(sfOne-sfZero*r); end;;
sfCheck(sfRawComp(sfBefore[1][2][1]),sfZero);
if sfRawComp(sfAfter[1][2][1])=sfZero then
  Print("FAIL raw-reader control\n"); QUIT_GAP(1);
fi;
sfNegatives:=sfNegatives+1;
# A nonbinary spare coefficient violates its weighted field equation at W=1.
sfAlpha:=Z(4);;
sfAfter:=StructuralCopy(sfBefore);; sfAfter[1][2][1]:=sfAlpha;;
sfCheck(sfValues(sfAfter,sfOne,sfZero),sfValues(sfBefore,sfOne,sfZero));
if sfAfter[1][2][1]^2-sfAfter[1][2][1]=sfZero then
  Print("FAIL fresh-field control\n"); QUIT_GAP(1);
fi;
sfNegatives:=sfNegatives+1;
# Evaluation coordinates really are an invertible change of scalar parameters.
sfEval:=List(sfPoints,p->[sfOne,p[1],p[2],p[1]*p[2]]);;
sfCheck(RankMat(sfEval),4);
Print("PASS: ",sfCases," spare-row perturbations; ",sfComparisons,
  " product/companion comparisons; evaluation rank ",RankMat(sfEval),
  "; ",sfNegatives," negative controls.\n");
QUIT_GAP(0);
