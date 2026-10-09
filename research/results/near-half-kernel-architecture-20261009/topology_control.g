# Characteristic-two alternating-cochain compiler and graph chain certificates.
# Uses native GAP SolutionMat on packed binary boundary matrices, never custom elimination.
Check:=function(ok,msg) if not ok then Error(msg);fi;end;
Alt:=function(labs,start)
 local a,i;
 if Length(Set(List(labs,AbsInt)))<>Length(labs) then return 0;fi;
 a:=ShallowCopy(labs);Sort(a,function(x,y)return AbsInt(x)<AbsInt(y);end);
 for i in [1..Length(a)] do if SignInt(a[i])<>start*(-1)^(i-1) then return 0;fi;od;
 return 1;
end;
DeltaAlt:=function(labs)
 return (Sum([1..Length(labs)],i->Alt(labs{Difference([1..Length(labs)],[i])},1))+Alt(labs,1)+Alt(labs,-1)) mod 2;
end;
cochainchecks:=0;
Print("SIZING alternating multisets: palettes1..5, lengths2..palette+2; graph tests <=22 signed nodes through dimension3 or <=10 through dimension4\n");
for m in [1..5] do
 labels:=Concatenation([-m..-1],[1..m]);
 for q in [2..m+2] do
  Check(Binomial(2*m+q-1,q)<=12000,"multiset sizing");
  for labs in UnorderedTuples(labels,q) do
   if ForAll(labs,x->not -x in labs) then
    Check(DeltaAlt(labs)=0,"alternating coboundary identity");cochainchecks:=cochainchecks+1;
   fi;
  od;
 od;
od;
Check(DeltaAlt([1,-1])=1,"complementary-label negative control");
Graph:=function(n,edges)
 local adj,e;
 adj:=List([1..n],i->List([1..n],j->false));
 for e in edges do adj[e[1]][e[2]]:=true;adj[e[2]][e[1]]:=true;od;
 return rec(n:=n,adj:=adj,edges:=edges);
end;
Complete:=function(n) return Graph(n,Combinations([1..n],2));end;
CycleGraphControl:=function(n) return Graph(n,Concatenation(List([1..n-1],i->[i,i+1]),[[1,n]]));end;
Mycielski:=function(g)
 local edges,e,i,n;
 n:=g.n;edges:=ShallowCopy(g.edges);
 for e in g.edges do Add(edges,[e[1],n+e[2]]);Add(edges,[e[2],n+e[1]]);od;
 for i in [1..n] do Add(edges,[n+i,2*n+1]);od;
 return Graph(2*n+1,edges);
end;
Face:=function(g,f)
 local pos,neg;
 pos:=Filtered(f,i->i<=g.n);neg:=List(Filtered(f,i->i>g.n),i->i-g.n);
 return ForAll(pos,u->ForAll(neg,v->g.adj[u][v]));
end;
Mask:=function(f) return Sum(f,i->2^(i-1));end;
TauMask:=function(mask,n) return (mask mod 2^n)*2^n+QuoInt(mask,2^n);end;
positive:=0;negative:=0;localassignments:=0;compiled:=0;
Run:=function(name,g,c,expect,compile)
 local faces,masks,dicts,j,f,d,row,boundary,rhs,i,pos,sol,chains,failed,n,bits,
       q,verts,assignment,labels,code,u,sign,delta,bad,ones,zeros,S,globalbits,coeff,idx,states;
 n:=g.n;faces:=[];masks:=[];dicts:=[];chains:=[];failed:=0;
 for j in [0..c] do
  Check(Binomial(2*n,j+1)<=7500,"face-enumeration sizing");
  f:=Filtered(Combinations([1..2*n],j+1),x->Face(g,x));Add(faces,f);Add(masks,List(f,Mask));
  d:=NewDictionary(0,true);for i in [1..Length(f)] do AddDictionary(d,masks[j+1][i],i);od;Add(dicts,d);
 od;
 row:=List(faces[1],f->Zero(GF(2)));ConvertToVectorRep(row,2);row[LookupDictionary(dicts[1],1)]:=One(GF(2));Add(chains,row);
 for j in [1..c] do
  rhs:=ShallowCopy(chains[j]);
  for i in [1..Length(rhs)] do
   if not IsZero(chains[j][i]) then pos:=LookupDictionary(dicts[j],TauMask(masks[j][i],n));rhs[pos]:=rhs[pos]+One(GF(2));fi;
  od;
  boundary:=[];
  for f in faces[j+1] do
   row:=List(faces[j],x->Zero(GF(2)));ConvertToVectorRep(row,2);
   for u in f do pos:=LookupDictionary(dicts[j],Mask(f)-2^(u-1));row[pos]:=One(GF(2));od;Add(boundary,row);
  od;
  if Length(boundary)=0 then
   if ForAll(rhs,IsZero) then sol:=[];else sol:=fail;fi;
  else sol:=SolutionMat(boundary,rhs);fi;
  if sol=fail then failed:=j;break;fi;
  if Length(boundary)>0 then Check(sol*boundary=rhs,"exact chain boundary");fi;Add(chains,sol);
 od;
 Print(name," FACE_COUNTS=",List(faces,Length)," FAILURE_LEVEL=",failed,"\n");
 if not expect then Check(failed=c,"negative chain obstruction");negative:=negative+1;return;fi;
 Check(failed=0,"positive chain existence");positive:=positive+1;
 bits:=LogInt(c-1,2)+1;
 if compile then
  Check(bits*n<=10,"explicit polynomial compilation sizing");coeff:=BlistList([1..2^(bits*n)],[]);
 fi;
 for j in [1..c] do for idx in [1..Length(faces[j+1])] do
  if not IsZero(chains[j+1][idx]) then
   f:=faces[j+1][idx];verts:=Set(List(f,i->((i-1) mod n)+1));
   globalbits:=Concatenation(List(verts,u->[(u-1)*bits+1..u*bits]));
   states:=2^(bits*Length(verts));Check(states<=1024,"local truth-table sizing");
   for assignment in Tuples([0,1],Length(globalbits)) do
    labels:=[];bad:=false;
    for u in f do
     pos:=Position(verts,((u-1) mod n)+1);code:=Sum([1..bits],i->2^(i-1)*assignment[(pos-1)*bits+i]);
     if code>=c then bad:=true;code:=0;fi;
     sign:=1;if u>n then sign:=-1;fi;Add(labels,sign*(code+1));
    od;
    delta:=DeltaAlt(labels);
    if not bad then bad:=ForAny(labels,a->-a in labels);fi;
    Check(delta=0 or bad,"local identity uses only domain/edge violations");localassignments:=localassignments+1;
    if compile and delta=1 then
     ones:=Sum(Filtered([1..Length(assignment)],i->assignment[i]=1),i->2^(globalbits[i]-1));
     zeros:=List(Filtered([1..Length(assignment)],i->assignment[i]=0),i->globalbits[i]);
     for S in Combinations(zeros) do pos:=ones+Sum(S,i->2^(i-1))+1;coeff[pos]:=not coeff[pos];od;
    fi;
   od;
  fi;
 od;od;
 if compile then Check(SizeBlist(coeff)=1 and coeff[1],"literal sum of multilinear local identities is one");compiled:=compiled+1;fi;
end;
Run("K3_TWO_COLOURS",Complete(3),2,true,true);
Run("C5_TWO_COLOURS",CycleGraphControl(5),2,true,true);
Run("K4_THREE_COLOURS",Complete(4),3,true,true);
Run("MYCIELSKI_C5_THREE_COLOURS",Mycielski(CycleGraphControl(5)),3,true,false);
Run("K5_FOUR_COLOURS",Complete(5),4,true,true);
Run("C5_THREE_COLOURS",CycleGraphControl(5),3,false,false);
Run("K4_FOUR_COLOURS",Complete(4),4,false,false);
Print("COCHAIN_IDENTITIES=",cochainchecks," POSITIVE_CHAINS=",positive," NEGATIVE_CHAINS=",negative," LOCAL_ASSIGNMENTS=",localassignments," LITERAL_UNIT_CERTIFICATES=",compiled,"\n");
Print("ALL TOPOLOGICAL COMPILER CONTROLS PASSED\n");
QUIT;
