# Independent whole Cartier-map return and complete low signed-kernel checks.
Read("research/results/bmd-exception-short-returns-20261008/low-kernels.g");
f:=GF(27);; o:=One(f);; zz:=Zero(f);; x:=Indeterminate(f,"x");;
a:=RootsOfPolynomial(f,x^3-x-o)[1];; labels:=List([0..8],i->a^i);;
decode:=c->(c mod 3)*o+(QuoInt(c,3) mod 3)*a+QuoInt(c,9)*a^2;;
mat:=A->List(A,r->List(r,decode));; frob:=function(A,e) return List(A,r->List(r,c->c^e)); end;;
inum:=IndeterminateNumberOfUnivariateRationalFunction(x);;
cut:=function(p,n) local c;c:=CoefficientsOfUnivariatePolynomial(p);if Length(c)>n then c:=c{[1..n]};fi;return UnivariatePolynomialByCoefficients(FamilyObj(o),c,inum);end;;
coeffs:=function(p,n) local c;c:=CoefficientsOfUnivariatePolynomial(p);return List([1..n],i->(function() if i<=Length(c) then return c[i];else return zz;fi;end)());end;;
polys:=[o*x^0];; products:=[o*x^0];; weights:=[0];; roots:=List(labels,b->cut((o+b*x)^41,81));;
for S in [1..511] do
 bit:=First([0..8],b->QuoInt(S,2^b) mod 2=1);;
 polys[S+1]:=polys[S-2^bit+1]*(o+labels[bit+1]*x);;
 products[S+1]:=cut(products[S-2^bit+1]*roots[bit+1],81);;
 weights[S+1]:=weights[S-2^bit+1]+1;;
od;
ranks:=[0,0,0,0];; count:=0;;
for S in [0..511] do
 g:=Maximum(0,QuoInt(weights[S+1]-1,2));;
 if g>0 then
  count:=count+1;; cf:=coeffs(polys[S+1],3*g+1);;
  B:=List([1..g],i->List([1..g],j->(function() if 3*i-j>=0 then return cf[3*i-j+1];else return zz;fi;end)()));;
  P:=(frob(B,9)*frob(B,3)*B)^1560;; A:=IdentityMat(g,f);;
  for j in [1..4] do
   A:=frob(A,3)*B;;ranks[j]:=ranks[j]+RankMat(A);;
   if A*P<>A then Error("whole short return failed");fi;
  od;
 fi;
od;
if count<>466 or ranks<>[744,744,744,744] then Error("whole-map scope");fi;
I:=[];;for S in [0..511] do if weights[S+1]<=3 then for j in [0..QuoInt(3-weights[S+1],2)] do Add(I,[S,j]);od;fi;od;
FC:=TransposedMat(List(I,v->coeffs(cut(x^v[2]*products[v[1]+1],81),81)));;
nu:=coeffs(cut(polys[512]^40,81),81);;
Toep:=List([1..81],i->List([1..81],j->(function() if i>=j then return nu[i-j+1];else return zz;fi;end)()));;
GC:=Toep*FC;;
for b in [1..4] do
 q:=3^b;;J:=mat(LOW_DATA[b][3]);;C:=mat(LOW_DATA[b][4]);;K:=mat(LOW_DATA[b][5]);;h:=[137,131,113,61][b];;
 if J<>FC{[1..q]} or C<>TransposedMat(Reversed(GC{[1..q]}))*J then Error("complete source/cup mismatch");fi;
 if RankMat(J)<>140-h or RankMat(C)<>140-h or RankMat(K)<>h then Error("complete low ranks");fi;
 if J*K<>NullMat(q,h,f) or C*K<>NullMat(140,h,f) then Error("actual complete kernels");fi;
 Print("GAP_SHORT_TANGENT base=",b," whole_map_return=true kernel=",h," complete_source_match=true\n");
od;
Print("GAP_SHORT_TANGENTS_COMPLETED characters466 ranks744=true\n");
QUIT;
