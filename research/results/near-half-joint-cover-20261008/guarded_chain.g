# Guarded-chain controls over F2/F3: four parameter triples per field, at most 128 points.
# Reuses the preceding separator checker filtered-basis helpers. Tests actual truncated ideals.
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
  Sort(mons,function(a,b) if Length(a)<>Length(b) then return Length(a)>Length(b);fi;return a<b;end);
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
  key:=String(allowed);
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
Mon:=function(A,S)
 local r; r:=List(A.mons,m->Zero(A.F));r[Position(A.mons,S)]:=One(A.F);return r;
end;;
MulSet:=function(A,r,S)
 local out,i;out:=r;for i in S do out:=Mult(A,out,i,false);od;return out;
end;;
Member:=function(A,r,i) return r-Mult(A,r,i,false);end;;
Contains:=function(rows,r) return Length(RB(Concatenation(rows,[r])))=Length(rows);end;;
count:=0;;ideals:=0;;identities:=0;;
for p in [2,3] do
 for pars in [[2,1,1],[3,1,1],[2,2,1],[3,1,2]] do
  t:=pars[1];k:=pars[2];c:=pars[3];n:=t*k+t-1+c;D:=t*k+c;
  if n>7 then Error("sizing gate");fi;
  A:=Ambient(GF(p),n);groups:=List([1..t],j->[(j-1)*k+1..j*k]);
  zs:=[t*k+1..t*k+t-1];spect:=[t*k+t..n];
  gs:=[];
  Add(gs,Member(A,Mon(A,groups[1]),zs[1]));
  for j in [2..t-1] do Add(gs,Member(A,Mult(A,Mon(A,groups[j]),zs[j-1],false),zs[j]));od;
  Add(gs,Mult(A,Mon(A,groups[t]),zs[t-1],false));
  Allowed:=function(point,j)
    local product;product:=Product(point{groups[j]});
    if j=1 then return product*(1-point[zs[1]])=0;
    elif j=t then return product*point[zs[t-1]]=0;
    else return product*point[zs[j-1]]*(1-point[zs[j]])=0;fi;
  end;;
  cover:=[];
  for S in Filtered(Combinations([1..t]),s->Length(s)<t) do
    j:=First([1..t],i->not i in S);
    zval:=List([1..t-1],function(i) if i<j then return 1;else return 0;fi;end);
    if not ForAll(Filtered(A.cube,point->point{zs}=zval),point->ForAll(S,i->Allowed(point,i))) then Error("disabling assignment");fi;
    ideal:=IdealData(A,Filtered([1..Length(A.cube)],i->ForAll(S,j->Allowed(A.cube[i],j))));
    Append(cover,ideal.parts[D+1]);ideals:=ideals+1;
  od;
  cover:=RB(cover);P:=Mon(A,[1..t*k]);W:=spect{[1..c-1]};w:=Last(spect);
  target:=MulSet(A,P,spect);pred:=MulSet(A,P,W);
  if Contains(cover,target) or not Contains(cover,pred) or Contains(cover,Mon(A,[])) then Error("cutoff separation");fi;
  prefix:=gs[1];
  for j in [2..t-1] do
    left:=Member(A,MulSet(A,prefix,groups[j]),zs[j]);
    right:=MulSet(A,gs[j],[1..(j-1)*k]);
    if Maximum(DegreeOfVector(left,A.degs),DegreeOfVector(right,A.degs))>j*k+2 then Error("prefix cost");fi;
    prefix:=left+right;
    if prefix<>Member(A,Mon(A,[1..j*k]),zs[j]) then Error("prefix identity");fi;
    identities:=identities+1;
  od;
  left:=MulSet(A,prefix,groups[t]);right:=MulSet(A,gs[t],[1..(t-1)*k]);
  if left+right<>P or Maximum(DegreeOfVector(left,A.degs),DegreeOfVector(right,A.degs))>t*k+1 then Error("final fall");fi;
  if DegreeOfVector(MulSet(A,left,W),A.degs)>D or DegreeOfVector(MulSet(A,right,W),A.degs)>D then Error("weighted cost");fi;
  identities:=identities+1;count:=count+1;
  Print("p=",p," t,k,c=",pars," n=",n," D=",D," Kdim=",Length(cover)," WP in, wWP and 1 out; identities PASS\n");
 od;
od;
Print("TOTAL cases=",count," proper ideals=",ideals," derivation identities=",identities," ALL GUARDED CHAIN CONTROLS PASSED\n");
QUIT;
