\\ Exact torsion function and three RR frames for the four-pair n9 boundary.
default(parisizemax,2500000000);
default(nbthreads,1);
o=Mod(1,13);assert(ok,msg)=if(!ok,print("FAIL ",msg);quit(1));
sl=[o,2*o,3*o,4*o];ell=vector(4,i,o+sl[i]*T);
roots=vector(4,i,sqrt(ell[i]+O(T^769))); subs=vector(16,mask,prod(i=1,4,if(bittest(mask-1,i-1),roots[i],o)));
for(i=1,4,assert(valuation(roots[i]^2-ell[i],T)>=769,"root-square identity"));
basis(M)={my(b=List());for(mask=0,15,for(j=0,(M-hammingweight(mask))\2,listput(b,[mask,j])));return(Vec(b));};
jetmatrix(b,N)=matrix(N,#b,i,j,if(i-1<b[j][2],0*o,polcoef(subs[b[j][1]+1],i-1-b[j][2],T)));
cochains(b,K)=vector(matsize(K)[2],j,vector(16,mask,sum(i=1,#b,if(b[i][1]==mask-1,K[i,j]*T^b[i][2],0*o))));
{my(b=basis(96),J=jetmatrix(b,768),K=matker(J));assert(matsize(K)[2]==1,"degree-zero torsion kernel dimension");
phi=cochains(b,K)[1];assert(J*K==0,"torsion kernel all jets");
assert(sum(i=1,#b,K[i,1]*polcoef(subs[b[i][1]+1],768-b[i][2],T))!=0,"exact torsion order");
print("TORSION source=",#b," zero_order=768 dimension=1 pole_bound=96");}
out="research/results/bmd-nine-thirteen-period-20261008/paired-data-second.gp";
write(out,"sl=",sl,";phi=",phi,";");
{for(d=3,5,my(M=32*d-72,N=256*d-768,b=basis(M),K=if(N==0,matid(#b)*o,matker(jetmatrix(b,N))),co=cochains(b,K));
assert(#co==188,"RR frame dimension");if(N>0,assert(jetmatrix(b,N)*K==0,"all RR marked jets"));
write(out,"base",d,"=",co,";");print("FRAME degree=",d," pole=",M," jets=",N," columns=188");)}
print("COMPLETE exact torsion divisor and all three 188-dimensional RR frames.");
