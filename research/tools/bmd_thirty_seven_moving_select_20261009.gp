\\ Test fully split quadratic-field marks on three fixed prime-field curves.
\\ First precompute quotient models/cardinalities and square roots; then exact point orders.
default(parisizemax,1000000000);
default(nbthreads,1);
p=37;a=ffgen(Mod(1,p)*(x^2+x+36),'a);o=a^0;
assert(c,s)=if(!c,print("FAIL ",s);quit(1));
code(z)={my(v=z.pol);lift(polcoef(v,0))+p*lift(polcoef(v,1));};
field=vector(p^2,j,(j-1)%p+((j-1)\p)*a);
sqrts=vector(p^2,j,-1);for(j=1,p^2,sqrts[code(field[j]^2)+1]=j-1);
curves=[[1,2,14,25],[1,2,7,32],[1,2,6,33]];best=10^12;selected=[];checked=0;split=0;
{for(ci=1,#curves,my(sl=curves[ci]*o,models=List());
for(mask=0,15,if(hammingweight(mask)>=3,my(ids=select(i->bittest(mask,i-1),[1,2,3,4]),f=prod(j=1,#ids,o+sl[ids[j]]*T),t0=-o/sl[ids[1]],g=subst(f,T,t0+T),c=vector(4,j,polcoef(g,j,T)),E=ellinit([0*o,c[2],0*o,c[1]*c[3],c[1]^2*c[4]]),card=ellcard(E));listput(models,[ids,t0,c[1],E,card]);print("QUOTIENT curve=",ci," mask=",mask," cardinality=",card)));
for(tc=p,p^2-1,checked++;my(t=field[tc+1],rs=vector(4,i,sqrts[code(o+sl[i]*t)+1]));
if(vecmin(rs)<=0,next);split++;my(roots=vector(4,i,field[rs[i]+1]),orders=vector(5),ex=1);
for(j=1,5,my(md=models[j],xx=md[3]/(t-md[2]),yy=md[3]*prod(k=1,#md[1],roots[md[1][k]])/(t-md[2])^2,P=[xx,yy],E=md[4]);assert(ellisoncurve(E,P),"marked quotient equation");my(r=ellorder(E,P,md[5]));assert(ellmul(E,P,r)==[0],"exact point order");orders[j]=r;ex=lcm(ex,r/gcd(r,8)));
my(bd=lcm(32,8*ex),normalized=vector(4,i,sl[i]/(o+sl[i]*t)));assert(#Set(normalized)==4,"distinct normalized slopes");
for(i=1,4,assert(sqrts[code(normalized[i])+1]>=0,"infinity remains quadratic split");for(j=1,4,if(i!=j,assert(sqrts[code(o-normalized[j]/normalized[i])+1]>=0,"branch remains quadratic split"))));
print("MARK curve=",ci," t_code=",tc," root_codes=",rs," slope_codes=",vector(4,i,code(normalized[i]))," marked_orders=",orders," bound=",bd);
if(bd<best,best=bd;selected=[ci,tc,rs,vector(4,i,code(normalized[i])),orders]);
));}
assert(checked==3996,"all non-prime-field base coordinates on three curves");
write("research/results/bmd-thirty-seven-moving-mark-20261009/selected-mark.gp","selected=",selected,";torsionBound=",best,";");
print("COMPLETE base_coordinates=",checked," fully_split_marks_up_to_signs=",split," smallest_bound=",best," selected=",selected);
quit;
