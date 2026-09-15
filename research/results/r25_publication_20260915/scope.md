# R25 publication theorem

Target: thm:publication-Res-parity-bit-PHP, actual usual CNF, n=2^ell holes,
m=n+1 pigeons, every real K>0, and eventually more than n^K proof nodes.
The concrete AffineDAG definition includes both recorded rule conventions.

Dependencies: completed R24 actual initial clauses, DAG translation and complete
family identity; completed R17 finite/asymptotic exclusion, transitively using the
verified matching/cube/kernel/removal chain. No new assumption is introduced.

Choose a=max(ceil(K),2). A putative S<=n^K proof has S<=n^a and yields at most
3S+choose(n+1,2)<=13 n^a+1 blocks. With h=3ell its PC ceiling is 12ell+1,
which is at most 13(ell+1). R17 at a,13,1 excludes this for large ell.
Only the final new module needs elaboration; imported proofs use existing caches.
