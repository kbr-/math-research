Read("research/results/bmd-exception-relative-centres-20261008/matrices.g");
f:=GF(3^8);; x:=Indeterminate(f,"x");;
a:=RootsOfPolynomial(f,Sum([0..8],i->CENTRE_FIELD[i+1]*x^i))[1];;
decode:=function(c)
 local z,i; z:=Zero(f);
 for i in [0..7] do z:=z+(QuoInt(c,3^i) mod 3)*a^i; od;
 return z;
end;;
for item in CENTRE_DATA do
 N:=item[3];; h:=item[4];;
 J0:=List(item[8],row->List(row,decode));;
 if RankMat(J0)<>N then Error("reference jet rank mismatch"); fi;
 J:=List(item[5],row->List(row,decode));;
 C:=List(item[6],row->List(row,decode));;
 K:=NullspaceMat(TransposedMat(J));;
 if RankMat(J)<>N or Length(K)<>h then Error("kernel mismatch"); fi;
 P:=K*C;; stack:=Concatenation(J,TransposedMat(C));;
 if RankMat(P)<>h or DeterminantMat(P)=Zero(f) or RankMat(stack)<>N+h then Error("pairing mismatch"); fi;
 P[1]:=List(P[1],z->Zero(f));;
 if RankMat(P)<>h-1 then Error("corruption not detected"); fi;
 Print("GAP_CENTRE b=",item[1]," jet_rank=",N," pairing_rank=",h," stack_rank=",N+h," corruption_detected\n");
od;
Print("GAP_RELATIVE_CENTRES_COMPLETED cases=2\n");
QUIT;
