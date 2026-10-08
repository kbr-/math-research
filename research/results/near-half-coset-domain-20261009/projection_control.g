# Exact finite controls for the Boolean projection ceiling, not its
# asymptotic path bound. Three models, largest cube8 and modular grid49.
Check:=function(ok,msg) if not ok then Error(msg);fi;end;;
# Ring-independent constant handling in the character factors.
PhasePoly:=function(xs,o,zeta,a) local z,i;z:=o;for i in [1..Length(a)] do z:=z*(o+(zeta^a[i]-zeta^0)*xs[i]);od;return z;end;;
models:=[rec(q:=3,F:=GF(4),n:=3,rows:=[[2,1,0],[2,0,1]],charges:=[1,2]),
 rec(q:=5,F:=GF(16),n:=2,rows:=[[1,1]],charges:=[3]),
 rec(q:=7,F:=GF(8),n:=2,rows:=[[1,1]],charges:=[5])];
Print("SIZING 3 models: Boolean cubes8,4,4; modular grids27,25,49; one basis inverse per model\n");
certTerms:=0;gridChecks:=0;
for mdl in models do
 q:=mdl.q;nf:=mdl.n;fld:=mdl.F;zeta:=Z(Size(fld))^((Size(fld)-1)/q);fe:=One(fld);fz:=Zero(fld);
 ring:=PolynomialRing(fld,nf);xs:=IndeterminatesOfPolynomialRing(ring);o:=One(ring);
 bits:=Tuples([0,1],nf);betas:=bits;
 phaseEval:=function(beta,a) return zeta^(Sum([1..nf],i->beta[i]*a[i]) mod q);end;
 basis:=List(betas,beta->List(bits,a->phaseEval(beta,a)));
 Check(RankMat(basis)=Length(bits),"Boolean character basis rank");invBasis:=basis^-1;
 coset:=Filtered(Tuples([0..q-1],nf),a->ForAll([1..Length(mdl.rows)],j->Sum([1..nf],i->mdl.rows[j][i]*a[i]) mod q=mdl.charges[j]));
 Check(not IsEmpty(coset) and Intersection(coset,bits)=[],"field-consistent Boolean-empty projection");
 for coords in Combinations([1..nf]) do
  if Length(coords)=nf then continue;fi;
  Check(ForAny(coset,a->ForAll(coords,i->a[i] in [0,1])),"proper coordinate projection remains Boolean-feasible");
 od;
 values:=List([1..Length(mdl.rows)],j->List(bits,a->phaseEval(mdl.rows[j],a)-zeta^mdl.charges[j]));
 coeffs:=[];
 for j in [1..Length(mdl.rows)] do
  hv:=[];
  for b in [1..Length(bits)] do
   chosen:=First([1..Length(mdl.rows)],l->values[l][b]<>fz);
   Check(chosen<>fail,"partition selector exists");
   if chosen=j then Add(hv,values[j][b]^-1);else Add(hv,fz);fi;
  od;
  Add(coeffs,hv*invBasis);
 od;
 result:=Zero(ring);nonzeroTerms:=[];
 for j in [1..Length(mdl.rows)] do for b in [1..Length(betas)] do
  shifted:=List([1..nf],i->(betas[b][i]+mdl.rows[j][i]) mod q);
  piece:=PhasePoly(xs,o,zeta,shifted)-zeta^mdl.charges[j]*PhasePoly(xs,o,zeta,betas[b]);
  result:=result+coeffs[j][b]*piece;certTerms:=certTerms+1;
  if coeffs[j][b]<>fz and not IsZero(piece) then Add(nonzeroTerms,coeffs[j][b]*piece);fi;
 od;od;
 Check(result=o,"literal transported projection certificate");
 Check(not IsEmpty(nonzeroTerms) and result-nonzeroTerms[1]<>o,"omitted-term negative control");
 # q-root-grid indicator of the two Boolean states; tensor telescoping.
 bis:=[];
 for i in [1..nf] do
  bp:=Zero(ring);
  for exponent in [0..q-1] do bp:=bp+(fe+zeta^(-exponent))*xs[i]^exponent/(q*fe);od;
  Add(bis,bp);
 od;
 prodB:=o;tel:=Zero(ring);
 for i in [1..nf] do tel:=tel+(bis[i]-o)*prodB;prodB:=prodB*bis[i];od;
 Check(tel=prodB-o,"ordinary-domain telescoping identity");
 for a in Tuples([0..q-1],nf) do
  vals:=List(a,i->zeta^i);ev:=Value(prodB,xs,vals);
  if ForAll(a,i->i in [0,1]) then Check(ev=fe,"Boolean selector value");
  else Check(ev=fz,"non-Boolean selector value");fi;
  if a in coset then Check(ev=fz,"selector lies in coset ideal");fi;
  gridChecks:=gridChecks+1;
 od;
 Print("q=",q," field=",fld," projection_size=",nf," coset_points=",Length(coset)," basis_rank=",RankMat(basis)," coefficients=",coeffs," PASS\n");
od;
Print("TOTAL transported_terms=",certTerms," root_grid_evaluations=",gridChecks,"\nALL PROJECTION CONTROLS PASSED\n");
QUIT;
