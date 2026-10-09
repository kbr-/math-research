#!/usr/bin/env python3
"""Test proposed degree reflection against retained exact full-cut tables, without rerunning ranks."""
import argparse,csv,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('tables',nargs='+');a=p.parse_args();reports=[]
for item in a.tables:
 path,period=item.rsplit(':',1);period=int(period);rows=list(csv.DictReader(Path(path).open()));table={int(x['degree_residue']):(int(x['rank']),int(x['order_index'])) for x in rows};assert len(table)==len(rows)
 missing=[];rank_bad=[];order_bad=[]
 for d,value in table.items():
  other=(6-d)%period
  if other not in table:missing.append([d,other]);continue
  if table[other][0]!=value[0]:rank_bad.append([d,other,value,table[other]])
  if table[other][1]!=value[1]:order_bad.append([d,other,value,table[other]])
 reports.append(dict(table=path,period=period,rows=len(rows),missing_partners=missing,rank_mismatches=rank_bad,selected_order_mismatches=order_bad))
a.out.write_text(json.dumps(dict(reports=reports,scope='Retained exact finite data; not a proof of universal reflection'),indent=2)+'\n')
for r in reports:print(r['table'],'rows',r['rows'],'missing',len(r['missing_partners']),'rank_mismatches',len(r['rank_mismatches']),'order_mismatches',len(r['selected_order_mismatches']))
