# Independent test on the actual stored rank-two restrictions, including a negative control.
Read("research/results/bmd-exception-outer-cups-20261008/remainder.g");
f:=GF(27);;o:=One(f);;z:=Zero(f);;x:=Indeterminate(f,"x");;a:=RootsOfPolynomial(f,x^3-x-o)[1];;
decode:=c->(c mod 3)*o+(QuoInt(c,3) mod 3)*a+QuoInt(c,9)*a^2;;
forms:=Filtered(OUTER_QUADRATIC_DATA,r->r[2]=138);;if List(forms,r->r[1])<>[2809,3745] then Error("exact two cases");fi;
for item in forms do
 C:=List(item[5],r->List(r,decode));;zeroCount:=0;;singular:=0;;
 for v in Tuples(Elements(f),2) do if v<>[z,z] and v*C*v=z then zeroCount:=zeroCount+1;fi;od;
 for N in [1,2] do for c in Elements(f) do
  if DeterminantMat(N*C/(2*o)+[[z,c],[-c,z]])=z then singular:=singular+1;fi;
 od;od;
 Print("GAP_ANISOTROPIC exponent=",item[1]," isotropic_vectors=",zeroCount," singular_compatible=",singular," negative_det_character=",(-DeterminantMat(C))^13,"\n");
od;
control:=[[o,z],[z,-o]];;
if Number(Elements(f),c->DeterminantMat(control+[[z,c],[-c,z]])=z)<>2 then Error("isotropic control");fi;
Print("GAP_ANISOTROPIC_COMPLETED actual_forms2 vectors1456 matrices108 control=true\n");
QUIT;
