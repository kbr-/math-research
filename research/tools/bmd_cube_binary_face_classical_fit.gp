\\ Structure of the binary-face Weierstrass numerators W_M(T), M = 3..6, from
\\ bmd_cube_binary_face_wronskian.gp (monic, non-branch part of the limit-space Wronskian).
\\ Test: does W_M satisfy a second-order Heine-Stieltjes equation
\\   A(T) W'' + B(T) W' + C(T) W = 0,  deg A <= 3, deg B <= 2, deg C <= 1,
\\ and where does A vanish? If A vanishes only at branch values or where W does not vanish, all
\\ zeros of W off those points are simple (a double zero would force W = 0 by uniqueness).
\\ Solved exactly as a linear system over Q; the kernel is printed.

OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
W = [ 'T^3 + 3/4*'T, 'T^6 + 15/4*'T^4 + 15/8*'T^2 + 5/64, 'T^10 + 45/4*'T^8 + 105/4*'T^6 + 525/32*'T^4 + 315/128*'T^2 + 21/512, 'T^15 + 105/4*'T^13 + 1365/8*'T^11 + 25025/64*'T^9 + 45045/128*'T^7 + 63063/512*'T^5 + 15015/1024*'T^3 + 6435/16384*'T ];
main() = {
  for (i = 1, #W,
    my(M = i + 2, w = W[i], n = poldegree(w));
    \\ unknowns: A = a0..a3, B = b0..b2, C = c0..c1
    my(basis = concat([vector(4, j, 'T^(j-1) * deriv(deriv(w))), vector(3, j, 'T^(j-1) * deriv(w)), vector(2, j, 'T^(j-1) * w)]));
    my(mat = matrix(n + 2, #basis, r, c, polcoeff(basis[c], r - 1, 'T)));
    my(K = matker(mat));
    emit(Str("M=", M, " n=", n, " kernel dimension=", #K));
    for (c = 1, #K,
      my(v = K[, c], A = sum(j = 1, 4, v[j] * 'T^(j-1)), B = sum(j = 1, 3, v[4+j] * 'T^(j-1)), C = sum(j = 1, 2, v[7+j] * 'T^(j-1)));
      my(s = content([A, B, C]));
      A /= s; B /= s; C /= s;
      emit(Str("  A=", factor(A), "  B=", B, "  C=", C))));
}
main();
\\ Comparison with Q_r: D^r (1-T^2)^(-3/2) = (1-T^2)^(-3/2-r) Q_r(T), computed by the recurrence
\\ Q_0 = 1, Q_1 = 3T, Q_(k+1) = (2k+3) T Q_k + k(k+2)(1-T^2) Q_(k-1).
Qr(n) = { my(a = 1, b = 3*'T, c); if (n == 0, return(a)); for (k = 1, n - 1, c = (2*k+3)*'T*b + k*(k+2)*(1-'T^2)*a; a = b; b = c); b; };
compareQ() = {
  for (i = 1, #W,
    my(M = i + 2, n = binomial(M, 2), q = Qr(n));
    emit(Str("M=", M, " r=", n, " monic Q_r equals W_M: ", q / pollead(q) == W[i],
      "; G(Q_r)=0: ", ('T^2-1)*deriv(deriv(q)) - (2*n+1)*'T*deriv(q) + n*(n+2)*q == 0)));
}
compareQ();
