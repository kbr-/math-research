\\ Replay all exact row operations, audit characteristic scope, verify simple kernels.
default(parisizemax,1000000000);
default(nbthreads,1);
ep='ep;b='b;T='T;
assert(c,msg)=if(!c,print("FAIL ",msg);quit(1));
contents(v)={my(a=Vec(numerator(v)),d=Vec(denominator(v)),den=1);for(i=1,#a,assert(type(a[i])=="t_INT"||type(a[i])=="t_FRAC","one-variable rational numerator");den=lcm(den,denominator(a[i])));for(i=1,#d,assert(type(d[i])=="t_INT"||type(d[i])=="t_FRAC","one-variable rational denominator");den=lcm(den,denominator(d[i])));[content(a*den),content(d*den)];};
{for(which=1,2,my(path=if(which==1,"constraints.gp","second-constraints.gp"));read(concat("research/results/bmd-elliptic-adjacent-profile-20261009/",path));my(bad=1,n=matsize(R)[1],S=R);for(i=1,n,for(j=1,32,my(co=Vec(R[i,j]));for(k=1,#co,bad=lcm(bad,abs(contents(co[k])[2])))));for(z=1,#operations,my(op=operations[z],ri=op[1]);if(type(op[2])=="t_INT",S[ri,]*=ep^op[2],my(v=op[2]);assert(v[ri]==1,"row replacement coefficient one");for(i=1,n,bad=lcm(bad,abs(contents(v[i])[2])));S[ri,]=sum(i=1,n,v[i]*S[i,])));assert(matrix(n,32,i,j,polcoef(S[i,j],0,ep))==primitive,"exact full row operation replay");my(dc=contents(rankMinor));bad=lcm(bad,abs(dc[1]*dc[2]));print("AUDITED_PRIMES stage=",which," ",factor(bad)[,1]~);if(which==1,my(K=matrix(15,3,i,j,polcoef([T^2,T^3,T^4*(b*T+b+2)][j],15-i,T)));assert(primitive[,1..15]*K==matrix(12,3)&&matrank(K)==3,"first exact three-direction kernel");assert(primitive[,16..32]==matrix(12,17),"first complete low block"),assert(matrank(primitive[,1..6])==6&&primitive[,7..32]==matrix(6,26),"second full consecutive kernel"));)}
read("research/results/bmd-elliptic-adjacent-profile-20261009/field-audit.gp");
q=vector(7,i,if(i==6,1,if(i==7,7,0)))~;
assert(field997[,1..7]*q==vector(6)~&&matrank(field997[,1..7])==6&&field997[,8..32]==matrix(6,25),"exact exceptional rational source");
u='u;endpoint=u^7*(u+2)^7*((u+1)^2+7);
M=matrix(2,2,i,j,polcoef(endpoint,14+i-j,u));
assert(M==[120,560;16,120]&&matdet(M)==5440&&Mod(matdet(M),997)==455,"exceptional endpoint determinant nonzero");
print("EXCEPTIONAL_ENDPOINT matrix=",M," determinant=",matdet(M)," residue997=",Mod(matdet(M),997));
print("COMPLETE independent row replay, denominator audit and both complete kernels and the exceptional endpoint.");
quit;
