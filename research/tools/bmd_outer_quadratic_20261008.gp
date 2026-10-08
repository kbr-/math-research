\\ Actual quadratic section obstruction on the complete corank-one central cup.
\\ Exhaustive reduced period; eight sizing cases are retained separately from the remainder.
default(parisizemax,1000000000);
default(nbthreads,1);
T='T;
read("research/tools/bmd_root_jets.gp");
cr_assert(c,s)={if(!c,error(s));};
cr_frob(A,e)={matrix(matsize(A)[1],matsize(A)[2],i,j,A[i,j]^e);};
cr_row(v,B,s)={my(D=cr_frob(B,9)*cr_frob(B,3)*B,r=v*D^(s\3));for(j=1,s%3,r=matrix(1,#v,i,k,r[1,k]^3)*B);r;};
read("research/results/bmd-exception-outer-cups-20261008/exponents.gp");
{
my(start=getwalltime(),pilot=(getenv("BMD_OUTER_STAGE")=="pilot"),pairs=if(pilot,OUTER_PAIRS[1..8],OUTER_PAIRS[9..#OUTER_PAIRS]),count=#pairs,a=ffgen(Mod(1,3)*(a^3+2*a+2),'a),one=a^0,I=rootbasis(9,3),poly=vector(512),off=vector(512),total=0,vectors=vector(count,i,vector(2,j,vector(769))),periodchecks=0);
poly[1]=one;
for(S=1,511,my(b=valuation(S,2));poly[S+1]=poly[S-2^b+1]*(one+a^b*T));
for(S=0,511,
 my(g=max(0,(hammingweight(S)-1)\2));off[S+1]=total;if(g==0,next());
 my(B=matrix(g,g,i,j,if(3*i-j>=0,polcoef(poly[S+1],3*i-j,T),0)*one),series=1/sqrt(poly[S+1]+O(T^2)));
 for(j=1,2,
  my(v=matrix(1,g,u,l,if(j-l>=0,polcoef(series,j-l,T),0)*one));
  if(pilot,for(b=1,3,cr_assert(cr_row(v,B,b+4680)==cr_row(v,B,b),"both coefficient rows have exact short period");periodchecks++));
  for(ii=1,count,my(row=cr_row(v,B,pairs[ii][1]));for(l=0,g-1,vectors[ii][j][total+l+1]=row[1,l+1]));
 );total+=g;
);
cr_assert(total==769,"all coordinates");
my(field=vector(27,i,one*((i-1)%3)+a*(((i-1)\3)%3)+a^2*((i-1)\9)),codes=Map(),out=getenv("BMD_OUTER_OUT"));
for(i=1,27,mapput(codes,Str(field[i]),i-1));
write(out,"OUTER_QUADRATIC_DATA := [");
for(ii=1,count,
 my(Cs=vector(2,j,matrix(140,140,u,v,
  my(common=bitand(I[u][1],I[v][1]),S=511-bitxor(I[u][1],I[v][1]),shift=I[u][2]+I[v][2]);
  sum(l=0,poldegree(poly[common+1],T),polcoef(poly[common+1],l,T)*vectors[ii][j][off[S+1]+shift+l+1])
 )),C=Cs[1],C2=Cs[2],ker=matker(C),h=140-pairs[ii][2],restricted=mattranspose(ker)*C2*ker);
 cr_assert(C==mattranspose(C)&&C2==mattranspose(C2)&&matsize(ker)==[140,h],"full symmetric cup and expected kernel");
 my(encoded=matrix(h,h,u,v,mapget(codes,Str(restricted[u,v]))));
 print("OUTER_QUADRATIC exponent=",pairs[ii][1]," rank=",pairs[ii][2]," restricted_second=",encoded);
 write(out,"[",pairs[ii][1],",",pairs[ii][2],",",vector(2,j,vector(769,u,mapget(codes,Str(vectors[ii][j][u])))),",",vector(140,u,vector(h,v,mapget(codes,Str(ker[u,v])))),",",vector(h,u,vector(h,v,encoded[u,v])),"]",if(ii<count,",",""));
);
write(out,"];");print("OUTER_QUADRATIC_COMPLETED cases=",count," period_checks=",periodchecks," wall_ms=",getwalltime()-start);
}
quit;
