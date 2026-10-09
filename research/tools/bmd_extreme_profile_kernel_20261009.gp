\\ Extract exact high-source generators from the full primitive constraint matrix.
default(parisizemax,1000000000);
default(nbthreads,1);
ep='ep;b='b;T='T;
read("research/results/bmd-elliptic-extreme-profile-20261009/constraints.gp");
assert(c,msg)=if(!c,print("FAIL ",msg);quit(1));
assert(primitive[,17..32]==matrix(14,16),"all columns below the sixteen-column tail are free");
K=matker(primitive[,1..16]);assert(matsize(K)==[16,2],"exactly two high directions survive");
OUT="research/results/bmd-elliptic-extreme-profile-20261009/kernel.gp";
write(OUT,"K=",K,";");
{for(j=1,2,my(f=sum(h=0,15,K[h+1,j]*T^(15-h)));print("GENERATOR ",j," ",factor(f));write(OUT,"f",j,"=",f,";"));}
print("COMPLETE exact two-dimensional kernel and full tail support.");
quit;
