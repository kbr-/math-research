# Exact Boolean-function control, not a charged-system computation.
# g=(xy,yz), features=(1,x,y,z), all 256 affine coefficient rows.
# For each multiplier cutoff 0..3, expanded and original tuple kernels agree;
# expected shortened dimension <= half original rank. Compare actual errors.
field := GF(2);; one := One(field);; zero := Zero(field);;
points := Tuples([zero,one],3);;
inputs := List(points,p->[p[1]*p[2],p[2]*p[3]]);;
features := List(points,p->Concatenation([one],p));;
monomials := Combinations([1..3]);;
rows := Tuples([zero,one],8);;
if Length(rows)*4<>1024 then Error("sizing"); fi;
Print("Rows: ",Length(rows),"; cutoffs: 4; row-cutoff cases: 1024\n");
for cutoff in [0..3] do
  mons := Filtered(monomials,s->Length(s)<=cutoff);
  vals := List(mons,s->List(points,p->Product(s,j->p[j])));
  # Empty products are integer 1; convert to the finite field explicitly.
  vals := vals*one;
  original := List(vals,v->Concatenation(List([1..2],i->List([1..8],q->v[q]*inputs[q][i]))));
  expanded := List(vals,v->Concatenation(List([1..2],i->Concatenation(List([1..4],j->List([1..8],q->v[q]*inputs[q][i]*features[q][j]))))));
  originalRank := RankMat(original);
  if RankMat(expanded)<>originalRank then Error("kernel invariance"); fi;
  shortSum := 0; errorSum := 0; constantSum := 0;
  bestAffine := 100; bestConstant := 100;
  for coefficients in rows do
    pencil := List([1..8],q->Sum([1..2],i->Sum([1..4],j->coefficients[4*(i-1)+j]*features[q][j])*inputs[q][i]));
    pencilMat := List(vals,v->List([1..8],q->v[q]*pencil[q]));
    shortDim := originalRank-RankMat(pencilMat);
    errorMat := List(vals,v->Concatenation(List([1..2],i->List([1..8],q->v[q]*inputs[q][i]*(one-pencil[q])))));
    errorRank := RankMat(errorMat);
    shortSum := shortSum+shortDim; errorSum := errorSum+errorRank;
    bestAffine := Minimum(bestAffine,errorRank);
    constant := ForAll([2,3,4,6,7,8],j->coefficients[j]=zero);
    if constant then
      constantSum := constantSum+errorRank;
      bestConstant := Minimum(bestConstant,errorRank);
    fi;
    Print("K=",cutoff," c=",List(coefficients,Int)," short=",shortDim," actual=",errorRank,"\n");
  od;
  if 2*shortSum>Length(rows)*originalRank then Error("shortening expectation"); fi;
  if cutoff=0 and (bestAffine<>0 or bestConstant<>1) then Error("optimized control"); fi;
  if cutoff=3 and (errorSum/256<>3/2 or constantSum/4<>3/2) then Error("full-space means"); fi;
  Print("SUMMARY K=",cutoff," tuple_rank=",originalRank," mean_short=",shortSum/256,
        " affine_mean_actual=",errorSum/256," constant_mean_actual=",constantSum/4,
        " affine_min=",bestAffine," constant_min=",bestConstant,"\n");
od;
Print("PASS: feature kernels, shortening bound and optimized-choice control\n");
QUIT;
