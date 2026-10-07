\\ Lift base frames from the original source, then test the refused path at N=16,17.
default(parisizemax,2000000000);
default(nbthreads,1);
read("research/tools/bmd_branch_state_core_20261007.gp");
read("research/tools/bmd_series_graph_core_20261007.gp");
setup_precision(N)={
 PREC=N;WP=3*N;
 CCOEF=matrix(CC,3,c,r,truncate(XPAR^max(0,-2*valuation(ZZ[c],XPAR))*ZZ[c]^(r-1)+O(XPAR^WP)));
 HCOEF=matrix(CC,3,c,r,if(r==1,0*OO,truncate(XPAR^AH*RR[c]^(-1)*(r-1)*ZZ[c]^(r-2)+O(XPAR^WP))));
 INVCACHE=Map();LOCALCACHE=Map();INVS=0;INVHITS=0;PICK_FALLBACKS=0;LOCALS=0;LOCALHITS=0;INVMS=0;RESMS=0;EXCHANGES=0;NEGATIVE=0;STARTMS=getwalltime()
};
{
T='x;XPAR='u;NN=3;PP=3;OO=Mod(1,3);BB=4;CC=12;HH=1;GG=1;
AA=[OO,OO*XPAR,OO*(XPAR^2+XPAR+2)];my(coords=List());for(S=0,7,for(i=1,NN,if(!bittest(S,i-1),listput(coords,[S,i]))));COORD=Vec(coords);
ZZ=vector(CC,c,-OO/AA[COORD[c][2]]);RR=vector(CC,c,my(S=COORD[c][1],i=COORD[c][2]);AA[i]*prod(h=1,NN,if(h==i||bittest(S,h-1),OO,OO+AA[h]*ZZ[c])));AH=0;for(c=1,CC,for(r=1,2,AH=max(AH,-valuation(RR[c]^(-1)*r*ZZ[c]^(r-1),XPAR))));
my(ell=vector(NN,i,OO+AA[i]*T+O(T^13)),roots=apply(sqrt,ell));for(i=1,NN,assert(valuation(roots[i]^2-ell[i],T)>=13,"root equations"));CH=vector(8,S,prod(i=1,NN,if(bittest(S-1,i-1),roots[i],OO)));
my(exactbase=vector(3*CC),cache=Map());gettime();
for(j=0,2,for(delta=0,CC-1,
 my(d=NN-j,L=max(0,BB*d-delta),key=[d,L],U);
 if(mapisdefined(cache,key),U=mapget(cache,key),U=exact_frame(source_eval(d)*matker(source_jet(d,L)));mapput(cache,key,U));
 assert(matsize(U)[2]==max(0,BB*d+1-GG-L),"exact base rank");exactbase[j*CC+delta+1]=U
));print("EXACT_BASE_COMPONENTS=",#exactbase," distinct_source_kernels=",#cache," CPU_MS=",gettime());
my(lines=readstr("research/results/bmd-exception-series-kernel-20261007/series-graph.txt"),refs=Map());
for(i=1,#lines,my(z=strsplit(lines[i],"BASE_STATE = "));if(#z==2,mapput(refs,0,eval(z[2])));z=strsplit(lines[i]," DATA = ");if(#z==2,my(x=eval(strsplit(z[1]," representative_x=")[2]));if(x==1||x==5,mapput(refs,x,eval(z[2])))));
my(precisions=[16,17]);for(ni=1,#precisions,my(N=precisions[ni]);
 setup_precision(N);my(state=[0,apply(U->chop(U,N),exactbase)],x=0,refchecks=0,ok=1);
 assert([state[1],apply(U->chop(U,16),state[2])]==mapget(refs,0),"base lift disagrees with checked source");refchecks+=36;
 print("LIFT_BASE precision=",N," DATA = ",state);
 for(t=1,2,
  my(a=if(t==1,1,2),start=getwalltime(),result=edge(state,a));
  if(!result[1],print("PREFIX_REFUSED precision=",N," x=",x," digit=",a," reason=",result);ok=0;break);
  state=result[2];x=3*x+a;
  assert([state[1],apply(U->chop(U,16),state[2])]==mapget(refs,x),"prefix lift disagrees with saved frames");refchecks+=36;
  print("LIFT_EDGE precision=",N," x=",x," certificate=",result[3]," wall_ms=",getwalltime()-start);print("LIFT_STATE precision=",N," x=",x," DATA = ",state)
 );
 if(ok,
  my(ch=vector(3,r,my(jp=-floor((-2*(r-1))/3),dp=BB*NN+BB*floor((-2*(r-1))/3)-ceil((BB*NN-9-(r-1))/3));state[2][jp*CC+dp+1]),target=local_step(ch,9));
  print("TARGET precision=",N," parent_degree=18 jet_length=63 result=",if(target[1],[1,target[3]],target));
  if(target[1],my(start=getwalltime(),result=edge(state,0));if(result[1],print("LIFT_EDGE precision=",N," x=15 certificate=",result[3]," wall_ms=",getwalltime()-start);print("LIFT_STATE precision=",N," x=15 DATA = ",result[2]),print("NEXT_COMPONENT_REFUSED precision=",N," reason=",result)))
 );
 print("LIFT_SUMMARY precision=",N," reference_components=",refchecks," elapsed_ms=",getwalltime()-STARTMS," inverse_candidates=",INVS," inverse_cache_hits=",INVHITS," local_transitions=",LOCALS," local_cache_hits=",LOCALHITS," corruption_detected=",NEGATIVE," pivot_fallbacks=",PICK_FALLBACKS)
);
print("PRECISION_LIFT_COMPLETED; path controls only, not a total graph")
}
quit;
