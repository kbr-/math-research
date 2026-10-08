\\ Bounded raw polynomial certificate for independent GAP checks.
default(parisizemax,2500000000);
default(nbthreads,1);
a=ffgen(Mod(1,5)*(x^2+x+1),'a);o=a^0;
field=vector(25,i,o*((i-1)%5)+a*((i-1)\5));
code(z)={for(i=1,25,if(z==field[i],return(i-1)));error("field code");};
firstcurve=if(getenv("BMD_QUINARY_CERT")=="fourth",3,1);lastcurve=if(firstcurve==3,3,2);
{for(curve=firstcurve,lastcurve,
read(Str("research/results/bmd-nine-quinary-period-20261008/paired-data",["-second","-third","-fourth"][curve],".gp"));
my(out=Str("research/results/bmd-nine-quinary-period-20261008/raw-certificate",["-second","-third","-fourth"][curve],".g"),bases=if(curve==3,[base3,base4,base5,base6,base7],[base3,base4,base5]));
write(out,"slCodes := ",apply(code,sl),";");write(out,"phiCodes := ",vector(16,i,vector(if(curve==3,81,49),j,code(polcoef(phi[i],j-1,T)))),";");
for(z=1,#bases,my(M=32*(z+2)-72,b=List());for(mask=0,15,for(j=0,(M-hammingweight(mask))\2,listput(b,[mask,j])));write(out,"frame",z," := ",vector(#b,i,vector(188,j,code(polcoef(bases[z][j][b[i][1]+1],b[i][2],T)))),";"));
print("RAW_CERTIFICATE curve=",curve," complete");)}
