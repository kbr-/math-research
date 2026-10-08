# Exact scheduled-review controls; no asymptotic degree extrapolation.
# Lex monomial support test reuses prior Boolean ideal/echelon helpers.
RB:=function(rows) if IsEmpty(rows) then return [];fi;return BaseMat(rows);end;;
Same:=function(U,V) return Length(U)=Length(V) and Length(RB(Concatenation(U,V)))=Length(U);end;;
Meet:=function(U,V)
  local rel,n;
  if IsEmpty(U) or IsEmpty(V) then return [];fi;
  n:=Length(U);rel:=NullspaceMat(Concatenation(U,V));
  return RB(List(rel,c->c{[1..n]}*U));
end;;
DegreeOfVector:=function(row,degs)
  local nz;
  nz:=Filtered([1..Length(row)],i->not IsZero(row[i]));
  if IsEmpty(nz) then return -1;fi;
  return Maximum(degs{nz});
end;;
Ambient:=function(F,n)
  local mons,degs,cube,ind,cache,data;
  mons:=Combinations([1..n]);
  Sort(mons,function(a,b) local i; for i in Concatenation(Reversed([1,3..n-1]),[2,4..n]) do if (i in a)<>(i in b) then return i in a;fi;od;return false;end);
  degs:=List(mons,Length);cube:=Tuples([0,1],n);
  ind:=List(cube,a->List(mons,S->(function()
    local ones;
    ones:=Filtered([1..n],i->a[i]=1);
    if IsSubset(S,ones) then return (-One(F))^(Length(S)-Length(ones));fi;
    return Zero(F);
  end)()));
  return rec(F:=F,n:=n,mons:=mons,degs:=degs,cube:=cube,ind:=ind,cache:=rec(),factorizations:=0);
end;;
IdealData:=function(A,allowed)
  local key,rows,parts,tops,d,positions;
  key:=Concatenation(List([1..Length(A.cube)],function(i) if i in allowed then return "1";else return "0";fi;end));
  if IsBound(A.cache.(key)) then return A.cache.(key);fi;
  rows:=RB(A.ind{Difference([1..Length(A.cube)],allowed)});
  parts:=List([0..A.n],d->Filtered(rows,r->DegreeOfVector(r,A.degs)<=d));
  tops:=List([0..A.n],d->RB(List(parts[d+1],r->List([1..Length(r)],j->(function()
    if A.degs[j]=d then return r[j];fi;return Zero(A.F);
  end)()))));
  A.cache.(key):=rec(rows:=rows,parts:=parts,tops:=tops);
  A.factorizations:=A.factorizations+1;
  return A.cache.(key);
end;;
TopData:=function(data,d) if d+1>Length(data.tops) then return [];fi;return data.tops[d+1];end;;
Mult:=function(A,row,i,graded)
  local out,j,S,k;
  out:=List(A.mons,S->Zero(A.F));
  for j in [1..Length(row)] do
    if IsZero(row[j]) then continue;fi;
    S:=A.mons[j];
    if graded and i in S then continue;fi;
    k:=Position(A.mons,Union(S,[i]));out[k]:=out[k]+row[j];
  od;
  return out;
end;;
Check:=function(ok,msg) if not ok then Error(msg);fi;end;;
# Directly test the source's reducibility condition for the naive induced-vertex support.
# Stop once the prediction is falsified: K3 (64 cube points), otherwise K4 (256).
for nverts in [3,4] do
 A:=Ambient(GF(2),2*nverts);sets:=Combinations([1..nverts]);inits:=[];
 for S in sets do
  allowed:=Filtered([1..Length(A.cube)],idx->ForAll(Combinations(S,2),e->A.cube[idx]{[2*e[1]-1,2*e[1]]}<>A.cube[idx]{[2*e[2]-1,2*e[2]]}));
  data:=IdealData(A,allowed);
  Add(inits,Set(List(data.rows,r->A.mons[First([1..Length(r)],i->not IsZero(r[i]))])));
 od;
 bad:=[];
 for mon in A.mons do
  support:=Set(List(mon,i->QuoInt(i+1,2)));
  if mon in Last(inits) and not mon in inits[Position(sets,support)] then Add(bad,mon);fi;
 od;
 Print("naive induced support K",nverts," counterexamples=",bad,"\n");
 if not IsEmpty(bad) then break;fi;
od;
# Literal zero-odd-moment obstruction, without any Pfaffian rank assumptions.
for F in [GF(2),GF(4)] do
 R:=PolynomialRing(F,6);x:=IndeterminatesOfPolynomialRing(R);o:=One(R);
 u:=[x[1],x[3],x[5]];v:=[x[2],x[4],x[6]];
 total:=Zero(R);
 for e in Combinations([1..3],2) do
  k:=First([1..3],i->not i in e);
  total:=total+(o+u[k])*(o+u[e[1]]+u[e[2]])*(o+v[e[1]]+v[e[2]]);
 od;
 rhs:=o+Sum(u)+Sum(Combinations([1..3],2),e->u[e[1]]*u[e[2]]*(v[e[1]]+v[e[2]]));
 Check(IsZero(total-rhs),"odd moment literal triangle identity");
 Print("odd moment triangle identity field=",F," PASS\n");
od;
# Probability-bound parameter controls. Counts and powers are exact integers/rationals.
# These test nonvacuity of the estimate, not samples or PC hardness.
for ell in [3,4,8,12] do
 nv:=ell*2^ell;kw:=4*ell;mr:=3*2^(ell-2);q:=NextPrimeInt(nv^2);
 Check(q<=2*nv^2,"prime interval");
 eps:=(mr+3*nv)/q+mr*q/2^kw+2^nv/q^mr+q/(mr*2^kw);
 Print("source ell=",ell," v=",nv," k=",kw," m=",mr," q=",q," bound<1=",eps<1,"\n");
 if ell>=4 then Check(eps<1,"nonvacuous source estimate");fi;
od;
Print("ALL REVIEW CONTROLS PASSED (support counterexamples, if present, are the tested outcome)\n");
QUIT;
