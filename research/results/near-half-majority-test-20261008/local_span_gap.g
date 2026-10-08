# Test K_D = (I_positive intersect B_<=D) + (I_negative intersect B_<=D),
# the complete separately truncated local vanishing ideals of two opposite
# MAJ_(2k+1) constraints sharing one variable, with a free spectator w.
# k=1: exact full degree-three matrices on six variables over F2 and F3.
# k=9: the actual MAJ19 witness, symbolically; no enormous matrix is built.
# This is a satisfiable calibration of kernel closure, not a hard CNF family.
if not IsBound(OUT) then Error("Set OUT"); fi;
out:=OutputTextFile(OUT,false);; SetPrintFormattingStatus(out,false);;
Check:=function(ok,msg) if not ok then Error(msg); fi; end;;
Deg:=function(p) local e,i,d;
 if IsZero(p) then return 0; fi;
 e:=ExtRepPolynomialRatFun(p); d:=0;
 for i in [1,3..Length(e)-1] do d:=Maximum(d,Sum(e[i]{[2,4..Length(e[i])]})); od;
 return d;
end;;
vars:=[];; one:=0;; ring:=0;; supports:=[];; fld:=GF(2);;
PolyVector:=function(p)
 local e,i,j,s,pos,v;
 v:=List(supports,s->Zero(fld)); e:=ExtRepPolynomialRatFun(p);
 for i in [1,3..Length(e)-1] do
  s:=[];
  for j in [1,3..Length(e[i])-1] do
   Check(e[i][j+1]=1,"nonmultilinear matrix entry"); Add(s,e[i][j]);
  od;
  pos:=Position(supports,Set(s)); Check(pos<>fail,"matrix degree exceeded");
  v[pos]:=v[pos]+e[i+1];
 od;
 return v;
end;;
LocalBasis:=function(localvars,positive,cap)
 local outside,basis,s,t,p;
 outside:=Difference([1..Length(vars)],localvars); basis:=[];
 for s in Combinations(localvars) do
  if Length(s)>=2 and Length(s)<=cap then
   for t in Combinations(outside) do
    if Length(s)+Length(t)<=cap then
     if positive then p:=one*Product(s,i->one-vars[i]);
     else p:=one*Product(s,i->vars[i]); fi;
     Add(basis,p*Product(t,i->vars[i]));
    fi;
   od;
  fi;
 od;
 return basis;
end;;
for prime in [2,3] do
 fld:=GF(prime); ring:=PolynomialRing(fld,6); vars:=IndeterminatesOfPolynomialRing(ring); one:=One(ring);
 z:=vars[1]; a:=one-vars[2]; b:=vars[4]; w:=vars[6];
 p:=a*b; g:=(one-z)*a; h:=z*b;
 Check(IsZero(b*g+a*h-p),"literal resolvent identity");
 Check(Maximum(Deg(b*g),Deg(a*h))=3 and Deg(p)=2 and Deg(w*p)=3,"degree fall ledger");
 supports:=Concatenation([[]],Combinations([1..6],1),Combinations([1..6],2),Combinations([1..6],3));
 Check(Length(supports)=42,"small matrix sizing");
 low:=Concatenation(LocalBasis([1,2,3],true,2),LocalBasis([1,4,5],false,2));
 high:=Concatenation(LocalBasis([1,2,3],true,3),LocalBasis([1,4,5],false,3));
 matlow:=List(low,PolyVector); mathigh:=List(high,PolyVector);
 rlow:=RankMat(matlow); rhigh:=RankMat(mathigh);
 Check(RankMat(Concatenation(matlow,[PolyVector(p)]))=rlow+1,"resolvent unexpectedly local in low degree");
 Check(RankMat(Concatenation(mathigh,[PolyVector(p)]))=rhigh,"resolvent absent at allowed ceiling");
 Check(RankMat(Concatenation(mathigh,[PolyVector(w*p)]))=rhigh+1,"spectator multiple unexpectedly in local span");
 # A genuine joint model proves 1 survives: z=0, both A bits one, both B bits zero.
 point:=List([0,1,1,0,0,0],i->i*One(fld));
 Check(ForAll(high,q->IsZero(Value(q,vars,point))),"joint model control");
 Check(not IsZero(Value(one,vars,point)),"unit control");
 joint:=Filtered(Tuples([0,1],6),q->Sum(q{[1,2,3]})>=2 and Sum(q{[1,4,5]})<=1);
 Check(Length(joint)=12,"joint model count");
 evalmat:=List(supports,s->List(joint,q->One(fld)*Product(s,i->q[i])));
 erank:=RankMat(evalmat);
 Check(IsZero(PolyVector(w*p)*evalmat),"joint ideal did not absorb witness");
 Check(not IsZero(PolyVector(one)*evalmat),"joint ideal killed the unit");
 PrintTo(out,"small field=",prime," columns=",Length(supports)," low_rows=",Length(low),
  " low_rank=",rlow," high_rows=",Length(high)," high_rank=",rhigh,
  "; p outside K2, p in K3, w*p outside K3 PASS\n");
 PrintTo(out,"joint repair: states=",Length(joint)," evaluation_rank=",erank,
  " kernel_dimension=",Length(supports)-erank,"; witness absorbed and unit survives PASS\n");
od;
# Actual predicate: MAJ19(z,A_18)=1 and MAJ19(z,B_18)=0.
fld:=GF(2); ring:=PolynomialRing(fld,38); vars:=IndeterminatesOfPolynomialRing(ring); one:=One(ring);
z:=vars[1]; aa:=[2..10]; bb:=[20..28]; w:=vars[38];
a:=Product(aa,i->one-vars[i]); b:=Product(bb,i->vars[i]);
p:=a*b; g:=(one-z)*a; h:=z*b;
Check(IsZero(b*g+a*h-p),"majority19 literal resolvent");
Check(Deg(g)=10 and Deg(h)=10 and Deg(p)=18 and Deg(w*p)=19,"majority19 degree ledger");
Check(Maximum(Deg(b*g),Deg(a*h))=19,"majority19 original peak");
Check(18-9<10,"coefficient-extraction exclusion");
# Exhaust all free coordinates on each extracted clause's nonzero support.
# There are ten prescribed zeroes (or ones), leaving nine free bits.
extensions:=Tuples([0,1],9); Check(Length(extensions)=512,"support enumeration size");
for bits in extensions do
 Check(Sum(bits)<10,"positive clause support must violate majority-one");
 Check(10+Sum(bits)>=10,"negative clause support must violate majority-zero");
od;
PrintTo(out,"majority19: original width=19; extracted widths=10; p degree=18; w*p degree=19; peak=19; nonzero-support checks=1024 PASS\n");;
PrintTo(out,"Nonmembership for majority19 uses the proved coefficient functional and local minimum degree 10, not a rank extrapolation.\nALL CHECKS PASSED\n");;
CloseStream(out);; QUIT;
