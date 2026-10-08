# Exact generator certificates for one-row generalized-PHP restriction.
# Every bit pattern, m/r/n=4/2/3 and 5/3/4, over GF(2) and GF(3).
# No closure, model enumeration, or inferred degree lower bound is tested.
# Output full counts to stdout; archive via save-run-output.py.
vars:=[];; one:=1;; zero:=0;; ncol:=0;;
RowSplitSumPol:=function(xs) local ans,z; ans:=zero; for z in xs do ans:=ans+z; od; return ans; end;;
RowSplitProdPol:=function(xs) local ans,z; ans:=one; for z in xs do ans:=ans*z; od; return ans; end;;
RowSplitCell:=function(i,j) return vars[(i-1)*ncol+j]; end;;
RowSplitTerm:=function(S,j) return RowSplitProdPol(List(S,i->RowSplitCell(i,j))); end;;
RowSplitDegreePol:=function(f) local e,ans,i,j,d;
 e:=ExtRepPolynomialRatFun(f); ans:=0;
 for i in [1,3..Length(e)-1] do
  d:=0; for j in [2,4..Length(e[i])] do d:=d+e[i][j]; od;
  ans:=Maximum(ans,d);
 od; return ans;
end;;
RowSplitGenerators:=function(rows,rr,cols) local out,S,j,k,x,i;
 out:=[];
 for S in Combinations(rows,rr) do
  Add(out,rec(kind:="row",S:=S,pol:=RowSplitSumPol(List(cols,j->RowSplitTerm(S,j)))-one));
  for j in cols do for k in cols do if j<k then
   Add(out,rec(kind:="collision",S:=S,j:=j,k:=k,pol:=RowSplitTerm(S,j)*RowSplitTerm(S,k)));
  fi; od; od;
 od;
 for S in Combinations(rows,rr+1) do for j in cols do
  Add(out,rec(kind:="cap",S:=S,j:=j,pol:=RowSplitTerm(S,j)));
 od; od;
 for i in rows do for j in cols do
  x:=RowSplitCell(i,j); Add(out,rec(kind:="bool",S:=[i],j:=j,pol:=x*x-x));
 od; od;
 return out;
end;;
checks:=0;; nonzeroChecks:=0;; families:=0;; maxCost:=0;; wrongOverlapDetected:=false;;
RowSplitCheckCert:=function(lhs,terms,available,bound) local rhs,t,cost;
 rhs:=zero;
 for t in terms do
  if not t[2] in available then Error("Unlisted certificate generator"); fi;
  cost:=RowSplitDegreePol(t[1])+RowSplitDegreePol(t[2]);
  if cost>bound then Error("Certificate degree exceeds bound"); fi;
  maxCost:=Maximum(maxCost,cost); rhs:=rhs+t[1]*t[2];
 od;
 if lhs<>rhs then Error("Polynomial certificate identity failed"); fi;
 checks:=checks+1; if lhs<>zero then nonzeroChecks:=nonzeroChecks+1; fi;
end;;
for prime in [2,3] do
 for pars in [[4,2,3],[5,3,4]] do
  mrow:=pars[1]; threshold:=pars[2]; ncol:=pars[3];
  ring:=PolynomialRing(GF(prime),mrow*ncol);;
  vars:=IndeterminatesOfPolynomialRing(ring);; one:=One(ring);; zero:=Zero(ring);;
  allrows:=[1..mrow]; freeRows:=[1..mrow-1]; allcols:=[1..ncol];
  original:=RowSplitGenerators(allrows,threshold,allcols);;
  for bits in Tuples([0,1],ncol) do
   classes:=[Filtered(allcols,j->bits[j]=0),Filtered(allcols,j->bits[j]=1)];;
   targets:=Concatenation(RowSplitGenerators(freeRows,threshold,classes[1]),
                          RowSplitGenerators(freeRows,threshold-1,classes[2]));;
   targetPols:=List(targets,g->g.pol);;
   images:=ShallowCopy(vars);;
   for j in allcols do images[(mrow-1)*ncol+j]:=bits[j]*one; od;
   sourcePols:=List(original,g->Value(g.pol,vars,images));;
   # Restricted source -> two target systems.
   for gi in [1..Length(original)] do
    g:=original[gi]; lhs:=sourcePols[gi]; terms:=[];
    hasFixed:=mrow in g.S; S:=Difference(g.S,[mrow]);
    if lhs=zero then
     RowSplitCheckCert(lhs,[],targetPols,2*threshold);
    elif g.kind="row" then
     if hasFixed then terms:=[[one,lhs]];
     else
      targetRow:=RowSplitSumPol(List(classes[1],j->RowSplitTerm(S,j)))-one;
      terms:=[[one,targetRow]];
      for j in classes[2] do Add(terms,[one,RowSplitTerm(S,j)]); od;
     fi;
     RowSplitCheckCert(lhs,terms,targetPols,2*threshold);
    elif g.kind="cap" then
     if hasFixed or g.j in classes[1] then terms:=[[one,lhs]];
     else
      small:=S{[1..threshold]}; extra:=Difference(S,small);
      terms:=[[RowSplitTerm(extra,g.j),RowSplitTerm(small,g.j)]];
     fi;
     RowSplitCheckCert(lhs,terms,targetPols,2*threshold);
    elif g.kind="collision" then
     if hasFixed or (g.j in classes[1] and g.k in classes[1]) then terms:=[[one,lhs]];
     elif g.j in classes[2] then terms:=[[RowSplitTerm(S,g.k),RowSplitTerm(S,g.j)]];
     else terms:=[[RowSplitTerm(S,g.j),RowSplitTerm(S,g.k)]];
     fi;
     RowSplitCheckCert(lhs,terms,targetPols,2*threshold);
    else RowSplitCheckCert(lhs,[[one,lhs]],targetPols,2*threshold);
    fi;
   od;
   # Target -> restricted source. Only zero-class row equations need correction.
   for g in targets do
    if g.pol in sourcePols then
     RowSplitCheckCert(g.pol,[[one,g.pol]],sourcePols,2*threshold);
    else
     if g.kind<>"row" or Length(g.S)<>threshold then Error("Unexpected inverse generator"); fi;
     sourceRow:=RowSplitSumPol(List(allcols,j->RowSplitTerm(g.S,j)))-one;
     terms:=[[one,sourceRow]];
     for j in classes[2] do Add(terms,[-one,RowSplitTerm(g.S,j)]); od;
     RowSplitCheckCert(g.pol,terms,sourcePols,2*threshold);
     if Length(classes[2])>0 and sourceRow<>g.pol then wrongOverlapDetected:=true; fi;
    fi;
   od;
   families:=families+1;
  od;
 od;
od;
if families<>48 or nonzeroChecks=0 or not wrongOverlapDetected then Error("Missing controls"); fi;
Print("families=",families," generator_certificates=",checks,
 " nonzero_identities=",nonzeroChecks," max_certificate_degree=",maxCost,"\n");
Print("PASS: both exact generator transfers; all bit patterns; GF(2),GF(3); missing row correction detected.\n");
QUIT;
