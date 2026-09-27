-- Use the actual tripleSource to remove the unknown residual before eliminating.
-- Read the successful full tripleSource and tripleCore connection; do not rebuild kernels.
-- An invariant span of the tripleCore columns and actual tripleSource is exactly the tripleUpper
-- relation module: it contains the initial cyclic marker, and its generators
-- already belong to the true tripleUpper relation module. No finite-prefix equality
-- for the original full defect is assumed.
upperClock=cpuTime();
-- The first run printed all source coordinates (140 MB of captured output).
-- They are retained losslessly in its archive; set true only to reproduce that
-- redundant lift dump. Membership is already checked by exact remainders.
upperEmitFullSourceCoordinates=false;
R=QQ[A,B,C,D];
sourceLines=separate("\n",get "research/results/cube-triple-triple-source-relations-20260927/source-certificate.txt");
priorLines=separate("\n",get "research/results/cube-triple-triple-transverse-residual-20260927/deflation-certificate.txt");
readMatrix=(lines,tag)->matrix value substring(#tag,first select(lines,l->substring(0,#tag,l)==tag));
tripleSource=readMatrix(sourceLines,"SOURCE_MATRIX=");
tripleCore=readMatrix(priorLines,"CORE_RAW=");
mat=readMatrix(sourceLines,"CORE_CONNECTION=");
selected=readMatrix(sourceLines,"SELECTED_LIFTS=");
alpha=(A-C)/3;leftSlope=alpha+2;rightSlope=alpha-2;
drift={3*B+2*leftSlope*A,3*leftSlope*B-2*A^2/3,
       3*D+2*rightSlope*C,3*rightSlope*D-2*C^2/3};
delta=f->sum(toList(0..3),i->drift#i*diff(R_i,f));
con=vv->matrix apply(entries vv,row->apply(row,f->delta f))+mat*vv;
<< "INPUT core=" << numcols tripleCore << " source=" << numcols tripleSource
   << " CPU=" << cpuTime()-upperClock << endl << flush;
tripleUpper=gens gb(tripleCore|tripleSource);
<< "UPPER_BASIS_COLUMNS=" << numcols tripleUpper << " CPU=" << cpuTime()-upperClock << endl << flush;
assert(con(tripleUpper)%gb tripleUpper==0);
assert(tripleCore%gb tripleUpper==0 and tripleSource%gb tripleUpper==0);
<< "UPPER_INVARIANT=true" << endl;
<< "UPPER_RELATIONS=" << toString entries tripleUpper << endl;
<< "UPPER_DIMENSION=" << dim coker tripleUpper << endl;
coreCoords=tripleCore//tripleUpper;
if upperEmitFullSourceCoordinates then sourceCoords=tripleSource//tripleUpper;
selectedCoords=selected//tripleUpper;
connCoords=con(tripleUpper)//tripleUpper;
assert(entries(tripleUpper*coreCoords)==entries tripleCore);
if upperEmitFullSourceCoordinates then assert(entries(tripleUpper*sourceCoords)==entries tripleSource);
assert(entries(tripleUpper*connCoords)==entries con(tripleUpper));
<< "CORE_COORDINATES=" << toString entries coreCoords << endl;
if upperEmitFullSourceCoordinates then << "SOURCE_COORDINATES=" << toString entries sourceCoords << endl;
<< "SELECTED_COORDINATES=" << toString entries selectedCoords << endl;
<< "CONNECTION_COORDINATES=" << toString entries connCoords << endl;
<< "COMPLETE cpu=" << cpuTime()-upperClock << endl << flush;
exit 0;
