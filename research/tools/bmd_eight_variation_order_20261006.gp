\\ Actual saturated elliptic frame at the smallest obstructed conic degree.
\\ Reuse one boundary inverse and lift its kernel until the first nonzero cokernel coefficient.
default(parisizemax,3000000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
bin(n,k)={if(k<0,0,binomial(n,k));};
OUT=getenv("OUT");if(OUT==0 || OUT=="",error("OUT required"));
emit(s)={print(s);write(OUT,s);};
{
my(d=6,D=16*d-41,N=8*(D+1),J=9,q=2*D+1,rr=[1,3,5],C=matrix(3,q+1,i,j,Mod((-1)^(j-1-rr[i])*bin(j-1,rr[i]),3)),piv=List(),rank=0);
forstep(j=q,q-8,-1,my(ix=concat(Vec(piv),[j+1]),rk=matrank(matrix(3,#ix,i,k,C[i,ix[k]])));if(rk>rank,listput(piv,j+1);rank=rk);if(rank==3,break));
assert(rank==3,"full source cuts");
my(PV=Vec(piv),Inv=matrix(3,3,i,j,C[i,PV[j]])^-1,E=select(e->!setsearch(Set(PV),e+1),vector(q+1,j,j-1)),nbase=3+#E,Delta=matrix(J+1,nbase),xp=(Mod(1,3)+z+O(z^(q+J+2)))^122,remseries=xp^7,yp=vector(q+1));
assert(nbase==2*D+2,"source block dimension");yp[1]=Mod(1,3);for(j=2,q+1,yp[j]=yp[j-1]*(xp-1));
for(j=0,J,for(k=1,3,Delta[j+1,k]=Mod(bin(17,j),3));assert(Delta[j+1,1]==polcoef(remseries,j,z),"independent remainder frame coefficient"));
for(col=1,#E,
 my(e=E[col],a=Inv*C[,e+1],f=Mod(2,3)^e*(yp[e+1]-sum(k=1,3,a[k]*yp[PV[k]])));
 for(j=0,J,
  my(val=Mod(0,3));
  for(h=0,j,
   my(co=if(h==0,Mod(1,3),Mod(0,3)));
   for(k=1,3,if(PV[k]-1==e+h,co=-a[k]));
   if(co!=0,val+=co*(-1)^(j-h)*Mod(2,3)^(h-2*j)*(bin(e+2*j-h-1,j-h)-bin(e+2*j-h-1,j-h-1)));
  );
  Delta[j+1,col+3]=val;
  assert(val==polcoef(f,e+j,z),"independent square-root frame coefficient");
 );
);
assert(vector(nbase,j,Delta[1,j])==vector(nbase,j,Mod(1,3)),"normalized constant frame");
for(col=1,#E,assert(Delta[2,col+3]==if(E[col]==2*D-1,Mod(0,3),Mod(-E[col],3)),"first variation formula"));
my(modulus=ffinit(3,10,'a),a=ffgen(modulus,'a),o=a^0,u=a,rs=u/(u^2+1),ss=u/(u^2-1),b=-ss^2/rs^2,t=o*T+O(T^N),r=sqrt(1-t),s=sqrt(1+b*t),g=(1-t)*(1+b*t)^2,pre=[r^3,r^2,s^3,r*s^3],base=concat(vector(3,j,t^(j-1)),vector(#E,j,g*t^E[j])));
my(functions=vector(N,j,pre[(j-1)\nbase+1]*base[(j-1)%nbase+1]),A=matrix(N,N,i,j,polcoef(functions[j],i-1,T)),ix=matindexrank(A),Rows=ix[1],Cols=ix[2]);
assert(#Rows==N-1 && #Cols==N-1,"known boundary corank one");
my(freeRow=select(j->!setsearch(Set(Rows),j),vector(N,j,j))[1],freeCol=select(j->!setsearch(Set(Cols),j),vector(N,j,j))[1],AI=matrix(N-1,N-1,i,j,A[Rows[i],Cols[j]])^-1,k0=vector(N,j,0*o)~,left=vector(N,j,0*o));
k0[freeCol]=o;my(kp=-AI*vector(N-1,i,A[Rows[i],freeCol])~,lp=-vector(N-1,j,A[freeRow,Cols[j]])*AI);
for(j=1,N-1,k0[Cols[j]]=kp[j];left[Rows[j]]=lp[j]);left[freeRow]=o;
assert(A*k0==vector(N,j,0*o)~ && left*A==vector(N,j,0*o),"exact boundary kernel and cokernel");
emit(Str("FIELD=",modulus," d=",d," D=",D," N=",N," u=",u," b=",b," free_row=",freeRow," free_column=",freeCol));
emit("PASS all saturated frame coefficients through order9 against direct square-root expansion");
write(OUT,"CORE_ORDERS=",E);write(OUT,"COEFFICIENTS=",Delta);write(OUT,"RIGHT_KERNEL=",k0);write(OUT,"LEFT_KERNEL=",left);
my(lifts=List(),found=0);listput(lifts,k0);
for(j=1,J,
 my(rhs=vector(N,i,0*o)~);
 for(h=1,j,
  my(v=A*vector(N,i,Delta[h+1,(i-1)%nbase+1]*lifts[j-h+1][i])~);
  rhs-=vector(N,i,if(i>h,v[i-h],0*o))~;
 );
 my(obstruction=left*rhs);
 emit(Str("order=",j," cokernel_coefficient=",obstruction));
 if(obstruction!=0,found=j;break);
 my(kj=vector(N,i,0*o)~,part=AI*vector(N-1,i,rhs[Rows[i]])~);
 for(i=1,N-1,kj[Cols[i]]=part[i]);assert(A*kj==rhs,"exact kernel-lift equation");
 listput(lifts,kj);write(OUT,"KERNEL_LIFT_ORDER_",j,"=",kj);
);
if(found,emit(Str("PASS first nonzero actual saturated determinant order=",found)),emit("UNRESOLVED: no nonzero coefficient through order9; not an infinite-order assertion"));
}
quit;
