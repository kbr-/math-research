\\ Compare every stated finite carry with the original degree/length recursion.
\\ Exhaustive deficits in small dimensions and n9,p3; large-prime boundary controls.
assert(c,s)={if(!c,error(s));};
{
my(cases=[[3,3],[3,5],[3,7],[9,3],[10,97]],xs=[0,1,2,19],total=0,done=0);
for(t=1,#cases,my(n=cases[t][1],p=cases[t][2],B=2^(n-1),C=n*B,g=1+(n-3)*B/2,ds=if(p==97,[0,g-1,C-1],[0..C-1]));total+=#xs*p*3*p*#ds);
print("PLANNED_CARRY_COMPARISONS=",total);assert(total<700000,"control budget");gettime();
for(t=1,#cases,
 my(n=cases[t][1],p=cases[t][2],B=2^(n-1),C=n*B,g=1+(n-3)*B/2,ds=if(p==97,[0,g-1,C-1],[0..C-1]),before=done);
 for(xi=1,#xs,my(x=xs[xi]);for(a=0,p-1,for(j=0,2,for(di=1,#ds,my(delta=ds[di],d=n+p*x+a-j,L=B*d-delta);
  assert(min(2,p*min(x,2)+a)==min(2,p*x+a),"flag transition");
  for(r=0,p-1,
   my(jp=-floor((a-j-2*r)/p),dp=B*n+B*floor((a-j-2*r)/p)-ceil((B*(n+a-j)-delta-r)/p),directd=floor((d+(p-1)*n-2*r)/p),directL=ceil((L-r)/p));
   assert(0<=jp && jp<=2,"three-degree window");
   assert(directd==n+x-jp && B*directd-directL==dp,"carry formula");
   assert(dp<C,"faithful range");if(dp<0,assert(directL>B*directd,"zero child"));
   done++
  )
 ))));
 print("CASE n=",n," p=",p," deficit_count=",#ds," comparisons=",done-before)
);
assert(done==total,"count mismatch");print("CARRY_CONTROLS_COMPLETED comparisons=",done," CPU_MS=",gettime())
}
quit;
