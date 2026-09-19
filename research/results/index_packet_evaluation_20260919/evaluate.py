#!/usr/bin/env python3
"""Preserve representative packet outputs and test qualification retention."""
import argparse
import importlib.util
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,write_json
spec=importlib.util.spec_from_file_location('deps',ROOT/'tools/claim-dependencies.py')
deps=importlib.util.module_from_spec(spec);spec.loader.exec_module(deps)
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
data=load()
samples=[
 ('lem:mp-telescoping',['exact companion equality refuted','loose input-degree bound'],
  'Partial formalization/counterexample is explicit; original statement excerpts omit formulas and later proof detail. Read the correction and exact bound before use.'),
 ('prop:mp-substitution-interface',['Conditional working proof'],
  'Conditional status and supplied-premise statement orient correctly; bounded output omits later shortcut controls. Proof reliance still requires exact hypothesis review.'),
 ('obs:composition-gap',['Correction with obstruction','discharged for every recorded round bound'],
  'Verbatim assessment retains the evolving correction and repair history; long excerpts truncate, so a selected old obstruction must not override its later qualified repair.'),
 ('check:hole-axioms-dense-form-images',['Finite check','not a theorem'],
  'Finite-check status is explicit and method excerpts expose scope; selection is not evidence for a universal conclusion.'),
 ('thm:matching-affine-annihilators',['Working proof'],
  'A bounded packet can show the theorem inequality without all definitions or assumptions. Good for finding the relevant tool, insufficient to apply it.')]
rows=[]
for label,fragments,interpretation in samples:
 packet=deps.metadata_packet(data,label,limit=3,width=700)
 assert all(fragment in packet['assessment'] for fragment in fragments),label
 assert packet['proof_ready'] is False
 rows.append({'packet':packet,'assessment_fragments_checked':fragments,
              'evaluation':interpretation,'display_characters':len(deps.packet_text(packet)),
              'source_blocks':sum(p['total_blocks'] for p in packet['passages']),
              'selected_blocks':sum(p['included_blocks'] for p in packet['passages'])})
write_json(args.out,{'samples':rows,'conclusion':'Useful for orientation/triage and locating sources; not proof readiness.',
                    'limitations':'Five purposive cases, not exhaustive extraction accuracy. Index assessments may themselves need audit. Always inspect exact statements, proofs and corrections before reliance.'})
for row in rows:
 print(row['packet']['id'],str(row['selected_blocks'])+'/'+str(row['source_blocks'])+' blocks',str(row['display_characters'])+' display characters')
