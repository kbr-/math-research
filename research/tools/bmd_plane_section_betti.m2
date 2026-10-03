-- Plane-section Betti numbers of the first-step curve (cycle bmd-20261009-df, goal-level route review).
-- Input: files written by research/tools/bmd_plane_minors.cpp (stripped maximal minors on a random affine plane).
-- Statement tested: the first-step threshold l_0 is the initial degree of T_d.  On a generic plane the section
-- scheme of V(T_d) (cut out off collisions by the maximal minors: cor:cube-first-step-brill-noether) has an ideal
-- whose initial degree is at most indeg T_d, since restriction keeps a minimal generator nonzero; if T_d is
-- arithmetically Cohen-Macaulay its graded Betti numbers equal the section's.  The minor scheme and T_d agree on the
-- plane at d = 2 (the control: generators 12,13,14,15, relations 17,18,19); reducedness at d = 3 is checked
-- separately (msolve on the exported ideal counts distinct points).  A general-purpose radical of a length-1460
-- ideal ran over five minutes and was dropped.
-- Usage: M2 --script bmd_plane_section_betti.m2 IN1.m2 P1 OUT1.ms [IN2.m2 P2 OUT2.ms ...]   (one series run)
args = drop(scriptCommandLine, 1);
for k from 0 to #args // 3 - 1 do (
    file := args#(3*k); p := value args#(3*k+1); msout := args#(3*k+2);
    R := ZZ/p[x, y];
    use R;
    load file;
    co := product collisionForms;
    T := saturate(ideal select(minorList, f -> f != 0), co);
    G := flatten entries gens gb T;
    msout << "x,y" << endl << p << endl << demark(",\n", apply(G, toString)) << endl << close;
    S := ZZ/p[x, y, z, MonomialOrder => GRevLex];
    projT := ideal homogenize(sub(gens gb T, S), z);
    print(file | ": section length " | toString degree T);
    print("  section scheme: Betti " | toString betti res projT);
    );
