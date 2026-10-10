# Independent reconstruction over GF(125), with the specified modulus.
F:=GF(125);; one:=One(F);;
g:=First(Elements(F),z->z^3+4*z^2+3*z+one=Zero(F));;
if g=fail or g^5=g then Error("Bad cubic field generator");fi;
codes:=[0,10,15,75,84,89,97,124,11];;
a:=List(codes,c->Sum([0..2],j->(QuoInt(c,5^j) mod 5)*g^j));;
if Length(Set(a))<>9 then Error("Collisions");fi;
e:=Concatenation([one],List([1..8],j->Zero(F)));;
for i in [2..9] do for j in Reversed([1..8]) do e[j+1]:=e[j+1]+a[i]*e[j];od;od;
f:=e[2]*e[6]-e[7];; companion:=(e[2]^2-e[3])*e[6]-e[2]*e[7]+e[8];;
if f<>Zero(F) or companion<>2*g^2+g then Error("Section mismatch");fi;
L:=Concatenation([0..35],[37,42]);;
M:=List([0,1],k->List(L,function(j) if j=k then return one; else return Zero(F); fi; end));;
for i in [1..9] do for j in [i+1..9] do
 s:=Concatenation([one],List([1..42],k->Zero(F)));;
 for k in [1..42] do
  q:=Zero(F);; if k=1 then q:=a[i]+a[j];elif k=2 then q:=a[i]*a[j];fi;
  for r in [1..k-1] do q:=q-s[r+1]*s[k-r+1];od;
  s[k+1]:=q/(2*one);
 od;
 Add(M,List(L,k->s[k+1]));
od;od;
V:=one;;for i in [1..9] do for j in [i+1..9] do V:=V*(a[j]-a[i]);od;od;
r:=RankMat(M);; d:=DeterminantMat(M);;
if r<>38 or d<>3*one or d/V^9<>g^2+2*g+3*one then Error("Original-minor mismatch");fi;
Print("GAP_SECTION_VERIFIED rank=",r," det=3 normalized=g^2+2g+3 f=0 companion=2g^2+g\n");
Print("INPUT_FACTOR_SECTION_INDEPENDENT_COMPLETED\n");
QUIT;
