b(t) = if (t >= 0, binomial(t + 3, 3), 0);
h(t) = b(t-5) + b(t-6) + 2*b(t-7) + b(t-8) - b(t-10) - b(t-11) - b(t-12);
chi(t) = 2*binomial(t + 3, 3) - 71*(t + 2) + 420;
print("h0(E(l)), l = 0..12: ", vector(13, l, h(l - 1)));
print("h2(E(l)) = chi - h0, l = 0..12: ", vector(13, l, chi(l - 1) - h(l - 1)));
\\ spectrum multiplicities from h2: f(l) - f(l+1) = #{m >= l+3}
f = vector(13, l, chi(l - 1) - h(l - 1));
print("#{m >= l+3}, l = 0..11: ", vector(12, l, f[l] - f[l + 1]));
quit;
