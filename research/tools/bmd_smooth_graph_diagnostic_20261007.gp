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
UNIT_NEWTON=0;T='x;XPAR='u;a=ffgen(Mod(1,3)*('a^2+'a+2),'a);OO=a^0;NN=3;PP=3;BB=4;CC=12;HH=1;GG=1;PREC=2;WP=6;MAXSTATES=256;
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
INVCACHE=Map();LOCALCACHE=Map();INVS=0;INVHITS=0;PICK_FALLBACKS=0;LOCALS=0;LOCALHITS=0;INVMS=0;RESMS=0;EXCHANGES=0;NEGATIVE=0;STARTMS=getwalltime();

my(lines=readstr("research/results/bmd-exception-reversed-graph-20261007/smooth-graph.txt"),st=[]);
for(i=1,#lines,if(strsplit(lines[i],"STATE 19 representative_x=18 DATA = ")!=[lines[i]],st=eval(strsplit(lines[i]," DATA = ")[2])));
assert(#st,"missing refused source");my(ans=edge(st,2));print("REFUSAL_DIAGNOSTIC=",if(ans[1],[1,ans[3]],ans));my(Y=LAST_FAILED_IMAGE,pv=matindexrank(chop(Y,1)),A=submat(Y,pv[1],pv[2]));print("UNIT_PIVOT size=",matsize(A)," det_val=",valuation(matdet(A),XPAR));
for(t=1,3,my(work=WP*2^t,Q);iferr(Q=matsolve(matrix(matsize(A)[1],matsize(A)[2],i,j,A[i,j]+O(XPAR^work)),matid(matsize(A)[1])),E,print("SOLVER_ERROR=",E);next);Q=chop(Q,WP);print("CANDIDATE work=",work," residual=",inverse_residual(A,Q)));
print("SMOOTH_REFUSAL_DIAGNOSTIC_COMPLETED")
}
quit;
