#!/usr/bin/env python3
"""Export only structural counts for the known historical explicit resume turn."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[3]
START='2026-09-10T21:55:18.743Z'
FILES=['research/notes/RESUME.md','research/AGENTS.md','COMPUTATION_RULES.md','notebook.html']

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    # Binding was checked against CODEX_THREAD_ID in the controller before this
    # protected job. Never export the identifier, log path or raw transcript.
    identity=(ROOT/'.codex-session-id').read_text().strip()
    paths=list((Path.home()/'.codex/sessions').rglob('*-'+identity+'.jsonl'))
    if len(paths)!=1:raise ValueError('Expected this checkout’s uniquely bound session log')
    active=False;calls=[];outputs={};completion=None;prompt_count=0
    for line in paths[0].open():
        try:record=json.loads(line)
        except ValueError:continue
        p=record.get('payload',{});stamp=record.get('timestamp','')
        if stamp==START and record.get('type')=='response_item' and p.get('type')=='message' and p.get('role')=='user':
            active=True;prompt_count+=1;continue
        if not active:continue
        if record.get('type')=='response_item' and p.get('type')=='message' and p.get('role')=='user':break
        if record.get('type')=='event_msg' and p.get('type')=='task_complete':
            message=p.get('last_agent_message','')
            completion={'timestamp':stamp,'reported_duration_ms':p.get('duration_ms'),
                        'mentions_readiness':bool(re.search(r'\bready\b|restored',message,re.I)),
                        'message_characters':len(message)}
        if record.get('type')!='response_item':continue
        if p.get('type') in ('custom_tool_call','function_call'):
            body=p.get('input',p.get('arguments',''))
            commands=[]
            for match in re.finditer(r'(?:"cmd"|\bcmd)\s*:\s*("(?:\\.|[^"\\])*")',body):
                try:commands.append(json.loads(match.group(1)))
                except ValueError:pass
            mentions={name for name in FILES if name in body}
            # Separate root and scoped AGENTS references without exporting commands.
            root_agents=any(re.search(r'(?<![/\w])AGENTS\.md',cmd) for cmd in commands)
            calls.append({'_call_id':p.get('call_id'),'timestamp':stamp,'tool':p.get('name'),
                          'nested_shell_calls':body.count('tools.exec_command('),
                          'parsed_command_count':len(commands),'root_agents_mentioned':root_agents,
                          'files_mentioned':sorted(mentions),
                          'uses_cat':any(re.search(r'\bcat\b',cmd) for cmd in commands),
                          'uses_sed':any(re.search(r'\bsed\b',cmd) for cmd in commands),
                          'uses_rg':any(re.search(r'\brg\b',cmd) for cmd in commands)})
        if p.get('type') in ('custom_tool_call_output','function_call_output'):
            raw=p.get('output','');text=raw if isinstance(raw,str) else json.dumps(raw)
            outputs[p.get('call_id')]={'transcript_result_bytes':len(text.encode()),
                 'truncation_marker_detected':bool(re.search(r'\d+ tokens truncated|Warning: truncated output|\[Showing last \d+',text))}
    if prompt_count!=1 or completion is None:raise ValueError('Resume boundaries were not established')
    for call in calls:
        call.update(outputs.get(call.pop('_call_id'),{'output_not_located':True}))
    elapsed=(datetime.fromisoformat(completion['timestamp'].replace('Z','+00:00'))-datetime.fromisoformat(START.replace('Z','+00:00'))).total_seconds()
    result={'sample':'Explicit post-compaction restoration request in this same session, before resume.py existed',
            'request_timestamp':START,'completion':completion,'request_to_completion_seconds':elapsed,
            'outer_tool_calls':len(calls),'nested_shell_calls':sum(c['nested_shell_calls'] for c in calls),
            'calls':calls,'privacy':'No session IDs, transcript paths, raw commands, user/assistant text or source contents exported.',
            'limits':'One historical sample from an earlier guide and notebook version. Counts show actual batching, not a population average. '
                     'Absence of a truncation marker does not certify complete understanding. Transcript-result bytes include tool envelopes '
                     'and are not directly comparable with benchmark stdout bytes. Duration includes model/orchestration time, unlike subprocess timings.'}
    with args.out.open('x') as output:json.dump(result,output,indent=2);output.write('\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
