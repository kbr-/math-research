# Independent native GAP checks: free identities, then path matrices selecting
# words without expanding free-word supports. Stages: symbolic identities;
# all binary words of lengths 1 and 3; omitted-prefix and syzygy controls.
# Expected: original certificate specializes to one and to zero at placeholders
# zero; the guarded prefix's path entry equals MOD3 in every enumerated word.
# Refuted by: a nonzero identity residual, a wrong path entry, or a surviving
# omitted-prefix or altered-syzygy control at its specified distinguishing input.
# Possible because: noncommutative factor order selects a different path, and
# dropping a necessary summand destroys the original certificate identity.
cqA := FreeAssociativeAlgebraWithOne(GF(2), "z", "q", "x", "y1", "y2");;
cqG := GeneratorsOfAlgebra(cqA);;
cqOne := One(cqA);; cqZero := Zero(cqA);;
cqZ := cqG[2];; cqQ := cqG[3];; cqX := cqG[4];;
cqY1 := cqG[5];; cqY2 := cqG[6];;
cqChecks := 0;; cqControls := 0;; cqQueries := 0;;
cqCheck := function(a,b)
  if a <> b then Print("FAIL identity or path entry\n"); QUIT_GAP(1); fi;
  cqChecks := cqChecks+1;
end;;
cqC := function(q,x,y1,y2,one) return y1+y2+q*(x*y1+y2*(one+x)); end;;
cqCheck(cqC(cqQ,cqX,cqOne+cqX,cqX,cqOne),cqOne);
cqCheck(cqC(cqQ,cqX,cqZero,cqZero,cqOne),cqZero);
cqB := cqZ+cqZ*cqZ;;
cqCheck((cqOne+cqB)*(cqOne+cqB*cqQ),
        cqOne+cqB+cqB*cqQ+cqB*cqB*cqQ);
if cqOne+cqX+cqX+cqQ*(cqX*(cqOne+cqX)+cqX*cqX)=cqOne then
  Print("FAIL altered syzygy control\n"); QUIT_GAP(1);
fi;
cqControls := cqControls+1;
if cqB*cqQ=cqQ*cqB then Print("FAIL order control\n"); QUIT_GAP(1); fi;
cqControls := cqControls+1;
cqRun := function(one,a,b,n)
  local zsum,t,out;
  zsum := Sum([0..n],j->a^j);
  out := 0*one;
  for t in [0..QuoInt(n,3)] do out := out+zsum*(b*zsum)^(3*t); od;
  return out;
end;;
for cqN in [1,3] do
  for cqBits in Tuples([0,1],cqN) do
    cqDim := cqN+2;
    cqI := IdentityMat(cqDim,GF(2));
    cqMZ := NullMat(cqDim,cqDim,GF(2)); cqMZ[1][2] := One(GF(2));
    cqM0 := NullMat(cqDim,cqDim,GF(2));
    cqM1 := NullMat(cqDim,cqDim,GF(2));
    for cqJ in [1..cqN] do
      if cqBits[cqJ]=0 then cqM0[cqJ+1][cqJ+2] := One(GF(2));
      else cqM1[cqJ+1][cqJ+2] := One(GF(2)); fi;
    od;
    cqMQ := cqRun(cqI,cqM0,cqM1,cqN);
    cqMB := cqMZ+cqMZ*cqMZ;
    cqMP := (cqI+cqMB)*(cqI+cqMB*cqMQ);
    cqExpected := Zero(GF(2));
    if Sum(cqBits) mod 3=0 then cqExpected := One(GF(2)); fi;
    cqCheck(cqMP[1][cqDim],cqExpected);
    cqQueries := cqQueries+1;
    Print("n=",cqN," bits=",cqBits," selected=",Int(cqMP[1][cqDim]),
          " expected=",Int(cqExpected),"\n");
    if ForAll(cqBits,b->b=0) then
      if (cqI+cqMB)[1][cqDim]=cqMP[1][cqDim] then
        Print("FAIL omitted prefix control\n"); QUIT_GAP(1);
      fi;
      cqControls := cqControls+1;
    fi;
  od;
od;
if cqChecks<>13 or cqQueries<>10 or cqControls<>4 then
  Print("FAIL completion counts\n"); QUIT_GAP(1);
fi;
Print("PASS: ",cqChecks," equalities including ",cqQueries,
      " native path-matrix queries; ",cqControls," negative controls.\n");
QUIT_GAP(0);
