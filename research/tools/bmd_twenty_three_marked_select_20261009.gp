\\ Choose an actual marked torsion candidate rather than bounding whole elliptic groups.
default(parisizemax,2500000000);
default(nbthreads,1);
o=Mod(1,23);field=vector(23,i,o*(i-1));
assert(c,s)=if(!c,print("FAIL ",s);quit(1));
ordmark(ids)={my(sl=vector(#ids,j,field[ids[j]+1]),f=prod(j=1,#sl,o+sl[j]*T),t0=-o/sl[1],g=subst(f,T,t0+T),c=vector(4,j,polcoef(g,j,T)),E=ellinit([0*o,c[2],0*o,c[1]*c[3],c[1]^2*c[4]]),P=[c[1]*sl[1],c[1]*sl[1]^2]);assert(ellisoncurve(E,P),"exact marked elliptic model");my(r=ellorder(E,P));assert(ellmul(E,P,r)==[0],"actual point order");return(r);};
best=10^12;chosen=[];orders=[];checked=0;
{for(b=2,20,for(k=b+1,21,for(l=k+1,22,my(ids=[1,b,k,l],rs=List(),ex=1);
for(mask=0,15,if(hammingweight(mask)>=3,my(sub=select(i->bittest(mask,i-1),[1,2,3,4]),r=ordmark(vector(#sub,j,ids[sub[j]])));listput(rs,r);ex=lcm(ex,r/gcd(r,8))));
my(bd=lcm(32,8*ex));checked++;print("INPUT ",ids," marked_orders=",Vec(rs)," bound=",bd);
if(bd<best,best=bd;chosen=ids;orders=Vec(rs));
)));}
assert(checked==1330,"complete normalized prime-field search");
write("research/results/bmd-twenty-three-paired-20261009/selected-curve.gp","slCodes=",chosen,";torsionBound=",best,";");
print("COMPLETE selected=",chosen," marked_orders=",orders," bound=",best," inputs=",checked);
