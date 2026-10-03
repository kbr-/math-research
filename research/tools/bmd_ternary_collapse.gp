\\ Sequential collapse of labels into the dummy label 0 (cycle bmd-20261009-ab, 9 October 2026).
\\ beta(m) = [x^m](1+x)^(1/2) mod 3; A = {beta != 0}. State: P = exponents of pure T-power rows, Q = exponents q of
\\ the rows T^q w_j shared by all remaining labels. Start P = {0,1}, Q = {0}. Step (one label -> 0): its own rows
\\ T^q w_m (q in Q) contribute pure powers T^t on a set S of |Q| exponents outside P, with leading coefficient
\\ det[beta(t - q)]_{q in Q, t in S}; the least a_m-order uses the minimal Sigma S with nonzero minor; its pair rows
\\ become T^alpha w_j with alpha the least element of A outside Q. Then P = P u S, Q = Q u {alpha}.
\\ Tested statement (greedy chain; the simulation places no cap at D, so beyond step 4 it does not model any fixed Delta_n): at every step the
\\ minimal-sum S with nonzero minor is unique, and the final P is {0, ..., D-1}, D = binom(n+1,2) + 2.
\\ Search for S: subsets of the first |Q| + XS exponents outside P (XS extra), all of them.
OUT = "research/results/bmd-20261009-ab/collapse.txt";
beta(m) = { if (m < 0, return(0)); my(d0 = m % 3, t = m \ 3); while(t, if(t % 3 == 2, return(0)); t \= 3); binomial(2, d0) };
XS = 8;
step(P, Q) = {
  my(k = #Q, avail = List(), t = 0);
  while(#avail < k + XS, if(!setsearch(P, t), listput(avail, t)); t++);
  avail = Vec(avail);
  my(best = 10^9, cnt = 0, bestS = 0);
  forsubset([#avail, k], I, my(S = vector(k, i, avail[I[i]]), s = vecsum(S));
    if (s <= best, my(d = matdet(matrix(k, k, a, b, Mod(beta(S[b] - Q[a]), 3))));
      if (d != 0, if (s < best, best = s; cnt = 1; bestS = S, cnt++))));
  [bestS, cnt, best];
};
nextA(Q) = { my(m = Q[#Q] + 1); while(!beta(m), m++); m };
{
  my(P = [0, 1], Q = [0], log = List(), fail = 0);
  for (c = 0, 13, my(r = step(P, Q), S = r[1]);
    if (S == 0, write(OUT, "step ", c + 1, ": no nonzero minor among the first |Q| + ", XS, " free exponents"); fail = 1; break);
    my(gap = Set(S) != Set([vecmin(S) .. vecmax(S)]) || vecmin(S) != #P);
    listput(log, [c + 1, S, r[2], gap]);
    P = setunion(P, Set(S)); Q = concat(Q, nextA(Q));
    my(D = (c + 1) * (c + 2) / 2 + 2, interval = (P == Set([0 .. D - 1])));
    write(OUT, "n=", c + 1, ": S = ", if(#S <= 12, S, Str(S[1..3], "...", S[#S - 2..#S])), ", minimizers ", r[2], ", S not the next consecutive block: ", gap, "; P = [0, D-1]: ", interval));
}
