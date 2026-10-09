# Exact validation of the new characteristic-two middle-matrix rule.
# Odd row n=2s+1, nonzero modular coefficients, all targets:
# if c=2b-sum(a) !=0 and z^c+z^-c != sum_i(z^ai+z^-ai),
# evaluation through s-1 must be onto. Check normalized character top terms,
# the weighted Hodge identity T^4=sigma*T^2, congruence and actual GF(2) ranks.
# Even central rows test the sum_i(z^ai+z^-ai) !=0 corollary.
# Signed/permutation orbits: sorted coefficient multisets in 1..(q-1)/2.
# All arithmetic/ranks use native GAP finite fields, not floating point.
RunChecks := function()
local out, F, zero, one, q, h, E, zeta, n, s, d, pts, ones, mons, evals,
 a, sets, eta, etaInv, w, roots, prodEta, prodRoot, sig, T, T2, N, i,j,
 left, right, missing, b, A, gamma, alpha, beta, M, scaled, ident, ids,
 vals, rk, c, predicted, expected, col, topPlus, topMinus, normPlus,
 normMinus, Pleft, PleftInv, row, countRows, countPred, countNonempty,
 countTop, countCentral, countCentralNonempty, countSingular, coeffSets,
 evenK, centralB, centralSig, mat, weights, maxMatrix, inv2;
 out := "research/results/near-half-central-slice-filtration-20261009/middle_matrix_output.txt";
 PrintTo(out,"Exact weighted middle-matrix validation.\n");
 F:=GF(2); zero:=Zero(F); one:=One(F);
 countRows:=0; countPred:=0; countNonempty:=0; countTop:=0;
 countCentral:=0; countCentralNonempty:=0; countSingular:=0; maxMatrix:=0;
 for q in [3,5,7] do
  h:=OrderMod(2,q); E:=GF(2^h); zeta:=Z(2^h)^QuoInt(2^h-1,q);
  for n in [3,5,7] do
   s:=QuoInt(n-1,2); d:=s-1;
   pts:=Tuples([0,1],n); ones:=List(pts,p->Filtered([1..n],j->p[j]=1));
   mons:=Concatenation(List([0..d],j->Combinations([1..n],j)));
   evals:=List(ones,on->List(mons,function(m) if IsSubset(on,m) then return one; else return zero; fi; end));
   for row in evals do ConvertToVectorRep(row,2); od;
   sets:=Combinations([1..n],s); N:=Length(sets); maxMatrix:=Maximum(maxMatrix,N);
   # Canonical signed/permutation orbits are nondecreasing tuples.
   coeffSets:=Filtered(Tuples([1..QuoInt(q-1,2)],n),a->ForAll([1..n-1],i->a[i]<=a[i+1]));
   for a in coeffSets do
    A:=Sum(a); eta:=List(a,t->zeta^t+One(E)); etaInv:=List(a,t->zeta^(-t)+One(E));
    w:=List(a,t->zeta^t+zeta^(-t)); roots:=List(w,t->t^(2^(h-1)));
    prodEta:=Product(eta); prodRoot:=Product(roots); sig:=Sum(w);
    T:=List([1..N],i->List([1..N],j->Zero(E)));
    for i in [1..N] do for j in [1..N] do
      if IsEmpty(Intersection(sets[i],sets[j])) then
       missing:=Difference([1..n],Union(sets[i],sets[j]));
       if Length(missing)<>1 then Error("missing coordinate"); fi;
       T[i][j]:=roots[missing[1]];
      fi;
    od; od;
    ConvertToMatrixRep(T,2^h); T2:=T*T;
    if T2*T2<>sig*T2 then Error("Hodge identity"); fi;
    vals:=List(pts,p->Sum([1..n],j->a[j]*p[j]) mod q);
    for b in [0..q-1] do
     countRows:=countRows+1;
     gamma:=zeta^b+zeta^(A-b); alpha:=gamma/prodEta; beta:=alpha*prodRoot;
     c:=(2*b-A) mod q;
     if beta^2<>zeta^c+zeta^(-c) then Error("beta normalization"); fi;
     predicted:=c<>0 and beta^2<>sig;
     M:=List([1..N],i->List([1..N],j->Zero(E)));
     for i in [1..N] do
      right:=sets[i]; left:=Difference([1..n],right);
      Pleft:=Product(eta{left}); PleftInv:=Product(etaInv{left});
      for j in [1..N] do
       col:=sets[j]; topPlus:=Zero(E); topMinus:=Zero(E);
       if IsSubset(left,col) then topPlus:=Product(eta{col})/Pleft; topMinus:=Product(etaInv{col})/PleftInv; fi;
       if col=right then
        topPlus:=topPlus+zeta^b*Product(etaInv{col})/Pleft;
        topMinus:=topMinus+zeta^(-b)*Product(eta{col})/PleftInv;
       fi;
       expected:=Zero(E);
       if IsEmpty(Intersection(right,col)) then expected:=One(E); fi;
       if col=right then expected:=expected+alpha*Product(w{right}); fi;
       M[i][j]:=topPlus+topMinus;
       if M[i][j]<>expected then Error("normalized top coefficient"); fi;
       countTop:=countTop+1;
      od;
     od;
     ConvertToMatrixRep(M,2^h);
     scaled:=List([1..N],i->List([1..N],j->M[i][j]/Product(roots{sets[i]})/Product(roots{sets[j]})));
     ident:=IdentityMat(N,E);
     if scaled<>T/prodRoot+alpha*ident then Error("matrix congruence"); fi;
     ids:=Filtered([1..Length(pts)],i->vals[i]=b);
     if IsEmpty(ids) then rk:=0; else rk:=RankMat(evals{ids}); fi;
     if predicted then
      countPred:=countPred+1;
      if not IsEmpty(ids) then countNonempty:=countNonempty+1; fi;
      if RankMat(M)<>N then Error("predicted invertibility failed"); fi;
      if rk<>Length(ids) then Error("predicted interpolation failed"); fi;
     elif rk<Length(ids) then countSingular:=countSingular+1;
     fi;
     AppendTo(out,"q=",q," n=",n," a=",a," b=",b," points=",Length(ids)," rank=",rk," predicted=",predicted,"\n");
    od;
   od;
   Print("Completed q=",q," n=",n," coefficient orbits=",Length(coeffSets),"\n");
  od;
  for evenK in [4,6,8] do
   d:=QuoInt(evenK,2)-1; pts:=Tuples([0,1],evenK);
   mons:=Concatenation(List([0..d],j->Combinations([1..evenK],j)));
   ones:=List(pts,p->Filtered([1..evenK],j->p[j]=1));
   mat:=List(ones,on->List(mons,function(m) if IsSubset(on,m) then return one; else return zero; fi; end));
   for row in mat do ConvertToVectorRep(row,2); od;
   coeffSets:=Filtered(Tuples([1..QuoInt(q-1,2)],evenK),a->ForAll([1..evenK-1],i->a[i]<=a[i+1]));
   inv2:=QuoInt(q+1,2);
   for a in coeffSets do
    centralB:=(inv2*Sum(a)) mod q;
    centralSig:=Sum(a,t->zeta^t+zeta^(-t));
    ids:=Filtered([1..Length(pts)],i->(Sum([1..evenK],j->a[j]*pts[i][j])-centralB) mod q=0);
    if IsEmpty(ids) then rk:=0; else rk:=RankMat(mat{ids}); fi;
    if centralSig<>Zero(E) then
     countCentral:=countCentral+1;
     if not IsEmpty(ids) then countCentralNonempty:=countCentralNonempty+1; fi;
     if rk<>Length(ids) then Error("central interpolation prediction failed"); fi;
    fi;
    AppendTo(out,"CENTRAL q=",q," k=",evenK," a=",a," points=",Length(ids)," rank=",rk," predicted=",centralSig<>Zero(E),"\n");
   od;
  od;
 od;
 AppendTo(out,"PASS rows=",countRows," predicted=",countPred," nonempty predicted=",countNonempty," top coefficients=",countTop," failures when criterion absent=",countSingular," central predicted=",countCentral," central nonempty predicted=",countCentralNonempty," largest middle matrix=",maxMatrix,"\n");
end;
RunChecks();
QUIT;
