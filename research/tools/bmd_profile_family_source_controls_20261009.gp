\\ Independent full-polynomial source extraction with shared nested power prefixes.
default(parisizemax,1000000000);
default(nbthreads,1);
ep='ep;b='b;T='T;x='x;
read("tools/saturated_rows.gp");
read("research/tools/bmd_profile_family_core_20261009.gp");
DIRECT_POWERS=Map();
direct_rows(lo,coff,gdeg,g,eps,T,x,p,L,H,cuts)={
  my(C=L+coff,v=2*C+1-gdeg,amin=lo+1,rows=matsize(cuts)[1],key=Str([p,L]),o=Mod(1,p),XP,TP);
  if(mapisdefined(DIRECT_POWERS,key),my(old=mapget(DIRECT_POWERS,key));XP=List(old[1]);TP=List(old[2]),XP=List([o]);TP=List([o]));
  while(#XP<2*C+2,listput(XP,XP[#XP]*(x-1)));
  while(#TP<C+1,listput(TP,TP[#TP]*(1+eps*T)));
  mapput(DIRECT_POWERS,key,[Vec(XP),Vec(TP)]);
  my(A=matrix(gdeg,gdeg,i,j,polcoef(XP[v+j+1],2*i-1,x)),inv=A^-1,R=matrix(2*rows,H));
  for(h=0,H-1,
    my(e=v-h,al=-inv*vector(gdeg,i,polcoef(XP[e+1],2*i-1,x))~,f=XP[e+1]+sum(j=1,gdeg,al[j]*XP[v+j+1]));
    for(i=1,gdeg,family_check(polcoef(f,2*i-1,x)==0,"actual missing odd coefficient"));
    my(ev=sum(j=0,C,polcoef(f,2*j,x)*TP[j+1]),od=g*sum(j=0,C-gdeg,polcoef(f,2*gdeg+1+2*j,x)*TP[j+1]));
    for(which=1,2,
      my(F=if(which==1,ev,od),fac=o*2^(v-2*L-h)*eps^(h-L-amin+if(which==1,0,gdeg)));
      for(i=1,rows,R[(which-1)*rows+i,h+1]=fac*sum(a=amin,coff,cuts[i,a-lo]*polcoef(F,L+a,T)))
    )
  );R;
};
run_controls()={
  my(total=0,caseCount=0,p=53,o=Mod(1,p));
  for(r=0,12,
    my(P=family_first(r,64,ep,o*2,T,0,p),R=direct_rows(P[4],P[5],3,P[12],ep,T,x,p,p,64,P[10]));
    family_check(R==P[7],"all first-root equations match independent positive-degree extraction");
    print("DIRECT_FIRST residue=",r," equations=",matsize(R)[1]*64," positive_parameter=",p);total+=matsize(R)[1]*64;caseCount++
  );
  for(r=0,4,
    read(Str("research/results/bmd-profile-family-20261009/first-r",r,".gp"));
    my(P=family_second(r,limitLowOffset,limitHighDegree,o*limitHighCoefficients,64,ep,b,T,0,p),R=direct_rows(P[4],P[5],1,o*(1+T),ep,T,x,p,2*p,64,P[10]));
    family_check(R==P[7],"all second-root equations match independent positive-degree extraction");
    print("DIRECT_SECOND residue=",r," equations=",matsize(R)[1]*64," positive_parameter=",2*p);total+=matsize(R)[1]*64;caseCount++
  );
  my(wp=101,wo=Mod(1,wp),Q=Mat([wo*(b+1),wo])~,P=family_second(12,24,26,Q,64,ep,b,T,0,wp),R=direct_rows(24,26,1,wo*(1+T),ep,T,x,wp,2*wp,64,P[10]));
  family_check(R==P[7],"largest altered-boundary coordinate window");
  total+=matsize(R)[1]*64;caseCount++;
  print("DIRECT_WIDE low=24 high=26 equations=",matsize(R)[1]*64," positive_parameter=",2*wp);
  family_check(caseCount==19,"all independent source controls complete");
  print("COMPLETE source_cases=",caseCount," all_coefficient_equations=",total," shared_power_prefixes=true");
};
iferr(run_controls(),E,print(E);quit(1));
quit;
