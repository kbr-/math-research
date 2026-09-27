-- Test whether the actual polynomial image Phi42(K2) is stable under its
-- normalization coordinate b. Smallest core N=6; no change of dimension.
-- A failure refutes treating the image as a B42-module without extra data.
-- All weights9..19 are processed in one pass, stopping at first failure.
-- Weights9,10 are zero-image controls. Weights11..18 cover every generator
-- by the proved residual source theorem, so testing b through weight19 is
-- complete for b-stability at N=6, not just a heuristic window.
-- Stages: universal pair columns; exact EPD integration; full kernel of the
-- normalized triple-double map in each source degree; actual image quotient;
-- exact membership of b times the preceding image. All ranks use M2 over QQ.
-- Refuse source sizes above2000 or target sizes above280 before rank work.
imClock=cpuTime();
imP=QQ[c_2..c_6,ss,vv,Degrees=>{2,3,4,5,6,1,2}];
imAvec={1_imP,ss};
for j from 2 to 6 do imAvec=append(imAvec,ss*imAvec#(j-1)-vv*imAvec#(j-2)+(-1)^j*c_j);
imA5=imAvec#5;imA6=imAvec#6;
imL=f->diff(ss,diff(ss,f))+ss*diff(ss,diff(vv,f))+vv*diff(vv,diff(vv,f))+(5/2)*diff(vv,f);
imPrimitive=(ii,jj)->(
    co:=1_QQ/((jj+1)*(ii+jj+5/2));ans:=co*ss^ii*vv^(jj+1);
    for t from 1 to ii//2 do (
        co=-co*(ii-2*t+2)*(ii-2*t+1)/((jj+1+t)*(ii+jj-t+5/2));
        ans=ans+co*ss^(ii-2*t)*vv^(jj+1+t);
    );ans
);
imIntegrate=f->sum(listForm f,term->(
    ex:=term#0;co:=term#1;
    co*product(toList(0..4),j->imP_j^(ex#j))*imPrimitive(ex#5,ex#6)
));
imNorm=QQ[tr,dr];imNZ=imNorm[zz];
imNP=(zz-tr)^3*(zz-dr)^2*(zz+3*tr+2*dr);
imNC=apply(toList(2..6),j->sub((-1)^j*coefficient(zz^(6-j),imNP),imNorm));
imNormMap=map(imNorm,imP,imNC|{tr+dr,tr*dr});
-- Differentiate before evaluation, then multiply the evaluated v derivative.
imChi=u->imNormMap(u)-(2/5)*(dr-tr)*(imNormMap(diff(ss,u))+dr*imNormMap(diff(vv,u)));
imR=QQ[bb,ea,eb,ec,ed,Degrees=>{1,2,3,4,2}];
imT=imR/((ideal(ea,eb,ec,ed))^4);
imZ=imT[z];imF=(z-bb)^4+ea*(z-bb)^2-eb*(z-bb)+ec;imG=(z+2*bb)^2+ed;
imPC=apply(toList(2..6),j->sub((-1)^j*coefficient(z^(6-j),imF*imG),imT));
imXY=imT[x,y];imQ=imXY/ideal((x-bb)^4+ea*(x-bb)^2-eb*(x-bb)+ec,(y+2*bb)^2+ed);
imToQ=map(imQ,imP,apply(imPC,f->sub(f,imQ))|{sub(x+y,imQ),sub(x*y,imQ)});
imWeights=flatten apply(toList(0..1),j->apply(toList(0..3),i->i+j+1));
imEncode=f->matrix table(8,1,(i,j)->sub(coefficient(x^(i%4)*y^(i//4),lift(f,imXY)),imT));
imBin={1_QQ};for j from 1 to 17 do imBin=append(imBin,last(imBin)*(-3/2-j+1)/j);
imColumns=apply(toList(0..17),j->imEncode sub((y-x)*sum(toList(0..j),i->imBin#i*imBin#(j-i)*x^i*y^(j-i)),imQ));
imTBasis=d->if d<0 then {} else flatten entries basis(d,imT);
imRows=d->flatten apply(toList(0..7),i->apply(imTBasis(d-imWeights#i),m->{i,lift(m,imR)}));
imQQ=(mat,rows)->matrix table(#rows,numcols mat,(i,j)->lift(coefficient(rows#i#1,lift(mat_(rows#i#0,j),imR)),QQ));
imJoin=(lis,n)->if #lis==0 then map(imT^n,imT^0,0) else fold((a,b)->a|b,lis);
imFailed=false;imPrev=null;imPrevDegree=-1;
for d from 9 to 19 do if not imFailed then (
    us:=if d<9 then {} else flatten entries basis(d-9,imP);
    vs:=if d<10 then {} else flatten entries basis(d-10,imP);
    rows:=imRows d;ns:=#us+#vs;
    assert(ns<=2000 and #rows<=280);
    << "SIZE weight=" << d << " source=" << ns << " target=" << #rows << endl << flush;
    chiValues:=apply(us,u->imChi u)|apply(vs,v->dr*imChi v);
    chi:=matrix table(d-8,ns,(i,j)->lift(coefficient(tr^i*dr^(d-9-i),chiValues#j),QQ));
    kerChi:=gens ker chi;
    qSource:=apply(us,u->imA5*u)|apply(vs,v->imA6*v);
    qPrimitives:=apply(qSource,q->(
        prim:=imIntegrate q;assert(imL(prim)==q);prim
    ));
    raw:=imJoin(apply(qPrimitives,q->imEncode(sub(y-x,imQ)*imToQ q)),8);
    actual:=raw*sub(kerChi,imT);
    rels:=imJoin(flatten apply(toList(0..d-2),j->apply(imTBasis(d-j-2),m->m*imColumns#j)),8);
    rq:=imQQ(rels,rows);iq:=imQQ(actual,rows);
    rrank:=rank rq;irank:=rank(rq|iq);extra:=0;
    if imPrev=!=null then extra=rank(rq|iq|imQQ(bb*imPrev,rows))-irank;
    if d<=10 then assert(irank==rrank);
    << "RESULT weight=" << d << " relationRank=" << rrank << " imageDim=" << irank-rrank
       << " bClosureFailure=" << extra << endl << flush;
    << "SOURCE_KERNEL_QQ weight=" << d << " matrix=" << toString entries kerChi << endl;
    << "IMAGE_QQ weight=" << d << " matrix=" << toString entries iq << endl;
    << "RELATIONS_QQ weight=" << d << " matrix=" << toString entries rq << endl;
    if extra>0 then (
        << "B_PREVIOUS_IMAGE_QQ weight=" << d << " matrix=" << toString entries imQQ(bb*imPrev,rows) << endl;
        imFailed=true;
    );
    imPrev=actual;imPrevDegree=d;
);
<< "FINISHED normalizationStable=" << not imFailed << " lastWeight=" << imPrevDegree
   << " cpu=" << cpuTime()-imClock << endl << flush;
exit 0;
