\\ Assemble quotient jets with the exact norm/pullback identity and cubic Witt carry modulo9.
default(parisize,256000000);
default(parisizemax,1500000000);
default(nbthreads,1);
T='T;
read("research/tools/bmd_witt_jets_20261008.gp");
if(getenv("BMD_WITT_ORDER")=="8",read("research/results/bmd-exception-cubic-obstruction-20261008/characters8-input.gp"),read("research/results/bmd-exception-cubic-obstruction-20261008/characters-input.gp"));
read("research/tools/bmd_root_cochains_20261008.gp");
{
my(start=getwalltime(),order=#JW_CHARACTERS[1][5][1],pilot=(getenv("BMD_WITT_ASSEMBLY_STAGE")=="pilot"),selected=if(pilot,[1],[2..30]),a=ffgen(Mod(1,3)*(a^3+2*a+2),'a),one=a^0,b='b,a9=Mod(Mod(1,9)*b,b^3-b-1),one9=a9^0,field=vector(27,i,one*((i-1)%3)+a*(((i-1)\3)%3)+a^2*((i-1)\9)),lifted=vector(27,i,one9*((i-1)%3)+a9*(((i-1)\3)%3)+a9^2*((i-1)\9)),codes=Map(),P9=vector(512),R9=vector(512),I9=vector(512),P3=vector(512),R3=vector(512),I3=vector(512),rr9=vector(9),N=12,out=getenv("BMD_WITT_ASSEMBLY_OUT"));
for(i=1,27,mapput(codes,Str(field[i]),i-1));
for(i=1,9,
 my(v=vector(N));v[1]=one9;
 for(j=1,N-1,v[j+1]=(if(j==1,a9^(i-1),0*one9)-sum(k=1,j-1,v[k+1]*v[j-k+1]))/2);
 rr9[i]=sum(j=0,N-1,v[j+1]*T^j);
 jw_assert(jc_cut(rr9[i]^2,N)==one9+a9^(i-1)*T,"lifted square-root identity");
);
P9[1]=one9;R9[1]=one9;I9[1]=one9;P3[1]=one;R3[1]=one;I3[1]=one;
for(S=1,511,
 my(bit=valuation(S,2));P9[S+1]=P9[S-2^bit+1]*(one9+a9^bit*T);R9[S+1]=jc_cut(R9[S-2^bit+1]*rr9[bit+1],N);I9[S+1]=truncate(1/(R9[S+1]+O(T^N)));
 P3[S+1]=P3[S-2^bit+1]*(one+a^bit*T);R3[S+1]=truncate(sqrt(P3[S+1]+O(T^9)));I3[S+1]=truncate(1/(R3[S+1]+O(T^9)));
);
write(out,"CUBIC_EXPONENTS := ",vector(#selected,i,JW_EXPONENTS[selected[i]]),";");
write(out,"CUBIC_CHARACTERS := ",vector(#JW_CHARACTERS,i,JW_CHARACTERS[i][1]),";");write(out,"CUBIC_STATES := [");
for(ci=1,#selected,
 my(si=selected[ci],X=vector(512,i,0*one9),cube,states=vector(466));
 for(i=1,466,states[i]=JW_CHARACTERS[i][5][si]);
 for(block=1,if(order==8,2,1),
 X=vector(512,i,0*one9);
 for(i=1,466,my(row=JW_CHARACTERS[i],v=row[5][si][block]);X[row[1]+1]=sum(j=1,#v,lifted[v[j]+1]*T^(4-j)));
 cube=jc_cube(X,R9,I9,N);
 for(i=1,466,
  my(row=JW_CHARACTERS[i],S=row[1],g=#row[5][si][1],given=row[5][si],self=P9[S+1]*X[S+1]^3,v=vector(g));
  for(j=1,g,
   my(difference=liftall(polcoef(self-cube[S+1],12-j,T)),coeff=vector(3,k,lift(polcoef(difference,k-1,b))));
   jw_assert(vector(3,k,coeff[k]%3)==[0,0,0],"integral cubic carry before division");
   my(code=sum(k=1,3,((coeff[k]\3)%3)*3^(k-1)),selfcoeff=liftall(polcoef(self,12-j,T)),scode=sum(k=0,2,(lift(polcoef(selfcoeff,k,b))%3)*3^k));
   v[j]=mapget(codes,Str(field[given[3*block][j]+1]+field[code+1]+2*field[scode+1]));
  );states[i][3*block]=v;
 );
 );
 if(pilot,
  my(A0=vector(512),H=vector(512),Inf=vector(512));
  for(S=0,511,
   my(g=max(0,(hammingweight(S)-1)\2),inv=I3[S+1]);
   A0[S+1]=2*(polcoef(inv,1,T)*T+polcoef(inv,2,T)*T^2);H[S+1]=if(g,2*one,0*one);Inf[S+1]=if(g,0*one,2*one);
  );
  my(carry=jc_product3(A0+H,H+Inf,A0+Inf,R3,I3,3));
  for(i=1,466,
   my(S=JW_CHARACTERS[i][1],g=#states[i][1]);
   jw_assert(states[i][1]==vector(g,j,if(j==1,2,0)),"direct full Abel first coordinate");
   my(wanty=vector(g,j,mapget(codes,Str(if(2-j>=0,-2*polcoef(I3[S+1],2-j,T),0*one)))),wantv=vector(g,j,mapget(codes,Str(if(3-j>=0,polcoef(carry[S+1],3-j,T),0*one)))));
   jw_assert(states[i][2]==wanty&&states[i][3]==wantv,"direct full Abel versus norm-pullback cubic assembly");
  );
  if(order==8,
   for(S=0,511,
    my(g=max(0,(hammingweight(S)-1)\2),inv=I3[S+1]);
    H[S+1]=-2*sum(j=1,min(g,2),polcoef(inv,2-j,T)*T^(2-j));
    Inf[S+1]=-2*(polcoef(inv,0,T)+polcoef(inv,1,T)*T)-H[S+1];
    A0[S+1]=-2*(inv-polcoef(inv,0,T)-polcoef(inv,1,T)*T);
   );
   carry=jc_product3(A0+H,H+Inf,A0+Inf,R3,I3,6);
   for(i=1,466,
    my(S=JW_CHARACTERS[i][1],g=#states[i][1],want=vector(g,j,mapget(codes,Str(polcoef(carry[S+1],6-j,T)-2*polcoef(I3[S+1],6-j,T)))));
    jw_assert(states[i][6]==want,"direct full Abel second Witt block");
    for(m=4,8,if(m%3,
     want=vector(g,j,mapget(codes,Str(if(m-j>=0,2*polcoef(I3[S+1],m-j,T)/m,0*one))));
     jw_assert(states[i][m]==want,"direct full Abel higher additive coordinates");
    ));
   );
  );
  print("WITT_ASSEMBLY_CONTROL direct_full_Abel=true order=",order," coordinates=",769*order);
 );
 write(out,states,if(ci<#selected,",",""));
 print("WITT_ASSEMBLY exponent=",JW_EXPONENTS[si]," all_character_carries_integral=true wall_ms=",getwalltime()-start);
);
write(out,"];");print("WITT_ASSEMBLY_COMPLETED exponents=",#selected," wall_ms=",getwalltime()-start);
}
quit;
