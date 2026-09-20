# Finite controls for the flat-stratum coefficient map

These are pointwise controls for the notebook's support-restricted poset
interpolation. They do not test graph separation or prove the asymptotic source
endpoint.

The test uses old Boolean variables x,y,z, bottom forms x,y,x+y, rank cutoff
one, and two accuracy-one parents with shared bottom products:

- (P_1, P_2, z + P_3);
- (x + P_1 + P_2, z + 2 P_1 + P_2).

The first parent uses three proper lines and zero; the second uses the first
two lines and zero. The inverse-poset selectors are the line indicators and
one minus their sum. The weight is x over F2, and x^(p-1)+y^(p-1) over F3/F5.
It excludes the rank-two active intersection. Affine reference tuples use the
exact Fermat prefix normalizer.

All 24 Boolean points are retained in stratum-controls.json, including values
outside the weight support. The accepted run has:

- 120 weighted parent-companion checks;
- 192 coefficient-field checks and all bottom-companion checks;
- 32 support-partition checks;
- zero unexpected failures.

Removing the boundary-excluding weight gives 3, 8 and 10 nonzero parent
companions over F2/F3/F5 respectively. The partition also fails over each field.

Reproduce from the repository root, within the shared controls:

    ./compute.sh c++ -std=c++17 -O2 -Wall -Wextra -Werror \
      research/tools/check_flat_stratum_map.cpp -o /tmp/check_flat_stratum_map
    ./compute.sh /tmp/check_flat_stratum_map \
      --out research/results/spin_20260921_flat_state_parent_lift/stratum-controls.json

The source's polynomial degree bounds are proved algebraically in the notebook;
this finite program checks evaluations, not symbolic NS certificates. No graph,
large span lattice, or exponential interpolation family is constructed here.
