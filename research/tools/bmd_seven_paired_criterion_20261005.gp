\\ Independent d=5 control of the actual three-disjoint-pair n=7 limit.
\\ Compare its normalized character span and Hasse kernel with 36 conditions,
\\ then 32 after top-coordinate elimination. No all-degree rank inference.
default(parisizemax,1000000000);setrand(20261005);
assert(c,s)={if(!c,error(s));};
{
my(d=5,b=4*d-5,c=8*d-17,N=64*d-128,M=16*d-23,low=M-9);
my(exps=[[2,2,0],[2,2,0],[1,3,0],[1,3,0],[1,0,3],[1,0,3],[0,1,3],[0,1,3]]);
print("seed=20261005 d=",d," N=",N," M=",M," ambient=",4*M);
forprime(p=3,7,
 my(e=ceil(log(100000)/log(p)),g=ffgen(p^e,'a),o=g^0,aa=vector(3,i,random(g)));
 while(#Set(aa)!=3 || prod(i=1,3,aa[i])==0,aa=vector(3,i,random(g)));
 my(ll=vector(3,i,o+aa[i]*T+O(T^(N+1))),ww=apply(sqrt,ll));
 my(common=ll[1]^(1-d)*ll[2]^(2-2*d),shape=[ll[2]^2,ww[2]*ll[1],ww[1]/ll[1]*ll[2]^2,ww[1]*ww[2]],raw=List());
 for(s=1,4,for(block=0,1,
   my(f=common*shape[s]*if(block,ww[3]*ll[1]*ll[2]^2*ll[3]^(3-b),ll[3]^(7-b)));
   for(j=0,c,listput(raw,f*T^j));
 ));
 assert(#raw==N,"raw count");
 my(norm=ww[1]/(ww[2]*ww[3])*ll[1]^(d-1)*ll[2]^(2*d-2)*ll[3]^(b-3));
 my(chars=vector(8,s,prod(j=1,3,if(bittest(s-1,j-1),ww[j],o))),cols=List(),top=List(),omit=List());
 for(s=0,7,
  my(w=hammingweight(s),bound=(M-w)\2);
  for(j=0,bound,
   listput(cols,[s,j]);
   if(w+2*j>low,listput(top,#cols));
   if(j==bound && w<=1,listput(omit,#cols));
  );
 );
 my(Amb=matrix(N,#cols,i,j,polcoef(chars[cols[j][1]+1]*T^cols[j][2],i-1,T)),K=matker(Amb));
 assert(#cols==N+36 && #K==36 && #top==36 && #omit==4,"ambient/kernel dimensions");
 my(Phi=matrix(36,#cols,i,j,0*o),r=4);
 for(i=1,4,Phi[i,omit[i]]=o);
 for(s=0,7,for(node=1,3,for(k=0,exps[s+1][node]-1,
  r++;my(x=-1/aa[node]);
  for(j=1,#cols,if(cols[j][1]==s && cols[j][2]>=k,Phi[r,j]=binomial(cols[j][2],k)*x^(cols[j][2]-k)));
 )));
 assert(r==36 && matrank(Phi)==36,"36 independent constraints");
 my(Y=List());
 for(s=0,7,
  my(poly=prod(node=1,3,(o+aa[node]*T)^exps[s+1][node]));
  for(j=0,c,listput(Y,vector(#cols,k,if(cols[k][1]==s,polcoef(poly*T^j,cols[k][2],T),0*o))~));
 );
 my(YM=Mat(Vec(Y)));assert(matrank(YM)==N && Phi*YM==matrix(36,N),"table kernel");
 my(Raw=matrix(N,N,i,j,polcoef(raw[j]*norm,i-1,T)),Table=Amb*YM);
 assert(matrank(matconcat([Raw,Table]))==matrank(Table),"normalized spans");
 my(cor=N-matrank(Raw),cor36=36-matrank(Phi*K));assert(cor==cor36,"36 criterion");
 my(Top=matrix(36,36,i,j,K[top[i],j]));assert(matrank(Top)==36,"sample principal: cannot eliminate");
 my(C=K*Top^-1,free=select(i->!setsearch(Set(Vec(omit)),top[i]),vector(36,i,i)),PC=Phi*C);
 my(Small=matrix(32,32,i,j,PC[i+4,free[j]]),cor32=32-matrank(Small));
 assert(cor32==cor,"32 criterion");
 print("p=",p," e=",e," slopes=",aa," raw_rank=",N-cor," phi_rank=36 marked_rank=",36-cor36," top_rank=36 reduced_rank=",32-cor32," direct/table PASS");
);
print("PASS: three exact encoding controls; uniform determinant nonvanishing is not inferred.");
}
quit;
