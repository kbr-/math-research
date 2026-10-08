Read("research/results/bmd-exception-stable-projection-20261008/matrices.g");
f:=GF(3^6);; x:=Indeterminate(f,"x");;
z:=RootsOfPolynomial(f,Sum([0..6],i->STABLE_FIELD[i+1]*x^i))[1];;
decode:=function(c)
 local v,i; v:=Zero(f);
 for i in [0..5] do v:=v+(QuoInt(c,3^i) mod 3)*z^i; od;
 return v;
end;;
a:=decode(612);; o:=One(f);;
if a^3+2*a+2*o<>Zero(f) then Error("wrong F27 embedding"); fi;
labels:=List([0..8],i->a^i);; stable:=0;; blocks:=0;;
for S in [1..511] do
 bits:=Filtered([0..8],i->QuoInt(S,2^i) mod 2=1);;
 g:=QuoInt(Length(bits)-1,2);;
 if g>0 then
  poly:=Product(bits,i->o+labels[i+1]*x);;
  cc:=CoefficientsOfUnivariatePolynomial(poly);;
  coeff:=function(k)
   if k<0 or k>=Length(cc) then return Zero(f); fi;
   return cc[k+1];
  end;;
  B:=List([0..g-1],i->List([0..g-1],j->coeff(3*i+2-j)));;
  D:=List(B,row->List(row,v->v^9))*List(B,row->List(row,v->v^3))*B;;
  P:=D^9360;;
  if P*P<>P or D^4*(IdentityMat(g,f)-P)<>NullMat(g,g,f) then Error("projector mismatch"); fi;
  stable:=stable+RankMat(P);; blocks:=blocks+1;;
 fi;
od;
if stable<>744 or blocks<>466 then Error("stable dimensions"); fi;
for item in STABLE_DATA do
 N:=item[2];; h:=item[3];;
 C:=List(item[6],row->List(row,decode));;
 if N=0 then K:=IdentityMat(h,f);; stack:=TransposedMat(C);;
 else
  J:=List(item[4],row->List(row,decode));;
  J0:=List(item[5],row->List(row,decode));;
  if RankMat(J)<>N or RankMat(J0)<>N then Error("jet ranks"); fi;
  K:=NullspaceMat(TransposedMat(J));;
  if Length(K)<>h then Error("kernel"); fi;
  stack:=Concatenation(J,TransposedMat(C));;
 fi;
 R:=K*C;;
 if RankMat(R)<>item[7] or RankMat(stack)<>N+item[7] then Error("relative rank"); fi;
 if item[7]=h then
  R[1]:=List(R[1],v->Zero(f));;
  if RankMat(R)<>h-1 then Error("corruption"); fi;
 fi;
 Print("GAP_STABLE_RETURN b=",item[1]," kernel=",h," rank=",item[7]," stack_rank=",N+item[7],"\n");
od;
Print("GAP_STABLE_PROJECTION_COMPLETED stable_rank744 blocks466 cases3 corruption_detected\n");
QUIT;
