# Exact coordinate-restriction lifting controls, all 27 partial assignments
# and 27 clause indicators on three variables, over GF(2) and GF(3).
# Set OUT explicitly with GAP -c. No rank or asymptotic hardness test is claimed.
if not IsBound(OUT) then Error("Set OUT"); fi;
out:=OutputTextFile(OUT,false);; SetPrintFormattingStatus(out,false);;
CheckLift:=function(ok,msg) if not ok then Error(msg); fi; end;;
choices:=Tuples([-1,0,1],3);;
total:=0;; compatible:=0;; zeroRestricted:=0;; omittedFactorFailures:=0;;
for prime in [2,3] do
  fld:=GF(prime); ring:=PolynomialRing(fld,3); vars:=IndeterminatesOfPolynomialRing(ring);
  one:=One(ring); zero:=Zero(ring);
  Lit:=function(i,b) if b=1 then return vars[i]; else return one-vars[i]; fi; end;
  for restriction in choices do
    fixed:=Filtered([1..3],i->restriction[i]<>-1);
    indicator:=Product(fixed,i->Lit(i,restriction[i]))*one;
    for clause in choices do
      support:=Filtered([1..3],i->clause[i]<>-1);
      axiom:=Product(support,i->Lit(i,clause[i]))*one;
      conflict:=ForAny(Intersection(fixed,support),i->restriction[i]<>clause[i]);
      values:=List([1..3],function(i)
        if restriction[i]=-1 then return vars[i]; else return restriction[i]*One(fld); fi;
      end);
      restricted:=Value(axiom,vars,values);
      if conflict then
        CheckLift(IsZero(restricted),"conflicting clause not zero"); zeroRestricted:=zeroRestricted+1;
      else
        remaining:=Difference(support,fixed); extra:=Difference(fixed,support);
        expected:=Product(remaining,i->Lit(i,clause[i]))*one;
        multiplier:=Product(extra,i->Lit(i,restriction[i]))*one;
        CheckLift(IsZero(restricted-expected),"wrong restricted indicator");
        CheckLift(IsZero(indicator*restricted-axiom*multiplier),"literal lifting failed");
        CheckLift(Length(Union(support,fixed))<=Length(support)+Length(fixed),"degree count");
        if not IsZero(indicator*restricted-axiom) then
          omittedFactorFailures:=omittedFactorFailures+1;
        fi;
        compatible:=compatible+1;
      fi;
      total:=total+1;
    od;
  od;
  # An adaptive coordinate tree: inspect x1, then x2 on the zero branch,
  # x3 on the one branch. Its leaf indicators still sum literally to one.
  leaves:=[(one-vars[1])*(one-vars[2]),(one-vars[1])*vars[2],
           vars[1]*(one-vars[3]),vars[1]*vars[3]];
  CheckLift(IsZero(Sum(leaves)-one),"adaptive partition failed");
  CheckLift(not IsZero(Sum(leaves{[1..3]})-one),"omitted leaf negative control");
od;
CheckLift(total=1458 and omittedFactorFailures>0,"wrong exhaustive scope");
PrintTo(out,"All cases: ",total,"\nCompatible literal lifts: ",compatible,
  "\nZero restricted clauses: ",zeroRestricted,
  "\nOmitted-factor negative controls rejected: ",omittedFactorFailures,
  "\nAdaptive partition identities: 2\nOmitted-leaf negative controls rejected: 2\nPASS\n");
CloseStream(out); Print("PASS; exact output at ",OUT,"\n"); QUIT;
