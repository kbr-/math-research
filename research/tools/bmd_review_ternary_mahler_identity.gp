\\ Cheap test of an Outside lead of the goal-level route review of cycle keh (9 October 2026): over F_3,
\\   (1 + aT)^(1/2) = (1 + aT)^2 (1 + a^3 T^3)^(-1/2),
\\ a Mahler-type functional equation w(T) = (1 + aT)^2 / w(a^3; T^3) (since 1/2 = 2 + 3(-1/2) in Z_3 and Frobenius).
\\ Checks the identity coefficientwise in F_3[a] up to T^89, and the recorded Lucas form beta(m) of the left side.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta(m) = { if (m < 0, return(0)); my(d0 = m % 3, t = m \ 3); while(t, if(t % 3 == 2, return(0)); t \= 3); binomial(2, d0) };
{
  my(P = 90, o = Mod(1, 3), L = sqrt(o + o * 'a * 'T + O('T^P)), R = (o + o * 'a * 'T)^2 / sqrt(o + o * 'a^3 * 'T^3 + O('T^P)));
  my(ok = (L == R), lucas = vector(P, k, polcoef(L, k - 1, 'T) == beta(k - 1) * o * 'a^(k - 1)));
  emit(Str("identity (1+aT)^(1/2) = (1+aT)^2 (1+a^3T^3)^(-1/2) over F_3 to T^", P - 1, ": ", ok));
  emit(Str("Lucas form beta(m) a^m for all m < ", P, ": ", vecmin(lucas) == 1));
}
quit;
