# Independent GAP character pairing ranks for the same one-parameter pencil.
F := GF(3^10);; x := Indeterminate(F);; one := One(F);; zero := Zero(F);;
f := x^9+x^8+x^5+x-one;; roots := RootsOfUPol(F,f);;
if Length(Set(roots)) <> 9 then Error("not nine roots"); fi;
v := List(roots, b -> one/Value(Derivative(f),b));;
counts := List([1..9], i -> List([0..4], j -> 0));;
total := 0;; genus := 0;; controls := 0;;
g := 0;; S := [];; weights := [];; e := 0;;
for m in [3..9] do
 for S in Combinations([1..9],m) do
  R := Product(S,i -> x-roots[i]);; g := QuoInt(m-1,2);;
  weights := List(S,i -> 2*one/Value(Derivative(R),roots[i]));;
  H := List([1..g],i -> List([1..g],j -> Sum([1..m],k -> weights[k]*v[S[k]]*roots[S[k]]^(i+j-2))));;
  r := RankMat(H);; counts[m][r+1] := counts[m][r+1]+1;
  total := total+r;; genus := genus+g;;
  for e in [0..1+(1-m mod 2)] do
   C := List([1..g],i -> List([1..g],j -> Sum([1..m],k -> weights[k]*roots[S[k]]^(i+j-2+e))));;
   if RankMat(C) <> 0 then Error("coordinate-change control failed"); fi;
   controls := controls+1;
  od;
 od;
od;
expected := [[0,0,0,0,0],[0,0,0,0,0],[4,80,0,0,0],[1,125,0,0,0],[0,5,121,0,0],[0,1,83,0,0],[0,0,1,35,0],[0,0,0,9,0],[0,0,0,0,1]];;
if counts <> expected or total <> 757 or genus <> 769 or controls <> 1151 then Error("independent rank or control disagreement"); fi;
Print("GAP_RANK_COUNTS=",counts,"\nTOTAL_RANK=",total," GENUS=",genus," COORDINATE_CONTROLS=",controls,"\n");
Print("PENCIL_PARAMETER_INDEPENDENT_CHECK_COMPLETED\n");
QUIT;
