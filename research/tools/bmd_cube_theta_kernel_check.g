# Independent GAP check of the PARI transfer matrix and binary kernel.
# The inputs are transcribed exactly from the retained complete cellular output.
TransferMatrix := [
[0,0,-1,1,1,-1,0,0,-1,0],
[0,0,0,-1,0,1,1,0,1,0],
[0,0,-1,0,-1,0,1,0,0,0],
[-1,-1,1,1,0,1,0,0,0,1],
[1,1,-1,-1,0,0,0,-1,0,0],
[1,1,0,-1,-1,0,1,-1,0,0],
[-1,0,0,2,1,-1,-1,1,0,0],
[-1,0,1,1,0,0,-1,1,-1,0],
[1,0,-1,0,0,0,0,0,0,-1],
[0,-1,1,1,1,0,-1,1,0,1]];
KernelColumns := [
[1,1,0,0,1],[0,1,0,1,0],
[1,1,0,0,0],[0,1,1,1,1],
[1,0,0,0,0],[0,0,1,0,1],
[0,1,0,0,0],[0,0,1,0,0],
[0,0,0,1,0],[0,0,0,0,1]];
det := DeterminantMat(TransferMatrix);
sn := SmithNormalFormIntegerMat(TransferMatrix);
diagonal := List([1..10],i->sn[i][i]);
if AbsInt(det)<>32 or diagonal<>[1,1,1,1,1,2,2,2,2,2] then
 Error("integer transfer certificate failed");fi;
mf := TransferMatrix*One(GF(2)); kf := KernelColumns*One(GF(2));
if RankMat(mf)<>5 or RankMat(kf)<>5 or
 mf*kf<>NullMat(10,5,GF(2)) then Error("binary kernel failed");fi;
symp := NullMat(10,10,GF(2));
for j in [1..5] do symp[2*j-1][2*j]:=One(GF(2));symp[2*j][2*j-1]:=One(GF(2));od;
if TransposedMat(kf)*symp*kf<>NullMat(5,5,GF(2)) then Error("isotropy failed");fi;
weights := [0,0,0,0,0,0];
for bits in Tuples([Zero(GF(2)),One(GF(2))],5) do
 v := kf*bits;
 wt := Number([1..5],j->v[2*j-1]<>Zero(GF(2)) or v[2*j]<>Zero(GF(2)));
 weights[wt+1]:=weights[wt+1]+1;
od;
if weights<>[1,0,0,10,15,6] then Error("block weight certificate failed");fi;
Print("Transfer determinant: ",det,"\nSmith diagonal: ",diagonal,
 "\nBinary ranks: ",RankMat(mf),", ",RankMat(kf),
 "\nBlock weights 0 through 5: ",weights,"\nPASS independent GAP check\n");
QUIT;
