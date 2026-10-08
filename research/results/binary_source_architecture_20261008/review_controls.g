# Exact controls for conditional MP defect transport and the coordinate-profile
# counterexample. The MP rule is tested on all six Boolean-valued functions of
# one bit, 4^6=4096 choices, at both multiplier cutoffs 0 and 1.
F:=GF(2);; functionsList:=Tuples([Zero(F),One(F)],2);;
out:=OutputTextFile("research/results/binary_source_architecture_20261008/transport-cases.txt",false);;
SetPrintFormattingStatus(out,false);;
AppendTo(out,"function_indices_P_a_b_u_c_v;Pa_zero;rank_pair_K0;rank_transformed_K0;rank_pair_K1;rank_transformed_K1\n");
valid:=0;; comparisons:=0;; negative:=0;;
for indices in Tuples([1..4],6) do
 vals:=functionsList{indices};
 pref:=vals[1];a:=vals[2];b:=vals[3];u:=vals[4];c:=vals[5];v:=vals[6];
 err1:=List([1..2],i->b[i]-(1-a[i])*u[i]);
 err2:=List([1..2],i->c[i]-(1-u[i])*v[i]);
 trans:=List([1..2],i->(1-a[i])*c[i]-(1-a[i])*v[i]+v[i]*b[i]);
 if trans<>List([1..2],i->(1-a[i])*err2[i]+v[i]*err1[i]) then Error("identity"); fi;
 conditioned:=ForAll([1..2],i->pref[i]*a[i]=Zero(F));
 if conditioned then valid:=valid+1; fi;
 ranks:=[];
 for k in [0..1] do
  domain:=[[One(F),One(F)],[Zero(F),One(F)]]{[1..k+1]};
  oldMat:=List(domain,f->Concatenation(List([1..2],i->pref[i]*err1[i]*f[i]),List([1..2],i->pref[i]*err2[i]*f[i])));
  newMat:=List(domain,f->Concatenation(List([1..2],i->pref[i]*err1[i]*f[i]),List([1..2],i->pref[i]*trans[i]*f[i])));
  oldRank:=RankMat(oldMat);newRank:=RankMat(newMat);
  Append(ranks,[oldRank,newRank]);
  if conditioned then
   comparisons:=comparisons+1;
   if oldRank<>newRank then Error("conditional transport"); fi;
  elif oldRank<>newRank then negative:=negative+1; fi;
 od;
 AppendTo(out,indices,";",conditioned,";",ranks,"\n");
od;
CloseStream(out);
if valid<>2304 or comparisons<>4608 or negative=0 then Error("coverage"); fi;
Print("4096 function tuples; valid=",valid," conditional comparisons=",comparisons,
 " unconditioned rank-mismatch controls=",negative,"\n");
base:=List([97,82,52],m->List([0..6],i->(QuoInt(m,2^i) mod 2)*One(F)));;
permuted:=List(base,row->row{[1,2,3,7,5,6,4]});;
z:=Z(2^13);; ef:=GF(2^13);;
values:=List([1..7],y->(y mod 2)*One(ef)+(QuoInt(y,2) mod 2)*z+(QuoInt(y,4) mod 2)*z^4);;
escapes:=[];; words:=[];;
for B in [base,permuted] do
 BE:=List(B,row->List(row,x->Int(x)*One(ef)));
 mult:=List(BE,row->List([1..7],j->row[j]*values[j]));
 Add(escapes,RankMat(Concatenation(BE,mult))-3);
 Add(words,List(Tuples([Zero(F),One(F)],3),coeff->Number(coeff*B,x->x<>Zero(F))));
od;
if escapes<>[2,3] or words[1]<>words[2] then Error("weight-profile control"); fi;
Print("escape ranks=",escapes," identical word weights=",words[1],"\n");
Print("All assertions passed. The general proofs and degree buffers are analytic.\n");
QUIT;
