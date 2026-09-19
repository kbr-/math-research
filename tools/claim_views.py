#!/usr/bin/env python3
"""Derived topic/lifecycle views and lexical duplicate candidates; never edits metadata."""
import argparse
from collections import defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, urlunsplit
import posixpath

from claim_registry import REGISTRY, load, markdown_links, escape_cell

STOP = set('a an the and or of to in for with by on is are be as at from this that'.split())


def fingerprint(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode()).hexdigest()


def warnings(data):
    result = defaultdict(list)
    for edge in data.get('relationships', []):
        if edge['type'] in ('corrects', 'supersedes') and edge['target']['namespace'] == 'current':
            result[edge['target']['id']].append({
                'type': edge['type'], 'source': edge['source'],
                'review_status': edge['review_status'], 'id': edge['id']})
    return {key: sorted(value, key=lambda x: x['id']) for key, value in result.items()}


def topic_map(data):
    groups = {t['id']: {**deepcopy(t), 'claim_ids': []}
              for t in sorted(data.get('topic_definitions', []), key=lambda t: t['id'])}
    unclassified = []
    for claim in data['claims']:
        if not claim.get('topics'):
            unclassified.append(claim['id'])
        for topic in claim.get('topics', []):
            groups[topic]['claim_ids'].append(claim['id'])
    for group in groups.values():
        group['count'] = len(group['claim_ids'])
    return {'schema_version': 1, 'derived_from_sha256': fingerprint(data),
            'claim_count': len(data['claims']), 'topics': list(groups.values()),
            'unclassified': unclassified,
            'note': 'Multi-topic membership overlaps; unclassified means missing topic metadata.'}


def claim_view(data, topic=None, lifecycle='all'):
    if lifecycle not in ('all', 'active', 'historical'):
        raise ValueError('Unknown lifecycle: ' + lifecycle)
    if topic is not None and topic != '@unclassified' and topic not in {
            t['id'] for t in data.get('topic_definitions', [])}:
        raise ValueError('Unknown topic: ' + topic)
    notices = warnings(data)
    rows = []
    for claim in data['claims']:
        historical = claim.get('mathematical_status') == 'retracted' or any(
            w['type'] == 'supersedes' and w['review_status'] == 'reviewed'
            for w in notices.get(claim['id'], []))
        if lifecycle == 'active' and historical or lifecycle == 'historical' and not historical:
            continue
        if topic == '@unclassified' and claim.get('topics'):
            continue
        if topic is not None and topic != '@unclassified' and topic not in claim.get('topics', []):
            continue
        rows.append({**deepcopy(claim), 'warnings': deepcopy(notices.get(claim['id'], []))})
    return {'schema_version': 1, 'derived_from_sha256': fingerprint(data),
            'topic': topic, 'lifecycle': lifecycle, 'claims': rows,
            'note': 'Historical means explicitly retracted or superseded by a reviewed edge. '
                    'Active means not so marked, not validity or current-route membership. '
                    'Corrections remain visible in every applicable view; unreviewed edges are labelled.'}


def public_markdown(text):
    # Registry Markdown links are relative to research/CLAIM_INDEX.md, not this output file.
    for link in reversed(markdown_links(text)):
        target = link['target']
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc:
            continue
        path = posixpath.normpath(posixpath.join('research', parsed.path)) if parsed.path else 'research/CLAIM_INDEX.md'
        absolute = urlunsplit(('https', 'github.com', '/kbr-/math-research/blob/main/' + path,
                               parsed.query, parsed.fragment))
        text = text.replace('](' + target + ')', '](' + absolute + ')')
        text = text.replace('](<' + target + '>)', '](<' + absolute + '>)')
    return text


def markdown(report):
    lines = ['> Generated from research/claims/index.json; do not edit this view.', '', report['note'], '']
    if 'topics' in report:
        lines += ['| Topic | Claims | Description |', '|---|---:|---|']
        lines += ['| ' + ' | '.join(map(escape_cell, [t['id'], str(t['count']), t['description']])) + ' |'
                  for t in report['topics']]
        lines += [f'| @unclassified | {len(report["unclassified"])} | No assigned topics |']
    else:
        lines += ['| ID | Summary | Status and warnings | Source |', '|---|---|---|---|']
        for claim in report['claims']:
            status = claim.get('mathematical_status') or 'unreviewed'
            notes = [f"{w['type']} by {w['source']['id']} ({w['review_status']})" for w in claim['warnings']]
            cells = [claim['id'], public_markdown(claim['summary']),
                     status + ('; ' + '; '.join(notes) if notes else ''), public_markdown(claim['record'])]
            lines.append('| ' + ' | '.join(escape_cell(c.replace('\n', ' ')) for c in cells) + ' |')
    return '\n'.join(lines) + '\n'


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


def bundle_files(data):
    """Complete, linked Markdown views; dictionary keys are safe relative filenames."""
    files = {}
    overview = topic_map(data)
    lines = ['> Generated from research/claims/index.json; do not edit these views.', '',
             '# Topic map', '', '[All claims](all.md) · [Active](active.md) · '
             '[Historical/retracted](historical.md) · [Unclassified](unclassified.md)', '',
             overview['note'], '', '| Topic | Claims | Description |', '|---|---:|---|']
    for topic in overview['topics']:
        filename = 'topic-' + hashlib.sha256(topic['id'].encode()).hexdigest()[:20] + '.md'
        files[filename] = markdown(claim_view(data, topic['id']))
        lines.append('| ' + ' | '.join(escape_cell(value) for value in [
            '[' + topic['id'] + '](' + filename + ')', str(topic['count']), topic['description']]) + ' |')
    lines += [f'| [Unclassified](unclassified.md) | {len(overview["unclassified"])} | No assigned topics |', '']
    files['topics.md'] = '\n'.join(lines)
    for mode in ('all', 'active', 'historical'):
        files[mode + '.md'] = markdown(claim_view(data, lifecycle=mode))
    files['unclassified.md'] = markdown(claim_view(data, '@unclassified'))
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', type=Path, default=REGISTRY)
    parser.add_argument('mode', choices=['topics', 'view', 'duplicates', 'bundle'])
    parser.add_argument('--topic', help='Topic ID or @unclassified')
    parser.add_argument('--lifecycle', choices=['all', 'active', 'historical'], default='all')
    parser.add_argument('--threshold', type=float, default=.5)
    parser.add_argument('--format', choices=['json', 'markdown'], default='json')
    parser.add_argument('--out', type=Path, required=True, help='Complete, untruncated derived output')
    args = parser.parse_args()
    if args.out.resolve() == args.registry.resolve():
        parser.error('Derived output must not replace its canonical registry')
    data = load(args.registry)
    if args.mode == 'bundle':
        args.out.mkdir(parents=True, exist_ok=True)
        for filename, content in bundle_files(data).items():
            (args.out / filename).write_text(content)
        print(f'Saved navigable derived views to {args.out}/topics.md')
        return
    report = (topic_map(data) if args.mode == 'topics' else
              claim_view(data, args.topic, args.lifecycle) if args.mode == 'view' else
              duplicate_candidates(data, args.threshold))
    if args.mode == 'duplicates' and args.format != 'json':
        parser.error('Duplicate candidates use JSON to retain method and review limitations')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(markdown(report) if args.format == 'markdown' else
                        json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(f'Saved complete {args.mode} report to {args.out}')


if __name__ == '__main__':
    main()
