\\ Full symbolic-source reductions at precisely the rational certificate's excluded large primes.
default(parisizemax,1000000000);
default(nbthreads,1);
ep='ep;b='b;T='T;
assert(c,msg)=if(!c,print("FAIL ",msg);quit(1));
OUT="research/results/bmd-elliptic-adjacent-profile-20261009/field-audit.gp";
{for(stage=1,2,read(concat("research/results/bmd-elliptic-adjacent-profile-20261009/",if(stage==1,"constraints.gp","second-constraints.gp")));my(fields=if(stage==1,[29],[139,997,3463,3539,12589,189041]),n=matsize(R)[1]);for(z=1,#fields,my(p=fields[z],S=Mod(1,p)*R,depth=vector(n),steps=0);while(1,for(i=1,n,my(v=vecmin(vector(32,j,valuation(S[i,j],ep))));assert(v<64,"nonzero row");if(v>0,S[i,]/=ep^v;depth[i]+=v));my(C=matrix(n,32,i,j,polcoef(S[i,j],0,ep)),K=matker(C~));if(matsize(K)[2]==0,break);my(v=K[,1],ri=0,d=0);for(i=1,n,if(v[i]!=0,ri=i;d=max(d,depth[i])));v/=v[ri];S[ri,]=sum(i=1,n,v[i]*S[i,]);depth[ri]=d;steps++;assert(steps<=n*64,"polynomial minor degree bound"));my(C=matrix(n,32,i,j,polcoef(S[i,j],0,ep)),matches=0);assert(vecmax(depth)<32&&matrank(C)==n,"full bounded saturated rows");if(stage==1,my(K=matrix(15,3,i,j,polcoef([T^2,T^3,T^4*(b*T+b+2)][j],15-i,T)));matches=(C[,1..15]*K==matrix(12,3)&&C[,16..32]==matrix(12,17)),matches=(matrank(C[,1..6])==6&&C[,7..32]==matrix(6,26)));write(OUT,"field",p,"=",C,"; depth",p,"=",depth,";");print("FIELD stage=",stage," p=",p," max_pole=",vecmax(depth)," expected_source=",matches));)}
print("COMPLETE all seven excluded large-prime source matrices; inspect each expected_source flag.");
quit;
