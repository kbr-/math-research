#!/usr/bin/env python3
import argparse,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,write_json
spec=importlib.util.spec_from_file_location('deps',ROOT/'tools/claim-dependencies.py');deps=importlib.util.module_from_spec(spec);spec.loader.exec_module(deps)
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
data=load();packets=[deps.metadata_packet(data,c['id'],limit=4,width=1000) for c in data['claims'][280:360]]
write_json(args.out,{'packets':packets,'scope':'Selected evidence; exact indexed assessments retained, not complete proof review.'})
for packet in packets:
 print(packet['id'])
 for passage in packet['passages']:
  snippets=passage['excerpts']
  print(' ',passage['target'].split('#')[-1], '[widened]' if passage['widened'] else '')
  if snippets:print(' ',snippets[0]['text'][:160])
