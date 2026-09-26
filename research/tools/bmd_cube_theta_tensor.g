# Fixed exact test of the actual gluing kernel's tensor and all 32 characters.
# Uses GAP rational/cyclotomic matrix arithmetic; no branch-parameter sweep.
# Tensor factor one is the most significant bit of a basis-state index.
Id2 := IdentityMat(2,Rationals);
PauliX := [[0,1],[1,0]];
PauliZ := [[1,0],[0,-1]];
PauliY := [[0,-E(4)],[E(4),0]];
Id32 := IdentityMat(32,Rationals);
KernelGenerators := [
 [1,0,1,0,1,0,0,0,0,0],
 [1,1,1,1,0,0,1,0,0,0],
 [0,0,0,1,0,1,0,1,0,0],
 [0,1,0,1,0,0,0,0,1,0],
 [1,0,0,1,0,1,0,0,0,1]];
PauliTensor := function(v)
 local parts,j,x,z;
 parts:=[];
 for j in [1..5] do
  x:=v[2*j-1];z:=v[2*j];
  if x=0 and z=0 then Add(parts,Id2);
  elif x=1 and z=0 then Add(parts,PauliX);
  elif x=0 and z=1 then Add(parts,PauliZ);
  else Add(parts,PauliY);fi;
 od;
 return Iterated(parts,KroneckerProduct);
end;
SymplecticBit := function(u,v)
 return Sum([1..5],j->u[2*j-1]*v[2*j]+u[2*j]*v[2*j-1]) mod 2;
end;
Stabilizers := List(KernelGenerators,PauliTensor);
for j in [1..5] do
 if Stabilizers[j]^2<>Id32 then Error("not an involution");fi;
 for k in [1..5] do
  if Stabilizers[j]*Stabilizers[k]<>Stabilizers[k]*Stabilizers[j] then
   Error("noncommuting generators");fi;
 od;
od;
Projector := Id32;
for s in Stabilizers do Projector:=Projector*(Id32+s)/2;od;
if Projector^2<>Projector or RankMat(Projector)<>1 then Error("bad projector");fi;
firstcol:=First([1..32],j->ForAny([1..32],i->Projector[i][j]<>0));
ThetaState:=List([1..32],i->Projector[i][firstcol]);
firstnz:=First(ThetaState,x->x<>0);
ThetaState:=ThetaState/firstnz;
if not ForAll(ThetaState,x->x in [-1,0,1]) then Error("unexpected coefficients");fi;
for s in Stabilizers do if s*ThetaState<>ThetaState then Error("state not invariant");fi;od;
ThetaAffineVars:=List([1..5],j->Indeterminate(Rationals,Concatenation("u",String(j))));
ThetaMonomial:=function(b)
 return Product([1..5],j->ThetaAffineVars[j]^(QuoInt(b,2^(5-j)) mod 2));
end;
ThetaExpanded:=Sum([0..31],b->ThetaState[b+1]*ThetaMonomial(b));
ThetaCompact:=
 (1-ThetaAffineVars[3]*ThetaAffineVars[4])*(1+ThetaAffineVars[5])
 +ThetaAffineVars[2]*(ThetaAffineVars[3]+ThetaAffineVars[4])*(1-ThetaAffineVars[5])
 +ThetaAffineVars[1]*(
 (1+ThetaAffineVars[3]*ThetaAffineVars[4])*(1-ThetaAffineVars[5])
 +ThetaAffineVars[2]*(ThetaAffineVars[3]-ThetaAffineVars[4])*(1+ThetaAffineVars[5]));
if ThetaCompact<>ThetaExpanded then Error("compact theta polynomial mismatch");fi;
Print("SIZE: five qubits, 32 basis states, 1024 Pauli labels, 32 characters\n");
Print("COMPACT_POLYNOMIAL_EXPANDED=",ThetaExpanded,"\n");
Print("POSITIVE_STATE_COEFFICIENTS=",ThetaState,"\n");
Print("NONZERO_TENSOR_TERMS=[\n");
for b in [0..31] do
 if ThetaState[b+1]<>0 then
  Print("  ",[List([1..5],i->QuoInt(b,2^(5-i)) mod 2),ThetaState[b+1]],",\n");
 fi;
od;
Print("]\n");
CharacterRepresentatives:=List([1..32],i->fail);
for mask in [0..1023] do
 label:=List([1..10],i->QuoInt(mask,2^(i-1)) mod 2);
 character:=List(KernelGenerators,v->SymplecticBit(label,v));
 ci:=1+Sum([1..5],j->character[j]*2^(j-1));
 if CharacterRepresentatives[ci]=fail then CharacterRepresentatives[ci]:=label;fi;
od;
if fail in CharacterRepresentatives then Error("character map not onto");fi;
CharacterStates:=List(CharacterRepresentatives,v->PauliTensor(v)*ThetaState);
for ci in [1..32] do
 for j in [1..5] do
  expected:=(-1)^(QuoInt(ci-1,2^(j-1)) mod 2);
  if Stabilizers[j]*CharacterStates[ci]<>expected*CharacterStates[ci] then
   Error("character conjugation mismatch");fi;
 od;
od;
StateMatrix:=TransposedMat(CharacterStates);
Gram:=TransposedMat(List(StateMatrix,row->List(row,ComplexConjugate)))*StateMatrix;
norm:=Sum(ThetaState,x->x^2);
if Gram<>norm*Id32 or RankMat(StateMatrix)<>32 then Error("character basis failed");fi;
BadState:=ShallowCopy(ThetaState);BadState[First([1..32],i->BadState[i]<>0)]:=0;
if ForAll(Stabilizers,s->s*BadState=BadState) then Error("missing-term control passed");fi;
Print("CHARACTER_REPRESENTATIVES=",CharacterRepresentatives,"\n");
Print("CHARACTER_STATES=",CharacterStates,"\n");
Print("PROJECTOR_RANK=",RankMat(Projector)," STATE_SUPPORT=",Number(ThetaState,x->x<>0),
 " GRAM_SCALAR=",norm," CHARACTER_BASIS_RANK=",RankMat(StateMatrix),"\n");
Print("PASS all 32 characters, all 160 eigenvalue relations, full character basis; missing-term control rejected\n");
QUIT;
