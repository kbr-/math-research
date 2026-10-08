\\ Finish the finite set of low-degree centres: b0 means the140-dimensional canonical theta bundle.
\\ First admissible iterate5 has243jets; smaller iterates have rank at most81.
\\ Stages: cached Cartier blocks and direct inverse-root243jets; full140-square cup; corruption.
\\ Expected under5s from the prior47-square full-source/direct coefficient test.
default(parisizemax,1500000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
{
my(start=getwalltime(),q=6561,modulus=ffinit(3,8,'a),a=ffgen(modulus,'a),one=a^0,lc=[508,5690,5164,3098,2894,6147,276,4463,174],labels=apply(c->sum(j=0,7,(c\3^j)%3*a^j),lc),basis=List(),polys=vector(512),rows=vector(512),direct=vector(512));
for(S=0,511,
 polys[S+1]=prod(i=1,9,if(bittest(S,i-1),one+labels[i]*T,one));
 if(hammingweight(S)<=3,for(j=0,(3-hammingweight(S))\2,listput(basis,[S,j])));
 my(g=(hammingweight(S)-1)\2);
 if(g>0,
  my(B=matrix(g,g,i,j,polcoef(polys[S+1],3*(i-1)+2-(j-1),T)),r=vector(g,j,if(j==1,one,0*one)));
  for(t=1,5,r=apply(z->z^3,r)*B);rows[S+1]=r;
  my(v=1/sqrt(polys[S+1]+O(T^243)));direct[S+1]=vector(243,j,polcoef(v,j-1,T))
 )
);
my(I=Vec(basis),h=#I,checks=0);assert(h==140,"complete middle source");
my(C=matrix(h,h,i,j,
 my(S=I[i][1],R=I[j][1],U=bitxor(511,bitxor(S,R)),f=polys[bitand(S,R)+1]*T^(I[i][2]+I[j][2]),r=rows[U+1],v=sum(k=0,#r-1,r[k+1]*polcoef(f,k,T)),raw=sum(k=0,poldegree(f),polcoef(f,k,T)*direct[U+1][243-k]));
 assert(poldegree(f)<#r && v==raw,"holomorphic/direct coefficient control");checks++;v
),rank=matrank(C),det=matdet(C));
assert(C==mattranspose(C),"symmetric cup");
print("MIDDLE_CUP iterate=5 rank=",rank," target=140 determinant=",det," direct_checks=",checks);
assert(rank==h,"middle first iterate not full; no all-centre claim");
my(field=vector(q,j,sum(k=0,7,((j-1)\3^k)%3*a^k)),codes=Map(),out="research/results/bmd-exception-relative-centres-20261008/middle.g");
for(j=1,q,mapput(codes,Str(field[j]),j-1));
write(out,"MIDDLE_FIELD := ",vector(9,j,lift(polcoef(modulus,j-1))),";");
write(out,"MIDDLE_CODES := ",vector(h,i,vector(h,j,mapget(codes,Str(C[i,j])))),";");
write(out,"MIDDLE_DET := ",mapget(codes,Str(det)),";");
C[,2]=C[,1];assert(matdet(C)==0,"duplicate-column control");
print("MIDDLE_CUP_COMPLETED direct_checks=",checks," corruption_detected=true wall_ms=",getwalltime()-start);
}
quit;
