# R14 concrete row-cube restrictions

Integration baseline b4406163e9372f20ba481eeb475703c5d2379cf3 includes verified disjoint coordinate pairs and generic binary cube degree/NS transport. This worker owns RowCubeRestriction.lean and finalR14 assembly. r_foundations owns RowCubeCoefficientIsolation.lean independently, under a generic substitution-coordinate interface supplied throughparent. Do not duplicate its coefficient proof or edit its worktree.

Concrete data: selected rowset S, forbidden columnset F, endpoints point:S→F2→FinN containedinF, and each cube choice gives an injective selected-row assignment. Untagged retained cells map to residual variables through exact complement equivalences; tagged cells map to one-hot constants at their chosen endpoint; other forbidden-column cells mapzero. Prove every actual functionalUnary generator has a cube-independent image equalzero or a supplied residual generator. Apply previously proved cubeDifference_ns, with actualdegreeB−|S|. Buildthisdatafromdisjointcoordinatepairs eventually, preserving |F|=2|S|.

Must prove decoder-coordinate interface for isolationworker: at selectedrowi, aeval(boardInput epsilon)(decoderInput(i,t))=C(bitLabelEquiv(point i epsilon_i)t); outsideS the image is cube-independent. Finalcoefficientisolator then provesvalue1 onthe selectednonzerocoefficient. Residualdesignpositivity/degreeparametersalreadyverified. No abstracthgen orseparatorassumption mayremainincompleteR14.

Some initialboard-interface planningduringcleanintegrationwait precededthisclock; no timebackfilled. Parentownsalllivingsections/route. Localcommitsonly; no newagents,pushesoruncoordinatedrebases. Broaderpost-all-Rxxsweepdeferred.
