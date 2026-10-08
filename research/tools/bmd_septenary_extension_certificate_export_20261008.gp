\\ Bounded raw polynomial certificate for independent GAP checks.
default(parisizemax,2500000000);
default(nbthreads,1);
a=ffgen(Mod(1,7)*(x^2+x+6),'a);o=a^0;
field=vector(49,i,o*((i-1)%7)+a*((i-1)\7));
code(z)={for(i=1,49,if(z==field[i],return(i-1)));error("field code");};
read("research/results/bmd-nine-septenary-period-20261008/paired-data-third.gp");
out="research/results/bmd-nine-septenary-period-20261008/raw-certificate-third.g";bases=[base3,base4,base5];
write(out,"slCodes := ",apply(code,sl),";");write(out,"phiCodes := ",vector(16,i,vector(49,j,code(polcoef(phi[i],j-1,T)))),";");
for(z=1,#bases,my(M=32*(z+2)-72,b=List());for(mask=0,15,for(j=0,(M-hammingweight(mask))\2,listput(b,[mask,j])));write(out,"frame",z," := ",vector(#b,i,vector(188,j,code(polcoef(bases[z][j][b[i][1]+1],b[i][2],T)))),";"));
print("RAW_CERTIFICATE complete");
