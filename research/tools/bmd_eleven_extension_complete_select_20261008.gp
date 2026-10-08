\\ Choose an extension-field input with five order128 elliptic quotients.
\\ This is only input selection; the exact divisor will be constructed separately.
default(parisizemax,2500000000);
default(nbthreads,1);
a=ffgen(Mod(1,11)*(x^2+x+1),'a);o=a^0;
field=vector(121,i,o*((i-1)%11)+a*((i-1)\11));
chi(z)=if(z==0,0,if(z^60==o,1,-1));
val=matrix(120,121,i,j,o+field[i+1]*field[j]);
countcurve(ids)={my(s=vector(#ids,j,field[ids[j]+1]),n=if(#ids%2,1,1+chi(prod(j=1,#s,s[j]))));for(z=1,121,n+=1+chi(prod(j=1,#ids,val[ids[j],z])));return(n);};
chosen=[];checked=0;
{for(b=3,118,my(elig=List());for(k=b+1,120,if(countcurve([1,b,k])==128,listput(elig,k)));
for(i=1,#elig,for(j=i+1,#elig,my(k=elig[i],l=elig[j]);if(b<11&&k<11&&l<11,next);checked++;if(countcurve([1,k,l])==128&&countcurve([b,k,l])==128&&countcurve([1,b,k,l])==128,chosen=[1,b,k,l];break(3))));print("SECOND ",b," eligible=",#elig," checked=",checked));}
print("SELECTION checked_pairs=",checked," chosen=",chosen);
if(#chosen==4,write("research/results/bmd-nine-eleven-period-20261008/selected-extension-curve.gp","slCodes=",chosen,";torsionBound=128;baseModulus=Mod(1,11)*(x^2+x+1);"));
print("COMPLETE bounded input selection; not an original normality test.");
