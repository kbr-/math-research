# Exhaustive 10-bit gadget check, all row polarities via constructive
# witnesses, 384 literal proof identities over Q/F2/F3, and one n=3 full
# construction (265 variables,126 modular rows) with every deleted-row witness.
# Does not enumerate the global cube or estimate asymptotic PC degree.
Check:=function(ok,msg) if not ok then Error(msg);fi;end;;
Deg:=function(p) local e,i,d;
 if IsZero(p) then return 0;fi;e:=ExtRepPolynomialRatFun(p);d:=0;
 for i in [1,3..Length(e)-1] do d:=Maximum(d,Sum(e[i]{[2,4..Length(e[i])]}));od;return d;
end;;
PointOn:=function(xs,o,idx,a) local z,i;z:=o;for i in idx do if a[i]=1 then z:=z*xs[i];else z:=z*(o-xs[i]);fi;od;return z;end;;
DotMod:=function(a,b) return Sum([1..Length(a)],i->a[i]*b[i]) mod 3;end;;
rows:=[[1,1,1,1,1,1,2,2,1,0],
 [1,1,1,2,2,2,2,2,1,2],
 [0,1,2,1,1,1,2,2,0,2]];rhs:=[0,0,2];
scopes:=List(rows,a->Filtered([1..10],i->a[i]<>0));
Check(List(scopes,Length)=[9,10,8],"gadget widths");
fld:=GF(3);fe:=One(fld);fz:=Zero(fld);
trans:=List([[1,1,1],[1,1,2],[1,2,1]],r->r*fe);
Check(RankMat(trans)=3,"invertible row mixing");
baseRows:=[[-1,1,0,0,0,0,-1,-1,-1,-1],[-1,0,1,0,0,0,0,0,-1,-1],[0,0,0,1,1,1,0,0,0,-1]];
Check(trans*List(baseRows,r->r*fe)=List(rows,r->r*fe) and trans*([1,2,0]*fe)=rhs*fe,"mixed rows exact");
Print("SIZING gadget_cube=1024; polarity_cases=1792; bad_extensions=128 per proof field; global n=3 only\n");
cube4:=Tuples([0,1],4);privates:=Tuples([0,1],6);goodPriv:=[];badPriv:=[];
localSat:=0;deletionLocal:=0;
for hub in cube4 do
 solutions:=Filtered(privates,a->ForAll([1..3],j->DotMod(rows[j],Concatenation(a,hub))=rhs[j]));
 isNAE:=not (hub=[0,0,0,0] or hub=[1,1,1,1]);
 Check((not IsEmpty(solutions))=isNAE,"NAE4 projection");
 Add(goodPriv,solutions);localSat:=localSat+Length(solutions);
 witnesses:=[];
 if not isNAE then
  for j in [1..3] do
   a:=First(privates,a->ForAll(Difference([1..3],[j]),l->DotMod(rows[l],Concatenation(a,hub))=rhs[l]));
   Check(a<>fail and DotMod(rows[j],Concatenation(a,hub))<>rhs[j],"local deleted-row witness");Add(witnesses,a);deletionLocal:=deletionLocal+1;
  od;
 fi;
 Add(badPriv,witnesses);
od;
# Construct a meet failure for every polarity of each row table.
polarityChecks:=0;
for j in [1..3] do
 k:=Length(scopes[j]);cs:=rows[j]{scopes[j]};
 for flip in Tuples([0,1],k) do
  cc:=List([1..k],i->((1-2*flip[i])*cs[i]) mod 3);bb:=(rhs[j]-Sum([1..k],i->cs[i]*flip[i])) mod 3;
  pair:=First(Combinations([1..k],2),ij->cc[ij[1]]=cc[ij[2]]);Check(pair<>fail,"duplicate nonzero coefficient");
  rest:=Difference([1..k],pair){[1,2]};target:=(bb-cc[pair[1]]) mod 3;
  vals:=First(Tuples([0,1],2),a->(cc[rest[1]]*a[1]+cc[rest[2]]*a[2]) mod 3=target);
  Check(vals<>fail,"two free bits cover F3");a:=List([1..k],i->0);a[rest[1]]:=vals[1];a[rest[2]]:=vals[2];
  b:=ShallowCopy(a);c:=ShallowCopy(a);b[pair[1]]:=1;c[pair[2]]:=1;
  Check(DotMod(cc,a)<>bb and DotMod(cc,b)=bb and DotMod(cc,c)=bb,"polarity meet failure");polarityChecks:=polarityChecks+1;
 od;
od;
# Every bad full tuple extends one original forbidden indicator to the whole
# gadget, and summing the private bits gives the four-hub forbidden indicator.
proofIdentities:=0;
for pf in [Rationals,GF(2),GF(3)] do
 ring:=PolynomialRing(pf,10);xs:=IndeterminatesOfPolynomialRing(ring);o:=One(ring);
 for hub in [[0,0,0,0],[1,1,1,1]] do
  total:=Zero(ring);firstTerm:=fail;
  for private in privates do
   a:=Concatenation(private,hub);j:=First([1..3],j->DotMod(rows[j],a)<>rhs[j]);Check(j<>fail,"some row is violated");
   input:=PointOn(xs,o,scopes[j],a);mult:=PointOn(xs,o,Difference([1..10],scopes[j]),a);
   full:=PointOn(xs,o,[1..10],a);Check(input*mult=full and Deg(full)=10,"paid gadget indicator extension");
   total:=total+full;proofIdentities:=proofIdentities+1;if firstTerm=fail then firstTerm:=full;fi;
  od;
  targetPoly:=PointOn(xs,o,[7..10],Concatenation([0,0,0,0,0,0],hub));
  Check(total=targetPoly and total-firstTerm<>targetPoly,"private indicator sum and omission control");
 od;
 Print("proof field=",pf," gadget replay PASS\n");
od;
# n=3 minimally UNSAT dense 3-CNF, then signed NAE4 with one shared hub t.
n:=3;cycle:=[];
for i in [1..n] do nxt:=i mod n+1;Add(cycle,[i,nxt]);Add(cycle,[-i,-nxt]);od;
Lit:=function(l,a) if l>0 then return a[l];else return 1-a[-l];fi;end;;
ClauseTrue:=function(cl,a) return ForAny(cl,l->Lit(l,a)=1);end;;
cycleWitness:=List([1..2*n],j->First(Tuples([0,1],n),a->ForAll(Difference([1..2*n],[j]),l->ClauseTrue(cycle[l],a))));
Check(ForAll([1..2*n],j->not ClauseTrue(cycle[j],cycleWitness[j])),"odd-cycle minimal witnesses");
clauses:=[];hubWitness:=[];
for i in [1..2*n] do
 Add(clauses,Concatenation([-(2*n+i)],cycle[i]));
 Add(hubWitness,Concatenation(cycleWitness[i],List([1..n],j->0),List([1..2*n],j->1),[0]));
od;
for i in [1..2*n] do for j in [1..2*n] do
 shifted:=List(cycle[j],function(l) if l>0 then return l+n;else return l-n;fi;end);
 Add(clauses,Concatenation([2*n+i],shifted));flags:=List([1..2*n],l->1);flags[i]:=0;
 Add(hubWitness,Concatenation(cycleWitness[i],cycleWitness[j],flags,[0]));
od;od;
num:=Length(clauses);h:=4*n+1;v:=6*num+h;
Check(num=4*n^2+2*n and v=265,"construction sizing");
for j in [1..num] do
 a:=hubWitness[j];Check(ForAll(Difference([1..num],[j]),i->ClauseTrue(clauses[i],a)) and not ClauseTrue(clauses[j],a),"dense-clause deletion witness");
od;
# Build the actual modular coefficient matrix and affine right side.
mat:=[];charges:=[];
for j in [1..num] do
 lits:=Concatenation(clauses[j],[h]);coords:=Concatenation([h+6*(j-1)+1..h+6*j],List(lits,AbsInt));
 for typ in [1..3] do
  rr:=List([1..v],i->fz);bb:=rhs[typ]*fe;
  for i in [1..10] do
   coeff:=rows[typ][i]*fe;
   if i>6 and lits[i-6]<0 then bb:=bb-coeff;coeff:=-coeff;fi;
   rr[coords[i]]:=rr[coords[i]]+coeff;
  od;
  Add(mat,rr);Add(charges,bb);
 od;
od;
Check(RankMat(mat)=3*num,"full row rank");
occ:=List([1..v],i->Number(mat,r->r[i]<>fz));
Check(Minimum(occ)=2 and Number(occ,i->i>=3)=5*num+h,"occurrence and branching counts");
Check(Maximum(List(mat,r->Number(r,x->x<>fz)))=10,"actual original width");
# Every deleted modular row gets one full Boolean witness.
for bad in [1..num] do for typ in [1..3] do
 a:=ShallowCopy(hubWitness[bad]);
 for j in [1..num] do
  hv:=Concatenation(List(clauses[j],l->Lit(l,a)),[a[h]]);pos:=Position(cube4,hv);
  if j=bad then private:=badPriv[pos][typ];else private:=goodPriv[pos][1];fi;
  Append(a,private);
 od;
 residual:=mat*(a*fe)-charges;idx:=3*(bad-1)+typ;
 Check(residual[idx]<>fz and ForAll(Difference([1..3*num],[idx]),i->residual[i]=fz),"full modular row deletion witness");
od;od;
# Local private-code distance proves the tensor lower bound for the radius.
privateRows:=List(baseRows,r->r{[1..6]}*fe);received:=[1,0,0,0,1,2]*fe;
dists:=List(Tuples(Elements(fld),3),lambda->Number(received-lambda*privateRows,x->x<>fz));
Check(Minimum(dists)=3,"private-block coset distance");
Print("TOTAL local_solutions=",localSat," local_deletion_witnesses=",deletionLocal,
 " polarity_checks=",polarityChecks," proof_identities=",proofIdentities,"\n");
Print("GLOBAL n=",n," base_clauses=",num," hubs=",h," variables=",v," rank=",RankMat(mat),
 " deletion_witnesses=",3*num," branching_variables=",Number(occ,i->i>=3)," radius_lower=",3*num,
 " radius_upper=",3*num+h," projection_lower=",3*num," projection_upper=",3*num+h,"\n");
Print("ALL COUPLED CODE CONTROLS PASSED\n");
QUIT;
