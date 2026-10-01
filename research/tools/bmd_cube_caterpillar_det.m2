-- Low-contact determinant at the caterpillar point (6 October 2026; cycle bmd-20261006-j).  Tested statement: in nested
-- coordinates a_N = 0, a_i = x_1...x_(i-1), the R x R determinant D(x) = det(H_k(a_i,a_j))_(i<j, k<=R-1),
-- H_k(X,Y) = [T^k]((1+XT)(1+YT))^(-3/2), R = binom(N,2), has the form x^e * u(x) with u(0) != 0: some monomial of D
-- divides every other monomial.  Then rank A_(R-1) = R near the caterpillar point off the boundary, so the contact locus
-- K (rank A_(R+1) < R) avoids a neighbourhood of it.  Prediction from the recursive block structure: the exponent of
-- x_i is the sum over the nested levels of their lowest column indices, and the constant is a product of Toeplitz
-- minors of (1+T)^(-3/2), nonzero by the hook-content formula.  Env CUBE_NS (space-separated N values), CUBE_P (0 for QQ).
NS=apply(select(separate(" ",getenv "CUBE_NS"),s->s!=""),value); charP=value getenv "CUBE_P";
scan(NS,N->(
  R:=binomial(N,2); L:=R-1;
  S:=(if charP==0 then QQ else ZZ/charP)[x_1..x_(N-2)];
  a:=apply(N,i->if i==N-1 then 0_S else product(toList(0..i-1),j->S_j));
  b:=apply(L+1,m->sub(product(toList(0..m-1),r->(-3/2-r))/m!,S));
  H:=(X,Y,k)->sum(toList(0..k),m->b#m*b#(k-m)*X^m*Y^(k-m));
  pl:=flatten apply(N,i->apply(toList(i+1..N-1),j->(i,j)));
  A:=matrix apply(pl,pr->apply(L+1,k->H(a#(pr#0),a#(pr#1),k)));
  t0:=cpuTime();
  D:=det A;
  mons:=apply(terms D,leadMonomial);
  expos:=apply(mons,m->first exponents m);
  minE:=apply(N-2,i->min apply(expos,e->e#i));
  divides:=any(expos,e->e==minE);
  << "N=" << N << " R=" << R << " det terms " << #mons << ", cpu " << cpuTime()-t0 << endl;
  << "  componentwise minimal exponent " << minE << "; attained by a monomial of D: " << divides << endl;
  if divides then << "  constant u(0) = coefficient of x^" << minE << ": " << coefficient(product(N-2,i->S_i^(minE#i)),D) << endl;
  << "MONOMIAL_TIMES_UNIT N=" << N << ": " << divides << endl << flush;
));
exit 0;
