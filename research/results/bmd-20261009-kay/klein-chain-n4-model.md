# Klein chain model of the genus-five root cover C_4

Source: lem:cube-klein-chain-realization (entry-2026-10-09-cube-klein-chain-realization in
research/branches/binary-multiplicity-degree/notebook.html). This is the explicit Schottky-type model of
the curve C_4 that carries the n=5 collision series U_d.

## Field and parameters

- K is complete and discretely valued, with algebraically closed residue field of characteristic not 2.
- The parameters alpha and beta have v(alpha) > 0 and v(beta) > 0.
- K is replaced by K(sqrt(alpha), sqrt(beta)), so that every group below fixes a vertex of the
  Bruhat-Tits tree.

## Generators

Matrices are written in PGL_2(K) as [[a, b], [c, d]], acting by z -> (az+b)/(cz+d). The auxiliary
coordinate is w = (z-1)/(z+1), given by M = [[1, -1], [1, 1]] with det 2 (a unit), so M fixes the
vertex |z| = 1.

| group | elements | fixed vertex |
|---|---|---|
| B_1 | z, -z, alpha/z, -alpha/z: [[1,0],[0,1]], [[-1,0],[0,1]], [[0,alpha],[1,0]], [[0,-alpha],[1,0]] | abs(z) = abs(alpha)^(1/2) |
| B_2 | z, -z, 1/z, -1/z | abs(z) = 1 |
| B_3 | M^-1 {w, -w, beta/w, -beta/w} M | abs(w) = abs(beta)^(1/2) |

The edge involutions are:

- c_1 = (z -> -z), the shared element of B_1 and B_2. Its axis is 0 to infinity.
- c_2 = (z -> 1/z) = (w -> -w), the shared element of B_2 and B_3. Its axis is z = 1 to z = -1.

The branch involutions, labelled as in lem:cube-tame-chain-model:

| involution | element | image in G = F_2^4 |
|---|---|---|
| b_1 | alpha/z | e_1 |
| b_2 | -alpha/z | e_2 |
| c_1 | -z | e_1 + e_2 |
| b_3 | -1/z | e_3 |
| c_2 | 1/z = c_1 b_3 | e_1 + e_2 + e_3 |
| b_4 | w -> beta/w | e_4 |
| b_5 | w -> -beta/w = c_2 b_4 | e_1 + e_2 + e_3 + e_4 |

## Conditions of the lemma

1. c_1 and c_2 are distinct elements of B_2.
2. Each group is {±x, ±1/x} in a coordinate x scaled to its vertex:
   - x = z / sqrt(alpha) for B_1;
   - x = z for B_2;
   - x = w / sqrt(beta) for B_3.
3. The vertices lie on the axes and are distinct:
   - abs(z) = abs(alpha)^(1/2) and abs(z) = 1 lie on the axis of c_1, and differ since v(alpha) > 0;
   - abs(w) = 1 (which is abs(z) = 1) and abs(w) = abs(beta)^(1/2) lie on the axis of c_2, and differ
     since v(beta) > 0.

## Output of the lemma

- Gamma = ker(N -> G) is a Schottky group of rank 5, with N = <B_1, B_2, B_3>.
- Gamma \ Omega is a root cover w_i^2 = 1 + a_i T, i = 1..4, of genus 5.
- Branch points:
  - T = -1/a_i is the image of the fixed points of b_i;
  - T = infinity is the image of the fixed points of b_5.
- The edge lengths are v(alpha)/2 and v(beta)/2.

## Still open

- Formulas for T and w_i as theta quotients, with the automorphy character removed.
- The leading coefficient of det Phi_P at n=5.
