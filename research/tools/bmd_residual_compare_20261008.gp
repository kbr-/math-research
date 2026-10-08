\\ All order-27 return competitions on the complete residual-reference primitive modules.
default(parisize,256000000);
default(parisizemax,1500000000);
default(nbthreads,1);
T='T;
read("research/tools/bmd_root_jets.gp");
read("research/tools/bmd_low_multiplier_core_20261008.gp");
read(getenv("BMD_RESIDUAL_INPUT"));
{
my(start=getwalltime(),a=ffgen(Mod(1,3)*(a^3+2*a+2),'a),one=a^0,field=vector(27,i,one*((i-1)%3)+a*(((i-1)\3)%3)+a^2*((i-1)\9)),codes=Map(),I=rootbasis(9,3),polys=vector(512),off=vector(512),rows=vector(6,s,vector(769)),total=0,out=getenv("BMD_RESIDUAL_COMPARE_OUT"),records=List());
for(i=1,27,mapput(codes,Str(field[i]),i-1));polys[1]=one;
for(S=1,511,my(bit=valuation(S,2));polys[S+1]=polys[S-2^bit+1]*(one+a^bit*T));
for(S=0,511,
 my(g=max(0,(hammingweight(S)-1)\2));off[S+1]=total;if(!g,next());
 my(B=matrix(g,g,i,j,if(3*i-j>=0,polcoef(polys[S+1],3*i-j,T),0)*one),v=matrix(1,g,i,j,(j==1)*one));
 for(s=1,6,v=lm_frob(v,3)*B;for(j=1,g,rows[s][total+j]=v[1,j]));total+=g;
);
for(ci=1,#RM_MODULES,
 my(case=RM_MODULES[ci],mult=case[2],amax=vecmax(apply(x->x[1],case[6])));
 lm_assert(case[5]==1&&amax<27,"complete module with strict comparison gap");
 my(K=lm_decode(case[7],field),h=matsize(K)[2],E0=lm_decode(case[8],field),E1=lm_decode(case[9],field),W=lm_sub(E0,[1..140],[1..h]));
 lm_assert(matrank(concat(K,W))==h,"actual positive and negative primitive specializations");
 for(vi=1,#RM_VECTORS,for(u=-1,1,
  my(v=RM_VECTORS[vi],C=mult*lm_cup(apply(x->field[x+1],v[4]),polys,off,I)+u*lm_cup(rows[6],polys,off,I),A=mattranspose(K)*C*W,r=matrank(A),der=-1,f0=matrix(140,0),f1=f0);
  if(r==h-1,
   my(rad=matker(A),g1=E1*rad);f0=W*rad;
   lm_assert(mattranspose(K)*C*f0==matrix(h,1),"physical radical");
   if(case[4],lm_assert(lm_sub(g1,[141..140+case[4]],[1])==matrix(case[4],1),"regular first correction"));
   f1=lm_sub(g1,[1..140],[1]);der=mapget(codes,Str((mattranspose(f0)*C*f1)[1,1]));
  );
  print("RESIDUAL_COMPARISON multiplier=",mult," k=",v[2]," tail=",u," rank=",r," needed=",h," derivative_code=",der);
  listput(records,[mult,v[2],u,h,r,der,lm_encode(C,codes),lm_encode(A,codes),lm_encode(f0,codes),lm_encode(f1,codes)]);
 ));
);
write(out,"RESIDUAL_COMPARISONS := ",Vec(records),";");
print("RESIDUAL_COMPARISONS_COMPLETED cases=",#records," wall_ms=",getwalltime()-start);
}
quit;
