\\ Independent positive-degree extraction of every complete source constraint.
default(parisizemax,1000000000);
default(nbthreads,1);
ep='ep;b='b;T='T;x='x;
assert(c,msg)=if(!c,print("FAIL ",msg);quit(1));
{for(stage=1,2,my(p=23,s=23*stage,gdeg=if(stage==1,3,1),C=s+if(stage==1,7,6),g=if(stage==1,(1+T)*(1+2*T)^2,1+T),G=g*(1+ep*T)^(gdeg+1),emax=2*s+12,odd=2*gdeg+1,o=Mod(1,p),A=matrix(gdeg,gdeg,i,j,o*polcoef((x-1)^(emax+j),2*i-1,x)));read(concat("research/results/bmd-elliptic-extreme-profile-20261009/",if(stage==1,"constraints.gp","second-constraints.gp")));my(expected=o*subst(R,b,2),actual=matrix(matsize(R)[1],32));for(h=0,31,my(e=emax-h,al=-A^-1*vector(gdeg,i,o*polcoef((x-1)^e,2*i-1,x))~,f=o*(x-1)^e+sum(j=1,gdeg,al[j]*(x-1)^(emax+j)),ev=sum(j=0,C,polcoef(f,2*j,x)*(1+ep*T)^j),od=g*sum(j=0,C-gdeg,polcoef(f,odd+2*j,x)*(1+ep*T)^j));for(i=1,gdeg,assert(polcoef(f,2*i-1,x)==0,"exact omitted odd source coefficient"));for(which=1,2,my(F=if(which==1,ev,od),fac=o*2^(12-h)*ep^(h-s+if(which==1,0,gdeg)));if(stage==1,for(j=1,7,actual[(which-1)*7+j,h+1]=fac*(polcoef(F,s+j,T)-polcoef(G,j,T)*polcoef(F,s,T))),for(j=2,6,actual[(which-1)*5+j-1,h+1]=fac*(polcoef(G,1,T)*polcoef(F,s+j,T)-polcoef(G,1,T)*(2*polcoef(G,j,T)-polcoef(G^2,j,T))*polcoef(F,s,T)-(polcoef(G^2,j,T)-polcoef(G,j,T))*polcoef(F,s+1,T))))));assert(actual==expected,"all original high-source equations match the bounded encoding");print("DIRECT_SOURCE stage=",stage," positive_parameter=",s," field=23 equations=",matsize(R)[1]*32," all_pass=true"));}
print("COMPLETE independent full-polynomial source controls.");
quit;
