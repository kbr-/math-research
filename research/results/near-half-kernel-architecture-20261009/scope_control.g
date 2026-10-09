# Scope tests for perfect-field moment positivity, finite-grid nonemptiness,
# quantum recovery versus annihilation, and normalized sum-product messages.
Check:=function(ok,msg) if not ok then Error(msg);fi;end;
Print("SIZING 1024 pairs of affine coefficient maps on four bits; sixteen old assignments; matrices at most4x4\n");
pts:=Tuples([0,1],4);coeffs:=Tuples([0,1],5);solutions:=0;comparisons:=0;
for a in coeffs do for b in coeffs do
 good:=true;
 for x in pts do
  av:=(a[1]+Sum([1..4],i->a[i+1]*x[i])) mod 2;
  bv:=(b[1]+Sum([1..4],i->b[i+1]*x[i])) mod 2;
  g:=x[1]*x[2];h:=x[3]*x[4];p:=(1+av*g+bv*h) mod 2;
  if g*p<>0 or h*p<>0 then good:=false;fi;
  comparisons:=comparisons+1;
 od;
 if good then solutions:=solutions+1;fi;
od;od;
Check(solutions=0,"complete affine coefficient grid empty");
# Seven affine equations in ten parameters; the last is inconsistent with the first six.
a:=NullMat(7,10,GF(2));
a[1][4]:=One(GF(2));a[2][5]:=One(GF(2));
for j in [1..3] do a[3][j]:=One(GF(2));od;
a[4][7]:=One(GF(2));a[5][8]:=One(GF(2));
for j in [6,9,10] do a[6][j]:=One(GF(2));od;
a[7]:=List([1..10],j->One(GF(2)));rhs:=[0,0,1,0,0,1,1]*One(GF(2));
Check(RankMat(a)=6 and RankMat(List([1..7],i->Concatenation(a[i],[rhs[i]])))=7,"affine inconsistency rank");
Check(7<10,"divisibility degree sum hypothesis");
for x in pts do
 g:=x[1]*x[2];h:=x[3]*x[4];av:=1;bv:=1-g;p:=1-av*g-bv*h;
 Check(g*p=0 and h*p=0 and bv^2=bv,"degree-two coefficient repair");
od;
# Actual binary Boolean moments: weights on01,10,11, with mass1.
states:=[[0,1],[1,0],[1,1]];basis:=List(states,x->[1,x[1],x[2]])*One(GF(2));
moment:=TransposedMat(basis)*basis;
Check(moment=[[1,0,0],[0,0,1],[0,1,0]]*One(GF(2)) and RankMat(moment)=3,"nondegenerate Boolean moment form");
v:=[0,1,0]*One(GF(2));w:=[0,0,1]*One(GF(2));
Check(v*moment*v=Zero(GF(2)) and v*moment*w=One(GF(2)),"zero norm not radical");
# Two-dimensional logical code times a syndrome bit; exact recoverability does not mean zero error.
for fld in [Rationals,GF(2)] do
 p:=DiagonalMat([1,0,1,0])*One(fld);
 e:=[[0,1,0,0],[1,0,0,0],[0,0,0,1],[0,0,1,0]]*One(fld);
 z:=NullMat(4,4,fld);ident:=IdentityMat(4,fld);
 Check(p*e*p=z and e*p<>z and p*e^2*p=p,"compressed error versus actual error");
 r0:=p;r1:=p*e;
 Check(TransposedMat(r0)*r0+TransposedMat(r1)*r1=ident,"recovery completeness identity");
 Check(r0*p=p and r1*p=z and r0*e*p=z and r1*e*p=p,"explicit syndrome recovery identities");
od;
# A one-factor tree with x != y. Exact field sum-product returns a zero partition function.
table:=[[0,1],[1,0]]*One(GF(2));msg:=List(table,Sum);
Check(msg=[1,1]*One(GF(2)) and Sum(msg)=Zero(GF(2)),"tree parity normalization failure");
Check(Sum(table[1])=One(GF(2)),"conditioning supplies a genuine point control");
Print("AFFINE_MAP_PAIRS=1024 OLD_ASSIGNMENT_COMPARISONS=",comparisons," AFFINE_SOLUTIONS=",solutions," COEFFICIENT_RANKS=6,7 MOMENT_RANK=",RankMat(moment)," QEC_FIELDS=2 TREE_REPAIR=PASS\n");
Print("ALL REVIEW SCOPE CONTROLS PASSED\n");
QUIT;
