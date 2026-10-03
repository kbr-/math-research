-- The polar colon on a random plane, without collision saturation (cycle bmd-20261009-dh).
-- Input: files written by research/tools/bmd_plane_minors.cpp (stripped minors and extraK).  F = minorList#N (Delta
-- over the common collision factor u), m1 = minorList#(N-1) (M_{N-1}/u) and k = extraK (K/u).  By the polar minor
-- identity (F, delta F) = (F, m1), and by its second form the analogue of Q is a unit times K modulo the polar
-- ideal; the candidate T = (F, m1) : k.  Statement tested: the first-step curve has no curve component in a collision
-- hyperplane, that is, the colon has no points on the plane's collision lines.  Control: d = 2, where T_2 has none
-- and degree 120.  Printed: lengths of the complete intersection (Bezout: lambda(lambda+1)), of the colon, and of
-- each after saturating by the collision forms.
-- Usage: M2 --script bmd_plane_polar_colon.m2 IN1.m2 P1 [IN2.m2 P2 ...]   (one series run)
args = drop(scriptCommandLine, 1);
for i from 0 to #args // 2 - 1 do (
    file := args#(2*i); p := value args#(2*i+1);
    R := ZZ/p[x, y];
    use R;
    load file;
    co := product collisionForms;
    N := #minorList - 1;
    CI := ideal(minorList#N, minorList#(N-1));
    L := CI : extraK;
    print(file | ": degrees F " | toString first degree minorList#N | ", m1 " | toString first degree minorList#(N-1)
          | ", k " | toString first degree extraK);
    print("  complete intersection: length " | toString degree CI | ", off collisions " | toString degree saturate(CI, co));
    print("  colon (F, m1) : k: length " | toString degree L | ", off collisions " | toString degree saturate(L, co));
    G := flatten entries gens gb L;
    msout := replace("\\.m2$", "-colon.ms", file);
    msout << "x,y" << endl << p << endl << demark(",\n", apply(G, toString)) << endl << close;
    print("  colon basis written to " | msout | " (reducedness: msolve -P 1 and bmd_param_squarefree.py)");
    S := ZZ/p[x, y, z, MonomialOrder => GRevLex];
    projL := ideal homogenize(sub(gens gb L, S), z);
    print("  colon section: Betti " | toString betti res projL);
    );
