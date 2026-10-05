\\ Independent exact matching-to-direct-jet check for c=7,6,3.
\\ Includes both extra high-coefficient rows and free matching-polynomial columns.
default(parisizemax,2000000000);
x;z;T;
assert(c,s)={if(!c,error(s));};
rowsZ(a1,a3,j,N)={my(l1=1+a1*T+O(T^N),l3=1+a3*T+O(T^N),w1=sqrt(l1),w3=sqrt(l3),base=l1^(1-j)*l3^(2-2*j),sh=[l3^2,w3*l1,w1/l1*l3^2,w1*w3],R=List());for(s=1,4,for(k=0,4*j-5,listput(R,base*sh[s]*T^k)));Vec(R);};
conds(P,M)={my(ip=subst(P,z,ii),im=subst(P,z,-ii),DP=deriv(P,z));[subst(DP,z,o)-M*subst(P,z,o),-subst(DP,z,-o)-M*subst(P,z,-o),ip+im,subst(DP,z,ii)+subst(DP,z,-ii)+M*ii*(ip-im),polcoef(P,2*M,z)+polcoef(P,0,z)];};
{
my(g=ffgen(3^6,'a));o=g^0;ii=sqrt(-o);my(u=g);assert(u^4!=o,"bad conic mark");
for(ee=4,6,
 my(q=3^ee,delta=(q-16)%32,d=(q+48-delta)/32,c=(15-delta)/2,alpha=(q+1)/2,A=16*d-16,B=A-16,N=A+B,M=8*d-6,MM=M-8,L=B+c,nq=c+5,nfree=max(0,5-c),dim=nq+nfree,X=o+x+O(x^L));
 print("BEGIN e=",ee," d=",d," N=",N," matching_dim=",dim," mark=",u);
 my(K=matrix(dim,dim,i,j,0*o));
 for(j=0,nq-1,
   my(up=(z-u)^alpha*z^j,uc=conds(up,M));for(r=1,5,K[r,j+1]=uc[r]);
   my(F=u^j*X^(j-1)*(X+1)^(alpha-1)*(1-u^4*X^2)^(alpha-1)/((1+u^2*X^2)^2*(1-u^2*X^2)^4));
   my(P=sum(l=0,L-1,polcoef(F,l,x)*(z/u-1)^l),lc=conds(P,MM));
   for(r=1,4,K[5+r,j+1]=lc[r]);
   if(c>=5,for(r0=0,c-6,K[10+r0,j+1]=polcoef(P,L-1-r0,z)));
   K[dim,j+1]=lc[5];
 );
 for(j=0,nfree-1,
   my(P=(z-u)^(L+j),lc=conds(P,MM),col=nq+j+1);
   for(r=1,4,K[5+r,col]=lc[r]);K[dim,col]=lc[5];
 );
 my(kcor=dim-matrank(K),a1=u^2/(u^2+1)^2,a3=u^2/(u^2-1)^2,R=concat(rowsZ(a1,a3,d,N),apply(f->f*T^alpha,rowsZ(a1,a3,d-1,N))));
 assert(#R==N,"direct count");
 my(dcor=N-matrank(matrix(N,N,i,j,polcoef(R[i],j-1,T))));
 assert(kcor==dcor,"matching/direct discrepancy");
 print("PASS e=",ee," c=",c," matching_corank=",kcor," direct_corank=",dcor);
);
}
quit;
