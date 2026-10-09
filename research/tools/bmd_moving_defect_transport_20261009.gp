\\ Validate a3-functional Mobius construction on the existing six-label
\\ witness at its old and moving marks. No new size or parameter sweep.
default(parisizemax,500000000);
default(parisize,64000000);
x='x;y='y;
g=ffgen(Mod(1,3)*('g^4+'g^3+'g^2+'g+1),'g);o=g^0;
ep=g;vv=g+o;DD=vv^2-o;A=DD*ep^2;B=DD^2*ep^4-ep^2;t=0*o;u=o+A+B;D=t-u;
FX=x^3+A*x^2+B*x-t;FY=y^3+A*y^2+B*y-u;
red(P)={my(R=P%FX,Z=0*o);for(i=0,2,Z+=x^i*(polcoef(R,i,x)%FY));Z};
co(P,i,j)=polcoef(polcoef(P,i,x),j,y);
Ls(P)={P=red(P);[
 co(P,2,1)-co(P,1,2),
 -A^2*co(P,1,0)+A^2*co(P,0,1)+A*B*co(P,2,0)-A*B*co(P,0,2)+A*D*co(P,2,1)-B*D*co(P,2,2),
 A^2*B*co(P,1,0)-A^2*B*co(P,0,1)-A*B^2*co(P,2,0)+A*B^2*co(P,0,2)+A^2*D*co(P,1,1)-B^2*D*co(P,2,2)
]};
{
my(labels=[0,ep+DD*ep^2,-ep+DD*ep^2,1,1+vv*ep+DD*ep^2,1-vv*ep+DD*ep^2]*o);
my(V=matrix(9,9,i,j,labels[(i-1)\3+1]^((j-1)\3)*labels[(i-1)%3+4]^((j-1)%3)));
if(matdet(V)==0,error("tensor evaluation"));
my(path="research/results/bmd-cubic-defect-coupling-20261009/transport-check.sing");
write(path,"ring r=(3,g),(z),dp; minpoly=g^4+g^3+g^2+g+1;");
for(case=1,2,
 my(tau=if(case==1,0*o,g^2),ix=lift(1/Mod(1+tau*x,FX)),iy=lift(1/Mod(1+tau*y,FY)),ax=red(x*ix),ay=red(y*iy),ss=ax+ay,dd=red((ax-ay)^2),Q=vector(11,j,0*o));
 Q[1]=o;for(l=1,10,Q[l+1]=red(ss*Q[l]+if(l>=2,dd*sum(h=0,l-2,Q[h+1]*Q[l-1-h]),0*o)));
 my(d3=red(((1+tau*x)*(1+tau*y))^3));
 for(l=0,6,if(Ls(red(d3*Q[l+1]))!=[0,0,0]*o,error("transported H9 annihilator")));
 my(aa=Ls(red(d3*Q[8])),bb=Ls(red(d3*Q[9])),cc=[aa[2]*bb[3]-aa[3]*bb[2],aa[3]*bb[1]-aa[1]*bb[3],aa[1]*bb[2]-aa[2]*bb[1]]);
 if(cc==[0,0,0]*o,error("dependent last constraints"));
 my(ell=vector(9,j,cc*Ls(red(d3*x^((j-1)\3)*y^((j-1)%3)))~),w=ell*V^-1,M=matrix(9,11,i,j,0*o));
 for(j=1,11,my(cv=vector(9,k,co(Q[j],(k-1)\3,(k-1)%3))~,ev=V*cv);for(i=1,9,M[i,j]=ev[i]));
 if(w*matrix(9,9,i,j,M[i,j])!=vector(9,j,0*o),error("raw kernel"));
 my(first=1);while(w[first]==0,first++);w/=w[first];
 if(case==1,if(ell[8]/cc[1]!=o||ell[6]/cc[1]!=-o,error("canonical specialization"));if(cc*Ls(Q[11])~/cc[1]!=-A^4*D,error("q10 specialization")));
 my(response=w*M[,11]);
 print("CASE = ",case,"; TAU = ",tau,"; CROSS_PRODUCT = ",cc,"; ROW_WEIGHTS = ",w,"; Q10_RESPONSE = ",response);
 write(path,Str("matrix W",case,"[1][9]; matrix M",case,"[9][11];"));
 for(i=1,9,write(path,Str("W",case,"[1,",i,"]=",w[i],";"));for(j=1,11,write(path,Str("M",case,"[",i,",",j,"]=",M[i,j],";"))));
 write(path,Str("matrix R",case,"=W",case,"*M",case,";"));
 write(path,Str("for(int j",case,"=1;j",case,"<=9;j",case,"++){if(R",case,"[1,j",case,"]!=0){ERROR(\"kernel mismatch\");}}"));
 write(path,Str("if(R",case,"[1,11]!=",response,"){ERROR(\"response mismatch\");}"))
);
write(path,"print(\"INDEPENDENT_MOVING_FUNCTIONALS_PASSED\"); quit;");
print("MOVING_DEFECT_TRANSPORT_COMPLETED")
}
quit;
