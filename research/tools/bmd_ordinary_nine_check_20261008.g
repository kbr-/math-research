# Independently reconstruct all Cartier blocks in GAP's finite-field arithmetic.
Read("research/results/bmd-exception-ordinary-extraction-20261008/ordinary-data.g");
f:=GF(3^8); o:=One(f); x:=Indeterminate(f,"x");
pol:=Sum([0..8],i->ORDINARY_FIELD_POLY[i+1]*x^i);
rr:=RootsOfPolynomial(f,pol);;
if Length(rr)<>8 then Error("field polynomial not separable/split"); fi;
a:=rr[1];;
decode:=function(c)
 local z,i;
 z:=Zero(f);
 for i in [0..7] do z:=z+(QuoInt(c,3^i) mod 3)*a^i; od;
 return z;
end;
labels:=List(ORDINARY_LABEL_CODES,decode);;
if Length(Set(labels))<>9 or Zero(f) in labels then Error("bad labels"); fi;
blocks:=0;; genus:=0;; negative:=false;;
for item in ORDINARY_DET_CODES do
 S:=item[1];;
 bits:=Filtered([0..8],i->QuoInt(S,2^i) mod 2=1);;
 g:=QuoInt(Length(bits)-1,2);;
 poly:=Product(bits,i->o+labels[i+1]*x);;
 cc:=CoefficientsOfUnivariatePolynomial(poly);;
 coeff:=function(k)
  if k<0 or k>=Length(cc) then return Zero(f); fi;
  return cc[k+1];
 end;
 H:=List([0..g-1],i->List([0..g-1],j->coeff(3*i+2-j)));;
 det:=DeterminantMat(H);;
 if det=Zero(f) or det<>decode(item[2]) or RankMat(H)<>g then
  Error("Cartier determinant/rank disagreement");
 fi;
 blocks:=blocks+1;; genus:=genus+g;;
 if not negative and g>=2 then
  H[2]:=ShallowCopy(H[1]);
  if DeterminantMat(H)<>Zero(f) or RankMat(H)>=g then Error("corruption not detected"); fi;
  negative:=true;
 fi;
od;
if blocks<>466 or genus<>769 or not negative then Error("incomplete inventory/control"); fi;
Print("GAP_ORDINARY_NINE_COMPLETED: all466determinants_match; total_rank769; duplicate_row_detected\n");
QUIT;
