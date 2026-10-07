\\ Exhaustive finite-field controls of the actual group law, V Fr=[p], and
\\ the polynomial zero-curvature fibre algebra.
default(parisizemax,1500000000);
default(nbthreads,1); setrand(20261007);
iferr(read("research/tools/bmd_hyperelliptic_division_core_20261007.gp"),err,print(err);quit(1));
hc_controls()={
my(curves=[[3,Mod(1,3)*(x^3+x^2+1)],[3,Mod(1,3)*(x^9+x^8+x^5+x-1)],[5,Mod(1,5)*(x^3+x^2+1)]]);
for(ci=1,#curves,
 hc_setup(curves[ci][2],curves[ci][1]);my(cp=hyperellcharpoly(HC_F),expected=subst(cp,variable(cp),1),candidates=sum(m=0,HC_G,HC_P^(2*m)),started=getwalltime());
 print("SIZING p=",HC_P," genus=",HC_G," candidate_pairs=",candidates," Jacobian_order=",expected," group_table_cells=",expected^2," associativity_lookups=",expected^3);
 hc_assert(expected<=250 && candidates<=8000,"exhaustive control exceeds budget");
 my(L=List());listput(L,hc_zero());
 for(m=1,HC_G,for(uc=0,HC_P^m-1,my(u=HC_ONE*x^m+sum(j=0,m-1,Mod((uc\HC_P^j)%HC_P,HC_P)*x^j));for(vc=0,HC_P^m-1,my(v=sum(j=0,m-1,Mod((vc\HC_P^j)%HC_P,HC_P)*x^j));if(hc_rem(v^2-HC_F,u)==0,listput(L,[u,v])))));
 my(classes=Vec(L),N=#classes,idx=Map());hc_assert(N==expected,"Jacobian order mismatch");for(i=1,N,mapput(idx,Str(classes[i]),i));
 my(T=matrix(N,N));for(i=1,N,for(j=1,N,my(D=hc_add(classes[i],classes[j]));hc_assert(mapisdefined(idx,Str(D)),"group closure failure");T[i,j]=mapget(idx,Str(D))));
 hc_assert(T==mattranspose(T),"commutativity failure");
 for(i=1,N,hc_assert(T[i,1]==i,"identity failure");hc_assert(setsearch(Set(T[i,]),1)!=0,"inverse missing");for(j=1,N,hc_assert(T[T[i,j],]==vector(N,k,T[i,T[j,k]]),"associativity failure")));
 my(triples=vector(N,i,mapget(idx,Str(hc_mul(classes[i],HC_P)))),mult=vector(N,j,sum(i=1,N,triples[i]==j)),vf=0,cf=0,branch=0,ell=if(HC_G==1,ellinit([0,1,0,0,1]*Mod(1,HC_P)),0));
 for(i=1,N,
  my(D=classes[i],V=hc_v(hc_fr(D)));hc_assert(V==classes[triples[i]],"V Fr differs from p-multiplication");vf++;if(poldegree(gcd(D[1],HC_F),x)>0,branch++);
  my(Q=hc_connection(D),M=matid(HC_G)-Q[2],r=matrank(M),aug=matconcat([M,Mat(-Q[1]~)]),pred=if(matrank(aug)==r,HC_P^(HC_G-r),0));hc_assert(pred==mult[i],"curvature fibre count differs from actual V fibre");cf++;
  if(HC_G==1,my(P=if(poldegree(D[1],x)==0,[0],[-polcoef(D[1],0,x),polcoef(D[2],0,x)]),P3=ellmul(ell,P,HC_P),D3=classes[triples[i]]);if(#P3==1,hc_assert(poldegree(D3[1],x)==0,"PARI elliptic infinity mismatch"),hc_assert(D3==[HC_ONE*x-P3[1],P3[2]],"PARI elliptic multiplication mismatch")))
 );
 if(HC_G==1,my(Z=hc_connection(hc_zero()),M=matid(1)-Z[2]);hc_assert(matrank(matconcat([M,Mat([HC_ONE]~)]))>matrank(M),"corrupted curvature coefficient was not rejected");print("CORRUPTION_CONTROL p=",HC_P," passed"));
 print("FINITE_CHECK p=",HC_P," genus=",HC_G," classes=",N," group_pairs=",N^2," associative_triples=",N^3," V_comparisons=",vf," connection_fibres=",cf," branch_cases=",branch," elapsed_ms=",getwalltime()-started);
);
print("HYPERELLIPTIC_FINITE_CONTROLS_COMPLETED");
};
iferr(hc_controls(),err,print(err);quit(1));
quit;
