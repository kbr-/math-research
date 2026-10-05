\\ Independent full Laurent reconstruction of the bounded smoothing vector at the first family member.
\\ Solve for the explicit kernel in the actual saturated source, differentiate that source basis,
\\ remove outer poles by an actual order-N section, and compare all eleven symbolic entries.
default(parisizemax,3000000000);
default(threadsize,64000000);
default(threadsizemax,512000000);
default(nbthreads,1);
setrand(20261005);
if(default(nbthreads)!=1,quit(1));
assert(c,s)={if(!c,error(s));};
cuts(P,M,N,u,ii)={
 my(o=u^0,b=vector(11,j,0*o),der=deriv(P,z),plus=vector(7,j,polcoef(P,2*M-(j-1),z)+polcoef(P,j-1,z)),minus=vector(7,j,polcoef(P,2*M-(j-1),z)-polcoef(P,j-1,z)));
 for(j=0,1,
  my(a=(1-2*j)*o);
  b[j+1]=(a-u)^(1-N)*a^(-M)*(subst(der,z,a)-M/a*subst(P,z,a));
 );
 b[3]=ii^(-M)*subst(P,z,ii)+(-ii)^(-M)*subst(P,z,-ii);
 b[4]=plus[2];b[5]=plus[6]+2*plus[4];
 b[6]=plus[1];b[7]=plus[5]+plus[3];b[8]=plus[7]+3*plus[3];
 b[9]=minus[3]-2*minus[1];b[10]=minus[5]-minus[1];b[11]=minus[4]-minus[2];
 return(b~);
};
{
my(d=10,p=7,c=8*d-17,N=8*c+8,M=4*c+9,MP=M+14,g=ffgen(p^4,'a),o=g^0,u=random(g));
while(u==0 || u^4==o,u=random(g));
my(ss=u^2+u^-2,quad=z^4-ss*z^2+o,C=u^N,ii=sqrt(-o),cols=List(),pref=[[1,0],[0,3],[2,0],[1,3]],add=[[2,4],[2,4],[0,4],[0,4]]);
print("d=",d," p=",p," c=",c," state=",c%49," N=",N," M=",M," u=",u," seed=20261005 threads=",default(nbthreads));
for(kind=1,4,
 my(m=if(kind<=2,3,2),base=pref[kind],extra=add[kind]);
 for(j=0,m-1,listput(cols,[base[1],base[2],j,o/2]));
 for(r=0,6,
  my(A=(c-r)\7,B=(c-m-r)\7,K=A+B+1);
  for(k=0,K,listput(cols,[base[1]+extra[1],base[2]+extra[2],r+7*k,-k*o/4]));
 );
);
assert(#cols==N,"source count");
my(powers=vector(2*c+1));powers[1]=o;for(j=1,2*c,powers[j+1]=powers[j]*quad);
my(polys=vector(N,j,my(b=cols[j]);z^(M-b[1]-b[2]-2*b[3])*(z^2+o)^b[1]*(z^2-o)^b[2]*powers[b[3]+1]));
my(S=matrix(2*M+1,N,i,j,polcoef(polys[j],i-1,z)),marked=(z-u)^N,Q=C*(o-u*z)*(o+z^2)*(u+C*z^7),F=marked*Q,Fvec=vector(2*M+1,j,polcoef(F,j-1,z))~);
my(ik=matindexrank(S),I=ik[1]);
assert(#I==N,"independent full source");
my(coords=matsolve(vecextract(S,I,vector(N,j,j)),vector(N,j,Fvec[I[j]])~));
assert(S*coords==Fvec && cuts(F,M,N,u,ii)==vector(11,j,0*o)~,"explicit kernel in actual full source and cuts");
print("full Laurent source coordinates verified");
my(weighted=S*vector(N,j,cols[j][4]*coords[j])~,Pone=quad^7*sum(j=1,2*M+1,weighted[j]*z^(j-1)));
assert(poldegree(Pone,z)<=2*MP,"first variation pole bound");
my(top=sum(j=0,13,polcoef(Pone,2*MP-j,z)*x^j)+O(x^14),bottom=sum(j=0,13,polcoef(Pone,j,z)*x^j)+O(x^14));
my(upper=top*(o-u*x+O(x^14))^(-N),lower=bottom/C*(o-x/u+O(x^14))^(-N));
my(R=sum(j=0,13,polcoef(lower,j,x)*z^j+polcoef(upper,j,x)*z^(38-j)),removed=marked*R,red=Pone-removed);
for(j=0,13,assert(polcoef(red,j,z)==0 && polcoef(red,2*MP-j,z)==0,"exact outer pole cancellation"));
my(reduced=red/z^14);
assert(type(reduced)=="t_POL" && poldegree(reduced,z)<=2*M,"reduced original ambient");
my(b=cuts(reduced,M,N,u,ii),expected=vector(11,j,0*o)~);
expected[4]=(2*u^30+2*u^28-2*u^2-2)/u^14*C^2;
expected[5]=(u^2+1)/u^8*C^3+(-2*u^30-2*u^28+2*u^2+2)/u^14*C^2+(-u^10-u^8)*C;
expected[6]=(-2*u^28+2)/u^13*C^2;
expected[7]=(-3*u^8-3*u^6-1)/u^7*C^3+(-2*u^16-2*u^14+2*u^2+2)/u^7*C^2+(u^9+3*u^3+3*u)*C;
expected[8]=(2*u^2+2)/u*C^3+(2*u^28-u^22-u^20+u^8+u^6-2)/u^13*C^2+(-2*u^3-2*u)*C;
assert(b==expected,"all eleven bounded symbolic deformation entries");
my(D=Mat(vector(11,j,cuts(marked*z^(j-1),M,N,u,ii))),left=matker(D~));
assert(#left==1,"one-dimensional small cokernel");
my(scalar=(left~*b)[1]);
assert(scalar!=0,"nonzero intrinsic first variation");
print("reduced_vector=",b~);
print("small_cokernel_scalar=",scalar);
print("PASS: exact full-source variation, outer-pole removal, all eleven symbolic entries, nonzero scalar");
}
quit;
