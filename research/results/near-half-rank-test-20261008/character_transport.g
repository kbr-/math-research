# Exhaustive character-binomial transport with literal Boolean cofactors.
# q=3 on three variables and q=5 on two variables; all target exponent pairs
# and phases. Also checks a full-field-consistent Boolean-empty ternary coset.
# Set OUT with GAP -c; every completed case is retained in the output file.
if not IsBound(OUT) then Error("Set OUT"); fi;
out:=OutputTextFile(OUT,false);; SetPrintFormattingStatus(out,false);;
CTCheck:=function(ok,msg) if not ok then Error(msg); fi; end;;
ctq:=3;; ctvars:=[];; ctroot:=0;; ctone:=0;; ctring:=0;;
CTChar:=function(a) return Product([1..Length(a)],i->ctone+(ctroot^a[i]-ctone)*ctvars[i]); end;;
CTDegree:=function(p) local e,i,ans;
 if IsZero(p) then return 0; fi;
 e:=ExtRepPolynomialRatFun(p); ans:=0;
 for i in [1,3..Length(e)-1] do ans:=Maximum(ans,Sum(e[i]{[2,4..Length(e[i])]})); od;
 return ans;
end;;
ctmoves:=0;; ctmaxpeak:=0;;
CTMove:=function(state,j,t,ceiling)
 local old,a,b,anew,bnew,new,unit,ar,br,corr,peak;
 a:=state.a; b:=state.b; old:=CTChar(a)-state.phase*CTChar(b);
 unit:=ctone+(ctroot^t-ctone)*ctvars[j];
 anew:=ShallowCopy(a); bnew:=ShallowCopy(b);
 anew[j]:=(a[j]+t) mod ctq; bnew[j]:=(b[j]+t) mod ctq;
 new:=CTChar(anew)-state.phase*CTChar(bnew);
 ar:=ShallowCopy(a); br:=ShallowCopy(b); ar[j]:=0; br[j]:=0;
 corr:=(ctvars[j]^2-ctvars[j])*(ctroot^t-ctone)*
       ((ctroot^a[j]-ctone)*CTChar(ar)-state.phase*(ctroot^b[j]-ctone)*CTChar(br));
 CTCheck(IsZero(old*unit-new-corr),"literal Boolean cofactor failed");
 peak:=Maximum(CTDegree(old*unit),CTDegree(corr),CTDegree(new));
 CTCheck(peak<=ceiling,"transport ceiling exceeded");
 state.a:=anew; state.b:=bnew; state.peak:=Maximum(state.peak,peak);
 ctmoves:=ctmoves+1; ctmaxpeak:=Maximum(ctmaxpeak,peak);
end;;
ctcases:=0;;
for settings in [[3,3,4],[5,2,16]] do
 ctq:=settings[1]; dim:=settings[2]; fld:=GF(settings[3]);
 ctroot:=Z(settings[3])^QuoInt(settings[3]-1,ctq);
 ctring:=PolynomialRing(fld,dim); ctvars:=IndeterminatesOfPolynomialRing(ctring); ctone:=One(ctring);
 vectors:=Tuples([0..ctq-1],dim);
 for p in vectors do for qvec in vectors do
  diff:=List([1..dim],i->(p[i]-qvec[i]) mod ctq);
  support:=Filtered([1..dim],i->diff[i]<>0);
  initiala:=List([1..dim],i->0); initialb:=ShallowCopy(initiala);
  for idx in [1..Length(support)] do
   j:=support[idx];
   if idx<=QuoInt(Length(support)+1,2) then initiala[j]:=diff[j];
   else initialb[j]:=(-diff[j]) mod ctq; fi;
  od;
  common:=Filtered([1..dim],i->p[i]<>0 and qvec[i]<>0);
  pa:=ShallowCopy(p); qb:=ShallowCopy(qvec);
  for j in common do pa[j]:=(p[j]-qvec[j]) mod ctq; qb[j]:=0; od;
  atoB:=Filtered([1..dim],i->initiala[i]<>0 and qb[i]<>0);
  btoA:=Filtered([1..dim],i->initialb[i]<>0 and pa[i]<>0);
  cap:=Maximum(QuoInt(Length(support)+1,2),Number(p,a->a<>0),Number(qvec,a->a<>0))+2;
  for phaseexp in [0..ctq-1] do
   state:=rec(a:=ShallowCopy(initiala),b:=ShallowCopy(initialb),phase:=ctroot^phaseexp,peak:=0);
   pairs:=Minimum(Length(atoB),Length(btoA));
   for idx in [1..pairs] do
    j:=atoB[idx]; CTMove(state,j,(-state.a[j]) mod ctq,cap);
    j:=btoA[idx]; CTMove(state,j,(-state.b[j]) mod ctq,cap);
   od;
   for idx in [pairs+1..Length(atoB)] do j:=atoB[idx]; CTMove(state,j,(-state.a[j]) mod ctq,cap); od;
   for idx in [pairs+1..Length(btoA)] do j:=btoA[idx]; CTMove(state,j,(-state.b[j]) mod ctq,cap); od;
   CTCheck(state.a=pa and state.b=qb,"wrong normalized target");
   for j in common do CTMove(state,j,qvec[j],cap); od;
   CTCheck(state.a=p and state.b=qvec,"wrong final target");
   ctcases:=ctcases+1;
   PrintTo(out,"case ",ctq," ",p," ",qvec," phase ",phaseexp," peak ",state.peak," cap ",cap,"\n");
  od;
 od; od;
od;
# x1+x3=0, x2+x3=2 modulo 3: parameter t=x3 gives
# x1=-t, x2=2-t, x3=t. Each point has one coordinate equal to 2.
ctq:=3;; fld:=GF(4);; ctroot:=Z(4);; ctring:=PolynomialRing(fld,1);;
ctvars:=IndeterminatesOfPolynomialRing(ctring);; ctone:=One(ctring);;
constants:=[0,2,0];; linear:=[2,2,1];;
gvals:=List([1..3],j->List([0..2],function(t)
 local a; a:=(constants[j]+linear[j]*t) mod 3;
 return ctroot^(2*a mod 3)-(One(fld)+ctroot)*ctroot^a+ctroot;
end));;
hvals:=List([1..3],j->List([0..2],t->Zero(fld)));;
for t in [0..2] do
 j:=PositionProperty([1..3],j->not IsZero(gvals[j][t+1]));
 CTCheck(j<>fail,"coset unexpectedly has Boolean point");
 hvals[j][t+1]:=gvals[j][t+1]^-1;
od;
final:=Zero(ctring);;
for j in [1..3] do for beta in [0..2] do
 coeff:=Sum([0..2],t->hvals[j][t+1]*ctroot^((-beta*t) mod 3))/(3*One(fld));
 relation:=ctroot^((2*constants[j]) mod 3)*CTChar([(beta+2*linear[j]) mod 3])
 -(ctone+ctroot)*ctroot^constants[j]*CTChar([(beta+linear[j]) mod 3])
 +ctroot*CTChar([beta]);
 final:=final+coeff*relation;
 PrintTo(out,"Fourier coefficient j=",j," beta=",beta,": ",coeff,"\n");
od; od;
CTCheck(IsZero(final-ctone),"Fourier recombination did not give one");
for t in [0..2] do
 CTCheck(Sum([1..3],j->hvals[j][t+1]*gvals[j][t+1])=One(fld),"partition failed");
 j:=PositionProperty([1..3],j->not IsZero(hvals[j][t+1]));
 CTCheck(Sum(Difference([1..3],[j]),a->hvals[a][t+1]*gvals[a][t+1])<>One(fld),"missing term not detected");
od;
PrintTo(out,"SUMMARY transport_cases=",ctcases," moves=",ctmoves," max_actual_peak=",ctmaxpeak,
 " Fourier_coefficients=9 partition_points=3 omitted_partition_controls=3\nPASS\n");
CloseStream(out); Print("PASS; complete output at ",OUT,"\n"); QUIT;
