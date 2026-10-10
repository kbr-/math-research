# Exact GAP verification of the entire degree<=12 secant determinant polynomial.
F:=GF(27);; o:=One(F);; zz:=Zero(F);;
g:=First(Elements(F),x->x^3-x+o=zz);;
if g=fail or g^3=g then Error("Bad cubic generator");fi;
z:=[zz,o,g,g^2,g+o];;
Secant:=function(B)
 local rows,i,j,ti,tj,u,out,k,m;
 rows:=[];
 for i in [1..5] do for j in [i+1..5] do
  ti:=z[i]^3+B*z[i];tj:=z[j]^3+B*z[j];
  if ti=tj then Error("Bad interpolation point");fi;
  u:=[o,ti+tj,ti*tj,(ti+tj)^3];out:=[];
  for k in [0..9] do
   m:=QuoInt(k,3);
   if k mod 3=0 then Add(out,u[m+1]);
   elif k mod 3=1 then Add(out,(z[i]*(u[m+2]+tj*u[m+1])-z[j]*(u[m+2]+ti*u[m+1]))/(ti-tj));
   else Add(out,(-z[i]^2*(u[m+2]+tj*u[m+1])+z[j]^2*(u[m+2]+ti*u[m+1]))/(ti-tj));fi;
  od;Add(rows,out);
 od;od;
 return DeterminantMat(rows);
end;;
expected:=B->g*B^5+2*g*B^4+(2*g+2*o)*B^3+(2*g^2+g+o)*B^2+B+(g^2+2*o);;
safe:=Filtered(Elements(F),B->Length(Set(List(z,x->x^3+B*x)))=5);;
if Length(safe)<13 then Error("Not enough safe interpolation points");fi;
for i in [1..13] do
 if Secant(safe[i])<>expected(safe[i]) then Error("Full polynomial mismatch");fi;
od;
# Bound12 follows from each column j having beta degree<=floor(j/3), with exact division.
# Thirteen distinct safe values prove the entire stored polynomial, not just sampling.
Print("GAP_SHEAR_POLYNOMIAL_VERIFIED points=13 degree_bound=12 actual_degree=5\n");
Print("SECANT_SHEAR_INDEPENDENT_COMPLETED\n");
QUIT;
