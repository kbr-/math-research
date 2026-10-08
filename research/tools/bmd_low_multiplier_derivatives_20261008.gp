\\ Two rank-one restrictions on the actual low-family primitive modules.
default(parisize,256000000);
default(parisizemax,1500000000);
default(nbthreads,1);
T='T;
read("research/tools/bmd_root_jets.gp");
read("research/tools/bmd_low_multiplier_core_20261008.gp");
read("research/results/bmd-exception-low-multipliers-20261008/derivative-input.gp");
{
my(start=getwalltime(),a=ffgen(Mod(1,3)*(a^3+2*a+2),'a),one=a^0,field=vector(27,i,one*((i-1)%3)+a*(((i-1)\3)%3)+a^2*((i-1)\9)),codes=Map(),I=rootbasis(9,3),polys=vector(512),off=vector(512),rows=vector(6,s,vector(769)),total=0,out="research/results/bmd-exception-low-multipliers-20261008/derivatives.g",records=List());
for(i=1,27,mapput(codes,Str(field[i]),i-1));polys[1]=one;
for(S=1,511,my(bit=valuation(S,2));polys[S+1]=polys[S-2^bit+1]*(one+a^bit*T));
for(S=0,511,
 my(g=max(0,(hammingweight(S)-1)\2));off[S+1]=total;if(!g,next());
 my(B=matrix(g,g,i,j,if(3*i-j>=0,polcoef(polys[S+1],3*i-j,T),0)*one),v=matrix(1,g,i,j,(j==1)*one));
 for(s=1,6,v=lm_frob(v,3)*B;for(j=1,g,rows[s][total+j]=v[1,j]));total+=g;
);
for(ci=1,2,
 my(case=if(ci==1,LM_MODULES[2],LM_REFINED),b=case[1],k=if(ci==1,3,27),tail=if(ci==1,-1,0),degree=if(ci==1,9,27),vec=0);
 for(i=1,#LM_VECTORS,if(LM_VECTORS[i][1]==b&&LM_VECTORS[i][2]==k,vec=LM_VECTORS[i][4]));lm_assert(type(vec)=="t_VEC","exact failed vector");
 my(C=4*lm_cup(apply(x->field[x+1],vec),polys,off,I)+tail*lm_cup(rows[b+valuation(degree,3)],polys,off,I),K=lm_decode(case[7],field),E0=lm_decode(case[8],field),E1=lm_decode(case[9],field),h=matsize(K)[2],W=lm_sub(E0,[1..140],[1..h]),A=mattranspose(K)*C*W,u=matker(A),f0=W*u,g1=E1*u);
 lm_assert(matrank(A)==h-1&&matsize(u)==[h,1],"one actual radical");
 lm_assert(mattranspose(K)*C*f0==matrix(h,1)&&matrank(concat(K,f0))==h,"common physical left/right radical");
 if(case[4],lm_assert(lm_sub(g1,[141..140+case[4]],[1])==matrix(case[4],1),"first outside correction is regular"));
 my(f1=lm_sub(g1,[1..140],[1]),value=(mattranspose(f0)*C*f1)[1,1],code=mapget(codes,Str(value)));
 print("LOW_RELATIVE_DERIVATIVE base=",b," multiplier4 k=",k," order=",degree," rank=",h-1," needed=",h," value=",value," code=",code);
 listput(records,[b,k,degree,tail,lm_encode(C,codes),lm_encode(f0,codes),lm_encode(f1,codes),code]);
);
write(out,"LOW_DERIVATIVES := ",Vec(records),";");
print("LOW_RELATIVE_DERIVATIVES_COMPLETED cases2 wall_ms=",getwalltime()-start);
}
quit;
