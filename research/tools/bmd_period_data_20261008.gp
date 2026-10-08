\\ Export actual kernel bases and reference cup matrices for a complete stable-period test.
\\ Reuse maximal jets per curve; validate every kernel/reference rank and all root squares.
\\ Input format: curve count; per curve field degree, base degree, period; modulus;9 labels;
\\ four cases: b,source dimension,h,reference exponent residue,reference rank; K if b>0; C_ref.
\\ No full-period computation is done here. Largest matrix768x769; prior dual-centre run14s.
read("research/tools/bmd_root_jets.gp");
default(parisizemax,2500000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
joinfields(v,sep)={my(s="");for(j=1,#v,s=Str(s,if(j==1,"",sep),v[j]));s;};
{
my(out="research/results/bmd-exception-period-cover-20261008/period-inputs.txt",start=getwalltime());
write(out,2);
for(ci=0,1,
 my(f=if(ci==0,6,8),basef=if(ci==0,3,8),q=3^f,modulus=ffinit(3,f,'z),z=ffgen(modulus,'z),one=z^0,field=vector(q,j,sum(k=0,f-1,((j-1)\3^k)%3*z^k)),codes=Map(),labels,mark);
 for(j=1,q,mapput(codes,Str(field[j]),j-1));
 if(ci==0,my(a=field[613]);assert(a^3+2*a+2==0,"same embedded F27 generator");labels=vector(9,i,a^(i-1));mark=one,
  my(lc=[508,5690,5164,3098,2894,6147,276,4463,174]);labels=apply(c->field[c+1],lc);mark=field[296]
 );
 my(wval=apply(a->sqrt(one+a*mark),labels),Ibig=rootbasis(9,6),Jbig=rootjets(labels,mark,wval,Ibig,768),Jzero=rootjets(labels,0*one,vector(9,i,one),Ibig,768),polys=vector(512),rows=vector(512));
 assert(#Ibig==769,"complete maximal source");
 for(S=0,511,
  polys[S+1]=prod(i=1,9,if(bittest(S,i-1),one+labels[i]*T,one));
  my(g=(hammingweight(S)-1)\2);
  if(g>0,
   my(B=matrix(g,g,i,j,polcoef(polys[S+1],3*(i-1)+2-(j-1),T)),r=vector(g,j,if(j==1,one,0*one)));
   if(ci==0,
    my(D=matrix(g,g,i,j,B[i,j]^9)*matrix(g,g,i,j,B[i,j]^3)*B);
    rows[S+1]=vector(6,j,r*D^9360)
   ,
    my(seq=vector(6));seq[1]=r;
    for(t=1,5,r=apply(v->v^3,r)*B;seq[t+1]=r);
    rows[S+1]=seq
   )
  )
 );
 write(out,f," ",basef," ",if(ci==0,28080,74880));
 write(out,joinfields(apply(x->Str(x),vector(f+1,j,lift(polcoef(modulus,j-1))))," "));
 write(out,joinfields(apply(x->Str(x),apply(a->mapget(codes,Str(a)),labels))," "));
 for(b=0,3,
  my(I=rootbasis(9,3+b),II=rootbasis(9,3-b),h=#II,N=256*b,idx=select(j->2*Ibig[j][2]+hammingweight(Ibig[j][1])<=3+b,vector(#Ibig,j,j)),K,t=if(ci==0,0,[5,4,3,0][b+1]));
  if(b,
   my(J=matrix(N,#I,r,j,Jbig[r,idx[j]]),J0=matrix(N,#I,r,j,Jzero[r,idx[j]]));K=matker(J);
   assert(matsize(K)==[#I,h] && matrank(J0)==N && J*K==matrix(N,h),"actual full kernel/reference");
  ,K=matid(h)*one);
  my(C=matrix(#I,h,i,j,my(S=I[i][1],R=II[j][1],U=bitxor(511,bitxor(S,R)),fpoly=polys[bitand(S,R)+1]*T^(I[i][2]+II[j][2]),row=rows[U+1][t+1]);assert(poldegree(fpoly)<#row,"holomorphic source product");sum(k=0,#row-1,row[k+1]*polcoef(fpoly,k,T))),rank=matrank(mattranspose(K)*C));
  if(ci==1 || b<3,assert(rank==h,"previous accepted reference rank"));
  write(out,b," ",#I," ",h," ",t," ",rank);
  if(b,for(i=1,#I,write(out,joinfields(apply(x->Str(x),vector(h,j,mapget(codes,Str(K[i,j]))))," "))));
  for(i=1,#I,write(out,joinfields(apply(x->Str(x),vector(h,j,mapget(codes,Str(C[i,j]))))," ")));
  print("PERIOD_INPUT curve=",ci," b=",b," source=",#I," h=",h," reference_residue=",t," rank=",rank)
 );
);
print("PERIOD_INPUTS_COMPLETED path=",out," wall_ms=",getwalltime()-start);
}
quit;
