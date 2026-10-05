\\ Uniform low-u matching matrices for q=3^e, e=3,4,5,6 mod8, d>=4.
\\ Representative exponents [11,4 (12 above precision36),5,6] have q>=81. Coefficient dependence
\\ is through q mod81 and mod8; PREC=32 stays below omitted constant terms.
default(parisizemax,1000000000);
u;
PREC=32;if(getenv("PREC")!=0 && getenv("PREC")!="",PREC=eval(getenv("PREC")));g=ffgen(9,'a);o=g^0;ii=sqrt(-o);uu=Mod(u,u^PREC);nodes=[o,-o,ii,-ii];
OUT=getenv("OUT");if(OUT==0 || OUT=="",error("OUT required"));
emit(s)={print(s);write(OUT,s);};
assert(c,s)={if(!c,error(s));};
rootpow(z,n)={sum(k=0,PREC-1,o*binomial(n,k)*(-uu)^k*z^(n-k));};
highcf(alpha,kk,r,v)={my(l=alpha-kk-1-r);if(v==-1,(-1)^l+sum(b=0,kk+r-1,binomial(alpha-1,b)*binomial(alpha-2-b,kk+r-1-b)),sum(h=0,v,binomial(v,h)*binomial(alpha-1,kk+r+h)*2^(kk+r+h)));};
{
my(proofmode=getenv("PROOF")!="" && getenv("PROOF")!=0,exponents=[11,if(PREC>36 || proofmode,12,4),5,6]);
for(cas=1,4,
 if(proofmode,PREC=if(cas==2,48,32);uu=Mod(u,u^PREC));
 my(ee=exponents[cas],q=3^ee,delta=(q-16)%32,d=(q+48-delta)/32,c=(15-delta)/2,alpha=(q+1)/2,A=16*d-16,B=A-16,M=8*d-6,MM=M-8,L=B+c,kk=16-2*c,nq=c+5,nfree=max(0,5-c),dim=nq+nfree);
 if(getenv("ONLY")!=0 && getenv("ONLY")!="" && c!=eval(getenv("ONLY")),next);
 assert(d>=4 && L-1>=PREC && B+4>=PREC && alpha>=PREC,"precision boundary");
 my(W=vector(PREC,r,vector(PREC,v,o*highcf(alpha,kk,r-1,v-2))));
 my(den=(1+u+O(u^PREC))^(-2)*(1-u+O(u^PREC))^(-4));
 my(TA=matrix(PREC,nq,r,j,0*uu));
 for(r=0,PREC-1,for(j=0,nq-1,
   my(z=0*uu);
   for(a=0,(PREC-1-j)\4,for(b=0,(PREC-1-j-4*a)\2,
     my(v=j-1+2*a+2*b,k=j+4*a+2*b);
     z+=o*(-1)^a*binomial(alpha-1,a)*polcoef(den,b,u)*W[r+1][v+2]*uu^k;
   ));
   TA[r+1,j+1]=z;
 ));
 my(PW=matrix(PREC,4,r,h,rootpow(nodes[h],L-r)),PD=matrix(PREC,4,r,h,o*(L-r)*rootpow(nodes[h],L-r-1)));
 my(F=matrix(dim,dim,i,j,0*uu));
 for(j=0,nq-1,
   my(val=vector(4,h,rootpow(nodes[h],alpha)*nodes[h]^j),der=vector(4,h,o*alpha*rootpow(nodes[h],alpha-1)*nodes[h]^j+if(j,o*j*rootpow(nodes[h],alpha)*nodes[h]^(j-1),0*uu)));
   F[1,j+1]=val[1]*(-M)+der[1];F[2,j+1]=val[2]*(-M)-der[2];
   F[3,j+1]=val[3]+val[4];F[4,j+1]=der[3]+der[4]+o*M*ii*(val[3]-val[4]);
   F[5,j+1]=if(j==nq-1,o,0*o)+if(j==0,(-uu)^alpha,0*uu);
   my(vv=vector(4,h,sum(r=0,PREC-1,uu^r*TA[r+1,j+1]*PW[r+1,h])),dd=vector(4,h,sum(r=0,PREC-1,uu^r*TA[r+1,j+1]*PD[r+1,h])));
   F[6,j+1]=dd[1]-MM*vv[1];F[7,j+1]=-dd[2]-MM*vv[2];
   F[8,j+1]=vv[3]+vv[4];F[9,j+1]=dd[3]+dd[4]+o*MM*ii*(vv[3]-vv[4]);
   if(c>=5,
     for(r0=0,c-5,
       my(row=if(r0==c-5,dim,10+r0));
       F[row,j+1]=sum(r=0,r0,(-1)^(r0-r)*binomial(L-1-r,r0-r)*TA[r+1,j+1]);
     )
   );
 );
 for(j=0,nfree-1,
   my(col=nq+j+1,pow=L+j,vv=vector(4,h,rootpow(nodes[h],pow)),dd=vector(4,h,o*pow*rootpow(nodes[h],pow-1)));
   F[6,col]=dd[1]-MM*vv[1];F[7,col]=-dd[2]-MM*vv[2];
   F[8,col]=vv[3]+vv[4];F[9,col]=dd[3]+dd[4]+o*MM*ii*(vv[3]-vv[4]);
   F[10,col]=if(j==nfree-1,o,0*o);
 );
 emit(Str("case e=",ee," mod8=",ee%8," q=",q," d=",d," c=",c," alpha=",alpha," L=",L," dim=",dim," precision=",PREC));
 write(OUT,Str("matrix=",F));
 write(OUT,Str("valuations=",matrix(dim,dim,i,j,min(PREC,valuation(lift(F[i,j]),u)))));
 my(EX=if(proofmode,matdet(matrix(dim,dim,i,j,lift(F[i,j]))),0));
 F=matrix(dim,dim,i,j,lift(F[i,j])+O(u^PREC));
 my(DD=matdet(F));
 if(proofmode && DD!=0,assert(valuation(EX,u)==valuation(DD,u) && polcoef(EX,valuation(EX,u),u)==polcoef(DD,valuation(DD,u),u),"exact polynomial determinant disagrees");emit("Exact polynomial determinant leading term agrees"));
 emit(Str("determinant=",DD));
 if(DD==0,emit("UNRESOLVED at this precision"),emit(Str("leading_order=",valuation(DD,u)," leading_coefficient=",polcoef(DD,valuation(DD,u),u))));
);
}
quit;
