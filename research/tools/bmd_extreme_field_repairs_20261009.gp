\\ Resolve the rational elimination denominators at 43 and 257 on the full source matrix.
default(parisizemax,1000000000);
default(nbthreads,1);
ep='ep;b='b;T='T;
assert(c,msg)=if(!c,print("FAIL ",msg);quit(1));
read("research/results/bmd-elliptic-extreme-profile-20261009/second-constraints.gp");
OUT="research/results/bmd-elliptic-extreme-profile-20261009/field-repairs.gp";
{for(z=1,2,my(p=[43,257][z],S=Mod(1,p)*R,depth=vector(10),steps=0);while(1,for(i=1,10,my(v=vecmin(vector(32,j,valuation(S[i,j],ep))));assert(v<64,"nonzero row");if(v>0,S[i,]/=ep^v;depth[i]+=v));my(C=matrix(10,32,i,j,polcoef(S[i,j],0,ep)),K=matker(C~));if(matsize(K)[2]==0,break);my(v=K[,1],ri=0,d=0);for(i=1,10,if(v[i]!=0,ri=i;d=max(d,depth[i])));v/=v[ri];S[ri,]=sum(i=1,10,v[i]*S[i,]);depth[ri]=d;steps++;assert(steps<=410,"minor degree bound"));my(C=matrix(10,32,i,j,polcoef(S[i,j],0,ep)),K=matrix(14,4,i,j,if(13-(i-1)==j,1,0)));assert(vecmax(depth)<32,"all omitted columns still vanish");assert(matrank(C)==10&&C[,1..14]*K==matrix(10,4)&&C[,15..32]==matrix(10,18),"same complete four-direction kernel");write(OUT,"field",p,"=",C,"; depth",p,"=",depth,";");print("REPAIRED field=",p," steps=",steps," pole_depth=",vecmax(depth)," same_full_source=true"));}
\\ Independent rational-endpoint jet test: Frobenius gaps preserve the last eight jets.
{for(z=1,3,my(p=[23,43,257][z],s=p,N=8*s+8,M=matrix(8,8,i,j,sum(k=0,2,binomial(2,k)*binomial(4*s,4*s+i-j-k)*2^(j+k-i)))*Mod(1,p));assert(M==matrix(8,8,i,j,if(i-j>=0&&i-j<=2,Mod(binomial(2,i-j),p),Mod(0,p))),"all retained high jets equal the unit triangular endpoint");assert(matdet(M)==1,"actual endpoint determinant"));}
print("COMPLETE both excluded-prime repairs and three independent rational-endpoint controls.");
quit;
