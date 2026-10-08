# Exact controls for rank(A)-rank(A A*) = dim(im(A*) intersect ker A),
# column-vector convention, Hermitian adjoint over F4. Enumerate only all
# 256 two-by-two matrices, then one explicit unitary projection control.
ff := GF(4);; om := Z(4);; oo := One(ff);; zz := Zero(ff);;
star := a -> TransposedMat(List(a,r -> List(r,x -> x^2)));;
hist := [0,0,0];; count := 0;;
for entries in Tuples(Elements(ff),4) do
 mat := [entries{[1..2]},entries{[3..4]}];
 adj := star(mat);
 # Columns of A* represented as rows are coefficient-conjugates of A.
 imagebasis := BaseMat(List(mat,r -> List(r,x -> x^2)));
 kern := NullspaceMat(TransposedMat(mat));
 together := Concatenation(imagebasis,kern);
 if Length(together)=0 then joinedrank:=0; else joinedrank:=RankMat(together); fi;
 radical := Length(imagebasis)+Length(kern)-joinedrank;
 if RankMat(mat)-RankMat(mat*adj) <> radical then Error("radical identity"); fi;
 hist[radical+1] := hist[radical+1]+1; count:=count+1;
od;
Print("PASS ",count," matrices; radical-loss histogram 0,1,2: ",hist,"\n");
unitary := [[oo,oo,oo],[oo,om,om^2],[oo,om^2,om]];;
if unitary*star(unitary) <> IdentityMat(3,ff) then Error("unitary"); fi;
proj := DiagonalMat([oo,oo,zz]);;
high := DiagonalMat([zz,zz,oo]);;
zero := DiagonalMat([oo,zz,zz]);;
qq := unitary*zero*star(unitary);;
if qq*qq<>qq or star(qq)<>qq or proj*high<>NullMat(3,3,ff) then Error("projections"); fi;
trans := high*qq*proj;;
if RankMat(trans)<>1 or RankMat(trans*star(trans))<>0 then Error("Gram collapse"); fi;
Print("PASS unitary-conjugated projection: transition rank=",RankMat(trans)," squared rank=",RankMat(trans*star(trans)),"\n");
# A rank-preserving left inverse exists here but cannot be the adjoint.
leftpick := [[zz,zz,oo]];;
if RankMat(leftpick*trans)<>1 then Error("separate dual control"); fi;
Print("PASS independent dual retains rank, with no assertion of source realization\n");
# Scalar count collision at 0 and two violations; exact zero test at N=3.
bits := Tuples([zz,oo],3);;
for bit in bits do
 indicator := Product(List(bit,x -> oo+x));
 if (indicator=oo) <> ForAll(bit,x -> x=zz) then Error("zero indicator"); fi;
od;
if oo+oo<>zz then Error("count alias"); fi;
Print("PASS 8 zero-test values and characteristic-two count alias\n");
Print("ALL DUAL RANK CHECKS PASSED\n");
QUIT;
