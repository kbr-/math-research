#!/usr/bin/env python3
"""Audit the fixed Fossick goal against current sources without selecting a new pass."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools'))
from fossick import inventory, read_state, work, write_report
from claim_attention import load as attention_load, latest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    scope = json.loads((Path(__file__).parent/'scope.json').read_text())
    state = read_state(ROOT)
    data, rows = inventory(ROOT)
    pending, frontier = work(state, rows)
    goal = set(scope['claims'])
    current = {c['id'] for c in data['claims']}
    covered = {c for r in state['ledger'].values() for c in r['reviews'] + r['attention']}
    errors = []
    if state['active']:
        errors.append('Unfinished batch remains')
    if pending:
        errors.append('Unscreened or stale in-scope articles remain')
    if frontier != state['scan']['terminal'] or state['ended_at'] != frontier:
        errors.append('Ended-at marker has not reached the pinned endpoint')
    if goal - covered or goal - current:
        errors.append('Starting claims are missing or unscreened')
    ids = [r['id'] for r in rows]
    scoped = rows[:ids.index(state['scan']['terminal'])+1]
    flags = latest(attention_load(ROOT))
    for row in scoped:
        saved = state['ledger'].get(row['id'])
        if not saved:
            continue
        if not saved['note'].strip():
            errors.append(row['id'] + ': missing reason')
        if set(row['claims']) - set(saved['reviews'] + saved['attention']):
            errors.append(row['id'] + ': source-linked claim not accounted for')
        if set(saved['attention']) - set(flags):
            errors.append(row['id'] + ': missing attention handoff')
    reports = {}
    for path in (ROOT/'research/results').glob('fossick_scan_20260920_*/completion.json'):
        result = json.loads(path.read_text())
        reports[result['proposal_sha256']] = result
    for token, receipt in state['receipts'].items():
        if reports.get(token) != receipt:
            errors.append('Missing or changed durable completion receipt: ' + token)
    report = dict(passed=not errors, errors=errors, starting_revision=scope['revision'],
                  starting_claims=len(goal), screened_starting_claims=len(goal & covered),
                  missing_claims=sorted(goal-covered), current_extra_claims=sorted(current-goal),
                  pinned_articles=len(scoped), screened_articles=len(state['ledger']),
                  unfinished_or_stale_articles=len(pending), ended_at=frontier,
                  receipt_count=len(state['receipts']), attention_items=len(flags),
                  limits='Coverage and current evidence fingerprints, not an independent proof or novelty audit. '
                         'Later scan-checkpoint entries do not extend the fixed goal. Candidate audits may remain pending.')
    write_report(args.out, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
