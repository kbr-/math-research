# Independent exact subset-Cartier control in GAP; no PARI data imported.
F := GF(3^10);; x := Indeterminate(F);; one := One(F);; zero := Zero(F);;
f := x^9+x^8+x^5+x-one;; roots := RootsOfUPol(F,f);;
if Length(Set(roots)) <> 9 then Error("not nine distinct roots"); fi;
counts := List([1..9], i -> 0);; good := ShallowCopy(counts);;
g := 0;; cs := [];;
for m in [3..9] do
  for S in Combinations([1..9],m) do
    R := Product(S, i -> x-roots[i]);;
    cs := CoefficientsOfUnivariatePolynomial(R);; g := QuoInt(m-1,2);;
    C := List([1..g], i -> List([1..g], function(j)
      local k; k := 3*i-j;
      if k < 0 or k >= Length(cs) then return zero; fi;
      return cs[k+1];
    end));;
    counts[m] := counts[m]+1;
    if DeterminantMat(C) <> zero then good[m] := good[m]+1; fi;
  od;
od;
if counts <> [0,0,84,126,126,84,36,9,1] or good <> [0,0,84,125,126,84,36,9,1] then Error("PARI/GAP disagreement"); fi;
Print("GAP independent subset counts=",counts," ordinary=",good,"\n");
Print("TERNARY_PENCIL_INDEPENDENT_CHECK_COMPLETED\n");
QUIT;
