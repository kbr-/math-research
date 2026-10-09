# Exhaust all three-bit relations and coordinate splits over F2,F3.
# Compare direct filtered module-map feasibility, bounded-degree supported
# trace weights, and failure of a monic degree drop. Native GAP ranks/solves.
# Coefficient matrices have at most nine rows and eight columns; augmented
# feasibility matrices add one column. Printed sizing refers to coefficients.
RankSafe:=function(a)
 if Length(a)=0 or Length(a[1])=0 then return 0; fi;
 return RankMat(a);
end;
Ev:=function(mon,pt,one,zero)
 if IsSubset(pt,mon) then return one; else return zero; fi;
end;
Feasible:=function(a,b)
 return RankSafe(a)=RankSafe(List([1..Length(a)],i->Concatenation(a[i],[b[i]])));
end;
Iverson:=function(b) if b then return 1; else return 0; fi; end;
Main:=function()
local casecount,successcount,mapchecks,signedchecks,k,pts,prime,F,one,zero,allowedidx,allowed,forbidden,shared,priv,ns,nt,lower,elow,eplus,nodrop,pars,pm,sm,direct,rhs,hasmap,wm,wa,hasweight,sol,wval,p,sp,pp,vs,vals,coef,j,q,rel,fibersizes,fiberranks,a,fiber,rr;
Print("SIZING 256 three-bit relations x8 splits x2 fields; matrices<=9x8; one seven-bit scope control\n");
casecount:=0; successcount:=0; mapchecks:=0; signedchecks:=0;
k:=3; pts:=Combinations([1..k]);
for prime in [2,3] do
 F:=GF(prime); one:=One(F); zero:=Zero(F);
 for allowedidx in Combinations([1..Length(pts)]) do
  allowed:=pts{allowedidx}; forbidden:=Difference(pts,allowed);
  for shared in Combinations([1..k]) do
   priv:=Difference([1..k],shared); ns:=Length(shared); nt:=Length(priv);
   lower:=Filtered(pts,m->Length(m)<ns);
   elow:=List(allowed,p->List(lower,m->Ev(m,p,one,zero)));
   eplus:=List(allowed,p->Concatenation(List(lower,m->Ev(m,p,one,zero)),[Ev(shared,p,one,zero)]));
   nodrop:=RankSafe(eplus)>RankSafe(elow);
   pars:=[];
   for pm in Combinations(priv) do
    for sm in Combinations(shared) do
     if Length(sm)<=Length(pm) then Add(pars,[pm,sm]); fi;
    od;
   od;
   direct:=List(forbidden,p->List(pars,z->Ev(Intersection(p,priv),z[1],one,zero)*Ev(z[2],p,one,zero)*((-one)^(Length(z[1])-Length(Intersection(p,priv))))));
   # Avoid negative exponents on zero factors: finite-field -1 is invertible.
   Add(direct,List(pars,z->Ev(z[1],[],one,zero)*Ev(z[2],[],one,zero)));
   rhs:=Concatenation(List(forbidden,p->zero),[one]);
   hasmap:=Feasible(direct,rhs);
   wm:=Filtered(pts,m->Length(m)<=nt);
   wa:=List(forbidden,p->List(wm,m->Ev(m,p,one,zero)));
   Add(wa,List(wm,m->Iverson(m=priv)*one));
   hasweight:=Feasible(wa,rhs);
   if not(nodrop=hasmap and hasmap=hasweight) then Error("criterion mismatch"); fi;
   casecount:=casecount+1;
   if hasweight then
    successcount:=successcount+1;
    sol:=SolutionMat(TransposedMat(wa),rhs);
    if sol=fail then Error("rank/solve disagreement"); fi;
    wval:=p->Sum([1..Length(wm)],i->sol[i]*Ev(wm[i],p,one,zero));
    for p in forbidden do if wval(p)<>zero then Error("weight support"); fi; od;
    sp:=Combinations(shared); pp:=Combinations(priv);
    vs:=List(sp,p->List(sp,m->Ev(m,p,one,zero)));
    for pm in pp do
     vals:=List(sp,a->Sum(pp,b->((-one)^(nt-Length(b)))*wval(Union(a,b))*Ev(pm,b,one,zero)));
     coef:=vals*Inverse(TransposedMat(vs));
     for j in [1..Length(sp)] do
      if Length(sp[j])>Length(pm) and coef[j]<>zero then Error("degree increase"); fi;
     od;
     if Length(pm)=0 and not ForAll(vals,z->z=one) then Error("not unital"); fi;
     mapchecks:=mapchecks+1;
    od;
    signedchecks:=signedchecks+Length(forbidden);
   fi;
  od;
 od;
od;
# Binary raw conditional affine sections need not give a filtered retraction.
F:=GF(2); one:=One(F); zero:=Zero(F);
sp:=Combinations([1..3]); pp:=Combinations([4..7]);
q:=b->(Iverson(IsSubset(b,[4,5]))+Iverson(IsSubset(b,[6,7]))) mod 2;
rel:=[]; fibersizes:=[]; fiberranks:=[];
for a in sp do
 fiber:=Filtered(pp,b->q(b)=Iverson(Length(a)=3));
 Add(fibersizes,Length(fiber));
 rr:=RankMat(List(fiber,b->Concatenation([one],List([4..7],i->Iverson(i in b)*one))));
 Add(fiberranks,rr); if rr<>5 then Error("fiber not affine-full"); fi;
 Append(rel,List(fiber,b->Union(a,b)));
od;
if RankMat(List(rel,p->Concatenation([one],List([1..7],i->Iverson(i in p)*one))))<>8 then Error("row not affine-full"); fi;
if not ForAll(rel,p->Iverson(IsSubset(p,[1..3]))=q(p)) then Error("monic drop"); fi;
Print("EXHAUSTIVE_CASES=",casecount," RETRACTIONS=",successcount," FILTERED_MOMENT_CHECKS=",mapchecks," ZERO_SUPPORT_CHECKS=",signedchecks,"\n");
Print("RAW_SECTION_ROW_SIZE=",Length(rel)," FIBER_SIZES=",fibersizes," FIBER_AFFINE_RANKS=",fiberranks," FULL_AFFINE_RANK=8 MONIC_DROP_DEGREE=3_TO_2\n");
Print("ALL FILTERED RETRACTION CONTROLS PASSED\n");
end;
Main();
QUIT;
