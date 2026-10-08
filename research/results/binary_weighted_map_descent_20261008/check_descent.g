# Exhaustive joint weighted-map descent control.
# One old Boolean bit, two fresh binary variables, maps and weight degree <=1.
# Original source polynomials have degree <=2; D=3 pays all weighted products.
# GF(8) exercises a three-step Frobenius orbit. Only valid point triples are
# assembled; the 8^6 possible functions have exactly 4368 valid nonzero weights.
# Native GAP NullspaceMat verifies ALL binary source polynomials in the nine
# degree<=2 monomials (mod x^2=x), rather than enumerating their 512 sums.
# Full accepted-case records are printed; compute.sh and save-run-output retain them.
RunWeightedDescentCheck := function()
 local f2, f8, basis, coords, values, coord, down, project, monomials,
       require, triples, wv, av, bv, first, second, weights, amap, bmap,
       before, after, candidate, coeff, bestW, bestRank, oldRank,
       sourceRows, newRows, kernel, i, j, orbit, cases, comparisons,
       sourceSpaces, started, oldValues, ranks, a4, gamma, proj4, f4;
 f2:=GF(2); f8:=GF(8); basis:=[One(f8),Z(8),Z(8)^2];
 coords:=Tuples([Zero(f2),One(f2)],3);
 values:=List(coords,c->Sum([1..3],j->c[j]*basis[j]));
 require:=function(ok,message)
   if not ok then Print("FAIL: ",message,"\n"); QUIT_GAP(1); fi;
 end;
 coord:=z->coords[Position(values,z)];
 down:=function(z)
   if z=Zero(f8) then return Zero(f2); fi;
   if z=One(f8) then return One(f2); fi;
   Print("FAIL: nonbinary projected value\n"); QUIT_GAP(1);
 end;
 project:=z->z+z^2+z^4; # Trace(1)=1 in the degree-three extension.
 monomials:=function(x,y,z)
   return [One(f8),x,y,z,x*y,x*z,y*z,y^2,z^2];
 end;
 Print("GF8 basis=",basis,"; coordinate order=",coords,"\n");
 Print("Stages: valid point triples; complete two-point maps; kernel/rank checks; controls\n");
 triples:=[];
 for wv in values do for av in values do for bv in values do
   if wv*(av^2-av)=Zero(f8) and wv*(bv^2-bv)=Zero(f8) then
     Add(triples,[wv,av,bv]);
   fi;
 od; od; od;
 require(Length(triples)=92,"point-triple count");
 require(Length(triples)^2-64^2=4368,"nonzero valid pair count");
 require(Length(triples)^2<10000,"bounded run size");
 Print("Point triples=92; candidate pairs=8464; valid nonzero cases=4368\n");
 started:=Runtime(); cases:=0; comparisons:=0; sourceSpaces:=0;
 for first in triples do for second in triples do
   weights:=[first[1],second[1]];
   if ForAll(weights,IsZero) then continue; fi;
   amap:=[first[2],second[2]]; bmap:=[first[3],second[3]];
   before:=[monomials(Zero(f8),amap[1],bmap[1]),
            monomials(One(f8),amap[2],bmap[2])];
   after:=[monomials(Zero(f8),project(amap[1]),project(bmap[1])),
           monomials(One(f8),project(amap[2]),project(bmap[2]))];
   for i in [1..2] do
     for orbit in [0..2] do
       require(weights[i]*(amap[i]^(2^orbit)-amap[i])=Zero(f8),"Frobenius a");
       require(weights[i]*(bmap[i]^(2^orbit)-bmap[i])=Zero(f8),"Frobenius b");
     od;
     for j in [1..9] do
       require(weights[i]*(before[i][j]-after[i][j])=Zero(f8),"weighted monomial");
       comparisons:=comparisons+1;
     od;
   od;
   oldRank:=RankMat(DiagonalMat(weights));
   require(oldRank=Number(weights,z->not IsZero(z)),"point/rank cross-check");
   bestRank:=-1; bestW:=fail;
   for coeff in coords do
     candidate:=List([1..2],i->Sum([1..3],j->coeff[j]*coord(weights[i])[j]));
     if RankMat(DiagonalMat(candidate))>bestRank then
       bestRank:=RankMat(DiagonalMat(candidate)); bestW:=candidate;
     fi;
   od;
   require(bestRank>0 and 2*bestRank>=oldRank,"binary retained rank");
   sourceRows:=List([1..9],j->Concatenation(
       coord(weights[1]*before[1][j]),coord(weights[2]*before[2][j])));
   newRows:=List([1..9],j->List([1..2],i->bestW[i]*down(after[i][j])));
   kernel:=NullspaceMat(sourceRows);
   require(ForAll(Flat(kernel*newRows),IsZero),"all source relations preserved");
   sourceSpaces:=sourceSpaces+1; cases:=cases+1;
   Print("CASE ",List(Concatenation(first,second),z->Position(values,z)-1),
         " weight=",List(bestW,IntFFE)," ranks=",[oldRank,bestRank],
         " source_kernel=",Length(kernel)," PASS\n");
 od; od;
 require(cases=4368 and comparisons=78624 and sourceSpaces=4368,"final counts");
 # Full three-bit function space: each nonzero GF8 value appears once.
 # Weight degree<=3, multiplier cutoff3, D=6; all seven nonzero binary
 # component combinations have rank4, while the original weight has rank7.
 oldValues:=values; ranks:=[];
 for coeff in coords do
   if ForAll(coeff,IsZero) then continue; fi;
   candidate:=List(oldValues,z->Sum([1..3],j->coeff[j]*coord(z)[j]));
   Add(ranks,RankMat(DiagonalMat(candidate)));
 od;
 require(RankMat(DiagonalMat(oldValues))=7 and Set(ranks)=[4],"rank-loss control");
 # Omitting the fresh field equation invalidates the claim.
 f4:=GF(4); a4:=Z(4); gamma:=a4^2;
 proj4:=gamma*a4+(gamma*a4)^2;
 require(a4^2+a4+One(f4)=Zero(f4),"missing-field source root");
 require(proj4^2+proj4+One(f4)<>Zero(f4),"missing-field negative control");
 require(a4^2-a4<>Zero(f4),"missing field really violated");
 Print("SUMMARY cases=",cases," monomial_point_checks=",comparisons,
       " source_kernel_spaces=",sourceSpaces,
       " source_polynomial_span_size=512 rank_control=[7,4] negative_control=PASS",
       " runtime_ms=",Runtime()-started,"\n");
 Print("ALL WEIGHTED DESCENT CHECKS PASSED\n");
end;
RunWeightedDescentCheck();
QUIT_GAP(0);
