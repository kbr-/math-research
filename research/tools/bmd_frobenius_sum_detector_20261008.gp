\\ Test a sufficient effective scalar detector for the actual three-orbit theta family.
\\ On the certified ordinary n9/F_(3^8) curve, find an elliptic character with trace1mod9.
\\ Then its unit Frobenius root is1mod9 and its other root has3-adic valuation8.
\\ Stages: at most84 degree3 quotient counts; stop at first detector; independent full Fq count.
\\ Earlier466 genus<=4 quotient counts overF27 took1.6s; at most84 genus1 counts fit20s.
default(parisizemax,500000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
{
my(p=3,e=8,q=p^e,modulus=ffinit(p,e,'a),a=ffgen(modulus,'a),one=a^0,lc=[508,5690,5164,3098,2894,6147,276,4463,174],labels=apply(c->sum(j=0,7,(c\3^j)%3*a^j),lc),found=0,tested=0,start=getwalltime());
assert(vector(9,j,lift(polcoef(modulus,j-1)))==[1,2,2,1,0,0,2,1,1],"same ordinary field presentation");
assert(#Set(labels)==9 && prod(i=1,9,labels[i])!=0,"same admissible root tuple");
for(S=1,511,if(hammingweight(S)==3,
 tested++;
 my(poly=prod(i=1,9,if(bittest(S,i-1),one+labels[i]*T,one)),cp=hyperellcharpoly(poly),tr=-polcoef(cp,1));
 assert(poldegree(cp)==2 && polcoef(cp,0)==q,"elliptic Frobenius polynomial");
 print("ELLIPTIC_TRACE subset=",S," trace=",tr," residue9=",tr%9);
 if(tr%9==1,
  my(field=vector(q,j,sum(k=0,e-1,((j-1)\p^k)%p*a^k)),count=q+1);
  for(j=1,q,my(v=subst(poly,T,field[j]));if(v!=0,count+=if(v^((q-1)/2)==one,1,-1)));
  assert(count==q+1-tr,"independent full finite-field point count");
  print("SCALAR_DETECTOR subset=",S," field_modulus=",modulus," label_codes=",lc);
  print("QUOTIENT_POLYNOMIAL=",poly," FROBENIUS_POLYNOMIAL=",cp," RATIONAL_POINTS=",count);
  print("DETECTOR_DATA unit_root_mod9=1 nonunit_valuation3=8 allowed_positive_total_weight_at_most=8");
  found=1;break
 )
));
assert(found,"no trace1mod9 detector in the bounded elliptic inventory");
print("FROBENIUS_SUM_DETECTOR_COMPLETED tested=",tested," wall_ms=",getwalltime()-start);
}
quit;
