# Exact two-degree PC reset control over F2:
# {x^2, x^2-x, xy-1, y^2-y}, original degree 2.
# All eight vectors in A_1 are checked at each closure step.
prF := GF(2);;
prOne := One(prF);; prZero := Zero(prF);;
prMat := a -> List(a,row->List(row,x->x*prOne));;
# Columns of degree-two coordinates: z^2,xz,yz,x^2,xy,y^2.
prRel := prMat([[0,0,0,1,0,0],[0,1,0,1,0,0],
               [1,0,0,0,1,0],[0,0,1,0,0,1]]);;
prProjection := prMat([[1,0],[0,0],[0,1],[0,0],[1,0],[0,1]]);;
if RankMat(prRel)<>4 or RankMat(prProjection)<>2
   or prRel*prProjection<>NullMat(4,2,prF) then
  Error("degree-two quotient");
fi;
prUnit := prMat([[1,0]])[1];;
prZ := prMat([[1,0],[0,0],[0,1]]);;
prX := prMat([[0,0],[0,0],[1,0]]);;
prY := prMat([[0,1],[1,0],[0,1]]);;
prE := VectorSpace(prF,IdentityMat(3,prF));;
prW := VectorSpace(prF,[prMat([[0,0]])[1]]);;
prDims := [Dimension(prW)];;
prTests := 0;;
for prStep in [1..3] do
  prPre := Filtered(Elements(prE),v->v*prZ in prW);;
  prTests := prTests+Length(Elements(prE));
  prRows := Concatenation(List(prPre,v->v*prZ),
                         List(prPre,v->v*prX),
                         List(prPre,v->v*prY));;
  prW := VectorSpace(prF,prRows);;
  Add(prDims,Dimension(prW));
  if not prUnit in prW then Error("marked unit did not enter"); fi;
od;
if prDims<>[0,1,2,2] or RankMat(prZ)<>2 then Error("Wong sequence"); fi;
prS := prMat([[1,0,0],[0,0,1]]);;
prLoop := prS*prY;;
if prLoop=NullMat(2,2,prF) or prLoop^2<>prLoop then
  Error("reset loop not nonzero idempotent");
fi;
# Build block matrices without relying on a CAS block constructor's conventions.
prForward := [];;
for prA in [prZ,prX,prY] do
  prB := NullMat(5,5,prF);;
  for prI in [1..3] do
    for prJ in [1..2] do prB[prI][3+prJ]:=prA[prI][prJ]; od;
  od;
  Add(prForward,prB);
od;
for prA in prForward do
  for prB in prForward do
    if prA*prB<>NullMat(5,5,prF) then Error("forward square zero"); fi;
  od;
od;
Print("PASS: NS quotient dimension 2, unit nonzero; Wong dimensions ",prDims,
      "; ",prTests," input-vector membership tests; Z rank 2 maximal;\n");
Print("9 forward-arrow products zero; reset loop nonzero idempotent;\n");
Print("marked unit enters at first closure step; no lower-bound assertion.\n");
QUIT;
