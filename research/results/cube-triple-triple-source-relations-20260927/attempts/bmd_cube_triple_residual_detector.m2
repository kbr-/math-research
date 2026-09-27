-- The complete residual has length16, top dimension4 and m^5=0.
-- Four source classes form its top, first visible at quadratic order.
-- Test the specific hypothesis that the seventh transverse power detects all,
-- with the sixth power as the minimality control. Max QQ ambient4*210=840.
-- Both quotients use one seventh-power Artin ring and the now-certified complete
-- twelve-column core presentation. No whole polynomial closure is repeated.
detectorClock=cpuTime();
R=QQ[A,B,C,D];
dcSource=separate("\n",get "research/results/cube-triple-triple-source-relations-20260927/source-certificate.txt");
dcCore=separate("\n",get "research/results/cube-triple-triple-transverse-residual-20260927/deflation-certificate.txt");
dcRead=(ls,tag)->matrix value substring(#tag,first select(ls,l->substring(0,#tag,l)==tag));
dcRel=dcRead(dcCore,"CORE_RAW=");
dcSel=dcRead(dcSource,"SELECTED_LIFTS=");
dcArt=R/((ideal gens R)^7);
assert(numcols basis dcArt==210);
dcRel7=sub(dcRel,dcArt);dcUpper7=dcRel7|sub(dcSel,dcArt);
dcFull=coker dcRel7;dcUpper=coker dcUpper7;
dcFull7=numcols basis dcFull;dcQuot7=numcols basis dcUpper;
<< "POWER=7 FULL=" << dcFull7 << " UPPER=" << dcQuot7
   << " RESIDUAL_IMAGE=" << dcFull7-dcQuot7 << " CPU=" << cpuTime()-detectorClock << endl << flush;
dcTrunc=gens((ideal gens dcArt)^6*dcArt^4);
dcFull6=numcols basis coker(dcRel7|dcTrunc);
dcQuot6=numcols basis coker(dcUpper7|dcTrunc);
<< "POWER=6 FULL=" << dcFull6 << " UPPER=" << dcQuot6
   << " RESIDUAL_IMAGE=" << dcFull6-dcQuot6 << endl;
assert(dcFull7>=dcQuot7 and dcFull7-dcQuot7<=16);
assert(dcFull6>=dcQuot6 and dcFull6-dcQuot6<=dcFull7-dcQuot7);
<< "COMPLETE cpu=" << cpuTime()-detectorClock << endl << flush;
exit 0;
