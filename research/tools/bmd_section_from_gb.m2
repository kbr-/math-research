-- Length and Betti numbers of a plane section from msolve's saturated Groebner basis (cycle bmd-20261009-dg).
-- Input: files written by research/tools/bmd_minors_msolve.py to-m2 (gbList: the reduced basis in x, y of the
-- minor ideal saturated by the collision forms, grevlex).  Same statement and bound as bmd_plane_section_betti.m2.
-- Usage: M2 --script bmd_section_from_gb.m2 IN1.m2 P1 [IN2.m2 P2 ...]   (one series run)
args = drop(scriptCommandLine, 1);
for k from 0 to #args // 2 - 1 do (
    file := args#(2*k); p := value args#(2*k+1);
    R := ZZ/p[x, y, MonomialOrder => GRevLex];
    use R;
    load file;
    T := ideal gbList;
    S := ZZ/p[x, y, z, MonomialOrder => GRevLex];
    projT := ideal homogenize(sub(gens gb T, S), z);
    print(file | ": section length " | toString degree T);
    print("  section scheme: Betti " | toString betti res projT);
    );
