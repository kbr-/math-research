-- Low-contact determinant along F-curves with one tie (6 October 2026; cycle bmd-20261006-k).  Tested statement: for
-- the roots a_j = eps^j (2 <= j <= N-1), a_N = 0, a_1 = c eps^i (a_1 tied with a_i at scale eps^i, 2 <= i <= N-1), the
-- determinant D = det(H_k(a_j,a_l))_(j<l, k<=R-1), H_k(X,Y) = [T^k]((1+XT)(1+YT))^(-3/2), R = binom(N,2), has lowest
-- eps-coefficient L_i(c) with no root c in k^* off c = 1 (where a_1 and a_i collide).  Then the generic, and every
-- non-colliding, point of the corresponding F-curve (parts: the upper chain with infinity, {a_i}, {a_1}, the lower
-- cluster) lies outside the closure of the codimension-one locus rank A_(R-1) < R, hence outside the closure of the
-- contact locus K.  Env CUBE_NS (space-separated N values).
NS=apply(select(separate(" ",getenv "CUBE_NS"),s->s!=""),value);
scan(NS,N->(
  R:=binomial(N,2); L:=R-1;
  S:=QQ[symbol c, symbol e]; c:=S_0; e:=S_1;
  b:=apply(L+1,m->product(toList(0..m-1),r->(-3/2-r))/m!);
  H:=(X,Y,k)->sum(toList(0..k),m->b#m*b#(k-m)*X^m*Y^(k-m));
  for i from 2 to N-1 do (
    a:=prepend(c*e^i,append(apply(toList(2..N-1),j->e^j),0_S));
    pl:=flatten apply(N,j->apply(toList(j+1..N-1),l->(j,l)));
    A:=matrix apply(pl,pr->apply(L+1,k->H(a#(pr#0),a#(pr#1),k)));
    D:=det A;
    v:=min apply(terms D,t->(degree(e,t)));
    Li:=sum select(terms D,t->degree(e,t)==v);
    Lc:=sub(Li//e^v,{e=>1});
    << "N=" << N << " tie level i=" << i << ": lowest eps-power " << v << ", L_i(c) factors: " << toString factor Lc << endl << flush;
  );
));
exit 0;
