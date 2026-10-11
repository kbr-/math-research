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
It then lists the sentences outside the mathematics that hold a count, and the sentences outside the
statements and proofs that hold a universal or negative word, each to be read beside its source.
"""
import argparse
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
# Every prefix the registry's identifiers had on 11 October 2026, and historical: until then eleven were listed
# and 352 registered identifiers, imported statements (imp:) among them, were passed over.
PREFIXES = ('lem|thm|prop|cor|conj|obs|ex|def|rem|local|historical|imp|check|audit|third-party|ctx|criterion|q|'
            'note|open|draft|proof')
CLAIM = re.compile(r'<code>((?:' + PREFIXES + r'):[A-Za-z0-9-]+)</code>')
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


# Paragraphs that are a statement or its proof, where a universal word is the mathematics itself: by their
# leading label or, without one, the heading they stand under.  A summary of the result, its bearing, its
# reading and its structural reason are not among them: those are where a draft says more than it proved.
STATEMENT = re.compile(r'^(?:General statement|Setting|Degenerate cases|Nonvacuity|Sources read|'
                       r'.*\b(?:lemma|proposition|theorem|corollary|proof)\b.*)$', re.I)
# Paragraphs about how the work was done, where such a word is not a conclusion about the mathematics.  A first
# form without this list, and with "only" and "neither" among the words, listed 203 of the 435 sentences of six
# entries, too many to read.
BOOKKEEPING = re.compile(r'^(?:Where we stand|Chosen|Returns|Picked|Best outcome|Architecture test|Earlier entries.*|Owed attempt|'
                         r'Question|Verification gate|Record search|Process assessment|Review|'
                         r'Specification decision|Reviewer\'s suggestions.*|Sub-idea.*|The computation|'
                         r'Against the expectations.*|What was built)$', re.I)
# The paragraphs where a result is summed up, printed first: the others are prose under the entry's own headings.
SUMMARY = re.compile(r'^(?:New mathematics|Goal progress|Structural reason|Follow-up)$', re.I)
TITLE = re.compile(r'<h3>(.*?)</h3>(?:\s*<p class="entry-meta">(.*?)</p>)?', re.S)
STATUS_LINE = re.compile(r'<p class="entry-meta">.*?</p>', re.S)
UNIVERSAL = re.compile(r'\b(?:no|none|nothing|never|cannot|every|all|always|any|whatever)\b', re.I)


def universals(draft):
    """((section label, sentence text) for every sentence, outside the statements, their proofs and the
    paragraphs of bookkeeping, that holds a universal or a negative word; the number of sentences read).  The
    status line is not read here: the report prints it whole.  On 12 October 2026 four drafts of one block
    concluded more than they proved ("no witness of product form...", "it creates none"), each found by a
    reviewer; listed, each such sentence is read beside the statement it rests on before the reviewer's brief.
    The list is long, most sentences on it being sound: it is a reading list and not a finding."""
    found, read, heading = [], 0, ''
    for tag, body in BLOCK.findall(STATUS_LINE.sub('', draft)):
        if tag in ('h3', 'h4'):
            heading = text(body) if tag == 'h4' else ''
            continue
        label = LABEL.match(body)
        where = label.group(1) if label else heading
        if STATEMENT.match(where) or BOOKKEEPING.match(where):
            continue
        for index, sentence in enumerate(sentences(body)):
            unlabelled = LABEL.sub('', sentence) if index == 0 and label else sentence
            bare = re.sub(r'\\\(.*?\\\)|\\\[.*?\\\]|<code>.*?</code>', ' ', unlabelled, flags=re.S)
            read += 1
            if UNIVERSAL.search(text(bare)):
                found.append((where, text(sentence)))
    return found, read


def universals_report(draft, width):
    found, read = universals(draft)
    found = [row for row in found if SUMMARY.match(row[0])] + [row for row in found if not SUMMARY.match(row[0])]
    lines = [f'  [{where}] {sentence if width <= 0 else sentence[:width]}' for where, sentence in found]
    title = TITLE.search(draft)
    head = [] if not title else [f'  [title] {text(title.group(1))}'] + (
        [f'  [status line] {text(title.group(2))}'] if title.group(2) else [])
    return '\n'.join(['The title and the status line, whatever their words, then the sentences outside the '
                      'statements, proofs and bookkeeping that say no, none, cannot, every, all and the like, '
                      'the summing-up paragraphs first; read each beside the statement it rests on:']
                     + head + lines + [f'{len(found)} such sentences of {read} read.'])


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
    unknown = sorted({ident.split(':', 1)[0] for ident in summaries} - set(PREFIXES.split('|')))
    if unknown:                 # a kind of identifier added to the registry since the list was written
        lines.append('WARNING: the registry holds identifiers with prefixes this tool does not look for, so '
                     'sentences citing them are not listed: ' + ', '.join(unknown) + '. Add them to PREFIXES.')
    lines.append(f'{len(found)} citing sentences, {claims} claims, {len(unregistered)} unregistered.')
    return '\n'.join(lines), unregistered


def readings(transcript=None, draft=None):
    """Lines to print before a brief, or none: theorem-like statements of TeX and Lean sources that begin,
    unread, just past a range the session read since its last checkpoint (tools/session_reads.py).  A reading
    of 11 October 2026 stopped fifty lines short of the proposition that decided its test, and its reviewer
    found it.  Nothing here fails the listing; an agent without a Claude Code transcript gets no lines."""
    try:
        sys.path.insert(0, str(ROOT / 'tools'))
        import session_reads
        import stand_in_review
        transcript = transcript or stand_in_review.session_transcript(ROOT)
        lines = session_reads.current_lines(pathlib.Path(transcript).read_text(errors='replace').splitlines(),
                                            draft)
    except Exception:
        return []
    return (['', 'Readings since the last checkpoint: statements that begin just past a range of a source that '
             'was read, sources that could not be checked, the unread parts of files the draft names, and its '
             'sentences on what a partly read file says; say in the draft whether '
             'each was read or why it does not matter:'] + lines) if lines else []


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
    print('\n' + universals_report(draft, args.width))
    for line in readings(draft=draft):
        print(line)
    log_run(draft)
    return 1 if unregistered or missing else 0


if __name__ == '__main__':
    sys.exit(main())
