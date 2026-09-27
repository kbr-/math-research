-- Close only the residual relations inside the already verified upper module.
-- Input matrices come from the completed upper calculation; no source kernels
-- or universal-column construction is repeated. Keep syzygies in the same CAS
-- process. Print final minimal data, not arbitrary 218-column lift matrices.
residualClock=cpuTime();
R=QQ[A,B,C,D];
packet=separate("\n",get "research/results/cube-triple-triple-source-relations-20260927/upper-presentation.txt");
readTag=tag->matrix value substring(#tag,first select(packet,l->substring(0,#tag,l)==tag));
resUpper=readTag "UPPER_RELATIONS=";
resCore=readTag "CORE_COORDINATES=";
resConn=readTag "CONNECTION_COORDINATES=";
alpha=(A-C)/3;leftSlope=alpha+2;rightSlope=alpha-2;
drift={3*B+2*leftSlope*A,3*leftSlope*B-2*A^2/3,
       3*D+2*rightSlope*C,3*rightSlope*D-2*C^2/3};
delta=f->sum(toList(0..3),i->drift#i*diff(R_i,f));
resCon=vv->matrix apply(entries vv,row->apply(row,f->delta f))+resConn*vv;
resGB=gb(resUpper,Syzygies=>true);
resSyz=syz resGB;
assert(resUpper*resSyz==0);
<< "UPPER_SYZYGIES=" << numcols resSyz << " CPU=" << cpuTime()-residualClock << endl << flush;
resRels=gens gb(resSyz|resCore);
<< "INITIAL_RELATIONS=" << numcols resRels << " DIMENSION=" << dim coker resRels
   << " CPU=" << cpuTime()-residualClock << endl << flush;
resStable=false;resRound=0;
while not resStable and resRound<30 do (
    resExtra=resCon(resRels)%gb resRels;
    if resExtra==0 then resStable=true else resRels=gens gb(resRels|resExtra);
    resRound=resRound+1;
    << "CLOSURE_ROUND=" << resRound << " RELATIONS=" << numcols resRels
       << " STABLE=" << resStable << " CPU=" << cpuTime()-residualClock << endl << flush;
);
assert(resStable);
resModule=prune coker resRels;
assert(dim resModule==0);
<< "FULL_RESIDUAL_LENGTH=" << numcols basis resModule << endl << flush;
resSigma=(A+C+3)*(A+C+12)*(A+C+24);
resOriginRels=saturate(image presentation resModule,ideal resSigma);
resOrigin=prune(coker gens resOriginRels);
assert(dim resOrigin==0);
<< "ORIGIN_LENGTH=" << numcols basis resOrigin << endl;
<< "ORIGIN_ANNIHILATOR=" << toString gens annihilator resOrigin << endl;
<< "ORIGIN_PRESENTATION=" << toString entries presentation resOrigin << endl;
<< "ORIGIN_BASIS=" << toString entries basis resOrigin << endl;
<< "COMPLETE cpu=" << cpuTime()-residualClock << endl << flush;
exit 0;
