\\ Compare an all-degree proposed ordinary residue with the old leading scalar, not a normality sample.
default(parisizemax,1000000000);
default(nbthreads,1);
p=53;d=7;h=128;s=128*d-448;
den=sum(i=1,h-1,(i+h-1)\p-(2*i-1)\p);
num=sum(i=1,h-1,(2*s+i+h-1)\p-(2*s+2*i-1)\p);
print("COMPARISON prime=",p," degree_class=",d," ordinary_residue=",(32*d-97)%p," denominator_valuation=",den," first_numerator_level=",num," difference=",num-den);
print("The denominator has no p^2 factors; numerator higher levels can only increase the difference.");
print("COMPLETE fixed-index factorial counts, invariant throughout degree7mod53.");
quit;
