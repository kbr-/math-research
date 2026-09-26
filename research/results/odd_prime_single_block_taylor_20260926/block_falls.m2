-- Degree falls of one randomized-prefix block in form-value space.
-- R = F_3[y]/(y^3 - y) is the ring of functions on F_3^h, T = gr R = F_3[y]/(y^3).
-- The clauses g_i Q^C generate I = I(allowed set) in R. Statement tested: gr I = (tops tau_i)
-- iff length T/(tau) equals the number of allowed points |A_C|; a strict excess of the length
-- means clause combinations of lower degree (degree falls), so no list of liftable syzygies
-- generates the top syzygies. Also reports the least degree of gr I (the immunity).
kk = ZZ/3;
out = openOut getenv "BF_OUT";
run1 = (label, h, cs) -> (
    Rt := kk[y_1..y_h];
    Y := gens Rt;
    T := Rt / ideal apply(Y, v -> v^3);
    t := #cs;
    Phi := product(cs, c -> (sum(h, k -> c#k * (Y#k)^2))^2);
    taus := apply(Y, v -> sub(v^2 * Phi, T));
    lenT := sum(0..(2*h), d -> hilbertFunction(d, T / ideal taus));
    pts := toList((h:0)..(h:2));
    allowed := #select(pts, pt -> (
        g := apply(pt, a -> if a == 0 then 1 else 0);
        all(g, a -> a == 0) or any(cs, c -> (sum(h, k -> c#k * g#k)) % 3 != 0)));
    -- immunity: least degree of a nonzero polynomial function vanishing on the allowed set
    out << label << " h=" << h << " t=" << t << " lenT/(tau)=" << lenT << " allowed=" << allowed
        << " falls=" << (lenT != allowed) << endl; out << flush);
setRandomSeed 20260926;
for h from 2 to 7 do (
    for trial from 1 to 3 do run1("random t=1", h, {apply(h, k -> random(0, 2))});
    run1("all-ones t=1", h, {apply(h, k -> 1)}));
for h from 3 to 7 do for trial from 1 to 2 do run1("random t=2", h, {apply(h, k -> random(0, 2)), apply(h, k -> random(0, 2))});
close out;
