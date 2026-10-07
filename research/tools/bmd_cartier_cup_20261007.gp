\\ Test whether the first Frobenius-deflated cup form can be nonsingular.
\\ Forms on H0(cH), c=(n-3)/2, using only holomorphic products fg*dT/W.
\\ Character Cartier blocks replace growing q-jet expansions; direct small jets check the encoding.
default(parisizemax,1000000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s))};
{
my(fd=7,ev=getenv("BMD_CUP_FIELD_DEGREE"));if(ev,fd=eval(ev));assert(fd==3||fd==7,"allowed field degrees");my(cases=if(fd==3,[9],[3,5,9]),direct=0);T='x;p=3;modulus=ffinit(p,fd);a=ffgen(modulus,'a);one=a^0;print("FIELD_MODULUS=",modulus);
for(ci=1,#cases,
 my(n=cases[ci],c=(n-3)/2,aa=vector(n,i,a^(i-1)),all=2^n-1,polys=vector(2^n),blocks=vector(2^n),rows=vector(2^n),basis=List(),bad=0,g=0);
 assert(#Set(aa)==n && !setsearch(Set(aa),0*one),"admissible labels");
 for(S=0,all,polys[S+1]=prod(i=1,n,if(bittest(S,i-1),one+aa[i]*T,one));my(dim=floor((hammingweight(S)-1)/2));
  if(dim>0,my(f=polys[S+1]^((p-1)/2));blocks[S+1]=matrix(dim,dim,i,j,polcoef(f,p*(i-1)+p-1-(j-1),T));rows[S+1]=vector(dim,j,if(j==1,one,0*one));g+=dim;if(matdet(blocks[S+1])==0,bad++));
  if(hammingweight(S)<=c,for(j=0,floor((c-hammingweight(S))/2),listput(basis,[S,j])))
 );
 my(I=Vec(basis),h=#I);
 print("CUP_SETUP n=",n," p=3 field_degree=",fd," theta_sections=",h," genus=",g," singular_Cartier_blocks=",bad," largest_matrix=",[h,h]);
 my(found=-1);for(s=0,8,
  my(M=matrix(h,h,i,j,my(S=I[i][1],R=I[j][1],Q=bitxor(all,bitxor(S,R)),f=polys[bitand(S,R)+1]*T^(I[i][2]+I[j][2]),dim=#rows[Q+1]);assert(poldegree(f)<=dim-1,"product not holomorphic");sum(t=0,dim-1,rows[Q+1][t+1]*polcoef(f,t,T))),rank=matrank(M));
  assert(M==mattranspose(M),"cup form not symmetric");if(s==0,assert(rank==1,"initial evaluation rank"));
  if(n<=5 && s<=2,
   my(q=p^s);
   for(i=1,h,for(j=1,h,my(S=I[i][1],R=I[j][1],Q=bitxor(all,bitxor(S,R)),f=polys[bitand(S,R)+1]*T^(I[i][2]+I[j][2]),w=sqrt(polys[Q+1]+O(T^q)));if(polcoef(w,0,T)!=one,w=-w);assert(M[i,j]==polcoef(f/w,q-1,T),"Cartier/direct jet discrepancy");direct++))
  );
  print("CUP_RANK n=",n," iterate=",s," q=",p^s," rank=",rank," target=",h);
  if(rank==h,
   found=s;
   if(fd==3,
    my(field=vector(p^fd,j,one*((j-1)%p)+a*(((j-1)\p)%p)+a^2*((j-1)\p^2)),codes=Map(),det=matdet(M));
    for(j=1,#field,mapput(codes,Str(field[j]),j-1));assert(det!=0,"full-rank determinant");
    my(out="research/results/bmd-exception-torsion-deflation-20261007/cup-data.g");
    write(out,"CUP_FIELD_POLY := ",vector(fd+1,j,lift(polcoef(modulus,j-1))),";");
    write(out,"CUP_CODES := ",vector(h,i,vector(h,j,mapget(codes,Str(M[i,j])))),";");
    write(out,"CUP_DET_CODE := ",mapget(codes,Str(det)),";");
    print("FULL_CUP_DETERMINANT=",det," code=",mapget(codes,Str(det))," matrix_path=",out)
   );break
  );
  for(S=0,all,if(type(rows[S+1])=="t_VEC",rows[S+1]=apply(z->z^p,rows[S+1])*blocks[S+1]))
 );
 print("CUP_RESULT n=",n," first_full_iterate=",found," ordinary=",bad==0);
 if(fd==3 && found>=4,
  my(cache=Map(),times=vector(n),estimated=0,qfield=p^fd,started=getwalltime(),budget=120000,allow=1);
  for(m=3,n,my(S=2^m-1,start=getwalltime(),cp=hyperellcharpoly(polys[S+1]),ms=getwalltime()-start);mapput(cache,S,cp);times[m]=max(1,ms);estimated+=binomial(n,m)*times[m];print("POINT_COUNT_SIZE branches=",m," genus=",floor((m-1)/2)," wall_ms=",ms);if(ms>5000,allow=0;break));
  print("POINT_COUNT_ESTIMATE_MS=",estimated," budget_ms=",budget);
  if(allow && estimated<budget,
   my(exp=1,tracechecks=0,field=vector(qfield,j,one*((j-1)%p)+a*(((j-1)\p)%p)+a^2*((j-1)\p^2)),cpvar);
   for(S=0,all,my(dim=floor((hammingweight(S)-1)/2));if(dim>0,
    my(cp);if(mapisdefined(cache,S),cp=mapget(cache,S),cp=hyperellcharpoly(polys[S+1]));cpvar=variable(cp);assert(poldegree(cp)==2*dim,"Frobenius polynomial degree");for(j=0,dim,assert(polcoef(cp,j)==qfield^(dim-j)*polcoef(cp,2*dim-j),"Frobenius functional equation"));
    my(points=qfield+if(hammingweight(S)%2,1,if(pollead(polys[S+1])^((qfield-1)/2)==one,2,0)));
    for(j=1,qfield,my(v=subst(polys[S+1],T,field[j]));if(v!=0,points+=if(v^((qfield-1)/2)==one,1,-1)));
    assert(points==qfield+1+polcoef(cp,2*dim-1),"independent rational point count");tracechecks++;
    my(order=subst(cp,cpvar,1));assert(order>0,"positive Jacobian order");exp=lcm(exp,order);print("QUOTIENT_ORDER subset=",S," genus=",dim," order=",order," charpoly=",cp);
    if(getwalltime()-started>budget,error("point-count sizing underestimated; no exponent accepted"))
   ));
   my(M=2^(n-1)*exp,v=valuation(M,p),m=M/p^v,period=fd*p^2*lcm(vector(4,i,qfield^i-1)),first=found+max(0,ceil((v-found)/period))*period);
   print("EXPLICIT_CONSTANTS annihilator=",M," p_valuation=",v," prime_to_p_part=",m," exponent_period_bound=",period," first_exponent=",first," first_full_iterate=",found," quotient_trace_checks=",tracechecks," pointcount_wall_ms=",getwalltime()-started)
  ,print("POINT_COUNTS_NOT_RUN: estimate exceeds bounded pilot"))
 )
);
print("DIRECT_COEFFICIENT_CHECKS=",direct);print("CARTIER_CUP_CONTROLS_COMPLETED; no generic normality asserted from ranks alone")
}
quit;
