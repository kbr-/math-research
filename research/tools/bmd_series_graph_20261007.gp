\\ Residual-certified graph pilot; shared kernel extracted without changing its checks.
default(parisizemax,2000000000);
default(nbthreads,1);
read("research/tools/bmd_series_graph_core_20261007.gp");
{
XPAR='u;NN=3;PP=3;OO=Mod(1,3);BB=4;CC=12;GG=1;PREC=16;WP=3*PREC;MAXSTATES=64;
my(AA=[OO,OO*XPAR,OO*(XPAR^2+XPAR+2)],coords=List());for(S=0,7,for(i=1,NN,if(!bittest(S,i-1),listput(coords,[S,i]))));my(COORD=Vec(coords),ZZ=vector(CC,c,-OO/AA[COORD[c][2]]),RR=vector(CC,c,my(S=COORD[c][1],i=COORD[c][2]);AA[i]*prod(h=1,NN,if(h==i||bittest(S,h-1),OO,OO+AA[h]*ZZ[c]))),AH=0);
for(c=1,CC,for(r=1,2,AH=max(AH,-valuation(RR[c]^(-1)*r*ZZ[c]^(r-1),XPAR))));
CCOEF=matrix(CC,3,c,r,truncate(XPAR^max(0,-2*valuation(ZZ[c],XPAR))*ZZ[c]^(r-1)+O(XPAR^WP)));
HCOEF=matrix(CC,3,c,r,if(r==1,0*OO,truncate(XPAR^AH*RR[c]^(-1)*(r-1)*ZZ[c]^(r-2)+O(XPAR^WP))));
my(lines=readstr("research/results/bmd-exception-adic-closure-20261007/canonical-pilot.txt"),base=0,reference=0);
for(i=1,#lines,my(z=strsplit(lines[i],"BASE_STATE = "));if(#z==2,base=eval(z[2]));z=strsplit(lines[i]," DATA = ");if(#z==2 && eval(strsplit(z[1]," representative_x=")[2])==1,reference=eval(z[2])));
assert(base!=0 && reference!=0,"missing independently checked reference states");
base[2]=apply(U->chop(U,PREC),base[2]);reference[2]=apply(U->chop(U,PREC),reference[2]);
for(i=1,#base[2],my(U=base[2][i],k=matsize(U)[2]);if(k,assert(submat(U,canonical_rows(U),[1..k])==matid(k),"base chart")));
INVCACHE=Map();LOCALCACHE=Map();INVS=0;INVHITS=0;PICK_FALLBACKS=0;LOCALS=0;LOCALHITS=0;INVMS=0;RESMS=0;EXCHANGES=0;NEGATIVE=0;STARTMS=getwalltime();
my(states=List([base]),xs=List([0]),seen=Map(),edges=List(),at=1,stop=0,reference_checks=0);mapput(seen,Str(base),1);
print("SERIES_GRAPH precision=",PREC," product_precision=",WP," cap=",MAXSTATES," time_budget_ms=120000; exact residual certificates");print("BASE_STATE = ",base);
while(at<=#states && !stop,
 for(a=0,2,
  my(start=getwalltime(),result=edge(states[at],a),elapsed=getwalltime()-start);
  if(!result[1],print("CERTIFICATE_REFUSED source=",at," representative_x=",xs[at]," digit=",a," reason=",result," wall_ms=",elapsed);stop=1;break);
  if(at==1 && a<=1,assert(result[2]==if(a==0,base,reference),"rational-reference state mismatch");reference_checks+=3*CC);
  my(key=Str(result[2]),dest);
  if(mapisdefined(seen,key),dest=mapget(seen,key),if(#states>=MAXSTATES,print("STATE_CAP_REACHED; graph incomplete");stop=1;break);listput(states,result[2]);listput(xs,3*xs[at]+a);dest=#states;mapput(seen,key,dest);print("STATE ",dest," representative_x=",xs[dest]," DATA = ",result[2]));
  listput(edges,[at,a,dest,result[3]]);print("EDGE = ",[at,a,dest,result[3]]," WALL_MS=",elapsed);
  if(elapsed>10000,print("STOP_SCALING: edge exceeds10s");stop=1;break)
 );at++
);
print("GRAPH_RESULT states=",#states," edges=",#edges," closed=",!stop && at>#states," elapsed_ms=",getwalltime()-STARTMS," inverses=",INVS," inverse_cache_hits=",INVHITS," local_transitions=",LOCALS," local_cache_hits=",LOCALHITS," candidate_inverse_ms=",INVMS," residual_check_ms=",RESMS," exchanges=",EXCHANGES," reference_frame_checks=",reference_checks," corruption_detected=",NEGATIVE," pivot_fallbacks=",PICK_FALLBACKS);
print("SERIES_GRAPH_COMPLETED; closed=false is not a complete normality certificate")
}
quit;
