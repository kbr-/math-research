# Independent complete Laurent-section verification; no reuse of PARI's linear solves.
Read("research/results/bmd-exception-cubic-obstruction-20261008/assembly8-pilot.g");
states:=ShallowCopy(CUBIC_STATES);;exponents:=ShallowCopy(CUBIC_EXPONENTS);;ids:=CUBIC_CHARACTERS;;
Read("research/results/bmd-exception-cubic-obstruction-20261008/assembly8-full.g");;Append(states,CUBIC_STATES);;Append(exponents,CUBIC_EXPONENTS);;
Read("research/results/bmd-exception-cubic-obstruction-20261008/section-pilot.g");records:=ShallowCopy(BOUNDED_SECTION_RESULTS);;
Read("research/results/bmd-exception-cubic-obstruction-20261008/section-full.g");Append(records,BOUNDED_SECTION_RESULTS);;
f:=GF(27);;one:=One(f);;zero:=Zero(f);;x:=Indeterminate(f,"x");;a:=RootsOfPolynomial(f,x^3-x-one)[1];;inum:=IndeterminateNumberOfUnivariateRationalFunction(x);;
decode:=c->(c mod 3)*one+(QuoInt(c,3) mod 3)*a+QuoInt(c,9)*a^2;;
poly:=v->UnivariatePolynomialByCoefficients(FamilyObj(one),v,inum);;
cut:=function(p,n) local c;c:=CoefficientsOfUnivariatePolynomial(p);if Length(c)>n then c:=c{[1..n]};fi;return poly(c);end;;
cf:=function(p,n) local c;if n<0 then return zero;fi;c:=CoefficientsOfUnivariatePolynomial(p);if n<Length(c) then return c[n+1];fi;return zero;end;;
weights:=[0];;polys:=[one*x^0];;roots:=[one*x^0];;inverse:=[one*x^0];;offsets:=[];;total:=0;;
for S in [1..511] do
 bit:=First([0..8],b->QuoInt(S,2^b) mod 2=1);;
 weights[S+1]:=weights[S-2^bit+1]+1;polys[S+1]:=polys[S-2^bit+1]*(one+a^bit*x);
 roots[S+1]:=cut(polys[S+1]^41,32);inverse[S+1]:=cut(polys[S+1]^40,32);
 if cut(roots[S+1]^2-polys[S+1],32)<>zero*x^0 or cut(roots[S+1]*inverse[S+1],32)<>one*x^0 then Error("independent root series");fi;
od;
I:=[];;for S in [0..511] do offsets[S+1]:=total;total:=total+Maximum(0,QuoInt(weights[S+1]-1,2));if weights[S+1]<=3 then for j in [0..QuoInt(3-weights[S+1],2)] do Add(I,[S,j]);od;fi;od;
walsh:=function(v) local w,bit,S,i,j,u,t;w:=ShallowCopy(v);for bit in [0..8] do for S in [0..511] do if QuoInt(S,2^bit) mod 2=0 then i:=S+1;j:=S+2^bit+1;u:=w[i];t:=w[j];w[i]:=u+t;w[j]:=u-t;fi;od;od;return w;end;;
fourier:=function(v,N) return walsh(List([1..512],i->cut(v[i]*roots[i],N)));end;;
back:=function(v,N) local w;w:=walsh(v);return List([1..512],i->cut(w[i]*inverse[i],N)/(512*one));end;;
Cup:=function(v)
 local C,i,j,common,S,shift,coef;
 C:=NullMat(140,140,f);
 for i in [1..140] do for j in [1..140] do
  common:=Sum([0..8],b->2^b*(QuoInt(I[i][1],2^b) mod 2)*(QuoInt(I[j][1],2^b) mod 2));S:=511-(I[i][1]+I[j][1]-2*common);shift:=I[i][2]+I[j][2];coef:=CoefficientsOfUnivariatePolynomial(polys[common+1]);
  C[i][j]:=Sum([1..Length(coef)],l->coef[l]*v[offsets[S+1]+shift+l]);
 od;od;return C;
end;;
Ecoef:=[1,1,2,2,0,1,0,0,2];;checked:=0;;
for s in Set(List(records,r->r[1])) do
 subset:=Filtered(records,r->r[1]=s);si:=Position(exponents,s);maxorder:=Maximum(List(subset,r->(function()if r[4]=0 then return 8;else return r[4];fi;end)()));precision:=4*maxorder;;
 coords:=List([1..maxorder],m->List([1..512],i->zero*x^0));lambda:=List([1..769],i->zero);nextlambda:=ShallowCopy(lambda);;
 for ci in [1..466] do
  S:=ids[ci];given:=states[si][ci];g:=Length(given[1]);;
  for m in [1..maxorder] do coords[m][S+1]:=Sum([1..g],j->decode(given[m][j])*x^(4-j));od;
  raw:=polys[S+1]*coords[1][S+1]^3;;
  for j in [1..g] do lambda[offsets[S+1]+j]:=512*decode(given[1][j]);nextlambda[offsets[S+1]+j]:=512*cf(raw,12-j);od;
 od;
 C:=Cup(lambda);Cnext:=Cup(nextlambda);rank:=RankMat(C);;
 if (s>=6 and rank<>139) or (s=2 and rank<>9) or (s=4 and rank<>79) then Error("complete first cup rank");fi;
 wh:=List(coords,v->fourier(v,precision));G:=List([0..maxorder],j->List([1..512],i->zero*x^0));Gsquare:=List([0..maxorder],j->List([1..512],i->zero*x^0));;
 for branch in [1..512] do
  gg:=List([0..maxorder],j->zero*x^0);gg[1]:=one*x^0;
  for m in [1..maxorder] do
   U:=cut(x^(4*(m-1))*wh[m][branch],precision);powers:=[one*x^0];for k in [1..QuoInt(maxorder,m)] do powers[k+1]:=cut(powers[k]*U,precision);od;
   fresh:=[];for j in [0..maxorder] do fresh[j+1]:=cut(Sum([0..QuoInt(j,m)],k->Ecoef[k+1]*powers[k+1]*gg[j-k*m+1]),precision);od;gg:=fresh;
  od;
  for j in [0..maxorder] do G[j+1][branch]:=gg[j+1];Gsquare[j+1][branch]:=cut(Sum([0..j],k->gg[k+1]*gg[j-k+1]),precision);od;
 od;
 cubeone:=List(G[2],p->cut(p^3,precision));cubetwo:=List(G[3],p->cut(p^3,precision));;
 for item in subset do
  N:=item[2];u:=QuoInt(N,3);if N mod 3=1 then base:=G;else base:=Gsquare;fi;
  GN:=[];for j in [0..maxorder] do GN[j+1]:=[];for i in [1..512] do tmp:=base[j+1][i];if j>=3 then tmp:=tmp+u*cubeone[i]*base[j-2][i];fi;if j>=6 then tmp:=tmp+(u*cubetwo[i]+Binomial(u,2)*cubeone[i]^2)*base[j-5][i];fi;GN[j+1][i]:=cut(tmp,precision);od;od;
  fvec:=List(item[7],decode);if C*fvec<>List([1..140],i->zero) or fvec*Cnext*fvec<>decode(item[6]) then Error("first radical and slope");fi;
  sections:=List(item[8],rows->List(rows,r->poly(List(r,decode))));hats:=List(sections,v->fourier(v,precision));lastCorrection:=Length(sections)-1;;
  expected:=List([1..512],i->zero*x^0);for i in [1..140] do expected[I[i][1]+1]:=expected[I[i][1]+1]+fvec[i]*x^I[i][2];od;
  if sections[1]<>expected then Error("actual initial section");fi;
  for j in [0..lastCorrection] do for S in [0..511] do if sections[j+1][S+1]<>zero*x^0 and 2*(DegreeOfUnivariateLaurentPolynomial(sections[j+1][S+1])-4*j)+weights[S+1]>3 then Error("global infinity bound");fi;od;od;
  if item[4]=0 then upto:=8;else upto:=item[4];fi;
  for k in [1..upto] do
   sums:=List([1..512],i->cut(Sum([1..k],j->GN[j+1][i]*hats[k-j+1][i]),precision));
   if k<=lastCorrection then sums:=List([1..512],i->sums[i]+hats[k+1][i]);fi;
   actual:=back(sums,precision);
   if k<item[4] or item[4]=0 then
    if ForAny(actual,p->cut(p,4*k)<>zero*x^0) then Error("full Laurent section identity");fi;
   else
    obstruction:=List(I,v->512*cf(actual[512-v[1]],4*k-v[2]-1));scalar:=fvec*obstruction;
    if scalar=zero or scalar<>decode(item[5]) then Error("actual nonzero scalar obstruction");fi;
   fi;
  od;
  checked:=checked+1;
 od;
 Print("GAP_BOUNDED_SECTIONS exponent=",s," cases=",Length(subset)," exact_global_lifts=true\n");
od;
if checked<>150 then Error("complete check scope");fi;
Print("GAP_BOUNDED_SECTION_LIFTING_COMPLETED cases150 target144 complete_first_kernels=true exact_global_lifts=true\n");
QUIT;
