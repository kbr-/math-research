# Modulo8 local ternary Fourier transfer, represented in its free rank-two ring.
# All two-edge orientations, charges, forbidden patterns and evaluation labels.
# This is an encoding control, not a small graph in the global hard window.
out:=OutputTextFile("research/results/binary_precision_replay_20261009/charged-ring-checks.txt",false);;
SetPrintFormattingStatus(out,false);;
rr:=Integers mod 8;;
oo:=One(rr);; zz:=Zero(rr);; im:=IdentityMat(2,rr);; zm:=NullMat(2,2,rr);;
zeta:=[[zz,-oo],[oo,-oo]];; inv3:=3*oo;;
ch:=e->zeta^(e mod 3);;
ind:=function(a,b) return inv3*(im+ch(b-a)+ch(a-b));end;;
checks:=0;;bad:=0;;negative:=0;;eigen:=0;;units:=0;;
for val in [zeta^3-im,zeta^2+zeta+im,3*inv3*im-im] do checks:=checks+1;if val<>zm then bad:=bad+1;fi;od;
for a in [0..2] do
 for b in [0..2] do
  checks:=checks+1;
  want:=zm;if a=b then want:=im;fi;
  if ind(a,b)<>want then bad:=bad+1;fi;
  if a=b and im+ch(b-a)+ch(a-b)<>im then negative:=negative+1;fi;
 od;
od;
pts:=Tuples([0,1,2],2);;
for signs in Tuples([-1,1],2) do
 for c in [0..2] do
  bv:=List(pts,b->ch(signs*b)-ch(c));;
  for a in pts do
   aa:=(signs*a) mod 3;;lambda:=ch(aa)-ch(c);;
   if aa<>c then
    units:=units+1;checks:=checks+1;
    linv:=ch(-c)*inv3*(ch(c-aa)-im);
    if lambda*linv<>im then bad:=bad+1;fi;
   fi;
   for j in [1..9] do
    pr:=ind(a[1],pts[j][1])*ind(a[2],pts[j][2]);;
    eigen:=eigen+1;checks:=checks+1;
    if bv[j]*pr<>lambda*pr then bad:=bad+1;fi;
   od;
  od;
 od;
od;
AppendTo(out,"modulus=8; extension_basis=1,zeta; zeta^2+zeta+1=0\n");
AppendTo(out,"checks=",checks,"; eigenidentities=",eigen,"; forbidden_units=",units,"; omitted_normalization_failures=",negative,"; violations=",bad,"\n");
if checks=1056 and eigen=972 and units=72 and negative=3 and bad=0 then AppendTo(out,"PASS\n");else AppendTo(out,"FAIL\n");fi;
CloseStream(out);
QUIT;
