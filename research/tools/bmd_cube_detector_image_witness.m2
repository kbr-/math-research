-- Extract a short exact separating witness from the retained image calculation.
-- Reuse the matrices, without rerunning the degree series or the cyclic closure.
-- Verify lambda*relations=lambda*image13=0 and lambda*b(image12)=1.
imWClock=cpuTime();
imWSource=separate("\n",get "research/tools/bmd_cube_detector_image.m2");
imWEnd=first select(toList(0..#imWSource-1),i->substring(0,4,imWSource#i)=="imR=");
value concatenate apply(take(imWSource,imWEnd),l->l|"\n");
imWLines=separate("\n",get "research/results/cube-quadruple-detector-image-20260927/image-certificate.txt");
imWGet=tag->matrix value substring(#tag,first select(imWLines,l->substring(0,#tag,l)==tag));
imWRel=imWGet "RELATIONS_QQ weight=13 matrix=";
imWImg=imWGet "IMAGE_QQ weight=13 matrix=";
imWMult=imWGet "B_PREVIOUS_IMAGE_QQ weight=13 matrix=";
imWKernel=imWGet "SOURCE_KERNEL_QQ weight=12 matrix=";
imWAnn=gens ker transpose(imWRel|imWImg);
imWObs=transpose(imWAnn)*imWMult;
imWi=first select(toList(0..numrows imWObs-1),i->any(toList(0..numcols imWObs-1),j->imWObs_(i,j)!=0));
imWj=first select(toList(0..numcols imWObs-1),j->imWObs_(imWi,j)!=0);
imWLam=(1/imWObs_(imWi,imWj))*transpose submatrix(imWAnn,,{imWi});
assert(imWLam*imWRel==0 and imWLam*imWImg==0);
assert((imWLam*imWMult)_(0,imWj)==1);
imWU=flatten entries basis(3,imP);imWV=flatten entries basis(2,imP);
imWUValue=sum(toList(0..#imWU-1),i->imWKernel_(i,imWj)*imWU#i);
imWVValue=sum(toList(0..#imWV-1),i->imWKernel_(#imWU+i,imWj)*imWV#i);
assert(imChi(imWUValue)+dr*imChi(imWVValue)==0);
imWQ=imA5*imWUValue+imA6*imWVValue;
imWH=imIntegrate imWQ;assert(imL(imWH)==imWQ);
<< "U=" << toString imWUValue << " V=" << toString imWVValue << endl;
<< "Q=" << toString imWQ << endl;
<< "EPD_PRIMITIVE=" << toString imWH << endl;
<< "IMAGE12_COLUMN=" << imWj << " TARGET_DIMENSION=" << numcols imWLam << endl;
<< "SEPARATING_FUNCTIONAL=" << toString entries imWLam << endl;
<< "ZERO_ON_RELATIONS=" << (imWLam*imWRel==0) << " ZERO_ON_IMAGE13=" << (imWLam*imWImg==0)
   << " VALUE_ON_B_WITNESS=" << (imWLam*imWMult)_(0,imWj) << endl;
<< "PASS cpu=" << cpuTime()-imWClock << endl << flush;
exit 0;
