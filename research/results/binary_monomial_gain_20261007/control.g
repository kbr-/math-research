# Exact test of the all-parameter filtered rank formula on disjoint monomials.
# Six variables, 64 Boolean points, 64 monomials; eight codes, all 7 degree prefixes.
# One echelon calculation per code supplies every prefix, no degree-by-degree reruns.
F:=GF(2);; polvar:=Indeterminate(Rationals,"z");;
cases:=[ [3,2,[]], [3,2,[[1,1,1]]], [3,2,[[1,1,0],[0,1,1]]],
 [3,2,[[1,0,0],[0,1,0],[0,0,1]]], [2,3,[]], [2,3,[[1,1]]],
 [3,2,[[1,1,0],[0,1,1]],[[1,1]]],
 [3,2,[[1,1,0],[0,1,1]],[[1,0],[0,1]]] ];;
checks:=0;;
for item in cases do
 m:=item[1];; r:=item[2];; v:=m*r;;
 Assert(0,v=6);
 if Length(item)=3 then
  mix:=IdentityMat(m,F);;
  code:=List(item[3],row->List(row,a->a*One(F)));;
 else
  mix:=List(item[3],row->List(row,a->a*One(F)));;
  code:=List(item[4],row->List(row,a->a*One(F)));;
 fi;
 if Length(code)=0 then combined:=[]; else combined:=code*mix; fi;
 monomials:=Concatenation(List([0..v],d->Combinations([1..v],d)));;
 points:=Tuples(Elements(F),v);;
 mat:=[];;
 for point in points do
  vals:=List([1..m],i->Product(point{[(i-1)*r+1..i*r]}));;
  if ForAny(mix,row->Sum([1..m],i->row[i]*vals[i])<>Zero(F)) and ForAll(combined,row->Sum([1..m],i->row[i]*vals[i])=Zero(F)) then
   Add(mat,List(monomials,S->Product(List(S,i->point[i]),One(F))));
  fi;
 od;
 ech:=TriangulizedMat(mat);;
 pivots:=List(Filtered(ech,row->ForAny(row,a->a<>Zero(F))),row->PositionProperty(row,a->a<>Zero(F)));;
 if Length(mat)>0 then Assert(0,Length(pivots)=RankMat(mat)); fi;
 hp:=(1+polvar)^r-1-polvar^r;; total:=Zero(polvar);;
 for active in Combinations([1..m]) do
  if Length(active)=0 or Length(combined)=0 then cr:=0;
  else cr:=RankMat(List(combined,row->row{active})); fi;
  if Length(active)=0 then ar:=0; else ar:=RankMat(List(mix,row->row{active})); fi;
  nullity:=Length(active)-cr;; oldnull:=Length(active)-ar;;
  total:=total+hp^(m-Length(active))*((1+polvar^r)^nullity-polvar^(r*(ar-cr))*(1+polvar^r)^oldnull);
 od;
 coeffs:=CoefficientsOfUnivariatePolynomial(total);;
 profile:=[];;
 for cutoff in [0..v] do
  count:=Sum([0..cutoff],d->Binomial(v,d));;
  observed:=Number(pivots,pos->pos<=count);;
  expected:=Sum(coeffs{[1..Minimum(cutoff+1,Length(coeffs))]});;
  Assert(0,observed=expected);
  Add(profile,observed); checks:=checks+1;
 od;
 Print("m=",m," r=",r," input=",item," points=",Length(mat)," ranks=",profile,"\n");
od;
Print("PASS: ",checks," exact prefix ranks; largest matrix <=64x64\n");
QUIT;
