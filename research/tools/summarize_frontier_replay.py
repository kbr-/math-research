#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Kamil Braun
"""Stream the small metadata records from saved, already verified PC traces."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out', required=True, type=Path)
parser.add_argument('files', nargs='+', type=Path)
args = parser.parse_args()
cases, traces, controls = {}, {}, []
reports = 0
for path in args.files:
    case = None
    with path.open() as stream:
        for line in stream:
            if not any(marker in line for marker in (
                    '"record":"case"', '"record":"verified"',
                    '"record":"invalid_residue"', '"record":"nonfresh_retained_axiom"')):
                continue
            record = json.loads(line)
            if record['record'] == 'case':
                case = record['id']
                cases[case] = {key: record[key] for key in
                               ('p', 'accuracy', 'frontier_blocks', 'multiple', 'old_variables')}
                cases[case]['goal_arity'] = len(record['goal_inputs'])
            elif record['record'] == 'verified':
                key = case, record['name']
                if key in traces and traces[key]['verification'] != record:
                    raise ValueError(f'Inconsistent repeated trace metadata: {key}')
                traces.setdefault(key, {'case': case, 'verification': record, 'files': []})
                traces[key]['files'].append(str(path))
                reports += 1
            else:
                controls.append(record)
result = {'schema': 1, 'verification_reports': reports, 'distinct_traces': len(traces),
          'cases': cases, 'traces': list(traces.values()), 'controls': controls}
args.out.parent.mkdir(parents=True, exist_ok=True)
with args.out.open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(f'{len(traces)} distinct traces, {reports} reports, {len(controls)} scope controls.')
for suffix in ('_scalar', '_joined_mp', '_joined_then_zero', '_direct_frontier'):
    selected = [r['verification'] for (_, name), r in traces.items() if name.endswith(suffix)]
    print(suffix, 'count', len(selected), 'whole degree',
          (min(r['whole_trace_degree'] for r in selected), max(r['whole_trace_degree'] for r in selected)),
          'final cone degree', (min(r['final_cone_degree'] for r in selected), max(r['final_cone_degree'] for r in selected)))
