\\ Bounded raw polynomial certificate for independent GAP checks.
default(parisizemax,2500000000);
default(nbthreads,1);
a=ffgen(Mod(1,3)*(x^2+1),'a);o=a^0;
field=vector(9,i,o*((i-1)%3)+a*((i-1)\3));
code(z)={for(i=1,9,if(z==field[i],return(i-1)));error("field code");};
{for(curve=0,1,
read(Str("research/results/bmd-exception-outside-coverage-20261008/paired-data",if(curve,"-second",""),".gp"));
my(out=Str("research/results/bmd-exception-outside-coverage-20261008/raw-certificate",if(curve,"-second",""),".g"),bases=[base3,base4,base5]);
write(out,"slCodes := ",apply(code,sl),";");write(out,"phiCodes := ",vector(16,i,vector(49,j,code(polcoef(phi[i],j-1,T)))),";");
for(z=1,3,my(M=32*(z+2)-72,b=List());for(mask=0,15,for(j=0,(M-hammingweight(mask))\2,listput(b,[mask,j])));write(out,"frame",z," := ",vector(#b,i,vector(188,j,code(polcoef(bases[z][j][b[i][1]+1],b[i][2],T)))),";"));
print("RAW_CERTIFICATE curve=",curve," complete");)}
