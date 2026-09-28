\\ Test the general proposal that moving the mark can repair an additive
\\ subgroup's fixed-mark defect, before attempting an all-size proof.
\\ Smallest nontrivial subgroup: 9 labels; R=36, original D=38.
\\ Work in F81 so the ambient field-size pure-power relation lies beyond R.
\\ Stages: construct one additive plane; audit its linearized polynomial;
\\ fixed-mark negative control; at most three prescribed moving marks,
\\ stopping on first success; independently audit original square-root jets.
\\ This is not a dimension or order series. All output is promoted verbatim.
{
my(pp=ffinit(3,4,'z),t=ffgen(pp,'t),one=t^0);
my(labels=vector(9,i,((i-1)%3+((i-1)\3)*t)*one));
my(pairs=List());for(i=1,9,for(j=i+1,9,listput(pairs,[i,j])));pairs=Vec(pairs);
if(#Set(labels)!=9,error("labels are not distinct"));
my(X='X,addpoly=prod(i=1,9,X-labels[i]));
my(A=1+(t^3-t)^2,B=(t^3-t)^2);
if(addpoly!=X^9-A*X^3+B*X,error("linearized polynomial failed"));
print("FIELD_POLYNOMIAL = ",pp);
print("LABELS = ",labels);
print("ADDITIVE_POLYNOMIAL = ",addpoly);
print("PAIR_RANK = 36; ORIGINAL_DIMENSION = 38; FIXED_DEFECT_BOUND = 1");
my(marks=[0*one,t^2,t^3,t^2+t],success=0,checked=0);
for(mi=1,#marks,
 my(tau=marks[mi]);
 if(prod(i=1,9,1+labels[i]*tau)==0,
   print("MARK = ",tau," SKIPPED_RAMIFIED = 1");next);
 my(aa=vector(9,i,labels[i]/(1+labels[i]*tau)),Q=matrix(36,36));
 for(row=1,36,
   my(i=pairs[row][1],j=pairs[row][2],s=aa[i]+aa[j],delta=(aa[i]-aa[j])^2);
   Q[row,1]=one;
   for(l=1,35,Q[row,l+1]=s*Q[row,l]+delta*sum(h=0,l-2,Q[row,h+1]*Q[row,l-1-h])));
 my(rank=matrank(Q),det=matdet(Q));
 if((rank==36)!=(det!=0),error("rank/determinant mismatch"));
 if(mi==1,
   if(rank>35,error("fixed-mark obstruction failed"));
   if(Q[,10]-A*Q[,4]+B*Q[,2]!=vector(36)~,error("linearized column relation failed")));
 \\ Independent encoding: form each original square root recursively,
 \\ multiply the two root series, then compare all 1296 pair coefficients.
 my(W=matrix(9,38));
 for(i=1,9,
   W[i,1]=one;
   for(l=1,37,W[i,l+1]=(if(l==1,aa[i],0*one)-sum(j=1,l-1,W[i,j+1]*W[i,l-j+1]))/2));
 for(row=1,36,
   my(i=pairs[row][1],j=pairs[row][2],delta=(aa[i]-aa[j])^2);
   for(l=0,35,
     my(raw=sum(h=0,l+2,W[i,h+1]*W[j,l+3-h]));
     if(raw!=delta*Q[row,l+1],error("original source coefficient mismatch"));
     checked++));
 my(wrong=Q[1,1]+one);
 if((aa[1]-aa[2])^2*wrong==sum(h=0,2,W[1,h+1]*W[2,3-h]),
   error("negative encoding control missed"));
 print("MARK = ",tau," PAIR_RANK = ",rank," PAIR_DETERMINANT = ",det,
       " ORIGINAL_JET_RANK = ",rank+2);
 if(mi>1 && rank==35,
   my(ker=matker(Q));
   if(Q*ker!=matrix(36,1),error("kernel certificate failed"));
   print("MARKED_KERNEL_SUPPORT = ",select(j->ker[j+1,1]!=0,vector(36,j,j-1)));
   print("MARKED_KERNEL_VECTOR = ",ker[,1]));
 if(rank==36,success=1;break));
print("ENCODING_ENTRIES_CHECKED = ",checked);
print("ALTERED_COEFFICIENT_DETECTED = 1");
print("MOVING_MARK_SUCCESS = ",success);
print("ADDITIVE_MOVING_CONTROL_COMPLETED");
}
quit;
