# Nontrivial small control of the no-four-cycle neighborhood collapse.
Check:=function(ok,msg) if not ok then Error(msg);fi;end;
MemberBit:=function(e,i) if i in e then return One(GF(2));fi;return Zero(GF(2));end;
verts:=Combinations([1..5],2);n:=Length(verts);
adj:=List([1..n],i->Filtered([1..n],j->Intersection(verts[i],verts[j])=[]));
facets:=Set(adj);Check(ForAll(Combinations(facets,2),p->Length(Intersection(p[1],p[2]))<=1),"no four-cycle overlap");
complex:=Union(List(facets,Combinations));original:=ShallowCopy(complex);collapses:=0;
for facet in facets do
 centre:=facet[1];base:=Difference(facet,[centre]);subs:=Filtered(Combinations(base),s->Length(s)>=2);
 Sort(subs,function(a,b)return Length(a)>Length(b);end);
 for s in subs do
  target:=Union(s,[centre]);cofaces:=Filtered(complex,f->f<>s and IsSubset(f,s));
  Check(cofaces=[target],"elementary collapse free face");RemoveSet(complex,s);RemoveSet(complex,target);collapses:=collapses+1;
 od;
od;
Check(ForAll(complex,f->Length(f)<=2),"remaining complex is a graph");
Check(Filtered(complex,f->Length(f)=1)=List([1..n],i->[i]),"all vertices retained");
edges:=Filtered(complex,f->Length(f)=2);boundary:=List(edges,e->List([1..n],i->MemberBit(e,i)));
Check(Length(edges)=20 and RankMat(boundary)=9,"collapsed graph ranks");
Print("PETERSEN_VERTICES=10 ORIGINAL_COUNTS=",List([0..2],d->Number(original,f->Length(f)=d+1))," COLLAPSES=",collapses," FINAL_EDGES=",Length(edges)," H1_DIMENSION=",Length(edges)-RankMat(boundary),"\n");
Print("ALL NEIGHBORHOOD COLLAPSE CONTROLS PASSED\n");
QUIT;
