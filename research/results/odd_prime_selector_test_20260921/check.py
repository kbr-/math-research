"""Exact finite controls for the local selector identity, not a full PC checker."""
import json
from pathlib import Path
import numpy as np
out=[]
for p in (3,5,7):
    f,g,a,b=np.indices((p,p,p,p),dtype=np.int64)
    sel=lambda x:(1-np.power(x%p,p-1))%p
    tf,tg,th=sel(f),sel(g),sel(a*f+b*g)
    bad=(tf*tg*(1-th))%p
    assert not np.any(bad)
    wrong=(tf*(1-th))%p
    witness=np.argwhere(wrong!=0)[0].tolist()
    out.append({'p':p,'residue_assignments':p**4,'valid_identity_violations':int(np.count_nonzero(bad)),
                'omit_second_premise_witness_f_g_alpha_beta':witness,
                'omit_second_premise_violations':int(np.count_nonzero(wrong)),
                'scope':'Finite selector relation only; symbolic PC replay and degree proof are in the notebook.'})
Path(__file__).with_name('checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
