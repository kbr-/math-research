-- Independent root-coordinate Taylor check of BOTH 16-column obstruction
-- Krylov matrices. Uses a_i(z)=a_i/(1+a_i z) and literal square-root characters,
-- not the polynomial connection recurrence. All 512 entries are compared after
-- the explicit Vandermonde frame change; wrong omission of g(z)/g(0) is tested.
B=QQ[e_1..e_4,Degrees=>{1,2,3,4}];
cubeRead=(path,key)->(
    ls:=separate("\n",get path); hs:=select(ls,l->substring(0,#key,l)==key);
    assert(#hs==1); value substring(#key,hs#0));
cubeH=apply(cubeRead("research/results/cube-jet-layer-relations-20260927/monic-obstruction.txt","MONIC_W_TOP1="),f->sub(f,B));
cubeFamilyPath="research/results/cube-jet-layer-relations-20260927/monic-family-obstruction.txt";
cubeG=apply(cubeRead(cubeFamilyPath,"FAMILY_G="),f->sub(f,B));
FF=ZZ/32003;
cubeKH=matrix apply(cubeRead(cubeFamilyPath,"FAMILY_KRYLOV_H="),row->apply(row,c->sub(c,FF)));
cubeKG=matrix apply(cubeRead(cubeFamilyPath,"FAMILY_KRYLOV_G="),row->apply(row,c->sub(c,FF)));
R=FF[z]; S=R/ideal(z^16); zz=S_0;
cubeRoots={1,2,3,5};
cubeOrbit=apply(cubeRoots,a->a*sum(toList(0..15),j->(-a*zz)^j));
cubeEs=apply(toList(1..4),j->sum(subsets(4,j),I->product(I,i->cubeOrbit#i)));
cubeToOrbit=map(S,B,cubeEs);
cubeWH=apply(cubeH,f->cubeToOrbit f); cubeWG=apply(cubeG,f->cubeToOrbit f);
cubeHalfBinom={1_FF};
for j from 1 to 19 do cubeHalfBinom=append(cubeHalfBinom,last(cubeHalfBinom)*(3-2*j)/(2*j));
cubeSingle=apply(toList(0..3),i->apply(toList(0..19),j->cubeHalfBinom#j*(cubeOrbit#i)^j));
cubeSingleOrbit=apply(cubeRoots,a->sum(toList(0..15),j->cubeHalfBinom#j*(a*zz)^j));
cubeCharacters=new MutableHashTable; cubeOrbitCharacters=new MutableHashTable;
cubeCharacters#"{}"={1_S}|toList(19:0_S); cubeOrbitCharacters#"{}"=1_S;
cubeSubsets=flatten apply(toList(0..4),s->subsets(4,s));
for I in drop(cubeSubsets,1) do (
    parent:=toString take(I,#I-1); factorIndex:=last I;
    cubeCharacters#(toString I)=apply(toList(0..19),j->sum(toList(0..j),k->(cubeCharacters#parent)#k*(cubeSingle#factorIndex)#(j-k)));
    cubeOrbitCharacters#(toString I)=(cubeOrbitCharacters#parent)*cubeSingleOrbit#factorIndex;
);
cubeCoefficient=(f,j)->sub(coefficient(R_0^j,lift(f,R)),FF);
cubeWrongCount=0;
cubeDirect=apply({cubeWH,cubeWG},W->matrix apply(cubeSubsets,I->(
    ss:=#I; ks:=if ss>2 then 0 else (2-ss)//2+1;
    bare:=sum(toList(ks..19),c->W#c*(cubeCharacters#(toString I))#(c-ks))/(ks!);
    transported:=(cubeOrbitCharacters#(toString I))*bare;
    if ss>0 and cubeCoefficient(bare,1)!=cubeCoefficient(transported,1) then cubeWrongCount=cubeWrongCount+1;
    apply(toList(0..15),j->(j!)*cubeCoefficient(transported,j))
)));
cubeEvaluation=matrix table(4,4,(i,j)->(cubeRoots#i)^j*1_FF);
cubeFrames=apply(toList(0..4),s->(
    ids:=subsets(4,s);
    scales:=apply(ids,I->1_FF/product(subsets(I,2),pair->(cubeRoots#(pair#1)-cubeRoots#(pair#0))*1_FF));
    diagonalMatrix(scales)*exteriorPower(s,cubeEvaluation)));
cubeFrame=directSum cubeFrames;
assert(det cubeFrame!=0);
assert(cubeDirect#0==cubeFrame*cubeKH);
assert(cubeDirect#1==cubeFrame*cubeKG);
assert(cubeWrongCount>0);
<< "ROOT_KRYLOV_H=" << toString entries(cubeDirect#0) << endl;
<< "ROOT_KRYLOV_G=" << toString entries(cubeDirect#1) << endl;
<< "FRAME_DETERMINANT=" << det cubeFrame << endl;
<< "SYMMETRIC_DETERMINANTS H=" << det cubeKH << " G=" << det cubeKG << endl;
<< "PASS all512 root-coordinate Taylor identities; omitted-character-factor failures=" << cubeWrongCount << endl;
exit 0;
