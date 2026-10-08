# Exhaustive non-tautological resolution parent pairs on three non-pivot bits.
# 27*27 pairs per field; each compatible pair tests the literal common-factor
# identity and ordinary bag degree, over Q,F2,F3. No RM asymptotic test claimed.
Check:=function(ok,msg) if not ok then Error(msg);fi;end;;
Deg:=function(p) local e,i,d;
 if IsZero(p) then return 0;fi;e:=ExtRepPolynomialRatFun(p);d:=0;
 for i in [1,3..Length(e)-1] do d:=Maximum(d,Sum(e[i]{[2,4..Length(e[i])]}));od;return d;
end;;
count:=0;skipped:=0;
for F in [Rationals,GF(2),GF(3)] do
 ring:=PolynomialRing(F,4);xs:=IndeterminatesOfPolynomialRing(ring);o:=One(ring);
 for a in Tuples([0,1,2],3) do for b in Tuples([0,1,2],3) do
  if ForAny([1..3],i->a[i]<>0 and b[i]<>0 and a[i]<>b[i]) then skipped:=skipped+1;continue;fi;
  common:=o;left:=o;right:=o;used:=0;
  for i in [1..3] do
   if a[i]=0 and b[i]=0 then continue;fi;used:=used+1;
   val:=Maximum(a[i],b[i]);if val=1 then factor:=xs[i];else factor:=o-xs[i];fi;
   if a[i]<>0 and b[i]<>0 then common:=common*factor;
   elif a[i]<>0 then left:=left*factor;else right:=right*factor;fi;
  od;
  p:=xs[4]*common*left;q:=(o-xs[4])*common*right;
  terms:=[p*right,q*left];target:=common*left*right;
  Check(IsZero(Sum(terms)-target),"literal resolution simulation");
  Check(Maximum(List(terms,Deg))<=used+1,"pivot bag degree");
  count:=count+1;
 od;od;
 Print("field=",F," all parent pairs PASS\n");
od;
Check(count=1029 and skipped=1158,"enumeration counts");
Print("TOTAL compatible=",count," tautological=",skipped," max bag degree=4\nALL RESOLUTION CONTROLS PASSED\n");
QUIT;
