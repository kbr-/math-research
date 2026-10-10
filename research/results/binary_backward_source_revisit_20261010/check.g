# One-bit Boolean actual error tuples, common normalized F4 moment.
# Four nonzero binary subspaces S and 16 ordered pairs of Boolean multipliers.
# Largest matrix is 4x4; all 64 maps, not a growing size series.
saF:=GF(4);; saO:=One(saF);; saZ:=Zero(saF);; saA:=PrimitiveElement(saF);;
saG:=[[saO,saA],[saA,saA]];;
saI:=IdentityMat(2,saF);;
saM:=[[saZ,saZ],[saO,saO]];;
saGs:=NullMat(4,4,saF);;
for saI1 in [1..2] do
  for saI2 in [1..2] do
    saGs[saI1][saI2]:=saG[saI1][saI2];
    saGs[2+saI1][2+saI2]:=saG[saI1][saI2];
  od;
od;
saSpaces:=[[[saO],[saZ]],[[saZ],[saO]],[[saO],[saO]],saI];;
saMult:=[0*saI,saI,saM,saI+saM];;
saCount:=0;; saKernels:=0;;
for saS in saSpaces do
  saB:=TransposedMat(saS)*saG*saS;;
  if DeterminantMat(saB)=saZ then Error("input form"); fi;
  saP:=saS*saB^-1*TransposedMat(saS)*saG;;
  for saE1 in saMult do
    for saE2 in saMult do
      saT:=Concatenation(saE1*saS,saE2*saS);;
      saAdj:=saB^-1*TransposedMat(saT)*saGs;;
      if saB*saAdj<>TransposedMat(saT)*saGs then Error("adjoint"); fi;
      if RankMat(saT*saAdj)<>RankMat(saT) then Error("squared rank"); fi;
      saRaw:=[Concatenation(saE1[1],saE2[1]),
              Concatenation(saE1[2],saE2[2])];;
      if saS*saAdj<>saP*saRaw then Error("common moment projection"); fi;
      saK:=NullspaceMat(TransposedMat(saT));;
      if Length(saK)>0 then
        if DeterminantMat(saK*saB*TransposedMat(saK))=saZ then
          Error("kernel degeneracy");
        fi;
        saKernels:=saKernels+1;
      fi;
      saCount:=saCount+1;
    od;
  od;
od;
# Negative control: the opposite Gram product can still vanish.
saS:=saSpaces[1];;
saT:=Concatenation(saI*saS,saI*saS);;
saAdj:=TransposedMat(saT)*saGs;;
if saAdj*saT<>NullMat(1,1,saF)
   or RankMat(saT*saAdj)<>1 then Error("opposite Gram control"); fi;
# Normalization alone does not give a nonsingular moment pairing.
if DeterminantMat([[saO,saZ],[saZ,saZ]])<>saZ then
  Error("singular moment negative control");
fi;
Print("PASS: ",saCount," actual tuple maps; ",saKernels,
      " nonzero kernel restrictions; common adjoints, projections and TT* ranks.\n");
Print("2 negative controls: T*T may vanish; normalized moment may be singular.\n");
QUIT;
