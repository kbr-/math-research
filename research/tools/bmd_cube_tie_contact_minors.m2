-- Contact-level minors at a tie root (6 October 2026; cycle bmd-20261006-m).  Setting of
-- research/tools/bmd_cube_tie_fcurve.m2: a_j = eps^j (2 <= j <= N-1), a_N = 0, a_1 = c eps^i.  At a root c0 of the
-- low-contact leading coefficient L_i(c) (reduced modulo a prime p where it has a root), compute the eps-valuation of
-- every R x R minor of A_(R+1) (columns 0..R+1) at c = c0 and at a random control value of c.  A minor whose valuation
-- does not increase at c0 has a nonzero leading coefficient there.  The low-column minor (columns 0..R-1) must increase
-- (control).  Env CUBE_N, CUBE_I, CUBE_P, CUBE_C0 (space-separated roots), CUBE_CRAND.
N=value getenv "CUBE_N"; tieLevel=value getenv "CUBE_I"; charP=value getenv "CUBE_P";
c0s=apply(select(separate(" ",getenv "CUBE_C0"),s->s!=""),value); crand=value getenv "CUBE_CRAND";
R=binomial(N,2); L=R+1;
S=(ZZ/charP)[symbol e]; e=S_0;
b=apply(L+1,m->sub(product(toList(0..m-1),r->(-3/2-r))/m!,S));
H=(X,Y,k)->sum(toList(0..k),m->b#m*b#(k-m)*X^m*Y^(k-m));
val=f->if f==0 then infinity else min apply(terms f,t->first degree t);
minorVals=cc->(
  a:=prepend(cc*e^tieLevel,append(apply(toList(2..N-1),j->e^j),0_S));
  pl:=flatten apply(N,j->apply(toList(j+1..N-1),l->(j,l)));
  A:=matrix apply(pl,pr->apply(L+1,k->H(a#(pr#0),a#(pr#1),k)));
  hashTable apply(subsets(L+1,R),cols->(cols,val det A_cols)));
<< "N=" << N << " tie level " << tieLevel << " p=" << charP << " R=" << R << ": " << binomial(L+1,R) << " minors" << endl << flush;
V0=minorVals(crand*1_S);
low=toList(0..R-1);
<< "control c=" << crand << ": low-column minor valuation " << V0#low << ", minimal valuation over all minors " << min values V0 << endl << flush;
scan(c0s,c0->(
  V:=minorVals(c0*1_S);
  same:=select(keys V,k->V#k==V0#k);
  << "c0=" << c0 << ": low-column minor valuation " << V#low << " (control " << V0#low << "); minors with unchanged valuation: " << #same
     << " of " << #(keys V) << "; minimal valuation " << min values V << " (control " << min values V0 << ")" << endl;
  if #same>0 then << "  e.g. columns dropped: " << toString apply(take(sort same,3),k->toList(set toList(0..L)-set k)) << " valuation " << V#(first sort same) << endl;
  << "CONTACT_LEVEL_NONZERO c0=" << c0 << ": " << (#same>0) << endl << flush;
));
exit 0;
