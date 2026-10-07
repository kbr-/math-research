# Exhaustive Boolean common-factor prefix identity: two inputs and two rows.
# 2^7=128 assignments, 256 companion identities; non-Boolean F4 negative control.
F:=GF(2);; z:=Zero(F);; o:=One(F);;
cases:=Tuples([z,o],7);;
if Length(cases)<>128 then Error("Enumeration guard"); fi;
count:=0;;
for a in cases do
 H:=a[1];; u:=a[2];; v:=a[3];;
 q1:=a[4]*u+a[5]*v;; q2:=a[6]*u+a[7]*v;;
 orig:=(o+H*q1)*(o+H*q2);; reduced:=(o+q1)*(o+q2);;
 for h in [u,v] do
  if H*h*orig<>H*h*reduced then Error("Identity failed"); fi;
  count:=count+1;
 od;
 Print("assignment=",List(a,Int)," both_companions=PASS\n");
od;
w:=Z(4);; negative:=w*(One(w)+w);;
if negative=Zero(w) then Error("Negative control lost"); fi;
Print("assignments=",Length(cases)," identities=",count,
 " nonBoolean_F4_difference=",negative,"\n");
Print("PASS: exhaustive binary identity and non-idempotent negative control.\n");
QUIT;
