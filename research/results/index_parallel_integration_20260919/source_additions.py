#!/usr/bin/env python3
"""Integrate fully reviewed omissions from the complete source inventory."""
import json,sys,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,write_json,validate,REGISTRY
from claim_reviews import make_review,Evidence,FIELDS
data=load();old={c['id']:c for c in data['claims']};ev=Evidence()
rev=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
patch=json.loads((ROOT/'research/results/parallel_index_source_adjudication/proposals.json').read_text())
for row in patch['decisions']:
 for e in row['evidence']:assert ev.sha256(e['target'],e.get('normalization'))==e['sha256'],e['target']
for c in patch['claims']:
 assert c['id'] not in old,c['id']
 assert set(c['reviews'])==set(FIELDS)
 for rv in c['reviews'].values():
  for e in rv['evidence']:assert ev.sha256(e['target'],e.get('normalization'))==e['sha256'],e['target']
 data['claims'].append(c)
edges={e['id'] for e in data['relationships']};affected=set()
for e in patch['relationships']:
 assert e['id'] not in edges;edges.add(e['id']);data['relationships'].append(e)
 for endpoint in ('source','target'):
  if e[endpoint]['namespace']=='current':affected.add(e[endpoint]['id'])
for c in data['claims']:
 if c['id'] not in affected:continue
 rv=c['reviews']['relationships'];targets=[e['target'] for e in rv['evidence']]
 targets.append('results/parallel_index_source_adjudication/proposals.json')
 c['reviews']['relationships']=make_review(data,c,'relationships',targets,revision=rev,date='2026-09-19',reviewer='Codex coordinator, source-inventory integration',state=rv['state'],next_action=rv['next_action'],note=rv['note']+' Integrated scoped incident edges for explicitly adjudicated historical omissions; no inference from link presence alone.',evidence=ev)
validate(data);write_json(REGISTRY,data)
write_json(Path(__file__).with_name('source-additions.json'),{'new_claims':[c['id'] for c in patch['claims']],'edges_added':len(patch['relationships']),'decisions':len(patch['decisions']),'original_text_changed':False})
print('Added',len(patch['claims']),'historical records and',len(patch['relationships']),'scoped relationships.')
