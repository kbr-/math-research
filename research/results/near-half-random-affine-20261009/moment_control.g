# Exact fourth centered moments for modular counts on binary affine half-cubes.
# The finite ledger verifies identities, not asymptotic source probabilities.
Check:=function(b,s) if not b then Error(s);fi;end;
Print("SIZING cube k=3; q=3,5 all coefficient/target choices; 15 subsets; ordered distinct quadruples=1680 per field\n");
pts:=Tuples([0,1],3);halves:=[];
for h in Difference(pts,[[0,0,0]]) do
 for c in [0,1] do Add(halves,Filtered(pts,x->Sum([1..3],i->h[i]*x[i]) mod 2=c));od;
od;
Add(halves,pts);
quadchecks:=0;triplechecks:=0;momentchecks:=0;omitchecks:=0;samplecounts:=0;
for q in [3,5] do
 fld:=GF(q);one:=One(fld);prob:=1/q;
 quads:=Arrangements(pts,4);
 for z in quads do
  dep:=RankMat(List(z,x->Concatenation([1],x))*one)=3;
  para:=(z[1]+z[2]=z[3]+z[4]) or (z[1]+z[3]=z[2]+z[4]) or (z[1]+z[4]=z[2]+z[3]);
  Check(dep=para,"odd-field cube quadruple classification");quadchecks:=quadchecks+1;
 od;
 for z in Arrangements(pts,3) do
  Check(RankMat(List(z,x->Concatenation([1],x))*one)=3,"three-point independence");triplechecks:=triplechecks+1;
 od;
 for subset in halves do
  num:=Length(subset);mu:=num/q;
  depcount:=Number(Arrangements(subset,4),z->RankMat(List(z,x->Concatenation([1],x))*one)=3);
  measured:=0;
  for cf in Tuples([0..q-1],4) do
   count:=Number(subset,x->(Sum([1..3],i->cf[i]*x[i])-cf[4]) mod q=0);
   measured:=measured+(count-mu)^4;samplecounts:=samplecounts+1;
  od;
  measured:=measured/q^4;
  diagonal:=num*(prob*(1-prob)^4+(1-prob)*prob^4);
  pairs:=3*num*(num-1)*(prob*(1-prob))^2;
  circuits:=depcount*(prob^3-prob^4);
  Check(measured=diagonal+pairs+circuits,"exact fourth moment identity");
  Check(measured<=num/q+3*num^2/q^2+3*6^3/q^3,"universal moment bound");
  if circuits<>0 then Check(measured<>diagonal+pairs,"omitted circuit negative control");omitchecks:=omitchecks+1;fi;
  momentchecks:=momentchecks+1;
 od;
od;
# Characteristic two is an essential exclusion for the parallelogram count.
z:=[[0,0,0],[1,1,0],[1,0,1],[0,1,1]];
Check(RankMat(List(z,x->Concatenation([1],x))*One(GF(2)))=3,"binary tetrahedron dependence");
Check(not ((z[1]+z[2]=z[3]+z[4]) or (z[1]+z[3]=z[2]+z[4]) or (z[1]+z[4]=z[2]+z[3])),"binary non-parallelogram control");
fullsets:=0;projectionchecks:=0;
for mask in Tuples([0,1],8) do
 subset:=pts{Filtered([1..8],i->mask[i]=1)};
 if Length(subset)>0 and RankMat(List(subset,x->Concatenation([1],x))*One(GF(2)))=4 then
  fullsets:=fullsets+1;
  for S in Combinations([1..3]) do
   proj:=Set(List(subset,x->x{S}));
   Check(RankMat(List(proj,x->Concatenation([1],x))*One(GF(2)))=Length(S)+1,"full affine hull under projection");
   projectionchecks:=projectionchecks+1;
  od;
 fi;
od;
ratio:=8*(3/4)^8;Check(ratio<1,"new source circuit term decays");
Check(8*(3/4)^4>1,"old-parameter fourth-moment union bound fails to decay");
Print("QUADRUPLES=",quadchecks," TRIPLES=",triplechecks," MOMENT_IDENTITIES=",momentchecks," SAMPLES=",samplecounts," OMIT_CONTROLS=",omitchecks,"\n");
Print("FULL_AFFINE_RELATIONS=",fullsets," PROJECTIONS=",projectionchecks," NEW_CIRCUIT_RATIO=",ratio,"\n");
Print("ALL MODULAR FOURTH-MOMENT CONTROLS PASSED\n");
QUIT;
