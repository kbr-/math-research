# Independent GAP determinant and rank over the exact F27 coefficient presentation.
Read("research/results/bmd-exception-torsion-deflation-20261007/cup-data.g");;
F := GF(27);; one := One(F);; zero := Zero(F);;
root := First(Elements(F), t -> Sum([1..Length(CUP_FIELD_POLY)], i -> CUP_FIELD_POLY[i]*one*t^(i-1)) = zero);;
if root = fail then Error("field polynomial has no root"); fi;
decode := function(code)
  if code < 0 or code >= 27 then Error("invalid coefficient code"); fi;
  return (code mod 3)*one + (QuoInt(code,3) mod 3)*root + QuoInt(code,9)*root^2;
end;;
M := List(CUP_CODES, row -> List(row, decode));;
if Length(M) <> 140 or ForAny(M, row -> Length(row) <> 140) then Error("wrong matrix dimensions"); fi;
r := RankMat(M);; det := DeterminantMat(M);;
if r <> 140 or det = zero or det <> decode(CUP_DET_CODE) then Error("independent matrix verification failed"); fi;
bad := StructuralCopy(M);; bad[140] := ShallowCopy(bad[1]);;
if RankMat(bad) <> 139 or DeterminantMat(bad) <> zero then Error("duplicate-row corruption not detected"); fi;
Print("GAP_CUP_CHECK rank=",r," size=140 determinant_agrees=true duplicate_row_rank=139\n");
Print("CARTIER_CUP_INDEPENDENT_CHECK_COMPLETED\n");
QUIT;
