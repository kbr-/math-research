\\ Exact controls of the general last-root merge; no original large jet matrices.
default(parisizemax,1000000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
{
my(cases=[[3,6],[3,7],[5,6],[5,7]]);
for(cs=1,#cases,
 my(p=cases[cs][1],d=cases[cs][2],c=8*d-17,D=2*c-7,Q=2*c-12,res=(Q%p==0),a=ffgen(ffinit(p,2,'a),'a),o=a^0,V=o+t,W=o+a*t,Z=o+(a+1)*t,g6=W^2*Z^4);
 assert(a!=0 && a!=1 && a!=-1,"distinct nonzero slopes");
 for(m=6,7,
  my(A=c-m,B=c-8,qmax=max(2*A,2*B+1),E=if(m==7,vector(qmax+1,j,j-1),if(res,concat(vector(Q-1,j,j-1),[Q]),vector(Q,j,j-1))),g=if(m==6,g6,V*g6),qpow=p);
  while(qpow<=qmax+2,qpow*=p);
  my(root=(Mod(1,p)+t+O(t^(qmax+3)))^((qpow+1)/2));
  assert(#E==A+B+2,"full core dimension");
  for(j=1,#E,
   my(e=E[j],f=Mod(2,p)^e*(X-1)^e);
   if(m==6 && !res && e==Q-1,f+=Mod(2,p)^e/Mod(Q,p)*(X-1)^Q);
   for(k=0,qmax,if((k%2==0 && k>2*A)||(k%2==1 && k>2*B+1),assert(polcoef(f,k,X)==0,"actual core source support")));
   my(lifted=subst(f,X,root));
   assert(valuation(lifted,t)==e && polcoef(lifted,e,t)==Mod(1,p),"normalized dilation lift");
  );
  my(cols=concat(vector(m,j,o*t^(j-1)),vector(#E,j,g*t^E[j])),pred=if(m==6 && res,concat(vector(D,j,o*t^(j-1)),[g6*t^Q]),vector(D+1,j,o*t^(j-1))));
  my(height=D+2,M=matrix(height,#cols,i,j,polcoef(cols[j],i-1,t)),P=matrix(height,#pred,i,j,polcoef(pred[j],i-1,t)));
  assert(#cols==D+1 && matrank(M)==D+1 && matrank(matconcat([M,P]))==D+1,"full finite-cut limit equality");
  print("PASS p=",p," d=",d," divisor_degree=",m," core_dimension=",#E," limit_dimension=",#cols," exceptional=",m==6&&res);
 );
 my(weights=[6,7,9,9,8,8,10,11],sizes=[0,1,1,1,2,2,2,3],gdegrees=vector(8,j,(weights[j]-sizes[j])/2),M=2*D+11+2*res,N=8*(D+1),ambient=4*M,high=sum(j=1,8,(M-sizes[j])\2-gdegrees[j]-D));
 assert(vecsum(gdegrees)==28 && high==8+8*res && ambient-N==36+8*res,"all eight character costs");
 print("PROFILE p=",p," d=",d," D=",D," N=",N," M=",M," ambient=",ambient," finite=28 high=",high," square_criterion=",ambient-N);
);
print("PASS all four field/degree controls, complete core lifts and both source profiles.");
}
quit;
