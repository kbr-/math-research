-- Tor_1^{F3[w]/w^3}(F3, M)_d = ker(l: M_{d-1}->M_d) / l^2 M_{d-3}, for quotients of F3[a,u,b,v]
R = ZZ/3[a,u,b,v];
tor1 = (I, l, dmax) -> (
  Q := R/I; lq := sub(l, Q);
  apply(toList(1..dmax), d -> (
    B1 := basis(d-1, Q); B0 := basis(d, Q);
    if numcols B1 == 0 then return 0;
    K := if numcols B0 == 0 then numcols B1 else numcols B1 - rank last coefficients(lq*B1, Monomials => B0);
    Im := if d < 3 then 0 else (B3 := basis(d-3, Q); if numcols B3 == 0 then 0 else rank last coefficients(lq^2*B3, Monomials => B1));
    K - Im)));
I2 = ideal(a^3,u^3,b^3,v^3,a*u^2,b*v^2);
print("a+b on (au2,bv2), d=1..8: " | toString tor1(I2, a+b, 8));
I1 = ideal(a^3,u^3,b^3,v^3,a*u^2);
print("u on (au2), d=1..8: " | toString tor1(I1, u, 8));
print("a on (au2), d=1..8: " | toString tor1(I1, a, 8));
exit 0
