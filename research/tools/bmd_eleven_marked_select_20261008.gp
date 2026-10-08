\\ Choose an actual marked torsion candidate rather than bounding whole elliptic groups.
default(parisizemax,2500000000);
default(nbthreads,1);
a=ffgen(Mod(1,11)*(x^2+x+1),'a);o=a^0;
field=vector(121,i,o*((i-1)%11)+a*((i-1)\11));
assert(c,s)=if(!c,print("FAIL ",s);quit(1));
ordmark(ids)={my(sl=vector(#ids,j,field[ids[j]+1]),f=prod(j=1,#sl,o+sl[j]*T),t0=-o/sl[1],g=subst(f,T,t0+T),c=vector(4,j,polcoef(g,j,T)),E=ellinit([0*o,c[2],0*o,c[1]*c[3],c[1]^2*c[4]]),P=[c[1]*sl[1],c[1]*sl[1]^2]);assert(ellisoncurve(E,P),"exact marked elliptic model");my(r=ellorder(E,P));assert(ellmul(E,P,r)==[0],"actual point order");return(r);};
fixed=vector(120,k,if(k<=2,0,ordmark([1,2,k])));
best=10^12;chosen=[];orders=[];checked=0;
{for(k=3,119,for(l=k+1,120,if(k<11&&l<11,next);checked++;my(rs=[fixed[k],fixed[l]],ex=lcm(rs[1]/gcd(rs[1],8),rs[2]/gcd(rs[2],8)),bd=lcm(32,8*ex));if(bd>=best,next);
for(v=1,3,my(ids=if(v==1,[1,k,l],if(v==2,[2,k,l],[1,2,k,l])),r=ordmark(ids));rs=concat(rs,r);ex=lcm(ex,r/gcd(r,8));bd=lcm(32,8*ex);if(bd>=best,break));
if(#rs==5 && bd<best,best=bd;chosen=[1,2,k,l];orders=rs;print("IMPROVED slopes=",chosen," marked_orders=",orders," torsion_bound=",best," checked=",checked));if(best==32,break(2));));}
assert(#chosen==4,"nonprime selected input");
write("research/results/bmd-nine-eleven-period-20261008/selected-marked-curve.gp","slCodes=",chosen,";torsionBound=",best,";baseModulus=Mod(1,11)*(x^2+x+1);");
print("COMPLETE marked selection checked=",checked," slopes=",chosen," marked_orders=",orders," bound=",best,"; exact divisor still required.");
