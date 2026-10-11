#!/usr/bin/env python3
"""List each sentence of a draft entry that cites a claim, beside that claim's registered statement.

For the author to read before the reviewer's brief: a sentence that cites a claim for more than the claim
says is seen when the two stand side by side.  A claim declared by the draft itself (data-claims) is not in
the registry yet and is listed as declared; any other identifier the registry does not hold is listed as
unregistered.

Usage: draft_claim_sentences.py DRAFT.html [--registry INDEX.json] [--notebook NOTEBOOK.html] [--width N]
Prints, per cited claim in order of first citation, the registered summary and then each citing sentence
with the heading or paragraph label it stands under.  Ends with the counts: sentences, claims, unregistered.
With --notebook it then lists, per entry the draft links, that entry's title and status line and each
sentence linking it: a sentence about what an earlier entry said is read beside what that entry claims.
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


# Paragraphs of mathematics, where a number is part of a statement or an argument and not a count taken from
# somewhere: by their leading label or, without one, the heading they stand under.  Every other paragraph is
# listed: a first form that named the bookkeeping paragraphs missed a count under a heading it did not know.
MATHEMATICS = re.compile(r'^(?:New mathematics|General statement|Setting|Question|Degenerate cases|Nonvacuity|'
                         r'Sources read|.*\b(?:lemma|proposition|theorem|corollary|proof|formula|identity)\b.*)$', re.I)
NUMBER_WORDS = ('two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|'
                'seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|'
                'thousand|dozen')
COUNT = re.compile(r'(?<![\w.-])\d[\d,.]*(?!\w)|\b(?:' + NUMBER_WORDS + r')(?:-\w+)?\b', re.I)
MONTHS = 'January|February|March|April|May|June|July|August|September|October|November|December'
DATE = re.compile(r'\b\d{1,2} (?:' + MONTHS + r')(?: \d{4})?\b|\b(?:' + MONTHS + r') \d{4}\b')


def counts(draft):
    """(section label, sentence text) for every sentence, outside the paragraphs of mathematics, that holds a
    count: a number in digits or words outside TeX, identifiers, links' targets, dates and the paragraph's own
    label.  On 11 October 2026 three counts in
    one draft were quoted from memory and were wrong; listed, each is read beside the saved output it came
    from before the reviewer's brief."""
    found, heading = [], ''
    for tag, body in BLOCK.findall(draft):
        if tag in ('h3', 'h4'):
            heading = text(body) if tag == 'h4' else ''   # a title that names a lemma marks no paragraph
            continue
        label = LABEL.match(body)
        where = label.group(1) if label else heading
        if MATHEMATICS.match(where):
            continue
        for index, sentence in enumerate(sentences(body)):
            # Only the paragraph's own label is left out: bold at the start of a later sentence is its text.
            unlabelled = LABEL.sub('', sentence) if index == 0 and label else sentence
            bare = re.sub(r'\\\(.*?\\\)|\\\[.*?\\\]|<code>.*?</code>', ' ', unlabelled, flags=re.S)
            if COUNT.search(DATE.sub(' ', text(bare))):
                found.append((where, text(sentence)))
    return found


RUN_LOG = ROOT / 'research' / 'logs' / 'claim-searches.jsonl'


def log_run(draft, path=None):
    """Append this run, with the draft's article id and its number of count sentences, to the ignored log the
    finisher reads, so that an entry whose listing was never printed is reported.  A log that cannot be written
    is not an error.  The log is the registry searches' own and is not created here: in a checkout that has never
    searched, the finisher skips the checks that read it.  A draft without an article is logged as "-", which
    matches no entry."""
    import time
    ident = re.search(r'<article\b[^>]*\bid="([^"]+)"', draft)
    try:
        path = path or RUN_LOG
        if not path.exists():
            return
        with path.open('a') as handle:
            handle.write(json.dumps({'unix_s': time.time(), 'query': 'draft_counts '
                                     + (ident.group(1) if ident else '-') + f' {len(counts(draft))}'}) + '\n')
    except OSError:
        pass


def counts_report(draft, width):
    found = counts(draft)
    lines = [f'  [{where}] {sentence if width <= 0 else sentence[:width]}' for where, sentence in found]
    return '\n'.join(['Sentences outside the mathematics that hold a count; read each beside its saved source:']
                     + lines + [f'{len(found)} sentences with a count.'])


LINK = re.compile(r'<a href="#(entry-[A-Za-z0-9-]+)"')
ARTICLE = re.compile(r'<article id="(entry-[A-Za-z0-9-]+)"[^>]*>\s*<h3>(.*?)</h3>\s*<p class="entry-meta">(.*?)</p>', re.S)


def entry_links(draft):
    """(entry id, section label, sentence text) for every sentence of the draft that links an entry."""
    found, heading = [], ''
    for tag, body in BLOCK.findall(draft):
        if tag in ('h3', 'h4'):
            heading = text(body)
            continue
        label = LABEL.match(body)
        where = label.group(1) if label else heading
        for sentence in sentences(body):
            for entry in dict.fromkeys(LINK.findall(sentence)):
                found.append((entry, where, text(sentence)))
    return found


def entry_report(draft, notebook, width):
    """Per linked entry, its title and status line from the notebook, then each sentence linking it."""
    heads = {entry: (text(title), text(meta)) for entry, title, meta in ARTICLE.findall(notebook)}
    found = entry_links(draft)
    lines, missing = [], set()
    cut = (lambda s: s) if width <= 0 else (lambda s: s[:width])
    for entry in dict.fromkeys(e for e, _, _ in found):
        if entry in heads:
            lines.append(f'{entry}\n  TITLE: {cut(heads[entry][0])}\n  STATUS: {cut(heads[entry][1])}')
        else:
            lines.append(f'{entry}\n  TITLE: (NOT IN THE NOTEBOOK)')
            missing.add(entry)
        for linked, where, sentence in found:
            if linked == entry:
                lines.append(f'  [{where}] {cut(sentence)}')
        lines.append('')
    entries = len({e for e, _, _ in found})
    lines.append(f'{len(found)} linking sentences, {entries} entries, {len(missing)} not in the notebook.')
    return '\n'.join(lines), missing


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
    parser.add_argument('--notebook', help='also list sentences that link an entry of this notebook file, '
                        'beside the entry\'s title and status line')
    args = parser.parse_args()
    draft = pathlib.Path(args.draft).read_text()
    registry = json.loads(pathlib.Path(args.registry).read_text())
    out, unregistered = report(draft, registry, args.width)
    print(out)
    missing = set()
    if args.notebook:
        linked, missing = entry_report(draft, pathlib.Path(args.notebook).read_text(), args.width)
        print('\n' + linked)
    print('\n' + counts_report(draft, args.width))
    log_run(draft)
    return 1 if unregistered or missing else 0


if __name__ == '__main__':
    sys.exit(main())
