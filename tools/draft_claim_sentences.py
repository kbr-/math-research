#!/usr/bin/env python3
"""List each sentence of a draft entry that cites a claim, beside that claim's registered statement.

For the author to read before the reviewer's brief: a sentence that cites a claim for more than the claim
says is seen when the two stand side by side.  A claim declared by the draft itself (data-claims) is not in
the registry yet and is listed as declared; any other identifier the registry does not hold is listed as
unregistered.

Usage: draft_claim_sentences.py DRAFT.html [--registry INDEX.json] [--width N]
Prints, per cited claim in order of first citation, the registered summary and then each citing sentence
with the heading or paragraph label it stands under.  Ends with the counts: sentences, claims, unregistered.
"""
import argparse
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLAIM = re.compile(r'<code>((?:lem|thm|prop|cor|conj|obs|ex|def|rem|local|historical):[A-Za-z0-9-]+)</code>')
BLOCK = re.compile(r'<(p|li|h3|h4)\b[^>]*>(.*?)</\1>', re.S)
LABEL = re.compile(r'^\s*<(?:strong|em)>([^<]{1,80}?)\.?</(?:strong|em)>')


def text(fragment):
    """Plain text of an HTML fragment, claim identifiers kept, TeX kept."""
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', fragment))).strip()


def sentences(fragment):
    """The fragment's sentences as HTML; a full stop inside TeX or an identifier does not end one."""
    held = []

    def hold(match):
        held.append(match.group(0))
        return f'\x00{len(held) - 1}\x00'

    masked = re.sub(r'\\\(.*?\\\)|\\\[.*?\\\]|<code>.*?</code>', hold, fragment, flags=re.S)
    parts = re.split(r'(?<=[.?!])\s+(?=[A-Z<\x00(])', masked)
    return [re.sub(r'\x00(\d+)\x00', lambda m: held[int(m.group(1))], part) for part in parts]


def citations(draft):
    """(claim id, section label, sentence text) for every sentence of the draft that cites a claim."""
    found, heading = [], ''
    for tag, body in BLOCK.findall(draft):
        if tag in ('h3', 'h4'):
            heading = text(body)
            continue
        label = LABEL.match(body)
        where = label.group(1) if label else heading
        for sentence in sentences(body):
            for claim in dict.fromkeys(CLAIM.findall(sentence)):
                found.append((claim, where, text(sentence)))
    return found


def report(draft, registry, width):
    summaries = {claim['id']: claim['summary'] for claim in registry['claims']}
    declared = set((re.search(r'data-claims="([^"]*)"', draft) or [None, ''])[1].split())
    found = citations(draft)
    lines, unregistered = [], set()
    for claim in dict.fromkeys(c for c, _, _ in found):
        if claim in summaries:
            statement = summaries[claim]
        elif claim in declared:
            statement = '(declared by this draft; not yet registered)'
        else:
            statement = '(NOT IN THE REGISTRY)'
            unregistered.add(claim)
        lines.append(f'{claim}\n  REGISTERED: {statement if width <= 0 else statement[:width]}')
        for cited, where, sentence in found:
            if cited == claim:
                lines.append(f'  [{where}] {sentence if width <= 0 else sentence[:width]}')
        lines.append('')
    claims = len({c for c, _, _ in found})
    lines.append(f'{len(found)} citing sentences, {claims} claims, {len(unregistered)} unregistered.')
    return '\n'.join(lines), unregistered


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('draft')
    parser.add_argument('--registry', default=str(ROOT / 'research' / 'claims' / 'index.json'))
    parser.add_argument('--width', type=int, default=0, help='cut statements and sentences at N characters')
    args = parser.parse_args()
    draft = pathlib.Path(args.draft).read_text()
    registry = json.loads(pathlib.Path(args.registry).read_text())
    out, unregistered = report(draft, registry, args.width)
    print(out)
    return 1 if unregistered else 0


if __name__ == '__main__':
    sys.exit(main())
