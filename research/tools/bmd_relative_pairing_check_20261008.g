# Independent finite-field arithmetic and ranks of the retained actual matrices.
Read("research/results/bmd-exception-relative-pairing-20261008/matrices.g");
f:=GF(3^8);; x:=Indeterminate(f,"x");;
a:=RootsOfPolynomial(f,Sum([0..8],i->REL_FIELD[i+1]*x^i))[1];;
decode:=function(c)
 local z,i;
 z:=Zero(f);
 for i in [0..7] do z:=z+(QuoInt(c,3^i) mod 3)*a^i; od;
 return z;
end;;
J:=List(REL_J,row->List(row,decode));;
C:=List(REL_C,row->List(row,decode));;
K:=NullspaceMat(TransposedMat(J));;
if RankMat(J)<>256 or Length(K)<>47 then Error("kernel dimension mismatch"); fi;
P:=K*C;;
stack:=Concatenation(J,TransposedMat(C));;
if RankMat(P)<>47 or DeterminantMat(P)=Zero(f) or RankMat(stack)<>303 then
 Error("relative rank mismatch");
fi;
P[2]:=ShallowCopy(P[1]);;
if RankMat(P)<>46 or DeterminantMat(P)<>Zero(f) then Error("corruption control"); fi;
Print("GAP_RELATIVE_PAIRING_COMPLETED jet_rank256 kernel47 pairing_rank47 stacked_rank303 duplicate_row_detected\n");
QUIT;
