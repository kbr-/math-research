# Exact finite-field syndrome diagnostic in F4[F3^2], a satisfiable local algebra.
# Nine basis characters; three code vectors; two syndrome shifts; 16 coefficient pairs.
# Also test a binary axiom-only decoder against its explicit degree-two NS identity.
F:=GF(4);; z:=Zero(F);; o:=One(F);;
labels:=Tuples([0,1,2],2);;
# GAP has row-vector action; define an explicit integer indicator.
bit:=function(b) if b then return 1; else return 0; fi; end;;
shift:=function(b)
 return List(labels,a->List(labels,c->
  o*bit(c=List([1,2],i->(a[i]+b[i]) mod 3))));
end;;
U:=shift([1,0]);; V:=shift([2,0]);; I:=IdentityMat(9,F);;
code:=List([0,1,2],j->List(labels,a->o*bit(a=[0,j])));;
syndrome:=Concatenation(code,code*U);;
if RankMat(code)<>3 or RankMat(syndrome)<>6 then Error("Packing rank"); fi;
decoder:=List(labels,a->List([0,1,2],j->o*bit(a=[0,j])));;
if code*decoder<>IdentityMat(3,F) or code*U*decoder<>NullMat(3,3,F)
 or code*U*V*decoder<>IdentityMat(3,F) then Error("Decoder/cofactor control"); fi;
for coeff in Tuples(Elements(F),2) do
 op:=coeff[1]*I+coeff[2]*U;;
 expected:=3;; if ForAll(coeff,a->a=z) then expected:=0; fi;
 if RankMat(code*op)<>expected then Error("Syndrome injectivity"); fi;
 Print("coefficients=",coeff," restricted_rank=",expected,"\n");
od;
B:=GF(2);; one:=One(B);;
# Coefficients in order 1,x,y,xy; lambda=(1,0,0,1).
functional:=[one,Zero(B),Zero(B),one];;
axioms:=[[0,1,0,0],[0,0,1,0],[1,1,1,1]]*one;;
cofactored:=[0,1,0,1]*one;;
if axioms*functional<>[0,0,0]*one or cofactored*functional<>one
 or axioms[3]+cofactored+axioms[2]<>[1,0,0,0]*one then Error("NS control"); fi;
Print("PASS: code_dimension=3 tensor_rank=6; all 16 error combinations checked.\n");
Print("PASS: decoder kills error, inverse cofactor returns target; binary NS control passes.\n");
QUIT;
