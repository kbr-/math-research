\\ Exact full tail of the residue-two-profile degeneration; no pattern assumption.
default(parisizemax,1000000000);
default(nbthreads,1);
ep='ep;b='b;T='T;
read("research/results/bmd-elliptic-second-residue-20261009/constraints.gp");
assert(c,msg)=if(!c,print("FAIL ",msg);quit(1));
tailLength=0;for(j=1,32,if(primitive[,j]!=vector(12)~,tailLength=j));
C=matrix(12,tailLength,i,j,primitive[i,j]);K=matker(C);
assert(matsize(K)[2]==tailLength-12,"full high kernel dimension");
OUT="research/results/bmd-elliptic-second-residue-20261009/kernel.gp";
write(OUT,"tailLength=",tailLength,"; K=",K,";");
print("TAIL_LENGTH ",tailLength," HIGH_DIMENSION ",matsize(K)[2]);
{for(j=1,matsize(K)[2],my(f=sum(h=0,tailLength-1,K[h+1,j]*T^(tailLength-1-h)));print("GENERATOR ",j," ",factor(f));write(OUT,"f",j,"=",f,";"));}
print("COMPLETE exact residue-two high kernel.");
quit;
