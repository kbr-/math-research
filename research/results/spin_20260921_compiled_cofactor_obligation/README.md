Exact finite controls for the local companion-compression example.

The C++ checker uses GF(8), GF(16) and GF(32), validating that every nonzero
element has an inverse for the listed binary moduli. All ranks are exact.
The source is tools/check_frobenius_companion_gap.cpp relative to research/.

For h=1 and k=2,3,4, it computes ordinary NS spaces using the original generator
degree 3 and PC closures through degrees 3 and 4. Degree-descending echelon
pivots identify the entire lower-degree subspace eligible for multiplication.
Boolean reduction is degree preserving; it does not lower the carried budget
of the compressed generator.

The original target has minimum NS and PC degree 3. The compressed target has
minimum PC degree 4 and NS degree k+3. The report includes every queried rank
and membership result, not only the successful ceilings. All balanced
evaluation cuts of the inverse are checked. An additional k=3,h=2 case checks
leading degrees and the inverse certificate, but performs no NS/PC rank scan.

The largest rank space has 512 Boolean columns. The 2048-column case is
identity-only. The checker refuses larger enumerations; arrays and loops are
implemented in compiled C++, with no floating-point linear algebra.

Reproduce from the repository root through the shared resource controls:

    ./compute.sh --threads 1 g++ -std=c++17 -O2 -Wall -Wextra -Werror research/tools/check_frobenius_companion_gap.cpp -o /tmp/check_frobenius_companion_gap
    ./compute.sh --threads 1 /tmp/check_frobenius_companion_gap --out /tmp/exact-gap-controls.json

The tracked JSON is the complete output of the recorded run. This is a
satisfiable Boolean-domain consequence problem, not a PHP instance or a
computational proof of the arbitrary-parameter theorem.
