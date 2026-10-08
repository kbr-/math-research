# Exact verification of the single-domain Boolean counterexample constructed
# from the first exhaustive average failure. No additional search or scaling.
F:=GF(2);; extField:=GF(2^13);; z:=Z(2^13);;
bits:=List([1..7],y->List([0..2],i->QuoInt(y,2^i) mod 2));;
base:=List([97,82,52],m->List([0..6],i->(QuoInt(m,2^i) mod 2)*One(F)));;
perm:=List(bits,b->b[3]+2*((b[1]+b[3]) mod 2)+4*b[2]);;
if Order(PermList(perm))<>7 then Error("Singer cycle"); fi;
values:=List(bits,b->b[1]*One(extField)+b[2]*z+b[3]*z^4);;
blocks:=[];; permutation:=[1..7];;
for j in [0..6] do
 Add(blocks,List(base,row->row{permutation}));
 permutation:=List(permutation,i->perm[i]);
od;
joint:=NullMat(21,49,F);;
for j in [1..7] do
 for i in [1..3] do joint[3*(j-1)+i]{[7*(j-1)+1..7*j]}:=blocks[j][i]; od;
od;
jointValues:=Concatenation(List([1..7],j->values));;
overExt:=List(joint,row->List(row,x->Int(x)*One(extField)));;
multiplied:=List(overExt,row->List([1..49],j->row[j]*jointValues[j]));;
escape:=RankMat(Concatenation(overExt,multiplied))-RankMat(overExt);;
localGains:=List(blocks,B->List(bits,a->3-RankMat(List(B,row->row{Filtered([1..7],y->Sum([1..3],i->a[i]*bits[y][i]) mod 2=0)}))));;
jointGains:=List([1..7],a->Sum(localGains,g->g[a]));;
actualRanks:=List(bits,a->RankMat(List(joint,row->List([1..49],j->row[j]*(1-Sum([1..3],i->a[i]*bits[((j-1) mod 7)+1][i]))))));;
if RankMat(joint)<>21 or escape<>14 or jointGains<>List([1..7],i->3)
 or actualRanks<>List([1..7],i->18) then Error("counterexample failed"); fi;
if not ForAll(localGains,g->Maximum(g)=1 and Sum(g)=3) then Error("local control"); fi;
Print("base=",base,"\nSinger permutation=",perm,"\nlocal gains=",localGains,
 "\nrank U=",RankMat(joint)," generic escape=",escape,
 "\njoint gains=",jointGains," actual residual ranks=",actualRanks,
 "\nzero row residual rank=21; independently chosen block rows residual rank=14\n",
 "proposed residual upper bound=35/2; actual best=18; REFUTED\n");
QUIT;
