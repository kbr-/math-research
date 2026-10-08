\\ Exact torsion function and three RR frames for the four-pair n9 boundary.
default(parisizemax,2500000000);
default(nbthreads,1);
a=ffgen(Mod(1,5)*(x^2+x+1),'a);o=a^0;
field=vector(25,i,o*((i-1)%5)+a*((i-1)\5));
code(z)={for(i=1,25,if(z==field[i],return(i-1)));error("field code");};
assert(ok,msg)=if(!ok,error(msg));
curve=3;
sl=[o,a,2*o+a,o+2*a]; ell=vector(4,i,o+sl[i]*T);
roots=vector(4,i,sqrt(ell[i]+O(T^1281))); subs=vector(16,mask,prod(i=1,4,if(bittest(mask-1,i-1),roots[i],o)));
for(i=1,4,assert(valuation(roots[i]^2-ell[i],T)>=1281,"root-square identity"));
basis(M)={my(b=List());for(mask=0,15,for(j=0,(M-hammingweight(mask))\2,listput(b,[mask,j])));return(Vec(b));};
jetmatrix(b,N)=matrix(N,#b,i,j,if(i-1<b[j][2],0*o,polcoef(subs[b[j][1]+1],i-1-b[j][2],T)));
cochains(b,K)=vector(matsize(K)[2],j,vector(16,mask,sum(i=1,#b,if(b[i][1]==mask-1,K[i,j]*T^b[i][2],0*o))));
{my(b=basis(160),J=jetmatrix(b,1280),K=matker(J));assert(matsize(K)[2]==1,"degree-zero torsion kernel dimension");
phi=cochains(b,K)[1];assert(J*K==0,"torsion kernel all jets");
assert(sum(i=1,#b,K[i,1]*polcoef(subs[b[i][1]+1],1280-b[i][2],T))!=0,"exact torsion order");
print("TORSION source=",#b," zero_order=1280 dimension=1 pole_bound=160");}
assert(matsize(matker(jetmatrix(basis(32),256)))[2]==0,"nontrivial five-primary torsion part");
out="research/results/bmd-nine-quinary-period-20261008/paired-data-fourth.gp";
write(out,"sl=",sl,";phi=",phi,";");
{for(d=3,7,my(M=32*d-72,N=256*d-768,b=basis(M),K=if(N==0,matid(#b)*o,matker(jetmatrix(b,N))),co=cochains(b,K));
assert(#co==188,"RR frame dimension");if(N>0,assert(jetmatrix(b,N)*K==0,"all RR marked jets"));
write(out,"base",d,"=",co,";");print("FRAME degree=",d," pole=",M," jets=",N," columns=188");)}
print("COMPLETE exact torsion divisor and all five 188-dimensional RR frames.");
