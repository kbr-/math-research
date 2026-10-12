# Exhaustive finite controls for the minor-chart retraction and induced actions.
# The domain is the CONSISTENT partial rank base (AB)_[k],[k]=I_k plus Booleanity.
# It is not the inconsistent full rank base, nor a test of its PC hardness.
# Predictions: Lambda has unit rows, lands on column-support-at-most-k states,
# fixes those states, is idempotent, and satisfies Lambda M_x Lambda=Lambda M_x
# for every variable and every function (tested as exact operator rows).
# Refuted by: a changed matrix product, nonunit row, off-target output, unfixed
# target state, or unequal exact rows for an induced variable action.
# Possible because: ordinary multiplication on the image need not be the
# transported action; replacing the outer projection gives explicit failures.
# Negative control: omit the outer Lambda in Lambda M_x Lambda; detect a row
# differing from Lambda M_x on the actual full function space.
# Stages: enumerate each bounded ambient cube once; retain the partial-rank
# domain; build the operator by active pivot charts; check all action rows.
# All expected domain and target counts are computed below from finite formulas.

maF := GF(2);; maZero := Zero(maF);; maOne := One(maF);;
maChecks := 0;; maBadAction := false;;
maAssert := function(ok, label)
  maChecks := maChecks + 1;
  if not ok then Error(Concatenation("FAILED: ",label)); fi;
end;;
maToggle := function(set, value)
  if value in set then RemoveSet(set,value); else AddSet(set,value); fi;
end;;
maEncode := function(a,b)
  local vals, power, code, x;
  vals := Concatenation(Concatenation(a),Concatenation(b));
  power := 1; code := 0;
  for x in vals do
    if x = maOne then code := code+power; fi;
    power := 2*power;
  od;
  return code+1;
end;;
maBit := function(code,pos)
  return QuoInt(code-1,2^(pos-1)) mod 2;
end;;
maGauge := function(a,b,k,s)
  local n,t,m,c,x,h,i,j;
  n := Length(b); t := Difference([1..n],s);
  m := List([1..k],i->a[i]{s});
  # Called only on active p_S=1; here inverse and adjugate agree over F2.
  maAssert(DeterminantMat(m)=maOne,"active chart is invertible");
  c := List([1..k],i->a[i]{t});
  x := Inverse(m)*c; h := IdentityMat(n,maF);
  for i in [1..k] do
    for j in [1..n-k] do h[s[i]][t[j]] := x[i][j]; od;
  od;
  return [a*h,h*b];
end;;
maFixture := function(m,n,k)
  local v,ambient,bits,a,b,code,points,targets,rows,sets,s,p,out,target,
        row,expected,expectedTarget,fullRank,gl,kernel,beginChecks,i,j,u,
        composed,actual,wrong,valid,active,finalCounts;
  v := 2*m*n; ambient := 2^v;
  if ambient > 4096 then Error("Fixture exceeds its enumerated cube budget"); fi;
  Print("Fixture ",[m,n,k],": ",ambient," ambient points; ",
        Binomial(n,k)," charts; ",v," variable actions.\n");
  points := []; targets := []; rows := []; sets := Combinations([1..n],k);
  beginChecks := maChecks;
  for bits in Tuples([maZero,maOne],v) do
    a := List([1..m],i->bits{[(i-1)*n+1..i*n]});
    b := List([1..n],i->bits{[m*n+(i-1)*m+1..m*n+i*m]});
    if List([1..k],i->(a*b)[i]{[1..k]})=IdentityMat(k,maF) then
      code := maEncode(a,b); AddSet(points,code);
      active := Number([1..n],j->ForAny([1..k],i->a[i][j]=maOne));
      if active <= k then AddSet(targets,code); fi;
      row := [];
      for s in sets do
        p := DeterminantMat(List([1..k],i->a[i]{s})) *
             DeterminantMat(List(s,i->b[i]{[1..k]}));
        if p=maOne then
          out := maGauge(a,b,k,s);
          maAssert(out[1]*out[2]=a*b,"actual matrix product preserved");
          target := maEncode(out[1],out[2]);
          maToggle(row,target);
        fi;
      od;
      rows[code] := row;
    fi;
  od;
  fullRank := Product([0..k-1],i->2^n-2^i);
  gl := Product([0..k-1],i->2^k-2^i);
  kernel := 2^(k*(n-k)); # number of right inverses of a full-row-rank R
  expected := fullRank*kernel*2^(2*n*(m-k));
  expectedTarget := Binomial(n,k)*gl*kernel*2^(2*n*(m-k));
  maAssert(Length(points)=expected,"complete partial-rank domain count");
  maAssert(Length(targets)=expectedTarget,"complete support-conditioned count");
  for code in points do
    row := rows[code];
    maAssert(Length(row) mod 2=1,"unit preserved");
    maAssert(IsSubset(targets,row),"image uses only conditioned states");
    if code in targets then maAssert(row=[code],"conditioned states fixed"); fi;
    composed := [];
    for u in row do
      for target in rows[u] do maToggle(composed,target); od;
    od;
    maAssert(composed=row,"full operator idempotence");
    for j in [1..v] do
      composed := [];
      for u in row do
        if maBit(u,j)=1 then
          for target in rows[u] do maToggle(composed,target); od;
        fi;
      od;
      actual := Filtered(row,t->maBit(t,j)=1);
      maAssert(composed=actual,"Lambda M_x Lambda equals Lambda M_x");
      wrong := [];
      if maBit(code,j)=1 then wrong := row; fi;
      if wrong<>actual and not maBadAction then
        maBadAction := true;
        Print("Omitted outer projection detected: input code ",code,
              ", variable ",j,", wrong row ",wrong,", correct row ",actual,".\n");
      fi;
    od;
  od;
  Print("Complete domain=",Length(points)," (formula ",expected,
        "); conditioned states=",Length(targets)," (formula ",expectedTarget,
        "); checks=",maChecks-beginChecks,".\n");
end;;

maFixture(2,3,1);
maFixture(2,3,2);
maAssert(maBadAction,"ordinary multiplication negative control detected");
Print("PASS: ",maChecks," exact checks; all variable action rows tested.\n");
QUIT_GAP(0);
