\\ Replay all exact row operations, audit characteristic scope, verify simple kernels.
default(parisizemax,1000000000);
default(nbthreads,1);
ep='ep;b='b;T='T;
assert(c,msg)=if(!c,print("FAIL ",msg);quit(1));
contents(v)={my(a=Vec(numerator(v)),d=Vec(denominator(v)),den=1);for(i=1,#a,assert(type(a[i])=="t_INT"||type(a[i])=="t_FRAC","one-variable rational numerator");den=lcm(den,denominator(a[i])));for(i=1,#d,assert(type(d[i])=="t_INT"||type(d[i])=="t_FRAC","one-variable rational denominator");den=lcm(den,denominator(d[i])));[content(a*den),content(d*den)];};
{for(which=1,2,my(path=if(which==1,"constraints.gp","second-constraints.gp"));read(concat("research/results/bmd-elliptic-second-residue-20261009/",path));my(bad=1,n=matsize(R)[1],S=R);for(i=1,n,for(j=1,32,my(co=Vec(R[i,j]));for(k=1,#co,bad=lcm(bad,abs(contents(co[k])[2])))));for(z=1,#operations,my(op=operations[z],ri=op[1]);if(type(op[2])=="t_INT",S[ri,]*=ep^op[2],my(v=op[2]);assert(v[ri]==1,"row replacement coefficient one");for(i=1,n,bad=lcm(bad,abs(contents(v[i])[2])));S[ri,]=sum(i=1,n,v[i]*S[i,])));assert(matrix(n,32,i,j,polcoef(S[i,j],0,ep))==primitive,"exact full row operation replay");my(dc=contents(rankMinor));bad=lcm(bad,abs(dc[1]*dc[2]));print("AUDITED_PRIMES stage=",which," ",factor(bad)[,1]~);if(which==1,my(K=matrix(17,5,i,j,if(17-i==j+1,1,0)));assert(primitive[,1..17]*K==matrix(12,5)&&matrank(K)==5,"first five consecutive high directions");assert(primitive[,18..32]==matrix(12,15),"first complete low block"),assert(matrank(primitive[,1..4])==4&&primitive[,5..32]==matrix(4,28),"second complete consecutive source"));)}
read("research/results/bmd-elliptic-second-residue-20261009/field-audit.gp");
q=[0,0,0,1,11]~;
assert(field39227[,1..5]*q==vector(4)~&&matrank(field39227[,1..5])==4&&field39227[,6..32]==matrix(4,27),"exact exceptional rational source");
u='u;k='k;
AA=2*k^2+3*k+1;BB=2*k+2;CC=2*k*(2*k+1)*(k+1)/3;
assert(AA^2-BB*CC==(k+1)^2*(2*k+1)*(2*k+3)/3,"all-parameter two-jet identity");
endpoint=u^11*(u+2)^11*((u+1)^2+11);M=matrix(2,2,i,j,polcoef(endpoint,22+i-j,u));
assert(M==[276,2024;24,276]&&matdet(M)==27600&&Mod(matdet(M),39227)!=0,"exceptional endpoint determinant nonzero");
print("EXCEPTIONAL_ENDPOINT matrix=",M," determinant=",matdet(M));
controlCount=0;
{for(z=1,2,my(p=[5,7][z]);for(t=0,1,for(j=1,4,my(k0=[0,p-1,(p-1)/2,(p-3)/2][j],m=k0+t*p,N=2*m+2,P0=(u^2-1)^m*(u^2+k0),J=matrix(N,N,i,j,if(j<=2*m,Mod(binomial(j-1,i-1),p),Mod(polcoef(subst(P0*u^(j-2*m-1),u,1+u),i-1,u),p))),def=if(k0==p-1,2,if(j>=3,1,0)));assert(N-matrank(J)==def,"full rational source controls, including both deficient outcomes");controlCount++)));}
assert(controlCount==16,"all sixteen controls complete");
print("RATIONAL_SOURCE_CONTROLS ",controlCount," includes_corank_zero_one_two=true");
print("COMPLETE independent row replay, denominator audit and both complete kernels, general two-jet identity and exceptional endpoint.");
quit;
