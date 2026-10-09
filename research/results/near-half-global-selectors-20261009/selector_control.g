# Genuine marginal coefficient spaces, all-context selectors, and a nonlocal repair.
Check:=function(ok,s) if not ok then Error(s);fi;end;
Contains:=function(a,b) return ForAll(b,x->x in a);end;
Build:=function(scopes,allowed,n,fld)
 local out,M,a,b,Q,offs,total,rows,S,z,row,t,j,idx,localM,E,right,sol,dim;
 M:=[[]];for j in [1..n] do AddSet(M,[j]);od;
 for a in [1..Length(scopes)] do for b in [a+1..Length(scopes)] do
  for S in Combinations(Intersection(scopes[a],scopes[b])) do AddSet(M,S);od;
 od;od;
 offs:=[0];for a in [1..Length(scopes)] do Add(offs,Last(offs)+Length(allowed[a]));od;total:=Last(offs);
 rows:=[];
 for a in [1..Length(scopes)] do for b in [a+1..Length(scopes)] do
  Q:=Intersection(scopes[a],scopes[b]);
  for z in Tuples([0,1],Length(Q)) do
   row:=List([1..total],j->Zero(fld));
   for t in [1..Length(allowed[a])] do
    if List(Q,j->allowed[a][t][Position(scopes[a],j)])=z then row[offs[a]+t]:=One(fld);fi;
   od;
   for t in [1..Length(allowed[b])] do
    if List(Q,j->allowed[b][t][Position(scopes[b],j)])=z then row[offs[b]+t]:=-One(fld);fi;
   od;
   Add(rows,row);
  od;
 od;od;
 localM:=[];right:=[];
 for a in [1..Length(scopes)] do
  idx:=Filtered([1..Length(M)],j->Contains(scopes[a],M[j]));Add(localM,idx);
  E:=List(idx,j->List(allowed[a],x->Product(M[j],i->x[Position(scopes[a],i)])*One(fld)));
  Check(RankMat(E)=Length(idx),"overlap evaluation onto");
  sol:=List(IdentityMat(Length(idx),fld),b->SolutionMat(TransposedMat(E),b));
  Check(not fail in sol,"native right inverse");Add(right,TransposedMat(sol));
 od;
 out:=rec(scopes:=scopes,allowed:=allowed,n:=n,fld:=fld,M:=M,offs:=offs,rows:=rows,right:=right,localM:=localM);
 out.basis:=NullspaceMat(TransposedMat(rows));return out;
end;
Mom:=function(data,w,S)
 local a;
 a:=First([1..Length(data.scopes)],a->Contains(data.scopes[a],S));
 Check(a<>fail,"requested moment has context");
 return Sum([1..Length(data.allowed[a])],t->w[data.offs[a]+t]*Product(S,i->data.allowed[a][t][Position(data.scopes[a],i)]));
end;
SelectBit:=function(data,w,i,repair)
 local moments,S,owners,a,t,new,part;
 moments:=[];
 for S in data.M do
  owners:=Filtered([1..Length(data.scopes)],a->Contains(data.scopes[a],Union(S,[i])));
  if Length(owners)>0 then Add(moments,Mom(data,w,Union(S,[i])));
  elif repair and Length(S)=1 and Set([i,S[1]])=[1,3] then Add(moments,Mom(data,w,[])-Mom(data,w,[2]));
  else Add(moments,Zero(data.fld));fi;
 od;
 new:=[];
 for a in [1..Length(data.scopes)] do
  if i in data.scopes[a] then
   part:=List([1..Length(data.allowed[a])],t->w[data.offs[a]+t]*data.allowed[a][t][Position(data.scopes[a],i)]);
  else part:=data.right[a]*moments{data.localM[a]};fi;
  Append(new,part);
 od;
 return new;
end;
Matrices:=function(data,repair)
 return List([1..data.n],i->List(data.basis,w->SolutionMat(data.basis,SelectBit(data,w,i,repair))));
end;
Print("SIZING Hardy 13 local coordinates/6 compatible dimensions; path 6/4; three fields; 960 overlap-rank checks\n");
fieldschecked:=0;compatchecks:=0;idchecks:=0;masschecks:=0;
for fld in [GF(2),GF(3),Rationals] do
 one:=One(fld);zero:=Zero(fld);
 # Variables a,a',b,b' are 1,2,3,4.
 scopes:=[[1,3],[1,4],[2,3],[2,4]];
 allowed:=[Tuples([0,1],2),[[0,1],[1,0],[1,1]],[[0,1],[1,0],[1,1]],[[0,0],[0,1],[1,0]]];
 data:=Build(scopes,allowed,4,fld);Check(Length(data.basis)=6,"Hardy compatible dimension");
 mats:=Matrices(data,false);
 for i in [1..4] do
  Check(mats[i]^2=mats[i],"Hardy selector idempotence");idchecks:=idchecks+1;
  for w in data.basis do
   wi:=SelectBit(data,w,i,false);Check(data.rows*wi=List(data.rows,r->zero),"all-context compatibility");compatchecks:=compatchecks+1;
   for j in [1..4] do
    Check(Mom(data,SelectBit(data,SelectBit(data,w,j,false),i,false),[])=Mom(data,SelectBit(data,SelectBit(data,w,i,false),j,false),[]),"mass commutator zero");masschecks:=masschecks+1;
   od;
  od;
 od;
 original:=[1,0,0,0,1,1,-1,0,1,0,0,0,1]*one;
 Check(data.rows*original=List(data.rows,r->zero),"original Hardy compatibility");
 repaired:=original-SelectBit(data,original,1,false);
 expected:=[1,0,0,0,1,0,0,0,1,0,-1,1,1]*one;
 Check(repaired=expected and data.rows*repaired=List(data.rows,r->zero),"Hardy all-context selector repair");
 localonly:=ShallowCopy(original);
 for a in [1..2] do for t in [1..Length(allowed[a])] do
  localonly[data.offs[a]+t]:=original[data.offs[a]+t]*(1-allowed[a][t][1]);
 od;od;
 Check(data.rows*localonly<>List(data.rows,r->zero),"old componentwise negative control");
 # p=(1-a)(1-b') is an original clause. The chosen vector map does not kill it.
 temp:=original-SelectBit(data,original,4,false);
 axiomimage:=temp-SelectBit(data,temp,1,false);
 Check(Mom(data,axiomimage,[])=zero and Mom(data,axiomimage,[2])=one,"source axiom only mass-zero");
 Check(Mom(data,SelectBit(data,axiomimage,2,false),[])=one,"legal degree-three cofactor failure");
 # Two positive clauses on a path: zero filling fails at degree two, a global missing moment repairs it.
 path:=Build([[1,2],[2,3]],[[[0,1],[1,0],[1,1]],[[0,1],[1,0],[1,1]]],3,fld);
 Check(Length(path.basis)=4,"path compatible dimension");
 unit:=Concatenation([1,1,-1],[1,1,-1])*one;
 comm:=SelectBit(path,SelectBit(path,unit,2,false),1,false)-SelectBit(path,SelectBit(path,unit,1,false),2,false);
 Check(Mom(path,comm,[])=zero and Mom(path,comm,[3])=one,"zero-fill vector commutator");
 fixed:=Matrices(path,true);ident:=IdentityMat(4,fld);
 for i in [1..3] do Check(fixed[i]^2=fixed[i],"repaired idempotence");
  for j in [1..3] do Check(fixed[i]*fixed[j]=fixed[j]*fixed[i],"repaired global commutation");od;
 od;
 Check((ident-fixed[1])*(ident-fixed[2])=NullMat(4,4,fld) and (ident-fixed[2])*(ident-fixed[3])=NullMat(4,4,fld),"repaired clause annihilation");
 states:=[[0,1,0],[0,1,1],[1,1,0],[1,0,1]];
 Check(RankMat(List(states,x->Concatenation([1],x))*one)=4,"four actual model basis");
 fieldschecked:=fieldschecked+1;
od;
# The sparse quadratic row spaces needed for double overlaps.
rankchecks:=0;k:=6;pts:=Tuples([0,1],k);
for coeff in Tuples([1,2],k) do
 target:=(2*Sum(coeff)) mod 3;
 allowed:=Filtered(pts,x->(Sum([1..k],i->coeff[i]*x[i])-target) mod 3=0);
 for pair in Combinations([1..k],2) do
  mat:=List(allowed,x->Concatenation([1],x,[x[pair[1]]*x[pair[2]]])*One(GF(2)));
  Check(RankMat(mat)=k+2,"one-quadratic overlap moment map");rankchecks:=rankchecks+1;
 od;
od;
supportchecks:=0;
for pair in Combinations([1..3],2) do
 for cf in Difference(Tuples([0,1],5),[[0,0,0,0,0]]) do
  support:=Number(Tuples([0,1],3),x->(cf[1]+Sum([1..3],i->cf[i+1]*x[i])+cf[5]*x[pair[1]]*x[pair[2]]) mod 2=1);
  Check(support>=2,"nonzero quadratic support lower bound");supportchecks:=supportchecks+1;
 od;
od;
Print("FIELDS=",fieldschecked," COMPATIBILITY=",compatchecks," IDEMPOTENCE=",idchecks," MASS_COMMUTATION=",masschecks," OVERLAP_RANKS=",rankchecks," QUADRATIC_SUPPORTS=",supportchecks,"\n");
Print("ALL GLOBAL SELECTOR CONTROLS PASSED\n");
QUIT;
