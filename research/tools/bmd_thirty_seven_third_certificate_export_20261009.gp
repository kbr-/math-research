\\ Bounded raw polynomial certificate for independent GAP checks.
default(parisizemax,2500000000);
default(nbthreads,1);
code(z)=lift(z);
read("research/results/bmd-thirty-seven-paired-20261009/paired-data-third.gp");
out="research/results/bmd-thirty-seven-paired-20261009/raw-certificate-third.g";bases=[base3,base4,base5,base6,base7];
write(out,"slCodes := ",apply(code,sl),";");write(out,"phiCodes := ",vector(16,i,vector(81,j,code(polcoef(phi[i],j-1,T)))),";");
for(z=1,#bases,my(M=32*(z+2)-72,b=List());for(mask=0,15,for(j=0,(M-hammingweight(mask))\2,listput(b,[mask,j])));write(out,"frame",z," := ",vector(#b,i,vector(188,j,code(polcoef(bases[z][j][b[i][1]+1],b[i][2],T)))),";"));
print("RAW_CERTIFICATE complete");
