\\ Independent GP verification of FLINT norm certificates. Full control recomputes
\\ both original field-valued polynomial determinants before taking their norms.
\\ The series verifies every norm gcd, field, Vandermonde and two original-matrix
\\ evaluations, distinguishing these controls from a second full determinant run.
default(parisizemax,1000000000);
default(nbthreads,1);
x;z;t=varhigher("t");
assert(c,s)={if(!c,error(s));};
read(getenv("BMD_VERIFY_DATA"));
mkmat(n,aa,L)={
 my(o=aa[2]^0,N=n+1,m=N*(N-1)/2+2,out=List([vector(L,j,if(j==1,o,0*o)),vector(L,j,if(j==2,o,0*o))]));
 for(i=1,N,for(j=i+1,N,
  my(ser=sqrt(o+(aa[i]+aa[j])*t+aa[i]*aa[j]*t^2+O(t^L)));
  listput(out,vector(L,k,polcoef(ser,k-1,t)));
 ));
 assert(#out==m,"complete independent source");return(matrix(m,L,i,j,out[i][j]));
};
normpoly(P,pp,ee)={if(P==0,return(0));my(out=1);for(j=0,ee-1,out*=sum(k=0,poldegree(P,x),polcoef(P,k,x)^(pp^j)*x^k));return(out);};
{
for(ci=1,#DATA,
 my(d=DATA[ci],n=d[1],p=d[2],e=d[3],N=n+1,m=N*(N-1)/2+2,field=Mod(1,p)*Polrev(d[4],z),a=ffgen(field,'a),o=a^0,al=concat([0*o],vector(n,i,sum(j=0,e-1,d[5][i][j+1]*a^j))),be=concat([0*o],vector(n,i,sum(j=0,e-1,d[6][i][j+1]*a^j))),aa=vector(N,i,al[i]+x*be[i]));
 assert(polisirreducible(field),"field modulus");
 my(D=Mod(1,p)*Polrev(d[7],x),Dp=Mod(1,p)*Polrev(d[8],x),NV=Mod(1,p)*Polrev(d[9],x),G=Mod(1,p)*Polrev(d[10],x),V=prod(i=1,N,prod(j=i+1,N,aa[j]-aa[i])));
 assert(o*NV==normpoly(V,p,e),"exact field norm of all collision forms");
 my(expected=NV^N);expected/=pollead(expected);
 my(gd=gcd(D,Dp));for(j=1,#d[11],gd=gcd(gd,Mod(1,p)*Polrev(d[11][j],x)));
 gd/=pollead(gd);
 assert(gd==expected && G==expected,"complete independent norm gcd");
 my(betaM=mkmat(n,be,m),lead=matdet(betaM)^((p^e-1)/(p-1)));assert(lead!=0,"full original homogeneous direction");
 for(v=0,1,
  my(point=vector(N,i,al[i]+v*be[i]),M=mkmat(n,point,m+1),dv=matdet(matrix(m,m,i,j,M[i,j])),dpv=matdet(matrix(m,m,i,j,if(j<m,M[i,j],M[i,m+1]))));
  assert(o*subst(D,x,v)==dv^((p^e-1)/(p-1))/lead,"independent initial determinant value");
  assert(o*subst(Dp,x,v)==dpv^((p^e-1)/(p-1))/lead,"independent adjacent determinant value");
 );
 if(FULL_CONTROL,
  my(M=mkmat(n,aa,m+1),raw=matdet(matrix(m,m,i,j,M[i,j])),rawp=matdet(matrix(m,m,i,j,if(j<m,M[i,j],M[i,m+1]))),ND=normpoly(raw,p,e),NP=normpoly(rawp,p,e),lc=pollead(ND));
  assert(o*D==ND/lc && o*Dp==NP/lc,"full coefficient-by-coefficient original determinant norms");
  for(k=1,#d[11],my(other=matdet(matrix(m,m,i,j,if(j==k,M[i,m+1],M[i,j]))));assert(o*Mod(1,p)*Polrev(d[11][k],x)==normpoly(other,p,e)/lc,"all compound cofactor norms"));
 );
 print("PASS n=",n," p=",p," e=",e," full_polynomial_control=",FULL_CONTROL);
);
print("PASS all",#DATA," independent certificate checks.");
}
quit;
