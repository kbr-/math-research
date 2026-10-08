\\ Through order8 the multiplicative group has two length-two Witt blocks and four additive blocks.
default(parisizemax,1000000000);
default(nbthreads,1);
T='T;
read("research/tools/bmd_witt_jets_20261008.gp");
read("research/results/bmd-exception-cubic-obstruction-20261008/characters-input.gp");
jw_direct8(P,g,q)={
 my(r=truncate(1/sqrt(P+O(T^(8*q)))),first=jw_initial(P,g,q),second=jw_initial(P,g,2*q),v=vector(8));
 v[1]=first[1];v[2]=-second[1];v[3]=first[3];v[6]=-second[3]-jw_proj(r/(2*T^(6*q)),g);
 for(m=4,8,if(m%3,v[m]=jw_proj(r/(2*m*T^(m*q)),g)));v;
};
jw_step8(v,P,g)={
 my(first=jw_step([v[1],0,v[3]],P,g),second=jw_step([v[2],0,v[6]],P,g),ans=vector(8));
 ans[1]=first[1];ans[3]=first[3];ans[2]=second[1];ans[6]=second[3];
 for(m=4,8,if(m%3,ans[m]=jw_proj(P*v[m]^3,g)));ans;
};
{
my(start=getwalltime(),a=ffgen(Mod(1,3)*(a^3+2*a+2),'a),one=a^0,field=vector(27,i,one*((i-1)%3)+a*(((i-1)\3)%3)+a^2*((i-1)\9)),codes=Map(),infos=vector(4,g,jw_info(g,one)),out="research/results/bmd-exception-cubic-obstruction-20261008/characters8.g",controls=0);
for(i=1,27,mapput(codes,Str(field[i]),i-1));
my(Z='Z,E=exp(Z+Z^3/3+O(Z^9)),ec=vector(9,i,Mod(polcoef(E,i-1,Z),3)),scalar=prod(m=1,8,if(m==3,1,subst(sum(k=0,8,ec[k+1]*Z^k),Z,Mod(if(m==6,2,if(m%3==1,1,2)),3)*Z^m))));
jw_assert(valuation(scalar-sum(k=0,8,Mod(1,3)*Z^k),Z)>=9,"universal Abel factorization through order8");
write(out,"JET8_EXPONENTS := ",JW_EXPONENTS,";");write(out,"JET8_E := ",vector(9,i,lift(ec[i])),";");write(out,"JET8_CHARACTERS := [");
for(ci=1,466,
 my(row=JW_CHARACTERS[ci],S=row[1],P=sum(i=1,#row[2],field[row[2][i]+1]*T^(i-1)),g=#row[3],D=matrix(g,g,i,j,field[row[3][i][j]+1]),sz=#row[4],L=matrix(sz,sz,i,j,field[row[4][i][j]+1]),dp=vector(14),lp=vector(14),initial=jw_direct8(P,g,1),states=vector(30));
 dp[1]=D;lp[1]=L;for(j=2,14,dp[j]=dp[j-1]^2;lp[j]=lp[j-1]^2);
 if(setsearch([7,31,83,127,511],S),
  my(st=initial);for(s=1,3,st=jw_step8(st,P,g);jw_assert(st==jw_direct8(P,g,3^s),"direct all-eight Abel coordinates");controls++);
 );
 for(si=1,30,
  my(s=JW_EXPONENTS[si],v=vector(8),first=jw_fast([initial[1],0,initial[3]],s,P,g,infos[g],dp,lp),second=jw_fast([initial[2],0,initial[6]],s,P,g,infos[g],dp,lp));
  v[1]=first[1];v[3]=first[3];v[2]=second[1];v[6]=second[3];
  for(m=4,8,if(m%3,
   my(w=jw_poly(jw_power_vector(dp,s\3,jw_vector(initial[m],g))));for(j=1,s%3,w=jw_proj(P*w^3,g));v[m]=w;
  ));
  states[si]=vector(8,m,vector(g,j,mapget(codes,Str(jw_coeff(v[m],-j)))));
  jw_assert(states[si][1]==row[5][si][1]&&states[si][2]==row[5][si][2]&&states[si][3]==row[5][si][3],"preserved cubic coordinates");
 );
 if(ci>1,write(out,","));write(out,"[",S,",",states,"]");
);
write(out,"];");print("WITT_EIGHT_EXPORT_COMPLETED characters466 exponents30 direct_controls=",controls," coefficients=",vector(9,i,lift(ec[i]))," wall_ms=",getwalltime()-start);
}
quit;
