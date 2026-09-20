# Mixed-interface certificate controls

These exact binary ordinary-NS certificates check the hand construction in
[`mixed-polarization-helper-certificates`](https://kbr.is-a.dev/math-research/#mixed-polarization-helper-certificates).
They do not compute least proof degrees or establish a general conservativity theorem.
The rank-three retained degree lower bound is reused from the earlier archived matrices.

Reproduce from the repository root, using a new output path:

```bash
./compute.sh --threads 1 g++ -O2 -std=c++17 -Wall -Wextra -Werror \
  research/tools/check_mixed_interface_identity.cpp -o /tmp/check_mixed_interface_identity
./compute.sh --threads 1 /tmp/check_mixed_interface_identity --out /tmp/mixed-certificates.json
```

The workload is fixed to ranks 3, 4 and 5, at most 27 variables and certificate
degree 10. It uses sparse ordinary polynomials; no assignment enumeration,
linear-system search, random choices or new dependencies are involved.
All 21 certificates reconstruct exactly. Omitting an annihilation contribution
and undercharging the augmented budget are detected at each rank.

`certificates.json` preserves the original generators and degree charges, every
target and companion cofactor, and every Boolean correction cofactor. A polynomial
is a list of `[coefficient, [sorted variable ids with repetitions]]` terms over F2.
For rank r, variable ids are x: 0..r-1, y: r..2r-1, a: 2r..3r-1,
b: 3r..4r-1, u: 4r, v: 4r+1, and s: 4r+2..5r+1.
The Boolean-cofactor array uses this same order and multiplies z_i²+z_i.
Companion order is x_i A, y_i B, LE, KE, g_i G.

The checker expands before reduction, divides Boolean remainders explicitly,
reconstructs the full ordinary identity, and charges original generator degree
plus cofactor degree. Its undercharge control concerns this certificate, not
minimum proof degree. The output refuses overwriting an existing file.
