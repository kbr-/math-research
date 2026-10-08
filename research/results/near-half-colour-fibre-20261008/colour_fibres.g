# Literal characteristic-two degree certificates: all four local clauses;
# every root-normalized first-bit branch of K5 and K2 joined with C5.
# GF2/GF4, 160 branches total; no PC closure or asymptotic lower bound inferred.
Check:=function(ok,msg) if not ok then Error(msg);fi;end;;
Deg:=function(p)
 local e,i,d;
 if IsZero(p) then return 0;fi;
 e:=ExtRepPolynomialRatFun(p);d:=0;
 for i in [1,3..Length(e)-1] do d:=Maximum(d,Sum(e[i]{[2,4..Length(e[i])]}));od;
 return d;
end;;
Lit:=function(x,a) if a=0 then return One(x)+x;else return x;fi;end;;
localids:=0;;branches:=0;;corrections:=0;;negative:=0;;
Print("Planned GF2/GF4; local four-colour certificates and 16+64 branches per field; no larger series\n");
for fld in [GF(2),GF(4)] do
 R:=PolynomialRing(fld,4);x:=IndeterminatesOfPolynomialRing(R);o:=One(R);
 eu:=o+x[1]+x[3];ev:=o+x[2]+x[4];q:=eu*ev;sumclauses:=Zero(R);
 for a in [0,1] do for b in [0,1] do
  au:=Lit(x[1],a)*Lit(x[3],a);av:=Lit(x[2],b)*Lit(x[4],b);
  bu:=x[1]^2+x[1];bv:=x[2]^2+x[2];clause:=au*av;
  terms:=[Lit(x[1],a)*Lit(x[2],b)*q,bu*av,bv*au,bu*bv];
  Check(IsZero(Sum(terms)-clause),"literal reverse clause");
  Check(Maximum(List(terms,Deg))<=4,"local degree");
  sumclauses:=sumclauses+clause;localids:=localids+1;
 od;od;
 Check(IsZero(sumclauses-q),"sum to quadratic");localids:=localids+1;
 for n in [5,7] do
  if n=5 then edges:=Combinations([1..5],2);
  else edges:=Concatenation(List([1..4],i->[i,i+1]),[[1,5],[6,7]],List([1..5],i->[i,6]),List([1..5],i->[i,7]));fi;
  cycles:=Filtered(Combinations([1..n],3),c->ForAll(Combinations(c,2),e->e in edges));
  if n=7 then Add(cycles,[1..5]);fi;
  R:=PolynomialRing(fld,2*n-1);x:=IndeterminatesOfPolynomialRing(R);o:=One(R);
  us:=Concatenation(x{[1..n-1]},[Zero(R)]);vs:=x{[n..2*n-1]};
  alphas:=Tuples([0,1],n-1);Check(Length(alphas)<=64,"sizing gate");total:=Zero(R);peak:=0;
  for init in alphas do
   alpha:=Concatenation(init,[0]);
   cyc:=First(cycles,c->ForAll(c,i->alpha[i]=alpha[c[1]]));
   Check(cyc<>fail,"inconsistent fibre needs odd cycle");
   delta:=Product([1..n-1],i->Lit(us[i],alpha[i]));total:=total+delta;
   terms:=[];
   for j in [1..Length(cyc)] do
    a:=cyc[j];b:=cyc[(j mod Length(cyc))+1];
    eu:=o+us[a]+us[b];ev:=o+vs[a]+vs[b];
    corr:=Zero(R);
    for i in [a,b] do
     if i=n then continue;fi;
     other:=Product(Filtered([1..n-1],h->h<>i),h->Lit(us[h],alpha[h]));
     cc:=(us[i]^2+us[i])*other*ev;
     Check(IsZero(delta*(us[i]+alpha[i]*o)*ev-cc),"weighted Boolean correction");
     Check(Deg(cc)<=n+1,"correction ceiling");corr:=corr+cc;corrections:=corrections+1;
    od;
    weighted:=delta*eu*ev;
    Check(IsZero(weighted+corr-delta*ev),"weighted residual equation");
    peak:=Maximum(peak,Deg(weighted));Check(peak<=n+1,"weighted axiom ceiling");
    Add(terms,delta*ev);
   od;
   Check(IsZero(Sum(terms)-delta),"odd cycle branch sum");
   Check(not IsZero(Sum(terms)-terms[1]-delta),"omitted cycle edge negative control");negative:=negative+1;
   branches:=branches+1;
  od;
  Check(IsZero(total-o),"root-normalized partition");
  Print("field=",fld," graph N=",n," branches=",Length(alphas)," max weighted degree=",peak," PASS\n");
 od;
od;
# K4 is colourable: the root-normalized first-bit partition 1100 has only edges,
# and second-bit choices 0101 properly colour both parts. This rejects a mass
# obstruction without the non-four-colourability hypothesis.
alpha:=[1,1,0,0];beta:=[0,1,0,1];
Check(ForAll(Combinations([1..4],2),e->alpha[e[1]]<>alpha[e[2]] or beta[e[1]]<>beta[e[2]]),"K4 positive control");negative:=negative+1;
Print("TOTAL local identities=",localids," branches=",branches," weighted Boolean corrections=",corrections," negative/positive controls=",negative,"\nALL COLOUR FIBRE CHECKS PASSED\n");
QUIT;
