Read("research/results/bmd-exception-relative-centres-20261008/middle.g");
f:=GF(3^8);; x:=Indeterminate(f,"x");;
a:=RootsOfPolynomial(f,Sum([0..8],i->MIDDLE_FIELD[i+1]*x^i))[1];;
decode:=function(c)
 local z,i; z:=Zero(f);
 for i in [0..7] do z:=z+(QuoInt(c,3^i) mod 3)*a^i; od;
 return z;
end;;
M:=List(MIDDLE_CODES,row->List(row,decode));;
if RankMat(M)<>140 or DeterminantMat(M)<>decode(MIDDLE_DET) or M<>TransposedMat(M) then Error("middle cup mismatch"); fi;
M[2]:=ShallowCopy(M[1]);;
if RankMat(M)<>139 or DeterminantMat(M)<>Zero(f) then Error("middle control"); fi;
Print("GAP_MIDDLE_CUP_COMPLETED rank140 determinant_matched duplicate_row_detected\n");
QUIT;
