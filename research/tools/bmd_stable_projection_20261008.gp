\\ Test the existing nonordinary F27 root curve at the common Cartier return.
\\ Work in F729 only to choose a distinct mark; original labels remain in F27.
\\ Return exponent L=3*9*lcm_(j<=4)(27^j-1); compute stable projectors by binary matrix powers.
\\ Stages: fixed field/marks; complete256x303 jets; all small stable projectors;
\\ compare three-step functionals with direct27jets; restrict return cup; export actual matrices.
\\ Largest rank522-square, prior two-centre test14s; expected under20s.
default(parisizemax,1500000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
basis(d)={my(v=List());for(S=0,511,if(hammingweight(S)<=d,for(j=0,(d-hammingweight(S))\2,listput(v,[S,j]))));Vec(v);};
jetmat(labels,mark,wval,I,N)={
 my(one=labels[1]^0,roots=vector(9,i,wval[i]*sqrt(one+labels[i]/(one+labels[i]*mark)*T+O(T^N))),products=vector(512),co=vector(#I));
 for(i=1,9,assert(valuation(roots[i]^2-(one+labels[i]*mark+labels[i]*T),T)>=N,"marked square identity"));
 products[1]=one+O(T^N);
 for(S=1,511,if(hammingweight(S)<=5,my(b=valuation(S,2));products[S+1]=products[S-2^b+1]*roots[b+1]));
 for(j=1,#I,my(v=(mark+T)^I[j][2]*products[I[j][1]+1]);co[j]=vector(N,r,polcoef(v,r-1,T)));
 matrix(N,#I,r,j,co[j][r])
};
{
my(start=getwalltime(),q=729,modulus=ffinit(3,6,'z),z=ffgen(modulus,'z),one=z^0,field=vector(q,j,sum(k=0,5,((j-1)\3^k)%3*z^k)),a=0,acode=-1);
for(j=2,q,if(field[j]^3+2*field[j]+2==0,a=field[j];acode=j-1;break));
assert(acode>0 && a^27==a,"embedded recorded F27 generator");
my(labels=vector(9,i,a^(i-1)),wv=apply(x->sqrt(one+x),labels),Ibig=basis(5),L=3*9*lcm(vector(4,j,27^j-1)),Jbig=jetmat(labels,one,wv,Ibig,512),Jzero=jetmat(labels,0*one,vector(9,i,one),Ibig,512));
assert(#Ibig==522,"complete largest source");
print("STABLE_SETUP field=",modulus," F27_generator_code=",acode," P_T=1 Q_T=0 period=",L," P_roots=",wv);
my(polys=vector(512),rows=vector(512),rows3=vector(512),direct=vector(512),blocks=0,stable_rank=0,nonordinary=0);
for(S=0,511,
 polys[S+1]=prod(i=1,9,if(bittest(S,i-1),one+labels[i]*T,one));
 my(g=(hammingweight(S)-1)\2);
 if(g>0,
  my(B=matrix(g,g,i,j,polcoef(polys[S+1],3*(i-1)+2-(j-1),T)),D=matrix(g,g,i,j,B[i,j]^9)*matrix(g,g,i,j,B[i,j]^3)*B,E=D^(L/3),r=vector(g,j,if(j==1,one,0*one)));
  assert(E*E==E && D^4*(matid(g)*one-E)==matrix(g,g) && matrank(E)==matrank(D^4),"exact stable projection");
  rows[S+1]=r*E;rows3[S+1]=r*D;
  stable_rank+=matrank(E);blocks++;if(matdet(B)==0,nonordinary++);
  my(v=1/sqrt(polys[S+1]+O(T^27)));direct[S+1]=vector(27,j,polcoef(v,j-1,T))
 )
);
my(codes=Map(),out="research/results/bmd-exception-stable-projection-20261008/matrices.g",allout=List());
for(j=1,q,mapput(codes,Str(field[j]),j-1));
for(b=0,2,
 my(I=basis(3+b),II=basis(3-b),N=256*b,h=#II,idx=select(j->2*Ibig[j][2]+hammingweight(Ibig[j][1])<=3+b,vector(#Ibig,j,j)),J=matrix(N,#I,r,j,Jbig[r,idx[j]]),J0=matrix(N,#I,r,j,Jzero[r,idx[j]]),K=if(N,matker(J),matid(h)*one),K0=if(N,matker(J0),matid(h)*one),checks=0);
 assert(#I==N+h && matsize(K)==[#I,h] && matsize(K0)==[#I,h],"actual kernel/reference ranks");
 if(N,assert(J*K==matrix(N,h) && J0*K0==matrix(N,h),"actual kernels"));
 my(C=matrix(#I,h,i,j,
  my(S=I[i][1],R=II[j][1],U=bitxor(511,bitxor(S,R)),f=polys[bitand(S,R)+1]*T^(I[i][2]+II[j][2]),r=rows[U+1],r3=rows3[U+1]);
  assert(poldegree(f)<#r,"holomorphic product");
  assert(sum(k=0,#r3-1,r3[k+1]*polcoef(f,k,T))==sum(k=0,poldegree(f),polcoef(f,k,T)*direct[U+1][27-k]),"three-step/direct coefficient check");
  checks++;sum(k=0,#r-1,r[k+1]*polcoef(f,k,T))
 ),pair=mattranspose(K)*C,rank=matrank(pair),sr=if(N,matrank(matconcat([J;mattranspose(C)])),rank));
 assert(sr==N+rank && blocks==466 && nonordinary>0,"stacked rank and nonordinary scope");
 print("STABLE_RETURN b=",b," blocks=",blocks," stable_Cartier_rank=",stable_rank," nonordinary_blocks=",nonordinary," relative_rank=",rank," target=",h," determinant=",matdet(pair)," stacked_rank=",sr," direct_checks=",checks);
 listput(allout,[b,N,h,vector(N,i,vector(#I,j,mapget(codes,Str(J[i,j])))),vector(N,i,vector(#I,j,mapget(codes,Str(J0[i,j])))),vector(#I,i,vector(h,j,mapget(codes,Str(C[i,j])))),rank])
);
write(out,"STABLE_FIELD := ",vector(7,j,lift(polcoef(modulus,j-1))),";");
write(out,"STABLE_DATA := ",Vec(allout),";");
print("STABLE_PROJECTION_COMPLETED cases=3 wall_ms=",getwalltime()-start);
}
quit;
