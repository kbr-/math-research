# Fixed exact tests of review translations, not an asymptotic hardness search.
# Two overlapping NAE triples: 32 Boolean assignments, 18 valid states.
# Test every degree<=2 evaluation-kernel basis vector under all five variables.
# Contrast a scalar local moment, a 3x3 Weyl trace, and one species reaction.
if not IsBound(OUT) then Error("Set OUT"); fi;
out:=OutputTextFile(OUT,false);; SetPrintFormattingStatus(out,false);;
Check:=function(ok,msg) if not ok then Error(msg); fi; end;;
f:=GF(2);; one:=One(f);;
points:=Tuples([0,1],5);;
valid:=Filtered(points,a->Length(Set(a{[1,2,3]}))>1 and Length(Set(a{[3,4,5]}))>1);;
Check(Length(points)=32 and Length(valid)=18,"overlap enumeration");;
supports:=Concatenation([[]],Combinations([1..5],1),Combinations([1..5],2));;
EvalMon:=function(s,a) return one*Product(s,i->a[i]); end;;
mat:=List(supports,s->List(valid,a->EvalMon(s,a)));;
kernel:=NullspaceMat(mat);; rank:=RankMat(mat);; checks:=0;;
Check(rank<Length(supports) and Length(kernel)>0,"kernel test must not be vacuous");;
for rel in kernel do
 Check(IsZero(rel*mat),"evaluation kernel");
 for j in [1..5] do
  shifted:=List(supports,s->List(valid,a->EvalMon(Union(s,[j]),a)));
  Check(IsZero(rel*shifted),"vector kernel not stable under multiplication"); checks:=checks+1;
 od;
od;
Check(not IsZero(mat[1]),"empty state vanished");;
PrintTo(out,"overlap states=",Length(valid)," monomials=",Length(supports)," rank=",rank,
 " kernel_basis=",Length(kernel)," shifted_relations=",checks," PASS\n");;
# A normalized scalar moment on genuine satisfying states can have a nonideal
# kernel. This refutes scalar-kernel closure, not the existence of PC designs.
localstates:=[[1,0,0],[0,1,0],[0,0,1]];;
mom:=s->one*Sum(localstates,a->Product(s,i->a[i]));;
Check(mom([])=one and mom([])+mom([1])=Zero(f),"scalar normalization/kernel");;
Check(mom([2])+mom([1,2])=one,"scalar multiplication failure");;
Check(ForAll(localstates,a->Length(Set(a))>1),"local support invalid");;
PrintTo(out,"scalar: Lambda(1)=1; Lambda(1+x)=0; Lambda(y*(1+x))=1; closure claim FALSIFIED\n");;
# Weyl matrices over F4 retain the nontrivial cubic phase in characteristic two.
k:=GF(4);; z:=Z(4);; unit:=IdentityMat(3,k);;
u:=DiagonalMat([One(k),z,z^2]);;
v:=[[0,0,1],[1,0,0],[0,1,0]]*One(k);;
Check(u^3=unit and v^3=unit and u*v=z*v*u,"Weyl convention");;
Check(u*v<>v*u,"direct matrix substitution must fail commutation");;
ordered:=TraceMat(u*v*u^2*v^2);; commuted:=TraceMat(u^3*v^3);;
Check(ordered=z and commuted=One(k),"trace word values");;
Check(ordered<>commuted,"trace must distinguish commuting reorderings");;
spectral:=[];; spectralchecks:=0;;
for m in [u,v] do
 projectors:=List([0..2],a->Sum([0..2],t->z^((-a*t) mod 3)*m^t));
 Check(Sum(projectors)=unit,"spectral partition");
 Check(Sum([0..2],a->z^a*projectors[a+1])=m,"spectral affine reconstruction");
 for a in [1..3] do for b in [1..3] do
  if a=b then Check(projectors[a]*projectors[b]=projectors[a],"spectral idempotent");
  else Check(IsZero(projectors[a]*projectors[b]),"spectral orthogonality"); fi;
  spectralchecks:=spectralchecks+1;
 od; od;
 Add(spectral,projectors);
od;
Check(ForAny(Cartesian([1..3],[1..3]),ab->spectral[1][ab[1]]*spectral[2][ab[2]]<>
 spectral[2][ab[2]]*spectral[1][ab[1]]),"cross-context noncommutation");;
PrintTo(out,"Weyl: Tr(U V U^2 V^2)=",ordered,"; Tr(U^3 V^3)=",commuted,
 "; commutative trace translation FALSIFIED at degree six\n");;
PrintTo(out,"spectral projector products=",spectralchecks,"; both partitions/reconstructions PASS; cross-context commutation FAILS\n");;
# Complex-balanced reaction A <-> 2A with rates 1 and alpha, where alpha>0
# solves alpha^2+alpha-1=0. Its real positive equilibrium is 1/alpha.
# Reduce Z[alpha] modulo two by alpha->z. Boolean positivity means x=1.
r:=PolynomialRing(k,1);; x:=IndeterminatesOfPolynomialRing(r)[1];; o:=One(r);;
reaction:=x-z*x^2;; bool:=x^2-x;; active:=x-o;;
Check(z^2+z+One(k)=Zero(k),"coefficient reduction");;
Check(IsZero(reaction+z*bool-(One(k)-z)*active-(One(k)-z)*o),"degree-two chemical certificate");;
Check(One(k)-z<>Zero(k),"nonzero chemical contradiction");;
PrintTo(out,"chemical: (x-z*x^2)+z*(x^2-x)-(1-z)*(x-1)=1-z !=0; Boolean equilibrium transfer FALSIFIED\n");;
# Exact normalization ledger for the already audited compact colour transfer.
Check((2/9)/(2/3)=1/3 and 1/3<1/2,"encoding normalization control");;
PrintTo(out,"degree ledger: (2/9)/(2/3)=1/3 < 1/2; constant-factor preservation alone is insufficient\nALL CHECKS PASSED\n");;
CloseStream(out);; QUIT;
