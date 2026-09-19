#!/usr/bin/env python3
"""Record a precise negative mapping result, not nonexistence of a formal proof."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load, validate, write_json, REGISTRY
from claim_reviews import Evidence,make_review

parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
args=parser.parse_args();data=load();evidence=Evidence()
inventory=json.loads((Path(__file__).parent/'inventory.json').read_text())
mapped={c['id'] for c in inventory['claims']};changed=[]
for claim in data['claims']:
    if claim['id'] in mapped:continue
    assert claim['formalization']['status'] in (None,'no_record'),claim['id']
    claim['formalization']={'status':'no_record',
        'scope':'No explicit per-claim Lean mapping in the index links or the audited claims/ and third-party-claims/ source inventory. This is not a claim that no formal proof or implicit special-case coverage exists elsewhere.',
        'references':['results/index_formalization_metadata_20260919/inventory.json'],'artifacts':[]}
    claim['reviews']['formalization']=make_review(data,claim,'formalization',
        ['results/index_formalization_metadata_20260919/inventory.json'],
        revision='5ed10d8692edfc66d77f7425ee5cd31fa9b87124',date='2026-09-19',
        reviewer='Codex GPT-6 Astra',note='Mechanical explicit-mapping census only; no inference from mathematical implication or proof nonexistence.',
        evidence=evidence)
    changed.append(claim['id'])
validate(data);write_json(REGISTRY,data)
write_json(args.out,{'claims':changed,'count':len(changed),
    'inventory_sha256':evidence.formalization_inventory(),
    'scope':'No recorded per-claim mapping in the audited sources; adding/changing Lean sources makes these reviews stale.'})
print(f'Recorded {len(changed)} precise no-record mapping dispositions; proof absence is not asserted.')
