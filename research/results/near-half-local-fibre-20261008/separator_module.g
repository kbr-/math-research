# Exact one-bit separator quotient and multiplier controls.
# All 256 pairs of two-variable relations, over F2 and F3, with zero/one
# spectator; then 25 nonmonomial-fibre pairs in five variables over both fields.
# The relation census has dimension at most 32; the majority controls at most 128. Each ideal is echelonized once,
# with descending-degree columns, to obtain all filtration cutoffs at once.
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
PrivateTop:=function(A,P,rows,d)
  local out,r,v,j,S;
  out:=[];
  for r in rows do
    v:=List(P.mons,S->Zero(P.F));
    for j in [1..Length(r)] do
      S:=A.mons[j];
      if Length(S)=d and not 1 in S then v[Position(P.mons,List(S,i->i-1))]:=r[j];fi;
    od;
    Add(out,v);
  od;
  return RB(out);
end;;
stats:=rec(cases:=0,cutoffs:=0,actions:=0,nonzero:=0);;
Scenario:=function(p,na,nb,c,relsA,relsB,label)
  local F,A,P,ia,ib,ra,rb,Ua,Vb,fa,fb,eps,ok,I,J,U,V,L,Ks,Ns,Es,d,
        common,denom,images,actual,predicted,actualRank,predictedRank,i,low,
        dims,acts,allActs,prev,added;
  F:=GF(p);A:=Ambient(F,1+na+nb+c);P:=Ambient(F,na+nb+c);
  ia:=[1..na+1];ib:=Concatenation([1],[na+2..na+nb+1]);
  for ra in [1..Length(relsA)] do
    I:=IdealData(A,Filtered([1..Length(A.cube)],i->A.cube[i]{ia} in relsA[ra]));
    U:=[];
    for eps in [0,1] do
      Add(U,IdealData(P,Filtered([1..Length(P.cube)],i->Concatenation([eps],P.cube[i]{[1..na]}) in relsA[ra])));
    od;
    for rb in [1..Length(relsB)] do
      J:=IdealData(A,Filtered([1..Length(A.cube)],i->A.cube[i]{ib} in relsB[rb]));
      V:=[];
      for eps in [0,1] do
        Add(V,IdealData(P,Filtered([1..Length(P.cube)],i->Concatenation([eps],P.cube[i]{[na+1..na+nb]}) in relsB[rb])));
      od;
      L:=IdealData(A,Filtered([1..Length(A.cube)],i->A.cube[i]{ia} in relsA[ra] and A.cube[i]{ib} in relsB[rb]));
      Ks:=[];Ns:=[];Es:=[];prev:=[];
      for d in [0..A.n] do
        added:=Concatenation(Filtered(I.rows,r->DegreeOfVector(r,A.degs)=d),Filtered(J.rows,r->DegreeOfVector(r,A.degs)=d));
        prev:=RB(Concatenation(prev,added));Add(Ks,prev);
        common:=Meet(RB(Concatenation(TopData(U[1],d),TopData(V[1],d))),RB(Concatenation(TopData(U[2],d),TopData(V[2],d))));
        denom:=RB(Concatenation(Meet(TopData(U[1],d),TopData(U[2],d)),Meet(TopData(V[1],d),TopData(V[2],d))));
        Add(Ns,common);Add(Es,denom);
      od;
      dims:=[];allActs:=[];
      for d in [0..A.n-1] do
        low:=Filtered(Ks[d+2],r->DegreeOfVector(r,A.degs)<=d);
        if not Same(low,L.parts[d+1]) then Error("one-degree fibre splitting");fi;
        if not Same(PrivateTop(A,P,L.parts[d+1],d),Ns[d+1]) then Error("numerator image");fi;
        if not Same(PrivateTop(A,P,Ks[d+1],d),Es[d+1]) then Error("denominator image");fi;
        if Length(low)-Length(Ks[d+1])<>Length(Ns[d+1])-Length(Es[d+1]) then Error("separator quotient");fi;
        Add(dims,Length(Ns[d+1])-Length(Es[d+1]));
        stats.cutoffs:=stats.cutoffs+1;
        if Last(dims)>0 then stats.nonzero:=stats.nonzero+1;fi;
        acts:=[];
        for i in [1..A.n] do
          actual:=List(L.parts[d+1],r->Mult(A,r,i,false));
          actualRank:=Length(RB(Concatenation(Ks[d+2],actual)))-Length(Ks[d+2]);
          if i=1 then predictedRank:=0;
          else
            predicted:=List(Ns[d+1],r->Mult(P,r,i-1,true));
            predictedRank:=Length(RB(Concatenation(Es[d+2],predicted)))-Length(Es[d+2]);
          fi;
          if actualRank<>predictedRank then Error("multiplier action");fi;
          Add(acts,actualRank);stats.actions:=stats.actions+1;
        od;
        Add(allActs,acts);
      od;
      if label="majority" then
        for d in [0..A.n-1] do
          if d>=2 and d<=2+c then predictedRank:=4*Binomial(c,d-2);else predictedRank:=0;fi;
          if dims[d+1]<>predictedRank then Error("majority Hilbert function");fi;
          if not ForAll(allActs[d+1]{[1..5]},r->r=0) then Error("majority private actions");fi;
          if d>=2 and d<=c+1 then predictedRank:=4*Binomial(c-1,d-2);else predictedRank:=0;fi;
          if not ForAll(allActs[d+1]{[6..A.n]},r->r=predictedRank) then Error("majority spectator rank");fi;
        od;
      fi;
      stats.cases:=stats.cases+1;
      Print(label," p=",p," c=",c," pair=",[ra-1,rb-1]," H=",dims," actions=",allActs,"\n");
    od;
  od;
  Print("scenario ",label," p=",p," c=",c," factorizations=",[A.factorizations,P.factorizations]," PASS\n");
end;;
localCube:=Tuples([0,1],2);;
rels:=List([0..15],mask->Filtered(localCube,t->QuoInt(mask,2^(2*t[1]+t[2])) mod 2=1));;
for p in [2,3] do for c in [0,1] do Scenario(p,1,1,c,rels,rels,"exhaustive");od;od;
three:=Tuples([0,1],3);;
special:=[Filtered(three,t->Sum(t) mod 2=0),Filtered(three,t->Sum(t) mod 2=1),
          Filtered(three,t->t[1]=t[2]*t[3]),Filtered(three,t->Sum(t)>=2),Filtered(three,t->Sum(t)<=1)];;
for p in [2,3] do Scenario(p,2,2,0,special,special,"nonmonomial");od;
for p in [2,3] do for c in [0,1,2] do Scenario(p,2,2,c,[special[4]],[special[5]],"majority");od;od;
Print("TOTAL cases=",stats.cases," cutoffs=",stats.cutoffs," actions=",stats.actions,
      " nonzero fall quotients=",stats.nonzero," PASS\n");
# The paper's Hardy family is compatible, but the specified componentwise
# selector (leave contexts not containing a unchanged) destroys compatibility.
for F in [Rationals,GF(2),GF(3)] do
  family:=List([[1,0,0,0],[0,1,1,-1],[0,0,1,0],[0,0,1,0]],r->List(r,t->t*One(F)));;
  contexts:=[[1,2],[1,4],[3,2],[3,4]];;points:=Tuples([0,1],2);;
  Marginal:=function(v,pos)
    return List([0,1],bit->Sum(Filtered([1..4],i->points[i][pos]=bit),i->v[i]));
  end;;
  for i in [1..4] do for j in [i+1..4] do
    shared:=Intersection(contexts[i],contexts[j]);
    for coord in shared do
      if Marginal(family[i],Position(contexts[i],coord))<>Marginal(family[j],Position(contexts[j],coord)) then Error("Hardy compatibility");fi;
    od;
  od;od;
  changed:=List(family,ShallowCopy);;
  for i in [1,2] do changed[i][3]:=Zero(F);changed[i][4]:=Zero(F);od;
  if Marginal(changed[2],2)=Marginal(changed[4],2) then Error("Hardy selector control");fi;
od;
Print("Hardy selector: rational, binary and ternary compatibility / failure controls PASS\n");
Print("ALL SEPARATOR MODULE CONTROLS PASSED\n");
QUIT;
