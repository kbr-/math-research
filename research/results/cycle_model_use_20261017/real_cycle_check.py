"""Model use of a finished cycle by tools/model_usage.py, beside an independent full scan of the same
transcripts (no binary search, no shared parsing), with the tool's wall time.

Run (17 October 2026), through ./compute.sh with CLAUDE_CODE_SESSION_ID and USAGE_LOG_DIR set:
    python3 real_cycle_check.py WORKTREE JOURNAL SESSION
on Talagrand's cycle um-exits; output in real-cycle-check.txt beside this file.
Refuted by: token counts or dollars from the tool differing from the full scan's for the same interval.
Possible because: the tool seeks by binary search and skips lines, so a misplaced seek drops records.
Baseline: none; the full scan is the reference, read with no code shared with the tool.
Record checked: no registered claim concerns framework cost accounting, so none applies.
"""
import glob, json, sys, time
from datetime import datetime, timezone
sys.path.insert(0, sys.argv[1] + '/tools')
import model_usage as mu
journal, session = sys.argv[2], sys.argv[3]
events = [json.loads(line) for line in open(journal)]
began = time.monotonic()
use = mu.cycle(events)
print(f'tool: {time.monotonic() - began:.2f} s wall time')
print('tool:', json.dumps({k: use[k] for k in ('usd', 'rows', 'limit')}, indent=1))
stamp = lambda t: datetime.fromtimestamp(t, timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
low, high = stamp(events[0]['unix_s']), stamp(events[-1]['unix_s'])
home = mu.claude_home()
files = glob.glob(f'{home}/projects/*/{session}.jsonl') + glob.glob(f'{home}/projects/*/{session}/subagents/*.jsonl')
total = dict.fromkeys(('input', '5m', '1h', 'read', 'output'), 0)
for path in files:
    seen = set()
    for line in open(path, errors='replace'):
        if '"usage"' not in line:
            continue
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if record.get('type') != 'assistant' or not (low <= record.get('timestamp', '') <= high):
            continue
        message = record['message']
        if message['id'] in seen:
            continue
        seen.add(message['id'])
        usage, made = message['usage'], message['usage'].get('cache_creation', {})
        total['input'] += usage.get('input_tokens', 0); total['read'] += usage.get('cache_read_input_tokens', 0)
        total['5m'] += made.get('ephemeral_5m_input_tokens', 0); total['1h'] += made.get('ephemeral_1h_input_tokens', 0)
        total['output'] += usage.get('output_tokens', 0)
print('full scan:', low, high, total, 'tokens', sum(total.values()))
print('full scan at Opus 5.5 list prices: $%.6f' % ((total['input'] * 4 + total['5m'] * 5 + total['1h'] * 8
                                                    + total['read'] * 0.2 + total['output'] * 20) / 1e6))
