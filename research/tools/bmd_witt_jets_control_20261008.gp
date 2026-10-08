\\ Nonvacuous direct expansion controls at q1,3,9,27, across genera1..4 and an even-degree curve.
default(parisizemax,1000000000);
default(nbthreads,1);
T='T;
read("research/tools/bmd_witt_jets_20261008.gp");
{
my(start=getwalltime(),a=ffgen(Mod(1,3)*(a^3+2*a+2),'a),one=a^0,masks=[7,83,31,127,511],cases=0);
for(ci=1,#masks,
 my(S=masks[ci],P=prod(i=0,8,if(bittest(S,i),one+a^i*T,one)),g=(hammingweight(S)-1)\2,state=jw_initial(P,g,1));
 for(s=1,3,
  state=jw_step(state,P,g);my(direct=jw_initial(P,g,3^s));
  jw_assert(state==direct,"coefficientwise Frobenius versus direct normalized Abel cocycle");cases++;
  print("WITT_JET_CONTROL mask=",S," genus=",g," exponent=",s," all_three_coordinates=true");
 );
);
print("WITT_JET_CONTROL_COMPLETED cases=",cases," wall_ms=",getwalltime()-start);
}
quit;
