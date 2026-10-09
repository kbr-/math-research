# Check the two-stage ordinary-PC compiler, not a flattened NS identity.
# Star elimination uses the previously checked degree-four adjugate certificate.
# New tests: all first-bit determinant specializations over F2/F4; then full
# weighted branch proofs for the projected Mycielski K4 (five boundary vertices).
# 32 first-bit pins, 102 second-bit branches, ten inputs, at most ten variables.
Check:=function(b,msg) if not b then Error(msg);fi;end;
Deg:=function(p) local e,i,d;
 if IsFFE(p) or IsZero(p) then return 0;fi;
 e:=ExtRepPolynomialRatFun(p);d:=0;
 for i in [1,3..Length(e)-1] do d:=Maximum(d,Sum(e[i]{[2,4..Length(e[i])]}));od;
 return d;
end;
Sub:=function(p,vars,vals)
 if IsFFE(p) or IsZero(p) then return p;fi;
 return Value(p,vars,vals);
end;
StarDet:=function(u,v,o)
 return DeterminantMat(List([1..4],i->[o,u[i],v[i],u[i]*v[i]]));
end;
Pin:=function(f,vars,alpha,o)
 local delta,cur,next,coef,terms,i,without,prod;
 delta:=Product([1..Length(vars)],i->vars[i]+(1-alpha[i])*o);
 cur:=f;terms:=[];
 for i in [1..Length(vars)] do
  coef:=Sub(cur,[vars[i]],[Zero(o)])+Sub(cur,[vars[i]],[o]);
  next:=Sub(cur,[vars[i]],[alpha[i]*o]);
  Check(IsZero(cur+next+(vars[i]+alpha[i]*o)*coef),"multilinear pin telescope");
  without:=Product(Filtered([1..Length(vars)],j->j<>i),j->vars[j]+(1-alpha[j])*o);
  Add(terms,(vars[i]^2+vars[i])*without*coef);
  cur:=next;
 od;
 Check(IsZero(delta*f+Sum(terms)+delta*cur),"literal pin certificate");
 return rec(delta:=delta,restricted:=cur,terms:=terms,maxdegree:=Maximum(Concatenation([Deg(delta*f)],List(terms,Deg))));
end;
Iverson:=function(b) if b then return 1;else return 0;fi;end;
Scalar:=function(p,F) local e;
 if IsFFE(p) then return p;fi;
 if IsZero(p) then return Zero(F);fi;
 e:=ExtRepPolynomialRatFun(p);Check(Length(e)=2 and Length(e[1])=0,"nonconstant matrix entry");return e[2];
end;
Main:=function()
 local F,R,x,o,u,v,alpha,zs,os,d,pred,detchecks,firstpins,secondpins,branches,maxdeg,n,
 edges,stars,inputs,pin1,split,left,right,beta,pin2,rows,c,unit,const,coefs,j,g,zeroVals,
 cert,total,delta,chi,negative,satbranches,idx,firstmax,secondmax,allU,allV;
 detchecks:=0;
 Print("SIZING determinant pins16x2 fields; full projected graph five vertices,32 first pins,102 second branches; Gaussian matrices10x<=6\n");
 for F in [GF(2),GF(4)] do
  R:=PolynomialRing(F,8);x:=IndeterminatesOfPolynomialRing(R);o:=One(R);
  u:=x{[1..4]};v:=x{[5..8]};
  for alpha in Tuples([0,1],4) do
   d:=StarDet(List(alpha,a->a*o),v,o);
   zs:=Filtered([1..4],i->alpha[i]=0);os:=Difference([1..4],zs);
   pred:=Zero(o);
   if Length(zs)=2 then pred:=(v[zs[1]]+v[zs[2]])*(v[os[1]]+v[os[2]]);fi;
   Check(IsZero(d-pred),"determinant bipartite specialization");
   pin1:=Pin(StarDet(u,v,o),u,alpha,o);
   Check(IsZero(pin1.restricted-pred) and pin1.maxdegree<=8,"weighted determinant degree");
   detchecks:=detchecks+1;
  od;
 od;
 # Mycielski K4: boundary original vertices1..4 and apex5; four independent
 # clone centres, clone i adjacent to originals except i and to apex.
 F:=GF(2);R:=PolynomialRing(F,10);x:=IndeterminatesOfPolynomialRing(R);o:=One(R);
 u:=x{[1..5]};v:=x{[6..10]};
 edges:=Combinations([1..4],2);
 stars:=List([1..4],i->Concatenation(Difference([1..4],[i]),[5]));
 inputs:=Concatenation(List(edges,e->(o+u[e[1]]+u[e[2]])*(o+v[e[1]]+v[e[2]])),List(stars,s->StarDet(u{s},v{s},o)));
 firstpins:=0;secondpins:=0;branches:=0;maxdeg:=0;total:=Zero(o);satbranches:=0;
 for alpha in Tuples([0,1],5) do
  pin1:=List(inputs,g->Pin(g,u,alpha,o));delta:=pin1[1].delta;
  firstpins:=firstpins+Length(inputs);firstmax:=Maximum(List(pin1,p->p.maxdegree));maxdeg:=Maximum(maxdeg,firstmax);
  zs:=Filtered([1..5],i->alpha[i]=0);os:=Difference([1..5],zs);
  if Length(zs)<=Length(os) then left:=zs;right:=os;else left:=os;right:=zs;fi;
  for beta in Tuples([0,1],Length(left)) do
   pin2:=List(pin1,p->Pin(p.restricted,v{left},beta,o));chi:=pin2[1].delta;
   rows:=[];
   for g in List(pin2,p->p.restricted) do
    zeroVals:=List(x,z->Zero(o));const:=Sub(g,x,zeroVals);
    coefs:=List(right,j->Sub(g,x,Concatenation(List([1..5],z->Zero(o)),List([1..5],z->Iverson(z=j)*o)))+const);
    Check(IsZero(g-const-Sum([1..Length(right)],j->coefs[j]*v[right[j]])),"remaining equations not affine");
    Add(rows,List(Concatenation([const],coefs),z->Scalar(z,F)));
   od;
   unit:=Concatenation([One(F)],List(right,j->Zero(F)));
   c:=SolutionMat(rows,unit);Check(c<>fail,"projected contradiction lost");
   cert:=Sum([1..Length(inputs)],j->c[j]*delta*chi*pin2[j].restricted);
   Check(IsZero(cert-delta*chi),"weighted branch unit");
   for idx in [1..Length(inputs)] do
    # Crucially reuse delta*restricted input, not delta*original input.
    Check(IsZero(delta*(chi*pin1[idx].restricted+Sum(pin2[idx].terms)+chi*pin2[idx].restricted)),"second-stage identity");
    secondmax:=Maximum(Concatenation([Deg(delta*chi*pin1[idx].restricted)],List(pin2[idx].terms,z->Deg(delta*z))));
    maxdeg:=Maximum(maxdeg,secondmax);
   od;
   secondpins:=secondpins+Length(inputs);branches:=branches+1;total:=total+cert;
   Print("BRANCH u=",alpha," pinned-v=",left," values=",beta," affine-certificate=",c,"\n");
   # Removing all star equations leaves colourable K4 plus an unconstrained apex.
   if SolutionMat(rows{[1..Length(edges)]},unit)=fail then satbranches:=satbranches+1;fi;
  od;
 od;
 Check(IsZero(total-o),"literal global unit sum");
 Check(maxdeg<=9,"ordinary PC degree budget");
 Check(branches=102 and satbranches>0,"nonvacuous complete and negative controls");
 Print("DETERMINANT_IDENTITIES=",detchecks," FIRST_STAGE_IDENTITIES=",firstpins," SECOND_STAGE_IDENTITIES=",secondpins," COMPLETE_BRANCHES=",branches," MAX_ORDINARY_DEGREE=",maxdeg," OMITTED_STAR_CONSISTENT_BRANCHES=",satbranches,"\n");
 Print("ALL INDEPENDENT COLOUR COMPILER CONTROLS PASSED\n");
end;
Main();
QUIT;
