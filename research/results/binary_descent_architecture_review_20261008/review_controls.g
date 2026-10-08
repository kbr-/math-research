# Bounded falsification controls for coefficient-incidence shortcuts.
# Boolean evaluations check identities only, not satisfiability of charged axioms.
F := GF(2);; o := One(F);; z := Zero(F);;
checks := 0;; a := [];;
for bits in Tuples([z,o],10) do
  for boundary in [true,false] do
    if boundary then
      t := z; w := bits[1]; a := List([1..10],i->z);
      a[1] := o-bits[1];
    else
      t := o; w := bits[1]*bits[6]; a := List([1..10],i->z);
      a[1] := o; a[6] := o;
    fi;
    for group in [[1..5],[6..10]] do
      p := t-Sum(group,i->a[i]*bits[i]);
      for i in group do
        if w*bits[i]*p <> z then Error("companion failure"); fi;
        if w*(a[i]^2-t*a[i]) <> z then Error("field failure"); fi;
        checks := checks+2;
      od;
    od;
  od;
od;
Print("Boolean identity comparisons: ",checks,"\n");
F4 := GF(4);;
roots := Filtered(Elements(F4),a->a^2-a=Zero(F4));;
torus := Filtered(roots,a->a<>Zero(F4));;
if Length(roots)<>2 or Length(torus)<>1 then Error("torus control"); fi;
Print("Field roots: ",roots,"; nonzero chart: ",torus,"\n");
u := Indeterminate(F,"u");;
N := [[o,o],[o,o]];;
if N*N<>NullMat(2,2,F) then Error("nilpotence"); fi;
Print("Feedback determinant diagnostic: ",DeterminantMat(IdentityMat(2,F)-u*N),"\n");
if DeterminantMat(IdentityMat(2,F)-u*N)<>One(u) then Error("feedback"); fi;
if DeterminantMat(IdentityMat(2,F)-IdentityMat(2,F))<>z then Error("free feedback"); fi;
Print("Coherent feedback determinant: 1; free identity feedback determinant: 0\n");
column := [[o],[o]];;
dilation := [[z,o,o],[o,z,z],[o,z,z]];;
kernel := NullspaceMat(dilation);;
if RankMat(column)<>1 or TransposedMat(column)*column<>[[z]] or RankMat(dilation)<>2
   or Length(kernel)<>1 or kernel[1][1]<>z then Error("marked kernel"); fi;
Print("Rectangular rank: ",RankMat(column),"; dilation rank: ",RankMat(dilation),
      "; kernel: ",kernel,"\n");
Print("PASS: all bounded architecture controls\n");
QUIT;
