# Exact three-neighbour forcing, matching-pair projection and K5 unit certificate.
# All parameter-independent identities are checked over GF2/GF4. Truth controls
# cover triple overlaps 0..3 and one four-neighbour empty-list case: 21824 boundaries.
Check:=function(ok,msg) if not ok then Error(msg);fi;end;;
Deg:=function(p) local e,i,d;
 if IsZero(p) then return 0;fi;e:=ExtRepPolynomialRatFun(p);d:=0;
 for i in [1,3..Length(e)-1] do d:=Maximum(d,Sum(e[i]{[2,4..Length(e[i])]}));od;return d;
end;;
ColourTriple:=function(u,v,A) return Sum(Combinations(A,2),e->u[e[1]]*v[e[2]]+u[e[2]]*v[e[1]]);end;;
Forcing:=function(u,v,A,c)
 local T,a,b,fu,fv,termsu,termsv,i,other,o,q;
 o:=One(u[c]);T:=ColourTriple(u,v,A);a:=Sum(u{A});b:=Sum(v{A});
 fu:=T*(u[c]+a);fv:=T*(v[c]+b);termsu:=[];termsv:=[];
 for i in A do
  other:=Difference(A,[i]);q:=(o+u[c]+u[i])*(o+v[c]+v[i]);
  Add(termsu,Sum(u{other})*q);Add(termsu,(u[i]^2+u[i])*Sum(v{other}));
  Add(termsv,Sum(v{other})*q);Add(termsv,(v[i]^2+v[i])*Sum(u{other}));
 od;
 Check(IsZero(Sum(termsu)-fu) and IsZero(Sum(termsv)-fv),"forcing identities");
 Check(Maximum(List(Concatenation(termsu,termsv),Deg))<=3,"forcing original degrees");
 return rec(T:=T,a:=a,b:=b,fu:=fu,fv:=fv,termsu:=termsu,termsv:=termsv);
end;;
for F in [GF(2),GF(4)] do
 R:=PolynomialRing(F,16);x:=IndeterminatesOfPolynomialRing(R);o:=One(R);
 u:=List([1..8],i->x[2*i-1]);v:=List([1..8],i->x[2*i]);
 left:=Forcing(u,v,[1..3],7);
 for B in [[1,2,3],[1,2,4],[1,4,5],[4,5,6]] do
  right:=Forcing(u,v,B,8);T:=left.T;S:=right.T;
  U:=o+u[7]+u[8];Vv:=o+v[7]+v[8];Up:=o+left.a+right.a;Vp:=o+left.b+right.b;
  terms:=Concatenation([T*S*U*Vv],List(left.termsu,z->S*Vv*z),List(right.termsu,z->T*Vv*z),List(left.termsv,z->S*Up*z),List(right.termsv,z->T*Up*z));
  target:=T*S*Up*Vp;
  Check(IsZero(Sum(terms)-target),"literal pair projection certificate");
  Check(Maximum(List(terms,Deg))<=6,"pair original degree");
  Print("field=",F," A=[1,2,3] B=",B," literal pair terms=",Length(terms)," degree<=6 PASS\n");
  if B=[1,2,3] then
   frob:=[];
   for ij in Combinations([1..3],2) do
    for e in [ij,Reversed(ij)] do
     xx:=u[e[1]];yy:=v[e[2]];
     Add(frob,(xx^2+xx)*yy^2);Add(frob,xx*(yy^2+yy));
    od;
   od;
   Check(IsZero(Sum(frob)-T^2-T),"Boolean Frobenius certificate");
   bqs:=List(Combinations([1..3],2),e->(o+u[e[1]]+u[e[2]])*(o+v[e[1]]+v[e[2]]));
   Check(IsZero(Sum(bqs)-o-T),"triangle sum");
   full:=Concatenation(terms,frob,bqs);
   Check(IsZero(Sum(full)-o),"literal K5 unit certificate");
   Check(Maximum(List(full,Deg))<=6,"K5 degree");
   Print("K5 field=",F," certificate terms=",full,"\nK5 degree<=6 PASS\n");
  fi;
 od;
od;
# Fixed-point truth test: this is independent of field size in characteristic2.
Missing:=function(cols)
 if Length(Set(cols))<>3 then return fail;fi;
 return First([0..3],c->not c in cols);
end;;
scenarios:=[[[1,2,3],[1,2,3]],[[1,2,3],[1,2,4]],[[1,2,3],[1,4,5]],[[1,2,3],[4,5,6]],[[1,2,3,4],[5,6,7]]];
count:=0;
for scenario in scenarios do
 A:=scenario[1];B:=scenario[2];n:=Maximum(Union(A,B));
 Check(4^n<=16384,"truth sizing gate");good:=0;bad:=0;
 for col in Tuples([0..3],n) do
  L:=Difference([0..3],Set(col{A}));M:=Difference([0..3],Set(col{B}));
  extends:=ForAny(L,a->ForAny(M,b->a<>b));
  predicted:=not IsEmpty(L) and not IsEmpty(M);
  for aa in Combinations(A,3) do for bb in Combinations(B,3) do
   ma:=Missing(col{aa});mb:=Missing(col{bb});
   if ma<>fail and ma=mb then predicted:=false;fi;
  od;od;
  Check(extends=predicted,"exact matching-pair truth set");
  if extends then good:=good+1;else bad:=bad+1;fi;
  count:=count+1;
 od;
 Check(good>0 and bad>0,"nonvacuous projection control");
 Print("truth A=",A," B=",B," extendible=",good," forbidden=",bad," PASS\n");
od;
Check(count=21824,"total boundary controls");
Print("TOTAL boundaries=",count," literal pair certificates=8, K5 certificates=2\nALL COMPOSITION CONTROLS PASSED\n");
QUIT;
