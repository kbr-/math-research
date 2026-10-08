\\ Construct one ordinary n9 root curve over F_(3^8).
\\ Named test: all 466 character Cartier blocks must be invertible (total genus769).
\\ Stages: bounded tuple search; exact block determinants; portable field-code export.
\\ 20 tuples maximum; each has512 cached polynomials of degree<=9 and466 matrices of size<=4.
\\ Earlier 466 quotient point counts took1.6s; these tiny coefficient determinants need no counting.
default(parisizemax,500000000);
default(nbthreads,1);
setrand(20261008);
assert(c,s)={if(!c,error(s));};
{
my(p=3,e=8,q=p^e,n=9,modulus=ffinit(p,e,'a),a=ffgen(modulus,'a),one=a^0,field=vector(q,j,sum(k=0,e-1,((j-1)\p^k)%p*a^k)),codes=Map(),found=0,start=getwalltime());
for(j=1,q,mapput(codes,Str(field[j]),j-1));
assert(#Set(field)==q && polisirreducible(modulus),"finite field presentation");
for(trial=1,20,
 my(labelcodes=vector(n,i,1+random(q-1)),labels=apply(c->field[c+1],labelcodes));
 while(#Set(labelcodes)<n,labelcodes=vector(n,i,1+random(q-1));labels=apply(c->field[c+1],labelcodes));
 my(polys=vector(2^n),dcodes=List(),bad=0,genus=0,blocks=0);polys[1]=one;
 for(S=1,2^n-1,
  my(bit=valuation(S,2));polys[S+1]=polys[S-2^bit+1]*(one+labels[bit+1]*T);
  my(g=floor((hammingweight(S)-1)/2));
  if(g>0,my(H=matrix(g,g,i,j,polcoef(polys[S+1],3*(i-1)+2-(j-1),T)),det=matdet(H));blocks++;genus+=g;if(det==0,bad++);listput(dcodes,[S,mapget(codes,Str(det))]))
 );
 print("ORDINARY_TRIAL=",trial," singular_blocks=",bad," blocks=",blocks," total_genus=",genus);
 assert(blocks==466 && genus==769,"full positive-genus character inventory");
 if(bad==0,
  my(out="research/results/bmd-exception-ordinary-extraction-20261008/ordinary-data.g");
  write(out,"ORDINARY_FIELD_POLY := ",vector(e+1,j,lift(polcoef(modulus,j-1))),";");
  write(out,"ORDINARY_LABEL_CODES := ",labelcodes,";");
  write(out,"ORDINARY_DET_CODES := ",Vec(dcodes),";");
  print("ORDINARY_FIELD_MODULUS=",modulus);
  print("ORDINARY_LABEL_CODES=",labelcodes," labels=",labels);
  print("ORDINARY_DATA_PATH=",out);
  found=1;break
 )
);
assert(found,"no ordinary tuple in bounded search; do not claim a certificate");
print("ORDINARY_NINE_COMPLETED all466blocks_invertible genus769 wall_ms=",getwalltime()-start);
}
quit;
