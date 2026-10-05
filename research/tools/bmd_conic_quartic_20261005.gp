\\ Check the new quartic criterion against the original conic Hasse matrix.
\\ This is a one-off encoding check for the 5 October 2026 proof, not a degree sweep.
\\ Cases: (d,p)=(3,3),(6,3),(6,5), two admissible marks per case.
\\ The original four character rows are those of bmd_two_pair_conic_normality.gp.
\\ Assert equality of kernel dimensions; the known exceptional case has the explicit
\\ Frobenius quartic (z-u)(u^81*z^3+1). All arithmetic is exact in finite fields.
default(parisizemax, 1000000000);
OUT=getenv("OUT");
emit(s)={print(s);if(OUT!=0 && OUT!="",write(OUT,s));}
quartic(u,ii,d)={
  my(N=16*d-16,n=N/2,a=(u-ii)^N,b=(u+ii)^N,c=u^N,H=(n+2)*u^2+2-n,F=matrix(5,5));
  for(j=0,4,
    F[1,j+1]=(j+n-2)+(n+2-j)*u;
    F[2,j+1]=(-1)^j*((2-n-j)+(n+2-j)*u);
    F[3,j+1]=a*ii^j+b*(-ii)^j;
    F[4,j+1]=a*((u^2+1)*if(j,j*ii^(j-1),0)+(-2*n*u+ii*H)*ii^j)+b*((u^2+1)*if(j,j*(-ii)^(j-1),0)+(-2*n*u-ii*H)*(-ii)^j));
  F[5,1]=c;F[5,5]=1;F;
}
direct(u,d,o)={
  my(N=16*d-16,a1=u^2/(u^2+1)^2,a3=u^2/(u^2-1)^2,l1=o+a1*T+O(T^(N+2)),l3=o+a3*T+O(T^(N+2)),w1=sqrt(l1),w3=sqrt(l3));
  my(gens=[l3^2,w3*l1,w1*l3^2/l1,w1*w3],rows=List());
  for(g=1,4,for(j=0,4*d-5,listput(rows,gens[g]*T^j)));
  if(#rows!=N,error("dimension"));
  my(M=matrix(N,N+2,i,j,polcoeff(rows[i],j-1,T)));
  [matrank(M[,1..N]),matrank(M)];
}
setrand(20261005);
{
my(cases=[[3,3],[6,3],[6,5]]);
for(cas=1,#cases,
  my(d=cases[cas][1],p=cases[cas][2],N=16*d-16,e=2*ceil(log(1e5)/(2*log(p))),g=ffgen(p^e,'a),o=g^0,ii=sqrt(-o));
  for(sample=1,2,
    my(u=0);until(u!=0 && u^2!=1 && u^2!=-1,u=random(g));
    my(F=quartic(u,ii,d),rk=matrank(F),dr=direct(u,d,o));
    if(5-rk!=N-dr[1],error("quartic/direct kernel mismatch"));
    if(d==6 && p==3,
      my(q=vector(5,j,polcoeff((z-u)*(u^81*z^3+1),j-1,z))~);
      if(F*q!=vector(5,j,0)~,error("Frobenius witness failed")));
    emit(Str("d=",d," p=",p," extension=",e," sample=",sample," u=",u," quartic_rank=",rk," direct_rank_N=",dr[1]," direct_rank_Nplus2=",dr[2]))));
emit("PASS: six exact comparisons; the Frobenius witness passed at both exceptional marks.");
}
quit;
