\\ Test the relative Frobenius criterion at both remaining positive centres b2,b3 for n9.
\\ Shared roots and full V6 jet matrices are built once at each of the two fixed marks.
\\ b2: N512,h10,first permitted t3; b3:N768,h1,first permitted t0.
\\ Largest matrix769-square, below the archived1024-square5s control; expected under20s.
\\ Pass yields all-exponent original families through the reviewed criterion, not a complete cover.
default(parisizemax,2000000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
basis(d)={my(v=List());for(S=0,511,if(hammingweight(S)<=d,for(j=0,(d-hammingweight(S))\2,listput(v,[S,j]))));Vec(v);};
jetmat(labels,mark,wval,I,N)={
 my(one=labels[1]^0,roots=vector(9,i,wval[i]*sqrt(one+labels[i]/(one+labels[i]*mark)*T+O(T^N))),products=vector(512),co=vector(#I));
 for(i=1,9,assert(valuation(roots[i]^2-(one+labels[i]*mark+labels[i]*T),T)>=N,"marked square identity"));
 products[1]=one+O(T^N);
 for(S=1,511,if(hammingweight(S)<=6,my(b=valuation(S,2));products[S+1]=products[S-2^b+1]*roots[b+1]));
 for(j=1,#I,my(v=(mark+T)^I[j][2]*products[I[j][1]+1]);co[j]=vector(N,r,polcoef(v,r-1,T)));
 matrix(N,#I,r,j,co[j][r])
};
{
my(start=getwalltime(),q=6561,modulus=ffinit(3,8,'a),a=ffgen(modulus,'a),one=a^0,lc=[508,5690,5164,3098,2894,6147,276,4463,174],labels=apply(c->sum(j=0,7,(c\3^j)%3*a^j),lc),P=sum(j=0,7,(295\3^j)%3*a^j),wv=apply(z->sqrt(one+z*P),labels),Ibig=basis(6));
assert(vector(9,j,lift(polcoef(modulus,j-1)))==[1,2,2,1,0,0,2,1,1] && #Ibig==769,"fixed field and complete source");
my(Jbig=jetmat(labels,P,wv,Ibig,768),Jzero=jetmat(labels,0*one,vector(9,i,one),Ibig,768),polys=vector(512),blocks=vector(512),initial=vector(512),rows3=vector(512),direct=vector(512));
print("CENTRES_SHARED_READY max_jet_matrix=768x769 wall_ms=",getwalltime()-start);
for(S=0,511,
 polys[S+1]=prod(i=1,9,if(bittest(S,i-1),one+labels[i]*T,one));
 my(g=(hammingweight(S)-1)\2);
 if(g>0,
  blocks[S+1]=matrix(g,g,i,j,polcoef(polys[S+1],3*(i-1)+2-(j-1),T));
  initial[S+1]=vector(g,j,if(j==1,one,0*one));
  my(r=initial[S+1]);for(t=1,3,r=apply(z->z^3,r)*blocks[S+1]);rows3[S+1]=r;
  my(v=1/sqrt(polys[S+1]+O(T^27)));direct[S+1]=vector(27,j,polcoef(v,j-1,T))
 )
);
my(field=vector(q,j,sum(k=0,7,((j-1)\3^k)%3*a^k)),codes=Map(),allout=List());
for(j=1,q,mapput(codes,Str(field[j]),j-1));
for(b=2,3,
 my(N=256*b,II=basis(3-b),h=#II,idx=select(j->2*Ibig[j][2]+hammingweight(Ibig[j][1])<=3+b,vector(#Ibig,j,j)),I=apply(j->Ibig[j],idx),J=matrix(N,#I,r,j,Jbig[r,idx[j]]),J0=matrix(N,#I,r,j,Jzero[r,idx[j]]),K=matker(J),K0=matker(J0),t=if(b==2,3,0),rws=if(b==2,rows3,initial),power=3^t,checks=0);
 assert(#I==N+h && matsize(K)==[#I,h] && matsize(K0)==[#I,h],"full jets and exact kernel dimensions");
 assert(J*K==matrix(N,h) && J0*K0==matrix(N,h),"actual kernels");
 my(C=matrix(#I,h,i,j,
  my(S=I[i][1],R=II[j][1],U=bitxor(511,bitxor(S,R)),f=polys[bitand(S,R)+1]*T^(I[i][2]+II[j][2]),row=rws[U+1]);
  assert(poldegree(f)<#row,"holomorphic product");
  my(value=sum(k=0,#row-1,row[k+1]*polcoef(f,k,T)),raw=sum(k=0,min(poldegree(f),power-1),polcoef(f,k,T)*direct[U+1][power-k]));
  assert(value==raw,"direct versus Cartier");checks++;value
 ),pair=mattranspose(K)*C,rank=matrank(pair),stackrank=matrank(matconcat([J;mattranspose(C)])),D=256*((3+b)*N+9*N*(N-1)));
 assert(stackrank==N+rank,"stacked rank identity");
 assert(mattranspose(K0)*C==matrix(h,h),"same-mark vanishing");
 print("CENTRE b=",b," degree_centre=",3+b," source=",#I," jets=",N," kernel=",h," iterate=",t," pairing_rank=",rank," determinant=",matdet(pair)," stacked_rank=",stackrank," direct_checks=",checks," pole_bound=",D);
 listput(allout,[b,t,N,h,vector(N,i,vector(#I,j,mapget(codes,Str(J[i,j])))),vector(#I,i,vector(h,j,mapget(codes,Str(C[i,j])))),rank,vector(N,i,vector(#I,j,mapget(codes,Str(J0[i,j]))))]);
 assert(rank==h,"chosen first iterate not full; do not infer a generic obstruction")
);
my(out="research/results/bmd-exception-relative-centres-20261008/matrices.g");
write(out,"CENTRE_FIELD := ",vector(9,j,lift(polcoef(modulus,j-1))),";");
write(out,"CENTRE_DATA := ",Vec(allout),";");
print("RELATIVE_CENTRES_COMPLETED cases=2 all_first_iterates_full=true wall_ms=",getwalltime()-start);
}
quit;
