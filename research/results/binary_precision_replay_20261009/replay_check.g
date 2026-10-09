# Precision s=3, modulo8: all64 degree<=2 ordinary binary polynomials in x,y.
# Shared nonlinear interpretation x=a+b,y=ab on four old Boolean points.
# All4096 additions, sixteen legal variable multiplications, all coefficient fields.
out:=OutputTextFile("research/results/binary_precision_replay_20261009/replay-checks.txt",false);;
SetPrintFormattingStatus(out,false);;
modulus:=8;;
eta:=function(v) local j; v:=v mod modulus;for j in [1..2] do v:=(3*v^2-2*v^3) mod modulus;od;return v;end;;
cs:=Tuples([0,1],6);;
points:=Tuples([0,1],2);;
vals:=List(points,v->[1,v[1]+v[2],v[1]*v[2],(v[1]+v[2])^2,(v[1]+v[2])*v[1]*v[2],(v[1]*v[2])^2]);;
images:=List(cs,c->List(vals,v->eta(Sum([1..6],j->c[j]*v[j]))));;
ix:=c->1+Sum([1..6],j->c[j]*2^(6-j));;
addchecks:=0;;mulchecks:=0;;fieldchecks:=0;;wrongadd:=0;;bad:=0;;
for i in [1..64] do
 for j in [1..64] do
  c:=List([1..6],k->(cs[i][k]+cs[j][k]) mod 2);;
  for h in [1..4] do
   addchecks:=addchecks+1;
   if images[ix(c)][h]<>(images[i][h]+images[j][h]-2*images[i][h]*images[j][h]) mod modulus then bad:=bad+1;fi;
  od;
 od;
 for h in [1..4] do if (2*images[i][h]) mod modulus<>0 then wrongadd:=wrongadd+1;fi;od;
od;
for c in Tuples([0,1],3) do
 old:=[c[1],c[2],c[3],0,0,0];;
 prodx:=[0,c[1],0,c[2],c[3],0];;
 prody:=[0,0,c[1],0,c[2],c[3]];;
 for h in [1..4] do
  mulchecks:=mulchecks+2;
  if images[ix(prodx)][h]<>(eta(vals[h][2])*images[ix(old)][h]) mod modulus then bad:=bad+1;fi;
  if images[ix(prody)][h]<>(eta(vals[h][3])*images[ix(old)][h]) mod modulus then bad:=bad+1;fi;
 od;
od;
for h in [1..4] do
 for j in [2..3] do
 fieldchecks:=fieldchecks+1;
 if eta(vals[h][j]^2+vals[h][j])<>0 then bad:=bad+1;fi;
 od;
od;
halfchecks:=0;;lostones:=0;;
for v in Tuples([0,1],3) do
 c12:=(1-v[1])*(1-v[2]);;c23:=(1-v[2])*(1-v[3]);;
 num:=2-c12*(1+v[3])-c23*(1+v[1]);;
 target:=(1-c12)*(1-c23);;
 halfchecks:=halfchecks+1;
 if num<>2*target or ((num mod 4)/2) mod 2<>target then bad:=bad+1;fi;
 if target=1 and num mod 2=0 then lostones:=lostones+1;fi;
od;
AppendTo(out,"precision=3; modulus=8; input_polynomials=64; old_points=4\n");
AppendTo(out,"addition_checks=",addchecks,"; multiplication_checks=",mulchecks,"; field_checks=",fieldchecks,"; half_identity_checks=",halfchecks,"\n");
AppendTo(out,"ordinary_addition_failures=",wrongadd,"; premature_reduction_lost_ones=",lostones,"; violations=",bad,"\n");
if addchecks=16384 and mulchecks=64 and fieldchecks=8 and halfchecks=8 and wrongadd=128 and lostones=5 and bad=0 then AppendTo(out,"PASS\n");else AppendTo(out,"FAIL\n");fi;
CloseStream(out);
QUIT;
