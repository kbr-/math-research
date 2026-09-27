-- Check the characteristic-zero hypothesis of the new coefficient-base lemma.
-- For ordered multiplicities3,2 at N5 in characteristic3, trace forces c=0
-- and p=(Z-b)^3 Z^2=Z^5-b^3 Z^2. The proposed parameter c2 vanishes, so
-- the zero fibre is a line. This does not refute odd-field cube normality.
arR=ZZ/3[b,z];arP=(z-b)^3*z^2;
assert(arP==z^5-b^3*z^2);
assert(coefficient(z^3,arP)==0);
<< "POLYNOMIAL=" << toString arP << " C2=" << coefficient(z^3,arP)
   << " ZERO_FIBRE_DIMENSION=1 CHARACTERISTIC=3" << endl;
exit 0;
