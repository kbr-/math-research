#!/usr/bin/env python3
"""The registered claims a draft's claim summaries resemble, before the review.

Registration refuses a new claim that resembles a registered one unless the spec relates the two
(claim_authoring.similar_claims), but registration comes after the entry is drafted and reviewed.  On 11 October
2026 an entry presented as new what a registered finite check already had for three of its six sizes; its
reviewer found the earlier claim.  This tool runs the same search on a compact spec when it is first drafted
and prints, for each of its claims, the registered claims its summary most resembles, with scores, whatever
the spec's relationships say and whatever the threshold: the author reads those records before writing the
entry's claim of novelty.

Usage: claim_resemblance.py SPEC.json [--count N] [--registry PATH]
The spec is the compact form `claim-index.py author build` takes (a "claims" list with "id" and "summary").
Prints the registry's size, which the work grows with.
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from claim_authoring import SIMILAR_AT, similar_claims


DEFAULT_REGISTRY = ROOT / 'research' / 'claims' / 'index.json'
RUN_LOG = ROOT / 'research' / 'logs' / 'claim-searches.jsonl'


def log_run(idents, path=None):
    """Append this run to the ignored log of record searches, which the finisher reads: an entry of 11 October
    2026 said what its corollary added before the nearest registered claims were read, the tool having been
    run only after the review.  A log that cannot be written is not an error."""
    import time
    try:
        path = path or RUN_LOG
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('a') as handle:
            handle.write(json.dumps({'unix_s': time.time(), 'query': 'claim_resemblance ' + ' '.join(idents)}) + '\n')
    except OSError:
        pass


def resemblances(registered, spec, count=5):
    """[(draft id, [(score, registered id, summary start), ...]), ...] for the spec's claims; a claim already
    registered under the same id is not compared with itself."""
    summaries = {claim['id']: claim.get('summary', '') for claim in registered}
    out = []
    for claim in spec.get('claims', []):
        others = [c for c in registered if c['id'] != claim['id']]
        found = similar_claims(others, claim['summary'], count)
        out.append((claim['id'], [(score, ident, summaries[ident][:160]) for score, ident in found]))
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('spec')
    parser.add_argument('--count', type=int, default=5)
    parser.add_argument('--registry', default=str(DEFAULT_REGISTRY))
    args = parser.parse_args(argv)
    registered = json.loads(pathlib.Path(args.registry).read_text())['claims']
    spec = json.loads(pathlib.Path(args.spec).read_text())
    if args.registry == str(DEFAULT_REGISTRY):       # a run on the record: logged for the finisher, as searches are
        log_run([claim['id'] for claim in spec.get('claims', [])])
    print(f'{len(registered)} registered claims compared; registration refuses a score of {SIMILAR_AT} or more '
          'unless the spec relates the two.')
    related = {tuple(edge[:1] + edge[2:3]) for edge in spec.get('relationships', [])}
    for ident, found in resemblances(registered, spec, args.count):
        print(f'{ident}:')
        for score, other, start in found:
            mark = ' (related in the spec)' if (ident, other) in related or (other, ident) in related else ''
            print(f'  {score:.2f} {other}{mark}: {start}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
