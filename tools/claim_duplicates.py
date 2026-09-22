#!/usr/bin/env python3
"""Lexical duplicate candidates among registered claims; never edits metadata."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re

from claim_registry import REGISTRY, load

STOP = set('a an the and or of to in for with by on is are be as at from this that'.split())


def fingerprint(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode()).hexdigest()


def duplicate_candidates(data, threshold=0.5):
    """Sparse set-Jaccard retrieval over summary words, not mathematical equivalence."""
    if not 0 < threshold <= 1:
        raise ValueError('Threshold must be in (0, 1]')
    token_sets, postings, shared = {}, defaultdict(list), defaultdict(int)
    for claim in sorted(data['claims'], key=lambda c: c['id']):
        tokens = set(re.findall(r'[\w]+', claim['summary'].casefold())) - STOP
        identifier = claim['id']
        token_sets[identifier] = tokens
        for token in sorted(tokens):
            for prior in postings[token]:
                shared[(prior, identifier)] += 1
            postings[token].append(identifier)
    candidates = []
    for (left, right), count in shared.items():
        union = len(token_sets[left]) + len(token_sets[right]) - count
        score = count / union
        if score >= threshold:
            candidates.append({'left': left, 'right': right, 'score': round(score, 6),
                               'shared_tokens': sorted(token_sets[left] & token_sets[right]),
                               'disposition': 'unreviewed_candidate', 'accepted_relationship': False})
    candidates.sort(key=lambda p: (-p['score'], p['left'], p['right']))
    return {'schema_version': 1, 'derived_from_sha256': fingerprint(data),
            'method': 'summary-token-set-jaccard-v1', 'threshold': threshold,
            'claim_ids': sorted(token_sets), 'candidates': candidates,
            'note': 'Lexical suggestions only; incomplete for paraphrases and misleading for differing '
                    'hypotheses. Check encodings, quantifiers, hypotheses and costs before recording '
                    'any relationship. This report never merges or reclassifies claims.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', type=Path, default=REGISTRY)
    parser.add_argument('--threshold', type=float, default=.5)
    parser.add_argument('--out', type=Path, required=True, help='Complete, untruncated JSON report')
    args = parser.parse_args()
    if args.out.resolve() == args.registry.resolve():
        parser.error('The report must not replace its canonical registry')
    report = duplicate_candidates(load(args.registry), args.threshold)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(f'Saved complete duplicate-candidate report to {args.out}')


if __name__ == '__main__':
    main()
