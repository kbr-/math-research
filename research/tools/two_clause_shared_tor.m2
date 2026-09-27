-- Two designed clauses in shared columns: the Tor_1 defect of their tops (entry-2026-09-27-few-shared-columns).
--
-- Statement tested.  Over F_3, let A be the monomial algebra on the cells of two width-k clauses C, C' on
-- disjoint cells: variables x_(p,i) for part p of C (p = 0 is S, p = 1..k the T_j) and z_(p,i) for C', with all
-- squares zero and, in the matched case, x_(p,i) z_(p,i) = 0 (cell i of part p of C and of C' share a column, as in
-- the polynomial-graph design, where every clause uses the same columns part by part).  With
-- tau = e_2(S) prod_j e_1(T_j) and tau' likewise, the pair has only Frobenius syzygies and Koszul pairs in degree s
-- exactly when both single-clause annihilators are Taylor (column Wilson) and
--     Tor_1^A(A/tau, A/tau')_s = dim (tau A cap tau' A)_s - dim (tau tau' A)_s = 0.
-- The script computes this defect block by block in the multigrading by part counts (all relations are monomial,
-- tau and tau' are multihomogeneous): per target multidegree d, defect = r1 + r2 - r12 - r3 with r1 = rank of
-- tau * A_{d - deg tau}, r2 likewise for tau', r12 the rank of both together, r3 the rank of tau tau' * A_{...}.
-- Control: without matching (disjoint columns) A is a tensor product and the defect is 0 at every size and degree.
--
-- Usage: M2 --script two_clause_shared_tor.m2 "CASES" where CASES is a Macaulay2 list of
--   {k, {|S|, |T_1|, ..., |T_k|}, matched (true/false), smax}.
cases := value (scriptCommandLine#1);
kk := ZZ/3;
esym := (vs, r) -> sum(subsets(vs, r), product);
blockRank := (f, dsrc, dtgt, R) -> (
    if any(dsrc, e -> e < 0) then return 0;
    Bs := basis(dsrc, R);
    if numcols Bs == 0 then return 0;
    Bt := basis(dtgt, R);
    if numcols Bt == 0 then return 0;
    rank last coefficients(f * Bs, Monomials => Bt));
pairRank := (f, g, dsf, dsg, dtgt, R) -> (
    Bt := basis(dtgt, R);
    if numcols Bt == 0 then return 0;
    ms := {};
    if all(dsf, e -> e >= 0) then (Bs := basis(dsf, R); if numcols Bs > 0 then ms = append(ms, f * Bs));
    if all(dsg, e -> e >= 0) then (Bg := basis(dsg, R); if numcols Bg > 0 then ms = append(ms, g * Bg));
    if #ms == 0 then return 0;
    rank last coefficients(fold((a, b) -> a | b, ms), Monomials => Bt));
compositions := (n, parts, caps) -> (
    if parts == 0 then (if n == 0 then return {{}} else return {});
    flatten apply(toList(0..min(n, caps#0)), e -> apply(compositions(n - e, parts - 1, drop(caps, 1)), c -> prepend(e, c))));
for cs in cases do (
    k := cs#0; sz := cs#1; matched := cs#2; smax := cs#3;
    np := k + 1; h := k + 2;
    xs := flatten apply(np, p -> apply(sz#p, i -> x_(p, i)));
    zs := flatten apply(np, p -> apply(sz#p, i -> z_(p, i)));
    unitv := j -> apply(2 * np, t -> if t == j then 1 else 0);
    degs := flatten apply(np, p -> apply(sz#p, i -> unitv p)) | flatten apply(np, p -> apply(sz#p, i -> unitv(np + p)));
    P := kk[xs | zs, Degrees => degs];
    X := p -> apply(sz#p, i -> P_(sum(take(sz, p)) + i));
    Zv := p -> apply(sz#p, i -> P_(#xs + sum(take(sz, p)) + i));
    rels := apply(gens P, v -> v^2);
    if matched then rels = rels | flatten apply(np, p -> apply(sz#p, i -> (X p)#i * (Zv p)#i));
    R := P / ideal rels;
    tau := sub(esym(X 0, 2) * product(toList(1..k), j -> esym(X j, 1)), R);
    tauP := sub(esym(Zv 0, 2) * product(toList(1..k), j -> esym(Zv j, 1)), R);
    dt := {2} | toList(k : 1) | toList(np : 0);
    dtp := toList(np : 0) | {2} | toList(k : 1);
    caps := sz | sz;
    << "case k=" << k << " sizes=" << toString sz << " matched=" << toString matched << " h=" << h << endl << flush;
    for s from h + 1 to smax do (
        tot := 0;
        for d in compositions(s, 2 * np, caps) do (
            if matched and any(np, p -> d#p + d#(np + p) > sz#p) then continue;
            dsrc := d - dt; dsrcp := d - dtp; dboth := d - dt - dtp;
            r1 := blockRank(tau, dsrc, d, R);
            r2 := blockRank(tauP, dsrcp, d, R);
            if r1 == 0 or r2 == 0 then continue;
            r12 := pairRank(tau, tauP, dsrc, dsrcp, d, R);
            r3 := blockRank(tau * tauP, dboth, d, R);
            df := r1 + r2 - r12 - r3;
            if df != 0 then << "  s=" << s << " d=" << toString d << " defect=" << df << endl;
            tot = tot + df);
        << "  s=" << s << " total defect=" << tot << " (" << toString(cpuTime()) << " s)" << endl << flush));
