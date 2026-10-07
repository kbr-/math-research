\\ Parity-aware reversed-coordinate graph, using the checked residual kernel.
default(parisizemax,2000000000);
default(nbthreads,1);
read("research/tools/bmd_branch_state_core_20261007.gp");
read("research/tools/bmd_series_graph_core_20261007.gp");
weighted_source(d,L)={my(V=source_eval(d)*matker(source_jet(d,L)));matrix(CC,matsize(V)[2],c,j,AA[COORD[c][2]]^floor((d-hammingweight(COORD[c][1]))/2)*V[c,j])};
set_type(t)={CCOEF=TABLES[t+1][1];HCOEF=TABLES[t+1][2];};
reset_caches()={INVCACHE=Map();LOCALCACHE=Map();INVS=0;INVHITS=0;PICK_FALLBACKS=0;LOCALS=0;LOCALHITS=0;INVMS=0;RESMS=0;EXCHANGES=0;NEGATIVE=0;};
edge_reversed(state,a)={
 my(nf=min(2,3*state[1]+a),ep=(state[2]+a)%2,out=vector(3*CC),records=List(),frames=state[3]);
 for(j=0,2,
  my(typ=(NN+3*state[2]+a-j)%6);set_type(typ);
  for(delta=0,CC-1,
   my(ch=vector(3,r,my(jp=-floor((a-j-2*(r-1))/3),dp=BB*NN+BB*floor((a-j-2*(r-1))/3)-ceil((BB*(NN+a-j)-delta-(r-1))/3));if(dp<0,matrix(CC,0,i,k,0*OO),frames[jp*CC+dp+1])));
   my(d=NN+nf-j,L=BB*d-delta,k=max(0,BB*d+1-GG-max(L,0)),result=local_step(ch,k));
   if(!result[1],return([0,j,delta,typ,result]));out[j*CC+delta+1]=result[2];listput(records,concat([j,delta,typ],result[3]));
   if(getwalltime()-STARTMS>120000,return([0,j,delta,typ,"PILOT_TIME_BUDGET"]))
  )
 );[1,[nf,ep,out],Vec(records)]
};
{
T='x;XPAR='u;NN=3;PP=3;OO=Mod(1,3);BB=4;CC=12;HH=1;GG=1;PREC=16;WP=3*PREC;MAXSTATES=64;
AA=[OO,OO*XPAR,OO*(XPAR^2+XPAR+2)];my(coords=List());for(S=0,7,for(i=1,NN,if(!bittest(S,i-1),listput(coords,[S,i]))));COORD=Vec(coords);ZZ=vector(CC,c,-OO/AA[COORD[c][2]]);
my(ell=vector(NN,i,OO+AA[i]*T+O(T^13)),roots=apply(sqrt,ell));for(i=1,NN,assert(polcoef(roots[i],0,T)==OO && valuation(roots[i]^2-ell[i],T)>=13,"normalized roots"));CH=vector(8,S,prod(i=1,NN,if(bittest(S-1,i-1),roots[i],OO)));
TABLES=vector(6,tt,
 my(d=tt-1+6,C=matrix(CC,3,c,r,my(s=hammingweight(COORD[c][1]),i=COORD[c][2],h=(floor((d-s)/2)+NN-s-(r-1))%3);(-1)^(r-1)*AA[i]^h),H=matrix(CC,3,c,r,my(S=COORD[c][1],s=hammingweight(S),i=COORD[c][2],h=(floor((d-s)/2)+NN-s-(r-1))%3,Delta=prod(t=1,NN,if(t==i||bittest(S,t-1),OO,AA[i]-AA[t])));if(r==1,0*OO,(r-1)*(-1)^(r-2)*AA[i]^(h-1)/Delta)),ac=max(0,-mval(C)),ah=max(0,-mval(H)));
 [chop(XPAR^ac*C,WP),chop(XPAR^ah*H,WP),ac,ah]
);
my(parity_checks=0);for(x=0,3,for(a=0,2,for(j=0,2,assert((NN+3*x+a-j)%6==(NN+3*(x%2)+a-j)%6,"degree type");assert((3*x+a)%2==((x%2)+a)%2,"parity update");parity_checks+=2)));
assert((NN+3+0)%6!=(NN+0)%6,"missing-parity negative control");
reset_caches();my(empty=vector(3,r,matrix(CC,0,i,j,0*OO)));set_type(0);my(z=local_step(empty,0));assert(z[1],"empty kernel type0");set_type(1);z=local_step(empty,0);assert(z[1] && LOCALS==2 && LOCALHITS==0,"coefficient tables omitted from cache key");set_type(0);z=local_step(empty,0);assert(LOCALHITS==1,"identical operator cache reuse");
print("PARITY_CHECKS=",parity_checks," distinct_coefficient_cache_entries=",LOCALS," repeated_operator_hit=",LOCALHITS);
my(baseframes=vector(3*CC),basecache=Map());gettime();
for(j=0,2,for(delta=0,CC-1,my(d=NN-j,L=max(0,BB*d-delta),key=[d,L],U);if(mapisdefined(basecache,key),U=mapget(basecache,key),U=exact_frame(weighted_source(d,L));mapput(basecache,key,U));assert(matsize(U)[2]==max(0,BB*d+1-GG-L),"weighted base dimension");baseframes[j*CC+delta+1]=chop(U,PREC)));
print("BASE_SOURCE_KERNELS=",#basecache," CPU_MS=",gettime());
reset_caches();STARTMS=getwalltime();my(base=[0,0,baseframes],states=List([base]),xs=List([0]),seen=Map(),edges=List(),at=1,stop=0);mapput(seen,Str(base),1);
print("REVERSED_GRAPH precision=",PREC," types=6 state_cap=",MAXSTATES," time_budget_ms=120000");print("BASE_STATE = ",base);
while(at<=#states && !stop,
 for(a=0,2,
  my(start=getwalltime(),result=edge_reversed(states[at],a),elapsed=getwalltime()-start);
  if(!result[1],print("CERTIFICATE_REFUSED source=",at," representative_x=",xs[at]," digit=",a," reason=",result," wall_ms=",elapsed);stop=1;break);
  assert(result[2][2]==(3*xs[at]+a)%2,"result parity");
  if(at==1 && a==0,assert(result[2]==base,"weighted zero-digit source mismatch"));
  my(key=Str(result[2]),dest);
  if(mapisdefined(seen,key),dest=mapget(seen,key),if(#states>=MAXSTATES,print("STATE_CAP_REACHED; graph incomplete");stop=1;break);listput(states,result[2]);listput(xs,3*xs[at]+a);dest=#states;mapput(seen,key,dest);print("STATE ",dest," representative_x=",xs[dest]," DATA = ",result[2]));
  listput(edges,[at,a,dest,result[3]]);print("EDGE = ",[at,a,dest,result[3]]," WALL_MS=",elapsed);
  if(elapsed>10000,print("STOP_SCALING: edge exceeds10s");stop=1;break)
 );at++
);
print("GRAPH_RESULT states=",#states," edges=",#edges," closed=",!stop && at>#states," elapsed_ms=",getwalltime()-STARTMS," inverses=",INVS," inverse_cache_hits=",INVHITS," local_transitions=",LOCALS," local_cache_hits=",LOCALHITS," inverse_ms=",INVMS," residual_ms=",RESMS," pivot_fallbacks=",PICK_FALLBACKS," corruption_detected=",NEGATIVE);
print("REVERSED_GRAPH_COMPLETED; only total certified coverage proves all-degree normality")
}
quit;
