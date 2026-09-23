#!/usr/bin/env python3
"""Bounded ranked search and exact lookup of the structured claim registry.

Unfiltered display searches also show up to three historical statement matches.
Machine-readable outputs and registry filters retain their current-registry scope.
Each hit lists the claims recorded as its newer versions (refinements, corrections, formalizations).

A grep for one phrase misses a recorded claim that uses other words ("point-support lower bound"
was missed by "support size"). Give the statement's content words; rows are ranked by the rarity-
weighted number of distinct word stems they contain, so a row sharing several uncommon words with
the statement comes first whatever the phrasing.

Usage: tools/search-claims.py [-n ROWS] WORD [WORD ...]
       tools/search-claims.py --show LABEL [--json]
"""
import argparse
import json
import math
from pathlib import Path
import re
import sys

from claim_registry import REGISTRY, load, references, exported, write_json

ROOT = Path(__file__).resolve().parents[1]
STOP = set('a an and are as at be by for from has have in is it its no not of on or over that the this to '
           'with without every each any all at most least than then under into only which whose'.split())


def stem(word):
    word = word.lower()
    for suffix in ('ations', 'ation', 'ings', 'ing', 'ies', 'ed', 'es', 's'):
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[:len(word) - len(suffix)]
    return word


def stems(text):
    return {stem(w) for w in re.findall(r'[A-Za-z][A-Za-z0-9]+', text) if w.lower() not in STOP}


def search(data, words, *, status=None, kind=None, topic=None, formalization=None,
           has_lean=False):
    query = stems(' '.join(words))
    claims = data['claims']
    tokens = [stems(c['id'] + ' ' + c['summary'] + ' ' + c['assessment']) for c in claims]
    count = {q: sum(any(t.startswith(q) or q.startswith(t) for t in s) for s in tokens) for q in query}
    weights = {q: math.log((len(claims) + 1) / (count[q] + 1)) for q in query}
    result = []
    for c, token_set in zip(claims, tokens):
        if status and status.casefold() not in c['assessment'].casefold():
            continue
        if kind and (c['mathematical_status'] or 'unknown') != kind:
            continue
        if topic and topic not in c['topics']:
            continue
        if formalization and (c['formalization']['status'] or 'unknown') != formalization:
            continue
        if has_lean and not any('.lean' in r['target'] for r in references(c)):
            continue
        hits = [q for q in query if any(t.startswith(q) or q.startswith(t) for t in token_set)]
        if query and not hits:
            continue
        result.append((sum(weights[q] for q in hits), c))
    result.sort(key=lambda item: -item[0])
    return result


NEWER = ('refines', 'corrects', 'supersedes', 'formalizes', 'rediscovers')


def newer_versions(data, claim_id):
    """Claims recorded as refining, correcting, superseding, formalizing or rediscovering claim_id.

    A search that lands on an older statement must also show its later versions: a formalized
    refinement can drop hypotheses that the older statement still carries."""
    status = {c['id']: c['formalization']['status'] for c in data['claims']}
    return [(e['source']['id'], e['type'], status.get(e['source']['id']))
            for e in data['relationships']
            if e['type'] in NEWER and e['target']['namespace'] == 'current'
            and e['target']['id'] == claim_id and e['source']['namespace'] == 'current']


def historical_matches(words, root=ROOT, limit=3):
    """Rank the immutable index's statements, excluding proofs and later claims."""
    directory = root / 'php_codex_handoff/manuscript'
    index = directory / 'CLAIM_INDEX.md'
    if not index.exists():
        return []
    claims, chapters = [], {}
    pattern = re.compile(r'^\| \[[^\]]+\]\((chapters/[^)#]+)#([^)]+)\) '
                         r'\| (.*?) \| ([^|]+) \| \[`([^`]+)`\]')
    for line in index.read_text().splitlines():
        match = pattern.match(line)
        if not match:
            if '(chapters/' in line:
                raise ValueError('Cannot parse historical index row: ' + line)
            continue
        relative, anchor, title, status, ident = match.groups()
        if relative not in chapters:
            chapters[relative] = (directory / relative).read_text()
        chapter = chapters[relative]
        marker = '<a id="' + anchor + '"></a>'
        if chapter.count(marker) != 1:
            raise ValueError('Missing or ambiguous historical anchor: ' + relative + '#' + anchor)
        excerpt = chapter.split(marker, 1)[1].split('<a id=', 1)[0]
        statement = excerpt.split('**Proof', 1)[0]
        statement = re.sub(r'^#{1,6} .*$', '', statement, flags=re.M)
        claims.append({'id': ident, 'summary': title,
                       'assessment': ' '.join(statement.split()),
                       'historical_status': status.strip(),
                       'source': str((directory / relative).relative_to(root)) + '#' + anchor})
    return [claim for _, claim in search({'claims': claims}, words)[:limit]]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-n', type=int, help='explicit result limit (default 12 only for ordinary search)')
    parser.add_argument('--list', action='store_true', help='List all matching claims in registry order')
    parser.add_argument('--fields', help='Comma-separated field paths, e.g. id,summary')
    parser.add_argument('--format', choices=['display', 'tsv', 'json'])
    parser.add_argument('words', nargs='*')
    parser.add_argument('--registry', type=Path, default=REGISTRY)
    parser.add_argument('--show', metavar='LABEL', help='Exact label lookup, full metadata and source links')
    parser.add_argument('--status', help='Substring in the preserved assessment text')
    parser.add_argument('--kind', help='Reviewed mathematical status, or unknown')
    parser.add_argument('--topic')
    parser.add_argument('--formalization', choices=['unknown', 'not_started', 'no_record', 'statement_only', 'discrepant', 'partial', 'complete'])
    parser.add_argument('--has-lean', action='store_true', help='Has a Lean link; does not imply verified coverage')
    parser.add_argument('--json', action='store_true', help='Machine-readable output')
    parser.add_argument('--out', type=Path, help='Save selected data (JSON payload, or the chosen projection format)')
    args = parser.parse_args()
    from recovery_evidence import observe
    def observed(text, shown=True):
        selector={k:v for k,v in vars(args).items() if k!='out'}
        observe('read',tool='claim-search',selector=selector,text=text,shown=shown)
    if args.n is not None and args.n < 1:
        parser.error('-n must be positive')
    if args.json and args.format not in (None, 'json'):
        parser.error('--json conflicts with the selected format')
    output_format = args.format or ('json' if args.json or args.show else 'tsv' if args.list or args.fields else 'display')
    fields = args.fields.split(',') if args.fields else ['id', 'summary']
    allowed = {'id', 'summary', 'assessment', 'record', 'mathematical_status',
               'formalization.status', 'formalization.scope', 'topics', 'significance'}
    if args.fields and (len(fields) != len(set(fields)) or not set(fields) <= allowed):
        parser.error('--fields must name distinct supported claim fields: ' + ', '.join(sorted(allowed)))
    if args.fields and output_format == 'display':
        parser.error('--fields requires tsv or json format')
    data = load(args.registry)
    if args.show:
        if args.list or args.words or any([args.status, args.kind, args.topic, args.formalization, args.has_lean]):
            parser.error('--show cannot be combined with search terms or filters')
        selected = [c for c in data['claims'] if c['id'] == args.show]
        if not selected:
            parser.error(f'Unknown claim: {args.show}')
        total = 1
    else:
        if not args.list and not args.words and not any([args.status, args.kind, args.topic, args.formalization, args.has_lean]):
            parser.error('Supply content words, --show LABEL, or a filter')
        ranked = search(data, args.words, status=args.status, kind=args.kind, topic=args.topic,
                        formalization=args.formalization, has_lean=args.has_lean)
        total = len(ranked)
        if args.list:
            matches = {c['id'] for _, c in ranked}
            ranked = [(0, c) for c in data['claims'] if c['id'] in matches]
        limit = args.n if args.n is not None else (None if args.list or args.fields or output_format == 'tsv' else 12)
        selected = [c for _, c in (ranked[:limit] if limit is not None else ranked)]
    if output_format == 'tsv' or args.fields:
        def value(claim, field):
            result = claim
            for part in field.split('.'):
                result = result[part]
            return result
        projected = [{field: value(c, field) for field in fields} for c in selected]
        if output_format == 'json':
            text = json.dumps(projected, ensure_ascii=False, indent=2) + '\n'
        else:
            def cell(v):
                if v is None:
                    return r'\N'
                if not isinstance(v, str):
                    v = json.dumps(v, ensure_ascii=False, separators=(',', ':'))
                return v.replace('\\', '\\\\').replace('\t', r'\t').replace('\n', r'\n').replace('\r', r'\r')
            text = ''.join('\t'.join(cell(row[f]) for f in fields) + '\n' for row in projected)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(text)
        else:
            sys.stdout.write(text)
        observed(text, shown=not bool(args.out))
        if total > len(selected):
            print(f'{total-len(selected)} matches omitted by explicit limit.', file=sys.stderr)
        return
    payload = exported(data, selected)
    selected_ids = {c['id'] for c in selected}
    payload['relationships'] = [e for e in data['relationships'] if any(
        e[end]['namespace'] == 'current' and e[end]['id'] in selected_ids for end in ('source', 'target'))]
    payload['newer_versions'] = {c['id']: [{'id': i, 'type': t, 'formalization': f}
                                           for i, t, f in newer_versions(data, c['id'])]
                                 for c in selected if newer_versions(data, c['id'])}
    payload.update(total_matches=total, shown=len(selected), omitted=total-len(selected))
    if args.out:
        write_json(args.out, payload)
    if output_format == 'json' or args.show:
        text=json.dumps(payload, ensure_ascii=False, indent=2)+'\n'
        sys.stdout.write(text)
        observed(text)
        return
    def brief(text, limit):
        return text if len(text) <= limit else text[:limit-1] + '…'
    lines=[]
    for c in selected:
        lines += [c['id'], '  '+brief(c['summary'],230),
                  '  Assessment: '+brief(c['assessment'],150),
                  '  Formalization classification: '+(c['formalization']['status'] or 'unknown (see assessment)'),
                  '  Source: '+next(r['target'] for r in references(c) if r['field']=='record')]
        newer = newer_versions(data, c['id'])
        if newer:
            lines.append('  Newer versions (read before relying on this one): '+'; '.join(
                f'{i} ({t}, formalization {f or "unknown"})' for i, t, f in newer))
    lines.append(f'{len(selected)} of {total} matches; {total-len(selected)} omitted. '
                 'Use --show LABEL for full metadata; ellipses mark shortened text.')
    if (args.words and not args.list and args.registry.resolve() == REGISTRY.resolve()
            and not any([args.status, args.kind, args.topic, args.formalization, args.has_lean])):
        historical = historical_matches(args.words)
        if historical:
            lines.append('Historical statement matches (at most 3; read source before relying):')
            for c in historical:
                lines += [f"  historical:{c['id']} — {c['summary']} [{c['historical_status']}]",
                          '    '+brief(c['assessment'], 230), '    Source: '+c['source']]
    text='\n'.join(lines)+'\n';sys.stdout.write(text);observed(text)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as exc:
        sys.exit(f'search-claims: {exc}')
