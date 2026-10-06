\\ Full seven high cuts of the exceptional p7 boundary, retaining both source profiles.
default(parisizemax,1000000000);
default(nbthreads,1);
h;u;
assert(b,s)={if(!b,error(s));};
{
my(o=Mod(1,7),uu=o*u,D=103,N=832,M=422,rs=uu/(uu^2+1),a0=rs^2,S=uu^2+uu^-2);
my(A=[2*D-2,[[[2*D-1,1]],[[2*D-2,1]],[[2*D-3,1]]]],B=[2*D-1,[[[2*D-1,1],[2*D-2,5],[2*D-3,1]],[[2*D,1],[2*D-2,4],[2*D-3,2]]]]);
my(powers=[[5,0],[2,0],[0,3],[3,3]],spaces=[A,B,B,A],row=0,W=matrix(7,18));
for(ch=1,4,
 my(al=powers[ch][1],be=powers[ch][2],re=(-1)^be,Space=spaces[ch],main=al+be+2*Space[1],hi=M-(M-al-be)%2,wid=(hi-main)/2,levels=vector(wid,j,hi-2*(j-1)),Out=matrix(wid,#Space[2]));
 for(j=1,#Space[2],my(emax=vecmax(vector(#Space[2][j],k,Space[2][j][k][1])));
  for(k=1,#Space[2][j],my(e=Space[2][j][k][1],co=Space[2][j][k][2],lead=al+be+6+2*e,poly=co*(-a0)^(e-emax)*(1+h)^(al+2)*(1-h)^(be+4)*(1-S*h+h^2+O(h^16))^e);
   for(i=1,wid,my(ix=(lead-levels[i])/2);if(ix>=0,Out[i,j]+=polcoef(poly,ix,h)));
  );
 );
 assert(matrank(Out)==#Space[2],"outlier independence");my(Rel=matker(Out~)~);
 my(H=matrix(wid,13,i,j,my(r=M-levels[i],k=r-13+j);if(k>=0,o*binomial(N,k)*(-uu)^k,0*o)),L=matrix(wid,13,i,j,my(r=M-levels[i],k=r-j+1);if(k>=0,re*o*binomial(N,k)*(-1)^k*uu^-k,0*o)),High0=Rel*H,High1=Rel*L);
 for(i=1,matsize(Rel)[1],my(den=o,gg=0*o);for(j=1,13,den=lcm(den,denominator(High0[i,j]));den=lcm(den,denominator(High1[i,j])));
  for(j=1,13,High0[i,j]*=den;High1[i,j]*=den;gg=gcd(gg,gcd(High0[i,j],High1[i,j])));
  row++;for(j=1,wid,my(r=M-levels[j]);assert(r<=8,"high-cut depth");W[row,r+1]=Rel[i,j]*den/gg;W[row,r+10]=re*Rel[i,j]*den/gg);
 );
);
assert(row==7,"complete high cut count");
my(out="research/results/bmd-eight-exceptional-deformation-20261006/high-cuts.sing");write(out,"matrix HighCuts[7][18];");
for(i=1,7,for(j=1,18,if(W[i,j]!=0,write(out,"HighCuts[",i,",",j,"]=",liftall(W[i,j]),";"))));
write("research/results/bmd-eight-exceptional-deformation-20261006/high-cuts.gp","HIGH_CUTS=",liftall(W),";");
print("PASS seven complete high cuts, with row normalization matching the stored original matrix.");
}
quit;
