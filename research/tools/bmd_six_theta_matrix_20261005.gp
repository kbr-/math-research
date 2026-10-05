\\ Dimension-six intrinsic theta matrix, exact truncated finite-field control.
\\ Test the smallest bulk d=4, p=3. No uniform normality inferred.
\\ All rows/columns use the formulas of the accompanying notebook entry.
default(parisizemax,2000000000);
s; t;
PREC=24; DEG=4; PRIME=3; m=8*DEG-12; NN=4*m;
if(getenv("PREC")!=0 && getenv("PREC")!="",PREC=eval(getenv("PREC")));
OUT=getenv("OUT");if(OUT==0 || OUT=="",error("OUT required"));
emit(x)={print(x);write(OUT,x);};
assert(c,x)={if(!c,error(x));};
g=ffgen(PRIME^6,'a);o=g^0;u=g;ii=sqrt(-o);Q=u^NN;assert(Q!=o,"torsion sample");
tt=Mod(t,t^PREC);ss=s+O(s^12);yy=(2+ss)/(2-ss);J=PREC\4+2;
tp=-prod(k=1,J,(o-tt^(4*k))^2);
th(c,b)={my(f=o-tt^b*c);for(k=1,J,f*= (o-tt^(4*k+b)*c)*(o-tt^(4*k-b)/c));f;};
TQ=th(Q,0);chi=[1,1,1,1;1,1,-1,-1;1,-1,1,-1;1,-1,-1,1];
signs=[1,-1,1,-1];hs=[0,0,2,2];bs=[0,0,2,2,1,1,3,3];bc=[ii,-ii,ii,-ii,1,-1,1,-1];
weights(l,j,n)={my(ans=0);for(r=0,l,my(k=l-r,h=(j-n+k-r)/2);if(k>=0 && k<=n && h>=0 && denominator(h)==1 && (n>0 || r==0),ans+=binomial(n,k)*(-1)^(n-k)*if(r==0,1,binomial(n+r-1,r))/4^(r+h)));ans;};
W=vector(6,l,vector(6,j,vector(11,n,weights(l-1,j-1,n-1))));
A=th(yy^2,0)/(2*tp*ss);
INV=vector(4,h,1/(yy^(if(h<=2,-m,m))*(th(signs[h]*yy/u,hs[h])/th(signs[h]/u,hs[h]))^NN*A^(-m)));
ETAS=vector(4,h,th(signs[h]/u,hs[h])^NN);
DATA=vector(20,c,matrix(4,6));
for(h=1,4,DATA[1][h,6]=chi[4,h]);
DATA[2][1,5]=1;DATA[2][3,5]=1;
DATA[3][1,5]=1;DATA[3][2,5]=1;
DATA[4][3,5]=1;DATA[4][4,5]=1;
for(h=1,4,for(j=1,4,DATA[4+4*(h-1)+j][h,j]=1));
BETA=vector(20,c,matrix(4,6,h,j,sum(k=j,6,DATA[c][h,k]*polcoef(INV[h],k-j,s))));
Rinv=tt^(2*m);
K=vector(8,b,vector(4,h,0));
GV=vector(8,b,0);
emit(Str("d=",DEG," p=",PRIME," m=",m," N=",NN," t_precision=",PREC," field=3^6 u=",u," i=",ii," Q=",Q));
{
for(b=1,8,
  my(a=bs[b],c=bc[b],par=if(a>=2,1,-1),den=th(yy^2*if(b<=4,-o,o),if(b<=4,0,2)));
  GV[b]=yy^(par*m)*th(c*yy/u,a)^NN*(2*tp/den)^m;
  for(h=1,4,
    my(sc=a-hs[h],fac=o);if(sc<0,sc+=4;fac=Q);
    K[b][h]=fac*tp*th(Q*c/signs[h]*yy,sc)/(TQ*th(c/signs[h]*yy,sc));
  );
);
emit("Local G jets and translated Kronecker kernels ready");
for(mode=0,1,
Rinv=if(mode,tt^(2*m),0*tt);
emit(Str("cross_scale_mode=",mode));
EV=vector(8,b,matrix(6,20));
for(b=1,8,for(c=1,20,
  my(f=0*o);
  for(h=1,4,
    my(part=0*o,fac=if(h>2 && c<=2,Rinv,o));
    for(j=1,6,
      if(BETA[c][h,j]!=0,
        my(E=sum(l=0,5,ss^l*sum(n=0,10,W[l+1][j][n+1]*polcoef(K[b][h],n,s))));
        part+=BETA[c][h,j]*E;
      );
    );
    f+=fac*part/ETAS[h];
  );
  f*=GV[b];
  for(l=0,5,EV[b][l+1,c]=polcoef(f,l,s));
));
F=matrix(20,20);
for(c=1,20,
 F[1,c]=EV[1][1,c]+EV[2][1,c];
 F[2,c]=EV[3][1,c]+EV[4][1,c];
 F[3,c]=Rinv*EV[1][1,c]-EV[3][1,c];
 F[4,c]=EV[1][2,c]+EV[2][2,c];
 F[5,c]=EV[3][2,c]+EV[4][2,c];
 F[6,c]=Rinv*EV[1][2,c]+EV[3][2,c];
 F[7,c]=Rinv*(EV[1][3,c]-EV[2][3,c])-EV[3][3,c]+EV[4][3,c];
 F[8,c]=Rinv*(EV[1][4,c]-EV[2][4,c])+EV[3][4,c]-EV[4][4,c];
 my(r=8);
 for(l=0,5,
   my(cs=if(l==0 || l==2,[3,4],if(l==1,[1,2,3,4],if(l==3 || l==5,[1,2],[]))));
   for(j=1,#cs,r++;F[r,c]=sum(h=1,4,chi[cs[j],h]*EV[4+h][l+1,c]));
 );
 assert(r==20,"row count");
);
emit("Twenty-by-twenty matrix ready");
write(OUT,Str("matrix=",F));
F=matrix(20,20,i,j,lift(F[i,j])+O(t^PREC));
DD=matdet(F);
emit(Str("determinant=",DD));
if(DD==0,emit("UNRESOLVED: determinant vanishes to available precision"),emit(Str("leading_t_order=",valuation(DD,t)," leading_coefficient=",polcoef(DD,valuation(DD,t),t))));
);
}
quit;
