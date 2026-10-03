-- Collision strata of the polar colon on a random plane (cycle bmd-20261009-kap).
-- Input: a plane file of research/tools/bmd_plane_minors.cpp (minorList, extraK, collisionForms in the order
-- a_1..a_4, then a_i - a_j for i < j).  By the Taylor colon lemma, T_d restricted to the plane is
-- L = (F, m1) : k, collision points included.  Question (Kapranov boundary lead): on which collision strata does
-- the collision part of T_d lie, and which carry the link's part of the polar complete intersection CI = (F, m1)?
-- Printed per collision form l: the length of L and of CI supported on the line l = 0 (degree of the ideal minus
-- the degree of its saturation by l) and the number of distinct points there (degree of the radical of I + (l)).
-- Usage: M2 --script bmd_plane_colon_strata.m2 IN.m2 P
args = drop(scriptCommandLine, 1);
file := args#0; p := value args#1;
R := ZZ/p[x, y];
use R;
load file;
names := {"a1", "a2", "a3", "a4", "a1-a2", "a1-a3", "a1-a4", "a2-a3", "a2-a4", "a3-a4"};
N := #minorList - 1;
CI := ideal(minorList#N, minorList#(N-1));
L := CI : extraK;
print(file | ": length CI " | toString degree CI | ", L " | toString degree L);
onLine := (I, l) -> degree I - degree saturate(I, l);
points := (I, l) -> degree radical(I + ideal l);
for t from 0 to #collisionForms - 1 do (
    l := collisionForms#t;
    print("  " | names#t | ": L length " | toString onLine(L, l) | " at " | toString points(L, l) | " points; CI length "
          | toString onLine(CI, l) | " at " | toString points(CI, l) | " points"));
co := product collisionForms;
print("  all collision lines: L length " | toString(degree L - degree saturate(L, co)) | " at "
      | toString points(L, co) | " points; CI length " | toString(degree CI - degree saturate(CI, co)) | " at "
      | toString points(CI, co) | " points");
