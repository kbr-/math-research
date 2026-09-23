#!/usr/bin/env python3
"""Inspect candidate attention or append a reasoned decision; no novelty inference."""
import argparse
import json
from pathlib import Path
from claim_registry import load as load_claims
from claim_attention import load, reconcile, sync, decide, save, brief, overview, current, STATES

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    listing = sub.add_parser('list'); listing.add_argument('--all', action='store_true')
    listing.add_argument('--json', action='store_true', help='current state per claim, with pending group')
    sub.add_parser('sync')
    sub.add_parser('check')
    d = sub.add_parser('decide')
    d.add_argument('claim'); d.add_argument('--state', required=True, choices=STATES)
    d.add_argument('--note', required=True)
    d.add_argument('--actor', choices=('agent', 'user'), default='agent')
    a = p.parse_args()
    try:
        data = load_claims(ROOT/'research/claims/index.json')
        if a.command == 'sync':
            history, added = sync(ROOT, data)
            print(f'New/reopened attention items: {len(added)}')
        elif a.command == 'decide':
            history = decide(data, load(ROOT), a.claim, a.state, a.note, a.actor)
            save(ROOT, data, history)
        else:
            history, _ = reconcile(data, load(ROOT))
            if a.command == 'check':
                if history != load(ROOT) or (ROOT/'research/ATTENTION.md').read_text() != overview(data, history):
                    raise ValueError('Attention history/view stale; run tools/claim-attention.py sync')
                print('Attention history and generated view are current.')
                return
        if a.command == 'list' and a.json:
            print(json.dumps(current(data, history), ensure_ascii=False, indent=2))
            return
        print(overview(data, history) if a.command == 'list' and a.all else brief(data, history), end='')
    except (ValueError, OSError) as e:
        p.exit(2, f'attention: {e}\n')


if __name__ == '__main__':
    main()
