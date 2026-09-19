#!/usr/bin/env python3
"""Apply four source-audited scope clarifications, without changing proof coverage."""
import json,sys,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,write_json,validate,REGISTRY
from claim_reviews import make_review,Evidence
data=load();byid={c['id']:c for c in data['claims']};ev=Evidence()
rev=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
rows=json.loads((ROOT/'research/results/parallel_formalization_route_reconcile/proposed-corrections.json').read_text())
for row in rows:
 c=byid[row['id']];assert c['formalization']['scope']==row['before']
 old=c['reviews']['formalization'];targets=[i['target'] for i in old['evidence']]
 for item in old['evidence']:assert ev.sha256(item['target'])==item['sha256']
 c['formalization']['scope']=row['after'];targets.append('results/parallel_formalization_route_reconcile/report.json')
 c['reviews']['formalization']=make_review(data,c,'formalization',targets,revision=rev,date='2026-09-19',reviewer='Codex coordinator with independent route-map reconciliation',note=old['note']+' Removed obsolete prospective R15 wording; verified scope unchanged and assembly remains a separate claim. Existing evidence inspected, no fresh kernel replay.',evidence=ev)
validate(data);write_json(REGISTRY,data);print('Clarified',len(rows),'formalization scopes without expanding coverage.')
