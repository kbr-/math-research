\\ Test total digit closure for a smooth moving-mark elliptic family, not new n>=9 normality.
default(parisizemax,2000000000);
default(nbthreads,1);
read("research/tools/bmd_branch_state_core_20261007.gp");
read("research/tools/bmd_series_graph_core_20261007.gp");
set_source()={
 ZZ=vector(CC,c,-OO/AA[COORD[c][2]]);
 my(ell=vector(NN,i,OO+AA[i]*T+O(T^13)),roots=apply(sqrt,ell));
 for(i=1,NN,if(polcoef(roots[i],0,T)!=OO,roots[i]=-roots[i]);assert(polcoef(roots[i],0,T)==OO && valuation(roots[i]^2-ell[i],T)>=13,"root normalization"));
 CH=vector(8,S,prod(i=1,NN,if(bittest(S-1,i-1),roots[i],OO)))
};
{
T='x;XPAR='u;a=ffgen(Mod(1,3)*('a^2+'a+2),'a);OO=a^0;NN=3;PP=3;BB=4;CC=12;HH=1;GG=1;PREC=2;WP=6;MAXSTATES=256;GRAPH_BUDGET_MS=240000;
my(coords=List());for(S=0,7,for(i=1,NN,if(!bittest(S,i-1),listput(coords,[S,i]))));COORD=Vec(coords);
AA=[2*OO,a+2,2*a+1];my(constants=AA);
assert(#Set(AA)==3 && !setsearch(Set(AA),0*OO),"distinct nonzero labels");
set_source();my(k1=matsize(matker(source_jet(1,4)))[2],k3=matsize(matker(source_jet(3,12)))[2]);
print("CONSTANT_CALIBRATION labels=",AA," kernel_d1=",k1," kernel_d3=",k3," pair_sum=",AA[1]*AA[2]+AA[1]*AA[3]+AA[2]*AA[3]);
AA=apply(t->t/(OO+t*XPAR),constants);set_source();
RR=vector(CC,c,my(S=COORD[c][1],i=COORD[c][2]);AA[i]*prod(h=1,NN,if(h==i||bittest(S,h-1),OO,OO+AA[h]*ZZ[c])));
CCOEF=chop(matrix(CC,3,c,r,ZZ[c]^(r-1)),WP);
HCOEF=chop(matrix(CC,3,c,r,if(r==1,0*OO,RR[c]^(-1)*(r-1)*ZZ[c]^(r-2))),WP);
assert(mval(CCOEF)>=0 && mval(HCOEF)>=0,"smooth coefficient maps integral");
my(baseframes=vector(3*CC),basecache=Map());gettime();
for(j=0,2,for(delta=0,CC-1,my(d=NN-j,L=max(0,BB*d-delta),key=[d,L],U);if(mapisdefined(basecache,key),U=mapget(basecache,key),U=exact_frame(source_eval(d)*matker(source_jet(d,L)));mapput(basecache,key,U));assert(matsize(U)[2]==max(0,BB*d+1-GG-L),"moving base dimension");baseframes[j*CC+delta+1]=chop(U,PREC)));
print("BASE_SOURCE_KERNELS=",#basecache," CPU_MS=",gettime());
INVCACHE=Map();LOCALCACHE=Map();INVS=0;INVHITS=0;PICK_FALLBACKS=0;LOCALS=0;LOCALHITS=0;INVMS=0;RESMS=0;EXCHANGES=0;NEGATIVE=0;STARTMS=getwalltime();
my(base=[0,baseframes],states=List([base]),xs=List([0]),seen=Map(),edges=List(),at=1,stop=0);mapput(seen,Str(base),1);
print("SMOOTH_GRAPH precision=",PREC," state_cap=",MAXSTATES," time_budget_ms=240000");print("BASE_STATE = ",base);
while(at<=#states && !stop,
 for(digit=0,2,
  my(start=getwalltime(),result=edge(states[at],digit),elapsed=getwalltime()-start);
  if(!result[1],print("CERTIFICATE_REFUSED source=",at," representative_x=",xs[at]," digit=",digit," reason=",result," wall_ms=",elapsed);stop=1;break);
  if(at==1 && digit==0,assert(result[2]==base,"zero-digit source mismatch"));
  my(key=Str(result[2]),dest);
  if(mapisdefined(seen,key),dest=mapget(seen,key),if(#states>=MAXSTATES,print("STATE_CAP_REACHED; graph incomplete");stop=1;break);listput(states,result[2]);listput(xs,3*xs[at]+digit);dest=#states;mapput(seen,key,dest);print("STATE ",dest," representative_x=",xs[dest]," DATA = ",result[2]));
  listput(edges,[at,digit,dest,result[3]]);print("EDGE = ",[at,digit,dest,result[3]]," WALL_MS=",elapsed);
  if(elapsed>10000,print("STOP_SCALING: edge exceeds10s");stop=1;break)
 );at++
);
print("GRAPH_RESULT states=",#states," edges=",#edges," closed=",!stop && at>#states," elapsed_ms=",getwalltime()-STARTMS," inverses=",INVS," inverse_cache_hits=",INVHITS," local_transitions=",LOCALS," local_cache_hits=",LOCALHITS," inverse_ms=",INVMS," residual_ms=",RESMS," pivot_fallbacks=",PICK_FALLBACKS," corruption_detected=",NEGATIVE);
print("SMOOTH_GRAPH_COMPLETED; only total certified coverage proves all-degree normality")
}
quit;
