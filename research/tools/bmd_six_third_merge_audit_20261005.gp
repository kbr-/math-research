\\ Verify the mixed finite/infinity cut and the actual five/nine boundary criteria.
\\ Cases cover the safe branch, all ternary lambda values, and exceptional p=5,7.
default(parisizemax,2000000000);setrand(20261005);
s;z;T;
assert(c,m)={if(!c,error(m));};
{
my(cases=[[4,3],[5,3],[7,3],[10,3],[5,5],[8,5],[7,7]]);
for(cas=1,#cases,
 my(d=cases[cas][1],p=cases[cas][2],g=ffgen(p^6,'a),o=g^0,ii=sqrt(-o),u=random(g),b=4*d-5,m=2*b-2,N=4*m,n=N/2,bad=(b-2)%p==0);
 while(u==0 || u^4==o,u=random(g));
 my(PB=concat(vector(b+1,j,(1+s)^(2*(j-1))*o),vector(b-3,j,(1+s)*((1+s)^2-1)^2*(1+s)^(2*(j-1))*o)));
 my(MB=matrix(m,2*b+1,i,j,polcoef(PB[i],j-1,s)));
 if(bad,
   assert(matrank(MB[,1..m-1])==m-1 && matrank(MB[,1..m])==m-1 && matrank(MB[,1..m+1])==m,"exceptional cut profile"),
   assert(matrank(MB[,1..m])==m,"safe cut profile")
 );
 my(av=u^2/(u^2+1)^2,az=u^2/(u^2-1)^2,L=o+av*T+O(T^N),H=o+az*T+O(T^N),v=sqrt(L),w=sqrt(H),sh=[L,v,v*w^3,w^3],R=List());
 for(j=1,4,
   if(bad && (j==1 || j==3),
     for(k=0,m-2,listput(R,sh[j]*T^k));listput(R,sh[j]*H^m),
     for(k=0,m-1,listput(R,sh[j]*T^k))
   );
 );
 assert(#R==N,"limiting row count");
 my(dr=N-matrank(matrix(N,N,i,j,polcoef(R[i],j-1,T))),extra=if(bad,8,4),M=n+extra/2,K=matrix(extra+1,extra+1,i,j,0*o));
 for(j=0,extra,
   my(P=(z-u)^N*z^j,DP=deriv(P,z),HH=vector(5,k,polcoef(P,N+extra-(k-1),z)),LL=vector(5,k,polcoef(P,k-1,z)));
   K[1,j+1]=subst(DP,z,o)-M*subst(P,z,o);
   K[2,j+1]=-subst(DP,z,-o)-M*subst(P,z,-o);
   K[3,j+1]=ii^(-M)*subst(P,z,ii)+(-ii)^(-M)*subst(P,z,-ii);
   K[4,j+1]=HH[1]+LL[1];
   if(bad,
     K[5,j+1]=HH[2];K[6,j+1]=LL[2];
     K[7,j+1]=HH[3]-LL[3]+(n+2)*(HH[1]-LL[1]);
     K[8,j+1]=HH[4]+LL[4];
     K[9,j+1]=HH[5]+LL[5]+(n-2)*(HH[3]+LL[3]),
     K[5,j+1]=HH[2]+LL[2]
   );
 );
 my(kr=extra+1-matrank(K));assert(kr==dr,"boundary/direct coranks disagree");
 print("d=",d," p=",p," mark=",u," bad_merge=",bad," cut_profile=PASS criterion_size=",extra+1," criterion_corank=",kr," direct_corank=",dr," lambda=",binomial(N,3)%p);
);
print("PASS: all seven actual profile and boundary-kernel controls");
}
quit;
