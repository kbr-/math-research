\\ Actual section lifting through order8 on bounded original-curve cochains.
\\ Stop a multiplier at its first nonzero full scalar obstruction; retain corrections and gauges.
default(parisize,256000000);
default(parisizemax,2500000000);
default(nbthreads,1);
T='T;
read("research/tools/bmd_root_jets.gp");
read("research/tools/bmd_witt_jets_20261008.gp");
read("research/tools/bmd_root_cochains_20261008.gp");
read("research/tools/bmd_low_multiplier_core_20261008.gp");
read("research/results/bmd-exception-cubic-obstruction-20261008/assembly8-input.gp");
jo_source(v,I,one)={my(A=vector(512,i,0*one));for(i=1,140,A[I[i][1]+1]+=v[i]*T^I[i][2]);A;};
jo_obs(A,shift,I)={vector(140,i,512*polcoef(A[512-I[i][1]],shift-I[i][2]-1,T))~;};
jo_outside(A,shift)={for(S=0,511,if(A[S+1]!=0,jw_assert(2*(poldegree(A[S+1],T)-shift)+hammingweight(S)<=3,"outside section infinity bound")));};
jo_encode(A,shift,codes)={vector(512,S,vector(shift+2,j,mapget(codes,Str(polcoef(A[S],j-1,T)))));};
{
my(start=getwalltime(),pilot=(getenv("BMD_WITT_SECTION_STAGE")=="pilot"),selected=if(pilot,[3,5,7,8],[9..30]),a=ffgen(Mod(1,3)*(a^3+2*a+2),'a),one=a^0,field=vector(27,i,one*((i-1)%3)+a*(((i-1)\3)%3)+a^2*((i-1)\9)),codes=Map(),I=rootbasis(9,3),P=vector(512),R=vector(512),IR=vector(512),off=vector(512),total=0,precision=32,E=[1,1,2,2,0,1,0,0,2],out=getenv("BMD_WITT_SECTION_OUT"),records=List());
for(i=1,27,mapput(codes,Str(field[i]),i-1));P[1]=one;R[1]=one;IR[1]=one;
for(S=1,511,my(bit=valuation(S,2));P[S+1]=P[S-2^bit+1]*(one+a^bit*T);R[S+1]=truncate(sqrt(P[S+1]+O(T^precision)));IR[S+1]=truncate(1/(R[S+1]+O(T^precision))));
for(S=0,511,off[S+1]=total;total+=max(0,(hammingweight(S)-1)\2));jw_assert(total==769,"complete holomorphic coordinates");
for(ci=1,#selected,
 my(si=selected[ci],s=JC_EXPONENTS[si],W=vector(8,m,vector(512,i,0*one)),lambda=vector(769),nextlambda=vector(769),lambda2=vector(769));
 for(i=1,466,
  my(S=JC_CHARACTERS[i],given=JC_STATES[si][i],g=#given[1]);jw_assert(#given==8,"all eight normalized coordinates");
  for(m=1,8,W[m][S+1]=sum(j=1,g,field[given[m][j]+1]*T^(4-j)));
  my(next=P[S+1]*(sum(j=1,g,field[given[1][j]+1]*T^-j))^3);
  for(j=1,g,lambda[off[S+1]+j]=512*field[given[1][j]+1];lambda2[off[S+1]+j]=-512*field[given[2][j]+1];nextlambda[off[S+1]+j]=512*jw_coeff(next,-j));
 );
 my(C=lm_cup(lambda,P,off,I),Cnext=lm_cup(nextlambda,P,off,I),K=matker(C),rank=matrank(C),f=0,control=(s<6));
 if(control,
  jw_assert((s==2&&rank==9)||(s==4&&rank==79),"signed-family control rank");
  my(Q=mattranspose(K)*Cnext*K,h=matsize(K)[2]);
  for(j=1,h,if(Q[j,j]!=0,f=K[,j];break()));
  if(type(f)!="t_COL",for(j=1,h,for(k=j+1,h,if(Q[j,k]!=0,f=K[,j]+K[,k];break(2)))));
 ,
  jw_assert(rank==139,"complete target first radical");my(idx=0);
  for(j=1,#JC_KERNELS,if(JC_KERNELS[j][1]==s%4680,idx=j));jw_assert(idx>0,"registered scalar class");
  my(given=JC_KERNELS[idx]);f=vector(140,j,field[given[4][j][1]+1])~;
  jw_assert(lambda==apply(c->field[c+1],given[3][1])&&lambda2==apply(c->field[c+1],given[3][2]),"actual first and second coefficient calibration");
 );
 jw_assert(type(f)=="t_COL"&&C*f==vector(140,i,0*one)~,"nonzero exact first radical");
 my(slope=mattranspose(f)*Cnext*f,piv=matindexrank(C),rr=piv[1],cc=piv[2],inverse=lm_sub(C,rr,cc)^-1,F=jo_source(f,I,one),Fhat=jc_fourier(F,R,precision),WH=vector(8,m,jc_fourier(W[m],R,precision)),G=vector(9,j,vector(512,i,0*one)),G2=vector(9,j,vector(512,i,0*one)));
 for(branch=1,512,
  my(g=vector(9,j,if(j==1,one,0*one)));
  for(m=1,8,
   my(U=jc_cut(T^(4*(m-1))*WH[m][branch],precision),powers=vector(1+8\m));powers[1]=one;
   for(k=1,8\m,powers[k+1]=jc_cut(powers[k]*U,precision));
   g=vector(9,j,jc_cut(sum(k=0,(j-1)\m,E[k+1]*powers[k+1]*g[j-k*m]),precision));
  );
  for(j=1,9,G[j][branch]=g[j];G2[j][branch]=jc_cut(sum(k=1,j,g[k]*g[j-k+1]),precision));
 );
 my(cube1=vector(512,i,jc_cut((G[2][i]+O(T^precision))^3,precision)),cube2=vector(512,i,jc_cut((G[3][i]+O(T^precision))^3,precision)),units=if(control,[1,2,8],[1,2,4,5,7,8]));
 for(ui=1,#units,
  my(N=units[ui],n=N%3,u=N\3,base=if(n==1,G,G2),GN=vector(9,j,vector(512,i,jc_cut(base[j][i]+if(j>=4,u*cube1[i]*base[j-3][i],0)+if(j>=7,(u*cube2[i]+binomial(u,2)*cube1[i]^2)*base[j-6][i],0),precision))),sections=vector(9),transforms=vector(9),ord=0,value=0*one,gauges=List());
  sections[1]=F;transforms[1]=Fhat;
  for(k=1,8,
   my(bh=vector(512,i,jc_cut(sum(j=1,k,GN[j+1][i]*transforms[k-j+1][i]),precision)),A=jc_inverse(bh,IR,precision),ob=jo_obs(A,4*k,I),scalar=mattranspose(f)*ob);
   if(k==1,jw_assert(ob==vector(140,i,0*one)~,"initial section obstruction is zero"),
    if(scalar!=0,ord=k;value=scalar;break());
    my(rhs=-ob/n,coeff=inverse*vector(#rr,j,rhs[rr[j]])~,gauge=vector(140,j,0*one)~);
    for(j=1,#cc,gauge[cc[j]]=coeff[j]);jw_assert(C*gauge==rhs,"full cokernel solvability, not only scalar test");
    my(add=jo_source(gauge,I,one));sections[k]+=vector(512,i,T^(4*(k-1))*add[i]);transforms[k]=jc_fourier(sections[k],R,precision);
    my(addhat=jc_fourier(vector(512,j,T^(4*(k-1))*add[j]),R,precision));
    bh+=vector(512,i,jc_cut(GN[2][i]*addhat[i],precision));
    A=jc_inverse(bh,IR,precision);jw_assert(jo_obs(A,4*k,I)==vector(140,i,0*one)~,"corrected complete obstruction vanishes");listput(gauges,gauge);
   );
   sections[k+1]=vector(512,i,-jc_cut(A[i],4*k));jo_outside(sections[k+1],4*k);transforms[k+1]=jc_fourier(sections[k+1],R,precision);
  );
  if(control,
   if(N==2,jw_assert(ord==3&&value==slope&&slope!=0,"nonvacuous signed-family third departure"),jw_assert(ord==0,"actual signed-family sections survive all eight orders"));
  ,jw_assert(ord==0||ord>=3,"previous second scalar vanishes"));
  print("BOUNDED_SECTION_OBSTRUCTION exponent=",s," multiplier_mod9=",N," first_order=",ord," scalar_code=",mapget(codes,Str(value))," slope_code=",mapget(codes,Str(slope))," control=",control);
  my(last=if(ord,ord-1,8));listput(records,[s,N,control,ord,mapget(codes,Str(value)),mapget(codes,Str(slope)),vector(140,j,mapget(codes,Str(f[j]))),vector(last+1,j,jo_encode(sections[j],4*(j-1),codes))]);
 );
 print("BOUNDED_SECTION_PROGRESS exponent=",s," wall_ms=",getwalltime()-start);
);
write(out,"BOUNDED_SECTION_RESULTS := ",Vec(records),";");print("BOUNDED_SECTION_LIFTING_COMPLETED cases=",#records," wall_ms=",getwalltime()-start);
}
quit;
