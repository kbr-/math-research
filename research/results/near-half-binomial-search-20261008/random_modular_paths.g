# Exact local control for the random-intermediate-combination PC upper proof.
# Run with GAP -c 'OUT := "result path";' before reading this file.
# Exhausts all 3^4 random intermediate row coefficients of one non-star-local
# inconsistent ternary system, its 9 states and 8 balanced character steps.
# This verifies identities and expected supports, not an asymptotic bound.
if not IsBound(OUT) then Error("Set OUT to an explicit output path"); fi;
out := OutputTextFile(OUT, false);;
SetPrintFormattingStatus(out, false);;
PathLog := function(arg) local s; s:=String(arg); PrintTo(out,s,"\n"); end;;
PathCheck := function(ok,msg) if not ok then Error(msg); fi; end;;
F := GF(4);; zeta := Z(4);; one := One(F);; zero := Zero(F);;
R := PolynomialRing(F,3);; xs := IndeterminatesOfPolynomialRing(R);;
pts := Tuples([zero,one],3);;
rows := [[1,1,0],[0,1,1],[1,0,1],[1,1,1]];;
charges := [0,0,0,1];; witness := [1,1,1,1];;
PathCheck(List([1..3],j->Sum([1..4],i->witness[i]*rows[i][j]) mod 3)=[0,0,0],"bad witness");
PathCheck(Sum([1..4],i->witness[i]*charges[i]) mod 3=1,"bad charge");
PathCheck(ForAll([1..3],j->Number(rows,row->row[j]<>0)=3),"not non-star-local");
CharPoly := function(v) return Product([1..3],i->one+(zeta^(v[i] mod 3)-one)*xs[i]); end;;
PathDegree := function(p) local e,i,ds;
  if IsZero(p) then return 0; fi;
  e:=ExtRepPolynomialRatFun(p); ds:=[];
  for i in [1,3..Length(e)-1] do Add(ds,Sum(e[i]{[2,4..Length(e[i])]})); od;
  return Maximum(ds);
end;;
BoolZero := function(p) return ForAll(pts,t->IsZero(Value(p,xs,t))); end;;
BoolIdentity := function(p) PathCheck(BoolZero(p),"Boolean identity failed"); end;;
rowChecks:=0;; support:=[];; active:=[];;
for row in Tuples([0,1,2],3) do
  support:=Filtered([1..3],i->row[i]<>0);
  for b in [0..2] do
    interp:=Zero(R);
    for bits in Tuples([0,1],Length(support)) do
      phase:=Sum([1..Length(support)],i->row[support[i]]*bits[i]) mod 3;
      chi:=Product([1..Length(support)],function(i) if bits[i]=1 then return xs[support[i]]; else return one-xs[support[i]]; fi; end)*One(R);
      interp:=interp+(zeta^phase-zeta^b)*chi;
    od;
    PathCheck(CharPoly(row)-zeta^b=interp,"literal interpolation failed");
    rowChecks:=rowChecks+1;
  od;
od;
sumWidths:=List([1..9],i->0);; pathData:=[];; stepChecks:=0;; reductionChecks:=0;;
coeff:=[];; avec:=[];; bvec:=[];; inc:=[];; delta:=0;;
for middle in Tuples([0,1,2],4) do
  coeff:=[0,0,0,0]; avec:=[0,0,0]; bvec:=[0,0,0]; phase:=0;
  widths:=[0]; peak:=0;
  for step in [1..8] do
    rowidx:=((step-1) mod 4)+1;
    if step<=4 then target:=middle[rowidx]; else target:=witness[rowidx]; fi;
    delta:=(target-coeff[rowidx]) mod 3; coeff[rowidx]:=target;
    inc:=List(rows[rowidx],a->delta*a mod 3); d:=delta*charges[rowidx] mod 3;
    oldpoly:=CharPoly(avec)-zeta^phase*CharPoly(bvec);
    rowpoly:=CharPoly(inc)-zeta^d;
    raw:=oldpoly*CharPoly(inc)+zeta^phase*CharPoly(bvec)*rowpoly;
    PathCheck(raw=CharPoly(avec)*CharPoly(inc)-zeta^((phase+d) mod 3)*CharPoly(bvec),"step identity");
    peak:=Maximum(peak,PathDegree(oldpoly*CharPoly(inc)),PathDegree(CharPoly(bvec)*rowpoly));
    avec:=List([1..3],i->(avec[i]+inc[i]) mod 3); phase:=(phase+d) mod 3;
    newpoly:=CharPoly(avec)-zeta^phase*CharPoly(bvec);
    BoolIdentity(raw-newpoly); reductionChecks:=reductionChecks+1;
    for i in [1..3] do
      if avec[i]<>0 and bvec[i]<>0 then
        oldpoly:=newpoly; unit:=one+(zeta^((-bvec[i]) mod 3)-one)*xs[i];
        avec[i]:=(avec[i]-bvec[i]) mod 3; bvec[i]:=0;
        newpoly:=CharPoly(avec)-zeta^phase*CharPoly(bvec);
        BoolIdentity(oldpoly*unit-newpoly); peak:=Maximum(peak,PathDegree(oldpoly*unit));
        reductionChecks:=reductionChecks+1;
      fi;
    od;
    while AbsInt(Number(avec,a->a<>0)-Number(bvec,a->a<>0))>1 do
      oldpoly:=newpoly;
      if Number(avec,a->a<>0)>Number(bvec,a->a<>0) then
        i:=PositionProperty(avec,a->a<>0); shift:=(-avec[i]) mod 3;
        avec[i]:=0; bvec[i]:=shift;
      else
        i:=PositionProperty(bvec,a->a<>0); shift:=(-bvec[i]) mod 3;
        bvec[i]:=0; avec[i]:=shift;
      fi;
      unit:=one+(zeta^shift-one)*xs[i]; newpoly:=CharPoly(avec)-zeta^phase*CharPoly(bvec);
      BoolIdentity(oldpoly*unit-newpoly); peak:=Maximum(peak,PathDegree(oldpoly*unit));
      reductionChecks:=reductionChecks+1;
    od;
    alpha:=List([1..3],j->Sum([1..4],i->coeff[i]*rows[i][j]) mod 3);
    PathCheck(List([1..3],i->(avec[i]-bvec[i]) mod 3)=alpha,"wrong Gaussian character");
    PathCheck(ForAll([1..3],i->avec[i]=0 or bvec[i]=0),"supports not disjoint");
    width:=Number(alpha,a->a<>0); Add(widths,width);
    sumWidths[step+1]:=sumWidths[step+1]+width;
    PathCheck(PathDegree(newpoly)<=QuoInt(width+1,2),"unbalanced character degree");
    stepChecks:=stepChecks+1;
  od;
  PathCheck(avec=[0,0,0] and bvec=[0,0,0] and phase=1,"failed final state");
  PathCheck(IsZero(newpoly-(one-zeta)),"failed final constant");
  PathCheck(peak<=QuoInt(Maximum(widths)+1,2)+4,"peak exceeds proved path ceiling");
  Add(pathData,rec(middle:=middle,widths:=widths,peak:=peak));
od;
expected:=[];;
for step in [0..8] do
  if step<=4 then active:=[1..step]; else active:=[step-3..4]; fi;
  touched:=Number([1..3],j->ForAny(active,i->rows[i][j]<>0));
  Add(expected,81*2*touched/3);
od;
PathCheck(sumWidths=expected,"random path expectation failed");
# Scope negative control: x=2 modulo 3 is Boolean-unsatisfiable but has no
# linear inconsistency witness over F3, so it cannot trigger this theorem.
PathCheck(not ForAny([0,1,2],a->a mod 3=0 and (2*a) mod 3<>0),"scope control failed");
PathLog(rec(interpolation_checks:=rowChecks,paths:=Length(pathData),states:=9*Length(pathData),
        balanced_steps:=stepChecks,boolean_reductions:=reductionChecks,
        summed_widths:=sumWidths,expected_summed_widths:=expected,scope_negative_control:=true));
for item in pathData do PathLog(item); od;
PrintTo(out,"PASS exact GAP checks\n"); CloseStream(out);
Print("PASS; complete evidence written to ",OUT,"\n");
QUIT;
