# Exact checks: first-path mass dominates compatible minimal wide clauses,
# all two-variable binary CNFs (including false/empty/duplicates), b=1,p=1/10.
# Separately check literal-divisor complete-block pruning symbolically in GAP.
# Stages: 1023 indexed families x 3 affine domains x <=9 restrictions;
# then 125 nested clause pairs x two accuracies x GF(2),GF(3).
# No large-instance extrapolation or new rank kernel is used.
wpPatterns:=Tuples([-1,0,1],2);;
wpDomains:=[Tuples([0,1],2),[[0,0],[1,1]],[[0,0]]];;
wpProb:=1/10;; wpTheta:=(2*wpProb/(1-wpProb))^2;;
WpSub:=function(a,b) return ForAll([1..Length(a)],j->a[j]=-1 or a[j]=b[j]); end;;
WpWidth:=function(a) return Number(a,x->x<>-1); end;;
WpViol:=function(a,x) return ForAll([1..Length(a)],j->a[j]=-1 or a[j]=x[j]); end;;
WpRestrict:=function(fam,rho) local out,a,c,j,live;
 out:=[];
 for a in fam do
  live:=true; c:=ShallowCopy(a);
  for j in [1..2] do
   if rho[j]<>-1 then
    if a[j]<>-1 and a[j]<>rho[j] then live:=false; fi;
    c[j]:=-1;
   fi;
  od;
  if live then Add(out,c); fi;
 od;
 return out;
end;;
wpFamilies:=0;; wpCases:=0;; wpPointChecks:=0;; wpAffineGap:=false;;
wpMaxM:=[0,0,0];; wpMaxW:=[0,0,0];;
Print("STAGE indexed CNFs; theorem theta=",wpTheta,"\n");
Print("mask\tduplicate_first\tdomain\tE_minimal\tE_first_mass\tP_semantic_failure\n");
for wpMask in [0..511] do
 wpBase:=Filtered([1..9],j->QuoInt(wpMask,2^(j-1)) mod 2=1);;
 wpFam0:=List(wpBase,j->wpPatterns[j]);;
 wpVariants:=[wpFam0];;
 if Length(wpFam0)>0 then Add(wpVariants,Concatenation(wpFam0,[wpFam0[1]])); fi;
 for wpDup in [1..Length(wpVariants)] do
  wpFam:=wpVariants[wpDup];; wpFamilies:=wpFamilies+1;
  for wpDomainId in [1..3] do
   wpDomain:=wpDomains[wpDomainId];; wpEM:=0;; wpEW:=0;; wpPF:=0;; wpTotalProb:=0;;
   for wpRho in wpPatterns do
    wpFiber:=Filtered(wpDomain,x->ForAll([1..2],j->wpRho[j]=-1 or wpRho[j]=x[j]));;
    if Length(wpFiber)>0 then
     wpCases:=wpCases+1;
     wpLive:=Number(wpRho,x->x=-1);;
     wpMass:=wpProb^wpLive*(1-wpProb)^(2-wpLive)*Length(wpFiber)/Length(wpDomain);;
     wpTotalProb:=wpTotalProb+wpMass;
     wpAlive:=WpRestrict(wpFam,wpRho);; wpDistinct:=Set(wpAlive);;
     wpEasy:=Filtered(wpAlive,x->WpWidth(x)<=1);;
     wpMinimal:=Filtered(wpDistinct,c->not ForAny(wpDistinct,e->e<>c and WpSub(e,c)));;
     wpWide:=Filtered(wpMinimal,c->WpWidth(c)>1);;
     wpCompat:=Filtered(wpWide,c->ForAny(wpFiber,x->WpViol(c,x)));;
     wpM:=Length(wpCompat);; wpW:=0;
     for wpC in wpAlive do
      if WpWidth(wpC)>1 and ForAny(wpFiber,x->WpViol(wpC,x)) then
       wpCount:=Number(wpAlive,e->WpSub(e,wpC));;
       if wpCount<1 then Error("Missing selected clause in count"); fi;
       wpW:=wpW+1/wpCount;
      fi;
     od;
     if wpM>wpW then Error("Minimal count exceeds first mass"); fi;
     wpFailure:=false;
     for wpX in wpFiber do
      wpHv:=not ForAny(wpAlive,c->WpViol(c,wpX));;
      wpKv:=not ForAny(wpEasy,c->WpViol(c,wpX));;
      if wpHv<>wpKv then wpFailure:=true; fi;
      wpPointChecks:=wpPointChecks+1;
     od;
     if wpM=0 and wpFailure then Error("Pruning changed supported function"); fi;
     if wpDomainId=1 and wpM=0 and not ForAll(wpAlive,c->ForAny(wpEasy,e->WpSub(e,c))) then
      Error("Missing syntactic narrow witness");
     fi;
     if wpDomainId=2 and Length(wpWide)>0 and wpM=0 then wpAffineGap:=true; fi;
     wpEM:=wpEM+wpMass*wpM; wpEW:=wpEW+wpMass*wpW;
     if wpFailure then wpPF:=wpPF+wpMass; fi;
    fi;
   od;
   if wpTotalProb<>1 or wpEM>wpEW or wpEW>wpTheta or wpPF>wpEM then Error("Expected bound failed"); fi;
   wpMaxM[wpDomainId]:=Maximum(wpMaxM[wpDomainId],wpEM);
   wpMaxW[wpDomainId]:=Maximum(wpMaxW[wpDomainId],wpEW);
   Print(wpMask,"\t",wpDup-1,"\t",wpDomainId,"\t",wpEM,"\t",wpEW,"\t",wpPF,"\n");
  od;
 od;
od;
if not wpAffineGap then Error("Affine/full-cube distinction control missing"); fi;
Print("RESTRICTION_PASS families=",wpFamilies," conditional_cases=",wpCases," point_checks=",wpPointChecks," max_E_minimal=",wpMaxM," max_E_first_mass=",wpMaxW," affine_gap=true\n");
wpVars:=[];; wpOne:=1;; wpZero:=0;;
WpPol:=function(a) local out,j;
 out:=wpOne;
 for j in [1..3] do
  if a[j]=0 then out:=out*(wpOne-wpVars[j]); elif a[j]=1 then out:=out*wpVars[j]; fi;
 od;
 return out;
end;;
WpDegree:=function(f) local er,ans,i,j,d;
 er:=ExtRepPolynomialRatFun(f); ans:=0;
 if Length(er)=0 then return 0; fi;
 for i in [1,3..Length(er)-1] do
  d:=0; for j in [2,4..Length(er[i])] do d:=d+er[i][j]; od;
  ans:=Maximum(ans,d);
 od; return ans;
end;;
wpPairs:=0;; wpProducts:=0;; wpCompChecks:=0;; wpFieldChecks:=0;; wpMaxCost:=0;; wpWrongCofactor:=false;;
Print("STAGE symbolic source pruning\n");
for wpPrime in [2,3] do
 wpRing:=PolynomialRing(GF(wpPrime),7);; wpVars:=IndeterminatesOfPolynomialRing(wpRing);;
 wpOne:=One(wpRing);; wpZero:=Zero(wpRing);;
 for wpC in Tuples([-1,0,1],3) do
  for wpD in Filtered(Tuples([-1,0,1],3),e->WpSub(e,wpC)) do
   wpPairs:=wpPairs+1;
   wpF:=WpPol(wpD);; wpG:=WpPol(wpC);; wpQpat:=ShallowCopy(wpC);;
   for wpJ in [1..3] do if wpD[wpJ]<>-1 then wpQpat[wpJ]:=-1; fi; od;
   wpQ:=WpPol(wpQpat);;
   if wpG<>wpQ*wpF then Error("Literal factorization failed"); fi;
   for wpH in [1,2] do
    wpSourceP:=wpOne;; wpTargetP:=wpOne;; wpImages:=ShallowCopy(wpVars);;
    for wpU in [1..wpH] do
     wpSourceP:=wpSourceP*(wpOne-wpVars[3+wpU]*wpF-wpVars[5+wpU]*wpG);
     wpTargetP:=wpTargetP*(wpOne-wpVars[3+wpU]*wpF);
     wpImages[5+wpU]:=wpZero;
    od;
    if Value(wpSourceP,wpVars,wpImages)<>wpTargetP then Error("Product substitution failed"); fi;
    wpProducts:=wpProducts+1;
    wpTargetComp:=wpF*wpTargetP;
    if Value(wpG*wpSourceP,wpVars,wpImages)<>wpQ*wpTargetComp then Error("Companion image certificate failed"); fi;
    if Value(wpF*wpSourceP,wpVars,wpImages)<>wpTargetComp then Error("Selected companion failed"); fi;
    wpCompChecks:=wpCompChecks+2;
    wpCost:=WpDegree(wpQ)+WpDegree(wpTargetComp);;
    wpOriginal:=wpH*(WpWidth(wpC)+1)+WpWidth(wpC);;
    if wpCost>wpOriginal then Error("Original degree budget exceeded"); fi;
    wpMaxCost:=Maximum(wpMaxCost,wpCost);
    if wpQ*wpTargetComp<>wpTargetComp then wpWrongCofactor:=true; fi;
    for wpU in [1..wpH] do
     if Value(wpVars[5+wpU]^wpPrime-wpVars[5+wpU],wpVars,wpImages)<>wpZero then Error("Unused field image nonzero"); fi;
     if Value(wpVars[3+wpU]^wpPrime-wpVars[3+wpU],wpVars,wpImages)<>wpVars[3+wpU]^wpPrime-wpVars[3+wpU] then Error("Selected field image changed"); fi;
     wpFieldChecks:=wpFieldChecks+2;
    od;
   od;
  od;
 od;
od;
if not wpWrongCofactor then Error("Cofactor negative control absent"); fi;
Print("PRUNING_PASS pairs=",wpPairs," product_images=",wpProducts," companion_certificates=",wpCompChecks," field_images=",wpFieldChecks," max_original_cost=",wpMaxCost," missing_cofactor_detected=true\n");
Print("ALL_CHECKS_PASSED\n");
QUIT_GAP(0);
