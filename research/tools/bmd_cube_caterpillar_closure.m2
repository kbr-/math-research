-- Does the closure of the contact locus K contain the caterpillar point of M_(0,N+1)? (6 October 2026; cycle
-- bmd-20261006-j.)  Setting of lem:cube-contact-plane-criterion: R = binom(N,2), H_k(X,Y) = [T^k]((1+XT)(1+YT))^(-3/2),
-- A(a) = (H_k(a_i,a_j))_(i<j, k<=R+1), K = {a separated : rank A < R}.  Nested coordinates at the caterpillar point
-- (lem:cube-geometric-cone-collapse): a_N = 0, a_i = x_1...x_(i-1) (a_1 = 1), the point being x = 0.  The closure of K
-- in the chart is V(I : (x_1...x_(N-2))^infinity), I the ideal of maximal minors; the caterpillar point lies in it iff
-- that saturation plus (x_1, ..., x_(N-2)) is a proper ideal.  Env CUBE_N, CUBE_P (0 for QQ).
N=value getenv "CUBE_N"; charP=value getenv "CUBE_P";
R=binomial(N,2); L=R+1;
S=(if charP==0 then QQ else ZZ/charP)[x_1..x_(N-2)];
a=apply(N,i->if i==N-1 then 0_S else product(toList(0..i-1),j->x_(j+1)));
b=apply(L+1,m->sub(product(toList(0..m-1),r->(-3/2-r))/m!,S));
H=(X,Y,k)->sum(toList(0..k),m->b#m*b#(k-m)*X^m*Y^(k-m));
pairList=flatten apply(N,i->apply(toList(i+1..N-1),j->(i,j)));
A=matrix apply(pairList,pr->apply(L+1,k->H(a#(pr#0),a#(pr#1),k)));
<< "N=" << N << " R=" << R << " matrix " << numrows A << "x" << numcols A << endl << flush;
t0=cpuTime();
I=minors(R,A);
<< "minors computed: " << numgens I << " generators, cpu " << cpuTime()-t0 << endl << flush;
J=saturate(I,product(toList(1..N-2),i->x_i));
<< "saturated, cpu " << cpuTime()-t0 << "; codim of closure of K in the chart: " << codim J << endl << flush;
M=ideal apply(N-2,i->x_(i+1));
<< "CATERPILLAR_IN_CLOSURE=" << (J+M != ideal 1_S) << endl;
exit 0;
