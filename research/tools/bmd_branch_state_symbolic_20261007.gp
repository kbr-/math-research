\\ One-parameter exact arithmetic benchmark, not a full generic exception computation.
default(parisizemax,2000000000);
default(nbthreads,1);
setrand(20261007);
read("research/tools/bmd_branch_state_core_20261007.gp");
{
T='x;XPAR='u;
NN=3;PP=3;OO=Mod(1,3);BB=4;CC=12;HH=1;
AA=[OO,OO*XPAR,OO*(XPAR^2+XPAR+2)];
my(coords=List());for(S=0,7,for(i=1,NN,if(!bittest(S,i-1),listput(coords,[S,i]))));COORD=Vec(coords);
ZZ=vector(CC,c,-OO/AA[COORD[c][2]]);
RR=vector(CC,c,my(S=COORD[c][1],i=COORD[c][2]);AA[i]*prod(h=1,NN,if(h==i||bittest(S,h-1),OO,OO+AA[h]*ZZ[c])));
my(prec=29,ell=vector(NN,i,OO+AA[i]*T+O(T^prec)),roots=apply(sqrt,ell));
for(i=1,NN,assert(valuation(roots[i]^2-ell[i],T)>=prec,"root equations"));
CH=vector(8,S,prod(i=1,NN,if(bittest(S-1,i-1),roots[i],OO)));
CACHE=Map();CALLS=0;MAXCOLS=0;MAXDEG=0;MEASURE_SYMBOLIC=1;MAX_COEFF_DEGREE=0;
print("FIELD F3(u); slopes=[1,u,u^2+u+2]; exact rational-function operations");
my(degrees=[7,31,127],lastms=1,lastd=7);
for(i=1,#degrees,
 my(d=degrees[i],estimate=if(i==1,0,max(1,lastms)*(d/lastd)^2));
 print("SIZING d=",d," quadratic_extrapolation_ms=",estimate);
 if(i>1 && estimate>10000,print("STOP_SCALING: estimate exceeds ten seconds; no larger query attempted");break);
 my(before=CALLS);gettime();my(U=branch_state(d,4*d),ms=gettime());
 if(i==1,my(K=matker(source_jet(d,4*d)),V=source_eval(d)*K);assert(matsize(K)[2]==matsize(U)[2] && matrank(matconcat([U,V]))==matsize(U)[2],"symbolic direct control"));
 print("SYMBOLIC_QUERY d=",d," kernel_dimension=",matsize(U)[2]," new_states=",CALLS-before," max_columns=",MAXCOLS," max_stored_coefficient_degree=",MAX_COEFF_DEGREE," cpu_ms=",ms);
 lastms=ms;lastd=d
);
print("SYMBOLIC_BRANCH_STATE_COMPLETED: rational-family evaluation only, not a generic exception set.")
}
quit;
