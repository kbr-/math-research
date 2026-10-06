\\ Independent exact check of the upper1/lower2 source cuts, all basis sections.
default(parisizemax,1000000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
cut(P,M,upper,ii)={
 my(H=vector(7,j,polcoef(P,2*M-j+1,z)),Lo=vector(7,j,polcoef(P,j-1,z)),D=deriv(P,z));
 my(F=[subst(D,z,1)-M*subst(P,z,1),-subst(D,z,-1)-M*subst(P,z,-1),ii^(-M)*subst(P,z,ii)+(-ii)^(-M)*subst(P,z,-ii)]);
 if(upper,concat(F,[H[1]+Lo[1],H[2]+Lo[2],H[7]+Lo[7]-2*(H[5]+Lo[5]),H[5]-Lo[5]-H[3]+Lo[3]+H[1]-Lo[1]]),concat(F,[H[1]+Lo[1],H[2]+Lo[2]]));
};
{
my(a=ffgen(ffinit(3,4,'a),'a),o=a^0,u=a,ii=ffprimroot(a)^((3^4-1)/4),S=u^2+u^-2,T=o*z^4-S*z^2+o);
assert(u^4!=1 && ii^2==-o,"admissible conic");
for(upper=0,1,
 my(c=if(upper,55,56),M=4*c+if(upper,7,6),dim=8*c+8,count=0);
 for(ch=1,4,
  my(A=[2,1,0,1][ch],B=[0,0,3,3][ch],isA=(ch==2||ch==3),bound=2*c+if(upper && isA,-1,1),base=o*(z^2+1)^A*(z^2-1)^B,power=o);
  for(j=0,bound,
   my(P=z^(M-A-B-2*j)*base*power);
   assert(cut(P,M,upper,ii)==vector(if(upper,7,5),k,0*o),"main source cut");count++;
   power*=T;
  );
  if(upper && isA,
   A+=2;B+=4;base=o*(z^2+1)^A*(z^2-1)^B;
   power=T^(2*c-2);
   for(j=2*c-2,2*c-1,
    my(P=z^(M-A-B-2*j)*base*power);
    assert(cut(P,M,upper,ii)==vector(7,k,0*o),"exceptional source cut");count++;power*=T;
   );
  );
 );
 my(C=matrix(if(upper,7,5),2*M+1,i,j,cut(o*z^(j-1),M,upper,ii)[i]));
 assert(count==dim && matrank(C)==2*M+1-dim,"dimension and independent cuts");
 print("PASS upper=",upper," c=",c," sections=",count," ambient=",2*M+1," cut_rank=",matrank(C));
);
print("PASS full source memberships and independent cut codimensions; field=",a.pol," u=",u);
}
quit;
