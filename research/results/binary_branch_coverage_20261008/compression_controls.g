# Exhaustive test of monomial degree compression on the three-edge triangle.
# All nonzero multilinear weights over F2 and F3 on three Boolean variables;
# for each edge, solve for an arbitrary affine reference on the weight support.
# 255+6560=6815 weights, at most 20445 native linear solves, 4 by 8 matrices.
out:=OutputTextFile("research/results/binary_branch_coverage_20261008/weights.txt",false);;
SetPrintFormattingStatus(out,false);;
AppendTo(out,"field;weight_coefficients;degree;compressible;affine_references\n");
degrees:=[0,1,1,2,1,2,2,3];; edges:=[4,6,7];;
for prime in [2,3] do
 field:=GF(prime); elems:=List([0..prime-1],i->i*One(field));
 evals:=List([0..7],mask->List([0..7],point->
  Product([0..2],j->(1-(QuoInt(mask,2^j) mod 2))+
   (QuoInt(mask,2^j) mod 2)*(QuoInt(point,2^j) mod 2))*One(field)));
 affine:=evals{[1,2,3,5]};
 totals:=[0,0,0,0];passes:=[0,0,0,0];witness:=fail;
 for coefficients in Tuples(elems,8) do
  if ForAll(coefficients,x->x=Zero(field)) then continue; fi;
  degree:=Maximum(List(Filtered([1..8],i->coefficients[i]<>Zero(field)),i->degrees[i]));
  weightValues:=coefficients*evals;
  weightedAffine:=List(affine,row->List([1..8],i->row[i]*weightValues[i]));
  references:=[];good:=true;
  for e in edges do
   target:=List([1..8],i->weightValues[i]*evals[e][i]);
   solution:=SolutionMat(weightedAffine,target);
   if solution=fail then good:=false;break; fi;
   if solution*weightedAffine<>target then Error("reference certificate"); fi;
   Add(references,List(solution,Int));
  od;
  totals[degree+1]:=totals[degree+1]+1;
  if good then
   passes[degree+1]:=passes[degree+1]+1;
   if degree<2 then Error("hitting lower bound failed"); fi;
   if coefficients[4]=One(field) and Number(coefficients,x->x<>Zero(field))=1 then witness:=references; fi;
  fi;
  AppendTo(out,prime,";",List(coefficients,Int),";",degree,";",good,";",references,"\n");
 od;
 if Sum(totals)<>prime^8-1 or passes[3]=0 or witness=fail then Error("coverage"); fi;
 Print("field=",prime," weights by degree=",totals," compressible=",passes,
  "\nx1*x2 weight nonzero-reference certificate=",witness,"\n");
od;
CloseStream(out);
Print("All assertions passed. Strict degree drop and nonzero Boolean class are required.\n");
QUIT;
