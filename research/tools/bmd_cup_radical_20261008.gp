\\ Actual quadratic section obstruction on the complete corank-one central cup.
\\ Six stable exponents, no series of length3^s; tiny Cartier matrix powers.
default(parisizemax,1000000000);
default(nbthreads,1);
T='T;
read("research/tools/bmd_root_jets.gp");
cr_assert(c,s)={if(!c,error(s));};
cr_frob(A,e)={matrix(matsize(A)[1],matsize(A)[2],i,j,A[i,j]^e);};
cr_row(v,B,s)={my(D=cr_frob(B,9)*cr_frob(B,3)*B,r=v*D^(s\3));for(j=1,s%3,r=matrix(1,#v,i,k,r[1,k]^3)*B);r;};
{
my(start=getwalltime(),a=ffgen(Mod(1,3)*(a^3+2*a+2),'a),one=a^0,I=rootbasis(9,3),poly=vector(512),off=vector(512),dims=vector(512),blocks=vector(512),initial=vector(512),total=0,exponents=vector(6,i,3834+4680*(i-1)),vectors=vector(6,i,vector(2,j,vector(769))),controls=0);
poly[1]=one;
for(S=1,511,my(b=valuation(S,2));poly[S+1]=poly[S-2^b+1]*(one+a^b*T));
for(S=0,511,
 my(g=max(0,(hammingweight(S)-1)\2));off[S+1]=total;dims[S+1]=g;
 if(g==0,next());
 my(B=matrix(g,g,i,j,if(3*i-j>=0,polcoef(poly[S+1],3*i-j,T),0)*one),series=1/sqrt(poly[S+1]+O(T^54)));
 blocks[S+1]=B;initial[S+1]=vector(2,j,matrix(1,g,u,l,if(j-l>=0,polcoef(series,j-l,T),0)*one));
 for(j=1,2,
  my(v=initial[S+1][j]);
  for(s=1,3,my(row=cr_row(v,B,s));for(l=0,g-1,cr_assert(row[1,l+1]==polcoef(series,j*3^s-1-l,T),"direct Cartier moment control");controls++));
  for(ii=1,6,my(row=cr_row(v,B,exponents[ii]));for(l=0,g-1,vectors[ii][j][total+l+1]=row[1,l+1]));
 );
 total+=g;
);
cr_assert(total==769,"all holomorphic coordinates");
my(field=vector(27,i,one*((i-1)%3)+a*(((i-1)\3)%3)+a^2*((i-1)\9)),codes=Map(),out="research/results/bmd-exception-cup-radical-20261008/data.g");
for(i=1,27,mapput(codes,Str(field[i]),i-1));
write(out,"RADICAL_EXPONENTS := ",exponents,";");
write(out,"RADICAL_DATA := [");
for(ii=1,6,
 my(Cs=vector(2,j,matrix(140,140,u,v,
  my(common=bitand(I[u][1],I[v][1]),S=511-bitxor(I[u][1],I[v][1]),shift=I[u][2]+I[v][2]);
  sum(l=0,poldegree(poly[common+1],T),polcoef(poly[common+1],l,T)*vectors[ii][j][off[S+1]+shift+l+1])
 )),C=Cs[1],C2=Cs[2],ker=matker(C));
 cr_assert(C==mattranspose(C)&&C2==mattranspose(C2)&&matsize(ker)==[140,1],"full symmetric corank-one cup");
 my(value=(mattranspose(ker)*C2*ker)[1,1],code=mapget(codes,Str(value)));
 print("CUP_RADICAL exponent=",exponents[ii]," rank=139 quadratic_raw=",value," code=",code);
 write(out,"[",vector(2,j,vector(140,u,vector(140,v,mapget(codes,Str(Cs[j][u,v]))))),",",vector(140,u,mapget(codes,Str(ker[u,1]))),",",code,"]",if(ii<6,",",""));
);
write(out,"];");
print("CUP_RADICAL_COMPLETED direct_controls=",controls," wall_ms=",getwalltime()-start);
}
quit;
