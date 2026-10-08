# Independent modulo-nine assembly with three Z/9 polynomial components, not PARI's quotient ring.
Read("research/results/bmd-exception-cubic-obstruction-20261008/characters8.g");
characters:=JET8_CHARACTERS;;
Read("research/results/bmd-exception-cubic-obstruction-20261008/assembly8-pilot.g");
states:=ShallowCopy(CUBIC_STATES);;exponents:=ShallowCopy(CUBIC_EXPONENTS);;ids:=CUBIC_CHARACTERS;;
Read("research/results/bmd-exception-cubic-obstruction-20261008/assembly8-full.g");
Append(states,CUBIC_STATES);;Append(exponents,CUBIC_EXPONENTS);;
if exponents<>JET8_EXPONENTS or ids<>List(characters,r->r[1]) then Error("exact assembly scope");fi;
ring9:=Integers mod 9;;o9:=One(ring9);;z9:=Zero(ring9);;x:=Indeterminate(ring9,"x");;inum:=IndeterminateNumberOfUnivariateRationalFunction(x);;precision:=12;;
poly9:=v->UnivariatePolynomialByCoefficients(FamilyObj(o9),v,inum);;
cut:=function(p) local c;c:=CoefficientsOfUnivariatePolynomial(p);if Length(c)>precision then c:=c{[1..precision]};fi;return poly9(c);end;;
cf:=function(p,n) local c;c:=CoefficientsOfUnivariatePolynomial(p);if n<Length(c) then return Int(c[n+1]);fi;return 0;end;;
unit:=[o9*x^0,z9*x^0,z9*x^0];;nil:=[z9*x^0,z9*x^0,z9*x^0];;eta:=[z9*x^0,o9*x^0,z9*x^0];;
add:=function(a,b) return List([1..3],i->a[i]+b[i]);end;;
sub:=function(a,b) return List([1..3],i->a[i]-b[i]);end;;
scale:=function(a,c) return List(a,p->cut(c*p));end;;
mul:=function(a,b)
 local r0,r1,r2,r3,r4;
 r0:=a[1]*b[1];r1:=a[1]*b[2]+a[2]*b[1];r2:=a[1]*b[3]+a[2]*b[2]+a[3]*b[1];r3:=a[2]*b[3]+a[3]*b[2];r4:=a[3]*b[3];
 return [cut(r0+r3),cut(r1+r3+r4),cut(r2+r4)];
end;;
liftcode:=c->[(c mod 3)*o9*x^0,(QuoInt(c,3) mod 3)*o9*x^0,QuoInt(c,9)*o9*x^0];;
walsh:=function(v)
 local w,bit,S,u,t,j;
 w:=ShallowCopy(v);
 for bit in [0..8] do for S in [0..511] do if QuoInt(S,2^bit) mod 2=0 then
  j:=S+2^bit+1;u:=w[S+1];t:=w[j];w[S+1]:=add(u,t);w[j]:=sub(u,t);
 fi;od;od;return w;
end;;
labels:=[unit];;for i in [2..9] do labels[i]:=mul(labels[i-1],eta);od;
roots:=[];;invroots:=[];;
for i in [1..9] do
 rc:=[unit];;
 for j in [1..precision-1] do
  if j=1 then tmp:=labels[i];else tmp:=nil;fi;
  for k in [1..j-1] do tmp:=sub(tmp,mul(rc[k+1],rc[j-k+1]));od;rc[j+1]:=scale(tmp,5);
 od;
 root:=nil;;for j in [0..precision-1] do root:=add(root,scale(rc[j+1],x^j));od;
 if mul(root,root)<>add(unit,scale(labels[i],x)) then Error("mod9 root identity");fi;
 invp:=nil;;power:=unit;;for j in [0..precision-1] do invp:=add(invp,scale(power,x^j));power:=scale(mul(power,labels[i]),-1);od;
 roots[i]:=root;invroots[i]:=mul(root,invp);
od;
prods:=[unit];;invs:=[unit];;polys:=[unit];;
for S in [1..511] do
 bit:=First([0..8],b->QuoInt(S,2^b) mod 2=1);;
 prods[S+1]:=mul(prods[S-2^bit+1],roots[bit+1]);invs[S+1]:=mul(invs[S-2^bit+1],invroots[bit+1]);polys[S+1]:=mul(polys[S-2^bit+1],add(unit,scale(labels[bit+1],x)));
od;
f:=GF(27);;one:=One(f);;y:=Indeterminate(f,"y");;a:=RootsOfPolynomial(f,y^3-y-one)[1];;
decode:=c->(c mod 3)*one+(QuoInt(c,3) mod 3)*a+QuoInt(c,9)*a^2;;
for si in [1..30] do
 for block in [1..2] do
  cochain:=List([1..512],i->nil);;
  for ci in [1..466] do
   S:=characters[ci][1];v:=characters[ci][2][si][block];p:=nil;;
   for j in [1..Length(v)] do p:=add(p,scale(liftcode(v[j]),x^(4-j)));od;cochain[S+1]:=p;
  od;
  evals:=walsh(List([1..512],i->mul(cochain[i],prods[i])));;
  evals:=walsh(List(evals,v->mul(mul(v,v),v)));;
  cubes:=List([1..512],i->scale(mul(evals[i],invs[i]),8));;
  for ci in [1..466] do
   S:=characters[ci][1];given:=characters[ci][2][si];g:=Length(given[1]);self:=mul(polys[S+1],mul(mul(cochain[S+1],cochain[S+1]),cochain[S+1]));diff:=sub(self,cubes[S+1]);;
   for j in [1..g] do
    c:=List([1..3],k->cf(diff[k],12-j));if ForAny(c,v->v mod 3<>0) then Error("integral carry");fi;
    code:=Sum([1..3],k->QuoInt(c[k],3)*3^(k-1));scode:=Sum([1..3],k->(cf(self[k],12-j) mod 3)*3^(k-1));;
    wanted:=decode(given[3*block][j])+decode(code)+2*decode(scode);;
    if wanted<>decode(states[si][ci][3*block][j]) then Error("independent norm assembly");fi;
   od;
  od;
 od;
 for ci in [1..466] do for m in [1,2,4,5,7,8] do if states[si][ci][m]<>characters[ci][2][si][m] then Error("additive character assembly");fi;od;od;
 Print("GAP_WITT_ASSEMBLY exponent=",exponents[si]," both_carries=true\n");
od;
Print("GAP_WITT_ASSEMBLY_COMPLETED states30 characters466 coordinates8 modulo9=true\n");
QUIT;
