# Independent GAP polynomial construction and verification of every character's bounded jets.
Read("research/results/bmd-exception-cubic-obstruction-20261008/characters.g");
original:=WITT_CHARACTERS;;
Read("research/results/bmd-exception-cubic-obstruction-20261008/characters8.g");
f:=GF(27);;one:=One(f);;zero:=Zero(f);;x:=Indeterminate(f,"x");;a:=RootsOfPolynomial(f,x^3-x-one)[1];;
decode:=c->(c mod 3)*one+(QuoInt(c,3) mod 3)*a+QuoInt(c,9)*a^2;;
inum:=IndeterminateNumberOfUnivariateRationalFunction(x);;
poly:=v->UnivariatePolynomialByCoefficients(FamilyObj(one),v,inum);;
cut:=function(p,n) local c;c:=CoefficientsOfUnivariatePolynomial(p);if Length(c)>n then c:=c{[1..n]};fi;return poly(c);end;;
cf:=function(p,n) local c;if n<0 then return zero;fi;c:=CoefficientsOfUnivariatePolynomial(p);if n<Length(c) then return c[n+1];fi;return zero;end;;
proj:=function(p,d,g) return Sum([1..g],j->cf(p,d-j)*x^(4-j));end;;
vec:=function(p,g) return List([1..g],j->cf(p,4-j));end;;
fromvec:=v->Sum([1..Length(v)],j->v[j]*x^(4-j));;
pairmul:=function(u,v,P) return [u[1]*v[1]+P*u[2]*v[2],u[1]*v[2]+u[2]*v[1]];end;;
initial3:=function(P,g,q,inv)
 local A,H,pos,neg,carry,h;
 A:=[one*x^0/(2*one),cut(inv,3*q)/(2*one)];
 h:=Sum([1..Minimum(g,q)],j->cf(A[2],q-j)*x^(q-j));
 H:=[zero*x^0,h];pos:=[zero*x^0,A[2]-cut(A[2],q)];neg:=A-H-pos;
 carry:=pairmul(pairmul(pos+H,H+neg,P),pos+neg,P);
 return [proj(A[2],q,g),proj(-A[2],2*q,g),proj(carry[2],3*q,g)];
end;;
initial8:=function(P,g,q)
 local Q,inv,u,v,r,m;
 Q:=9;while Q<8*q do Q:=3*Q;od;
 inv:=cut(P^QuoInt(Q-1,2),8*q);
 u:=initial3(P,g,q,inv);v:=initial3(P,g,2*q,inv);r:=List([1..8],i->zero*x^0);
 r[1]:=u[1];r[2]:=-v[1];r[3]:=u[3];r[6]:=-v[3]-proj(inv/(2*one),6*q,g);
 for m in [4,5,7,8] do r[m]:=proj(inv/(2*m*one),m*q,g);od;
 return r;
end;;
step3:=function(v,P,g)
 local raw,h,pos,neg,carry;
 raw:=P*v[1]^3;h:=proj(raw,12,g)*x^8;pos:=raw-cut(raw,12);neg:=raw-h-pos;
 carry:=P*(pos+h)*(h+neg)*(pos+neg);
 return [proj(raw,12,g),proj(P*v[2]^3,12,g),proj(P*v[3]^3,12,g)+proj(carry,36,g)];
end;;
three:=function(v,P,g) local j;for j in [1..3] do v:=step3(v,P,g);od;return v;end;;
step8:=function(v,P,g)
 local u,w,r,m;u:=step3([v[1],zero*x^0,v[3]],P,g);w:=step3([v[2],zero*x^0,v[6]],P,g);
 r:=List([1..8],i->zero*x^0);r[1]:=u[1];r[3]:=u[3];r[2]:=w[1];r[6]:=w[3];
 for m in [4,5,7,8] do r[m]:=proj(P*v[m]^3,12,g);od;return r;
end;;
monolist:=function(g) local r,i,j,k;r:=[];for i in [1..g] do for j in [i..g] do for k in [j..g] do Add(r,[i,j,k]);od;od;od;return r;end;;
mono:=function(v,ls) return List(ls,t->v[t[1]]*v[t[2]]*v[t[3]]);end;;
powvec:=function(powers,n,v) local j;j:=1;while n>0 do if n mod 2=1 then v:=powers[j]*v;fi;n:=QuoInt(n,2);j:=j+1;od;return v;end;;
fast3:=function(init,s,P,g,monos,dp,lp)
 local k,m,z,v,u,j;k:=QuoInt(s,3);m:=Length(monos);z:=powvec(dp,k,vec(init[1],g));
 v:=powvec(lp,k,Concatenation(mono(vec(init[1],g),monos),vec(init[3],g)));
 if v{[1..m]}<>mono(z,monos) then Error("complete symmetric-cube state");fi;
 u:=[fromvec(z),zero*x^0,fromvec(v{[m+1..m+g]})];for j in [1..s mod 3] do u:=step3(u,P,g);od;return u;
end;;
exponential:=Sum([0..8],j->JET8_E[j+1]*one*x^j);;
for u in Elements(f) do for v in Elements(f) do
 if cut(Value(exponential,u*x)*Value(exponential,v*x)-Value(exponential,(u+v)*x)*Value(exponential,(-u*v*(u+v))*x^3),9)<>zero*x^0 then Error("exhaustive Witt addition law");fi;
od;od;
for ci in [1..466] do
 row:=original[ci];S:=row[1];P:=poly(List(row[2],decode));g:=Length(row[3]);D:=List(row[3],r->List(r,decode));L:=List(row[4],r->List(r,decode));monos:=monolist(g);m:=Length(monos);;
 if D^2*D^4680<>D^2 or L^2*L^4680<>L^2 then Error("whole-state period");fi;
 for point in Tuples([zero,one,2*one],g) do
  st:=three([fromvec(point),zero*x^0,zero*x^0],P,g);want:=L*Concatenation(mono(point,monos),List([1..g],i->zero));;
  if vec(st[1],g)<>D*point or vec(st[3],g)<>want{[m+1..m+g]} or want{[1..m]}<>mono(D*point,monos) then Error("exhaustive homogeneous-cubic interpolation");fi;
 od;
 point:=List([1..g],i->a^i+(i mod 3)*one);v:=List([1..g],i->a^(2*i)+one);;
 st:=three([fromvec(point),zero*x^0,fromvec(v)],P,g);want:=L*Concatenation(mono(point,monos),v);;
 if vec(st[1],g)<>D*point or vec(st[3],g)<>want{[m+1..m+g]} then Error("nonprime-field acceleration");fi;
 init:=initial8(P,g,1);dp:=[D];lp:=[L];for j in [2..14] do dp[j]:=dp[j-1]^2;lp[j]:=lp[j-1]^2;od;
 if S in [7,31,83,127,511] then st:=init;for s in [1..3] do st:=step8(st,P,g);if st<>initial8(P,g,3^s) then Error("direct Abel order-eight coordinates");fi;od;fi;
 for si in [1..30] do
  s:=WITT_EXPONENTS[si];u:=fast3([init[1],zero*x^0,init[3]],s,P,g,monos,dp,lp);v:=fast3([init[2],zero*x^0,init[6]],s,P,g,monos,dp,lp);st:=List([1..8],i->zero*x^0);;
  st[1]:=u[1];st[3]:=u[3];st[2]:=v[1];st[6]:=v[3];
  for idx in [4,5,7,8] do z:=fromvec(powvec(dp,QuoInt(s,3),vec(init[idx],g)));for j in [1..s mod 3] do z:=proj(P*z^3,12,g);od;st[idx]:=z;od;
  if List(st,p->vec(p,g))<>List(JET8_CHARACTERS[ci][2][si],r->List(r,decode)) then Error("all eight actual character coordinates");fi;
 od;
 if ci mod 50=0 then Print("GAP_WITT_CHARACTERS checked=",ci,"\n");fi;
od;
Print("GAP_WITT_CHARACTERS_COMPLETED characters466 states13980 coordinates8 exhaustive_addition729=true period14040=true\n");
QUIT;
