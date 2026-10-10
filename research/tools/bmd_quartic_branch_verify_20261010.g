# Independent exterior-companion construction of every original Schur column.
# The N9 normalized polynomial has degree<=47 in B;48 distinct values verify it fully.
F:=GF(81);; one:=One(F);; zero:=Zero(F);;
QuarticPairPhi:=function(N,deg,beta)
 local r,pairs,idx,i,j,k,u,v,X,S,V,DD,term,h,cat,base,value,jj,coef,rows;
 r:=N*(N-1)/2;pairs:=[];idx:=List([1..N],i->List([1..N],j->0));
 for i in [1..N] do for j in [i+1..N] do Add(pairs,[i,j]);idx[i][j]:=Length(pairs);idx[j][i]:=-Length(pairs);od;od;
 X:=List([1..N],i->List([1..N],j->zero));
 for i in [1..N-1] do X[i][i+1]:=one;od;
 X[N][deg+1]:=one;X[N][2]:=-beta;
 S:=List([1..r],i->List([1..r],j->zero));V:=List([1..r],i->List([1..r],j->zero));
 term:=function(row,index,c)
  if index>0 then row[index]:=row[index]+c;elif index<0 then row[-index]:=row[-index]-c;fi;
 end;
 for k in [1..r] do
  u:=pairs[k][1];v:=pairs[k][2];
  for i in [1..N] do
   if X[u][i]<>zero then term(S[k],idx[i][v],X[u][i]);fi;
   if X[v][i]<>zero then term(S[k],idx[u][i],X[v][i]);fi;
   for j in [1..N] do
    if X[u][i]<>zero and X[v][j]<>zero then term(V[k],idx[i][j],X[u][i]*X[v][j]);fi;
   od;
  od;
 od;
 DD:=S*S-V;
 if S*DD<>DD*S then Error("Noncommuting pair operators");fi;
 rows:=List([1..r],i->List([1..r],j->zero));
 base:=List([1..r],i->zero);base[idx[1][2]]:=one;
 for h in [0..QuoInt(r-1,2)] do
  cat:=Binomial(2*h,h)/(h+1);value:=ShallowCopy(base);
  for jj in [0..r-1-2*h] do
   coef:=(cat*Binomial(jj+2*h,2*h) mod 3)*one;
   if coef<>zero then rows[jj+2*h+1]:=rows[jj+2*h+1]+coef*value;fi;
   value:=value*S;
  od;
  base:=base*DD;
 od;
 return DeterminantMat(rows);
end;;
for b in Elements(F){[1..3]} do
 if QuarticPairPhi(4,2,b)<>b then Error("Known N4 frame control");fi;
od;
if QuarticPairPhi(9,2,one)<>zero then Error("Quadratic relation control");fi;
vals:=Elements(F){[1..48]};;
for b in vals do
 if QuarticPairPhi(9,4,b)<>b^11-b^6 then Error("Quartic coefficient mismatch");fi;
od;
Print("EXTERIOR_COMPANION_POLYNOMIAL_PASS values=48 degree_bound=47 polynomial=B^11-B^6\n");
Print("QUARTIC_BRANCH_INDEPENDENT_COMPLETED\n");
QUIT;
