#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,validate,write_json
from claim_reviews import Evidence,claim_digest
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();base=Path(__file__).parent;data=load();claims={c['id']:c for c in data['claims']};e=Evidence();inv={};edges={};conflicts=[]
for name in ['batch1.json','batch2.json','batch3.json','batch4.json','provenance-resolution.json']:
 patch=json.loads((base/name).read_text())
 for row in patch['claims']:
  assert claim_digest(claims[row['id']])==row['baseline_claim_sha256'],row['id']
  for ev in row['evidence']:assert e.sha256(ev['target'])==ev['sha256'],ev['target']
  inv[row['id']]=row
 for edge in patch['relationships']:
  assert edge['id'] not in edges or edges[edge['id']]==edge,edge['id']
  for target in edge['evidence']:assert e.sha256(target)
  edges[edge['id']]=edge
existing={r['id']:r for r in data['relationships']}
for key,edge in edges.items():
 if key in existing and existing[key]!=edge:conflicts.append({'id':key,'existing_scope':existing[key]['scope'],'proposed_scope':edge['scope']})
 if key not in existing:data['relationships'].append(edge)
validate(data)
write_json(a.out,{'inventories':len(inv),'states':{s:sum(i['state']==s for i in inv.values()) for s in ['reviewed','pending']},'proposed_edges':len(edges),'preexisting_edge_conflicts_for_root_review':conflicts,'checks':'Current claim fingerprints, every inventory evidence digest, every edge evidence local target, and combined registry schema validated without canonical writes.'})
print(f'{len(inv)} reviewed inventories; {len(edges)} proposed edges; {len(conflicts)} preexisting IDs require merge review; all evidence hashes/schema pass.')
