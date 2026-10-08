"""Check the complete period and compress only the exact rank/success predicate."""
import argparse, csv, hashlib, json
from collections import Counter
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("--ranks",required=True)
p.add_argument("--pilot",required=True)
p.add_argument("--out",required=True)
a=p.parse_args()
def rows(path):
    with open(path) as f:
        pairs=[(int(r["coefficient_residue"]),int(r["rank"])) for r in csv.DictReader(f)]
    assert len({s for s,_ in pairs})==len(pairs)
    return dict(pairs)
r=rows(a.ranks);pilot=rows(a.pilot)
L=28080
assert set(r)==set(range(L)) and set(r.values())<={0,60,61}
assert all(r[s]==v for s,v in pilot.items())
assert r[4]==0 and r[5]==61
ranks=bytes(r[s] for s in range(L))
success=bytes(int(r[s]==61) for s in range(L))
def period(v):
    k=(v+v).find(v,1)
    assert 0<k<=L and L%k==0 and all(v[i]==v[i%k] for i in range(L))
    return k
pr,ps=period(ranks),period(success)
failed=[(s-4)%ps for s in range(ps) if not success[s]]
summary={"coefficient_period":L,"rank_period":pr,"success_period":ps,
         "rank_counts":dict(sorted(Counter(r.values()).items())),
         "unit_delay_excluded_residues":sorted(failed),
         "zero_rank_coefficient_residues":[s for s in range(L) if r[s]==0],
         "normality_condition":"r=v3(256*m*h-epsilon)>=1; r modulo success_period outside unit_delay_excluded_residues",
         "scope":"Excluded residues are failed sufficient certificates, not normality exceptions.",
         "sha256":hashlib.sha256(Path(a.ranks).read_bytes()).hexdigest()}
Path(a.out).write_text(json.dumps(summary,indent=2)+"\n")
print("COMPLETE_SUMMARY",json.dumps({k:v for k,v in summary.items() if k not in ("unit_delay_excluded_residues","zero_rank_coefficient_residues")}))
print("EXCLUDED_RESIDUE_COUNT",len(failed),"ZERO_RANK_COEFFICIENT_RESIDUES",summary["zero_rank_coefficient_residues"])
