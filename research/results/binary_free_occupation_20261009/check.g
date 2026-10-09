# Exact reduction of the three-mode occupation matrices over F2.
# Eight basis states, three annihilation/creation pairs, and a three-state
# one-particle sector. This checks the imported encoding, not a PC rank estimate.
F := GF(2);; zero := Zero(F);; one := One(F);;
states := Tuples([0,1],3);;
dim := Length(states);;
Id := IdentityMat(dim,F);; occZeroMat := NullMat(dim,dim,F);;
ann := [];; cre := [];;
for j in [1..3] do
  mat := NullMat(dim,dim,F);
  for k in [1..dim] do
    if states[k][j]=1 then
      target := ShallowCopy(states[k]); target[j] := 0;
      mat[Position(states,target)][k] := one;
    fi;
  od;
  Add(ann,mat); Add(cre,TransposedMat(mat));
od;
pairChecks := 0;;
for i in [1..3] do
  if ann[i]^2<>occZeroMat or cre[i]^2<>occZeroMat then Error("nilpotence"); fi;
  for j in [1..3] do
    expected := occZeroMat; if i=j then expected:=Id; fi;
    if ann[i]*cre[j]+cre[j]*ann[i]<>expected then Error("mixed CAR"); fi;
    if ann[i]*ann[j]+ann[j]*ann[i]<>occZeroMat then Error("ann CAR"); fi;
    if cre[i]*cre[j]+cre[j]*cre[i]<>occZeroMat then Error("creation CAR"); fi;
    pairChecks:=pairChecks+3;
  od;
od;
sector := Filtered([1..dim],k->Sum(states[k])=1);;
outside := Difference([1..dim],sector);;
units := [];;
for i in [1..3] do
  units[i] := [];
  for j in [1..3] do
    op := cre[i]*ann[j];
    if op{outside}{sector}<>NullMat(Length(outside),Length(sector),F) then Error("sector leak"); fi;
    small := op{sector}{sector};
    expected := NullMat(3,3,F);
    target := Position(List(sector,k->states[k][i]),1);
    source := Position(List(sector,k->states[k][j]),1);
    expected[target][source] := one;
    if small<>expected then Error("matrix unit"); fi;
    units[i][j] := small;
  od;
od;
unitChecks:=0;;
for i in [1..3] do
  for j in [1..3] do
    for k in [1..3] do
      for l in [1..3] do
        expected:=NullMat(3,3,F); if j=k then expected:=units[i][l]; fi;
        if units[i][j]*units[k][l]<>expected then Error("unit multiplication"); fi;
        unitChecks:=unitChecks+1;
      od;
    od;
  od;
od;
if Sum([1..3],j->units[j][j])<>IdentityMat(3,F) then Error("one-hot identity"); fi;
PrintTo("research/results/binary_free_occupation_20261009/check.txt",
 "PASS\nfield=F2; occupation states=",dim,"; one-particle states=",Length(sector),
 "\nCAR pair identities=",pairChecks,"; individual nilpotence identities=6\n",
 "matrix units=9; matrix-unit product identities=",unitChecks,
 "\nAll bilinears preserve the one-particle sector; diagonal units sum to identity.\n");
QUIT;
