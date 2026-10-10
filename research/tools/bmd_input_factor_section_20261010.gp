\\ Test the actual old 38-square minor on f=e1*e5-e6=0, off collisions.
\\ A nonzero determinant disproves divisibility of its symmetric normalized quotient by f.
\\ Stop at a witness; failure in the bounded search is explicitly inconclusive.
default(parisize,128000000);
default(nbthreads,1);
x='x;T=varhigher("T");
codeval(c,g)=sum(j=0,2,((c\5^j)%5)*g^j);
{
my(field=Mod(1,5)*(x^3+4*x^2+3*x+1),g=ffgen(field,'g),o=g^0,L=concat([0..35],[37,42]),found=0,tested=0);
if(!polisirreducible(field),error("Bad field"));setrand(20261010);
for(attempt=1,32,
 my(codes=Set(vector(7,i,1+random(124))));if(#codes!=7,next);
 my(old=vector(7,i,codeval(codes[i],g)),E=prod(i=1,7,1+old[i]*x),
 a1=polcoef(E,1),a4=polcoef(E,4),a5=polcoef(E,5),a6=polcoef(E,6));
 for(c=1,124,
  if(setsearch(codes,c),next);my(y=codeval(c,g));
  if(a1*a5-a6+a1*a4*y+a4*y^2!=0,next);
  my(roots=concat([0*o],concat(old,[y])),EE=E*(1+y*x),e1=polcoef(EE,1),e2=polcoef(EE,2),e5=polcoef(EE,5),e6=polcoef(EE,6),e7=polcoef(EE,7),
  f=e1*e5-e6,gg=(e1^2-e2)*e5-e1*e6+e7,V=prod(i=1,9,prod(j=i+1,9,roots[j]-roots[i])),
  rows=List([vector(38,j,if(L[j]==0,o,0*o)),vector(38,j,if(L[j]==1,o,0*o))]));
  if(f!=0||V==0,error("Invalid section point"));
  for(i=1,9,for(j=i+1,9,my(S=sqrt((o+roots[i]*T)*(o+roots[j]*T)+O(T^43)));listput(rows,vector(38,k,polcoef(S,L[k],T)))));
  my(M=matrix(38,38,i,j,rows[i][j]),r=matrank(M));tested++;
  print("SECTION codes=",concat([0],concat(Vec(codes),[c]))," rank=",r," f=",f," g=",gg);
  if(r==38,print("WITNESS determinant=",matdet(M)," normalized=",matdet(M)/V^9," matrix=",M);found=1;break);
 );
 if(found,break);
);
print("SECTION_COMPLETE found=",found," tested=",tested," field=",field);
}
quit;
