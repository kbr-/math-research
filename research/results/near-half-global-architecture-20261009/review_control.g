# New architecture controls: bounded monomial rewriting, lifted LCM relations,
# exact linear compression versus multiplication, and reaction normalization.
Check:=function(ok,s) if not ok then Error(s);fi;end;
Print("SIZING 20 monomials through degree 3, two rewrite systems; three coefficient fields; two two-state reaction systems\n");
mons:=Filtered(Tuples([0..3],3),m->Sum(m)<=3);
lead:=[[2,0,0],[0,2,0],[0,0,2],[1,1,0],[0,1,1],[1,0,1]];
# fail denotes the zero polynomial, while [0,0,0] denotes one.
Terminals:=function(m, tails)
 local options,i,next,result;
 if m=fail then return [fail];fi;
 options:=Filtered([1..Length(lead)],i->ForAll([1..3],j->m[j]>=lead[i][j]));
 if Length(options)=0 then return [m];fi;
 result:=[];
 for i in options do
  if tails[i]=fail then AddSet(result,fail);
  else next:=m-lead[i]+tails[i];UniteSet(result,Terminals(next,tails));fi;
 od;
 return result;
end;
badtails:=[[1,0,0],[0,1,0],[0,0,1],[0,0,0],[0,0,0],fail];
goodtails:=[[1,0,0],[0,1,0],[0,0,1],fail,fail,fail];
Check(ForAll(Filtered(mons,m->Sum(m)<=2),m->Length(Terminals(m,badtails))=1),"unique bad-system reductions through degree 2");
Check(Length(Terminals([1,1,1],badtails))=3,"degree-three critical ambiguity");
Check(ForAll(mons,m->Length(Terminals(m,goodtails))=1),"satisfiable control confluence");
Print("REWRITE monomials=",Length(mons)," ambiguous_xyz=",Terminals([1,1,1],badtails),"\n");
fieldchecks:=0;
for fld in [GF(2),GF(3),Rationals] do
 one:=One(fld);zero:=Zero(fld);e:=IdentityMat(4,fld);
 proj:=[[1,0,0,1],[0,0,0,0],[0,0,1,0],[0,0,0,0]]*one;
 tx:=[[0,0,0,0],[1,1,0,0],[0,0,0,0],[0,0,1,1]]*one;
 ty:=[[0,0,0,0],[0,0,0,0],[1,0,1,0],[0,1,0,1]]*one;
 Check(proj^2=proj and tx^2=tx and ty^2=ty and tx*ty=ty*tx,"ambient idempotents and projection");
 Check(proj*e[1]=e[1] and proj*e[2]=0*e[1] and proj*ty*e[2]=e[1],"surviving unit but illegal quotient multiplication");
 rels:=[e[2],e[4]-e[1]];
 Check(ForAll(rels,r->proj*r=0*r),"linear relation elimination");
 Check(RankMat(Concatenation(rels,[e[1]]))=3,"unit absent from static span");
 Check(RankMat(Concatenation(rels,[e[4],e[1]]))=3,"one legal multiplier creates unit");
 Check(proj*tx*proj-(proj*tx*proj)^2=proj*tx*(e-proj)*tx*proj,"compression defect identity");
 lcms:=[[1,-1,0],[1,0,-1],[0,1,-1]]*one;
 Check(RankMat(lcms)=2,"LCM interval has two independent relations");
 ring:=PolynomialRing(fld,["x","y","z"]);vars:=IndeterminatesOfPolynomialRing(ring);x:=vars[1];y:=vars[2];z:=vars[3];
 Check(z*(x*y-one)-x*(y*z-one)=x-z,"first lifted LCM cycle");
 Check(z*(x*y-one)-y*(x*z)=-z,"second lifted LCM cycle");
 Check(z*x*y-x*y*z=0*x and z*x*y-y*x*z=0*x,"monomial tails vanish");
 fieldchecks:=fieldchecks+1;
od;
# The GS lower-series bound truncates by degree three for n=v+1>=3.
n:=3;numrels:=(n-1)*(n+2)/2;raw:=[1,n,n^2-numrels,n*(n^2-2*numrels)];
Check(raw=[1,3,4,-3],"first nontrivial homogenized Boolean GS control");
Print("GS n=3 quadratic_relations=",numrels," raw_coefficients=",raw,"\n");
# A<->B is weakly reversible with deficiency 2-1-1=0.
Check(1/2+1/2=1 and 1*(1/2)=1*(1/2),"positive symmetric equilibrium");
Check(2/3+1/3=1 and 1*(2/3)=2*(1/3),"positive asymmetric equilibrium");
f:=GF(2);pairs:=Tuples(Elements(f),2);
sym:=Filtered(pairs,p->p[1]=p[2] and p[1]+p[2]=One(f));
asym:=Filtered(pairs,p->p[1]=Zero(f)*p[2] and p[1]+p[2]=One(f));
Check(Length(sym)=0,"even normalization obstruction");
Check(asym=[[Zero(f),One(f)]],"odd-denominator support collapse");
Print("FIELDS=",fieldchecks," CHEMICAL symmetric_binary_solutions=",Length(sym)," asymmetric_binary_solutions=",Length(asym),"\n");
momentchecks:=0;
for fld in [GF(2),GF(3),Rationals] do
 one:=One(fld);zero:=Zero(fld);ring6:=PolynomialRing(fld,["a","b","c","u","v","w"]);
 vs:=IndeterminatesOfPolynomialRing(ring6);aa:=vs[1];bb:=vs[2];cc:=vs[3];uu:=vs[4];vv:=vs[5];ww:=vs[6];
 states:=[[1,1,1,0,0,0],[1,1,1,1,0,0],[1,1,1,0,1,0]]*one;
 Moment:=function(f) return -Value(f,vs,states[1])+Value(f,vs,states[2])+Value(f,vs,states[3]);end;
 mon2:=List(Filtered(Tuples([0..2],6),e->Sum(e)<=2),e->Product([1..6],i->vs[i]^e[i]));
 mon1:=Concatenation([one*vs[1]^0],vs);
 for f in [aa-one,bb-one,cc-one,ww] do
  for u in mon2 do Check(Moment(f*u)=zero,"static linear-input moments");momentchecks:=momentchecks+1;od;
 od;
 for f in [aa*bb*(one-uu),bb*cc*(one-vv),uu*vv*(one-ww)] do
  Check(Moment(f)=zero,"static Horn-input moments");momentchecks:=momentchecks+1;
 od;
 for x in vs do for u in mon1 do Check(Moment((x^2-x)*u)=zero,"Boolean moments");momentchecks:=momentchecks+1;od;od;
 Check(Moment(one*vs[1]^0)=one and Moment(one-uu)=zero and Moment(vv*(one-uu))=one,"static versus dynamic counterexample");
 Check(aa*bb*(one-uu)-bb*(one-uu)*(aa-one)-(one-uu)*(bb-one)=one-uu,"degree-three first Horn step");
 Check(bb*cc*(one-vv)-cc*(one-vv)*(bb-one)-(one-vv)*(cc-one)=one-vv,"degree-three second Horn step");
 Check(uu*vv*(one-ww)-vv*(one-ww)*(uu-one)-(one-ww)*(vv-one)=one-ww,"degree-three final Horn step");
od;
Print("STATIC_DESIGN_INPUT_MULTIPLES=",momentchecks,"; legal multiplication defect and degree-three PC proof passed in all three fields\n");

Print("ALL GLOBAL ARCHITECTURE CONTROLS PASSED\n");
QUIT;
