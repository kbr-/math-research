# Test the universal replacement c(1)/c(2) >= h(1)/h(2).
# Satisfiable Boolean base, NOT PHP: x1*y=x2*y=0, g=1-y.
# Sizes fixed before launch: 27 ambient F3 points, 5 models, at most 5x7 matrices.
# Predictions: h1=4,h2=5,c1=3,c2=4, hence c1*h2 < c2*h1.
F := GF(3);;
pts := Filtered(Tuples(Elements(F),3), v ->
  ForAll(v, z -> z*z=z) and v[1]*v[3]=Zero(F) and v[2]*v[3]=Zero(F));;
Assert(0,Length(pts)=5);
mons := [[],[1],[2],[3],[1,2],[1,3],[2,3]];;
evals := List(pts, v -> List(mons, s -> Product(List(s,i -> v[i]),One(F))));;
G := List([1..Length(pts)], i -> (One(F)-pts[i][3])*evals[i]);;
h1 := RankMat(List(evals,row -> row{[1..4]}));;
h2 := RankMat(evals);;
c1 := RankMat(List(G,row -> row{[1..4]}));;
c2 := RankMat(G);;
Assert(0,[h1,h2,c1,c2]=[4,5,3,4]);
Assert(0,c1*h2<c2*h1);
Print("Field F3; models=",Length(pts),"; columns=",Length(mons),"\n");
Print("[h1,h2,c1,c2]=",[h1,h2,c1,c2],"\n");
Print("c1*h2=",c1*h2," < c2*h1=",c2*h1,"; universal ratio FAILS\n");
QUIT;
